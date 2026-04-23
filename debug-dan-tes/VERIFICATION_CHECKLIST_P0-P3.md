# Verification Checklist P0-P3.7

## Status Legend
- ✅ = Verified & Working
- ⚠️ = Exists but needs testing
- ❌ = Missing or broken
- 🔄 = In progress

---

## P0 · Audio Library (CC-LIVE-CLIP-001..005)

### P0.1 - Setup deps + env vars [CC-LIVE-CLIP-001]
- [ ] 1.1 Dependencies in pyproject.toml: `pyyaml>=6.0.1`, `rapidfuzz>=3.9.0`, `aiofiles>=24.1.0`
- [ ] 1.2 Env vars in `.env.example`: `AUDIO_LIBRARY_DIR`, `CLIPS_SCRIPT_YAML`, `PRODUCTS_YAML`, `REPLY_TEMPLATES_YAML`, `LIVE_MAX_DURATION_S=7200`, `REPLY_CACHE_TTL_S=300`, `REPLY_CACHE_SIMILARITY=0.90`, `CLASSIFIER_LLM_THRESHOLD=0.80`
- [ ] 1.3 File exists: `apps/worker/src/banghack/core/audio_library/__init__.py`
- [ ] 1.4 File exists: `apps/worker/src/banghack/core/classifier/__init__.py`
- [ ] 1.5 File exists: `apps/worker/src/banghack/core/orchestrator/__init__.py`

### P0.2 - Audio Library Manager + Adapter [CC-LIVE-CLIP-002]
- [ ] 2.1 File exists: `apps/worker/config/clips_script.yaml` with 160 entries
- [ ] 2.2 File exists: `apps/worker/src/banghack/core/audio_library/manager.py` with `AudioLibraryManager` class
- [ ] 2.3 File exists: `apps/worker/static/audio_library/index.json`
- [ ] 2.4 File exists: `apps/worker/src/banghack/adapters/audio_library.py` with `AudioLibraryAdapter`

### P0.3 - Generator script + bat [CC-LIVE-CLIP-003]
- [ ] 3.1 File exists: `apps/worker/scripts/gen_audio_library.py`
- [ ] 3.2 File exists: `apps/worker/scripts/gen_audio_library.bat`
- [ ] 3.3 Generated audio files: At least 10 sample `.wav` files in `static/audio_library/`

### P0.4 - WS commands + Svelte AudioLibraryGrid [CC-LIVE-CLIP-004]
- [ ] 4.1 WS commands in `main.py`: `audio.list`, `audio.play`, `audio.stop`
- [ ] 4.2 AudioLibraryManager and AudioLibraryAdapter initialized in `main()`
- [ ] 4.3 File exists: `apps/controller/src/lib/stores/audio_library.ts`
- [ ] 4.4 File exists: `apps/controller/src/lib/components/AudioLibraryGrid.svelte`

### P0.5 - Tests + P0 acceptance [CC-LIVE-CLIP-005]
- [ ] 5.1 File exists: `apps/worker/tests/test_audio_library.py`
- [ ] 5.2 Test passes: `uv run pytest apps/worker/tests/test_audio_library.py`
- [ ] 5.3 index.json has fields: `id`, `file`, `hash`, `category`, `text`
- [ ] 5.4 Dashboard loads clips via `audio.list`, click play → audio <200ms
- [ ] 5.5 0 LLM calls during audio playback (check metrics)
- [ ] 5.6 Commits exist with proper messages

---

## P1 · Comment Classifier (CC-LIVE-CLASSIFIER-001..004)

### P1.1 - Rules classifier + config [CC-LIVE-CLASSIFIER-001]
- [ ] 6.1 File exists: `apps/worker/config/reply_templates.yaml` with 7+ intents
- [ ] 6.2 File exists: `apps/worker/src/banghack/core/classifier/rules.py` with `IntentResult` and `classify()`
- [ ] 6.3 File exists: `apps/worker/tests/test_classifier_rules.py` with 7+ test cases
- [ ] 6.4 Test passes: `uv run pytest apps/worker/tests/test_classifier_rules.py`

### P1.2 - LLM fallback + integration [CC-LIVE-CLASSIFIER-002]
- [ ] 7.1 File exists: `apps/worker/src/banghack/core/classifier/llm_fallback.py`
- [ ] 7.2 `handle_comment()` function in `main.py` with classifier integration

### P1.3 - DecisionStream Svelte [CC-LIVE-CLASSIFIER-003]
- [ ] 8.1 File exists: `apps/controller/src/lib/components/DecisionStream.svelte`
- [ ] 8.2 DecisionStream integrated in `apps/controller/src/routes/+page.svelte`
- [ ] 8.3 Acceptance: ≥80% comments classified rule-only, badges show real-time
- [ ] 8.4 Commits exist with proper messages

---

## P2 · Suggested Reply (CC-LIVE-ORCH-001..005)

### P2.1 - Budget Guard [CC-LIVE-ORCH-001]
- [ ] 9.1 File exists: `apps/worker/src/banghack/core/orchestrator/budget_guard.py` with `BudgetGuard` class
- [ ] 9.2 BudgetGuard wired to CostTracker in `main.py`

### P2.2 - Reply Cache + test [CC-LIVE-ORCH-002]
- [ ] 10.1 File exists: `apps/worker/src/banghack/core/orchestrator/reply_cache.py` with `ReplyCache` class
- [ ] 10.2 File exists: `apps/worker/tests/test_reply_cache.py`
- [ ] 10.3 Test passes: `uv run pytest apps/worker/tests/test_reply_cache.py`

### P2.3 - Suggester + reply_templates [CC-LIVE-ORCH-003]
- [ ] 11.1 File exists: `apps/worker/src/banghack/core/orchestrator/suggester.py` with `Suggester` class
- [ ] 11.2 Suggester initialized in `main()` and called from `handle_comment()`

### P2.4 - WS reply.* + ReplySuggestions [CC-LIVE-ORCH-004]
- [ ] 12.1 WS commands in `main.py`: `reply.approve`, `reply.reject`, `reply.regen`, `budget.get`
- [ ] 12.2 File exists: `apps/controller/src/lib/components/ReplySuggestions.svelte`

### P2.5 - Output guardrail + test [CC-LIVE-ORCH-005]
- [ ] 13.1 File exists: `apps/worker/tests/test_suggester.py` with `_safe()` regex tests
- [ ] 13.2 Test passes: `uv run pytest apps/worker/tests/test_suggester.py`
- [ ] 13.3 Acceptance: suggestion <2s, cache hit ≥30%, REPLY_ENABLED=false works
- [ ] 13.4 Commits exist with proper messages

---

## P3 · Live Director (CC-LIVE-DIRECTOR-001..005)

### P3.1 - products.yaml + Director state machine [CC-LIVE-DIRECTOR-001]
- [ ] 14.1 File exists: `apps/worker/config/products.yaml` with runsheet phases
- [ ] 14.2 File exists: `apps/worker/src/banghack/core/orchestrator/director.py` with `LiveDirector` class

### P3.2 - Runsheet loop + anti-repeat [CC-LIVE-DIRECTOR-002]
- [ ] 15.1 `_run_loop()` implemented in LiveDirector with phase iteration
- [ ] 15.2 Broadcasts `live.state` on phase change
- [ ] 15.3 Broadcasts `live.tick` every 30 seconds

### P3.3 - WS live.* + live_state store [CC-LIVE-DIRECTOR-003]
- [ ] 16.1 WS commands in `main.py`: `live.start`, `live.pause`, `live.resume`, `live.stop`, `live.emergency_stop`, `live.get_state`
- [ ] 16.2 LiveDirector initialized in `main()` with references
- [ ] 16.3 File exists: `apps/controller/src/lib/stores/live_state.ts`
- [ ] 16.4 wsStore handles `live.state` and `live.tick` events

### P3.4 - TwoHourTimer + EmergencyStop [CC-LIVE-DIRECTOR-004]
- [ ] 17.1 File exists: `apps/controller/src/lib/components/TwoHourTimer.svelte`
- [ ] 17.2 File exists: `apps/controller/src/lib/components/EmergencyStop.svelte`
- [ ] 17.3 Components integrated in `apps/controller/src/routes/+page.svelte`

### P3.5 - Tests + P3 acceptance [CC-LIVE-DIRECTOR-005]
- [ ] 18.1 File exists: `apps/worker/tests/test_director_state.py`
- [ ] 18.2 Test passes: `uv run pytest apps/worker/tests/test_director_state.py`
- [ ] 18.3 Acceptance: `live.start` → timer runs, phases auto-advance, anti-repeat works
- [ ] 18.4 Integration dry-run: 30 min test with `max_duration_s=1800`, `DRY_RUN=true`
- [ ] 18.5 Commits exist with proper messages

---

## P3.6 - Health Check Extension [Task 19]

### Health Check Updates
- [ ] 19.1 `/health` endpoint updated with: `audio_library_ready`, `classifier_ready`, `director_ready`, `budget_remaining_idr`, `worker_version: "0.4.0"`
- [ ] 19.2 HTTP 503 returned when critical component not ready

---

## P3.7 - Documentation Updates [Task 19]

### Documentation
- [ ] 19.3 `docs/CHANGELOG.md` updated with v0.4.0 section
- [ ] 19.4 `docs/ARCHITECTURE.md` updated with v0.4 components
- [ ] 19.5 Final commit: `[v0.4] update CHANGELOG → v0.4.0 shipped`

---

## Integration Tests

### End-to-End Verification
- [ ] Worker starts without errors
- [ ] Controller connects to worker via WebSocket
- [ ] Audio library loads and displays in dashboard
- [ ] Comment classifier works with test comments
- [ ] Reply suggester generates suggestions
- [ ] Live director can start/stop/pause/resume
- [ ] Emergency stop works correctly
- [ ] All WS commands respond correctly
- [ ] Health check returns 200 with all components ready

---

## Performance Checks

### Token Saving & Cost
- [ ] Rule-first classifier: ≥80% comments classified without LLM
- [ ] Reply cache: ≥30% cache hit rate after 50 comments
- [ ] Budget guard: Blocks LLM calls when budget exceeded
- [ ] Audio playback: <200ms latency
- [ ] Reply suggestions: <2s latency

---

## Notes
- All tests must pass before marking as ✅
- Integration tests should be run with real TikTok Live connection (or mock)
- Performance metrics should be measured during 30-minute dry-run
