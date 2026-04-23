# Changelog

All notable changes to this project will be documented in this file.  
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.4.1] — 2026-04-24 BUGFIX

### Fixed (v0.4.1 — SSR / SvelteKit errors)

**Bug 1 — `$state is not defined` (SSR crash):**
- Root cause: `live_state.ts` dan `audio_library.ts` menggunakan Svelte 5 runes (`$state`, `$derived`) di file `.ts` biasa yang tidak di-compile oleh Svelte compiler
- Fix: rename ke `.svelte.ts` extension agar Svelte compiler memproses runes
- Files: `stores/live_state.ts` → `stores/live_state.svelte.ts`, `stores/audio_library.ts` → `stores/audio_library.svelte.ts`
- Updated imports di: `TwoHourTimer.svelte`, `EmergencyStop.svelte`, `AudioLibraryGrid.svelte`

**Bug 2 — `window is not defined` (SSR crash di `ReplySuggestions.svelte:94`):**
- Root cause: `onDestroy(() => window.removeEventListener(...))` dipanggil saat SSR cleanup di Node.js, di mana `window` tidak tersedia
- Fix: pindahkan cleanup ke return value dari `onMount` (Svelte idiom yang benar — cleanup hanya jalan di client)
- Pattern: `onMount(() => { window.addEventListener(...); return () => window.removeEventListener(...); })`
- Same fix applied to `TwoHourTimer.svelte` (`onDestroy` → return dari `onMount`)

**Bug 3 — `$effect` di module-level store (SSR crash):**
- Root cause: `live_state.svelte.ts` menggunakan `$effect` di module-level untuk sync dari `wsStore.liveStateRaw`. `$effect` hanya valid di dalam komponen Svelte, bukan di store module
- Fix: ganti `$effect` + `$state` dengan `$derived` yang langsung membaca `wsStore.liveStateRaw` — tidak perlu side effect
- `audio_library.svelte.ts` disederhanakan menjadi pure type export (store tidak dipakai, `AudioLibraryGrid` sudah self-contained)

## [0.4.0] — 2026-04-24 SHIPPED

### Added (v0.4)

**P0 — Audio Library (CC-LIVE-CLIP-001..005):**
- `config/clips_script.yaml` — 160 script audio entries (9 categories)
- `core/audio_library/manager.py` — `AudioLibraryManager`: load index.json, fuzzy search, hot-reload, anti-repeat
- `adapters/audio_library.py` — `AudioLibraryAdapter`: sounddevice playback, serial queue
- `scripts/gen_audio_library.py` + `.bat` — Cartesia round-robin generator
- WS: `audio.list`, `audio.play`, `audio.stop` | `AudioLibraryGrid.svelte`

**P1 — Comment Classifier (CC-LIVE-CLASSIFIER-001..003):**
- `config/reply_templates.yaml` — 7 intents × 3 tone variants
- `core/classifier/rules.py` — 11 intents, rule-first, <10ms
- `core/classifier/llm_fallback.py` — LLM fallback with 5-min cache
- WS event: `comment.classified` | `DecisionStream.svelte`

**P2 — Suggested Reply (CC-LIVE-ORCH-001..005):**
- `core/orchestrator/budget_guard.py` — `BudgetGuard`
- `core/orchestrator/reply_cache.py` — cosine similarity cache
- `core/orchestrator/suggester.py` — template-first + LLM + `_safe()` guardrail
- WS: `reply.suggest`, `reply.approve`, `reply.reject`, `reply.regen` | `ReplySuggestions.svelte`

**P3 — Live Director (CC-LIVE-DIRECTOR-001..005):**
- `config/products.yaml` — 3 products + 8 runsheet phases
- `core/orchestrator/director.py` — `LiveDirector` state machine, hard-stop, 30s tick
- WS: `live.start/pause/resume/stop/emergency_stop/get_state` | `TwoHourTimer.svelte`, `EmergencyStop.svelte`

**Health Check v0.4:**
- `/health` extended: `audio_library_ready`, `classifier_ready`, `director_ready`, `budget_remaining_idr`, `worker_version: "0.4.0"`, HTTP 503 on degraded

## [Unreleased] — v0.4.0 planned (archived)

### Added (planned v0.4 — now shipped above)

**Core v0.4 Features:**
- **Live Director** state machine 2-jam (IDLE → HOOK → DEMO → CTA → REPLY → STOP@120min) — `core/orchestrator/director.py`
- **Pre-generated Audio Library** 160–220 clip Cartesia dengan index.json + fuzzy match — `core/audio_library/manager.py`, `adapters/audio_library.py`, `static/audio_library/`
- **Comment Classifier** rule-first (7 kategori ID: price, stock, how_to_use, objection, greeting, spam, other) + LLM fallback via guardrail — `core/classifier/{rules,llm_fallback}.py`
- **Suggested Reply** (semi-auto, human-in-the-loop) — `core/orchestrator/suggester.py`
- **Reply Cache** dengan cosine similarity > 0.9 (5 menit TTL) — `core/orchestrator/reply_cache.py`
- **2-hour hard-stop timer** dengan emergency stop manual
- **Products rotation config** — `config/products.yaml` (PALOMA, Reaim, TNW Chopper, CCTV, Aluflex, Locksworth, Senter XHP160, DINGS)

**Svelte Dashboard v0.4:**
- `AudioLibraryGrid.svelte` — grid 160 clip, search by tag, klik = play, latency <200ms
- `DecisionStream.svelte` — live feed keputusan director, color-code by state
- `ReplySuggestions.svelte` — 3 tombol opsi reply, operator klik pilih
- `TwoHourTimer.svelte` — countdown besar, warning di 10 menit terakhir
- `EmergencyStop.svelte` — tombol merah besar, konfirmasi modal

**Documentation v0.4:**
- `docs/LIVE_PLAN.md` — spec 2-jam Cartesia live, script host-led, 160–220 clip
- `docs/ORCHESTRATOR.md` — spec Python worker + Svelte control center, guardrail token-saving, LLM key pool

**Ticket prefixes v0.4:**
- `CC-LIVE-CLIP-xxx` (audio library)
- `CC-LIVE-CLASSIFIER-xxx` (comment classifier)
- `CC-LIVE-ORCH-xxx` (suggested reply + orchestrator)
- `CC-LIVE-DIRECTOR-xxx` (2-hour director state machine)

### Added (v0.3.0 shipped)

**Documentation:**
- Pulled Notion document "🎙️ Live Interaction Plan — 2 Jam Cartesia, Produk, Scene, Retensi" to `docs/live-interaction-plan-2-jam-cartesia.md`
  - Comprehensive 2-hour live streaming strategy for TikTok affiliate
  - 22 sections covering: theme, products, audio strategy, visual strategy, retention tactics, checklists
  - Includes Cartesia TTS prompt template for 200 audio variations
  - Production checklist and success metrics for first live test
- Added `docs/AUDIO_ROUTING_TROUBLESHOOTING.md` — comprehensive troubleshooting guide for VoiceMeeter + VB-CABLE setup
  - Step-by-step VoiceMeeter Banana configuration with screenshots descriptions
  - Common issues and solutions (no audio, low volume, OBS not capturing, latency, crackling)
  - Alternative setups and bypass options for testing
  - Debug steps and verification checklist

**Frontend — Audio Routing Setup:**
- Enhanced `/config` page Audio Routing Setup section with:
  - Prominent troubleshooting alert for "Audio Tidak Keluar" issue
  - Link to comprehensive troubleshooting guide
  - Expanded step-by-step instructions (7 detailed steps vs 4 brief steps)
  - Clearer VoiceMeeter configuration instructions with exact UI element names

**Frontend — TTS Output Test:**
- 2 section terpisah untuk test TTS dengan download & play:
  - **Edge-TTS (Lokal Fallback)** — Voice selector (ArdiNeural/GadisNeural)
  - **Cartesia TTS (Premium)** — Emotion selector (neutral/happy/sad/angry/dramatic/comedic)
- HTML5 audio player untuk preview hasil generate
- Download button untuk save audio file
- Metadata display (duration, file size)
- Real-time generation dengan loading state

**Backend — TTS Generate Commands:**
- `generate_edge_tts`: Generate Edge-TTS audio → save to static folder
  - Input: text, voice (default: id-ID-ArdiNeural)
  - Output: file_path, duration_s, file_size_kb, voice
- `generate_cartesia_tts`: Generate Cartesia TTS audio → save to static folder
  - Input: text, emotion (default: neutral)
  - Output: file_path, duration_s, file_size_kb, emotion, key_preview
- Static folder: `apps/controller/static/tts-samples/`
- File naming: `edge-{timestamp}.mp3` dan `cartesia-{timestamp}.wav`

### Fixed

**Frontend — Persona Page:**
- Auto-load persona content saat page mount (tidak perlu klik "Load dari file" manual)
- Persona sekarang persist setelah refresh — content yang disimpan muncul kembali
- Editor menampilkan full content (bukan hanya preview 200 karakter)
- Fix: `reload_persona` dan `save_persona` sekarang return full content

**Backend — Persona Commands:**
- `cmd_reload_persona`: Return full content via field `content` (selain `preview` 200 char)
- `cmd_save_persona`: Return full content dalam response untuk sync dengan editor

### Changed

**Frontend — UI Improvement:**
- `/config` page: Reorganized dengan tab navigation untuk mengurangi scroll panjang
  - **Tab 1: ⚙️ System & Runtime** — Runtime toggles, System checks, Daily budget
  - **Tab 2: 🤖 LLM & AI** — 9router, LLM tiers, Guardrail test & rules
  - **Tab 3: 🔊 TTS & Audio** — Cartesia config, key pool, Edge-TTS test, Cartesia test, Audio devices
  - **Tab 4: 📱 TikTok** — Connection test, Hot-swap account
  - Lebih user-friendly dengan navigasi yang jelas dan konten terorganisir per kategori

---

## [0.3.0] — 2026-04-23 · P3 Final Sprint

**Goal:** 100% config editable via `/config` UI. Zero edit file manual. Zero restart untuk ganti config.

### Added

**Backend — 3 file baru:**

- `core/config_store.py` — persist layer lengkap:
  - `write_env()` — atomic `.env` writer via temp-rename, backup `.env.bak.<ts>` sebelum setiap write
  - `read_env()` — baca `.env` dengan masking secret keys (CARTESIA_API_KEYS, NINEROUTER_API_KEY, dll)
  - `load_state()` / `save_state()` — persist runtime toggles ke `.state.json`
- `core/tiktok_supervisor.py` — `TikTokSupervisor` class:
  - Hot-swap TikTok account tanpa restart worker
  - `connect(username)` — graceful disconnect lama + connect baru
  - `disconnect()` — cancel task dengan 5s timeout (tidak hang worker)
  - `is_running()` — status check untuk heartbeat broadcast
- `ipc/audio.py` — `list_devices()` via `sounddevice`:
  - List semua output audio devices dengan index, name, channels, is_default
  - Graceful fallback kalau `sounddevice` tidak terinstall

**Backend — 11 command WS baru (total 30 command):**

| Command | Category | Fungsi |
|---------|----------|--------|
| `read_env` | config | Baca `.env` dengan masking secrets |
| `save_env` | config | Update key-value ke `.env` (atomic + backup) |
| `set_cartesia_config` | tts | Set voice_id / model / default_emotion + persist ke `.env` |
| `add_cartesia_key` | tts | Tambah key ke pool (validasi `sk_car_` prefix) + persist |
| `remove_cartesia_key` | tts | Hapus key dari pool by preview + persist |
| `update_guardrail` | guardrail | Update forbidden patterns + rate limit + persist ke `.env` |
| `set_budget_idr` | cost | Set daily budget (range 0–10M IDR) + persist ke `.env` |
| `connect_tiktok` | tiktok | Hot-swap TikTok account + persist username ke `.env` |
| `disconnect_tiktok` | tiktok | Graceful disconnect TikTok |
| `list_audio_devices` | system | List output audio devices |
| `read_cost_history` | cost | Baca `costs.jsonl` (7-day default) |

**Backend — perubahan existing:**

- `main.py` — `_wrap_cmd(name, category, handler)` wrapper:
  - Semua 30 command wrapped — exception → broadcast `error_event` dengan category → re-raise untuk `cmd_result`
  - Double safety net: error muncul di `/errors` page DAN di `cmd_result.ok=false`
- `main.py` — state restore on startup:
  - `REPLY_ENABLED` dan `DRY_RUN` di-restore dari `.state.json` saat worker start
  - `cmd_set_reply_enabled` dan `cmd_set_dry_run` sekarang persist ke `.state.json`
- `main.py` — hourly cost logging ke `costs.jsonl` (append JSONL per jam)
- `main.py` — heartbeat broadcast tambah field: `tiktok_username`, `tiktok_running`, `guardrail`
- `core/guardrail.py` — fully reconfigurable:
  - `update_config()` — atomic update (compile semua regex dulu sebelum replace, kalau 1 invalid → original config utuh)
  - `config_snapshot()` — return current config untuk heartbeat
  - Semua parameter baca dari env vars: `GUARDRAIL_MIN_WORDS`, `GUARDRAIL_RATE_MAX`, `GUARDRAIL_RATE_WINDOW_S`, `GUARDRAIL_MAX_CHARS`
- `core/cost.py` — mutable tariff:
  - `set_budget(idr)` — update budget runtime (range validation 0–10M)
  - `update_tariff()` — update LLM/TTS cost tables runtime
  - `record_llm()` / `record_tts()` pakai `self.llm_cost_per_1k` / `self.usd_to_idr` (bukan constants)
- `adapters/cartesia_pool.py` — CRUD methods:
  - `add_key(key)` — validasi `sk_car_` prefix + duplicate check
  - `remove_key_by_preview(preview_or_full)` — remove by preview string atau full key
- `adapters/tts.py` — `default_emotion` mutable:
  - `self.default_emotion` baca dari `CARTESIA_DEFAULT_EMOTION` env var (default: `neutral`)
  - `speak(text, emotion=None)` — kalau `emotion=None` pakai `self.default_emotion`
- `pyproject.toml` — tambah `sounddevice>=0.4.6`

**Frontend — 6 section baru di `/config`:**

- **Cartesia Voice Config** — input voice_id (UUID), select model (sonic-3/2/english), select default emotion, tombol Save & Apply + feedback
- **Cartesia Key Pool Management** — list keys dengan tombol Remove per key, input + tombol Add Key (validasi `sk_car_` prefix di frontend)
- **Guardrail Rules** — textarea forbidden patterns (1 regex per baris), input min_words/rate_max/window/max_chars, tombol Save & Apply + feedback
- **Daily Budget (IDR)** — number input + Save button, tampilkan current usage
- **TikTok Account (hot-swap)** — input username, tombol Connect + Disconnect, status indicator
- **Audio Output Device** — select dropdown devices (auto-load on connect), tombol Refresh

**Frontend — `/cost` page:**

- CSV export button — download `costs_<ts>.csv` dari `read_cost_history` result
- 7-day SVG line chart — pure SVG polyline, no external chart library
- Auto-load history on connect

**Frontend — `/+page.svelte` (Dashboard):**

- Hint "Edit models in .env" → link ke `/config` page

**Kiro Steering Files — 4 file baru di `.kiro/steering/`:**

- `product.md` — goal, persona Bang Hack, core loop, budget constraint
- `tech.md` — stack lock (Python 3.11+, Svelte 5 runes, Tailwind v4, port 8765/8766, audio format)
- `structure.md` — monorepo layout lengkap + command count
- `constraints.md` — Anti-FAKE rules, zero hardcode, error handling, budget cap, audio quality

---

## [0.2.3] — 2026-04-22 · P2-D Patch Sprint

**Goal:** Fix 3 hardcode kritis + 1 bug + 2 UX gap sebelum go-live.

### Fixed

- `adapters/tts.py` — encoding mismatch: `pcm_s16le` → `pcm_f32le`, `22050` → `44100` (match script kerja yang sudah terbukti)
- `adapters/llm.py` — model 9router hardcode: `"openai/kc/kilo-auto/free"` → `os.getenv("NINEROUTER_MODEL", "openai/kc/kilo-auto/free")`
- `routes/config/+page.svelte` — `slot.total_errors` → `slot.errors` (match field dari `cartesia_pool.stats()`)
- `ipc/ws_server.py` — suppress noisy `InvalidMessage` log dari TCP health-check probe (raw socket connect ke WS port)

### Added

- `adapters/tts.py` — emotion support untuk Cartesia Sonic-3:
  - `VALID_EMOTIONS = frozenset({"neutral", "happy", "sad", "angry", "dramatic", "comedic"})`
  - `speak(text, emotion="neutral")` — signature baru dengan default safe
  - `_cartesia_speak()` kirim `"experimental_controls": {"emotions": [safe_emotion]}` ke API
  - Auto-fallback ke `"neutral"` kalau emotion tidak dikenal
- `routes/config/+page.svelte` — emotion dropdown di Voice Output test (6 pilihan)
- `routes/persona/+page.svelte` — upgrade dari viewer-only ke full editor:
  - Textarea editable langsung di browser
  - Tombol Save & Apply → command `save_persona` baru
  - Hot-reload tanpa restart worker
  - Indicator `● unsaved` / `● synced`
- `main.py` — command `save_persona`: write ke `config/persona.md` + hot-reload ke memory

---

## [0.2.0] — 2026-04-22 · P2-C Sprint

**Goal:** Bidirectional WebSocket + full UX validation controller.

### Added

**Backend:**

- `ipc/ws_server.py` — bidirectional WS: broadcast metrics + handle inbound commands
  - `register_command(name, handler)` — register async command handler
  - `_handle_cmd()` — dispatch command, return `cmd_result` dengan `req_id`, `ok`, `latency_ms`
  - `hello` message saat connect: list semua registered commands
- `main.py` — 18 command WS (15 spec + 3 bonus):

| Command | Fungsi |
|---------|--------|
| `test_ffplay` | Probe ffplay binary |
| `test_ninerouter` | Ping 9router `/models` endpoint |
| `test_llm` | LLM roundtrip test |
| `test_cartesia_key` | Test 1 Cartesia key (synth "halo") |
| `test_cartesia_all` | Test semua keys di pool |
| `test_edge_tts` | Synth tanpa play (Azure reachability) |
| `test_tts_voice_out` | End-to-end TTS + play audio |
| `test_tiktok_conn` | Check akun live/offline |
| `reload_persona` | Reload `config/persona.md` ke memory |
| `test_reply` | Full pipeline test (guardrail + LLM, tanpa TTS) |
| `test_guardrail` | Test guardrail check |
| `reset_cost_today` | Reset cost counter (dev only, confirm flag) |
| `reload_env` | Reload `.env` (note: adapter tidak re-init) |
| `set_reply_enabled` | Toggle REPLY_ENABLED runtime |
| `set_dry_run` | Toggle DRY_RUN runtime |
| `update_llm_tier` | Update model string tier runtime |
| `test_llm_custom` | Test model arbitrary tanpa ubah router |
| `list_ninerouter_models` | Fetch model list dari 9router |

- `main.py` — `error_event` broadcast di `handle_reply` untuk LLM failure dan TTS error
- `adapters/tts.py` — default model `sonic-3` via `CARTESIA_MODEL` env var

**Frontend — 4 route stub → full implementation:**

- `/config` — 9 section: Runtime Toggles, System, 9router, LLM Tiers, Cartesia Pool, Edge-TTS, Voice Output, TikTok Connection, Guardrail Test
- `/errors` — error stream dengan category filter (llm, tts, tiktok, guardrail, system)
- `/persona` — persona viewer + test reply pipeline
- `/cost` — cost tracker dengan breakdown per tier + progress bar

**Frontend — `/+page.svelte` (Dashboard):**

- System Health card dengan 5 probe buttons (ffplay, 9router, LLM, Cartesia, Edge-TTS)

**Frontend — `lib/stores/ws.svelte.ts`:**

- `sendCommand(name, params)` — kirim command, return `req_id`
- `testResults` Map — store `cmd_result` per `req_id`
- `TestButton` component — wrapper untuk command dengan loading state + result display

---

## [0.1.5] — 2026-04-22 · P2-B Sprint

**Goal:** LLM + TTS reply loop end-to-end.

### Added

- `adapters/llm.py` — `LLMAdapter` dengan LiteLLM Router 3-tier:
  - Tier 1: 9router (`NINEROUTER_BASE_URL`, `NINEROUTER_MODEL`)
  - Tier 2: DeepSeek (`DEEPSEEK_API_KEY`)
  - Tier 3: Claude Haiku (`ANTHROPIC_API_KEY`)
  - `update_tier_model(tier_id, model)` — update model string runtime
  - `test_with_model(model, api_base, api_key)` — one-shot test tanpa ubah router
  - `get_model_list()` — return configured tiers untuk UI
  - Auto-prefix `openai/` untuk model tanpa provider prefix
- `adapters/tts.py` — `TTSAdapter` dengan Cartesia primary + edge-tts fallback:
  - `CartesiaPool` 5-key rotation dengan 24h cooldown per key
  - `speak(text)` — synth → temp WAV → ffplay subprocess → VB-CABLE
  - Fallback ke edge-tts kalau semua Cartesia keys exhausted
  - `_play_lock` — sequential playback (tidak overlap)
- `adapters/cartesia_pool.py` — `CartesiaPool`:
  - `from_env()` — parse `CARTESIA_API_KEYS` (comma-separated)
  - `acquire()` — sticky-until-error rotation
  - `mark_exhausted(slot)` — 24h cooldown + rotate
  - `stats()` — return pool status untuk UI
- `core/queue.py` — `ReplyQueue` dengan async worker
- `main.py` — full reply loop: TikTok comment → guardrail → LLM → TTS → broadcast
- `pyproject.toml` — tambah `httpx>=0.27.0`, `litellm>=1.50.0`, `cartesia>=2.0.0`

---

## [0.1.0] — 2026-04-22 · P2-A Sprint

**Goal:** TikTok read-only live feed (Rp 0, no LLM/TTS).

### Added

- `adapters/tiktok.py` — `TikTokAdapter` dengan `TikTokLive` library:
  - Event types: `connected`, `disconnected`, `offline`, `comment`, `gift`, `join`
  - `run_with_retry()` — auto-reconnect dengan exponential backoff
  - `TTEvent` dataclass untuk event normalization
- `main.py` — worker entry point:
  - Async main loop dengan heartbeat 5s
  - `State` class untuk tracking metrics (comments, replies, gifts, joins, viewers, latency p95)
  - Broadcast `tiktok_event` dan `metrics` via WebSocket
- `ipc/ws_server.py` — WebSocket server (broadcast only, port 8765)
- `ipc/http_server.py` — FastAPI HTTP server (port 8766)
- `core/persona.py` — `load_persona()` dari `config/persona.md` dengan DEFAULT_PERSONA fallback
- `core/guardrail.py` — `Guardrail` dengan forbidden patterns, min_words, rate limit, dedup
- `core/cost.py` — `CostTracker` dengan daily budget cap
- `apps/controller/` — SvelteKit controller baseline:
  - `lib/stores/ws.svelte.ts` — reactive WS store dengan Svelte 5 runes
  - `/+page.svelte` — dashboard dengan KPI cards + reply feed + comment feed
  - `/live/+page.svelte` — live comment monitor
  - `/errors/+page.svelte` — error stream (stub)
  - `/persona/+page.svelte` — persona viewer (stub)
  - `/config/+page.svelte` — config page (stub)
  - `/cost/+page.svelte` — cost tracker (stub)
- `scripts/dev.bat` — start worker + controller sekaligus
- `scripts/health_check.py` — 7-check health script (ffplay, port, 9router, LLM, Cartesia, edge-tts, WS commands)
- `pyproject.toml` — baseline dependencies (TikTokLive, edge-tts, websockets, FastAPI, uvicorn, python-dotenv)

---

## [0.0.1] — 2026-04-22 · Repo Init

### Added

- Monorepo skeleton: `apps/worker/`, `apps/controller/`, `docs/`, `scripts/`
- `docs/` — 12 dokumen: PRD, ARCHITECTURE, DESIGN, README, CHANGELOG, ERROR_HANDLING, PLAN, AGENT_BRIEF, GITHUB, STRUCTURE, TROUBLESHOOTING, KIRO_GUIDE
- `DOCS_HUB.md` — single source of truth index
- `.env.example` — template environment variables
- `.github/workflows/ci.yml` — CI: uv sync + pytest + svelte-check
- `.vscode/` — workspace settings + extensions recommendations
- `pyproject.toml` — Python project baseline

---

## Format panduan contribution

### [X.Y.Z] — YYYY-MM-DD

#### Added
- Fitur baru

#### Changed
- Perubahan behavior existing

#### Deprecated
- Akan dihapus versi berikutnya

#### Removed
- Dihapus

#### Fixed
- Bug fix

#### Security
- Vulnerability patch

---

## Commit Message Convention

Conventional Commits, scope wajib kalau ubah >1 modul:

```
feat(worker): add Claude fallback adapter
fix(controller/live): reply row not highlighting on click
chore(ci): bump uv to 0.5.4
docs(arch): revise WS protocol section
refactor(core/queue): extract priority function
test(guardrail): add Indonesia-specific regex coverage
```

Type: `feat|fix|chore|docs|refactor|test|style|perf|ci|revert`

---

## Roadmap (belum dikerjakan)

### [0.4.0] — Target Month 2

#### Planned
- Gift & Follow event → template reply khusus
- Session log export JSON
- Upgrade queue dari FIFO → priority (gift > comment > like)
- TikFinity alerts integration via Browser Source
- Keyword trigger → auto OBS scene switch (obs-websocket v5)
- Lumia Stream integration (smart light trigger saat gift)
- Multi-language persona support (EN fallback)
- Analytics export ke Notion database (via Notion API)
- ffplay per-device routing (audio device selector P4)

---

[Unreleased]: https://github.com/dedy45/livetik/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/dedy45/livetik/compare/v0.2.3...v0.3.0
[0.2.3]: https://github.com/dedy45/livetik/compare/v0.2.0...v0.2.3
[0.2.0]: https://github.com/dedy45/livetik/compare/v0.1.5...v0.2.0
[0.1.5]: https://github.com/dedy45/livetik/compare/v0.1.0...v0.1.5
[0.1.0]: https://github.com/dedy45/livetik/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/dedy45/livetik/releases/tag/v0.0.1
