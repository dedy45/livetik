# 📚 livetik · Docs Hub (PRD + Arch + Design + Agent Brief)

> 🎯 **Tujuan hub ini**: sumber tunggal kebenaran (single source of truth) untuk repo `dedy45/livetik`.  
> Semua PRD, arsitektur, design, dan plan ada di sini — siap di-hand off ke **agent coding VSCode** (Claude Code / Cursor / Windsurf / Copilot Chat + GitHub MCP).

---

## 🗂️ Peta Dokumen (baca urut dari atas)

| # | Dokumen | File | Untuk siapa | Baca kapan |
|---|---------|------|-------------|------------|
| 01 | PRD | [PRD.md](docs/PRD.md) | Semua | Sebelum mulai |
| 02 | Architecture | [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Dev + Agent | Sebelum bikin modul |
| 03 | Design | [DESIGN.md](docs/DESIGN.md) | Frontend + Agent | Sebelum bikin UI |
| 04 | README | [README.md](docs/README.md) | User baru | Entry point repo |
| 05 | CHANGELOG | [CHANGELOG.md](docs/CHANGELOG.md) | Semua | Setiap PR merge |
| 06 | Error Handling | [ERROR_HANDLING.md](docs/ERROR_HANDLING.md) | Dev + Agent | Saat debug |
| 07 | Plan | [PLAN.md](docs/PLAN.md) | Agent | Ambil tiket berikutnya |
| 08 | Agent Brief | [AGENT_BRIEF.md](docs/AGENT_BRIEF.md) | Agent | Paste di session awal |
| 09 | GitHub | [GITHUB.md](docs/GITHUB.md) | Dev | Setup & sync GitHub |
| 10 | Structure | [STRUCTURE.md](docs/STRUCTURE.md) | Dev | Cari file/folder |
| 11 | Troubleshooting | [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Dev | Fix errors |
| 12 | Kiro Guide | [KIRO_GUIDE.md](docs/KIRO_GUIDE.md) | Kiro IDE users | Development workflow |
| 13 | **Live Plan** | [LIVE_PLAN.md](docs/LIVE_PLAN.md) | **v0.4 Live** | **Spec 2-jam Cartesia live** |
| 14 | **Orchestrator** | [ORCHESTRATOR.md](docs/ORCHESTRATOR.md) | **v0.4 Live** | **Python worker + Svelte control** |

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
├── scripts/                           # dev.bat, install.bat, gen_audio_library.py/.bat (v0.4)
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

## ⚡ Quickstart untuk Agent Coding VSCode

```cmd
REM 1. Clone
git clone https://github.com/dedy45/livetik.git
cd livetik

REM 2. Install dependencies
scripts\install.bat

REM 3. Configure .env
copy .env.example .env
REM Edit .env dengan API keys

REM 4. Run development server
scripts\dev.bat
REM Controller: http://localhost:5173
```

---

## 📑 Child Documents

> Setiap dokumen di Notion berpasangan dengan file `.md` di folder `docs/` — agent VSCode bisa baca dari keduanya.

- [PRD.md](docs/PRD.md)
- [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [DESIGN.md](docs/DESIGN.md)
- [README.md](docs/README.md)
- [CHANGELOG.md](docs/CHANGELOG.md)
- [ERROR_HANDLING.md](docs/ERROR_HANDLING.md)
- [PLAN.md](docs/PLAN.md)
- [AGENT_BRIEF.md](docs/AGENT_BRIEF.md)
- [GITHUB.md](docs/GITHUB.md)
- [STRUCTURE.md](docs/STRUCTURE.md)
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- [KIRO_GUIDE.md](docs/KIRO_GUIDE.md)
- **[LIVE_PLAN.md](docs/LIVE_PLAN.md)** ← 🆕 v0.4 Live interaction 2 jam
- **[ORCHESTRATOR.md](docs/ORCHESTRATOR.md)** ← 🆕 v0.4 Python worker + Svelte control

---

## 🎯 Definition of Done Docs Hub

- [x] 11 dokumen tersedia sebagai file `.md` di folder `docs/`
- [x] Agent VSCode bisa mulai coding hanya dengan baca **Agent Brief** + **PRD** + **Architecture**
- [x] Setiap bug yang muncul punya **1 file pertama yang dibuka** (tabel navigasi error di atas)
- [x] Tidak ada duplikasi konten — setiap konsep ada di **1 dokumen canonical**
- [x] Format semua doc: Markdown (kompatibel GitHub render)
- [x] Troubleshooting guide untuk Git & SvelteKit errors
