# 🗓️ 07 · Plan — Roadmap & Tiket Coding

> **Canonical**: roadmap fase + daftar tiket `CC-LIVE-xxx` siap diambil agent VSCode. Mirror dari Notion.

---

## 1. Fase & Target

| Fase | Nama | Target | Goals |
|------|------|--------|-------|
| M0 | Scaffold | Day 1 | Monorepo structure, CI, VSCode config |
| M1 | Core Worker | Week 1 | TikTok + LLM + TTS + OBS + Guardrail + Queue |
| M2 | Controller UI | Week 1 | Dashboard + Live + Errors + Persona + Config + Cost |
| M3 | Polish | Week 2 | Telemetry, fallback, hot-reload, dry-run |
| M4 | v0.2 Features | Week 2 | Gift/Follow reply, Claude fallback, session export |
| M5 | v0.3 Features | Week 3 | TikFinity, OBS scene switch |
| M6 | v0.4 Live Orchestrator | Week 4–5 | Audio Library + Classifier + Suggested Reply + 2-hour Director |

---

## 2. Tiket CC-LIVE-xxx (Siap Diambil Agent)

Format tiap tiket: **ID • Title • Fase • Estimasi • Definition of Done • File yang disentuh • Reference**

---

### CC-LIVE-REPO-001 | Scaffold monorepo

- **Fase**: M0 • **Est**: 1h
- **DoD**: Semua folder dari ARCHITECTURE.md ada, `uv sync` jalan, `pnpm install` jalan, CI hijau
- **Files**: struktur awal saja
- **Ref**: folder tree di docs hub

---

### CC-LIVE-REPO-002 | Tailwind v4 theme + layout shell

- **Fase**: M0 • **Est**: 1h
- **DoD**: `app.css` dengan `@theme` (lihat Design doc §6), `+layout.svelte` sidebar + top bar, route stub `/`
- **Files**: `apps/controller/src/app.css`, `src/routes/+layout.svelte`, `src/lib/components/Sidebar.svelte`
- **Ref**: Design doc §3 IA, §6 Theme

---

### CC-LIVE-REPO-003 | CI GitHub Actions

- **Fase**: M0 • **Est**: 30m
- **DoD**: `.github/workflows/ci.yml` — job `worker` (uv sync, ruff, mypy, pytest) + job `controller` (pnpm i, svelte-check, build)
- **Files**: `.github/workflows/ci.yml`

---

### CC-LIVE-REPO-004 | VSCode workspace config

- **Fase**: M0 • **Est**: 30m
- **DoD**: `.vscode/settings.json` (python.defaultInterpreter = `.venv`), `launch.json` (debug worker + attach controller), `tasks.json` (dev task)
- **Files**: `.vscode/*.json`

---

### CC-LIVE-CORE-001 | Persona loader

- **Fase**: M1 • **Est**: 1h
- **DoD**: `core/persona.py` load markdown, return string; unit test
- **Files**: `core/persona.py`, `config/persona.md` (paste dari master blueprint §6), `tests/test_persona.py`

---

### CC-LIVE-CORE-002 | Guardrail engine

- **Fase**: M1 • **Est**: 2h
- **DoD**: `core/guardrail.py` dengan `check_input` + `check_output`, return `(ok: bool, reason: str)`, unit test minimal 20 case (link, brand, 08xx, politik, SARA, normal)
- **Files**: `core/guardrail.py`, `tests/test_guardrail.py`
- **Ref**: FORBIDDEN_PATTERNS di memory

---

### CC-LIVE-CORE-003 | Queue + rate limit

- **Fase**: M1 • **Est**: 2h
- **DoD**: `core/queue.py` dengan `asyncio.Queue`, dedup by comment_id (TTL 60s), `asyncio_throttle` max 8/min + min 4s gap; test dengan burst 50 events
- **Files**: `core/queue.py`, `tests/test_queue.py`

---

### CC-LIVE-ADAPTER-001 | TikTok adapter

- **Fase**: M1 • **Est**: 2h
- **DoD**: `adapters/tiktok.py` wrap `TikTokLiveClient`, translate `CommentEvent`/`GiftEvent`/`FollowEvent`/`ConnectEvent` → domain events di `core/events.py`, emit via callback
- **Files**: `adapters/tiktok.py`, `core/events.py`
- **Ref**: isaackogan quickstart

---

### CC-LIVE-ADAPTER-002 | LLM adapter DeepSeek

- **Fase**: M1 • **Est**: 2h
- **DoD**: `adapters/llm.py` class `LLMProvider` + `DeepSeekProvider` using `openai` SDK base_url override; retry 3× exponential backoff; token count return
- **Files**: `adapters/llm.py`, `tests/test_llm_smoke.py`

---

### CC-LIVE-ADAPTER-003 | TTS adapter Edge

- **Fase**: M1 • **Est**: 1.5h
- **DoD**: `adapters/tts.py` synthesize MP3 via `edge-tts`, play via ffplay subprocess serial, queue-driven
- **Files**: `adapters/tts.py`

---

### CC-LIVE-ADAPTER-004 | OBS file bridge

- **Fase**: M1 • **Est**: 30m
- **DoD**: `adapters/obs.py` atomic write (tmp + rename), test concurrent write 100×
- **Files**: `adapters/obs.py`

---

### CC-LIVE-MAIN-001 | Orchestrator wiring

- **Fase**: M1 • **Est**: 2h
- **DoD**: `main.py` asyncio.TaskGroup dengan 4 tasks (tiktok, ws, http, tts); graceful shutdown Ctrl+C; healthcheck log tiap 30s
- **Files**: `main.py`

---

### CC-LIVE-IPC-001 | WebSocket server

- **Fase**: M2 • **Est**: 1.5h
- **DoD**: `ipc/ws_server.py` broadcast ke semua client; heartbeat 30s; reconnect-safe
- **Files**: `ipc/ws_server.py`

---

### CC-LIVE-IPC-002 | FastAPI REST

- **Fase**: M2 • **Est**: 2h
- **DoD**: `ipc/http_api.py` endpoints per Arch doc §5b; Pydantic models; CORS localhost
- **Files**: `ipc/http_api.py`

---

### CC-LIVE-UI-001 | WS store + reconnect

- **Fase**: M2 • **Est**: 1.5h
- **DoD**: `lib/stores/ws.svelte.ts` runes-based, auto-reconnect 3s, cap 500 events
- **Files**: `apps/controller/src/lib/stores/ws.svelte.ts`, `state.svelte.ts`

---

### CC-LIVE-UI-002 | Dashboard 6 KPI cards

- **Fase**: M2 • **Est**: 2h
- **DoD**: route `/` dengan 6 KPICard + 1 chart + 5 event mini-feed (Design §3.1)
- **Files**: `src/routes/+page.svelte`, `src/lib/components/KPICard.svelte`, `StatusPill.svelte`, `SparkLine.svelte`

---

### CC-LIVE-UI-003 | Live monitor split view

- **Fase**: M2 • **Est**: 2h
- **DoD**: `/live` split 50/50 comment+reply feed, sticky filter, klik pair highlight
- **Files**: `src/routes/live/+page.svelte`, `EventRow.svelte`

---

### CC-LIVE-UI-004 | Errors page

- **Fase**: M2 • **Est**: 1.5h
- **DoD**: `/errors` tab per domain, table sortable, copy reproduce
- **Files**: `src/routes/errors/+page.svelte`

---

### CC-LIVE-UI-005 | Persona editor

- **Fase**: M2 • **Est**: 2h
- **DoD**: `/persona` Monaco editor + preview, save REST, test prompt box
- **Files**: `src/routes/persona/+page.svelte`

---

### CC-LIVE-UI-006 | Config page

- **Fase**: M2 • **Est**: 1.5h
- **DoD**: `/config` auto-form dari schema Pydantic (endpoint `/api/config/schema`)
- **Files**: `src/routes/config/+page.svelte`

---

### CC-LIVE-UI-007 | Cost tracker

- **Fase**: M2 • **Est**: 1h
- **DoD**: `/cost` today/week/month + chart + export CSV
- **Files**: `src/routes/cost/+page.svelte`

---

### CC-LIVE-TEL-001 | Structured logger

- **Fase**: M3 • **Est**: 1h
- **DoD**: `telemetry/logger.py` JSON log ke file + stdout; include trace_id
- **Files**: `telemetry/logger.py`

---

### CC-LIVE-TEL-002 | Cost tracker backend

- **Fase**: M3 • **Est**: 1h
- **DoD**: `telemetry/cost.py` accumulate token counts, expose via REST `/api/cost`
- **Files**: `telemetry/cost.py`

---

## 3. Dependency Graph

```
M0: REPO-001 → REPO-002 → REPO-003 → REPO-004
M1: CORE-001 → CORE-002 → CORE-003
    ADAPTER-001 → ADAPTER-002 → ADAPTER-003 → ADAPTER-004
    MAIN-001 (depends on all M1)
M2: IPC-001 → IPC-002
    UI-001 → UI-002 → UI-003 → UI-004 → UI-005 → UI-006 → UI-007
M3: TEL-001 → TEL-002
```

Agent harus ambil tiket urut dependency graph. Jangan skip ke M2 sebelum M1 selesai.

---

## 2b. Tiket v0.4 (M6 — Live Orchestrator, NEW)

> 🔴 Semua tiket v0.4 mengacu ke `docs/LIVE_PLAN.md` + `docs/ORCHESTRATOR.md`. Phase strict order: P0 → P1 → P2 → P3. Jangan loncat fase sebelum acceptance criteria terpenuhi.

### P0 · Audio Library Player

### CC-LIVE-CLIP-001 | Audio library index schema + loader

- **Fase**: M6-P0 • **Est**: 2h
- **DoD**: `core/audio_library/manager.py` load `static/audio_library/index.json` (schema: id, tag[], duration_ms, voice_id, script, scene_hint), fuzzy match by tag, test dengan 160 entry dummy
- **Files**: `core/audio_library/manager.py`, `static/audio_library/index.json`, `tests/test_audio_library.py`

### CC-LIVE-CLIP-002 | Generate 160–220 clip Cartesia

- **Fase**: M6-P0 • **Est**: 4h (batch job)
- **DoD**: script `scripts/gen_audio_library.py` pakai Cartesia pool + script dari `config/clips_script.yaml`, output `.wav` + update `index.json`, progress log, skip kalau sudah ada
- **Files**: `scripts/gen_audio_library.py`, `scripts/gen_audio_library.bat`, `apps/worker/config/clips_script.yaml`

### CC-LIVE-CLIP-003 | Audio playback adapter

- **Fase**: M6-P0 • **Est**: 2h
- **DoD**: `adapters/audio_library.py` playback via `sounddevice` ke virtual cable, queue-driven (tidak overlap), emit event `audio.playing` / `audio.done`
- **Files**: `adapters/audio_library.py`

### CC-LIVE-CLIP-004 | WS command audio.list / play / stop

- **Fase**: M6-P0 • **Est**: 1h
- **DoD**: 3 command baru di `ipc/ws_server.py`, return JSON schema terdokumentasi
- **Files**: `ipc/ws_server.py`

### CC-LIVE-CLIP-005 | Svelte AudioLibraryGrid panel

- **Fase**: M6-P0 • **Est**: 2.5h
- **DoD**: `lib/components/AudioLibraryGrid.svelte` grid 160 clip, search by tag, klik = play, latency target <200ms
- **Files**: `apps/controller/src/lib/components/AudioLibraryGrid.svelte`
- **Acceptance P0**: klik clip di dashboard → audio keluar <200ms, 0 LLM call, 160 clip ter-index

### P1 · Comment Classifier

### CC-LIVE-CLASSIFIER-001 | Rule-first classifier 7 kategori

- **Fase**: M6-P1 • **Est**: 3h
- **DoD**: `core/classifier/rules.py` regex + keyword dict Bahasa Indonesia untuk: price, stock, how_to_use, objection, greeting, spam, other. Return `(category, confidence)`. Test minimal 50 case.
- **Files**: `core/classifier/rules.py`, `core/classifier/keywords.yaml`, `tests/test_classifier_rules.py`

### CC-LIVE-CLASSIFIER-002 | LLM fallback dengan guardrail

- **Fase**: M6-P1 • **Est**: 2h
- **DoD**: `core/classifier/llm_fallback.py` lewat `guardrail/runtime.py`, hanya dipanggil kalau rule confidence < 0.8, hasil di-cache 5 menit
- **Files**: `core/classifier/llm_fallback.py`

### CC-LIVE-CLASSIFIER-003 | Badge di Live Comments feed

- **Fase**: M6-P1 • **Est**: 1h
- **DoD**: extend panel Live Comments existing, tampil badge kategori + confidence, filter dropdown
- **Files**: `apps/controller/src/routes/live/+page.svelte`

### CC-LIVE-CLASSIFIER-004 | WS event comment.classified

- **Fase**: M6-P1 • **Est**: 30m
- **DoD**: event baru `comment.classified` emit dari worker setelah setiap comment
- **Files**: `ipc/ws_server.py`
- **Acceptance P1**: 80%+ comment ter-klasifikasi rule-only, cost panel tunjukkan penghematan token

### P2 · Suggested Reply (semi-auto)

### CC-LIVE-ORCH-001 | Suggester engine 3-opsi

- **Fase**: M6-P2 • **Est**: 3h
- **DoD**: `core/orchestrator/suggester.py` generate 3 reply dari template + LLM (via guardrail + cache), latency target <2s
- **Files**: `core/orchestrator/suggester.py`, `config/reply_templates.yaml`

### CC-LIVE-ORCH-002 | Reply cache (cosine similarity)

- **Fase**: M6-P2 • **Est**: 2h
- **DoD**: `core/orchestrator/reply_cache.py` cache reply 5 menit, match comment mirip (cosine > 0.9) pakai hasil cached
- **Files**: `core/orchestrator/reply_cache.py`

### CC-LIVE-ORCH-003 | Svelte ReplySuggestions panel

- **Fase**: M6-P2 • **Est**: 2h
- **DoD**: `lib/components/ReplySuggestions.svelte` 3 tombol, operator klik pilih, WS `reply.suggest` / `reply.pick`
- **Files**: `apps/controller/src/lib/components/ReplySuggestions.svelte`

### CC-LIVE-ORCH-004 | Human-in-the-loop flag

- **Fase**: M6-P2 • **Est**: 1h
- **DoD**: `REPLY_ENABLED=false` tetap supported, REPLY_AUTO_AFTER_PICK=true opsi auto-send setelah pick
- **Files**: `.env.example`, `core/orchestrator/suggester.py`
- **Acceptance P2**: latency suggest <2s, human-in-the-loop, REPLY_ENABLED=false tidak break flow

### P3 · Live Director (2-jam state machine)

### CC-LIVE-DIRECTOR-001 | State machine skeleton

- **Fase**: M6-P3 • **Est**: 3h
- **DoD**: `core/orchestrator/director.py` state machine IDLE → HOOK → DEMO → CTA → REPLY → STOP@120min, transition handler, log tiap transition
- **Files**: `core/orchestrator/director.py`, `tests/test_director.py`

### CC-LIVE-DIRECTOR-002 | Products rotation config

- **Fase**: M6-P3 • **Est**: 1.5h
- **DoD**: `config/products.yaml` dengan daftar produk + slot waktu + CTA, loader + validator Pydantic
- **Files**: `apps/worker/config/products.yaml`, `core/config_store.py` extend

### CC-LIVE-DIRECTOR-003 | 2-hour timer + hard stop

- **Fase**: M6-P3 • **Est**: 1.5h
- **DoD**: timer countdown 120 menit, auto-stop director + TTS announcement, emit `director.stopped`
- **Files**: `core/orchestrator/director.py`

### CC-LIVE-DIRECTOR-004 | WS director.start / stop / state

- **Fase**: M6-P3 • **Est**: 1h
- **DoD**: 3 command + 1 broadcast event
- **Files**: `ipc/ws_server.py`

### CC-LIVE-DIRECTOR-005 | Svelte DecisionStream panel

- **Fase**: M6-P3 • **Est**: 2h
- **DoD**: `lib/components/DecisionStream.svelte` live feed keputusan, color-code by state
- **Files**: `apps/controller/src/lib/components/DecisionStream.svelte`

### CC-LIVE-DIRECTOR-006 | TwoHourTimer panel

- **Fase**: M6-P3 • **Est**: 1h
- **DoD**: `lib/components/TwoHourTimer.svelte` countdown besar, warning di 10 menit terakhir
- **Files**: `apps/controller/src/lib/components/TwoHourTimer.svelte`

### CC-LIVE-DIRECTOR-007 | EmergencyStop button

- **Fase**: M6-P3 • **Est**: 30m
- **DoD**: `lib/components/EmergencyStop.svelte` tombol merah besar, konfirmasi modal
- **Files**: `apps/controller/src/lib/components/EmergencyStop.svelte`

### CC-LIVE-DIRECTOR-008 | Health check extension

- **Fase**: M6-P3 • **Est**: 1h
- **DoD**: HTTP `/health` tambah probe `audio_library_ready`, `classifier_ready`, `director_ready`, `budget_remaining_idr`
- **Files**: `ipc/http_api.py`
- **Acceptance P3**: live 2 jam tanpa intervensi, hard-stop di 120 menit, semua keputusan ter-log
