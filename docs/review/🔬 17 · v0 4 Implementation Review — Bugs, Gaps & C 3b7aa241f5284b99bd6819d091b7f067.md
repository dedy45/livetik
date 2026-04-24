# 🔬 17 · v0.4 Implementation Review — Bugs, Gaps & Completion Plan

> **Tanggal audit**: 2026-04-23 · **Repo**: `dedy45/livetik@master` · **Commit basis**: hasil push setelah KIRO Handoff spec ([🛠️ 16 · KIRO Handoff — v0.4 Build Spec (Full Skeleton)](https://www.notion.so/16-KIRO-Handoff-v0-4-Build-Spec-Full-Skeleton-9e5d4d30289240c3bc229e7a66c036b7?pvs=21))
> 

> **Verdict singkat**: **Backend worker 85% siap dan berkualitas tinggi. UI controller 0% — tidak ada satupun komponen v0.4 di-commit. Audio library kosong (index.json 0 clips, script generator hilang). Ada 3 blocker kritis dan ~15 bug/gap medium.**
> 

---

## 📊 Skor Implementasi per Fase

| Fase | Target | Actual | Status | Catatan |
| --- | --- | --- | --- | --- |
| **P0 · Audio Library** | 4 file code + YAML + index + 160 wav + test + script gen | Code ✅ · YAML ⚠️ · index ❌ · wav ❌ · test ✅ · gen ❌ | 🔴 40% | Backend jalan, tapi library kosong |
| **P1 · Classifier** | rules + llm_fallback + test | Semua ✅ | 🟢 100% | Siap produksi |
| **P2 · Suggester** | suggester + cache + budget_guard + templates + test | Semua ✅ | 🟢 95% | Bug interpolasi + no rate-limit |
| **P3 · Live Director** | director + products.yaml + test | Semua ✅ | 🟡 85% | Bug "1 clip per phase" = silence 9 menit |
| **Controller UI** | 5 komponen + 3 store | Semua ❌ | 🔴 0% | Tidak ada yang di-commit |
| **Config/Env** | .env.example + pyproject | Partial ⚠️ | 🟡 70% | Empty defaults + model salah |
| **Docs sync** | DOCS_HUB up-to-date | ❌ | 🔴 20% | Masih versi v0.1 tech stack |

**Overall v0.4: 60% selesai. Masih butuh ~3-5 hari kerja untuk siap jalan.**

---

## 🚨 BLOCKER — Harus Dikerjakan Dulu (Tidak Bisa Jalan Tanpa Ini)

### BLOCKER-1 · Audio Library kosong (0 clips)

**File**: `apps/worker/static/audio_library/index.json`

```json
{
  "version": "1.0",
  "clips": []
}
```

**Dampak**: `AudioLibraryManager.load()` berhasil tanpa error, tapi `clip_count = 0`. Semua WS command `audio.list`, `audio.play` return empty. Director `by_category("A_opening")` → `[]` → tidak ada audio yang diputar → **live silent 2 jam penuh**.

**Akar masalah**: `scripts/gen_audio_library.py` dan `.bat` **TIDAK ADA DI REPO** (HTTP 404). Tanpa script ini, tidak ada cara generate 108 clip .wav dari Cartesia.

**Fix wajib**:

- Commit `scripts/gen_audio_library.py` yang baca `config/clips_script.yaml`, panggil Cartesia TTS per clip, tulis `.wav` + append ke `index.json`.
- Commit `scripts/gen_audio_library.bat` wrapper Windows.
- Jalankan lokal: `scripts\gen_audio_library.bat` → hasilkan 108 file wav + populate index.json.
- **JANGAN commit file .wav ke git** (total bisa 100-200MB). Tambah ke `.gitignore`: `apps/worker/static/audio_library/*.wav`.

### BLOCKER-2 · Semua komponen Svelte v0.4 hilang

**File yang 404 di raw GitHub**:

- `apps/controller/src/lib/components/AudioLibraryGrid.svelte` ❌
- `apps/controller/src/lib/components/TwoHourTimer.svelte` ❌
- `apps/controller/src/lib/components/ReplySuggestions.svelte` ❌
- `apps/controller/src/lib/components/DecisionStream.svelte` ❌
- `apps/controller/src/lib/components/EmergencyStop.svelte` ❌
- `apps/controller/src/lib/stores/live_state.ts` ❌
- `apps/controller/src/lib/stores/audio_library.ts` ❌
- `apps/controller/src/lib/stores/decisions.ts` ❌

**Dampak**: Worker siap, command WS lengkap (40+ command), tapi **tidak ada UI untuk memencet tombol**. User tidak bisa: trigger live.start, pilih clip audio, lihat decision stream komentar, approve/reject reply suggestion, lihat timer 2 jam, emergency stop.

**Fix wajib**: Lihat §6 di bawah untuk skeleton siap-paste tiap komponen.

### BLOCKER-3 · clips_script.yaml hanya cover 3 produk dari 11+

**File**: `apps/worker/config/clips_script.yaml` — 108 clip, 8 kategori:

- A_opening (18) · B_paloma_demo (18) · B_paloma_cta (18) · C_pintu_lipat_demo (18) · C_pintu_lipat_cta (18) · D_tnw_demo (18) · D_tnw_cta (18) · E_reply_price (18) · Z_closing (16)

**Target spec (dari KIRO Handoff)**: 160 clip, 11 kategori termasuk `D_cctv_context`, `E_senter_context`, `F_tracker_context`, `G_question_hooks`, `H_price_safe`, `I_trust_safety`, `J_idle_human`.

**Yang hilang dari workspace offers DB** ([](https://www.notion.so/e18e17f63dee4cbfa33815957cb698ba?pvs=21)):

- [CCTV V380 Pro Dual Lens HD 360 Auto Tracking Two-Way](https://www.notion.so/CCTV-V380-Pro-Dual-Lens-HD-360-Auto-Tracking-Two-Way-35b2a324fba1479293ba5cae319b94ed?pvs=21) CCTV V380 · [CCTV Paket V380Pro USB + Memory Card](https://www.notion.so/CCTV-Paket-V380Pro-USB-Memory-Card-59c2633486234679b83deace5d79a04d?pvs=21) CCTV Paket · [CCTV X6 ZIOTW WiFi HD 1080P Motion Detection Night Vision](https://www.notion.so/CCTV-X6-ZIOTW-WiFi-HD-1080P-Motion-Detection-Night-Vision-f86b9327e6714782a73a8b8b2594e22b?pvs=21) CCTV X6
- [LED Senter XHP160 Super Terang 10M LM USB Type-C IPX6](https://www.notion.so/LED-Senter-XHP160-Super-Terang-10M-LM-USB-Type-C-IPX6-01292b0838594df8bd20c77cfc30c7cc?pvs=21) Senter XHP160
- [DINGS Smart GPS Tracker Bluetooth 5.2 Tahan Air](https://www.notion.so/DINGS-Smart-GPS-Tracker-Bluetooth-5-2-Tahan-Air-0241a05f88194358884de08e48e1ca53?pvs=21) DINGS Tracker
- [Aluflex Mesh Door – Pintu Nyamuk Geser Aluminium Magnetik](https://www.notion.so/Aluflex-Mesh-Door-Pintu-Nyamuk-Geser-Aluminium-Magnetik-1d47b85ed99e49c3907f7ccf7f2fbfa8?pvs=21) Aluflex · [Locksworth Brankas Digital Fingerprint VS4552](https://www.notion.so/Locksworth-Brankas-Digital-Fingerprint-VS4552-a31f5299d0b84f36b1a66f31971e49dd?pvs=21) Locksworth · [Reaim PVC Pintu Lipat Geser Free Survey](https://www.notion.so/Reaim-PVC-Pintu-Lipat-Geser-Free-Survey-f04d872355134ba28d694e1952db97ba?pvs=21) Reaim PVC

**Dampak**: Hanya 3 dari 11+ produk affiliate bisa di-cover. Live 2 jam akan kehabisan variasi audio → repetitif → penonton churn.

---

## 🐛 BUG — Tingkat HIGH (Harus di-fix Sebelum Live)

- <strong>BUG-1 · Director cuma play 1 clip per phase → silent 9 menit</strong>
    
    **File**: `apps/worker/src/banghack/core/orchestrator/director.py` baris ~160
    
    ```python
    # Play a clip for this phase (anti-repeat: prefer not-recently-played)
    clips = self._audio_manager.by_category(phase.clip_category)
    ...
    if candidates:
    	clip = random.choice(candidates)
    	asyncio.create_task(self._audio_adapter.play(clip.id))
    
    # Wait for phase duration
    elapsed_in_phase = 0
    while elapsed_in_phase < phase.duration_s:
    	...
    	await asyncio.sleep(1)
    ```
    
    **Masalah**: Phase `paloma_demo` durasi 600 detik. Kode pilih **1 clip** (~15-20 detik audio), lalu `asyncio.sleep` 600 detik tanpa play clip berikutnya. Hasil: **20 detik audio + 580 detik silence**.
    
    **Fix**: Loop play clip dengan interval dalam satu phase.
    
    ```python
    # Inside phase duration loop
    next_clip_at = 0
    while elapsed_in_phase < phase.duration_s:
    	if elapsed_in_phase >= next_clip_at and self._state.mode == LiveMode.RUNNING:
    		clips = self._audio_manager.by_category(phase.clip_category)
    		not_played = self._audio_manager.not_played_since(window_s=600)
    		candidates = [c for c in clips if c.id in {x.id for x in not_played}] or clips
    		if candidates:
    			clip = random.choice(candidates)
    			asyncio.create_task(self._audio_adapter.play(clip.id))
    			next_clip_at = elapsed_in_phase + max(20, clip.duration_ms // 1000) + 5  # gap 5s
    	await asyncio.sleep(1)
    	if self._state.mode != LiveMode.PAUSED:
    		elapsed_in_phase += 1
    ```
    
- <strong>BUG-2 · Suggester: templates breakwhen product kosong</strong>
    
    **File**: `apps/worker/src/banghack/core/orchestrator/suggester.py` baris ~60
    
    ```python
    replies = [
    	_safe(tmpl.get("formal", "").format(product=product, user=user)),
    	...
    ]
    ```
    
    **Masalah**: `main.py` cmd_reply_suggest menerima `product = str(p.get("product", "")).strip()` — default `""`. Template `"Harga {product} kompetitif"` → hasil `"Harga  kompetitif"` (double space, tanpa nama produk).
    
    **Fix**:
    
    ```python
    # Di suggester.py atau main.py
    product = product or "produk ini"
    user = user or "kak"
    ```
    
- <strong>BUG-3 · BudgetGuard tidak enforce rate limit</strong>
    
    **File**: `apps/worker/src/banghack/core/orchestrator/budget_guard.py`
    
    ```python
    def can_call(self) -> bool:
    	return not self._cost.is_over_budget()
    ```
    
    **Masalah**: Spec requirement: *"LLM max 1 req/8-15 detik + max 3 reply/user/10 menit"*. Implementasi cuma check total budget harian. Kalau komentar ramai (>100/menit), LLM bisa di-spam → cost spike dan rate-limit dari provider.
    
    **Fix**: Tambah `_last_call_ts`, `_per_user_calls: dict[str, list[float]]`, logika:
    
    ```python
    def can_call(self, user: str = "") -> bool:
    	now = time.time()
    	if self._cost.is_over_budget():
    		return False
    	if now - self._last_call_ts < self._min_gap_s:  # default 10s
    		return False
    	if user:
    		recent = [t for t in self._per_user_calls.get(user, []) if now - t < 600]
    		if len(recent) >= 3:
    			return False
    	return True
    ```
    
- <strong>BUG-4 · .env.example: path default kosong semua</strong>
    
    **File**: `.env.example`
    
    ```bash
    AUDIO_LIBRARY_DIR=
    CLIPS_SCRIPT_YAML=
    PRODUCTS_YAML=
    REPLY_TEMPLATES_YAML=
    ```
    
    **Masalah**: Worker jalan dengan `os.getenv("AUDIO_LIBRARY_DIR", "static/audio_library")` — fallback default oke, **tapi user yang copy `.env.example → .env` akan dapat empty string** → `Path("") / "index.json"` → nanti error silent.
    
    **Fix**:
    
    ```bash
    AUDIO_LIBRARY_DIR=static/audio_library
    CLIPS_SCRIPT_YAML=config/clips_script.yaml
    PRODUCTS_YAML=config/products.yaml
    REPLY_TEMPLATES_YAML=config/reply_templates.yaml
    ```
    
- <strong>BUG-5 · CARTESIA_MODEL pakai nilai deprecated</strong>
    
    **File**: `.env.example`
    
    ```bash
    CARTESIA_MODEL=sonic-indonesian
    ```
    
    **Masalah**: Cartesia deprecate `sonic-indonesian` awal 2026. Kode `main.py` cmd_test_cartesia_key default `sonic-3`. Tes dengan `.env.example` langsung → API error 404 model.
    
    **Fix**: `CARTESIA_MODEL=sonic-3`
    
- <strong>BUG-6 · DOCS_[HUB.md](http://HUB.md) tech stack drift parah</strong>
    
    **File**: `DOCS_HUB.md`
    
    Dokumen masih sebut:
    
    - `TikTokLive >=5.0.8, <6.0` ❌ (actual: `>=6.4.0`)
    - `LLM primary: DeepSeek` ❌ (actual: LiteLLM 3-tier dengan 9router primary)
    - `TTS: Edge-TTS` ❌ (actual: Cartesia primary + edge-tts fallback)
    
    **Dampak**: Agent coding baca DOCS_HUB → pakai versi lib lama → install gagal atau behavior beda.
    
    **Fix**: Update tabel "Tech Stack Resmi" supaya sync dengan `pyproject.toml` real.
    
- <strong>BUG-7 · Dataclass LiveState, CommentDecision, AudioJob hilang</strong>
    
    **Spec KIRO Handoff** definisi 3 dataclass:
    
    - `LiveState(session_id, mode, started_at, max_duration_s, reply_enabled, auto_voice_enabled, llm_enabled, tts_enabled, token_budget_remaining, ...)`
    - `CommentDecision(action, priority, reason, needs_llm, safe_category)`
    - `AudioJob(kind, priority, text, file_path, user, product)`
    
    **Actual**: Hanya `DirectorState` (7 field) di [director.py](http://director.py). `CommentDecision` dan `AudioJob` tidak ada.
    
    **Dampak**: WS event `comment.classified` emit dict ad-hoc, tidak ada type safety. Testing harder.
    
    **Fix**: Buat `apps/worker/src/banghack/core/models.py` dengan 3 dataclass, pakai di semua tempat.
    
- <strong>BUG-8 · Reply cache tidak pakai rapidfuzz meski sudah di-install</strong>
    
    **File**: `reply_cache.py` — implement `_cosine_similarity` manual dengan `collections.Counter`.
    
    `pyproject.toml`: `rapidfuzz>=3.9.0` ✅ installed tapi tidak dipakai.
    
    **Dampak**: Cosine-similarity whitespace-tokenized tidak robust terhadap typo, case variation, urutan kata. Spec minta `rapidfuzz.fuzz.token_sort_ratio` atau `partial_ratio`.
    
    **Fix**:
    
    ```python
    from rapidfuzz import fuzz
    
    def _similarity(a: str, b: str) -> float:
    	return fuzz.token_sort_ratio(a.lower(), b.lower()) / 100.0
    ```
    

---

## ⚠️ BUG — Tingkat MEDIUM (Boleh Ditunda Setelah MVP Jalan)

| # | File | Masalah | Fix singkat |
| --- | --- | --- | --- |
| M1 | `llm_fallback.py` | Cache module-level global dict — tidak thread-safe, tidak reset-able | Wrap dalam class `LLMFallbackClassifier`, inject instance |
| M2 | `rules.py` | Intent `product_question` hilang (spec meminta 7 intent) | Tambah kategori untuk "fitur apa", "warna apa", "ukuran apa" |
| M3 | `suggester.py` | `.format()` crash kalau template ada `{` tak ber-pasangan | Pakai `.format_map(defaultdict(str))` |
| M4 | `audio_library.py` adapter | `sd.stop()` blocking, tidak async | Wrap dalam `run_in_executor` |
| M5 | `director.py` emergency_stop | Tidak cancel `_run_task` dengan timeout — bisa gantung kalau `sd.wait()` aktif | `await asyncio.wait_for(self._run_task, timeout=0.5)` |
| M6 | `main.py` reply.approve | Tidak re-check output safety sebelum TTS | Pass `_safe()` filter sebelum `tts.speak()` |
| M7 | `reply_cache.py` | In-memory, hilang saat restart | Tambah persist ke `.cache/replies.json` on shutdown |
| M8 | `products.yaml` | Hanya 3 produk, skip CCTV/Senter/Tracker | Extend sesuai BLOCKER-3 |
| M9 | `main.py` | `handle_comment` selalu emit WS event meski DRY_RUN=true | Tambah flag check |
| M10 | `audio_library/manager.py` | `by_product("paloma")` cuma string match → salah match kalau produk nama mengandung substring | Gunakan exact tag match |
| M11 | Tests | Tidak ada integration test end-to-end (worker + WS + director + audio) | Buat `tests/test_integration_live.py` |
| M12 | `clips_script.yaml` | Field `text` tapi manager baca `script` (ada fallback, tapi tidak konsisten) | Rename semua jadi `script` (atau sebaliknya) |

---

## ✅ Yang Sudah BAIK (Layak Diapresiasi)

- **40+ WS command handler** terregister di [main.py](http://main.py) dengan error-wrapper pattern — robust.
- **`/health` FastAPI endpoint** lengkap report audio_ready, classifier_ready, director_ready, budget_remaining → bonus yang tidak di-spec.
- **Test coverage**: `test_audio_library`, `test_classifier_rules`, `test_reply_cache`, `test_director_state` semua ada dan param-driven.
- **Classifier rules**: 10 intent + forbidden_contact + forbidden_link + spam + empty. Coverage bahasa gaul Indonesia bagus ("ready", "gimana", "cocok buat", dll).
- **Budget guard snapshot** integrate dengan metrics heartbeat — operator bisa monitor real-time.
- **Hot-reload index.json** — edit library tanpa restart worker.
- **Hard-stop 2 jam** implemented dengan dua check: `elapsed >= max_duration_s` di run_loop + tick_loop.
- **Template fallback** di suggester — kalau LLM gagal/budget habis, masih balas pakai template.
- **Output safety filter** (`_UNSAFE_PATTERNS`) — strip link, WA, nomor HP, harga Rp dari LLM output sebelum kirim.

---

## 🛠️ COMPLETION PLAN — 5 Hari Kerja

### Hari 1 · Unblock Audio Library (4-6 jam)

**Deliverable**: `scripts/gen_audio_library.py` + `.bat` committed, 108 .wav ter-generate, index.json populated.

```python
# scripts/gen_audio_library.py — skeleton
import asyncio
import json
import os
from pathlib import Path
import yaml
import httpx
from dotenv import load_dotenv

load_dotenv()

CLIPS_YAML = Path("apps/worker/config/clips_script.yaml")
OUT_DIR = Path("apps/worker/static/audio_library")
INDEX_JSON = OUT_DIR / "index.json"
API_KEY = os.environ["CARTESIA_API_KEYS"].split(",")[0]
VOICE_ID = os.environ["CARTESIA_VOICE_ID"]
MODEL = os.environ.get("CARTESIA_MODEL", "sonic-3")

async def gen_one(client, clip):
	out_path = OUT_DIR / f"{clip['id']}.wav"
	if out_path.exists():
		return {"id": clip["id"], "skipped": True}
	r = await client.post(
		"https://api.cartesia.ai/tts/bytes",
		headers={
			"Cartesia-Version": "2026-03-01",
			"X-API-Key": API_KEY,
			"Content-Type": "application/json",
		},
		json={
			"model_id": MODEL,
			"transcript": clip["text"],
			"voice": {"mode": "id", "id": VOICE_ID},
			"language": "id",
			"output_format": {"container": "wav", "encoding": "pcm_f32le", "sample_rate": 44100},
			"experimental_controls": {"emotions": [clip.get("emotion", "neutral")]},
		},
	)
	r.raise_for_status()
	out_path.write_bytes(r.content)
	size = len(r.content)
	duration_ms = int(size / (44100 * 4) * 1000)
	return {
		"id": clip["id"], "category": clip["category"],
		"tags": clip.get("tags", []),
		"duration_ms": duration_ms,
		"voice_id": VOICE_ID,
		"script": clip["text"],
		"scene_hint": clip["category"],
		"file_path": f"{clip['id']}.wav",
	}

async def main():
	OUT_DIR.mkdir(parents=True, exist_ok=True)
	data = yaml.safe_load(CLIPS_YAML.read_text(encoding="utf-8"))
	clips = data["clips"]
	print(f"Generating {len(clips)} clips...")
	async with httpx.AsyncClient(timeout=30) as client:
		index_entries = []
		for i, clip in enumerate(clips):
			try:
				entry = await gen_one(client, clip)
				if "skipped" not in entry:
					index_entries.append(entry)
					print(f"[{i+1}/{len(clips)}] {clip['id']} ({entry['duration_ms']}ms)")
				else:
					print(f"[{i+1}/{len(clips)}] {clip['id']} SKIPPED (exists)")
				await asyncio.sleep(0.5)  # rate limit
			except Exception as e:
				print(f"[{i+1}/{len(clips)}] {clip['id']} FAILED: {e}")
	INDEX_JSON.write_text(json.dumps({"version": "1.0", "clips": index_entries}, indent=2))
	print(f"\n✓ Wrote {len(index_entries)} entries to {INDEX_JSON}")

if __name__ == "__main__":
	asyncio.run(main())
```

```bash
REM scripts/gen_audio_library.bat
@echo off
cd /d %~dp0..
uv run --directory apps/worker python ../../scripts/gen_audio_library.py
pause
```

**Acceptance**: Run script → 108 .wav file di `apps/worker/static/audio_library/`. Restart worker → `/health` shows `audio_library_clip_count: 108`.

### Hari 2 · Svelte Controller Components (6-8 jam)

**Deliverable**: 5 komponen + 3 store + wire ke `/live` route.

**Skeleton prioritas (buat urutan ini)**:

1. `src/lib/stores/live_state.ts` — subscribe ke WS `live.state` + `live.tick`.
2. `src/lib/stores/decisions.ts` — append-only ring buffer untuk `comment.classified` events.
3. `src/lib/stores/audio_library.ts` — fetch `audio.list` sekali + subscribe `audio.now`/`audio.done`.
4. `TwoHourTimer.svelte` — display elapsed/remaining, color change <10min.
5. `EmergencyStop.svelte` — tombol merah besar, confirm dialog, call `live.emergency_stop`.
6. `AudioLibraryGrid.svelte` — grid kategori → klik = `audio.play`.
7. `DecisionStream.svelte` — log scrollable decision events.
8. `ReplySuggestions.svelte` — card 3 pilihan, approve/reject/regen.

**Skeleton `live_state.ts`**:

```tsx
import { writable, type Writable } from 'svelte/store';
import { wsClient } from '$lib/api/ws';

export interface LiveState {
	mode: 'IDLE' | 'RUNNING' | 'PAUSED' | 'STOPPED';
	phase: string;
	phase_idx: number;
	phase_total: number;
	product: string;
	elapsed_s: number;
	remaining_s: number;
}

const initial: LiveState = {
	mode: 'IDLE', phase: '', phase_idx: 0, phase_total: 0,
	product: '', elapsed_s: 0, remaining_s: 7200,
};

export const liveState: Writable<LiveState> = writable(initial);

wsClient.on('live.state', (ev) => liveState.set({ ...ev }));
wsClient.on('live.tick', (ev) => liveState.update(s => ({
	...s, elapsed_s: ev.elapsed_s, remaining_s: ev.remaining_s,
	mode: ev.mode, phase: ev.phase, product: ev.product,
})));

export const startLive = () => wsClient.cmd('live.start');
export const pauseLive = () => wsClient.cmd('live.pause');
export const resumeLive = () => wsClient.cmd('live.resume');
export const stopLive = () => wsClient.cmd('live.stop');
export const emergencyStop = () => wsClient.cmd('live.emergency_stop', { operator_id: 'ui' });
```

**Skeleton `TwoHourTimer.svelte`**:

```
<script lang="ts">
	import { liveState } from '$lib/stores/live_state';
	let { } = $props();

	function fmt(s: number): string {
		const h = Math.floor(s / 3600);
		const m = Math.floor((s % 3600) / 60);
		const sec = s % 60;
		return `${h}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;
	}

	let color = $derived(
		$liveState.remaining_s < 600 ? 'text-red-500' :
		$liveState.remaining_s < 1800 ? 'text-yellow-500' :
		'text-green-500'
	);
</script>

<div class="rounded-lg border p-4 font-mono">
	<div class="text-xs uppercase text-gray-500">Remaining</div>
	<div class="text-4xl {color}">{fmt($liveState.remaining_s)}</div>
	<div class="text-xs text-gray-400 mt-1">Elapsed: {fmt($liveState.elapsed_s)} / 2:00:00</div>
	<div class="text-xs">Mode: <b>{$liveState.mode}</b> · Phase: {$liveState.phase} ({$liveState.phase_idx+1}/{$liveState.phase_total})</div>
</div>
```

**Skeleton `EmergencyStop.svelte`**:

```
<script lang="ts">
	import { emergencyStop } from '$lib/stores/live_state';
	let confirming = $state(false);
	async function confirm() {
		await emergencyStop();
		confirming = false;
	}
</script>

{#if !confirming}
	<button class="bg-red-600 hover:bg-red-700 text-white font-bold py-4 px-8 rounded-lg text-xl" onclick={() => confirming = true}>
		🛑 EMERGENCY STOP
	</button>
{:else}
	<div class="bg-red-900/20 border-2 border-red-600 p-4 rounded">
		<p class="mb-2 font-bold">Yakin stop live sekarang?</p>
		<button class="bg-red-600 text-white px-4 py-2 rounded mr-2" onclick={confirm}>Ya, STOP</button>
		<button class="bg-gray-300 px-4 py-2 rounded" onclick={() => confirming = false}>Batal</button>
	</div>
{/if}
```

**Acceptance**: Route `/live` render 5 komponen. Click `🛑` → WS command terkirim → director stop dalam <500ms.

### Hari 3 · Fix HIGH bugs + Extend clips library (6-8 jam)

- Fix BUG-1 (director clip-loop per phase)
- Fix BUG-2 (product fallback string)
- Fix BUG-3 (BudgetGuard rate limit)
- Fix BUG-4 (.env.example path defaults)
- Fix BUG-5 (CARTESIA_MODEL)
- Fix BUG-6 (DOCS_HUB sync)
- Fix BUG-8 (pakai rapidfuzz)
- Extend `clips_script.yaml`: tambah 50+ clip CCTV/Senter/Tracker
- Re-run `gen_audio_library.bat`

### Hari 4 · Data models + Integration test (4-6 jam)

- Buat `apps/worker/src/banghack/core/models.py` dengan `LiveState`, `CommentDecision`, `AudioJob`.
- Refactor [main.py](http://main.py) + [director.py](http://director.py) + classifier pakai model ini.
- Buat `tests/test_integration_live.py`: dry-run 5 menit dengan mock TikTok feed.
- Verify semua `decision.*`, `audio.*`, `live.*` event jalan.

### Hari 5 · Dress rehearsal + Polish (4-6 jam)

- Full 30 menit dry-run dengan virtual camera OBS.
- Monitor `/health`, metrics broadcast, cost.
- Fix issue yang muncul.
- Update [📝 05 · CHANGELOG (Keep a Changelog)](https://www.notion.so/05-CHANGELOG-Keep-a-Changelog-cba7dd8becd94e3b820671a0d959bac7?pvs=21) CHANGELOG v0.4 shipped.
- Tag release `v0.4.0`.

---

## 📋 Definition of Done v0.4

- [ ]  `scripts/gen_audio_library.py` + `.bat` committed.
- [ ]  `apps/worker/static/audio_library/index.json` berisi ≥108 entry.
- [ ]  5 komponen Svelte + 3 store committed di `apps/controller/`.
- [ ]  `.env.example` path default tidak kosong.
- [ ]  `CARTESIA_MODEL=sonic-3`.
- [ ]  `DOCS_HUB.md` tech stack table sync dengan `pyproject.toml`.
- [ ]  Director play minimal 1 clip per 30 detik saat phase aktif.
- [ ]  BudgetGuard enforce min_gap_s + per-user rate limit.
- [ ]  Reply template product fallback `"produk ini"` kalau kosong.
- [ ]  `LiveState`, `CommentDecision`, `AudioJob` dataclass di `core/models.py`.
- [ ]  Reply cache pakai `rapidfuzz.fuzz.token_sort_ratio`.
- [ ]  Integration test 5-menit dry-run hijau.
- [ ]  30 menit dress rehearsal dengan OBS virtual camera sukses.
- [ ]  `/health` return `status: ok` (audio_ready + classifier_ready + director_ready).

---

## 🎯 Prompt Siap-Paste ke Agent Lokal

Copy ini ke chat agent lokal (Cursor/Claude Code/Windsurf):

```
Baca https://www.notion.so/9e5d4d30289240c3bc229e7a66c036b7 dan dokumen ini. Kerjakan berurut:

1. BLOCKER-1 dulu: commit scripts/gen_audio_library.py + .bat sesuai skeleton di §Hari 1. 
   Lalu jalankan → verifikasi index.json populated.

2. BLOCKER-2: commit 5 komponen Svelte + 3 store sesuai skeleton di §Hari 2.
   Wire semua ke src/routes/live/+page.svelte.

3. Fix HIGH bugs urut BUG-1 → BUG-8 sesuai §Hari 3.

4. Buat core/models.py dengan LiveState, CommentDecision, AudioJob (§Hari 4).

5. Run pytest — semua hijau. Run dress rehearsal 5 menit.

Setiap ticket = 1 commit. Prefix: [v0.4][fix:XXX] atau [v0.4][feat:XXX].
Kalau ada yang tidak jelas dari skeleton, STOP dan tanya — jangan asumsi.
Guardrail wajib: jangan ubah behavior v0.3 (reply_enabled=false default, dry_run=true default).
```

---

## 📎 Referensi

- Spec asli: [🛠️ 16 · KIRO Handoff — v0.4 Build Spec (Full Skeleton)](https://www.notion.so/16-KIRO-Handoff-v0-4-Build-Spec-Full-Skeleton-9e5d4d30289240c3bc229e7a66c036b7?pvs=21)
- Live plan: [🎙️ Live Interaction Plan — 2 Jam Cartesia, Produk, Scene, Retensi](https://www.notion.so/Live-Interaction-Plan-2-Jam-Cartesia-Produk-Scene-Retensi-1267e9d752fa48ad847d1b2e778644a7?pvs=21)
- Orchestrator plan: [🧠 Orchestrator Implementation Plan — Python Worker + Svelte Control Center](https://www.notion.so/Orchestrator-Implementation-Plan-Python-Worker-Svelte-Control-Center-ebeaa1b997794405bad652a133f2afbe?pvs=21)
- Offers DB: [](https://www.notion.so/e18e17f63dee4cbfa33815957cb698ba?pvs=21)
- Repo: `dedy45/livetik@master`
- Commit yang direview: HEAD of master per 2026-04-23