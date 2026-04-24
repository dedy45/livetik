# Langkah Selanjutnya yang Sebenarnya Perlu Dilakukan

**Tanggal**: 2026-04-24  
**Status**: Semua komponen sudah lengkap, siap untuk testing dan content generation

---

## ✅ YANG SUDAH SELESAI (Tidak Perlu Dikerjakan Lagi)

### Backend (95% Complete)
- ✅ Worker Python dengan semua adapter
- ✅ WebSocket server dengan 30+ commands
- ✅ Audio library manager
- ✅ Comment classifier (rule-first + LLM fallback)
- ✅ Live director state machine
- ✅ Budget guard dengan rate limiting
- ✅ Reply cache dengan similarity matching
- ✅ Suggester dengan template + LLM
- ✅ Script gen_audio_library.py + .bat

### Frontend (100% Complete)
- ✅ Semua 5 komponen v0.4 (AudioLibraryGrid, DecisionStream, ReplySuggestions, TwoHourTimer, EmergencyStop)
- ✅ Semua 3 stores (ws, live_state, audio_library)
- ✅ Dashboard dengan integrasi v0.4
- ✅ Audio Library page (/library)
- ✅ Layout navigation (Live Cockpit, Audio Library, v0.4.0-dev)
- ✅ Semua komponen menggunakan Svelte 5 runes dengan benar
- ✅ Semua komponen SSR-safe

### Documentation (100% Complete)
- ✅ DOCS_HUB.md updated
- ✅ CHANGELOG.md v0.4.2
- ✅ BUGFIX_PLAN.md updated
- ✅ UX_NAVIGATION_FIXES_COMPLETED.md

---

## 🎯 YANG BENAR-BENAR PERLU DILAKUKAN

### STEP 1: Generate Audio Library (1-2 jam) 🔴 URGENT

**Kenapa Urgent**: Tanpa ini, tidak bisa test audio playback sama sekali

**UPDATE v0.4.4**: TTS initialization error sudah diperbaiki! Cartesia API keys sekarang terbaca dengan benar.

**STATUS**: ✅ READY TO RUN (v0.4.4 fix applied)

**Opsi A: Cartesia (PREMIUM, HIGH QUALITY) ✅ RECOMMENDED**
```bash
cd livetik
scripts\gen_audio_library.bat
```

**Opsi B: Edge-TTS (FREE, NO API KEY REQUIRED)**
```bash
cd livetik
scripts\gen_audio_library_edgets.bat
```

**Rekomendasi**: Gunakan Opsi A (Cartesia) karena API key sudah dikonfigurasi dengan benar di `.env`. Kualitas Cartesia sonic-3 dengan emotion control lebih natural untuk live streaming. Edge-TTS tetap tersedia sebagai fallback.

**What Was Fixed (v0.4.4)**:
- ❌ Before: Worker loaded `apps/worker/.env` (partial config, no API keys)
- ✅ After: Worker loads `livetik/.env` (complete config, has API keys)
- ❌ Before: `load_dotenv()` → reads from CWD
- ✅ After: `load_dotenv(_env_path)` → explicit root path

**Expected Output**:
```
Processing clip A_opening_001...
✓ Generated A_opening_001.wav (3.2s, 102KB)
Processing clip A_opening_002...
✓ Generated A_opening_002.wav (2.8s, 89KB)
...
✓ Total: 108 clips generated
✓ index.json updated
```

**Verifikasi**:
```bash
# Check file count
dir apps\worker\static\audio_library\*.wav | measure

# Should show: Count = 108

# Check index.json
type apps\worker\static\audio_library\index.json

# Should show: {"clips": [108 entries]}
```

**Troubleshooting**:
- Error "uv not found" → Install uv: https://docs.astral.sh/uv/getting-started/installation/
- Error "edge_tts not found" → Run `uv sync` di apps/worker
- Error "File exists" → Normal, script skip file yang sudah ada (idempotent)

---

### STEP 2: Test Audio Playback (30 menit)

**Start Worker**:
```bash
cd livetik\apps\worker
uv run python -m banghack.ipc.main
```

**Expected Output**:
```
INFO: Worker starting...
INFO: Audio library loaded: 108 clips
INFO: WebSocket server on ws://localhost:8765
INFO: HTTP server on http://localhost:8766
```

**Start Controller**:
```bash
cd livetik\apps\controller
pnpm run dev
```

**Expected Output**:
```
VITE v5.x.x ready in xxx ms
➜ Local: http://localhost:5173/
```

**Test Sequence**:
1. Buka http://localhost:5173
2. Klik "Audio Library" di sidebar
3. Verifikasi: 108 clips muncul di grid
4. Klik salah satu clip
5. Expected: Audio keluar dari speaker (via VB-CABLE atau default device)

**Troubleshooting**:
- No audio → Check VoiceMeeter Banana setup (docs/AUDIO_ROUTING_TROUBLESHOOTING.md)
- Clips not showing → Check worker logs, pastikan index.json loaded
- Click tidak response → Check browser console untuk error

---

### STEP 3: Extend Content (3 jam) 🟡 HIGH PRIORITY

**File**: `apps/worker/config/clips_script.yaml`

**Yang Perlu Ditambah**:

```yaml
# 1. CCTV Category (20 clips)
D_cctv_demo:
  - id: D_cctv_demo_001
    script: "CCTV V380 Pro ini punya dual lens HD, bisa auto tracking 360 derajat!"
    tags: [cctv, v380pro, demo]
    scene_hint: product_showcase
  # ... 9 more demo clips

D_cctv_cta:
  - id: D_cctv_cta_001
    script: "Mau rumah aman 24 jam? Cek link di bio untuk CCTV V380 Pro!"
    tags: [cctv, v380pro, cta]
    scene_hint: call_to_action
  # ... 9 more cta clips

# 2. LED Senter Category (20 clips)
E_senter_demo:
  - id: E_senter_demo_001
    script: "LED Senter XHP160 ini super terang, 10 juta lumens! USB Type-C, tahan air IPX6!"
    tags: [senter, xhp160, demo]
    scene_hint: product_showcase
  # ... 9 more

E_senter_cta:
  # ... 10 clips

# 3. GPS Tracker Category (20 clips)
F_tracker_demo:
  - id: F_tracker_demo_001
    script: "DINGS Smart GPS Tracker pakai Bluetooth 5.2, tahan air, baterai awet!"
    tags: [tracker, dings, demo]
    scene_hint: product_showcase
  # ... 9 more

F_tracker_cta:
  # ... 10 clips

# 4. Question Hooks (10 clips)
G_question_hooks:
  - id: G_question_001
    script: "Wah, pertanyaan bagus nih! Sebentar ya, saya jelasin..."
    tags: [reaction, question, filler]
    scene_hint: host_reaction
  # ... 9 more

# 5. Price Deflection (10 clips)
H_price_safe:
  - id: H_price_001
    script: "Untuk harga terbaik, langsung cek link di bio ya kak!"
    tags: [price, deflect, safe]
    scene_hint: host_talking
  # ... 9 more

# 6. Trust & Safety (10 clips)
I_trust_safety:
  - id: I_trust_001
    script: "Produk ini sudah ribuan yang beli, review 4.8 bintang!"
    tags: [trust, review, social_proof]
    scene_hint: host_talking
  # ... 9 more

# 7. Idle Human Filler (10 clips)
J_idle_human:
  - id: J_idle_001
    script: "Sebentar ya kak, lagi atur kamera dulu..."
    tags: [filler, idle, human]
    scene_hint: host_adjusting
  # ... 9 more
```

**Total Tambahan**: ~70 clips → Total jadi ~180 clips

**Setelah Edit**:
```bash
# Re-run generator (idempotent, hanya generate yang baru)
scripts\gen_audio_library.bat

# Verifikasi
dir apps\worker\static\audio_library\*.wav | measure
# Should show: Count = 178-180
```

---

### STEP 4: Extend Products Runsheet (1 jam)

**File**: `apps/worker/config/products.yaml`

**Current**: 3 products, 8 phases, ~50 menit total

**Target**: 8+ products, 15+ phases, 120 menit (2 jam) tanpa loop

```yaml
products:
  # Existing (keep as is)
  - id: paloma_smartlock
    name: "PALOMA Smart Lock"
    # ...
  
  - id: reaim_pintu_lipat
    name: "Reaim Pintu Lipat PVC"
    # ...
  
  - id: tnw_chopper
    name: "TNW Blender Chopper"
    # ...

  # NEW - Add these
  - id: cctv_v380pro
    name: "CCTV V380 Pro Dual Lens"
    category: security
    price_range: "200k-350k"
    key_features:
      - "HD 1080P dual lens"
      - "Auto tracking 360°"
      - "Two-way audio"
      - "Night vision"
    
  - id: senter_xhp160
    name: "LED Senter XHP160"
    category: outdoor
    price_range: "150k-250k"
    key_features:
      - "10 juta lumens"
      - "USB Type-C rechargeable"
      - "IPX6 waterproof"
      - "5 mode cahaya"
  
  - id: tracker_dings
    name: "DINGS GPS Tracker"
    category: security
    price_range: "100k-200k"
    key_features:
      - "Bluetooth 5.2"
      - "Waterproof"
      - "Long battery life"
      - "Find My compatible"

  # Add 2-3 more products...

runsheet:
  # Existing phases (keep)
  - phase: opening
    duration_s: 300
    # ...
  
  # NEW phases - extend to cover 7200s (2 hours)
  - phase: cctv_demo
    duration_s: 600
    product: cctv_v380pro
    audio_categories: [D_cctv_demo]
    scene: product_showcase
  
  - phase: cctv_cta
    duration_s: 300
    product: cctv_v380pro
    audio_categories: [D_cctv_cta]
    scene: call_to_action
  
  - phase: senter_demo
    duration_s: 600
    product: senter_xhp160
    audio_categories: [E_senter_demo]
    scene: product_showcase
  
  - phase: senter_cta
    duration_s: 300
    product: senter_xhp160
    audio_categories: [E_senter_cta]
    scene: call_to_action
  
  # ... continue until sum(duration_s) >= 7200
```

**Verifikasi**:
```python
# Quick check
import yaml
with open('apps/worker/config/products.yaml') as f:
    data = yaml.safe_load(f)
total_duration = sum(p['duration_s'] for p in data['runsheet'])
print(f"Total duration: {total_duration}s ({total_duration/60:.1f} min)")
# Should be >= 7200s (120 min)
```

---

### STEP 5: Live Cockpit Redesign (3-4 jam) 🟡 MEDIUM PRIORITY

**File**: `apps/controller/src/routes/live/+page.svelte`

**Current State**: Passive event monitor (filter by type)

**Target State**: 3-panel active controller

**Layout**:
```
┌────────────────────────────────────────────────────────────┐
│ [⏱️ 1:23:45] [RUNNING · paloma · 2/8] [🛑 EMERGENCY]      │ ← sticky
├──────────────┬─────────────────────┬───────────────────────┤
│ RUNSHEET     │ COMMENT STREAM      │ METRICS               │
│ ▶ paloma     │ @user: "harga?"     │ 👁 234 viewers        │
│   reaim      │ [price_question]    │ 💬 127 comments       │
│   tnw        │                     │ 🤖 31 replies         │
│              │ REPLY SUGGESTIONS   │ 💰 Rp 3.240/50k       │
│ NOW PLAYING  │ 1. Cek bio ya kak   │                       │
│ 🎵 B_013     │ 2. Harga live hari  │ ACTIONS               │
│ "Material    │    ini di keranjang │ [⏸ Pause] [▶ Resume] │
│  anti-karat" │ 3. Yuk cek produk!  │ [⏭ Skip phase]       │
│              │ [1] [2] [3] [Q] [W] │                       │
└──────────────┴─────────────────────┴───────────────────────┘
```

**Implementation**:
1. Import TwoHourTimer, EmergencyStop (already done)
2. Create 3-column grid layout
3. Add runsheet panel (left)
4. Move DecisionStream to center
5. Move ReplySuggestions below DecisionStream
6. Add metrics panel (right)
7. Make top bar sticky
8. Wire keyboard shortcuts

**Keyboard Shortcuts**:
- `1`, `2`, `3` → Approve reply option
- `Q` → Reject reply
- `W` → Regenerate reply
- `Space` → Pause/Resume
- `Esc` → Blur focus
- `Ctrl+Shift+X` → Emergency stop

---

### STEP 6: Dress Rehearsal (1 jam)

**Prerequisites**:
- ✅ Audio library generated (180 clips)
- ✅ Products runsheet extended (2 hours)
- ✅ OBS Virtual Camera installed
- ✅ VoiceMeeter Banana configured

**Setup**:
```bash
# 1. Set safe mode di .env
REPLY_ENABLED=false
DRY_RUN=true

# 2. Start worker
cd apps/worker
uv run python -m banghack.ipc.main

# 3. Start controller
cd apps/controller
pnpm run dev

# 4. Open OBS, start virtual camera
```

**Test Checklist**:
- [ ] Timer countdown jalan (green → yellow → red)
- [ ] Audio clips play tanpa silent gap >30s
- [ ] Comment stream populate dengan intent badges
- [ ] Reply suggestions muncul (3 options)
- [ ] Keyboard shortcuts berfungsi (1/2/3/Q/W)
- [ ] Emergency stop confirm dialog muncul
- [ ] Phase transition smooth
- [ ] No crash selama 30 menit

**Success Criteria**:
- ✅ 30 menit continuous run tanpa crash
- ✅ No silent gap >30s
- ✅ All UI responsive
- ✅ Emergency stop berfungsi

---

## 📊 ESTIMASI WAKTU TOTAL

| Step | Estimasi | Priority | Blocker | Status |
|------|----------|----------|---------|--------|
| 1. Generate audio | 1-2 jam | 🔴 URGENT | Yes - can't test without this | ✅ READY (v0.4.4 fix) |
| 2. Test playback | 30 menit | 🔴 URGENT | Yes - verify audio works | Ready to test |
| 3. Extend content | 3 jam | 🟡 HIGH | No - can test with 108 clips | Pending |
| 4. Extend runsheet | 1 jam | 🟡 HIGH | No - can loop for testing | Pending |
| 5. Live Cockpit | 3-4 jam | 🟡 MEDIUM | No - current UI works | Pending |
| 6. Dress rehearsal | 1 jam | 🟢 LOW | No - final validation | Pending |

**Total**: 9.5-11.5 jam kerja

**Critical Path**: Step 1 → Step 2 → Step 6 (3.5 jam minimum untuk basic testing)

**v0.4.4 Update**: TTS initialization error fixed! Cartesia API keys sekarang terbaca dengan benar dari root `.env`.

---

## 🚀 QUICK START (Hari Ini)

**Jika hanya punya 2-3 jam hari ini**:

```bash
# 1. Generate audio (1-2 jam)
cd livetik
scripts\gen_audio_library.bat

# 2. Test playback (30 menit)
# Terminal 1:
cd apps/worker
uv run python -m banghack.ipc.main

# Terminal 2:
cd apps/controller
pnpm run dev

# 3. Open browser, test
http://localhost:5173
- Click "Audio Library"
- Click any clip
- Verify audio plays
```

**Jika punya 1 hari penuh**:

Lakukan Step 1-4 (generate + test + extend content + extend runsheet)

**Jika punya 2 hari**:

Lakukan semua Step 1-6 (full go-live ready)

---

## ❌ JANGAN LAKUKAN INI

### Jangan Ikuti cek.md Step 1-3

**Alasan**: Sudah selesai semua!

```
❌ "Commit 5 placeholder komponen" → Sudah ada full implementation
❌ "Commit 3 store minimum" → Sudah ada full implementation
❌ "Isi logic real per komponen" → Sudah selesai
```

### Jangan Buat Komponen Baru

Semua komponen sudah ada dan lengkap. Tidak perlu buat lagi.

### Jangan Ubah Naming Convention

`*.svelte.ts` sudah benar untuk Svelte 5 runes. Jangan rename ke `.ts`.

---

## 📞 TROUBLESHOOTING

### "Audio tidak keluar"
→ Baca `docs/AUDIO_ROUTING_TROUBLESHOOTING.md`
→ Check VoiceMeeter Banana setup
→ Check Windows audio device settings

### "Build error: Cannot find module"
→ Run `pnpm install` di apps/controller
→ Check import paths (should use `$lib/...`)

### "Worker crash saat start"
→ Check .env file (semua required keys ada?)
→ Check Python version (3.11+?)
→ Run `uv sync` di apps/worker

### "Clips tidak muncul di UI"
→ Check worker logs: "Audio library loaded: X clips"
→ Check index.json: should have clips array
→ Check browser console untuk error

---

## 🎯 SUCCESS METRICS

### Minimum Viable (untuk testing)
- ✅ 108 clips generated
- ✅ Audio playback works
- ✅ UI responsive
- ✅ No build errors

### Production Ready (untuk go-live)
- ✅ 180 clips generated
- ✅ 2-hour runsheet tanpa loop
- ✅ Live Cockpit redesigned
- ✅ 30-minute dress rehearsal passed
- ✅ All keyboard shortcuts work
- ✅ Emergency stop tested

---

## 📚 REFERENSI

- **Dokumen Akurat**: 
  - `CEK_MD_VERIFICATION_REPORT.md` (this directory)
  - `UX_NAVIGATION_FIXES_COMPLETED.md` (this directory)
  - `BUGFIX_PLAN.md` (this directory)
- **Dokumen Outdated**: 
  - `docs/review/cek.md` (written before implementation)
- **Audio Troubleshooting**: 
  - `docs/AUDIO_ROUTING_TROUBLESHOOTING.md`
- **Implementation Reference**: 
  - `docs/CHANGELOG.md` (v0.4.1, v0.4.2)
