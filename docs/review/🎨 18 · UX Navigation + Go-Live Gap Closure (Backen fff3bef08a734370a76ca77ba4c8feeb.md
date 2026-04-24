# 🎨 18 · UX Navigation + Go-Live Gap Closure (Backend + Frontend)

> **Tanggal**: 2026-04-24 · **Status basis**: Setelah user push fix batch pertama pasca [🔬 17 · v0.4 Implementation Review — Bugs, Gaps & Completion Plan](https://www.notion.so/17-v0-4-Implementation-Review-Bugs-Gaps-Completion-Plan-3b7aa241f5284b99bd6819d091b7f067?pvs=21)
> 

> **Verdict singkat**: **7 bug code sudah fixed** ✅. Tapi ada **1 bug build-crash baru** karena root `+page.svelte` mengimpor komponen yang belum ada. Audio library masih kosong, 5 komponen + 3 store masih 404. UX harus dipecah — Dashboard jangan ditaburi semua fitur, Live Cockpit dedicated page adalah jawabannya.
> 

---

## ✅ Re-Audit: Yang Sudah Diperbaiki (Hasil Push Terbaru)

| ID | Item | File | Status |
| --- | --- | --- | --- |
| BUG-2 | Product/user fallback kosong break template | `suggester.py` | 🟢 **FIXED** — `product = product or "produk ini"`, `user = user or "kak"` |
| BUG-4 | .env.example path default kosong | `.env.example` | 🟢 **FIXED** — `AUDIO_LIBRARY_DIR=static/audio_library` dan 3 path lain populated |
| BUG-7 | Dataclass LiveState/CommentDecision/AudioJob hilang | `core/models.py` | 🟢 **FIXED** — 3 dataclass + 3 enum (LiveMode, CommentAction, AudioJobKind) commited dengan schema lengkap |
| BUG-6 | DOCS_HUB tech stack drift | `DOCS_HUB.md` | 🟡 **PARTIAL** — tech stack table sudah sync (LiteLLM, Cartesia sonic-3, TikTokLive ≥6.4.0), tapi folder structure masih v0.1 (belum sebutkan `core/orchestrator/`, `core/audio_library/`, `core/models.py`, `ipc/http_server.py`) |

**Impact positif**: Worker backend sekarang berkualitas production-grade. Kalau audio library sudah ada, worker bisa jalan 2 jam tanpa silent gap dan budget aman.

---

## 🚨 Bug Kritis BARU: Build akan CRASH

<aside>
💥

**File**: `apps/controller/src/routes/+page.svelte`

Baris 2-7 mengimpor 5 komponen baru:

```jsx
import AudioLibraryGrid from '$lib/components/AudioLibraryGrid.svelte';
import DecisionStream from '$lib/components/DecisionStream.svelte';
import ReplySuggestions from '$lib/components/ReplySuggestions.svelte';
import TwoHourTimer from '$lib/components/TwoHourTimer.svelte';
import EmergencyStop from '$lib/components/EmergencyStop.svelte';
```

Tapi **kelima file ini masih 404 di raw GitHub**. Begitu user `pnpm dev`, Vite akan langsung error `Failed to resolve import`.

**Quick fix sementara** (sampai komponen benar-benar dibuat): comment-out 5 import + tag JSX yang pakai. Atau lebih baik — commit 5 komponen skeleton ASAP sesuai dokumen [🔬 17 · v0.4 Implementation Review — Bugs, Gaps & Completion Plan](https://www.notion.so/17-v0-4-Implementation-Review-Bugs-Gaps-Completion-Plan-3b7aa241f5284b99bd6819d091b7f067?pvs=21) §Hari 2.

</aside>

---

## 🚫 Yang BELUM Diperbaiki (Masih Blocker Go-Live)

| ID | Item | Status | Blocker level | B1-A | `scripts/gen_audio_library.py` | ❌ **404** | 🔴 Critical |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B1-B | `scripts/gen_audio_library.bat` | ❌ **404** | 🔴 Critical | B1-C | `static/audio_library/index.json` | 🚨 masih `{"clips": []}` | 🔴 Critical |
| B2-A | `AudioLibraryGrid.svelte` | ❌ 404 | 🔴 Critical (crashes build) | B2-B | `TwoHourTimer.svelte` | ❌ 404 | 🔴 Critical |
| B2-C | `EmergencyStop.svelte` | ❌ 404 | 🔴 Critical | B2-D | `ReplySuggestions.svelte` | ❌ 404 | 🔴 Critical |
| B2-E | `DecisionStream.svelte` | ❌ 404 | 🔴 Critical | B2-F | `lib/stores/live_state.ts` | ❌ 404 | 🔴 Critical |
| B2-G | `lib/stores/audio_library.ts` | ❌ 404 | 🔴 Critical | B2-H | `lib/stores/decisions.ts` | ❌ 404 | 🔴 Critical |
| B3-A | `clips_script.yaml` — CCTV/Senter/Tracker kategori | ⚠️ 3/11+ produk | 🟡 High | B3-B | `products.yaml` runsheet hanya 3 produk | ⚠️ runsheet 50 menit loop | 🟡 High |
| B6 | DOCS_HUB folder structure | ⚠️ partial | 🟢 Medium (kosmetik) | NEW | Layout version label `v0.1.0-dev` | ⚠️ masih v0.1 | 🟢 Medium |

---

## 🎨 UX Navigation — Apakah Perlu Page Khusus?

**Jawab singkat**: **Ya, 100% harus page khusus.** Root `/` (Dashboard) sekarang sudah dipenuhi 11 section (System Health, Status, Viewers, Comments, Replies, Latency, Cost, Events, Reply Feed, Budget, LLM Models, Live Comments). Menambahkan 5 komponen v0.4 (AudioLibraryGrid + TwoHourTimer + ReplySuggestions + DecisionStream + EmergencyStop) di tempat yang sama = **overcrowded dashboard** yang bikin host panik saat 2 jam live.

### Masalah desain saat ini

1. **Dashboard = dumping ground**. 11 section dalam 1 page = scroll panjang, fokus pecah.
2. **`/live` sekarang passive**. Cuma filter event (comment/gift/join/like), tidak ada tombol kontrol session.
3. **Tidak ada keyboard shortcut** untuk approve reply cepat (host harus drag mouse saat live).
4. **EmergencyStop tidak sticky** — kalau scroll ke bawah, tombol hilang (bahaya saat live bermasalah).

### Rekomendasi Information Architecture

| Route | Nama | Purpose | Status sekarang | `/` | **Dashboard** | Overview health + quick-start button ke /live. JANGAN taruh komponen live di sini. | 🔴 Refactor: hapus import v0.4 komponen, tambah tombol "Mulai Live Session →" |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/live` | **Live Cockpit** 🎙️ | THE page untuk kontrol 2 jam live. Ganti dari passive monitor jadi active controller. | 🔴 Redesign total | `/library` | **Audio Library** 🎵 (baru) | Kelola 108+ clip: preview, stats play-count, regenerate missing. | 🆕 Buat baru |
| `/errors` | **Errors** ⚠️ | Error log + notification history | 🟢 Sudah ada (tidak berubah) | `/persona` | **Persona** 🎭 | Edit [persona.md](http://persona.md)  • preview | 🟢 Sudah ada (tidak berubah) |
| `/config` | **Config** ⚙️ | LLM tiers, TTS voices, feature flags, products+runsheet editor | 🟡 Tambah: YAML editor untuk products/clips/templates | `/cost` | **Cost** 💰 | Budget detail + historical cost | 🟢 Sudah ada (tidak berubah) |

**Sidebar nav sudah di-setup di `+layout.svelte`** — cukup tambah 1 item baru `/library`:

```jsx
const nav = [
	{ href: '/', label: 'Dashboard', icon: '📊' },
	{ href: '/live', label: 'Live Cockpit', icon: '🎙️' },  // rename dari 'Live Monitor'
	{ href: '/library', label: 'Audio Library', icon: '🎵' },  // ← BARU
	{ href: '/errors', label: 'Errors', icon: '⚠️' },
	{ href: '/persona', label: 'Persona', icon: '🎭' },
	{ href: '/config', label: 'Config', icon: '⚙️' },
	{ href: '/cost', label: 'Cost', icon: '💰' }
];
```

Juga update version label `v0.1.0-dev → v0.4.0-dev`.

---

## 🎙️ Live Cockpit — Redesign Detail (File: `/live/+page.svelte`)

**Layout 3-panel + sticky top-bar**:

```
┌──────────────────────────────────────────────────────────────────────────┐
│  [⏱️ 1:23:45 remaining]  [RUNNING · paloma_demo · 2/8]   [🛑 EMERGENCY]  │ ← sticky top
├─────────────────┬────────────────────────────┬───────────────────────────┤
│ RUNSHEET        │ COMMENT STREAM             │ METRICS                   │
│ ▶ paloma_demo   │ 19:23 @rina_k              │ 👁 viewers: 234           │
│   paloma_cta    │  "cara instalnya gmn?"     │ 💬 comments: 127          │
│   pintu_demo    │  [intent: question]        │ 🤖 replies: 31            │
│                 │                            │ 💰 Rp 3.240 / 50.000      │
│ NOW PLAYING     │ 19:24 @budi                │                           │
│ 🎵 B_paloma_013 │  "harga berapa ka?"        │ LLM tier: 9router         │
│ "Material anti- │  [intent: price_question]  │ Cache hit: 42%            │
│  karat..."      │                            │                           │
│                 ├────────────────────────────┤ ACTIONS                   │
│ QUICK CATEGORY  │ REPLY SUGGESTIONS          │ [⏸ Pause]  [▶ Resume]     │
│ [A_opening]     │ ┌──────────────────────┐   │ [⏭ Skip phase]           │
│ [B_paloma_demo] │ │ 1. Halo kak, harga   │   │                           │
│ [C_pintu_demo]  │ │    cek di bio ya 😊  │   │                           │
│ [D_tnw_demo]    │ │ 2. Makasih kak! Cek  │   │                           │
│ [E_reply_price] │ │    keranjang untuk   │   │                           │
│ [Z_closing]     │ │    harga live hari   │   │                           │
│                 │ │    ini.              │   │                           │
│ AUDIO QUEUE     │ │ 3. Halo! Yuk cek     │   │                           │
│ 1. B_014 (12s)  │ │    produk kami!      │   │                           │
│ 2. B_018 (15s)  │ └──────────────────────┘   │                           │
│                 │ [A]pprove 1  [S]-2  [D]-3 │                           │
│                 │ [Q] Reject   [W] Regen    │                           │
└─────────────────┴────────────────────────────┴───────────────────────────┘
```

### Prinsip UX kritis

1. **Top bar always sticky** — `position: sticky; top: 0` — timer + mode + emergency tidak boleh hilang saat scroll.
2. **TwoHourTimer color semantic**:
    - Green: `remaining > 1800s` (>30 min)
    - Yellow: `remaining < 1800s` (<30 min)
    - Red + pulse: `remaining < 600s` (<10 min)
3. **EmergencyStop**: tombol merah besar 80px height, ikon 🛑. Single-click = confirm dialog → 2nd click = fire. Kalau sudah RUNNING dan user tekan selama >1 detik = bypass confirm (deadman switch untuk emergency beneran).
4. **Comment Stream**: auto-scroll bottom; pause-on-hover; intent chip colored (question=blue, buying_intent=green, forbidden=red, spam=gray).
5. **Reply Suggestions card**: 3 opsi tampil sekaligus; highlight Return key arrow; "cached" badge kalau dari cache (biar host tahu ini sudah dipake sebelumnya).
6. **Keyboard shortcuts** wajib:
    - `A` = Approve reply option 1
    - `S` = Approve reply option 2
    - `D` = Approve reply option 3
    - `Q` = Reject (skip)
    - `W` = Regenerate (new LLM call)
    - `Space` = Pause/Resume live session
    - `1`–`9` = Play quick-category clip (1=A_opening, 2=B_paloma_demo, dst)
    - `Esc` = Focus escape (blur input)
    - `Ctrl+Shift+X` = Emergency stop (keyboard fallback)

### WebSocket events yang di-consume di `/live`

| Event | Handler | UI update | `live.state` | `liveState.set()` | Update mode badge, phase, product |
| --- | --- | --- | --- | --- | --- |
| `live.tick` (tiap 30s) | `liveState.update({elapsed, remaining})` | Refresh timer countdown | `director.warning` | Toast + warn sound | Banner "10 menit tersisa!" |
| `comment.classified` | `decisions.append()` | Append ke Comment Stream dengan intent chip | `classifier.llm_used` | update classifier metric | Badge "LLM call" pada comment terkait |
| `audio.now` | `currentClip.set()` | Update Now Playing widget | `audio.done` | `currentClip.set(null)` | Clear Now Playing |
| `reply.suggested` | `replyQueue.set(replies)` | Show 3 cards | `reply.approved` / `rejected` | clear cards | Hide suggestions |
| `guardrail.blocked` | Toast warning | Banner "LLM blocked: {reason}" | `director.emergency_stopped` | Modal + stop sound | Modal konfirmasi session stopped |

---

## 📄 `/library` — Audio Library Manager (Baru)

**Tujuan**: Tempat host/operator kelola 108+ clip sebelum & saat live.

**Layout**:

- **Filter bar**: kategori dropdown, produk dropdown, tag search, "not played recently" toggle
- **Grid**: card per clip dengan: ID, kategori chip, script preview (2 baris), duration_ms, last_played_ts, play_count, tombol 🔊 preview + ▶ play-live
- **Bulk actions**: Regenerate selected (re-TTS via Cartesia), Delete, Export script-only
- **Stats panel**: Total clips, distribution per category, avg duration, top 10 most-played, bottom 10 never-played

**Kenapa penting?** Host mau variasi — kalau satu clip sudah diplay 3x dalam 30 menit, harus tahu dan bisa switch manual ke clip lain. Saat ini tidak ada visibility sama sekali.

---

## 🔧 Backend Gaps (Untuk Bisa Live)

- <strong>G1 · Audio Library generator script (CRITICAL)</strong>
    
    **File belum ada**: `scripts/gen_audio_library.py` + `scripts/gen_audio_library.bat`
    
    **Fungsi wajib**:
    
    - Baca `config/clips_script.yaml`
    - Loop per clip → call Cartesia TTS API
    - Tulis `.wav` ke `apps/worker/static/audio_library/{id}.wav`
    - Append metadata (id, category, tags, duration_ms, voice_id, script, file_path) ke `index.json`
    - Skip kalau file sudah ada (idempotent)
    - Rate-limit 0.5s per request (biar tidak kena 429)
    - Error handling: kalau 1 clip gagal, log + continue, jangan crash total
    
    **Skeleton lengkap** sudah ada di [🔬 17 · v0.4 Implementation Review — Bugs, Gaps & Completion Plan](https://www.notion.so/17-v0-4-Implementation-Review-Bugs-Gaps-Completion-Plan-3b7aa241f5284b99bd6819d091b7f067?pvs=21) §Hari 1.
    
    **Validasi setelah jalan**:
    
    ```bash
    curl -s http://localhost:8766/health | jq '.audio_ready, .audio_library_clip_count'
    # Output yang diharapkan: true, 108
    ```
    
- <strong>G2 · Extend library untuk 8 produk sisa (HIGH)</strong>
    
    **Target**: Tambah 7-8 kategori baru di `clips_script.yaml` dan product baru di `products.yaml`:
    
    - `D_cctv_demo` + `D_cctv_cta` untuk [CCTV V380 Pro Dual Lens HD 360 Auto Tracking Two-Way](https://www.notion.so/CCTV-V380-Pro-Dual-Lens-HD-360-Auto-Tracking-Two-Way-35b2a324fba1479293ba5cae319b94ed?pvs=21) / [CCTV X6 ZIOTW WiFi HD 1080P Motion Detection Night Vision](https://www.notion.so/CCTV-X6-ZIOTW-WiFi-HD-1080P-Motion-Detection-Night-Vision-f86b9327e6714782a73a8b8b2594e22b?pvs=21) / [CCTV Paket V380Pro USB + Memory Card](https://www.notion.so/CCTV-Paket-V380Pro-USB-Memory-Card-59c2633486234679b83deace5d79a04d?pvs=21)
    - `E_senter_demo` + `E_senter_cta` untuk [LED Senter XHP160 Super Terang 10M LM USB Type-C IPX6](https://www.notion.so/LED-Senter-XHP160-Super-Terang-10M-LM-USB-Type-C-IPX6-01292b0838594df8bd20c77cfc30c7cc?pvs=21)
    - `F_tracker_demo` + `F_tracker_cta` untuk [DINGS Smart GPS Tracker Bluetooth 5.2 Tahan Air](https://www.notion.so/DINGS-Smart-GPS-Tracker-Bluetooth-5-2-Tahan-Air-0241a05f88194358884de08e48e1ca53?pvs=21)
    - `G_question_hooks` (10 clips) — reaction saat viewer nanya, buy-me time
    - `H_price_safe` (10 clips) — deflect pertanyaan harga ke bio (anti-penalty)
    - `I_trust_safety` (10 clips) — testimoni, garansi, review klaim
    - `J_idle_human` (10 clips) — filler manusiawi saat gap ("lagi atur kamera dulu ya")
    
    **Runsheet extend** di `products.yaml`: tambah 10 phase baru untuk cover full 2 jam tanpa loop.
    
    **Dampak kalau tidak**: live 2 jam akan 3x loop runsheet 50 menit → repetitif → viewer churn.
    
- <strong>G3 · audio.queue + live.switch_product WS commands (MEDIUM)</strong>
    
    **File**: `apps/worker/src/banghack/ipc/main.py`
    
    Saat ini sudah ada 14 command, tapi UI `/library` butuh:
    
    - `audio.queue` — queue clip untuk main setelah clip sekarang selesai (bukan barge-in)
    - `live.switch_product` — paksa pindah ke phase produk tertentu ("sekarang bahas CCTV")
    
    Implementasi: director.switch_product(product_id) → find phase index → set phase_idx → break current phase loop.
    
- <strong>G4 · WS event naming konsistensi (MEDIUM)</strong>
    
    Spec sebut event `decision.*` tapi classifier emit `comment.classified` / `classifier.llm_used`.
    
    Pilih satu standar. Saya rekomen: **tetap `comment.classified`** (sudah working), tapi dokumentasikan di DOCS_HUB sebagai canonical.
    
- <strong>G5 · Hard-stop di runsheet end + warn-before-loop (LOW)</strong>
    
    Saat ini runsheet loops infinitely via `phase_idx % len(runsheet)`. Untuk 2 jam dengan runsheet 50 menit → loop 2.4x.
    
    Better: emit warning "runsheet loop ke-N" biar host aware, dan kalau `phase_idx >= len(runsheet) * 2`, hentikan (anti edge-case).
    

---

## 🎨 Frontend Gaps (Untuk Bisa Live)

- <strong>G6 · 5 Svelte components + 3 stores (CRITICAL, blocks build)</strong>
    
    **Skeleton lengkap** ada di [🔬 17 · v0.4 Implementation Review — Bugs, Gaps & Completion Plan](https://www.notion.so/17-v0-4-Implementation-Review-Bugs-Gaps-Completion-Plan-3b7aa241f5284b99bd6819d091b7f067?pvs=21) §Hari 2. Ditambah:
    
    **`ReplySuggestions.svelte`** skeleton:
    
    ```jsx
    <script lang="ts">
    	import { replyQueue, approveReply, rejectReply, regenReply } from '$lib/stores/replies';
    	import { onMount } from 'svelte';
    
    	onMount(() => {
    		const onKey = (e: KeyboardEvent) => {
    			if (e.key === 'a') approveReply(0);
    			if (e.key === 's') approveReply(1);
    			if (e.key === 'd') approveReply(2);
    			if (e.key === 'q') rejectReply();
    			if (e.key === 'w') regenReply();
    		};
    		window.addEventListener('keydown', onKey);
    		return () => window.removeEventListener('keydown', onKey);
    	});
    </script>
    
    {#if $replyQueue.length === 0}
    	<div class="text-gray-500 italic">Tidak ada reply suggestion…</div>
    {:else}
    	{#each $replyQueue as reply, i (i)}
    		<div class="border rounded p-3 mb-2 hover:bg-gray-50">
    			<span class="text-xs text-gray-500">[{['A','S','D'][i]}]</span>
    			<p>{reply}</p>
    			<button onclick={() => approveReply(i)} class="bg-green-600 text-white px-3 py-1 rounded mr-2">Approve</button>
    		</div>
    	{/each}
    	<button onclick={rejectReply} class="bg-gray-400 text-white px-3 py-1 rounded">[Q] Reject</button>
    	<button onclick={regenReply} class="bg-blue-500 text-white px-3 py-1 rounded">[W] Regen</button>
    {/if}
    ```
    
    **`DecisionStream.svelte`** skeleton:
    
    ```jsx
    <script lang="ts">
    	import { decisions } from '$lib/stores/decisions';
    
    	const intentColor = (intent: string) => {
    		return {
    			question: 'bg-blue-100 text-blue-800',
    			buying_intent: 'bg-green-100 text-green-800',
    			price_question: 'bg-yellow-100 text-yellow-800',
    			forbidden_link: 'bg-red-100 text-red-800',
    			spam: 'bg-gray-100 text-gray-600',
    		}[intent] || 'bg-gray-100 text-gray-600';
    	};
    </script>
    
    <div class="h-[400px] overflow-y-auto space-y-1">
    	{#each $decisions as d (d.comment_id)}
    		<div class="border-b py-2">
    			<span class="text-xs text-gray-400">{new Date(d.timestamp * 1000).toLocaleTimeString()}</span>
    			<span class="font-semibold ml-2">@{d.user}</span>
    			<span class="text-xs px-2 py-0.5 rounded {intentColor(d.intent)} ml-2">{d.intent}</span>
    			<p class="text-sm ml-2">{d.text}</p>
    		</div>
    	{/each}
    </div>
    ```
    
    **`AudioLibraryGrid.svelte`** skeleton:
    
    ```jsx
    <script lang="ts">
    	import { audioLibrary, playClip } from '$lib/stores/audio_library';
    
    	let category = $state<string>('');
    	const categories = $derived([...new Set($audioLibrary.map(c => c.category))].sort());
    	const filtered = $derived(category ? $audioLibrary.filter(c => c.category === category) : $audioLibrary);
    </script>
    
    <div class="mb-3">
    	{#each categories as cat}
    		<button class="px-3 py-1 rounded border mr-1 {category === cat ? 'bg-blue-500 text-white' : ''}"
    				onclick={() => category = category === cat ? '' : cat}>{cat}</button>
    	{/each}
    </div>
    
    <div class="grid grid-cols-3 gap-2 max-h-[300px] overflow-y-auto">
    	{#each filtered as clip (clip.id)}
    		<button class="border rounded p-2 text-left hover:bg-blue-50"
    				onclick={() => playClip(clip.id)}>
    			<div class="text-xs text-gray-500">{clip.id} · {Math.round(clip.duration_ms/1000)}s</div>
    			<div class="text-sm line-clamp-2">{clip.script}</div>
    		</button>
    	{/each}
    </div>
    ```
    
- <strong>G7 · Quick-fix untuk build crash (URGENT)</strong>
    
    **Kalau belum sempat bikin semua komponen**, minimal commit 5 file kosong dulu biar build tidak crash:
    
    ```jsx
    // apps/controller/src/lib/components/AudioLibraryGrid.svelte
    <div>AudioLibraryGrid placeholder</div>
    ```
    
    Ulangi untuk 4 komponen lain. Ini buy time untuk user tetap bisa `pnpm dev` sambil komponen beneran dikerjakan.
    
- <strong>G8 · WS client di-connect ke event v0.4 (HIGH)</strong>
    
    **File**: `apps/controller/src/lib/stores/ws.svelte.ts` (sudah ada, perlu extend)
    
    Tambah handler untuk:
    
    - `live.state` → set liveState
    - `live.tick` → update timer
    - `comment.classified` → append decisions
    - `audio.now` / `audio.done` → update current clip
    - `reply.suggested` → set replyQueue
    - `guardrail.blocked` → toast
    
    Saat ini store cuma handle event generic (metrics, comments, events) — event v0.4-specific belum di-wire.
    
- <strong>G9 · Routing `/library` baru (MEDIUM)</strong>
    
    Buat `apps/controller/src/routes/library/+page.svelte` sesuai desain di atas. Cuma butuh ~150 baris.
    
- <strong>G10 · Layout: nav item + version label (LOW)</strong>
    
    Update `+layout.svelte`:
    
    - Rename `Live Monitor → Live Cockpit`
    - Tambah `Audio Library` nav item
    - `v0.1.0-dev → v0.4.0-dev`

---

## 📅 3-Day Go-Live Sprint

### Hari 1 · Unblock Build + Audio Library (8 jam)

**Pagi** (4 jam) — Fix build crash + bikin stores:

1. Commit 3 stores lengkap: `live_state.ts`, `audio_library.ts`, `decisions.ts`
2. Commit `TwoHourTimer.svelte`, `EmergencyStop.svelte` (2 komponen paling simpel)
3. Commit 3 komponen placeholder kosong (`AudioLibraryGrid`, `DecisionStream`, `ReplySuggestions`)
4. `pnpm dev` — verifikasi build tidak crash

**Siang-Sore** (4 jam) — Generate audio library:

1. Commit `scripts/gen_audio_library.py` + `.bat`
2. Set Cartesia API keys di `.env` lokal
3. Run `scripts\gen_audio_library.bat`
4. Verifikasi 108 file `.wav` di `apps/worker/static/audio_library/`
5. `curl http://localhost:8766/health` → expect `audio_library_clip_count: 108`
6. Tambah `.gitignore`: `apps/worker/static/audio_library/*.wav` (jangan push WAV ke git)

### Hari 2 · Redesign /live Cockpit + /library (8 jam)

**Pagi** (4 jam) — Live Cockpit:

1. Redesign `routes/live/+page.svelte` dari monitor passive jadi 3-panel layout
2. Isi 3 komponen placeholder: `AudioLibraryGrid`, `DecisionStream`, `ReplySuggestions` dengan skeleton di atas
3. Wire WS events v0.4 di `ws.svelte.ts`
4. Implement keyboard shortcuts (A/S/D/Q/W/Space/1-9/Esc)

**Sore** (4 jam) — Library page + routing:

1. Buat `routes/library/+page.svelte`
2. Update `+layout.svelte`: nav items, version label
3. Refactor root `/` (Dashboard): hapus 5 import komponen live, ganti dengan tombol "Mulai Live Session →" yang link ke /live

### Hari 3 · Content + Dress Rehearsal (6 jam)

**Pagi** (3 jam) — Extend library:

1. Tambah 7 kategori baru di `clips_script.yaml` (~70 clips tambahan)
2. Tambah 5 produk baru di `products.yaml` + extend runsheet untuk cover 2 jam tanpa loop
3. Re-run `gen_audio_library.bat` (hanya clips baru karena idempotent)

**Sore** (3 jam) — Dress rehearsal:

1. 30 menit mock-live dengan OBS virtual camera
2. Verifikasi: timer jalan, audio tidak silent >30s, decision stream isi, reply suggestion muncul, emergency stop fungsi
3. Fix issue minor yang muncul
4. Update [📝 05 · CHANGELOG (Keep a Changelog)](https://www.notion.so/05-CHANGELOG-Keep-a-Changelog-cba7dd8becd94e3b820671a0d959bac7?pvs=21) dengan v0.4.0 final notes
5. Tag release `v0.4.0`

---

## ✅ Go-Live Readiness Checklist

### Backend must-have

- [ ]  `scripts/gen_audio_library.py` + `.bat` committed
- [ ]  `static/audio_library/index.json` berisi minimal 108 entry
- [ ]  108 file `.wav` ada di filesystem lokal (bukan di git)
- [ ]  `/health` endpoint return `audio_ready: true, classifier_ready: true, director_ready: true`
- [ ]  `products.yaml` runsheet cover minimal 2 jam (sum duration_s >= 7200) tanpa loop
- [ ]  `clips_script.yaml` minimal 160 clip di 11 kategori
- [ ]  WS command `audio.queue` + `live.switch_product` implemented
- [ ]  DOCS_HUB folder structure section updated

### Frontend must-have

- [ ]  5 komponen Svelte committed dengan behavior lengkap (bukan placeholder)
- [ ]  3 store committed dan connected ke WS
- [ ]  `/live` redesigned jadi 3-panel cockpit
- [ ]  `/library` page baru
- [ ]  Root `/` tidak import komponen live (prevent crash)
- [ ]  Layout nav: Live Cockpit + Audio Library items
- [ ]  Keyboard shortcuts A/S/D/Q/W/Space/1-9/Esc berfungsi
- [ ]  EmergencyStop sticky di top bar semua scroll position
- [ ]  TwoHourTimer color change green → yellow → red
- [ ]  `pnpm dev` clean build tanpa warning/error

### Operations must-have

- [ ]  `.env` lokal punya 5 Cartesia API key
- [ ]  `.env` lokal punya DeepSeek / 9router key
- [ ]  OBS Virtual Camera driver installed + tested
- [ ]  Scene switcher di OBS: `scene_opening`, `scene_product`, `scene_cta`, `scene_closing`
- [ ]  `REPLY_ENABLED=false` saat dress rehearsal pertama (aman dulu)
- [ ]  `DRY_RUN=true` saat dress rehearsal pertama
- [ ]  Dress rehearsal 30 menit sukses (no silent >30s, no crash, emergency stop fungsi)

---

## 🎯 Prompt Siap-Paste ke Agent Lokal (Hari 1)

```jsx
Baca dokumen ini dan https://www.notion.so/3b7aa241f5284b99bd6819d091b7f067 sebagai referensi. Kerjakan urut strict:

HARI 1 — CRITICAL (urgent, build sedang crash karena root +page.svelte import komponen yang belum ada):

1. Buat 3 store di apps/controller/src/lib/stores/:
   - live_state.ts (skeleton di doc 17 §Hari 2)
   - audio_library.ts (fetch + subscribe audio.list, audio.now, audio.done)
   - decisions.ts (ring buffer comment.classified)

2. Buat 5 komponen di apps/controller/src/lib/components/:
   - TwoHourTimer.svelte (skeleton di doc 17)
   - EmergencyStop.svelte (skeleton di doc 17)
   - AudioLibraryGrid.svelte (skeleton di doc 18)
   - DecisionStream.svelte (skeleton di doc 18)
   - ReplySuggestions.svelte (skeleton di doc 18)

3. pnpm dev → verifikasi tidak crash.

4. Buat scripts/gen_audio_library.py dan .bat (skeleton di doc 17 §Hari 1).
   Run dengan Cartesia API key aktif.
   Verifikasi: 108 file .wav + index.json populated.

5. Tambah di .gitignore: apps/worker/static/audio_library/*.wav

6. Commit per step dengan prefix [v0.4][feat:XXX] atau [v0.4][fix:XXX].

STOP kalau ada yang tidak jelas, jangan asumsi. Guardrail: jangan ubah behavior worker v0.3 existing.
```

---

## 📎 Referensi

- Spec build lengkap: [🛠️ 16 · KIRO Handoff — v0.4 Build Spec (Full Skeleton)](https://www.notion.so/16-KIRO-Handoff-v0-4-Build-Spec-Full-Skeleton-9e5d4d30289240c3bc229e7a66c036b7?pvs=21)
- Implementation review + bug detail: [🔬 17 · v0.4 Implementation Review — Bugs, Gaps & Completion Plan](https://www.notion.so/17-v0-4-Implementation-Review-Bugs-Gaps-Completion-Plan-3b7aa241f5284b99bd6819d091b7f067?pvs=21)
- Live plan 2 jam: [🎙️ Live Interaction Plan — 2 Jam Cartesia, Produk, Scene, Retensi](https://www.notion.so/Live-Interaction-Plan-2-Jam-Cartesia-Produk-Scene-Retensi-1267e9d752fa48ad847d1b2e778644a7?pvs=21)
- Orchestrator plan: [🧠 Orchestrator Implementation Plan — Python Worker + Svelte Control Center](https://www.notion.so/Orchestrator-Implementation-Plan-Python-Worker-Svelte-Control-Center-ebeaa1b997794405bad652a133f2afbe?pvs=21)
- Offers DB: [](https://www.notion.so/e18e17f63dee4cbfa33815957cb698ba?pvs=21)
- Repo: `dedy45/livetik@master`