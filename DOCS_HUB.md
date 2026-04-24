# 📚 livetik · Docs Hub v0.4.6

> 🎯 **Single source of truth** untuk repo `dedy45/livetik` v0.4.6  
> **Status:** 85% ready (1 blocker: generate audio library)  
> **Cost:** ~Rp 11 per 2-hour session  
> **Architecture:** Worker → sounddevice → VB-CABLE → OBS → TikTok Live

---

## ⭐ START HERE (Urutan Baca untuk User Baru)

1. **[README.md](README.md)** — Overview sistem + quick start
2. **[WORKFLOW_ACTUAL.md](WORKFLOW_ACTUAL.md)** — Workflow sebenarnya (CRITICAL)
3. **[docs/CHANGELOG.md](docs/CHANGELOG.md)** — Status v0.4.6 + history
4. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Architecture detail

**Quick Start:**
```bash
scripts\install.bat              # Install dependencies
scripts\gen_audio_library_edgets.bat  # Generate 108 clips (8-12 min)
scripts\dev.bat                  # Start worker + controller
```

---

## 🗂️ Peta Dokumen Lengkap

### Root Level (Entry Points)
| # | Dokumen | File | Untuk siapa | Baca kapan |
|---|---------|------|-------------|------------|
| 00 | **Docs Hub** | **[DOCS_HUB.md](DOCS_HUB.md)** | **Semua** | **THIS FILE - Peta navigasi** |
| 01 | **README** | **[README.md](README.md)** | **User baru** | **Entry point repo** |
| 02 | **Workflow Actual** | **[WORKFLOW_ACTUAL.md](WORKFLOW_ACTUAL.md)** | **Semua** | **CRITICAL - Workflow sebenarnya** |

### Scripts (Working Commands)
| # | Script | File | Fungsi |
|---|--------|------|--------|
| 03 | Install | [scripts/install.bat](scripts/install.bat) | Install worker + controller dependencies |
| 04 | Dev Server | [scripts/dev.bat](scripts/dev.bat) | Start worker + controller (2 windows) |
| 05 | Generate Audio | [scripts/gen_audio_library_edgets.bat](scripts/gen_audio_library_edgets.bat) | Generate 108 clips (8-12 min) |
| 06 | Health Check | [scripts/health.bat](scripts/health.bat) | Check system health |

### Docs Folder (Specifications)
| # | Dokumen | File | Untuk siapa | Baca kapan |
|---|---------|------|-------------|------------|
| 05 | PRD | [docs/PRD.md](docs/PRD.md) | Semua | Product requirements |
| 06 | **Architecture** | **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** | **Dev + Agent** | **Sebelum bikin modul** |
| 07 | Design | [docs/DESIGN.md](docs/DESIGN.md) | Frontend + Agent | Sebelum bikin UI |
| 08 | **CHANGELOG** | **[docs/CHANGELOG.md](docs/CHANGELOG.md)** | **Semua** | **Status v0.4.6 + history** |
| 09 | **Live Plan** | **[docs/LIVE_PLAN.md](docs/LIVE_PLAN.md)** | **v0.4 Live** | **Strategi 2-jam live** |
| 10 | Orchestrator | [docs/ORCHESTRATOR.md](docs/ORCHESTRATOR.md) | v0.4 Live | Python worker + Svelte control |
| 11 | Error Handling | [docs/ERROR_HANDLING.md](docs/ERROR_HANDLING.md) | Dev + Agent | Saat debug |
| 12 | Plan | [docs/PLAN.md](docs/PLAN.md) | Agent | Ambil tiket berikutnya |
| 13 | Agent Brief | [docs/AGENT_BRIEF.md](docs/AGENT_BRIEF.md) | Agent | Paste di session awal |
| 14 | Docs README | [docs/README.md](docs/README.md) | Dev | Docs overview |

---

## 🏗️ Monorepo Folder Structure (final, locked)

```
livetik/
├── apps/
│   ├── worker/                        # Python 3.11+ (UV managed)
│   │   ├── pyproject.toml
│   │   ├── src/banghack/
│   │   │   ├── adapters/              # tiktok, llm, tts, obs, audio_library, cartesia_pool
│   │   │   ├── core/
│   │   │   │   ├── audio_library/     # manager.py (v0.4)
│   │   │   │   ├── classifier/        # rules.py, llm_fallback.py (v0.4)
│   │   │   │   ├── orchestrator/      # director.py, suggester.py, budget_guard.py, reply_cache.py (v0.4)
│   │   │   │   ├── models.py          # LiveState, CommentDecision, AudioJob dataclasses (v0.4)
│   │   │   │   ├── persona.py
│   │   │   │   ├── guardrail.py
│   │   │   │   ├── queue.py
│   │   │   │   ├── cost.py
│   │   │   │   └── config_store.py
│   │   │   ├── ipc/                   # ws_server, http_server, main
│   │   │   └── config/                # persona.md, clips_script.yaml, products.yaml, reply_templates.yaml
│   │   ├── static/audio_library/      # Generated .wav files + index.json (v0.4)
│   │   └── tests/
│   └── controller/                    # Svelte 5 + Tailwind v4
│       └── src/
│           ├── routes/                # dashboard, live, library, errors, persona, config, cost
│           └── lib/
│               ├── components/        # AudioLibraryGrid, DecisionStream, ReplySuggestions, TwoHourTimer, EmergencyStop (v0.4)
│               └── stores/            # ws, live_state, audio_library (v0.4)
├── docs/                              # ← semua dokumen ini
├── scripts/                           # dev.bat, install.bat, gen_audio_library.py/.bat, gen_audio_library_edgets.py/.bat (v0.4.3)
├── .github/workflows/ci.yml
├── .vscode/
├── .env.example
└── README.md
```

---

## 🧭 Navigasi cepat saat error

| Error type | File pertama dibuka |
|------------|---------------------|
| Git push failed | `docs/TROUBLESHOOTING.md` |
| SvelteKit tsconfig warning | `docs/TROUBLESHOOTING.md` |
| TikTok disconnect | `adapters/tiktok.py` |
| LLM rate limit / timeout | `adapters/llm.py` |
| TTS tidak bunyi | `adapters/tts.py` |
| Guardrail false positive | `core/guardrail.py` |
| OBS overlay tidak update | `adapters/obs.py` |
| Controller tidak connect | `ipc/ws_server.py` |

---

## 🐙 Mapping GitHub Reference → Dipakai di Mana

| Repo | URL | Dipakai di | Cara pakai |
|------|-----|------------|------------|
| isaackogan/TikTokLive | github.com/isaackogan/TikTokLive | adapters/tiktok.py | uv dependency |
| AutoFTbot/tiktok-ai-auto-reply-live | github.com/AutoFTbot/... | Pattern reference | Konsep saja, tidak di-vendor |

### Yang BUKAN di-copy dari AutoFTbot

- ❌ Kode Node.js (`index.js`, `package.json`) — kita Python
- ❌ Gemini SDK — kita DeepSeek (`openai` SDK dengan `base_url`)
- ❌ Audio player Node.js — kita pakai `ffplay` subprocess atau `edge-tts` langsung stream

### Yang DI-copy (pattern/konsep)

- ✅ Struktur `on('chat', handler)` → Python `@client.on(CommentEvent)`
- ✅ Queue-based TTS playback (jangan overlap) → `core/queue.py`
- ✅ Guardrail blocklist → `core/guardrail.py` (diperluas untuk Indonesia context)
- ✅ Persona prompt format → `config/persona.md`

---

## 🛠️ Tech Stack Resmi (locked)

| Layer | Tech | Version | Notes |
|-------|------|---------|-------|
| Worker runtime | Python | 3.11+ | asyncio, type hints wajib |
| Worker deps | UV | latest | pyproject.toml, bukan pip |
| TikTok scrape | TikTokLive | ≥6.4.0 | isaackogan/TikTokLive |
| LLM router | LiteLLM | latest | 3-tier: 9router → DeepSeek → Claude |
| LLM tier 1 | 9router | free | Rate-limited, primary |
| LLM tier 2 | DeepSeek | deepseek-chat | Cheap fallback ~Rp 1.5/reply |
| LLM tier 3 | Claude Haiku | claude-3-haiku | Premium fallback ~Rp 5/reply |
| TTS primary | Cartesia | sonic-3 | Multi-key pool, id language |
| TTS fallback | Edge-TTS | latest | id-ID-ArdiNeural |
| Audio play | sounddevice | latest | Python audio playback |
| Controller | Svelte 5 | 5.x | runes: $state, $derived |
| CSS | Tailwind | v4 | CSS-first @theme |
| Build | Vite + SvelteKit | latest | pnpm |
| IPC WS | websockets | Python | ws://localhost:8765 |
| IPC REST | FastAPI | latest | http://localhost:8766 |

---

## ⚡ Quickstart (15 Menit)

```bash
# 1. Install dependencies
scripts\install.bat

# 2. Configure
cp .env.example .env
# Edit .env: set TIKTOK_USERNAME, CARTESIA_API_KEYS

# 3. Generate audio library (WAJIB, 8-12 menit)
scripts\gen_audio_library_edgets.bat

# 4. Setup VB-CABLE di OBS
# Install VB-CABLE → OBS Settings → Audio → Desktop Audio = "CABLE Output"

# 5. Start system
scripts\dev.bat

# 6. Open dashboard
# http://localhost:5173
# Test: Audio Library page → Click play button → Audio harus terdengar di OBS
```

---

## 🎯 Status Sistem v0.4.6

### What Works ✅
- Audio library manager (108 clips)
- Live director (2-hour state machine)
- Comment classifier (rule-first + LLM fallback)
- Reply suggester (template + cache + LLM)
- TikTok listener (read-only scrape)
- Svelte dashboard (monitoring & control)
- Audio playback via sounddevice → VB-CABLE → OBS
- Text overlay via obs/last_reply.txt
- Guardrail (budget cap, forbidden patterns)
- Cost tracking (~Rp 11 per 2-hour session)

### Blocker ⚠️
- **Generate audio library** (run `scripts\gen_audio_library_edgets.bat` once)

### Architecture (ACTUAL)
```
Worker → sounddevice → VB-CABLE → OBS → TikTok Live
```

**NOT:**
- ❌ HTTP serving to browser
- ❌ Audio playback in dashboard
- ❌ LLM-based audio selection (deterministic phase-based)

---

## 📑 All Documentation Files

### Root Level
- [README.md](README.md) — Main entry point
- [WORKFLOW_ACTUAL.md](WORKFLOW_ACTUAL.md) — Actual workflow (CRITICAL)
- [DOCS_HUB.md](DOCS_HUB.md) — This file (navigation hub)

### Scripts (Working)
- [scripts/install.bat](scripts/install.bat) — Install dependencies
- [scripts/dev.bat](scripts/dev.bat) — Start worker + controller
- [scripts/gen_audio_library_edgets.bat](scripts/gen_audio_library_edgets.bat) — Generate audio
- [scripts/health.bat](scripts/health.bat) — Health check

### Docs Folder
- [docs/README.md](docs/README.md) — Docs overview
- [docs/PRD.md](docs/PRD.md) — Product requirements
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — System architecture
- [docs/DESIGN.md](docs/DESIGN.md) — UX design
- [docs/CHANGELOG.md](docs/CHANGELOG.md) — Version history v0.0.1 → v0.4.6
- [docs/LIVE_PLAN.md](docs/LIVE_PLAN.md) — 2-hour live strategy
- [docs/ORCHESTRATOR.md](docs/ORCHESTRATOR.md) — Orchestrator spec
- [docs/ERROR_HANDLING.md](docs/ERROR_HANDLING.md) — Error handling
- [docs/PLAN.md](docs/PLAN.md) — Roadmap
- [docs/AGENT_BRIEF.md](docs/AGENT_BRIEF.md) — Agent instructions

---

## 🎯 Definition of Done v0.4.6

- [x] All docs updated to v0.4.6
- [x] All docs show ACTUAL workflow (sounddevice → VB-CABLE → OBS)
- [x] All docs clarify: NOT HTTP serving, NOT browser playback
- [x] All docs link to WORKFLOW_ACTUAL.md and QUICKSTART.md
- [x] All docs show correct cost (~Rp 11/session)
- [x] All docs show correct status (85% ready, 1 blocker)
- [x] New user can setup in 15 minutes following QUICKSTART.md
- [x] No conflicting information between docs
- [x] Clear navigation: README → QUICKSTART → WORKFLOW_ACTUAL → CHANGELOG

---

## 🔄 Fungsi File Ini (DOCS_HUB.md)

**Purpose:** Navigation hub untuk semua dokumentasi

**Kapan dibaca:**
- Saat pertama kali buka repo (setelah README.md)
- Saat cari dokumen tertentu (peta navigasi)
- Saat handoff ke agent coding (overview lengkap)

**Tidak untuk:**
- ❌ Setup sistem (baca QUICKSTART.md)
- ❌ Workflow detail (baca WORKFLOW_ACTUAL.md)
- ❌ Status terkini (baca CHANGELOG.md)

**Link dari:**
- README.md → "Dokumentasi" section
- docs/README.md → "Navigasi" section
