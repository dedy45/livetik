---
inclusion: always
---

# Constraints & Anti-FAKE Rules

## Anti-FAKE Level 5 REAL
Code is only "done" when it is pushed to origin/main AND verifiable via raw.githubusercontent.com.
Never claim "done" without git push confirmation.

## Zero Hardcode Rule
- No config values hardcoded in Python files
- All config via .env (persisted) or .state.json (runtime toggles)
- All config editable via /config UI without restart
- Exception: DEFAULT_FORBIDDEN_PATTERNS in guardrail.py (overridable via update_config)

## Error Handling
- All WS commands wrapped via _wrap_cmd(name, category, handler)
- Exceptions broadcast as error_event with category before re-raising
- error_event visible in /errors page with category filter
- Guardrail.update_config: compile ALL regex before replacing (atomic)
- write_env: atomic via temp-rename, backup .env.bak.<ts> before write

## Budget Hard Cap
- Default: Rp 5,000/day
- Max allowed via UI: Rp 10,000,000
- When over budget: reply loop skips, logs warning
- Budget persisted to .env via set_budget_idr command

## Audio Quality
- Cartesia: pcm_f32le @ 44100 (NEVER pcm_s16le/22050)
- Emotion: always send experimental_controls.emotions = [emotion]
- Default emotion: configurable via CARTESIA_DEFAULT_EMOTION env var

## State Persistence
- REPLY_ENABLED and DRY_RUN persist to .state.json on toggle
- Restored from .state.json on worker startup
- All other config persists to .env via write_env()

## TikTok Hot-Swap
- TikTokSupervisor.disconnect() MUST have 5s timeout
- Never hang the worker on disconnect
- connect_tiktok command writes new username to .env

## Validation Target
- 30 commands registered at startup
- /config: 15 sections visible
- ruff check: 0 errors
- pnpm check: 0 errors
