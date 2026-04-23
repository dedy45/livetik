# Debug & Test Suite - P0-P3 Verification

Comprehensive testing suite untuk verifikasi acceptance criteria P0-P3.7 sebelum production deployment.

## 📁 Files Overview

| File | Purpose | Status |
|------|---------|--------|
| `01_DEEP_ANALYSIS.md` | Root cause analysis & bug investigation | ✅ Complete |
| `02_inject_fake_comments.py` | Comment injection for classifier testing | ✅ Ready |
| `03_run_integration_test.py` | 30-minute full integration test | ✅ Ready |
| `04_test_emergency_stop.py` | Emergency stop latency verification | ✅ Ready |
| `05_test_anti_repeat.py` | Anti-repeat 20-minute window test | ✅ Ready |

## 🚀 Quick Start

### Prerequisites

1. **Worker must be running:**
   ```bash
   cd livetik/apps/worker
   uv run python -m banghack.main
   ```

2. **Generate audio files (if not done):**
   ```bash
   cd livetik/apps/worker
   uv run python scripts/gen_audio_library.py --category A_opening --limit 10
   ```

3. **Verify worker health:**
   ```bash
   curl http://localhost:8766/health
   ```

### Running Tests

#### 1. Comment Injection Test (5 minutes)

Test classifier and suggester with fake comments:

```bash
cd livetik
python debug-dan-tes/02_inject_fake_comments.py --count 50 --interval 5
```

**Expected output:**
- Comments classified with intent badges
- Suggestions generated <2s
- Rule-based classification ≥80%

---

#### 2. Emergency Stop Latency Test (2 minutes)

Verify emergency stop <500ms requirement:

```bash
cd livetik
python debug-dan-tes/04_test_emergency_stop.py --iterations 10
```

**Expected output:**
- All 10 iterations <500ms
- Pass rate: 100%
- Report saved to `emergency_stop_latency_report.json`

**Acceptance criteria:** ✅ PASS if avg latency <500ms

---

#### 3. Anti-Repeat Window Test (30 minutes)

Verify clips don't repeat within 20-minute window:

```bash
cd livetik
python debug-dan-tes/05_test_anti_repeat.py --duration 1800 --window 1200
```

**Expected output:**
- No violations (clips repeating <20 min)
- Clip frequency distribution
- Report saved to `anti_repeat_report.json`

**Acceptance criteria:** ✅ PASS if 0 violations

---

#### 4. Full Integration Test (30 minutes)

Complete end-to-end test with all components:

```bash
cd livetik
python debug-dan-tes/03_run_integration_test.py --duration 1800
```

**What it tests:**
- ✅ Timer runs for full duration
- ✅ Opening clip auto-plays
- ✅ Phases auto-advance
- ✅ Comment classification
- ✅ Reply suggestions
- ✅ Emergency stop at 15 min
- ✅ Budget tracking
- ✅ Error handling

**Expected output:**
- All phases executed
- Multiple clips played
- Comments classified
- Suggestions generated
- Emergency stop <500ms
- Report saved to `integration_test_report_YYYYMMDD_HHMMSS.json`

**Acceptance criteria:** ✅ PASS if all checks green

---

## 📊 Test Reports

All tests generate JSON reports in `debug-dan-tes/` folder:

- `emergency_stop_latency_report.json` - Emergency stop metrics
- `anti_repeat_report.json` - Anti-repeat violations
- `integration_test_report_*.json` - Full integration test results

## 🐛 Troubleshooting

### Worker not responding

```bash
# Check if worker is running
curl http://localhost:8766/health

# Check WebSocket connection
wscat -c ws://localhost:8765
```

### No audio files

```bash
cd livetik/apps/worker
uv run python scripts/gen_audio_library.py --category A_opening --limit 10
ls -la static/audio_library/*.wav
```

### Emergency stop fails

Check `01_DEEP_ANALYSIS.md` for root cause analysis. The fix has been applied to `adapters/audio_library.py`.

### Tests timeout

Increase timeout in test scripts:
```python
response = await asyncio.wait_for(ws.recv(), timeout=10.0)  # Increase from 5.0
```

## ✅ Acceptance Criteria Checklist

Run this checklist before declaring P0-P3 complete:

### P0 - Audio Library
- [ ] 160+ clips indexed in `static/audio_library/index.json`
- [ ] Click clip in dashboard → audio plays <200ms
- [ ] Hot-reload works (5s polling)
- [ ] WS commands work: `audio.list`, `audio.play`, `audio.stop`

### P1 - Comment Classifier
- [ ] 7 intents classified: greeting, price, stock, buying, compatibility, how_to_use, objection
- [ ] Rule-based classification ≥80%
- [ ] LLM fallback works when confidence <0.8
- [ ] Badge appears in Live Comments feed

### P2 - Suggested Reply
- [ ] 3 reply options generated <2s
- [ ] Template-first approach works
- [ ] LLM fallback via guardrail
- [ ] Cache hit rate ≥30%
- [ ] Human-in-the-loop (operator picks)

### P3 - Live Director
- [ ] `live.start` → timer runs
- [ ] Opening clip auto-plays
- [ ] Phases auto-advance
- [ ] OBS scene switch (manual workflow documented)
- [ ] Anti-repeat 20 min (0 violations)
- [ ] Emergency stop <500ms
- [ ] Hard-stop at max_duration (2 hours)
- [ ] Unit tests pass

## 🔧 Configuration

### Test Duration

Adjust test duration in scripts:

```bash
# 10-minute quick test
python debug-dan-tes/03_run_integration_test.py --duration 600

# Full 2-hour test
python debug-dan-tes/03_run_integration_test.py --duration 7200
```

### Comment Injection Rate

```bash
# Slow (every 10s)
python debug-dan-tes/02_inject_fake_comments.py --interval 10

# Fast (every 2s)
python debug-dan-tes/02_inject_fake_comments.py --interval 2

# Burst mode (stress test)
python debug-dan-tes/02_inject_fake_comments.py --burst 50
```

## 📝 Next Steps

After all tests pass:

1. ✅ Review all test reports
2. ✅ Document OBS manual workflow
3. ✅ Update `docs/CHANGELOG.md`
4. ✅ Commit with message: `[v0.4][P0-P3] All acceptance criteria verified`
5. ✅ Run production dry-run (2 hours)
6. ✅ Deploy to production

## 🎯 Success Criteria

**P0-P3 is COMPLETE when:**
- ✅ All 4 test scripts pass
- ✅ Emergency stop <500ms (100% pass rate)
- ✅ Anti-repeat 0 violations
- ✅ 30-minute integration test green
- ✅ Unit tests pass
- ✅ Documentation updated

---

**Last Updated:** 2026-04-24  
**Status:** 🟢 READY FOR TESTING
