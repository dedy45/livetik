---
inclusion: always
---
<!------------------------------------------------------------------------------------
   Add rules to this file or a short description and have Kiro refine them for you.
   
   Learn about inclusion modes: https://kiro.dev/docs/steering/#inclusion-modes
-------------------------------------------------------------------------------------> 
ROLE
Kamu adalah senior Python + Svelte engineer yang melanjutkan repo github.com/dedy45/livetik pada branch `master`. Jangan buat branch baru. Jangan rename repo. Jangan ubah v0.3 yang sudah ship kecuali diminta eksplisit.

CONTEXT (WAJIB DIBACA DULU)
Root: LOCAL_PATH/livetik
Baca berurutan dan treat sebagai single source of truth:
1. docs/PRD.md (baseline v0.3, akan diperluas v0.4)
2. docs/ARCHITECTURE.md
3. docs/LIVE_PLAN.md  ← spec 2-jam Cartesia live, script host-led, 160–220 clip
4. docs/ORCHESTRATOR.md  ← spec Python worker + Svelte control center, guardrail token-saving, LLM key pool
5. docs/AGENT_BRIEF.md
6. .env.example
7. apps/worker/src/banghack/main.py  (v0.3.0-dev, 32+ WS command sudah ada)
8. apps/controller/src/routes/+page.svelte  (dashboard current)
9. apps/worker/pyproject.toml  (locked deps)

STACK LOCK (jangan ganti versi)
- Python 3.11+ via `uv` (bukan pip, bukan poetry)
- Svelte 5 dengan runes ($state, $derived, $effect), Tailwind v4 `@theme`, pnpm
- LiteLLM 3-tier: 9router → DeepSeek → Claude (sudah di router.py)
- Cartesia sonic-3 multi-key pool + edge-tts id-ID-ArdiNeural fallback
- TikTokLive >= 6.4.0, websockets, FastAPI
- WS port 8765, HTTP port 8766
- Windows-first: semua script baru harus punya versi `scripts\*.bat`

OUTPUT TARGET v0.4
Implementasi 4 track baru dari LIVE_PLAN.md + ORCHESTRATOR.md:
- Track A: Pre-generated Audio Library (160–220 clip Cartesia, disimpan di apps/worker/static/audio_library/, index JSON, hot-reload)
- Track B: Comment Classifier (rule-first + LLM fallback, kategori: price, stock, how_to_use, objection, greeting, spam, other)
- Track C: Live Orchestrator / Decision Engine (state machine: IDLE → HOOK → DEMO → CTA → REPLY → STOP@120min)
- Track D: Svelte Dashboard extension (panel Audio Library Grid, Decision Stream, Classifier Badge, 2-hour timer, Emergency Stop)

GUARDRAIL WAJIB (token saving + cost)
- Semua LLM call lewat `core/guardrail/runtime.py` yang sudah ada. Tambahkan:
  * classifier rule-first (regex + keyword dict) → skip LLM kalau confidence > 0.8
  * reply cache: kalau comment mirip (cosine > 0.9) pakai reply cached < 5 menit
  * daily budget check sebelum setiap call, block kalau >= BUDGET_IDR_DAILY
  * round-robin multi-key untuk Cartesia dan 9router (sudah ada pool, tinggal wire ke classifier)
- Tidak boleh ada LLM call di hot path tanpa lewat guardrail.

FASE DELIVERABLE (strict order, jangan loncat)

P0 — Audio Library Player [CC-LIVE-CLIP-001..005]
- `core/audio_library/manager.py`: load index.json, fuzzy match by tag
- `adapters/audio_library.py`: playback via sounddevice ke virtual cable
- Svelte panel `lib/components/AudioLibraryGrid.svelte`: grid 160 clip, klik = play, search by tag
- WS command: `audio.list`, `audio.play`, `audio.stop`
- Acceptance: 160 clip ter-index, klik di dashboard → audio keluar < 200ms, tidak ada LLM call

P1 — Comment Classifier [CC-LIVE-CLASSIFIER-001..004]
- `core/classifier/rules.py`: 7 kategori, regex + keyword dict Bahasa Indonesia
- `core/classifier/llm_fallback.py`: lewat guardrail, hanya kalau rule confidence < 0.8
- Badge di Live Comments feed (panel existing)
- WS event: `comment.classified`
- Acceptance: 80% comment ter-klasifikasi rule-only, hemat token terbukti di cost panel

P2 — Suggested Reply (semi-auto) [CC-LIVE-ORCH-001..006]
- `core/orchestrator/suggester.py`: generate 3 opsi reply dari template + LLM (via guardrail + cache)
- Svelte `lib/components/ReplySuggestions.svelte`: 3 tombol, operator klik pilih
- WS: `reply.suggest`, `reply.pick`
- Acceptance: latency < 2s, human-in-the-loop, REPLY_ENABLED tetap bisa false

P3 — Live Director (2-jam state machine) [CC-LIVE-DIRECTOR-001..008]
- `core/orchestrator/director.py`: state machine + timer, auto-stop di 120 menit
- Rotasi produk dari `config/products.yaml` (PALOMA → Reaim Pintu Lipat → TNW Chopper, dst)
- Panel `lib/components/DecisionStream.svelte` + `TwoHourTimer.svelte` + `EmergencyStop.svelte`
- WS: `director.start`, `director.stop`, `director.state`
- Acceptance: live bisa jalan 2 jam tanpa intervensi, hard-stop di 120 menit, log semua keputusan

HEALTH CHECK BARU (extend yang sudah ada)
Tambah probe di HTTP `/health`:
- `audio_library_ready` (index loaded, file count)
- `classifier_ready` (rules loaded, LLM pool alive)
- `director_ready` (state machine instantiated)
- `budget_remaining_idr` (dari cost tracker)

NON-NEGOTIABLE
- TypeScript strict di controller
- Python type hints + ruff check
- Setiap WS command baru harus punya test di `apps/worker/tests/`
- Error handling: tiap adapter wrap try/except, emit `error.*` ke WS, jangan crash worker
- Tiap fase selesai = commit terpisah dengan pesan `[v0.4][CC-LIVE-XXX-NNN] deskripsi`
- Update `docs/CHANGELOG.md` tiap fase

MULAI DARI P0. Jangan lanjut ke P1 sebelum P0 acceptance criteria terpenuhi dan dikonfirmasi.