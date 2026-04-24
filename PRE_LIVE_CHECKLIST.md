# ✅ PRE-LIVE CHECKLIST — livetik v0.4.6

**Gunakan checklist ini sebelum GO LIVE ke TikTok Studio.**

---

## 🔧 HARDWARE & SOFTWARE

- [ ] **VB-CABLE terinstall**
  - Windows Sound settings → Output → ada "CABLE Input (VB-Audio Virtual Cable)"
  - Kalau belum: https://vb-audio.com/Cable/ → install → **RESTART WINDOWS**

- [ ] **OBS Studio terinstall**
  - Version 28+ recommended
  - Profile "Live" sudah configured

- [ ] **Python 3.11+ & UV**
  - `python --version` → 3.11 atau lebih tinggi
  - `uv --version` → installed

- [ ] **Node 20+ & pnpm**
  - `node --version` → 20 atau lebih tinggi
  - `pnpm --version` → installed

---

## ⚙️ CONFIGURATION

- [ ] **`.env` file configured**
  ```bash
  # Wajib diisi:
  TIKTOK_USERNAME=interiorhack.id
  AUDIO_OUTPUT_DEVICE=CABLE Input
  CARTESIA_API_KEYS=sk_car_...
  CARTESIA_VOICE_ID=280171e4-...
  NINEROUTER_API_KEY=sk-...
  
  # Feature flags untuk live:
  REPLY_ENABLED=true
  DRY_RUN=false
  ```

- [ ] **Audio library generated**
  - File exist: `apps/worker/static/audio_library/index.json`
  - Total clips: 108 files
  - Kalau belum: `scripts\gen_audio_library_edgets.bat`

- [ ] **Persona file exist**
  - File: `apps/worker/config/persona.md`
  - Size: ~1432 bytes
  - Kalau belum: copy dari `.kiro/steering/persona.md`

---

## 🔊 AUDIO ROUTING

- [ ] **List audio devices**
  ```bash
  python scripts/list_audio_devices.py
  ```
  Output harus tampilkan "CABLE Input" dengan marker `← VB-CABLE`

- [ ] **Test audio routing**
  ```bash
  python scripts/test_audio_routing.py
  ```
  Checklist dari script:
  - [ ] VB-CABLE detected
  - [ ] `.env` configured correctly
  - [ ] Test tone played successfully
  - [ ] OBS audio meter showed activity
  - [ ] Audio did NOT play through laptop speakers

- [ ] **OBS audio source configured**
  - Source type: **Audio Input Capture**
  - Device: `CABLE Output (VB-Audio Virtual Cable)`
  - Advanced Audio Properties:
    - Audio Monitoring: **Monitor and Output**
    - Monitor Device: Headphone kamu
  - Level meter: -20 dB saat silent

---

## 🐍 WORKER

- [ ] **Worker starts successfully**
  ```bash
  cd apps/worker
  uv run python -m banghack
  ```

- [ ] **Worker logs show:**
  ```
  ✓ audio_library: matched device X: CABLE Input
  ✓ tts: matched device X: CABLE Input
  ✓ audio_library: 108 clips loaded
  ✓ live_director: ready=True
  ✓ WS server listening on ws://127.0.0.1:8765
  ✓ HTTP server listening on http://127.0.0.1:8766
  ```

- [ ] **No errors in worker terminal**
  - Tidak ada error merah
  - Tidak ada warning "device not found"

---

## 🖥️ CONTROLLER

- [ ] **Controller starts successfully**
  ```bash
  cd apps/controller
  pnpm dev
  ```

- [ ] **Dashboard accessible**
  - URL: http://localhost:5173
  - Connection indicator: **HIJAU** (connected)

- [ ] **Dashboard pages working:**
  - [ ] `/` — Dashboard (metrics, viewers, comments)
  - [ ] `/library` — Audio Library (108 clips tampil)
  - [ ] `/persona` — Persona (text tampil)
  - [ ] `/config` — Config (env vars tersensor)
  - [ ] `/live` — Live Control (start/stop buttons)

- [ ] **Audio library test**
  - Buka `/library` page
  - Klik Play pada salah satu clip
  - ✅ OBS audio meter bergerak
  - ✅ Audio TIDAK keluar di laptop speaker
  - ✅ Audio keluar di headphone (via OBS monitor)

---

## 🎬 OBS

- [ ] **Scene configured**
  - Scene name: "Live Main" (atau sesuai setup kamu)
  - Video source: Looping video produk/ruangan
  - Audio source: "VO Bang Hack" = CABLE Output
  - Text source: `obs/last_reply.txt` (file-based overlay)

- [ ] **Audio mixer check**
  - Track "VO Bang Hack" visible
  - Level: -20 dB saat silent
  - Tidak ada clipping (merah)

- [ ] **Stream settings**
  - Platform: Custom
  - Server: TikTok Live RTMP URL
  - Stream Key: dari TikTok Studio
  - Output resolution: 1080p atau 720p
  - Bitrate: 2500-4000 kbps

- [ ] **Test stream (optional)**
  - Start Streaming (private mode)
  - Cek delay audio ≤ 500ms
  - Stop Streaming

---

## 🎯 LIVE DIRECTOR (Optional)

Kalau mau pakai auto-rotation:

- [ ] **Runsheet configured**
  - File: `apps/worker/config/products.yaml`
  - Minimal 3 phase: intro, showcase, CTA
  - Total duration: ≤ 7200s (2 jam)

- [ ] **Test Live Director**
  - Dashboard → `/live` → klik "Start Live"
  - Amati phase bergulir di metrics
  - Audio clips auto-play sesuai phase
  - Klik "Stop Live" untuk test emergency stop

Kalau TIDAK mau auto-rotation:
- [ ] Skip Live Director, manual play dari `/library` page

---

## 🚨 EMERGENCY PROCEDURES

- [ ] **Emergency stop tested**
  - Dashboard → `/live` → klik "Emergency Stop"
  - Audio langsung berhenti
  - Phase reset ke IDLE

- [ ] **Budget monitor working**
  - Dashboard → widget "Cost Today"
  - Hard cap: Rp 50.000/hari
  - Kalau mendekati → matikan `REPLY_ENABLED`

- [ ] **Handling masalah printed/bookmarked**
  - Dokumen: `docs/instruksi/🎬 livetik — LIVE READY SOP`
  - Section: "🛡️ HANDLING MASALAH"
  - Print atau bookmark untuk panik-guide

---

## 🎬 GO LIVE PROCEDURE

### T-30 menit

- [ ] Reboot PC (bersih dari zombie audio routing)
- [ ] Jalankan `scripts\dev.bat`
- [ ] Buka http://localhost:5173 → tunggu indicator hijau
- [ ] Buka OBS → load profile Live
- [ ] Checklist di atas ✅ semua

### T-5 menit

- [ ] Buka TikTok Studio → siap Go Live
- [ ] Dashboard `/config` → verify `REPLY_ENABLED=true`, `DRY_RUN=false`
- [ ] (Optional) Dashboard `/live` → klik "Start Live" kalau pakai Director

### T-0 (GO LIVE)

- [ ] OBS → Start Streaming
- [ ] TikTok Studio → Go Live
- [ ] Pantau 3 metric di dashboard:
  - `status = live` (TikTok connected)
  - `comments` counter naik
  - `latency_p95_ms` < 2000

### Selama Live

- [ ] Monitor dashboard metrics
- [ ] Approve reply suggestions (klik ✅ di `/live` page)
- [ ] Manual play clips dari `/library` (kalau tidak pakai Director)
- [ ] Scene switch manual di OBS (hotkey F1-F5)
- [ ] Budget monitor < Rp 50.000

### T+120 (END)

- [ ] Dashboard `/live` → klik "Stop Live" (kalau Director jalan)
- [ ] TikTok Studio → End Live
- [ ] OBS → Stop Streaming
- [ ] Screenshot metric final untuk log

---

## ❌ BLOCKER — JANGAN LIVE KALAU:

- ❌ VB-CABLE tidak terinstall
- ❌ `python scripts/test_audio_routing.py` gagal
- ❌ OBS audio meter tidak bergerak saat test clip
- ❌ Worker log tampil error "device not found"
- ❌ Audio library belum generated (0 clips)
- ❌ `.env` tidak configured (missing API keys)
- ❌ Dashboard tidak connect (indicator merah)

**Lebih baik tunda 1 hari daripada live dengan audio mati 2 jam!**

---

## ✅ DEFINITION OF DONE

Semua checklist di atas ✅ → **READY FOR LIVE** 🚀

Kalau ada 1 yang gagal → **FIX DULU** → test ulang → baru GO LIVE.

---

## 📚 REFERENCES

- [README.md](README.md) — Overview sistem
- [WORKFLOW_ACTUAL.md](WORKFLOW_ACTUAL.md) — Workflow sebenarnya
- [docs/AUDIO_ROUTING_IMPLEMENTATION.md](docs/AUDIO_ROUTING_IMPLEMENTATION.md) — Audio routing detail
- [docs/instruksi/🎬 livetik — LIVE READY SOP](docs/instruksi/🎬%20livetik%20—%20LIVE%20READY%20SOP%20(Voice-over%20→%20OBS,%20fix%20%209874dafedf7e4eb38dc4a26314a0d4ff.md) — Complete SOP
- [scripts/list_audio_devices.py](scripts/list_audio_devices.py) — Device discovery
- [scripts/test_audio_routing.py](scripts/test_audio_routing.py) — Integration test

---

**Last Updated:** 24 Apr 2026  
**Version:** v0.4.6  
**Status:** ✅ AUDIO ROUTING IMPLEMENTED
