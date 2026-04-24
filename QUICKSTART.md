# 🚀 QUICKSTART — livetik v0.4.6

> **Panduan cepat untuk menjalankan sistem dalam 15 menit.**  
> Untuk detail lengkap, baca [`WORKFLOW_ACTUAL.md`](WORKFLOW_ACTUAL.md)

---

## ⚡ TL;DR (Windows)

```bash
# 1. Install dependencies
cd apps/worker && uv sync && cd ../..
cd apps/controller && pnpm install && cd ../..

# 2. Setup config
cp .env.example .env
# Edit .env: set TIKTOK_USERNAME, API keys (optional)

# 3. Generate audio library (WAJIB, 8-12 menit)
scripts\gen_audio_library_edgets.bat

# 4. Setup VB-CABLE di OBS
# Install VB-CABLE → OBS Settings → Audio → Desktop Audio = "CABLE Output"

# 5. Start system
QUICK_START.bat

# 6. Open dashboard
# http://localhost:5173
```

---

## 📋 Prerequisites

### Software (WAJIB)
- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **UV** — [Install](https://github.com/astral-sh/uv) (`pip install uv`)
- **Node.js 20+** — [Download](https://nodejs.org/)
- **pnpm** — [Install](https://pnpm.io/installation) (`npm install -g pnpm`)
- **OBS Studio** — [Download](https://obsproject.com/)
- **VB-CABLE** — [Download](https://vb-audio.com/Cable/) (virtual audio device)

### API Keys (OPTIONAL)
- **Cartesia** — [Sign up](https://cartesia.ai) untuk TTS premium (bisa skip, pakai Edge-TTS gratis)
- **9router** — [Sign up](https://9router.com) untuk LLM routing (bisa skip)
- **DeepSeek** / **Anthropic** — untuk LLM fallback (bisa skip)

**Catatan:** Sistem bisa jalan tanpa API keys (pakai Edge-TTS gratis + no LLM reply).

---

## 🔧 Setup Step-by-Step

### 1. Clone & Install

```bash
git clone https://github.com/bamsbung/livetik.git
cd livetik

# Copy .env template
cp .env.example .env

# Install worker dependencies
cd apps/worker
uv sync
cd ../..

# Install controller dependencies
cd apps/controller
pnpm install
cd ../..
```

### 2. Configure .env

Edit `.env` di repo root:

```bash
# TikTok (WAJIB untuk scrape comments)
TIKTOK_USERNAME=interiorhack.id

# TTS (pilih salah satu atau keduanya)
CARTESIA_API_KEYS=sk_car_xxx,sk_car_yyy  # Premium (optional)
EDGE_TTS_VOICE=id-ID-ArdiNeural           # Gratis (default)

# LLM (optional, untuk dynamic replies)
NINEROUTER_API_KEY=your_key_here
NINEROUTER_BASE_URL=https://api.9router.com/v1
NINEROUTER_MODEL=openai/kc/kilo-auto/free

# Budget (optional)
DAILY_BUDGET_IDR=50000
```

**Minimal config untuk test:**
```bash
TIKTOK_USERNAME=interiorhack.id
EDGE_TTS_VOICE=id-ID-ArdiNeural
```

### 3. Generate Audio Library (WAJIB)

```bash
# Windows
scripts\gen_audio_library_edgets.bat

# Linux/Mac
python scripts/gen_audio_library_edgets.py
```

**Ini akan:**
- Generate 108 audio clips (~8-12 menit)
- Save ke `apps/worker/static/audio_library/`
- Create `index.json` dengan metadata

**Tanpa ini, worker tidak bisa play audio!**

### 4. Setup VB-CABLE di OBS

**Install VB-CABLE:**
1. Download dari https://vb-audio.com/Cable/
2. Install (restart PC jika diminta)
3. Verify: Control Panel → Sound → "CABLE Input" dan "CABLE Output" muncul

**Configure OBS:**
1. Buka OBS Studio
2. Settings → Audio
3. Set salah satu "Desktop Audio" ke **"CABLE Output (VB-Audio Virtual Cable)"**
4. Klik OK
5. Restart OBS

**Test audio:**
- Play musik di Windows Media Player
- Set output device ke "CABLE Input"
- OBS audio meter harus bergerak

### 5. Start System

**Opsi 1: Quick Start (Windows)**
```bash
QUICK_START.bat
```

Ini akan start worker + controller sekaligus di 2 terminal.

**Opsi 2: Manual (2 terminal)**

Terminal 1 - Worker:
```bash
cd apps/worker
uv run python -m banghack
```

Terminal 2 - Controller:
```bash
cd apps/controller
pnpm dev
```

**Expected output:**

Worker:
```
✓ Audio library loaded: 108 clips
✓ WebSocket server: ws://localhost:8765
✓ HTTP server: http://localhost:8766
✓ TikTok connected: @interiorhack.id
✓ Live Director: IDLE
```

Controller:
```
VITE v5.x.x ready in 1234 ms
➜ Local: http://localhost:5173
```

### 6. Open Dashboard

Buka browser: **http://localhost:5173**

**Dashboard pages:**
- `/` — Dashboard (metrics, system health)
- `/live` — Live Cockpit (comment stream)
- `/library` — Audio Library (108 clips grid)
- `/config` — Config (runtime settings)
- `/persona` — Persona (system prompt editor)
- `/cost` — Cost Tracker (budget monitoring)

---

## ✅ Verification Checklist

### Worker Health Check

```bash
# Check ports
netstat -an | findstr "8765"  # WebSocket
netstat -an | findstr "8766"  # HTTP

# Check audio library
curl http://localhost:8766/health
# Should return: "audio_library_ready": true, "clip_count": 108
```

### Dashboard Health Check

1. Open http://localhost:5173
2. Dashboard should show "Connected" (green dot)
3. Click "Audio Library" → should show 108 clips
4. Click play button on any clip → audio should play in OBS

### OBS Audio Check

1. OBS audio meter should show activity when clip plays
2. If no audio:
   - Check VB-CABLE installed correctly
   - Check OBS audio input = "CABLE Output"
   - Check worker terminal for errors

---

## 🎬 Go Live Test (30 menit)

### Preparation

1. **OBS Scene Setup:**
   - Create scene "Live Test"
   - Add video source (looping video produk/ruangan)
   - Add text source → read from `obs/last_reply.txt`
   - Audio input already set to VB-CABLE

2. **TikTok Setup:**
   - Buka TikTok app → Go Live
   - Copy RTMP URL + Stream Key
   - OBS Settings → Stream → paste URL + Key

3. **Worker Setup:**
   - Dashboard → Click "▶ Start Live"
   - Worker will begin 2-hour session
   - Phase 0: opening (180s) → plays A_opening clips

### During Live (Monitor)

**Dashboard shows:**
- Current phase (opening → hook → demo → etc)
- Viewers count
- Comments stream
- Audio "now playing"
- Cost tracker

**OBS shows:**
- Video loop
- Audio from VB-CABLE (worker clips)
- Text overlay (last_reply.txt)

**TikTok shows:**
- Your live stream with audio + video

### Stop Live

**Auto-stop:** 120 minutes (hard limit)

**Manual stop:**
- Dashboard → Click "⏹ Stop Live"
- Or "🚨 Emergency Stop" (immediate)

---

## 🐛 Troubleshooting

### Worker tidak start

**Error:** `CARTESIA_API_KEYS is empty`
- **Fix:** Edit `.env`, set `CARTESIA_API_KEYS=-` (disable) atau add valid key
- Or use Edge-TTS: `EDGE_TTS_VOICE=id-ID-ArdiNeural`

**Error:** `Audio library not found`
- **Fix:** Run `scripts\gen_audio_library_edgets.bat`

**Error:** `Port 8765 already in use`
- **Fix:** Kill existing worker: `taskkill /F /IM python.exe`

### Dashboard tidak connect

**Symptom:** Dashboard shows "Disconnected" (red dot)

**Fix:**
1. Check worker running: `netstat -an | findstr "8765"`
2. Check browser console for errors
3. Restart worker + controller

### Audio tidak keluar di OBS

**Symptom:** Worker plays clip, but OBS audio meter tidak bergerak

**Fix:**
1. Check VB-CABLE installed: Control Panel → Sound → "CABLE Output" exists
2. Check OBS audio input: Settings → Audio → Desktop Audio = "CABLE Output"
3. Test VB-CABLE: Play musik → set output to "CABLE Input" → OBS meter should move
4. Restart OBS

### Dashboard kosong (no clips)

**Symptom:** Audio Library page shows 0 clips

**Fix:**
1. Check worker terminal: should show "✓ Audio library loaded: 108 clips"
2. If not, run `scripts\gen_audio_library_edgets.bat`
3. Restart worker

---

## 📊 Cost Estimate (2-Hour Session)

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

GRAND TOTAL: ~Rp 11 per 2-hour session
```

**Budget:** Rp 50,000/day = ~4,500 sessions

---

## 📚 Next Steps

### After First Test
- [ ] Review session logs: `logs/session-<timestamp>.json`
- [ ] Check cost: Dashboard → Cost page
- [ ] Extend audio library: Add 50+ clips for CCTV, Senter, Tracker
- [ ] Customize persona: Dashboard → Persona page

### Production Checklist
- [ ] Generate 160+ audio clips (full library)
- [ ] Setup OBS scenes for all products
- [ ] Test 30-minute live (no strike)
- [ ] Test 2-hour live (full session)
- [ ] Monitor cost per session
- [ ] Backup `.env` and `config/` folder

### Documentation
- [`WORKFLOW_ACTUAL.md`](WORKFLOW_ACTUAL.md) — Complete workflow explanation
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — System architecture
- [`docs/LIVE_PLAN.md`](docs/LIVE_PLAN.md) — 2-hour live strategy
- [`docs/CHANGELOG.md`](docs/CHANGELOG.md) — Version history

---

## 🆘 Support

**Issues:** https://github.com/bamsbung/livetik/issues  
**Docs:** https://github.com/bamsbung/livetik/tree/main/docs

**Common questions:**
- "Dashboard kosong?" → Worker offline (expected), start worker first
- "Audio tidak keluar?" → Check VB-CABLE setup in OBS
- "LLM error?" → API keys optional, system works without LLM
- "Biaya mahal?" → Use Edge-TTS (gratis) + rule-based classifier (Rp 0)

---

**Bottom line:** Generate audio library → Setup VB-CABLE → Start worker → Open dashboard → Test audio → Go live!
