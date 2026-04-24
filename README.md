# 🎙️ livetik — Bang Hack Live AI Co-Pilot

> AI co-pilot untuk TikTok Live @interiorhack.id. Python worker + Svelte controller, faceless live dengan audio library pre-generated.

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![UV](https://img.shields.io/badge/deps-UV-orange.svg)](https://github.com/astral-sh/uv)
[![Svelte 5](https://img.shields.io/badge/UI-Svelte%205-ff3e00.svg)](https://svelte.dev/)
[![Tailwind v4](https://img.shields.io/badge/CSS-Tailwind%20v4-38bdf8.svg)](https://tailwindcss.com/)
[![Version](https://img.shields.io/badge/version-0.4.6-green.svg)](docs/CHANGELOG.md)

---

## 🎯 START HERE

**Baru pertama kali?** Baca urutan ini:

1. **[README.md](README.md)** — Overview sistem + quick start
2. **[WORKFLOW_ACTUAL.md](WORKFLOW_ACTUAL.md)** — Workflow sebenarnya (OBS + VB-Cable) 🎬
3. **[docs/CHANGELOG.md](docs/CHANGELOG.md)** — Status sistem v0.4.6 📋

**Sudah setup?** Langsung:
```bash
scripts\dev.bat   # Windows - Start worker + controller
```

---

## ✨ Fitur v0.4.6

### Core Features
- 🎵 **Pre-generated Audio Library** — 108+ clip Cartesia/Edge-TTS, fuzzy search, hot-reload
- 🎬 **Live Director** — 2-hour state machine (IDLE → HOOK → DEMO → CTA → REPLY → STOP)
- 🤖 **Comment Classifier** — rule-first (11 intents) + LLM fallback, <10ms
- 💬 **Suggested Reply** — template + cache + LLM, human-in-the-loop
- 🔴 **TikTok Live scrape** — via [`isaackogan/TikTokLive`](https://github.com/isaackogan/TikTokLive)
- 🛡️ **Guardrail** — blokir link, brand eksternal, topik sensitif, budget cap
- 🎮 **Controller UI** — Svelte 5 + Tailwind v4, monitor realtime, audio library grid
- 💰 **Cost tracker** — ~Rp 11 per 2-hour session dengan guardrail aktif

### Audio Flow (CRITICAL)
```
Worker → sounddevice → VB-CABLE → OBS → TikTok Live
```

**PENTING:**
- ❌ **BUKAN HTTP serving** ke browser
- ❌ **BUKAN audio playback** di dashboard
- ✅ **File system access** oleh worker (local files)
- ✅ **sounddevice playback** → VB-CABLE → OBS

---

## 🏗️ Arsitektur Aktual

```
┌─────────────────────────────────────────────────────────┐
│  TikTok Live (@interiorhack.id)                         │
│  Faceless Live - Visual + Voice Only                    │
└─────────────────────────────────────────────────────────┘
                           ▲
                           │ RTMP Stream
                           │
┌─────────────────────────────────────────────────────────┐
│  OBS STUDIO                                             │
│  - Scene: Visual produk/ruangan (looping video)        │
│  - Audio Input: VB-CABLE (virtual audio device)        │
│  - Text Overlay: obs/last_reply.txt (file-based)       │
└─────────────────────────────────────────────────────────┘
                           ▲
                           │
                    ┌──────┴──────┐
                    │             │
              Audio │             │ Text
            (VB-CABLE)            │ (File)
                    │             │
┌─────────────────────────────────────────────────────────┐
│  PYTHON WORKER (apps/worker/)                           │
│  - Audio Library Manager (108 clips)                    │
│  - Live Director (2-hour state machine)                 │
│  - Comment Classifier (rules + LLM fallback)            │
│  - Reply Suggester (template + LLM + cache)             │
│  - TikTok Listener (read-only scrape)                   │
│                                                          │
│  Audio: sounddevice → VB-CABLE → OBS                    │
│  Text: write to obs/last_reply.txt                      │
└─────────────────────────────────────────────────────────┘
                           ▲
                           │ WebSocket (monitoring only)
                           │
┌─────────────────────────────────────────────────────────┐
│  SVELTE CONTROLLER (apps/controller/)                   │
│  http://localhost:5173                                  │
│                                                          │
│  Purpose: MONITORING & MANUAL CONTROL                   │
│  - View live metrics (viewers, comments, cost)          │
│  - Manual approve reply suggestions                     │
│  - Emergency stop                                       │
│  - Audio library preview (metadata only)                │
└─────────────────────────────────────────────────────────┘
```

Full diagram: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## 🚀 Quickstart (15 Menit)

### 1. Install Dependencies

```bash
# Run install script
scripts\install.bat
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env: set TIKTOK_USERNAME, CARTESIA_API_KEYS
```

### 3. Generate Audio Library (WAJIB)

```bash
scripts\gen_audio_library_edgets.bat
```

Ini akan generate 108 audio clips (~8-12 menit). **Tanpa ini, worker tidak bisa play audio!**

### 4. Setup VB-CABLE di OBS

1. Install VB-CABLE dari https://vb-audio.com/Cable/
2. OBS → Settings → Audio → Desktop Audio = "CABLE Output"
3. Restart OBS

### 5. Start System

```bash
# Start worker + controller (opens 2 windows)
scripts\dev.bat
```

### 6. Open Dashboard

http://localhost:5173

**Test audio:** Audio Library page → Click play button → Audio harus terdengar di OBS

---

## 🧭 Struktur Repo

```
livetik/
├── apps/
│   ├── worker/                    # Python worker (UV)
│   │   ├── src/banghack/
│   │   │   ├── adapters/          # TikTok, LLM, TTS, Audio Library
│   │   │   ├── core/              # Persona, Guardrail, Queue, Classifier, Orchestrator
│   │   │   ├── ipc/               # WebSocket + HTTP server
│   │   │   └── main.py            # Entry point
│   │   └── static/audio_library/  # 108 pre-generated clips + index.json
│   └── controller/                # Svelte 5 dashboard
│       ├── src/routes/            # Dashboard, Live, Config, Persona, Cost, Library
│       └── src/lib/stores/        # WebSocket store, reactive state
├── config/                        # Persona, clips script, products, reply templates
├── docs/                          # PRD, Architecture, Design, Plan, LIVE_PLAN
├── scripts/                       # gen_audio_library, dev, health_check
├── obs/                           # last_reply.txt (text overlay bridge)
├── WORKFLOW_ACTUAL.md             # ⭐ BACA INI DULU - workflow sebenarnya
├── QUICKSTART.md                  # Setup 15 menit
├── QUICK_START.bat                # Windows quick start
└── .env                           # API keys & config (copy from .env.example)
```

---

## 📚 Dokumentasi

### Core Docs
- **[README.md](README.md)** — Overview sistem + quick start ⚡
- **[WORKFLOW_ACTUAL.md](WORKFLOW_ACTUAL.md)** — Workflow sebenarnya (OBS + VB-Cable) 🎬
- **[QUICK_START.bat](QUICK_START.bat)** — Windows quick start script

### Specifications
- [PRD](docs/PRD.md) — Product requirements
- [LIVE_PLAN](docs/LIVE_PLAN.md) — Strategi 2-hour live
- [ARCHITECTURE](docs/ARCHITECTURE.md) — System architecture
- [DESIGN](docs/DESIGN.md) — UX design

### Development
- [CHANGELOG](docs/CHANGELOG.md) — v0.0.1 → v0.4.6 history
- [PLAN](docs/PLAN.md) — Roadmap + tickets
- [ERROR_HANDLING](docs/ERROR_HANDLING.md) — Error matrix
- [AGENT_BRIEF](docs/AGENT_BRIEF.md) — Agent instructions

### Status Sistem (v0.4.6)
- **Status:** 85% ready (1 blocker: generate audio library)
- **Cost:** ~Rp 11 per 2-hour session
- **Audio Library:** 108 clips (A_opening → Z_closing)
- **Live Director:** 2-hour state machine (8 phases)
- **Comment Classifier:** 11 intents, rule-first + LLM fallback
- **Reply Suggester:** template + cache + LLM, human-in-the-loop

---

## 🛠️ Kontribusi

Format commit: `feat|fix|chore|docs|refactor: pesan singkat`  
Buka PR → CI check harus ijo (ruff, mypy, pytest, svelte-check).

## ⚠️ Disclaimer

Bot ini menambahkan **label AI-assisted** di reply. Tidak impersonate manusia. Patuhi TikTok Community Guidelines — **jangan spam, jangan link eksternal, jangan faux-live**.

## 📄 License

MIT © 2026 Dedy Prasetiyo
