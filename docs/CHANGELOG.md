# Changelog

All notable changes to this project will be documented in this file.  
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial repo skeleton
- Docs hub: PRD, Architecture, Design, Plan, Agent Brief

## [0.1.0] — TBD (target Week 1 end)

### Added

- `apps/worker` Python/UV baseline
  - TikTok adapter (isaackogan/TikTokLive wrapper)
  - DeepSeek LLM adapter
  - Edge-TTS adapter (id-ID-ArdiNeural)
  - OBS file bridge (last_reply.txt)
  - Core: persona loader, guardrail regex, queue rate-limit
  - IPC: WebSocket server + FastAPI REST
  - Telemetry: structured JSON logger, cost tracker
- `apps/controller` Svelte 5 + Tailwind v4
  - Dashboard (6 KPI cards)
  - Live monitor (split comment/reply feed)
  - Errors tab
  - Persona editor (Monaco)
  - Config page
  - Cost tracker
- CI GitHub Actions: uv sync + pytest + svelte-check
- Smoke test script

## [0.2.0] — TBD (target Week 2)

### Added

- Gift & Follow event → template reply
- Claude fallback kalau DeepSeek rate-limit
- Session log export JSON
- Persona hot-reload tanpa restart
- Dry-run mode untuk test tanpa broadcast

### Changed

- Upgrade queue dari FIFO → priority (gift > comment > like)

## [0.3.0] — TBD (target Week 3)

### Added

- TikFinity alerts integration via Browser Source compat
- Keyword trigger → auto OBS scene switch (via obs-websocket v5)
- Cartesia Sonic-3 TTS as opt-in (NFR target: lebih natural)

### Deprecated

- Edge-TTS sebagai default — akan tetap bisa di-toggle via `.env`

## [0.4.0] — TBD (target Month 2)

### Added

- Lumia Stream integration (smart light trigger saat gift)
- Multi-language persona support (EN fallback)
- Analytics export ke Notion database (via Notion API)

---

## Format panduan contribution

### [X.Y.Z] — YYYY-MM-DD

#### Added

- Fitur baru

#### Changed

- Perubahan behavior existing

#### Deprecated

- Akan dihapus versi berikutnya

#### Removed

- Dihapus

#### Fixed

- Bug fix

#### Security

- Vulnerability patch

---

## Commit Message Convention

Conventional Commits, scope wajib kalau ubah >1 modul:

```
feat(worker): add Claude fallback adapter
fix(controller/live): reply row not highlighting on click
chore(ci): bump uv to 0.5.4
docs(arch): revise WS protocol section
refactor(core/queue): extract priority function
test(guardrail): add Indonesia-specific regex coverage
```

Type: `feat|fix|chore|docs|refactor|test|style|perf|ci|revert`

---

[Unreleased]: https://github.com/bamsbung/tiklivenotion/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/bamsbung/tiklivenotion/releases/tag/v0.1.0
