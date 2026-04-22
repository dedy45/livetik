# 📁 10 · Structure — Project Organization

> **Canonical**: struktur folder dan file dalam repository. Mirror dari Notion.

---

## 🗂️ Root Level

```
livetik/
├── README.md                 # Project overview
├── DOCS_HUB.md              # Documentation hub
├── QUICKSTART.md            # Setup guide
├── LICENSE                  # MIT License
├── .gitignore               # Git ignore rules
├── .env.example             # Environment template
├── apps/                    # Monorepo applications
├── docs/                    # Documentation files
├── scripts/                 # Development scripts
└── .vscode/                 # VSCode configuration
```

## 📚 Documentation (`docs/`)

```
docs/
├── PRD.md                   # 01 - Product Requirements
├── ARCHITECTURE.md          # 02 - System Architecture
├── DESIGN.md                # 03 - UX/UI Design
├── README.md                # 04 - User Documentation
├── CHANGELOG.md             # 05 - Version History
├── ERROR_HANDLING.md        # 06 - Error Codes
├── PLAN.md                  # 07 - Roadmap & Tickets
├── AGENT_BRIEF.md           # 08 - Coding Guidelines
├── GITHUB.md                # 09 - GitHub Setup & Sync
└── STRUCTURE.md             # 10 - This file
```

## 🐍 Worker (`apps/worker/`)

Python backend (UV managed):

```
apps/worker/
├── pyproject.toml           # Python dependencies
├── src/banghack/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── adapters/            # External services
│   │   ├── tiktok.py        # TikTok Live client
│   │   ├── llm.py           # DeepSeek + Claude
│   │   ├── tts.py           # Edge-TTS
│   │   └── obs.py           # OBS file bridge
│   ├── core/                # Domain logic
│   │   ├── persona.py       # Persona loader
│   │   ├── guardrail.py     # Content filtering
│   │   ├── queue.py         # Rate limiting
│   │   └── events.py        # Event types
│   ├── ipc/                 # IPC
│   │   ├── ws_server.py     # WebSocket
│   │   └── http_api.py      # FastAPI REST
│   ├── config/              # Configuration
│   │   ├── settings.py      # Pydantic settings
│   │   └── persona.md       # Persona prompt
│   └── telemetry/           # Observability
│       ├── logger.py        # JSON logger
│       └── cost.py          # Cost tracker
└── tests/                   # Tests
```

### Module Boundaries

- **adapters/** - I/O dengan external services
- **core/** - Pure domain logic, no I/O
- **ipc/** - Communication dengan controller
- **config/** - Configuration management
- **telemetry/** - Logs, metrics, costs

## 🎨 Controller (`apps/controller/`)

Svelte 5 frontend (pnpm):

```
apps/controller/
├── package.json             # Node dependencies
├── svelte.config.js         # Svelte config
├── vite.config.ts           # Vite config
├── tsconfig.json            # TypeScript config
├── src/
│   ├── app.css              # Tailwind v4 theme
│   ├── app.html             # HTML template
│   ├── routes/              # SvelteKit routes
│   │   ├── +layout.svelte   # Root layout
│   │   ├── +page.svelte     # Dashboard (/)
│   │   ├── live/            # Live monitor
│   │   ├── errors/          # Error log
│   │   ├── persona/         # Persona editor
│   │   ├── config/          # Configuration
│   │   └── cost/            # Cost tracker
│   └── lib/                 # Shared code
│       ├── components/      # UI components
│       ├── stores/          # Svelte stores
│       └── api/             # REST clients
└── static/                  # Static assets
```

### Page Routes

| Route | Purpose |
|-------|---------|
| `/` | Dashboard (6 KPI cards) |
| `/live` | Live monitor split view |
| `/errors` | Error log dengan filter |
| `/persona` | Persona editor (Monaco) |
| `/config` | Configuration form |
| `/cost` | Cost tracker & analytics |

## 🛠️ Scripts (`scripts/`)

```
scripts/
├── install.bat              # Install dependencies
├── dev.bat                  # Development server
├── test.bat                 # Test installation
├── clean.bat                # Clean/reset installation
└── init-github.bat          # GitHub initialization
```

### Usage

```cmd
REM Install
scripts\install.bat

REM Test installation
scripts\test.bat

REM Development
scripts\dev.bat

REM Clean (reset)
scripts\clean.bat

REM GitHub
scripts\init-github.bat
```

## ⚙️ VSCode (`.vscode/`)

```
.vscode/
├── settings.json            # Editor settings
├── launch.json              # Debug configs
└── tasks.json               # Build tasks
```

## 📦 Generated (Not in Git)

```
# Python
apps/worker/.venv/           # Virtual environment
apps/worker/**/__pycache__/  # Python cache

# Node
apps/controller/node_modules/
apps/controller/.svelte-kit/

# Runtime
logs/                        # JSON logs
obs/                         # OBS bridge
_out.mp3                     # TTS temp
.env                         # Secrets
```

## 🔍 Quick Find

| Need | File |
|------|------|
| Ubah persona | `apps/worker/src/banghack/config/persona.md` |
| Tambah guardrail | `apps/worker/src/banghack/core/guardrail.py` |
| Edit dashboard | `apps/controller/src/routes/+page.svelte` |
| Ubah theme | `apps/controller/src/app.css` |
| Tambah API | `apps/worker/src/banghack/ipc/http_api.py` |
| Error codes | `docs/ERROR_HANDLING.md` |
| Ambil tiket | `docs/PLAN.md` |

## 📊 File Count

| Category | Count |
|----------|-------|
| Documentation | 10 files |
| Worker Python | ~20 files |
| Controller Svelte | ~15 files |
| Scripts | 3 files |
| Config | 10 files |
| **Total** | **~60 files** |

## 🔗 External References

- **TikTok Live**: [isaackogan/TikTokLive](https://github.com/isaackogan/TikTokLive)
- **UV**: [astral-sh/uv](https://github.com/astral-sh/uv)
- **Svelte 5**: [svelte.dev](https://svelte.dev/)
- **Tailwind v4**: [tailwindcss.com](https://tailwindcss.com/)

---

**Version**: 0.1.0-dev
