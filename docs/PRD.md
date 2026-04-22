# 📋 01 · PRD — Product Requirements Document

> **Canonical source** untuk apa yang dibangun & tidak dibangun di `tiklivenotion` v0.1.0–v0.3.0. Mirror dari Notion.

---

## 1. Product Summary

**Bang Hack** adalah AI co-pilot untuk TikTok Live @interiorhack.id — scrape komentar realtime, generate reply persona-aware, keluarkan sebagai voice-over + text overlay di OBS, dengan **controller UI** untuk monitoring dan kontrol manual.

### Elevator pitch

> Live TikTok affiliate home improvement dengan asisten AI yang membalas chat suara mirip tetangga Indonesia, guardrail anti-link, zero modal, dapat dimonitor lewat dashboard Svelte lokal.

---

## 2. Goals & Non-Goals

### ✅ Goals v0.1.0 (MVP Week 1)

- G1. Connect ke TikTok Live room `@interiorhack.id` via `isaackogan/TikTokLive`
- G2. Setiap komentar → LLM reply Bahasa Indonesia <8 detik p95
- G3. Reply keluar dalam 2 jalur: **voice-over** (Edge-TTS → VB-CABLE → OBS) + **text overlay** (file `obs/last_reply.txt`)
- G4. **Guardrail** wajib: blokir link, brand kompetitor, kata sensitif (politik/SARA/judi/dewasa)
- G5. **Rate limit**: max 8 reply/menit, min 4 detik antar reply
- G6. **Controller UI** (Svelte+Tailwind v4): live monitor, error log, persona editor, cost tracker
- G7. Dry-run mode untuk test tanpa actual TTS playback

### ✅ Goals v0.2.0 (Week 2)

- G8. Gift + Follow event → reply khusus (thanks template)
- G9. Fallback LLM (Claude Haiku) kalau DeepSeek fail
- G10. Export log session ke JSON untuk analisis

### ✅ Goals v0.3.0 (Week 3)

- G11. TikFinity alerts integration (via Browser Source)
- G12. Keyword trigger → auto scene-switch OBS

### ❌ Non-Goals (explicitly out of scope v0.x)

- N1. Avatar/lipsync realtime (deferred)
- N2. Faux live (video loop as camera) — risk tinggi, skip
- N3. Multi-akun simultan
- N4. Cloud hosting — semua **local-first**
- N5. Mobile app controller — desktop web only
- N6. Voice cloning (RVC/XTTS) — butuh GPU VRAM besar

---

## 3. User Stories

### US-01 | Sebagai streamer, saya ingin chat dibalas otomatis

**Given** saya sedang Live di TikTok  
**When** viewer comment "bang harga lampu PIR berapa?"  
**Then** Bang Hack membalas dalam ≤8 detik dengan voice + teks overlay, tanpa menyebut link/brand external

### US-02 | Sebagai streamer, saya ingin monitor kesehatan sistem

**Given** controller UI terbuka  
**When** ada error di worker  
**Then** UI tampil status merah + error log detail + saran fix di halaman `/errors`

### US-03 | Sebagai streamer, saya ingin edit persona tanpa restart

**Given** controller UI halaman `/persona`  
**When** saya edit prompt & klik Save  
**Then** worker reload persona di reply berikutnya, tanpa restart process

### US-04 | Sebagai streamer, saya ingin tahu sisa budget token

**Given** controller UI halaman `/cost`  
**When** saya lihat dashboard  
**Then** muncul: token terpakai, estimasi Rp, projected habis dalam X hari

### US-05 | Sebagai streamer, saya ingin pause sementara

**Given** sedang Live dan ingin bicara manual  
**When** saya klik tombol Pause di controller  
**Then** worker berhenti reply (tetap log chat) sampai Resume

---

## 4. Functional Requirements

| ID | Requirement | Priority | Fase |
|----|-------------|----------|------|
| FR-01 | Connect TikTok Live via isaackogan/TikTokLive | Must | v0.1 |
| FR-02 | LLM reply Bahasa Indonesia <8s p95 | Must | v0.1 |
| FR-03 | Voice-over via Edge-TTS id-ID-ArdiNeural | Must | v0.1 |
| FR-04 | Text overlay via obs/last_reply.txt | Must | v0.1 |
| FR-05 | Guardrail: blokir URL, brand, nomor HP, sensitif | Must | v0.1 |
| FR-06 | Rate limit: max 8/min, min 4s gap | Must | v0.1 |
| FR-07 | Controller UI: dashboard, live, errors, persona, config, cost | Must | v0.1 |
| FR-08 | Dry-run mode | Should | v0.1 |
| FR-09 | Gift/Follow event reply | Should | v0.2 |
| FR-10 | Claude fallback | Should | v0.2 |
| FR-11 | Session log export JSON | Should | v0.2 |
| FR-12 | Persona hot-reload | Should | v0.2 |

---

## 5. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | Reply latency p95 | ≤8 detik |
| NFR-02 | TTS audio quality | id-ID-ArdiNeural, natural |
| NFR-03 | Guardrail false negative | 0% untuk URL/brand |
| NFR-04 | Cost DeepSeek per Live 1 jam | ≤Rp 500 |
| NFR-05 | Worker memory | ≤200MB RSS |
| NFR-06 | Controller startup | ≤3 detik |

---

## 6. Success Metrics (Exit Criteria Week 1)

- ✅ 1 Live publik ≥30 menit tanpa strike
- ✅ Peak ≥20 concurrent viewer
- ✅ ≥3 klik keranjang kuning
- ✅ ≥5 follower baru
- ✅ Zero unmoderated link/brand di reply
- ✅ Biaya DeepSeek ≤Rp 2.000 total

---

## 7. Assumptions & Constraints

- A1. User sudah punya akun TikTok aktif dan eligible Live (≥1000 followers di Indonesia jika required 2026)
- A2. Hardware: Ryzen 7 2700x + GTX 1650 4GB + 16GB RAM
- A3. OS primary: Windows 11 (dev.ps1), fallback Linux (dev.sh)
- A4. Internet residential Indonesia stabil
- A5. API keys DeepSeek + Anthropic sudah diperoleh manual
- C1. Tidak boleh pakai VPN/proxy saat Live (anti-fraud TikTok)
- C2. Tidak boleh faux-live atau impersonate manusia — label **AI-assisted** wajib
- C3. Tidak boleh sebut link/brand external di reply (TikTok ToS)

---

## 8. Dependencies

- **External services**: DeepSeek API, Anthropic API (opsional), TikTok Live (free scrape), Microsoft Edge TTS (free)
- **Local tools**: OBS Studio, VB-CABLE, FFmpeg, UV, Node.js 20+, pnpm
- **Hardware**: tested pada GTX 1650 4GB — tidak ada dependency GPU (Edge-TTS cloud, LLM cloud)

---

## 9. Out-of-scope Explicit Rejection List

> 🚫 Metode di bawah ini **TIDAK akan diimplementasi** di v0.x — sudah ditolak karena risk tinggi / ToS violation / spek tidak cukup.

- Faux live / video loop sebagai kamera
- Impersonasi manusia tanpa label AI
- Spam reply tanpa rate limit
- Scraping data user TikTok di luar event stream
- Penggunaan TikTok API resmi (tidak tersedia publik)
