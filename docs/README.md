# 🎙️ livetik — Bang Hack Live AI Co-Pilot

> AI co-pilot untuk TikTok Live @interiorhack.id. Python worker + Svelte controller, faceless live dengan audio library pre-generated.

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![UV](https://img.shields.io/badge/deps-UV-orange.svg)](https://github.com/astral-sh/uv)
[![Svelte 5](https://img.shields.io/badge/UI-Svelte%205-ff3e00.svg)](https://svelte.dev/)
[![Tailwind v4](https://img.shields.io/badge/CSS-Tailwind%20v4-38bdf8.svg)](https://tailwindcss.com/)
[![Version](https://img.shields.io/badge/version-0.4.6-green.svg)](CHANGELOG.md)

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

**BUKAN HTTP serving ke browser!** Audio files diakses via file system lokal oleh worker, lalu diplay via sounddevice ke VB-CABLE (virtual audio device), yang di-capture OBS sebagai audio input.

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
│                                                          │
│  NOT FOR: Playing audio files or serving to OBS         │
└─────────────────────────────────────────────────────────┘
```

Full diagram: [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) | Workflow detail: [`WORKFLOW_ACTUAL.md`](../WORKFLOW_ACTUAL.md)

## 🚀 Quickstart

### Prasyarat

**Software:**
- Python 3.11+ • [UV](https://github.com/astral-sh/uv) • Node.js 20+ • [pnpm](https://pnpm.io/)
- OBS Studio • [VB-CABLE](https://vb-audio.com/Cable/) (virtual audio device)
- FFmpeg (optional, untuk Edge-TTS fallback)

**API Keys (optional):**
- [Cartesia](https://cartesia.ai) — untuk TTS premium (opsional, bisa pakai Edge-TTS gratis)
- [9router](https://9router.com) — untuk LLM routing (opsional)
- [DeepSeek](https://platform.deepseek.com) / Anthropic — untuk LLM fallback (opsional)

### Install

```bash
git clone https://github.com/bamsbung/livetik.git
cd livetik
cp .env.example .env   # edit API keys & TikTok username

# Worker
cd apps/worker && uv sync && cd ../..

# Controller
cd apps/controller && pnpm install && cd ../..
```

### Generate Audio Library (WAJIB)

```bash
# Windows
scripts\gen_audio_library_edgets.bat

# Linux/Mac
python scripts/gen_audio_library_edgets.py
```

Ini akan generate 108 audio clips (~8-12 menit). Tanpa ini, worker tidak bisa play audio.

### Setup VB-CABLE di OBS

1. Install VB-CABLE dari https://vb-audio.com/Cable/
2. Buka OBS → Settings → Audio
3. Set salah satu "Desktop Audio" ke "CABLE Output (VB-Audio Virtual Cable)"
4. Restart OBS

### Jalan

**Opsi 1: Quick Start (Windows)**
```bash
QUICK_START.bat   # Start worker + controller sekaligus
```

**Opsi 2: Manual dua terminal**
```bash
# Terminal 1 - Worker
cd apps/worker
uv run python -m banghack

# Terminal 2 - Controller
cd apps/controller
pnpm dev   # → http://localhost:5173
```

### Test Audio

1. Buka http://localhost:5173
2. Klik "Audio Library" di sidebar
3. Klik tombol play pada salah satu clip
4. Audio harus terdengar di OBS (cek audio meter)

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
├── QUICK_START.bat                # Windows quick start
└── .env                           # API keys & config (copy from .env.example)
```

**File penting untuk dibaca:**
1. [`WORKFLOW_ACTUAL.md`](../WORKFLOW_ACTUAL.md) — workflow sebenarnya (OBS + VB-Cable)
2. [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) — arsitektur lengkap
3. [`docs/LIVE_PLAN.md`](LIVE_PLAN.md) — strategi 2-hour live
4. [`docs/CHANGELOG.md`](CHANGELOG.md) — history perubahan v0.0.1 → v0.4.6

## 📚 Dokumentasi

### Mulai dari sini
- [WORKFLOW_ACTUAL.md](../WORKFLOW_ACTUAL.md) — ⭐ **BACA INI DULU** - workflow sebenarnya
- [QUICK_START.bat](../QUICK_START.bat) — Windows quick start script
- [CHANGELOG](CHANGELOG.md) — v0.0.1 → v0.4.6 history

### Spesifikasi
- [PRD](PRD.md) — product requirements (apa yang dibangun & tidak)
- [LIVE_PLAN](LIVE_PLAN.md) — strategi 2-hour live (tema, produk, script, runsheet)
- [Architecture](ARCHITECTURE.md) — diagram C4, data flow, IPC, audio routing
- [Design](DESIGN.md) — UX controller, component library

### Development
- [Plan](PLAN.md) — roadmap + tiket coding CC-LIVE-xxx
- [Error Handling](ERROR_HANDLING.md) — matriks error + recovery
- [Agent Brief](AGENT_BRIEF.md) — instruksi untuk Claude Code/Cursor

### Status Sistem
- **Version:** v0.4.6 (2026-04-24)
- **Status:** 85% ready (1 blocker: generate audio library)
- **Cost:** ~Rp 11 per 2-hour session
- **Audio Library:** 108 clips (A_opening → Z_closing)
- **Live Director:** 2-hour state machine (8 phases)
- **Comment Classifier:** 11 intents, rule-first + LLM fallback
- **Reply Suggester:** template + cache + LLM, human-in-the-loop

## 🛠️ Kontribusi

Format commit: `feat|fix|chore|docs|refactor: pesan singkat`  
Buka PR → CI check harus ijo (ruff, mypy, pytest, svelte-check).

## ⚠️ Disclaimer

Bot ini menambahkan **label AI-assisted** di reply. Tidak impersonate manusia. Patuhi TikTok Community Guidelines — **jangan spam, jangan link eksternal, jangan faux-live**.

## 📄 License

MIT © 2026 Dedy Prasetiyo
