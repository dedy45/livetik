# 🤖 08 · Agent Brief — Instruksi untuk VSCode Agent

> **Canonical**: prompt awal untuk agent coding VSCode (Claude Code, Cursor, Windsurf, Copilot Chat, Cline).  
> Paste di session awal.

---

## 0. Ticket Prefix v0.4 (NEW)

Semua tiket v0.4 menggunakan 4 prefix baru:

- **CC-LIVE-CLIP-xxx** — Audio Library (P0: pre-generated 160–220 clip Cartesia, index.json, playback adapter, Svelte grid)
- **CC-LIVE-CLASSIFIER-xxx** — Comment Classifier (P1: rule-first 7 kategori ID, LLM fallback via guardrail, badge UI)
- **CC-LIVE-ORCH-xxx** — Suggested Reply (P2: suggester 3-opsi, reply cache cosine, human-in-the-loop panel)
- **CC-LIVE-DIRECTOR-xxx** — Live Director (P3: state machine 2-jam, products rotation, timer, emergency stop, health check)

**Phase strict order**: P0 → P1 → P2 → P3. Jangan loncat fase sebelum acceptance criteria terpenuhi.

**Referensi wajib v0.4**:
- `docs/LIVE_PLAN.md` — spec 2-jam Cartesia live, script host-led, 160–220 clip
- `docs/ORCHESTRATOR.md` — spec Python worker + Svelte control center, guardrail token-saving, LLM key pool

---

## 1. Copy-Paste System Prompt untuk Agent

```
You are a senior full-stack engineer contributing to `dedy45/livetik`, a monorepo that runs a TikTok Live AI co-pilot.

STACK (non-negotiable):
- apps/worker: Python 3.11+, managed with UV (not pip). Use `uv add`, `uv run`, `uv sync`.
- apps/controller: Svelte 5 (runes: $state, $derived, $effect) + SvelteKit + Tailwind v4 (CSS-first @theme) + pnpm.
- IPC: WebSocket (ws://localhost:8765) + FastAPI REST (http://localhost:8766), loopback only.
- Do NOT introduce: Docker, Redis, PostgreSQL, Celery, Kafka, Next.js, React, npm, poetry, pip, requirements.txt.

READ FIRST (in docs/):
1. PRD.md — what we're building & explicit non-goals.
2. ARCHITECTURE.md — module boundaries, IPC protocol, event flow.
3. DESIGN.md — UI spec & Tailwind theme variables.
4. ERROR_HANDLING.md — error code schema, recovery patterns.
5. PLAN.md — pick the next CC-LIVE-xxx ticket by dependency order.

CODING RULES:
- Python: ruff + mypy strict on `core/` and `adapters/`. Type hints mandatory. Use `asyncio.TaskGroup`, not bare `asyncio.gather`.
- No I/O in `core/` — pure functions/classes. Side effects live in `adapters/` or `ipc/`.
- Svelte: prefer $state / $derived over stores for local state. Use class-based stores only for singletons (WS, REST client).
- Every new function/class gets a docstring (Python) or JSDoc (TS).
- Every domain module gets at least 1 happy-path test + 1 edge case.
- Commit messages: Conventional Commits (feat/fix/chore/docs/refactor/test), scope when touching >1 module.
- Never commit `.env`, `_out.mp3`, `logs/`, `obs/last_reply.txt`.

REFERENCE REPOS (read-only, do not vendor):
- isaackogan/TikTokLive — used as pip/uv dependency `TikTokLive>=5.0.8,<6.0.0`. Wrap, don't fork.
- AutoFTbot/tiktok-ai-auto-reply-live — pattern reference only (Node.js, port concepts to Python).

WHEN IN DOUBT:
- Prefer the path in ARCHITECTURE.md. If it conflicts with your instinct, raise a question in PR comment, don't silently change.
- If a ticket touches an interface, propose the change in PR description before implementing beyond scope.
- Default answer to scope creep: "create a follow-up ticket."

OUTPUT FORMAT:
- For each task: list files to change → diff → tests run → commands to verify.
- Don't invent env vars — all allowed keys are in `.env.example` + `config/settings.py`.
```

---

## 2. Agent Workflow (Per Ticket)

1. **Pick ticket** dari `docs/PLAN.md` urut dependency graph (§3)
2. **Create branch**: `feat/cc-live-<id>-<slug>` — contoh `feat/cc-live-core-002-guardrail`
3. **Implement**: ikuti DoD ticket, jangan lebar
4. **Self-check**:
   - `cd apps/worker && uv run ruff check . && uv run mypy src/`
   - `cd apps/worker && uv run pytest tests/ -v`
   - `cd apps/controller && pnpm svelte-check`
5. **Commit**: Conventional Commits, pesan merujuk ke ticket id
6. **PR**: judul = ticket title, body = DoD checklist + test evidence + any deviations
7. **Update CHANGELOG** di section `[Unreleased]`

---

## 3. Prompt Snippet Spesifik Per Stack

### 3a. Python worker

```
For apps/worker:
- Use UV. Add deps with `uv add <pkg>`. Dev deps: `uv add --dev <pkg>`.
- Directory layout follows src/banghack/{adapters,core,ipc,config,telemetry}/
- Pure domain in core/ (no import of adapters/ipc).
- asyncio everywhere. No threading for network I/O.
- Config via pydantic-settings BaseSettings reading .env.
- Logging via telemetry/logger.py — never bare `print`.
- External API calls MUST be wrapped in a retry helper and emit error events to WS when they fail permanently.
```

### 3b. Svelte controller

```
For apps/controller:
- Use Svelte 5 runes. Write `let count = $state(0)`, NOT `export let`.
- Tailwind v4: utilities from @theme tokens in src/app.css. Don't add `tailwind.config.js`.
- Components in lib/components/, stores in lib/stores/ with .svelte.ts extension.
- WS connection is singleton from lib/stores/ws.svelte.ts — subscribe, don't reconnect per page.
- REST calls via lib/api/*.ts with typed return (share types with worker via `packages/shared` if needed).
- Pages in src/routes/ follow SvelteKit file-based routing.
```

---

## 4. Anti-Patterns (Reject If Seen)

- ❌ `requirements.txt` — we use `pyproject.toml` + UV
- ❌ `npm install` — we use `pnpm`
- ❌ `tailwind.config.js` kompleks — v4 pakai CSS `@theme`
- ❌ Svelte 4 `<script>export let</script>` — pakai runes
- ❌ `threading.Thread` untuk network I/O — pakai asyncio
- ❌ `print(...)` untuk log — pakai logger
- ❌ Hard-coded API URL di komponen — lewat lib/api
- ❌ Import `adapters.*` dari dalam `core/` — break the boundary
- ❌ Commit `.env` dengan real key
- ❌ Giant PR mengubah >5 files non-trivial — split

---

## 5. Task Decomposition Heuristic

Kalau ticket >4 jam estimate → split jadi sub-tickets:

- Interface first (abstract class / protocol + test skeleton)
- Implementation (fill in)
- Integration (wire ke main.py atau route)
- Polish (error handling + logs + metrics)

---

## 6. How Agent Reports Progress

Every PR description:

```markdown
### Ticket
CC-LIVE-CORE-002 — Guardrail engine
### Changes
- Added `core/guardrail.py` with `check_input`, `check_output`
- Added 20 test cases in `tests/test_guardrail.py`
### DoD
- [x] check_input rejects URLs, brands, phone numbers
- [x] check_output rejects same + sensitive topics
- [x] 20 test cases pass
- [x] ruff + mypy clean
### Verify
cd apps/worker && uv run pytest tests/test_guardrail.py -v
### Deviations
(none / list)
```

---

## 7. Scaffold Checklist (M0) — Untuk Agent Pertama Kali

Agent pertama yang kerja harus deliver:

- [ ] Semua folder dari ARCHITECTURE.md struktur
- [ ] `apps/worker/pyproject.toml` dengan deps minimal
- [ ] `apps/worker/src/banghack/__init__.py` dengan `__version__ = "0.1.0-dev"`
- [ ] `apps/worker/src/banghack/main.py` dengan hello-world asyncio loop
- [ ] `apps/controller/package.json` + `svelte.config.js` + `vite.config.ts` + `tailwind.config.ts` + `src/app.css` + `src/app.html` + `src/routes/+layout.svelte` + `src/routes/+page.svelte` (hello)
- [ ] `scripts/dev.sh` + `scripts/dev.ps1` jalankan dua-duanya
- [ ] `.github/workflows/ci.yml` hijau
- [ ] `.vscode/settings.json` + `launch.json` + `tasks.json`
- [ ] `.env.example` lengkap
- [ ] `README.md` paste dari doc 04
- [ ] `LICENSE` MIT
- [ ] `.gitignore` proper (Python UV cache, node_modules, logs/, obs/, .env, _out.mp3)
- [ ] First commit: `chore: scaffold monorepo (CC-LIVE-REPO-001..004)`
