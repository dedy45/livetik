# 🎯 WORKFLOW SEBENARNYA - livetik v0.4

**PENTING:** Ini adalah workflow AKTUAL yang berjalan, bukan teori.

---

## 🎬 LIVE SETUP ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    TIKTOK LIVE STREAM                       │
│  @interiorhack.id - Faceless Live (Visual + Voice Only)    │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │ RTMP Stream
                           │
┌─────────────────────────────────────────────────────────────┐
│                      OBS STUDIO                             │
│  - Scene: Visual produk/ruangan (looping video)            │
│  - Audio: VB-CABLE (virtual audio cable)                   │
│  - Text Overlay: last_reply.txt (file-based)               │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │
                    ┌──────┴──────┐
                    │             │
              Audio │             │ Text
            (VB-CABLE)            │ (File)
                    │             │
┌─────────────────────────────────────────────────────────────┐
│                  PYTHON WORKER                              │
│  apps/worker/src/banghack/main.py                          │
│                                                             │
│  Components:                                                │
│  1. Audio Library Manager (108 clips)                      │
│  2. Live Director (2-hour state machine)                   │
│  3. Comment Classifier (rules + LLM fallback)              │
│  4. Reply Suggester (template + LLM + cache)               │
│  5. TikTok Listener (read-only scrape)                     │
│                                                             │
│  Audio Output: sounddevice → VB-CABLE → OBS                │
│  Text Output: write to obs/last_reply.txt                  │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │ WebSocket (monitoring only)
                           │
┌─────────────────────────────────────────────────────────────┐
│              SVELTE CONTROLLER (Dashboard)                  │
│  apps/controller/ - http://localhost:5173                  │
│                                                             │
│  Purpose: MONITORING & MANUAL CONTROL                       │
│  - View live metrics (viewers, comments, cost)             │
│  - Manual approve reply suggestions                         │
│  - Emergency stop                                           │
│  - Audio library preview                                    │
│                                                             │
│  NOT FOR: Serving audio files to OBS                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔊 AUDIO FLOW (CRITICAL PATH)

```
┌─────────────────────────────────────────────────────────────┐
│  AUDIO LIBRARY (Pre-generated)                             │
│  apps/worker/static/audio_library/                         │
│                                                             │
│  - 108 .wav files (Cartesia TTS)                           │
│  - index.json (metadata)                                    │
│  - Categories: A_opening, B_reset, C_paloma, etc.          │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Load at startup
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  AUDIO LIBRARY MANAGER                                      │
│  core/audio_library/manager.py                             │
│                                                             │
│  - Load index.json                                          │
│  - Search clips by category/tag                            │
│  - Return ClipMeta (id, path, duration, script)            │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Request clip
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  LIVE DIRECTOR                                              │
│  core/orchestrator/director.py                             │
│                                                             │
│  State Machine:                                             │
│  IDLE → RUNNING → PAUSED → STOPPED                         │
│                                                             │
│  Phase-based selection:                                     │
│  - Phase: opening → Category: A_opening                    │
│  - Phase: hook → Category: B_reset                         │
│  - Phase: demo → Category: C_paloma                        │
│  - etc.                                                     │
│                                                             │
│  Pick random clip from category                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Play clip
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  AUDIO ADAPTER                                              │
│  adapters/audio_library.py                                 │
│                                                             │
│  1. Load .wav file from disk                               │
│  2. Play via sounddevice library                           │
│  3. Output to VB-CABLE (virtual audio device)              │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Virtual audio cable
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  VB-CABLE (Virtual Audio Device)                           │
│  - Acts as virtual speaker                                  │
│  - OBS captures this as audio input                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Audio input
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  OBS STUDIO                                                 │
│  - Audio Input: VB-CABLE                                    │
│  - Mix with background music (optional)                    │
│  - Stream to TikTok via RTMP                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 💬 COMMENT REPLY FLOW (OPTIONAL)

```
┌─────────────────────────────────────────────────────────────┐
│  TIKTOK LIVE COMMENT                                        │
│  "bang harga PALOMA berapa?"                                │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ TikTokLive library
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  TIKTOK LISTENER                                            │
│  adapters/tiktok.py                                         │
│                                                             │
│  - Read-only scrape (no posting)                           │
│  - Emit comment events                                      │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Comment event
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  COMMENT CLASSIFIER                                         │
│  core/classifier/rules.py + llm_fallback.py                │
│                                                             │
│  1. Rule-first (regex, keywords)                           │
│     - price_question                                        │
│     - buying_intent                                         │
│     - spam                                                  │
│     - etc.                                                  │
│                                                             │
│  2. LLM fallback (if confidence < 0.8)                     │
│     - Cost: ~20 tokens                                      │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Intent + confidence
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  REPLY SUGGESTER                                            │
│  core/orchestrator/suggester.py                            │
│                                                             │
│  1. Template first (if intent matches)                     │
│  2. Cache lookup (cosine similarity > 0.9)                 │
│  3. LLM generation (if needed)                             │
│     - Cost: ~150 tokens                                     │
│     - Via guardrail (budget check)                         │
│                                                             │
│  Output: 3 reply options                                    │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Broadcast to dashboard
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  SVELTE DASHBOARD                                           │
│  ReplySuggestions.svelte                                   │
│                                                             │
│  Human operator:                                            │
│  - Review 3 options                                         │
│  - Click "Approve" (or press 1/2/3)                        │
│  - Or "Reject" / "Regen"                                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Approve command
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  TTS ADAPTER                                                │
│  adapters/tts.py                                            │
│                                                             │
│  1. Generate voice (Cartesia or Edge-TTS)                  │
│  2. Play via sounddevice → VB-CABLE                        │
│  3. Write text to obs/last_reply.txt                       │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Audio + Text
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  OBS STUDIO                                                 │
│  - Audio: VB-CABLE (reply voice)                           │
│  - Text Overlay: last_reply.txt (reply text)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 STATIC FOLDER PURPOSE

### `apps/worker/static/audio_library/`

**Purpose:** Pre-generated audio clips storage

**Contents:**
```
static/audio_library/
├── A_opening_001.wav
├── A_opening_002.wav
├── ...
├── Z_closing_005.wav
└── index.json
```

**Access Method:**
- ✅ **Direct file system access** (worker reads from disk)
- ❌ **NOT via HTTP** (no need - worker is local)
- ❌ **NOT via browser** (dashboard doesn't play audio)

**Why NOT HTTP?**
1. Worker and audio files are on SAME machine
2. sounddevice plays directly from file path
3. No network latency
4. No CORS issues
5. Simpler architecture

**Dashboard Role:**
- Display clip metadata (from WebSocket)
- Show "now playing" indicator
- Send play/stop commands
- NOT play audio itself (OBS does that)

---

## 🎛️ DASHBOARD PURPOSE (CLARIFIED)

### What Dashboard DOES:

1. **Monitor** live metrics
   - Viewers, comments, replies
   - Cost tracking
   - System health

2. **Control** worker
   - Start/stop live session
   - Pause/resume
   - Emergency stop

3. **Approve** replies
   - View 3 suggestions
   - Click to approve
   - Reject or regenerate

4. **Preview** audio library
   - See 108 clips metadata
   - Click to trigger playback (on worker)
   - NOT play in browser

### What Dashboard DOES NOT:

1. ❌ Play audio files in browser
2. ❌ Serve static files to OBS
3. ❌ Generate TTS in real-time
4. ❌ Connect to TikTok directly
5. ❌ Stream to OBS

**Dashboard = Control Center, NOT Audio Player**

---

## 🔄 COMPLETE LIVE SESSION FLOW

```
1. PREPARATION (Before Live)
   ├─ Generate 108 audio clips (scripts/gen_audio_library.bat)
   ├─ Setup OBS scenes (visual loops)
   ├─ Configure VB-CABLE as audio input in OBS
   └─ Test audio playback (worker → VB-CABLE → OBS)

2. START SERVICES
   ├─ Terminal 1: Start Worker (uv run python -m banghack)
   │  └─ Load audio library (108 clips)
   │  └─ Start WebSocket server (port 8765)
   │  └─ Start HTTP server (port 8766)
   │  └─ Connect to TikTok Live (if username set)
   │
   └─ Terminal 2: Start Controller (pnpm dev)
      └─ Open http://localhost:5173
      └─ Connect to worker via WebSocket

3. GO LIVE ON TIKTOK
   ├─ OBS: Start streaming to TikTok
   ├─ Dashboard: Click "▶ Start Live"
   └─ Worker: Begin 2-hour session
      ├─ Phase 0: opening (180s) → Play A_opening clips
      ├─ Phase 1: hook (240s) → Play B_reset clips
      ├─ Phase 2: demo (300s) → Play C_paloma clips
      └─ ... (8 phases total)

4. DURING LIVE (2 hours)
   ├─ Audio: Worker plays clips → VB-CABLE → OBS → TikTok
   ├─ Comments: TikTok → Worker → Classify → Suggest → Dashboard
   ├─ Replies: Dashboard approve → Worker TTS → VB-CABLE → OBS
   └─ Monitoring: Dashboard shows metrics in real-time

5. END LIVE
   ├─ Auto-stop at 120 minutes (hard limit)
   ├─ Or manual stop via dashboard
   └─ Worker logs session data
```

---

## 🚨 CRITICAL MISUNDERSTANDINGS CORRECTED

### ❌ WRONG: "Dashboard harus serve static files"

**✅ CORRECT:**
- Static files are for WORKER, not dashboard
- Worker reads from local file system
- No HTTP serving needed
- Dashboard only shows metadata

### ❌ WRONG: "Audio harus bisa diplay di browser"

**✅ CORRECT:**
- Audio plays on WORKER machine (sounddevice)
- Output to VB-CABLE (virtual audio device)
- OBS captures VB-CABLE as input
- Browser dashboard only sends play commands

### ❌ WRONG: "Dashboard kosong = bug"

**✅ CORRECT:**
- Dashboard shows LIVE data from worker
- If worker offline → dashboard shows defaults (empty)
- This is EXPECTED behavior
- Start worker → dashboard populates

### ❌ WRONG: "LLM harus pilih audio"

**✅ CORRECT:**
- LLM NOT used for audio selection
- Phase-based deterministic selection
- Cost: Rp 0 per clip
- LLM only for dynamic replies (optional)

---

## 📊 COST BREAKDOWN (2-Hour Session)

```
Audio Playback (108 clips, ~500 plays):
├─ Pre-generation: Rp 15 (one-time)
├─ Playback: Rp 0 (local files)
└─ Total: Rp 0 per session

Comment Classification (100 comments):
├─ Rule-based: 80 comments × Rp 0 = Rp 0
├─ LLM fallback: 20 comments × Rp 0.03 = Rp 0.60
└─ Total: ~Rp 1

Reply Suggestions (20 replies):
├─ Template: 10 replies × Rp 0 = Rp 0
├─ Cache: 5 replies × Rp 0 = Rp 0
├─ LLM: 5 replies × Rp 2 = Rp 10
└─ Total: ~Rp 10

Dynamic TTS (if REPLY_ENABLED):
├─ Cartesia: 20 replies × 15s × Rp 0.00001/s = Rp 0.003
└─ Total: ~Rp 0.003

GRAND TOTAL: ~Rp 11 per 2-hour session
```

**Budget: Rp 50,000/day = ~4,500 sessions**

---

## ✅ SYSTEM READY CHECKLIST

### Pre-flight
- [ ] Audio library generated (108 clips)
- [ ] VB-CABLE installed and configured
- [ ] OBS scenes setup with visual loops
- [ ] OBS audio input = VB-CABLE
- [ ] Worker .env configured

### Runtime
- [ ] Worker running (port 8765 + 8766)
- [ ] Controller running (port 5173)
- [ ] Dashboard shows "idle" status (not "disconnected")
- [ ] Health check: audio_ready = true, clip_count = 108
- [ ] Test audio: Click clip in dashboard → hear in OBS

### Go-Live
- [ ] OBS streaming to TikTok
- [ ] Dashboard: Click "▶ Start Live"
- [ ] Audio plays continuously
- [ ] Phase transitions automatically
- [ ] Emergency stop button ready

---

## 🎯 BOTTOM LINE

**Workflow Sebenarnya:**
1. Worker plays audio files → VB-CABLE → OBS → TikTok
2. Dashboard monitors & controls (NOT plays audio)
3. Static files accessed via file system (NOT HTTP)
4. LLM for replies only (NOT audio selection)
5. Cost: ~Rp 11 per 2-hour session

**Tidak Ada Bug:**
- Dashboard kosong = worker offline (expected)
- Static files tidak di-serve HTTP (not needed)
- LLM tidak pilih audio (by design)

**Sistem Siap:**
- 85% complete (code done)
- 1 blocker: Generate audio library (8-12 min)
- After generation: 100% ready for live test
