# 🎙️ livetik — Bang Hack Live AI Co-Pilot

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

Full diagram: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## 🚀 Quickstart

### Prasyarat

- Python 3.11+ • [UV](https://github.com/astral-sh/uv) • Node.js 20+ • [pnpm](https://pnpm.io/)
- OBS Studio • [VB-CABLE](https://vb-audio.com/Cable/) • FFmpeg
- API key: [DeepSeek](https://platform.deepseek.com) (wajib), Anthropic (opsional)

### Install

```cmd
git clone https://github.com/dedy45/livetik.git
cd livetik

REM Install dependencies
scripts\install.bat

REM Configure environment
copy .env.example .env
REM Edit .env dengan API keys
```

### Jalan

**Windows**:
```cmd
scripts\dev.bat
```

**Manual (dua terminal)**:
```cmd
REM Terminal 1
cd apps\worker
uv run python -m banghack

REM Terminal 2
cd apps\controller
pnpm dev
REM → http://localhost:5173
```

### Smoke test

```cmd
REM Verify setup
cd apps\worker
uv run python -c "import TikTokLive, openai, edge_tts"
echo Setup OK!
```

## 🧭 Struktur Repo

```
livetik/
├── apps/worker/        # Python bot (UV)
├── apps/controller/    # Svelte 5 dashboard
├── docs/               # PRD, Arch, Design, Plan (source of truth)
├── scripts/            # dev.bat, install.bat
└── .vscode/            # Debug configs
```

Navigasi detail & file pertama saat error: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## 📚 Dokumentasi

- [DOCS_HUB](DOCS_HUB.md) — Peta semua dokumen
- [QUICKSTART](QUICKSTART.md) — Setup 5 menit
- [PRD](docs/PRD.md) — apa yang dibangun & tidak
- [Architecture](docs/ARCHITECTURE.md) — diagram C4, data flow, IPC
- [Design](docs/DESIGN.md) — UX controller, component library
- [Error Handling](docs/ERROR_HANDLING.md) — matriks error + recovery
- [Plan](docs/PLAN.md) — roadmap + tiket coding CC-LIVE-xxx
- [Agent Brief](docs/AGENT_BRIEF.md) — instruksi untuk Claude Code/Cursor
- [CHANGELOG](docs/CHANGELOG.md) — Keep a Changelog format
- [GitHub](docs/GITHUB.md) — GitHub setup & sync
- [Structure](docs/STRUCTURE.md) — Project structure
- [Troubleshooting](docs/TROUBLESHOOTING.md) — Fix common errors

## 💾 Backup ke GitHub

**Quick backup:**
```cmd
scripts\backup-github.bat
```

**Manual:**
```cmd
git add .
git commit -m "Backup: update"
git push origin master
```

Troubleshooting: [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)

## 🛠️ Kontribusi

Format commit: `feat|fix|chore|docs|refactor: pesan singkat`  
Buka PR → CI check harus ijo (ruff, mypy, pytest, svelte-check).

## ⚠️ Disclaimer

Bot ini menambahkan **label AI-assisted** di reply. Tidak impersonate manusia. Patuhi TikTok Community Guidelines — **jangan spam, jangan link eksternal, jangan faux-live**.

## 📄 License

MIT © 2026 Dedy Prasetiyo
