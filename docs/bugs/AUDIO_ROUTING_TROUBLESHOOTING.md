# Audio Routing Troubleshooting Guide

> Panduan lengkap untuk setup audio routing VoiceMeeter + VB-CABLE untuk live TikTok

---

## Problem: Audio Tidak Keluar Setelah Ganti ke VoiceMeeter

### Gejala
- Setelah ganti Windows default output dari Realtek ke VoiceMeeter Input (VAIO)
- Audio tidak keluar dari speaker
- OBS juga tidak capture audio

### Root Cause
**VoiceMeeter belum dikonfigurasi untuk route audio ke speaker fisik.**

Ketika Windows default output = VoiceMeeter Input (VAIO), audio masuk ke VoiceMeeter tapi tidak otomatis keluar ke speaker. Kita harus set VoiceMeeter untuk route audio ke:
- **A1** = Speaker fisik (untuk dengar audio)
- **A2** = CABLE Input (untuk OBS capture)

---

## Solution: Konfigurasi VoiceMeeter Banana

### Step 1: Buka VoiceMeeter Banana Application

1. Cari "VoiceMeeter Banana" di Start Menu
2. Klik kanan → Run as Administrator (recommended)
3. Window VoiceMeeter Banana akan terbuka

### Step 2: Set Hardware Output A1 (Speaker Fisik)

1. Di bagian **HARDWARE OUT** (kanan atas), cari kolom **A1**
2. Klik dropdown di bawah **A1**
3. Pilih speaker fisik Anda:
   - **Realtek Audio** (jika pakai speaker/headphone langsung ke motherboard)
   - **USB Audio Device** (jika pakai USB speaker/headphone)
   - **HDMI Output** (jika audio lewat monitor HDMI)
   - **Bluetooth Audio** (jika pakai speaker/headphone Bluetooth)

**Contoh:**
```
A1: Realtek High Definition Audio
```

### Step 3: Set Hardware Output A2 (CABLE Input)

1. Di bagian **HARDWARE OUT**, cari kolom **A2**
2. Klik dropdown di bawah **A2**
3. Pilih **CABLE Input (VB-Audio Virtual Cable)**

**Contoh:**
```
A2: CABLE Input (VB-Audio Virtual Cable)
```

### Step 4: Enable A1 dan A2 untuk VAIO Input

1. Di bagian **HARDWARE INPUT** (kiri atas), cari row **VAIO** (VoiceMeeter Input)
2. Pastikan tombol **A1** dan **A2** di row VAIO **MENYALA** (warna hijau/kuning)
3. Jika belum menyala, klik tombol A1 dan A2 untuk enable

**Visual:**
```
VAIO (VoiceMeeter Input)
[A1: ON] [A2: ON] [A3: OFF] [B1: OFF] [B2: OFF]
```

### Step 5: Test Audio Flow

1. Buka browser → buka `/config` page
2. Scroll ke **TTS Output Test** section
3. Klik **Generate & Play** (Edge-TTS atau Cartesia)
4. **Expected Result:**
   - ✅ Audio keluar dari speaker fisik (via A1)
   - ✅ OBS meter bergerak (via A2 → CABLE Output)

---

## Verification Checklist

### Windows Settings
- [ ] Default Output Device = **VoiceMeeter Input (VAIO)**
  - Cara cek: Settings → System → Sound → Output → Choose your output device

### VoiceMeeter Banana Settings
- [ ] A1 = **Physical Speaker** (Realtek/USB/HDMI/Bluetooth)
- [ ] A2 = **CABLE Input (VB-Audio Virtual Cable)**
- [ ] VAIO row: **A1 button = ON** (hijau/kuning)
- [ ] VAIO row: **A2 button = ON** (hijau/kuning)

### OBS Settings
- [ ] Desktop Audio = **CABLE Output (VB-Audio Virtual Cable)**
  - Cara cek: Settings → Audio → Desktop Audio

### Test Result
- [ ] TTS audio plays in speaker
- [ ] OBS audio meter moves when TTS plays

---

## Common Issues

### Issue 1: Audio Keluar Tapi Sangat Pelan

**Cause:** Volume slider di VoiceMeeter terlalu rendah

**Solution:**
1. Di VoiceMeeter, cari **VAIO** row
2. Geser **fader** (volume slider) ke atas (sekitar -10 dB atau 0 dB)
3. Test lagi

### Issue 2: Audio Keluar di Speaker Tapi OBS Tidak Capture

**Cause:** A2 tidak enable atau OBS Desktop Audio salah

**Solution:**
1. Pastikan **A2 button di VAIO row = ON**
2. Pastikan **A2 = CABLE Input**
3. Pastikan **OBS Desktop Audio = CABLE Output**

### Issue 3: Audio Keluar di OBS Tapi Tidak di Speaker

**Cause:** A1 tidak enable atau A1 tidak set ke speaker fisik

**Solution:**
1. Pastikan **A1 button di VAIO row = ON**
2. Pastikan **A1 = Physical Speaker** (bukan CABLE, bukan None)

### Issue 4: Audio Delay/Latency Tinggi

**Cause:** Buffer size terlalu besar

**Solution:**
1. Di VoiceMeeter, klik **Menu → System Settings/Options**
2. Set **Buffering** = **WDM** (lowest latency)
3. Set **Buffer Size** = **128** atau **256** samples
4. Restart VoiceMeeter

### Issue 5: Audio Crackling/Popping

**Cause:** Buffer size terlalu kecil atau CPU overload

**Solution:**
1. Di VoiceMeeter, klik **Menu → System Settings/Options**
2. Set **Buffer Size** = **512** atau **1024** samples
3. Close aplikasi lain yang pakai audio (Discord, Spotify, dll)

---

## Alternative: Bypass VoiceMeeter (Temporary Test)

Jika VoiceMeeter masih bermasalah, bisa test dengan bypass dulu:

### Option A: Direct to Speaker (No OBS Capture)
1. Windows default output = **Realtek** (atau speaker fisik)
2. Test TTS → audio keluar di speaker
3. **Downside:** OBS tidak capture audio

### Option B: Direct to CABLE (OBS Capture Only)
1. Windows default output = **CABLE Input**
2. OBS Desktop Audio = **CABLE Output**
3. Test TTS → OBS capture audio
4. **Downside:** Tidak dengar audio di speaker (kecuali pakai OBS monitoring)

---

## Advanced: OBS Audio Monitoring

Jika mau dengar audio dari OBS (tanpa VoiceMeeter):

1. OBS → Settings → Audio → Advanced
2. Set **Monitoring Device** = **Physical Speaker** (Realtek/USB/HDMI)
3. Di OBS mixer, klik gear icon di **Desktop Audio**
4. Set **Audio Monitoring** = **Monitor and Output**
5. Test TTS → audio keluar di speaker via OBS monitoring

**Downside:**
- Latency lebih tinggi (50-200ms)
- Tidak bisa adjust volume per source

---

## Recommended Setup (Final)

### For Live Streaming:
```
Windows Default Output: VoiceMeeter Input (VAIO)
VoiceMeeter A1: Physical Speaker (Realtek/USB/HDMI)
VoiceMeeter A2: CABLE Input
OBS Desktop Audio: CABLE Output
```

**Benefit:**
- ✅ Dengar audio real-time di speaker (via A1)
- ✅ OBS capture audio clean (via A2 → CABLE)
- ✅ Bisa adjust volume per source di VoiceMeeter
- ✅ Low latency (10-30ms)

---

## Quick Reference: VoiceMeeter Button States

| Button | State | Meaning |
|--------|-------|---------|
| A1 | 🟢 Green | Audio routing to A1 (ON) |
| A1 | ⚫ Gray | Audio NOT routing to A1 (OFF) |
| A2 | 🟡 Yellow | Audio routing to A2 (ON) |
| A2 | ⚫ Gray | Audio NOT routing to A2 (OFF) |

**Target State for VAIO row:**
```
[A1: 🟢] [A2: 🟡] [A3: ⚫] [B1: ⚫] [B2: ⚫]
```

---

## Still Not Working?

### Debug Steps:

1. **Test Windows Sound:**
   - Windows Settings → Sound → Test (speaker icon)
   - Jika tidak keluar → problem di Windows/driver, bukan VoiceMeeter

2. **Test VoiceMeeter Direct:**
   - Di VoiceMeeter, klik **VAIO** row
   - Klik **SOLO** button (S)
   - Bicara ke mic atau play music
   - Jika tidak keluar → problem di VoiceMeeter config

3. **Reinstall VoiceMeeter:**
   - Uninstall VoiceMeeter Banana
   - Restart PC
   - Download fresh installer dari https://vb-audio.com/Voicemeeter/banana.htm
   - Install as Administrator
   - Restart PC lagi

4. **Check Audio Driver:**
   - Device Manager → Sound, video and game controllers
   - Pastikan tidak ada warning icon (⚠️)
   - Update driver jika ada

---

## Contact Support

Jika masih stuck, screenshot:
1. VoiceMeeter Banana window (full window)
2. Windows Sound Settings (Output section)
3. OBS Audio Settings
4. Error message (jika ada)

Dan kirim ke support channel.

---

## Related Documents

- [ARCHITECTURE.md](./ARCHITECTURE.md) — Audio flow diagram
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) — General troubleshooting
- [README.md](./README.md) — Setup guide
