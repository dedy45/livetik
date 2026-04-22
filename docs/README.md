# 🎙️ tiklivenotion — Bang Hack Live AI Co-Pilot

> AI co-pilot untuk TikTok Live @interiorhack.id. Python worker + Svelte controller, stack Rp 0, siap jalan lokal.

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![UV](https://img.shields.io/badge/deps-UV-orange.svg)](https://github.com/astral-sh/uv)
[![Svelte 5](https://img.shields.io/badge/UI-Svelte%205-ff3e00.svg)](https://svelte.dev/)
[![Tailwind v4](https://img.shields.io/badge/CSS-Tailwind%20v4-38bdf8.svg)](https://tailwindcss.com/)

## ✨ Fitur

- 🔴 **TikTok Live scrape** — via [`isaackogan/TikTokLive`](https://github.com/isaackogan/TikTokLive)
- 🧠 **AI reply Bahasa Indonesia** — DeepSeek primary, Claude fallback
- 🔊 **Voice-over otomatis** — Edge-TTS `id-ID-ArdiNeural`
- 🛡️ **Guardrail** — blokir link, brand eksternal, topik sensitif
- 🎮 **Controller UI** — Svelte 5 + Tailwind v4, monitor realtime, edit persona inline
- 💰 **Cost tracker** — budget token DeepSeek, projeksi Rp/hari
- 🎥 **OBS bridge** — text overlay + audio via VB-CABLE

## 🏗️ Arsitektur Singkat

```
Viewer → TikTok → Worker (Python/UV) → LLM → TTS+Text → OBS → TikTok
```

Full diagram: [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)

## 🚀 Quickstart

### Prasyarat

- Python 3.11+ • [UV](https://github.com/astral-sh/uv) • Node.js 20+ • [pnpm](https://pnpm.io/)
- OBS Studio • [VB-CABLE](https://vb-audio.com/Cable/) • FFmpeg
- API key: [DeepSeek](https://platform.deepseek.com) (wajib), Anthropic (opsional)

### Install

```bash
git clone https://github.com/bamsbung/tiklivenotion.git
cd tiklivenotion
cp .env.example .env   # edit API keys & TikTok username

# Worker
cd apps/worker && uv sync && cd ../..

# Controller
cd apps/controller && pnpm install && cd ../..
```

### Jalan

**Opsi 1: concurrent**
```bash
./scripts/dev.sh            # Linux/Mac
./scripts/dev.ps1           # Windows
```

**Opsi 2: manual dua terminal**
```bash
# Terminal 1
cd apps/worker && uv run python -m banghack

# Terminal 2
cd apps/controller && pnpm dev   # → http://localhost:5173
```

### Smoke test

```bash
./scripts/smoke.sh   # cek DeepSeek + Edge-TTS + Guardrail tanpa Live
```

## 🧭 Struktur Repo

```
tiklivenotion/
├── apps/worker/        # Python bot (UV)
├── apps/controller/    # Svelte 5 dashboard
├── docs/               # PRD, Arch, Design, Plan (source of truth)
├── scripts/            # dev.sh, smoke.sh
├── .github/workflows/  # CI
└── .vscode/            # Debug configs
```

Navigasi detail & file pertama saat error: [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)

## 📚 Dokumentasi

- [PRD](PRD.md) — apa yang dibangun & tidak
- [Architecture](ARCHITECTURE.md) — diagram C4, data flow, IPC
- [Design](DESIGN.md) — UX controller, component library
- [Error Handling](ERROR_HANDLING.md) — matriks error + recovery
- [Plan](PLAN.md) — roadmap + tiket coding CC-LIVE-xxx
- [Agent Brief](AGENT_BRIEF.md) — instruksi untuk Claude Code/Cursor
- [CHANGELOG](CHANGELOG.md) — Keep a Changelog format

## 🛠️ Kontribusi

Format commit: `feat|fix|chore|docs|refactor: pesan singkat`  
Buka PR → CI check harus ijo (ruff, mypy, pytest, svelte-check).

## ⚠️ Disclaimer

Bot ini menambahkan **label AI-assisted** di reply. Tidak impersonate manusia. Patuhi TikTok Community Guidelines — **jangan spam, jangan link eksternal, jangan faux-live**.

## 📄 License

MIT © 2026 Dedy Prasetiyo
