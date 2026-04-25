---
inclusion: always
---
 Project Structure — livetik monorepo

```
livetik/
├── apps/
│   ├── worker/                    # Python backend
│   │   ├── src/banghack/
│   │   │   ├── adapters/
│   │   │   │   ├── cartesia_pool.py   # 5-key pool with add/remove CRUD
│   │   │   │   ├── llm.py             # LiteLLM Router 3-tier
│   │   │   │   ├── tiktok.py          # TikTokLive adapter
│   │   │   │   └── tts.py             # Cartesia + edge-tts fallback
│   │   │   ├── core/
│   │   │   │   ├── config_store.py    # .env writer + .state.json persist
│   │   │   │   ├── cost.py            # Cost tracker (mutable tariff)
│   │   │   │   ├── guardrail.py       # Reconfigurable filter
│   │   │   │   ├── persona.py         # Persona loader
│   │   │   │   ├── queue.py           # Reply queue
│   │   │   │   └── tiktok_supervisor.py  # Hot-swap TikTok adapter
│   │   │   ├── ipc/
│   │   │   │   ├── audio.py           # sounddevice device lister
│   │   │   │   ├── http_server.py     # FastAPI HTTP API
│   │   │   │   └── ws_server.py       # WebSocket server
│   │   │   └── main.py               # Entry point (30 commands)
│   │   ├── config/
│   │   │   └── persona.md            # Bang Hack persona (editable via UI)
│   │   └── pyproject.toml
│   └── controller/                # SvelteKit frontend
│       └── src/routes/
│           ├── +page.svelte          # Dashboard
│           ├── config/+page.svelte   # Config & Validation (15 sections)
│           ├── persona/+page.svelte  # Persona editor
│           ├── cost/+page.svelte     # Cost tracker + 7d chart
│           ├── errors/+page.svelte   # Error stream
│           └── live/+page.svelte     # Live comment feed
├── .kiro/steering/               # Kiro context files
├── .env                          # Config (never commit secrets)
├── .state.json                   # Runtime toggle persistence
└── costs.jsonl                   # Hourly cost log
```

## Command Count
- P2-C: 19 commands
- P2-D bonus: +1 (save_persona) = 19 total
- P3: +11 new = 30 total commands registered
