# 🔍 Real State Audit — Livetik Dashboard Status

> **Document Type**: Technical Audit Report  
> **Project**: livetik (dedy45/livetik)  
> **Branch**: master  
> **Audit Date**: 2026-04-22  
> **Status**: Dashboard at Level 1/5 (Exists but 100% Mock)

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Audit Methodology](#audit-methodology)
3. [File Presence Matrix](#file-presence-matrix)
4. [Critical Findings](#critical-findings)
5. [Discrepancies](#discrepancies)
6. [Priority Action Plan](#priority-action-plan)
7. [Smoke Test Procedure](#smoke-test-procedure)
8. [Definition of REAL](#definition-of-real)
9. [KIRO Execution Prompt](#kiro-execution-prompt)
10. [Common Pitfalls](#common-pitfalls)
11. [Executive Summary for Stakeholders](#executive-summary-for-stakeholders)

---

## 🎯 Executive Summary

**Verdict**: Scaffold exists at Level 1 of 5. Dashboard displays but is **100% mock** — all state hardcoded, no WebSocket subscription, worker only prints heartbeat. Levels 2-5 (Compile clean → Test → Integrate → Observable) **not yet achieved**.

**Action Required**: 9 priority tasks (P0/P1/P2/P3) to make dashboard truly live.

**Completion Status**: ~28% (9 files exist + 2 mock files + 21 files missing/404)

---

## 🔬 Audit Methodology

### Why This Audit Exists

Notion ↔ GitHub connector is **read-only + frequently errors** (confirmed 8× failures this session). This audit uses direct fetch to `raw.githubusercontent.com/dedy45/livetik/master/<path>` which works reliably.

**Branch Note**: Default branch = `master`, NOT `main` — all Notion docs referencing `git push origin main` will fail.

### Verification Method (Reproducible)

```bash
https://raw.githubusercontent.com/dedy45/livetik/master/<path>
→ File exists: returns file content
→ File missing: returns "404: Not Found"
```

**Evidence Standard**: Every ✅ means file was actually downloaded and inspected. Every ❌ means HTTP 404 confirmed.

---

## 📊 File Presence Matrix

### Configuration & Documentation

| Path | Status | Notes |
|------|--------|-------|
| `README.md` | ✅ EXISTS | References repo as "tiklivenotion" — inconsistent with URL `dedy45/livetik` |
| `DOCS_HUB.md` | ✅ EXISTS | 12 entries, links to `docs/*.md` |
| `QUICKSTART.md` | ✅ EXISTS | 3-step install, Windows-first (good) |
| `.env.example` | ✅ EXISTS | **Complete** — all worker keys + IPC ports present |
| `scripts/dev.bat` | ✅ EXISTS | Starts worker + controller in separate windows |
| `scripts/install.bat` | ✅ REFERENCED | Not inspected but called by dev.bat |

### Controller (Frontend - Svelte 5)

| Path | Status | Notes |
|------|--------|-------|
| `apps/controller/package.json` | ✅ EXISTS | Svelte 5 + Tailwind v4 + SvelteKit 2 + Vite 5 ✅ **STACK CORRECT** |
| `apps/controller/src/app.css` | ✅ EXISTS | Tailwind v4 `@theme` • all design tokens ✅ |
| `apps/controller/src/routes/+layout.svelte` | ⚠️ EXISTS (MINIMAL) | Only top navbar — **NO 6-nav sidebar** per Design §2. Uses `<slot />` (Svelte 4 syntax, deprecated in Svelte 5) |
| `apps/controller/src/routes/+page.svelte` | ⚠️ EXISTS (MOCK) | 6 KPI cards display but **all values hardcoded** `$state('disconnected')` / `$state('00:00:00')` / `$state(0)`. No WS subscription. |
| `apps/controller/src/routes/live/+page.svelte` | ❌ 404 | Live monitor route not created |
| `apps/controller/src/routes/errors/+page.svelte` | ❌ 404 | Errors route not created |
| `apps/controller/src/routes/persona/+page.svelte` | ❌ 404 | Persona route not created |
| `apps/controller/src/routes/config/+page.svelte` | ❌ 404 | Config route not created |
| `apps/controller/src/routes/cost/+page.svelte` | ❌ 404 | Cost route not created |
| `apps/controller/src/lib/stores/ws.svelte.ts` | ❌ 404 | **CRITICAL** — without this, dashboard will never connect |
| `apps/controller/src/lib/components/*` | ❌ 404 | No `KPICard.svelte`, `StatusPill.svelte`, etc. |

### Worker (Backend - Python)

| Path | Status | Notes |
|------|--------|-------|
| `apps/worker/pyproject.toml` | ✅ EXISTS | Complete deps, hatchling build, ruff+mypy strict ✅ |
| `apps/worker/src/banghack/main.py` | ⚠️ EXISTS (SKELETON) | Only `while True: await asyncio.sleep(30); print("heartbeat")`. All init = TODO comments. **Does not start WS server, load config, or init any adapters.** |
| `apps/worker/src/banghack/__main__.py` | ❌ 404 | Consequence: `python -m banghack` (called by dev.bat) **will fail** — entry point `-m` requires `__main__.py` |
| `apps/worker/src/banghack/ipc/ws_server.py` | ❌ 404 | **CRITICAL** — no WS server = dashboard impossible to be live |
| `apps/worker/src/banghack/ipc/http_api.py` | ❌ 404 | REST API not implemented |
| `apps/worker/src/banghack/adapters/tiktok.py` | ❌ 404 | TikTok adapter missing |
| `apps/worker/src/banghack/adapters/llm.py` | ❌ 404 | LLM adapter missing |
| `apps/worker/src/banghack/adapters/tts.py` | ❌ 404 | TTS adapter missing |
| `apps/worker/src/banghack/adapters/obs.py` | ❌ 404 | OBS adapter missing |
| `apps/worker/src/banghack/core/guardrail.py` | ❌ 404 | Guardrail logic missing |
| `apps/worker/src/banghack/core/queue.py` | ❌ 404 | Queue management missing |
| `apps/worker/src/banghack/core/persona.py` | ❌ 404 | Persona logic missing |
| `apps/worker/src/banghack/config/persona.md` | ❌ 404 | Persona config missing |

### KIRO Configuration

| Path | Status | Notes |
|------|--------|-------|
| `.kiro/steering/product.md` | ❌ 404 | Not yet pasted from Notion spec |
| `.kiro/steering/tech.md` | ❌ 404 | Not yet pasted from Notion spec |
| `.kiro/steering/structure.md` | ❌ 404 | Not yet pasted from Notion spec |
| `.kiro/steering/style.md` | ❌ 404 | Not yet pasted from Notion spec |
| `.kiro/specs/01-scaffold-boot/*` | ❌ 404 | Spec not yet pasted |

### Summary Statistics

- **Files Present**: 9 complete + 2 mock/minimal = 11 files
- **Files Missing**: 21 files (404)
- **Completion Rate**: ~28% (execution files only, excluding documentation)

---

## 🔴 Critical Findings

### Finding #1: Dashboard = 100% MOCK

**Issue**: Direct answer to complaint "dashboard incomplete, doesn't match design"

**Evidence** — Content of `apps/controller/src/routes/+page.svelte` lines 2-4:

```typescript
let status = $state('disconnected');
let uptime = $state('00:00:00');
let queueSize = $state(0);
```

6 KPI cards hardcoded with literals "0", "Rp 0", "Disconnected". No `onMount`, no fetch, no WebSocket. Values **will never change** even if worker runs.

**Root Cause**: WS store (`lib/stores/ws.svelte.ts`) missing + worker WS server missing. Dashboard **has no data source**.

---

### Finding #2: Layout Missing 6-Nav Sidebar

**Issue**: Design spec (DESIGN.md §2) requires 2-column layout: left sidebar (6 nav items: Dashboard, Live, Errors, Persona, Config, Cost) + top status bar + main content.

**Current State**: Only top navbar with "Bang Hack Controller" title + version badge. **No sidebar at all**.

**Consequence**: Even if 5 other routes are created, users cannot navigate between pages via UI.

**Additional Bug**: Uses `<slot />` (Svelte 4 syntax, deprecated in Svelte 5). Should migrate to `{@render children()}` with `let { children } = $props()`. Still works now but will warn and eventually error in Svelte 6.

---

### Finding #3: Worker = Skeleton Infinite-Sleep

**Issue**: `apps/worker/src/banghack/main.py` only prints `🎙️ Bang Hack Worker v0.1.0-dev` then loops `asyncio.sleep(30)` forever. **Does not initialize anything** — all components written as `# TODO` comments.

**Additional Issue**: `__main__.py` **missing**, so command `uv run python -m banghack` in `dev.bat` will **error with `No module named banghack.__main__`**. This means `scripts\dev.bat` currently **fails at worker step**, only controller runs.

---

## ⚠️ Discrepancies (Medium Severity)

### Branch Inconsistency
- **Repo uses**: `master`
- **Notion docs likely reference**: `main`
- **Impact**: Command `git push -u origin main` will fail with `error: src refspec main does not match any`

### Repo Name Inconsistency
- **README + DOCS_HUB.md reference**: "tiklivenotion" / "bamsbung/tiklivenotion"
- **Actual URL**: "dedy45/livetik"
- **Action**: Choose one and be consistent

### Dependency Version Drift
pyproject.toml has looser lower bounds than Notion spec:
- `openai>=1.0.0` (vs ≥1.50)
- `edge-tts>=6.1.0` (vs ≥6.1.10)
- `ruff>=0.2.0` (vs ≥0.6)
- `fastapi>=0.109.0` (vs ≥0.110)

Not breaking, but risk of drift.

### Documentation Mirror Gap
6 docs exist in repo but not mirrored to Notion:
- `DOCS_HUB.md`
- `QUICKSTART.md`
- `docs/KIRO_GUIDE.md`
- `docs/GITHUB.md`
- `docs/STRUCTURE.md`
- `docs/TROUBLESHOOTING.md`

---

## 🎯 Priority Action Plan

> **Strategy**: Complete P0 first → dashboard will be live with real data (though still dummy metrics, but *flow* is end-to-end). P1 makes navigation match design. P2 adds real adapters. P3 activates KIRO steering.

### Phase P0: Dashboard Live (MANDATORY)

Without this, everything else is meaningless.

#### TASK-01: Create `apps/worker/src/banghack/__main__.py` (2 min)

**Content**:
```python
"""Module entry for `python -m banghack`."""
from .main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
```

**Verification**: `cd apps\worker && uv run python -m banghack` should print heartbeat (no module error).

---

#### TASK-02: Create `apps/worker/src/banghack/ipc/ws_server.py` (30 min)

Minimal WS server that broadcasts events to all clients.

**Content**: See implementation in original audit document section 4, TASK-02.

**Verification**: `uv run python -c "from banghack.ipc.ws_server import WSServer"` should import cleanly.

---

#### TASK-03: Wire `main.py` to init WS + emit dummy events (15 min)

Replace content of `apps/worker/src/banghack/main.py` to initialize WS server and broadcast metrics every 2 seconds.

**Content**: See implementation in original audit document section 4, TASK-03.

**Verification**: `scripts\dev.bat` → worker window should print `WS server listening on ws://127.0.0.1:8765` + broadcast log every 2 seconds.

---

#### TASK-04: Create `apps/controller/src/lib/stores/ws.svelte.ts` (30 min)

Reactive store using Svelte 5 runes + auto-reconnect.

**Content**: See implementation in original audit document section 4, TASK-04.

**Verification**: `pnpm check` should pass without TypeScript errors.

---

#### TASK-05: Refactor `+page.svelte` to subscribe to wsStore (10 min)

Replace content of `apps/controller/src/routes/+page.svelte` to consume wsStore.

**Content**: See implementation in original audit document section 4, TASK-05.

**Acceptance Criteria** (P0 Complete):
1. `scripts\dev.bat` starts both windows without error
2. Open `http://localhost:5173`
3. Within ≤5 seconds, status changes from `disconnected` → `connected`, Comments increment every 2 seconds, Uptime runs, Recent Events populate
4. Kill worker window. Within ≤3 seconds status returns to `disconnected` + metrics reset. Restart worker → auto-reconnect

**If all 4 criteria pass = dashboard is REAL, not FAKE.**

---

### Phase P1: Sidebar + Route Stubs (Match Design)

#### TASK-06: Update `+layout.svelte` add sidebar + migrate `<slot />`

Replace content of `apps/controller/src/routes/+layout.svelte`.

**Content**: See implementation in original audit document section 4, TASK-06.

**Verification**: Sidebar appears on left with 6 links, highlights active route, worker online/offline indicator at bottom.

---

#### TASK-07: Create 5 route stubs (10 min total)

Create placeholder files so navigation doesn't 404:
- `apps/controller/src/routes/live/+page.svelte`
- `apps/controller/src/routes/errors/+page.svelte`
- `apps/controller/src/routes/persona/+page.svelte`
- `apps/controller/src/routes/config/+page.svelte`
- `apps/controller/src/routes/cost/+page.svelte`

Each file content:
```svelte
<h2 class="text-2xl font-bold mb-4">[Page Name]</h2>
<div class="bg-bg-panel border border-border rounded-lg p-6 text-text-secondary">
	Coming in P2 — [brief description of planned features].
</div>
```

**Verification**: Click each sidebar nav → page loads, no 404.

---

### Phase P2: Real Adapters (After P0+P1 Green)

#### TASK-08: Build 4 adapters + 3 core modules (2-4 hours)

Files to create (from Architecture spec):
- `adapters/tiktok.py` — use `TikTokLiveClient` from package
- `adapters/llm.py` — DeepSeek primary via openai SDK + `base_url="https://api.deepseek.com"`, fallback Claude via anthropic SDK
- `adapters/tts.py` — `edge_tts.Communicate` stream to `ffplay` subprocess
- `adapters/obs.py` — write text file to `OBS_TEXT_FILE_PATH`
- `core/guardrail.py` — regex `FORBIDDEN_PATTERNS` + `SENSITIVE_TOPICS` + rate limit
- `core/queue.py` — asyncio.Queue for reply + TTS (no overlap)
- `core/persona.py` — load `config/persona.md` + format prompt

**Verification**: `uv run pytest apps/worker/tests/` — all unit tests pass (guardrail blocklist, queue dedup, persona format).

---

### Phase P3: KIRO Steering Active

#### TASK-09: Paste `.kiro/steering/*.md` (15 min)

Paste 4 files from Notion spec to `.kiro/steering/`:
- `product.md`
- `tech.md`
- `structure.md`
- `style.md`

Plus paste Spec 01-scaffold files to `.kiro/specs/01-scaffold-boot/`:
- `requirements.md`
- `design.md`
- `tasks.md`

**Verification**: KIRO IDE reads steering automatically — open KIRO chat, ask "what is the official project stack?" → answer should mention Python 3.11+/UV/Svelte 5/Tailwind v4/DeepSeek (if not mentioned, steering not loaded).

---

## 🧪 Smoke Test Procedure (3 Minutes)

Run in new terminal:

```bash
# 1. Worker startup
cd apps\worker && uv run python -m banghack
# Should print: "WS server listening on ws://127.0.0.1:8765"
# Ctrl+C to stop

# 2. WebSocket reachable (from repo root, different terminal)
npx -y wscat -c ws://127.0.0.1:8765
# Should receive hello event + metrics event every 2 seconds
# Ctrl+C to stop

# 3. Full e2e
scripts\dev.bat
# Open http://localhost:5173 → numbers move automatically
```

**If all 3 steps green = P0 phase complete, dashboard truly live.**

---

## 📈 Definition of REAL (5-Level Ladder)

| Level | Criteria | Current Status |
|-------|----------|----------------|
| **1 · Exist** | Scaffold files present in repo | ✅ 9 scaffold files |
| **2 · Compile** | `pnpm check` • `uv run ruff check` • `uv run mypy` clean | ⚠️ Not verified (likely pass for existing files) |
| **3 · Test** | `uv run pytest` • `pnpm test` pass | ❌ No tests exist |
| **4 · Integrate** | Worker ↔ Controller connected via WS, dashboard shows real data | ❌ Impossible now (WS server + store absent) |
| **5 · Observable** | Structured logging, errors visible in UI, cost tracked | ❌ No structured logging, no error route, no cost tracking |

**Targets**:
- **Post-P0 (2 hours work)**: Level 4 achieved (Integrate)
- **Post-P1 (3 hours work)**: Design match 100%
- **Post-P2+P3 (6-8 hours work)**: Level 5 observable + real adapters

---

## 💻 KIRO Execution Prompt

Paste this in KIRO IDE session:

```
@docs/DESIGN.md @.env.example @apps/worker/src/banghack/main.py @apps/controller/src/routes/+page.svelte

Real State Audit available in docs/real-state-audit.md.
Execute TASK-01 through TASK-05 (P0 phase) TODAY.

Mandatory constraints:
- Windows-first (.bat, not .sh/.ps1 — repo already uses this)
- Branch `master` not `main` for git push
- Svelte 5 runes syntax, don't use <slot />
- Tailwind v4 @theme, don't use tailwind.config.js
- UV for Python, don't use pip
- TypeScript strict, mypy strict

P0 acceptance criteria (don't mark done unless all pass):
1. `scripts\dev.bat` no error in worker window
2. `http://localhost:5173` status auto-changes disconnected → connected ≤5 seconds
3. Comments/Replies/Uptime move in real-time
4. Worker dies → UI auto-disconnect + reset; worker restarts → auto-reconnect

Report per-task with actual log output (not narrative).
```

---

## ⚠️ Common Pitfalls (Avoid During Execution)

- ❌ **DON'T** create `.sh` or `.ps1` — repo is consistent with Windows `.bat`, follow that
- ❌ **DON'T** use `import { writable } from 'svelte/store'` — this repo uses Svelte 5 runes
- ❌ **DON'T** use `tailwind.config.js` — repo uses Tailwind v4 CSS-first `@theme`
- ❌ **DON'T** `git push origin main` — default branch is `master`
- ❌ **DON'T** rename repo to `tiklivenotion` — real URL is `dedy45/livetik`, fix README instead
- ❌ **DON'T** install packages with `pip install` — always `uv add <pkg>` so `pyproject.toml` updates
- ❌ **DON'T** skip TASK-01 (`__main__.py`) — without it `python -m banghack` fails

---

## 📝 Executive Summary for Stakeholders

- Repo **exists with correct stack**, but **content is only 28%** of spec
- Dashboard you see today = **UI shell mock**, not UX bug — no data source because WS server + store not yet built
- With **5 P0 tasks (~2 hours)** dashboard will be live with real data (still dummy metrics but *flow* is end-to-end)
- Add **2 P1 tasks (~1 hour)** layout will match Design spec
- **9 total tasks** to reach real adapters + active KIRO steering

**Next Step**: Paste Prompt from §9 into KIRO IDE. Execute TASK-01 through TASK-05. Report smoke test §7 results.

---

**Document Version**: 1.0  
**Last Updated**: 2026-04-22  
**Maintained By**: Development Team  
**Related Docs**: [DOCS_HUB.md](../DOCS_HUB.md), [DESIGN.md](DESIGN.md), [ARCHITECTURE.md](ARCHITECTURE.md)
