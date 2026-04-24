# 🚀 21 · GO-LIVE RUNBOOK FINAL — Execute Today (Step-by-Step untuk Tes Langsung)

> **Tujuan dokumen ini**: SATU halaman final yang kamu ikuti top-to-bottom untuk jalan live test hari ini. Bukan analisis, bukan review — ini **eksekusi**.
> 

> **Basis**: Hasil audit [17 · v0.4 Implementation Review](https://www.notion.so/17-v0-4-Implementation-Review-Bugs-Gaps-Completion-Plan-3b7aa241f5284b99bd6819d091b7f067?pvs=21) + [18 · UX Navigation + Gap Closure](https://www.notion.so/18-UX-Navigation-Go-Live-Gap-Closure-Backend-Frontend-fff3bef08a734370a76ca77ba4c8feeb?pvs=21). Status repo `dedy45/livetik@master` per 2026-04-24.
> 

> **Output akhir**: Worker jalan, controller UI tidak crash, 108 audio clip siap, bisa tes 15 menit mock-live dengan OBS Virtual Camera.
> 

<aside>
🎯

**TL;DR**: Backend **85% siap**. UI controller **masih crash** karena 5 komponen + 3 store hilang. Audio library **kemungkinan kosong** (perlu run script generator). Follow 4 fase di bawah — estimasi **4-6 jam kerja** sampai bisa tes live.

</aside>

---

## 📊 STATUS FINAL (Fakta per 2026-04-24)

| Komponen | Status | Blocker? |
| --- | --- | --- |
| WS server + 14 command handler | ✅ Siap | Tidak |
| `scripts/gen_audio_library.py`  • `.bat` | ✅ Committed | Tapi belum di-run |
| `audio_library/index.json` | ⚠️ Kemungkinan `clips: []` | 🔴 **Isi clips kosong = live silent** |
| Controller `/library/+page.svelte` | ✅ Logic lengkap | Tapi store target 404 |
| Controller root `/+page.svelte` | 🔴 **CRASH** — import 5 komponen 404 | 🔴 **Build fail** |
| 3 store `.svelte.ts` | ❌ 404 | 🔴 **Wajib** |

**Verdict**: Doc #478 dan #484 sudah benar diagnosanya, tapi bukan untuk di-eksekusi. **Pakai doc ini.**

---

## 🔴 FASE 0 · Pre-flight Check (5 menit)

**Wajib dijalankan dulu untuk konfirmasi kondisi nyata**.

```bash
cd livetik
git pull origin master

REM Cek isi audio library
type apps\worker\static\audio_library\index.json
REM Kalau output = {"version":"1.0","clips":[]} → BELUM di-generate, wajib Fase 2
REM Kalau output ada 108 entries → Fase 2 bisa skip

REM Cek .wav count
dir apps\worker\static\audio_library\*.wav /b | find /c /v ""
REM Harus 108. Kalau 0 → wajib Fase 2

REM Cek .env
type .env | findstr CARTESIA_API_KEYS
REM Harus ada minimal 1 key. Kalau kosong → isi dulu sebelum lanjut
```

<aside>
⚠️

**Kalau belum punya `.env` lokal**: `copy .env.example .env` lalu isi `CARTESIA_API_KEYS`, `CARTESIA_VOICE_ID`, `TIKTOK_USERNAME=interiorhack.id`, `LLM_API_KEY_9ROUTER` (atau provider lain). Biarkan `REPLY_ENABLED=false` dan `DRY_RUN=true` untuk tes pertama.

</aside>

---

## 🛠️ FASE 1 · Fix Build Crash (90 menit)

**Tujuan**: `pnpm dev` tidak crash. Commit 3 store + 5 komponen.

### 1.1 — Buat 3 store (30 menit)

File: `apps/controller/src/lib/stores/live_state.svelte.ts`

```tsx
import { wsStore } from './ws.svelte';

export type LiveMode = 'IDLE' | 'RUNNING' | 'PAUSED' | 'STOPPED';

class LiveStateStore {
	mode = $state<LiveMode>('IDLE');
	phase = $state('');
	phase_idx = $state(0);
	phase_total = $state(0);
	product = $state('');
	elapsed_s = $state(0);
	remaining_s = $state(7200);

	start() { wsStore.sendCommand('live.start', {}); }
	pause() { wsStore.sendCommand('live.pause', {}); }
	resume() { wsStore.sendCommand('live.resume', {}); }
	stop() { wsStore.sendCommand('live.stop', {}); }
	emergency() { wsStore.sendCommand('live.emergency_stop', { operator_id: 'ui' }); }
}

export const liveState = new LiveStateStore();

// Wire ke ws event
if (typeof window !== 'undefined') {
	wsStore.onEvent('live.state', (ev: any) => {
		liveState.mode = ev.mode;
		liveState.phase = ev.phase;
		liveState.phase_idx = ev.phase_idx;
		liveState.phase_total = ev.phase_total;
		liveState.product = ev.product;
	});
	wsStore.onEvent('live.tick', (ev: any) => {
		liveState.elapsed_s = ev.elapsed_s;
		liveState.remaining_s = ev.remaining_s;
	});
}
```

File: `apps/controller/src/lib/stores/audio_library.svelte.ts`

```tsx
import { wsStore } from './ws.svelte';

export interface ClipMeta {
	id: string;
	category: string;
	tags: string[];
	duration_ms: number;
	script: string;
	scene_hint?: string;
	file_path?: string;
}

class AudioLibraryStore {
	clips = $state<ClipMeta[]>([]);
	nowPlaying = $state<string | null>(null);

	async load() {
		const reqId = wsStore.sendCommand('audio.list', {});
		await new Promise(r => setTimeout(r, 500));
		const result = wsStore.getResult(reqId);
		if (result?.ok && result.result?.clips) {
			this.clips = result.result.clips;
		}
		wsStore.clearResult(reqId);
	}

	play(clipId: string) { wsStore.sendCommand('audio.play', { clip_id: clipId }); }
	stop() { wsStore.sendCommand('audio.stop', {}); }
}

export const audioLibrary = new AudioLibraryStore();

if (typeof window !== 'undefined') {
	wsStore.onEvent('audio.now', (ev: any) => { audioLibrary.nowPlaying = ev.clip_id; });
	wsStore.onEvent('audio.done', () => { audioLibrary.nowPlaying = null; });
}
```

File: `apps/controller/src/lib/stores/decisions.svelte.ts`

```tsx
import { wsStore } from './ws.svelte';

export interface Decision {
	timestamp: number;
	comment_id: string;
	user: string;
	text: string;
	intent: string;
	action: string;
}

class DecisionsStore {
	items = $state<Decision[]>([]);
	max = 100;

	append(d: Decision) {
		this.items = [d, ...this.items].slice(0, this.max);
	}
}

export const decisions = new DecisionsStore();

if (typeof window !== 'undefined') {
	wsStore.onEvent('comment.classified', (ev: any) => {
		decisions.append({
			timestamp: ev.timestamp || Date.now() / 1000,
			comment_id: ev.comment_id || String(Date.now()),
			user: ev.user || 'unknown',
			text: ev.text || '',
			intent: ev.intent || 'other',
			action: ev.action || 'ignore',
		});
	});
}
```

### 1.2 — Buat 5 komponen (45 menit)

File: `apps/controller/src/lib/components/TwoHourTimer.svelte`

```
<script lang="ts">
	import { liveState } from '$lib/stores/live_state.svelte';

	function fmt(s: number): string {
		const h = Math.floor(s / 3600);
		const m = Math.floor((s % 3600) / 60);
		const sec = Math.floor(s % 60);
		return `${h}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;
	}

	const color = $derived(
		liveState.remaining_s < 600 ? 'text-red-500 animate-pulse' :
		liveState.remaining_s < 1800 ? 'text-yellow-500' : 'text-green-500'
	);
</script>

<div class="rounded-lg border p-4 font-mono">
	<div class="text-xs uppercase opacity-60">Remaining</div>
	<div class="text-4xl {color}">{fmt(liveState.remaining_s)}</div>
	<div class="text-xs opacity-60 mt-1">Elapsed {fmt(liveState.elapsed_s)} / 2:00:00</div>
	<div class="text-xs mt-1">Mode <b>{liveState.mode}</b> · Phase {liveState.phase} ({liveState.phase_idx + 1}/{liveState.phase_total})</div>
</div>
```

File: `apps/controller/src/lib/components/EmergencyStop.svelte`

```
<script lang="ts">
	import { liveState } from '$lib/stores/live_state.svelte';
	let confirming = $state(false);
</script>

{#if !confirming}
	<button class="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-6 rounded-lg text-lg w-full"
			onclick={() => confirming = true}>
		🛑 EMERGENCY STOP
	</button>
{:else}
	<div class="bg-red-900/20 border-2 border-red-600 p-3 rounded">
		<p class="mb-2 font-bold text-sm">Yakin stop live sekarang?</p>
		<button class="bg-red-600 text-white px-3 py-1 rounded mr-2" onclick={() => { liveState.emergency(); confirming = false; }}>
			Ya STOP
		</button>
		<button class="bg-gray-300 text-black px-3 py-1 rounded" onclick={() => confirming = false}>Batal</button>
	</div>
{/if}
```

File: `apps/controller/src/lib/components/AudioLibraryGrid.svelte`

```
<script lang="ts">
	import { audioLibrary } from '$lib/stores/audio_library.svelte';
	import { onMount } from 'svelte';

	onMount(() => audioLibrary.load());

	let filter = $state('');
	const categories = $derived([...new Set(audioLibrary.clips.map(c => c.category))].sort());
	const filtered = $derived(
		filter ? audioLibrary.clips.filter(c => c.category === filter) : audioLibrary.clips
	);
</script>

<div class="p-3 border rounded">
	<div class="flex justify-between mb-2">
		<h3 class="font-bold">Audio Library ({audioLibrary.clips.length})</h3>
		<button class="text-xs opacity-60 hover:opacity-100" onclick={() => audioLibrary.load()}>↻</button>
	</div>
	<div class="flex flex-wrap gap-1 mb-2">
		<button class="text-xs px-2 py-0.5 rounded border {filter === '' ? 'bg-blue-500 text-white' : ''}" onclick={() => filter = ''}>all</button>
		{#each categories as cat}
			<button class="text-xs px-2 py-0.5 rounded border {filter === cat ? 'bg-blue-500 text-white' : ''}" onclick={() => filter = cat}>{cat}</button>
		{/each}
	</div>
	<div class="grid grid-cols-2 gap-1 max-h-64 overflow-y-auto">
		{#each filtered as clip (clip.id)}
			<button class="text-left border rounded p-1.5 text-xs hover:bg-blue-500/10"
					onclick={() => audioLibrary.play(clip.id)}>
				<div class="font-mono opacity-60">{clip.id} · {Math.round(clip.duration_ms/1000)}s</div>
				<div class="line-clamp-2">{clip.script}</div>
			</button>
		{/each}
	</div>
</div>
```

File: `apps/controller/src/lib/components/DecisionStream.svelte`

```
<script lang="ts">
	import { decisions } from '$lib/stores/decisions.svelte';

	function chip(intent: string) {
		const map: Record<string,string> = {
			question: 'bg-blue-100 text-blue-800',
			buying_intent: 'bg-green-100 text-green-800',
			price_question: 'bg-yellow-100 text-yellow-800',
			forbidden_link: 'bg-red-100 text-red-800',
			forbidden_contact: 'bg-red-100 text-red-800',
			spam: 'bg-gray-100 text-gray-600',
		};
		return map[intent] || 'bg-gray-100 text-gray-600';
	}
</script>

<div class="p-3 border rounded">
	<h3 class="font-bold mb-2">Decision Stream</h3>
	<div class="max-h-80 overflow-y-auto space-y-1 text-sm">
		{#if decisions.items.length === 0}
			<div class="opacity-50 italic">Menunggu comment...</div>
		{:else}
			{#each decisions.items as d (d.comment_id)}
				<div class="border-b pb-1">
					<span class="text-xs opacity-60">{new Date(d.timestamp * 1000).toLocaleTimeString('id-ID')}</span>
					<span class="font-semibold ml-1">@{d.user}</span>
					<span class="text-xs px-1.5 py-0.5 rounded {chip(d.intent)} ml-1">{d.intent}</span>
					<div class="text-xs opacity-80">{d.text}</div>
				</div>
			{/each}
		{/if}
	</div>
</div>
```

File: `apps/controller/src/lib/components/ReplySuggestions.svelte`

```
<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	import { onMount } from 'svelte';

	let replies = $state<string[]>([]);
	let currentCommentId = $state<string | null>(null);

	function approve(i: number) {
		if (!currentCommentId) return;
		wsStore.sendCommand('reply.approve', { comment_id: currentCommentId, reply_text: replies[i] });
		replies = [];
		currentCommentId = null;
	}
	function reject() {
		if (!currentCommentId) return;
		wsStore.sendCommand('reply.reject', { comment_id: currentCommentId });
		replies = [];
		currentCommentId = null;
	}
	function regen() {
		if (!currentCommentId) return;
		wsStore.sendCommand('reply.regen', { comment_id: currentCommentId });
	}

	onMount(() => {
		wsStore.onEvent('reply.suggested', (ev: any) => {
			replies = ev.replies || [];
			currentCommentId = ev.comment_id;
		});
		const handler = (e: KeyboardEvent) => {
			if (replies.length === 0) return;
			if (e.key === 'a') approve(0);
			if (e.key === 's' && replies[1]) approve(1);
			if (e.key === 'd' && replies[2]) approve(2);
			if (e.key === 'q') reject();
			if (e.key === 'w') regen();
		};
		window.addEventListener('keydown', handler);
		return () => window.removeEventListener('keydown', handler);
	});
</script>

<div class="p-3 border rounded">
	<h3 class="font-bold mb-2">Reply Suggestions</h3>
	{#if replies.length === 0}
		<div class="opacity-50 italic text-sm">Menunggu komen...</div>
	{:else}
		{#each replies as r, i (i)}
			<div class="border rounded p-2 mb-1.5 text-sm">
				<span class="text-xs opacity-60">[{['A','S','D'][i]}]</span>
				<div>{r}</div>
				<button class="bg-green-600 text-white px-2 py-0.5 rounded text-xs mt-1" onclick={() => approve(i)}>Approve</button>
			</div>
		{/each}
		<div class="flex gap-2 mt-2">
			<button class="bg-gray-400 text-white px-2 py-1 rounded text-xs" onclick={reject}>[Q] Reject</button>
			<button class="bg-blue-500 text-white px-2 py-1 rounded text-xs" onclick={regen}>[W] Regen</button>
		</div>
	{/if}
</div>
```

### 1.3 — Commit + test (15 menit)

```bash
git add apps/controller/src/lib/stores/live_state.svelte.ts
git add apps/controller/src/lib/stores/audio_library.svelte.ts
git add apps/controller/src/lib/stores/decisions.svelte.ts
git add apps/controller/src/lib/components/TwoHourTimer.svelte
git add apps/controller/src/lib/components/EmergencyStop.svelte
git add apps/controller/src/lib/components/AudioLibraryGrid.svelte
git add apps/controller/src/lib/components/DecisionStream.svelte
git add apps/controller/src/lib/components/ReplySuggestions.svelte
git commit -m "[v0.4][feat] 3 stores + 5 Svelte components for Live Cockpit"
git push

cd apps/controller
pnpm install
pnpm dev
REM Buka http://localhost:5173 — harus tidak crash
```

<aside>
✅

**Acceptance Fase 1**: Browser [http://localhost:5173](http://localhost:5173) render Dashboard (masih passive, tapi tidak crash). Tidak ada error merah di terminal Vite.

</aside>

---

## 🎙️ FASE 2 · Generate Audio Library (60 menit)

**Skip kalau** Fase 0 check menunjukkan `index.json` sudah berisi 108+ entries DAN folder ada 108 file `.wav`.

### 2.1 — Jalankan generator

```bash
cd livetik
REM Pastikan .env terisi CARTESIA_API_KEYS, CARTESIA_VOICE_ID, CARTESIA_MODEL=sonic-3

scripts\gen_audio_library.bat
REM Output expected:
REM Generating 108 clips...
REM [1/108] A_opening_001 (14230ms)
REM [2/108] A_opening_002 (13180ms)
REM ...
REM ✓ Wrote 108 entries to apps\worker\static\audio_library\index.json
```

Durasi estimasi: **8-12 menit** (108 clip × ~5 detik per Cartesia call).

### 2.2 — Verifikasi

```bash
dir apps\worker\static\audio_library\*.wav /b | find /c /v ""
REM Harus 108

REM Spot-check 1 file
ffprobe apps\worker\static\audio_library\A_opening_001.wav
REM Harus: 44100Hz, \~14s duration
```

### 2.3 — Kalau error

| Error | Fix | `CARTESIA_API_KEYS not set` | Isi di `.env` — minimal 1 key dari [cartesia.ai](http://cartesia.ai) dashboard |
| --- | --- | --- | --- |
| `401 Unauthorized` | API key expired/invalid. Regenerate di cartesia dashboard | `429 Too Many Requests` | Rate limit. Increase sleep di script dari 0.5s → 1.5s, ulang |
| `404 model sonic-indonesian` | Ganti `.env`: `CARTESIA_MODEL=sonic-3` | Script crash mid-way | Re-run — script idempotent, skip file yang sudah ada |

<aside>
✅

**Acceptance Fase 2**: 108 file `.wav`, `index.json` berisi 108 entries dengan `duration_ms > 0`.

</aside>

---

## 🚦 FASE 3 · Start Worker + Controller (15 menit)

### 3.1 — Terminal 1: Worker

```bash
cd livetik\apps\worker
uv sync
uv run python -m banghack
REM Output expected:
REM [INFO] AudioLibraryManager loaded 108 clips
REM [INFO] Classifier ready (rules + llm_fallback)
REM [INFO] Suggester ready
REM [INFO] Director ready (runsheet 3 products, 8 phases, 3000s)
REM [INFO] WS server on ws://localhost:8765
REM [INFO] HTTP server on http://localhost:8766
REM [INFO] TikTok listener: DRY_RUN=true, REPLY_ENABLED=false
```

### 3.2 — Terminal 2: Health check

```bash
curl http://localhost:8766/health
REM Expected JSON:
REM {
}
REM empty-block/
REM empty-block/
REM   "status": "ok",
REM   "audio_ready": true,
REM   "audio_library_clip_count": 108,
REM   "classifier_ready": true,
REM   "director_ready": true,
REM   "budget_remaining_idr": 50000
REM }
```

Kalau `audio_ready: false` → kembali ke Fase 2. Kalau `clip_count: 0` → `index.json` tidak terbaca, cek path env.

### 3.3 — Terminal 3: Controller

```bash
cd livetik\apps\controller
pnpm dev
REM Buka http://localhost:5173
```

Navigasi:

- `/` — Dashboard (status worker, cost, health probe)
- `/library` — Audio Library (108 clip, klik untuk preview)
- `/live` — Live Monitor (passive, OK untuk tes awal)

<aside>
✅

**Acceptance Fase 3**: Dashboard tampilkan "Worker online" (dot hijau). `/library` tampilkan grid 108 clip. Klik 1 clip → audio keluar dari speaker laptop.

</aside>

---

## 🎬 FASE 4 · Dress Rehearsal 15 Menit (30 menit)

### 4.1 — Setup OBS

1. Install OBS Studio 30+ kalau belum
2. Tambah scene `test_live_1`
3. Source: **Image** dengan foto produk apapun (placeholder — video AI belum ready)
4. Source: **Audio Output Capture** device = speaker default (supaya audio Cartesia ketangkap ke OBS)
5. Tools → **Start Virtual Camera**

### 4.2 — Start session (DRY RUN)

Di controller `/` atau `/live`, kirim command via browser console (sementara tombol start belum di-wire):

```
// Buka DevTools Console di http://localhost:5173
// Sudah ada global wsStore — langsung call:
wsStore.sendCommand('live.start', {})
```

Ekspektasi di worker terminal:

```
[INFO] Director starting session (max 7200s, 8 phases)
[INFO] Phase 0: opening (180s) → category A_opening
[INFO] Playing A_opening_003 (14.2s)
[INFO] comment.classified emit (mock — DRY_RUN=true)
[INFO] Playing A_opening_007 (13.8s)  ← loop per phase sudah fixed
```

### 4.3 — Observe selama 15 menit

Check:

- [ ]  Audio keluar kontinyu (maksimal jeda 5 detik antar clip)
- [ ]  Pindah phase otomatis setelah durasi phase lewat
- [ ]  Timer remaining_s turun setiap detik
- [ ]  `/library` grid ke-highlight clip yang sedang play
- [ ]  `curl /health` masih `status: ok`
- [ ]  Budget remaining tidak bergerak (karena `REPLY_ENABLED=false`, LLM tidak dipanggil)

### 4.4 — Stop session

```
wsStore.sendCommand('live.stop', {})
```

Atau: pencet tombol 🛑 EmergencyStop di dashboard (kalau komponen sudah di-render).

### 4.5 — Review log

```bash
type apps\worker\logs\banghack.log | findstr /i "ERROR WARN"
REM Seharusnya bersih atau hanya ada WARN rate-limit yang benign
```

<aside>
✅

**Acceptance Fase 4 / GO-LIVE READY**: 15 menit dry-run selesai tanpa ERROR, audio kontinyu, worker + controller tidak crash, `/health` tetap ok. **Sistem siap untuk live test dengan TikTok beneran** (dengan `DRY_RUN=false` setelah ini).

</aside>

---

## 🔴 GO-LIVE NYATA (Setelah Fase 4 Hijau)

Kalau Fase 4 lulus, barulah berani live beneran. Update `.env`:

```bash
DRY_RUN=false
REPLY_ENABLED=false          REM tetap false untuk live pertama — LLM reply masih test mode
TIKTOK_USERNAME=interiorhack.id
LIVE_MAX_DURATION_S=900       REM 15 menit dulu, bukan 7200
```

1. OBS → Start Virtual Camera
2. TikTok Studio mobile/PC → pilih Virtual Camera sebagai input
3. Start Live di TikTok
4. Controller `/live` → `live.start`
5. Monitor `/library` + `/live` + worker log selama 15 menit
6. Emergency stop kalau ada:
    - Audio diam >30 detik
    - CPU >90% sustained
    - `/health` return `status: degraded`
    - TikTok warning/suspend notification

**Jangan langsung 2 jam.** Incremental: 15 menit → 30 menit → 1 jam → 2 jam. Dress rehearsal bertingkat.

---

## 📋 Checklist Eksekusi (Centang saat selesai)

### Pre-flight

- [ ]  `git pull origin master` bersih
- [ ]  `.env` terisi Cartesia keys + TikTok username
- [ ]  Cek status `index.json` dan `.wav` count

### Fase 1 · Build Fix

- [ ]  3 store committed (`live_state`, `audio_library`, `decisions`)
- [ ]  5 komponen committed
- [ ]  `pnpm dev` tidak crash

### Fase 2 · Audio

- [ ]  `gen_audio_library.bat` selesai tanpa error
- [ ]  108 `.wav` file exist
- [ ]  `index.json` 108 entries

### Fase 3 · Boot

- [ ]  Worker running di :8765 + :8766
- [ ]  `/health` → `status: ok, audio_ready: true`
- [ ]  Controller buka di :5173
- [ ]  `/library` render 108 clip
- [ ]  Klik 1 clip → audio keluar

### Fase 4 · Dress rehearsal

- [ ]  OBS Virtual Camera running
- [ ]  `live.start` via console
- [ ]  Audio kontinyu 15 menit
- [ ]  Pindah phase otomatis
- [ ]  `live.stop` clean shutdown
- [ ]  Log bebas ERROR

### Go-Live (kalau Fase 4 hijau)

- [ ]  `DRY_RUN=false` di `.env`
- [ ]  TikTok Studio pakai Virtual Camera
- [ ]  Live 15 menit sukses
- [ ]  Scale up bertahap

---

## 🎯 Hal yang SENGAJA belum di-scope di runbook ini

Supaya bisa go-live sekarang, 3 item berikut **ditunda** ke iterasi lanjut:

1. **Video library AI-generated** (Veo 3.1 + Nano Banana) — pakai placeholder image/stock footage dulu. Video AI ada di [19 · Video Faceless Workflow v2](https://www.notion.so/19-Video-Faceless-Workflow-v2-4-Produk-Veo-3-1-Realistic-Nano-Banana-Consistent-Loopable-B--15cac1e82fe34e3d869de731c71856b2?pvs=21) sebagai track paralel.
2. **Live Cockpit 3-panel redesign** — versi passive `/live` cukup untuk tes awal. Redesign dashboard penuh ada di [18 · UX Gap](https://www.notion.so/18-UX-Navigation-Go-Live-Gap-Closure-Backend-Frontend-fff3bef08a734370a76ca77ba4c8feeb?pvs=21) §Live Cockpit — setelah live pertama sukses.
3. **Reply LLM live mode** — `REPLY_ENABLED=true` ditunda sampai live pertama stabil. Biar dulu text-to-voice satu arah dari clip library.

---

## 🆘 Troubleshooting Cepat

| Gejala | Kemungkinan penyebab | Fix cepat | `pnpm dev` error `Failed to resolve import` | Komponen atau store belum di-commit | Cek Fase 1 — commit yang kurang |
| --- | --- | --- | --- | --- | --- |
| `/health` returns `audio_ready: false` | `index.json` tidak terbaca | Cek path `AUDIO_LIBRARY_DIR` di `.env` — harus `static/audio_library` relatif ke CWD worker | Worker start tapi `clip_count: 0` | `index.json` = `{"clips":[]}` | Run Fase 2 generator |
| `audio.play` sukses tapi tidak ada suara | Audio output device salah | Windows Settings → Sound → output default = speaker yang aktif. Restart worker. | Director tidak pindah phase | Runsheet loop infinite di v0.3, tapi v0.4 sudah fixed | Cek `director.py` version — harus ada BUG-1 fix (play clip tiap 20-30s dalam phase) |
| WS connect failed di browser | Worker tidak running atau port salah | Terminal worker aktif? `netstat -an | findstr 8765` | TikTok Live banned setelah Virtual Camera | Policy TikTok — deteksi non-camera input | Pakai HDMI capture card atau sharing-screen dari HP terpisah (bukan Virtual Camera) |

---

## 📎 Referensi

- Audit status: [17 · v0.4 Implementation Review](https://www.notion.so/17-v0-4-Implementation-Review-Bugs-Gaps-Completion-Plan-3b7aa241f5284b99bd6819d091b7f067?pvs=21)
- Gap analysis: [18 · UX Navigation + Go-Live Gap Closure](https://www.notion.so/18-UX-Navigation-Go-Live-Gap-Closure-Backend-Frontend-fff3bef08a734370a76ca77ba4c8feeb?pvs=21)
- Build spec: [16 · KIRO Handoff](https://www.notion.so/16-KIRO-Handoff-v0-4-Build-Spec-Full-Skeleton-9e5d4d30289240c3bc229e7a66c036b7?pvs=21)
- Live plan 2 jam: [Live Interaction Plan](https://www.notion.so/Live-Interaction-Plan-2-Jam-Cartesia-Produk-Scene-Retensi-1267e9d752fa48ad847d1b2e778644a7?pvs=21)
- Voice script: [20 · Live Voice Script v2](https://www.notion.so/20-Live-Voice-Script-v2-Fragment-Reaction-Kit-SSML-Pronunciation-Cartesia-TTS-Optimized-36de7d4f1aca4a3290427b05a7fd3626?pvs=21)
- Video workflow (track paralel): [19 · Video Faceless Workflow v2](https://www.notion.so/19-Video-Faceless-Workflow-v2-4-Produk-Veo-3-1-Realistic-Nano-Banana-Consistent-Loopable-B--15cac1e82fe34e3d869de731c71856b2?pvs=21)
- Repo: `dedy45/livetik@master`

---

<aside>
🚀

**Bottom line**: Doc ini adalah SATU runbook final yang replace doc #478 (review) dan #484 (gap plan) untuk keperluan eksekusi. Follow Fase 0→4 urut tanpa skip. Estimasi total 4-6 jam dari mulai sampai dress rehearsal hijau. Setelah itu baru langkah ke live TikTok nyata secara incremental 15-menit dulu.

</aside>