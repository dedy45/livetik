# 🔍 DEBUGGING CHECKLIST - livetik GO-LIVE

**Purpose:** Systematic debugging guide untuk troubleshooting sebelum dan saat live test.

---

## 🚨 PRE-FLIGHT CHECKS (WAJIB SEBELUM START)

### 1. Environment Variables
```bash
# Check .env exists
type .env

# Verify critical keys
findstr "CARTESIA_API_KEYS" .env
findstr "CARTESIA_VOICE_ID" .env
findstr "TIKTOK_USERNAME" .env
findstr "DRY_RUN" .env
findstr "REPLY_ENABLED" .env
```

**Expected:**
- `CARTESIA_API_KEYS` = sk_car_... (at least 1 key)
- `CARTESIA_VOICE_ID` = UUID format
- `TIKTOK_USERNAME` = username tanpa @
- `DRY_RUN` = true (untuk test pertama)
- `REPLY_ENABLED` = false (untuk test pertama)

### 2. Audio Library Status
```bash
# Check index.json
type apps\worker\static\audio_library\index.json

# Count clips in index
# Should NOT be: {"version":"1.0","clips":[]}
# Should be: {"version":"1.0","clips":[{...}, {...}, ...]}

# Count .wav files
dir apps\worker\static\audio_library\*.wav /s /b | find /c /v ""
# Expected: 108
```

**If clips = 0:**
```bash
# Generate audio library
scripts\gen_audio_library.bat
# Wait 8-12 minutes
```

### 3. Python Environment
```bash
# Check uv installed
where uv

# Check Python version
uv run python --version
# Expected: Python 3.11+

# Sync dependencies
cd apps\worker
uv sync
```

### 4. Node.js Environment
```bash
# Check pnpm installed
where pnpm

# Check Node version
node --version
# Expected: v18+

# Install dependencies
cd apps\controller
pnpm install
```

---

## 🔧 WORKER DEBUGGING

### Start Worker
```bash
cd apps\worker
uv run python -m banghack
```

### Expected Output (Good)
```
🎙️ Bang Hack Worker v0.3.0-dev (P2-C) starting
REPLY_ENABLED=False DRY_RUN=True
[INFO] AudioLibraryManager loaded 108 clips
[INFO] Classifier ready (rules + llm_fallback)
[INFO] Suggester ready
[INFO] Director ready (runsheet 3 products, 8 phases, 3000s)
[INFO] WS server on ws://localhost:8765
[INFO] HTTP server on http://localhost:8766
[INFO] TikTok listener: DRY_RUN=true, REPLY_ENABLED=false
```

### Common Errors & Fixes

#### Error: "CARTESIA_API_KEYS not set"
**Fix:**
```bash
# Edit .env and add:
CARTESIA_API_KEYS=sk_car_your_key_here
```

#### Error: "AudioLibraryManager loaded 0 clips"
**Fix:**
```bash
# Generate audio library
scripts\gen_audio_library.bat
```

#### Error: "TikTokLive import error"
**Fix:**
```bash
cd apps\worker
uv sync
# Verify TikTokLive installed:
uv run python -c "import TikTokLive; print(TikTokLive.__version__)"
```

#### Error: "Port 8765 already in use"
**Fix:**
```bash
# Find and kill process using port 8765
netstat -ano | findstr :8765
taskkill /PID <PID> /F
```

---

## 🖥️ CONTROLLER DEBUGGING

### Start Controller
```bash
cd apps\controller
pnpm dev
```

### Expected Output (Good)
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### Open Browser
```
http://localhost:5173
```

### Expected UI (Good)
- Dashboard loads without crash
- Status shows "Idle (worker ready, TikTok belum connect)"
- Green dot or yellow dot (not red)
- System Health probes visible
- No console errors in DevTools

### Common Errors & Fixes

#### Error: "Failed to resolve import"
**Symptom:** Browser console shows module not found

**Fix:**
```bash
cd apps\controller
# Clear cache and reinstall
rm -rf node_modules .svelte-kit
pnpm install
pnpm dev
```

#### Error: "WebSocket connection failed"
**Symptom:** Dashboard shows "disconnected" status

**Fix:**
1. Check worker is running (Terminal 1)
2. Check port 8765 is open:
```bash
curl ws://localhost:8765
# Should NOT return "connection refused"
```

#### Error: "Cannot GET /"
**Symptom:** Browser shows 404

**Fix:**
```bash
# Ensure you're accessing correct URL
# http://localhost:5173 (NOT 5174, NOT 3000)
```

---

## 🏥 HEALTH CHECK COMMANDS

### Worker Health
```bash
# HTTP health endpoint
curl http://localhost:8766/health

# Expected JSON:
{
  "status": "ok",
  "audio_ready": true,
  "audio_library_clip_count": 108,
  "classifier_ready": true,
  "director_ready": true,
  "budget_remaining_idr": 50000
}
```

### Critical Health Flags
- `audio_ready: false` → Audio library not loaded
- `clip_count: 0` → index.json empty
- `classifier_ready: false` → Rules not loaded
- `director_ready: false` → Runsheet not loaded

### Test Individual Components
```bash
# Test ffplay (audio playback)
curl -X POST http://localhost:8766/cmd \
  -H "Content-Type: application/json" \
  -d '{"type":"cmd","name":"test_ffplay","req_id":"test1","params":{}}'

# Test Cartesia key
curl -X POST http://localhost:8766/cmd \
  -H "Content-Type: application/json" \
  -d '{"type":"cmd","name":"test_cartesia_all","req_id":"test2","params":{}}'

# Test LLM
curl -X POST http://localhost:8766/cmd \
  -H "Content-Type: application/json" \
  -d '{"type":"cmd","name":"test_llm","req_id":"test3","params":{}}'
```

---

## 🎬 LIVE SESSION DEBUGGING

### Start Live Session
**Via Controller UI:**
1. Open http://localhost:5173
2. Click "▶ Start Live" button in TwoHourTimer panel

**Via WebSocket (manual):**
```javascript
// Open browser DevTools console at http://localhost:5173
wsStore.sendCommand('live.start', {})
```

### Expected Behavior (Good)
1. Timer starts counting down from 2:00:00
2. Mode changes to "RUNNING"
3. Audio plays from speaker (first clip from A_opening category)
4. Phase shows "opening" or similar
5. Product shows "PALOMA" or first product
6. Worker terminal shows:
```
[INFO] Director starting session (max 7200s, 8 phases)
[INFO] Phase 0: opening (180s) → category A_opening
[INFO] Playing A_opening_003 (14.2s)
```

### Common Issues During Live

#### Issue: No Audio Playing
**Symptoms:**
- Timer running but silent
- Worker shows "Playing X" but no sound

**Debug:**
```bash
# Check audio devices
curl -X POST http://localhost:8766/cmd \
  -H "Content-Type: application/json" \
  -d '{"type":"cmd","name":"list_audio_devices","req_id":"test4","params":{}}'

# Test audio output
curl -X POST http://localhost:8766/cmd \
  -H "Content-Type: application/json" \
  -d '{"type":"cmd","name":"test_tts_voice_out","req_id":"test5","params":{"text":"Test audio"}}'
```

**Fix:**
1. Check speaker volume (not muted)
2. Check Windows sound settings (default output device)
3. Restart worker

#### Issue: Timer Not Moving
**Symptoms:**
- Timer stuck at 2:00:00
- Mode shows "RUNNING" but elapsed_s = 0

**Debug:**
```bash
# Check live state
curl http://localhost:8766/api/live/state
```

**Fix:**
1. Stop and restart live session
2. Check worker logs for errors
3. Emergency stop and restart worker

#### Issue: Phase Not Changing
**Symptoms:**
- Stuck in "opening" phase for > 3 minutes
- Same audio clips repeating

**Debug:**
Check worker terminal for:
```
[INFO] Phase 0: opening (180s) → category A_opening
[INFO] Phase 1: hook (240s) → category B_reset
```

**Fix:**
1. Check runsheet in `config/products.yaml`
2. Verify phase durations are reasonable
3. Restart live session

#### Issue: Budget Exceeded
**Symptoms:**
- LLM calls stop working
- Dashboard shows "OVER BUDGET"

**Debug:**
```bash
curl http://localhost:8766/api/cost
```

**Fix:**
```bash
# Increase budget in .env
BUDGET_IDR_DAILY=100000

# Or reset cost (dev only)
curl -X POST http://localhost:8766/cmd \
  -H "Content-Type: application/json" \
  -d '{"type":"cmd","name":"reset_cost_today","req_id":"test6","params":{"confirm":true}}'
```

---

## 🚨 EMERGENCY PROCEDURES

### Emergency Stop Live
**Via UI:**
1. Click "🚨 EMERGENCY STOP" button
2. Confirm in modal

**Via Command:**
```javascript
// Browser console
wsStore.sendCommand('live.emergency_stop', {operator_id: 'operator'})
```

### Kill All Processes
```bash
# Kill worker
taskkill /F /IM python.exe

# Kill controller
taskkill /F /IM node.exe

# Or just Ctrl+C in each terminal
```

### Reset Everything
```bash
# 1. Stop all processes (Ctrl+C)

# 2. Clear logs
del apps\worker\logs\*.log

# 3. Reset state
del .state.json

# 4. Restart worker
cd apps\worker
uv run python -m banghack

# 5. Restart controller
cd apps\controller
pnpm dev
```

---

## 📊 LOG ANALYSIS

### Worker Logs
```bash
# View latest log
type apps\worker\logs\banghack.log | more

# Search for errors
findstr /I "ERROR" apps\worker\logs\banghack.log

# Search for warnings
findstr /I "WARN" apps\worker\logs\banghack.log
```

### Common Log Patterns

**Good:**
```
[INFO] AudioLibraryManager loaded 108 clips
[INFO] Playing A_opening_003 (14.2s)
[INFO] Phase 1: hook (240s)
```

**Bad:**
```
[ERROR] TTS error: Connection timeout
[ERROR] LLM all tiers failed
[ERROR] Audio playback failed: device not found
[WARN] BUDGET EXCEEDED (Rp 50000)
```

---

## 🎯 ACCEPTANCE CRITERIA CHECKLIST

### Before Starting Live Test
- [ ] Audio library has 108 clips
- [ ] Worker starts without errors
- [ ] Controller loads without crash
- [ ] `/health` returns `audio_ready: true`
- [ ] `/library` shows 108 clips grid
- [ ] Click 1 clip → audio plays

### During 15-Minute Test
- [ ] Audio plays continuously (max 5s gap)
- [ ] Phase transitions automatically
- [ ] Timer counts down correctly
- [ ] No ERROR in worker logs
- [ ] No crash in controller
- [ ] Emergency stop works

### After Test
- [ ] Review worker logs (no critical errors)
- [ ] Check cost (should be < Rp 100)
- [ ] Verify no memory leaks
- [ ] Confirm all processes stopped cleanly

---

## 📞 TROUBLESHOOTING DECISION TREE

```
Problem: System won't start
├─ Worker won't start
│  ├─ Check Python/uv installed
│  ├─ Check .env exists
│  └─ Check port 8765 free
├─ Controller won't start
│  ├─ Check Node/pnpm installed
│  ├─ Check port 5173 free
│  └─ Run pnpm install
└─ Both start but can't connect
   ├─ Check firewall
   ├─ Check localhost resolution
   └─ Restart both services

Problem: No audio during live
├─ Check audio library (108 clips?)
├─ Check speaker volume
├─ Check Windows audio device
├─ Test with test_tts_voice_out
└─ Check worker logs for playback errors

Problem: Live session stuck
├─ Check timer moving?
│  ├─ Yes → Check phase transitions
│  └─ No → Restart live session
├─ Check worker logs
└─ Emergency stop and restart

Problem: Budget exceeded
├─ Check current cost
├─ Increase BUDGET_IDR_DAILY
├─ Or reset cost (dev only)
└─ Disable LLM calls (DRY_RUN=true)
```

---

**REMEMBER:** Untuk test pertama, gunakan:
- `DRY_RUN=true` (no real TikTok, no real LLM calls)
- `REPLY_ENABLED=false` (no TTS replies, only audio library)
- `LIVE_MAX_DURATION_S=900` (15 menit, bukan 2 jam)

Incremental testing: 15 min → 30 min → 1 hour → 2 hours
