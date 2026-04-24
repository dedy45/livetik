### Status GitHub Setelah Push Terakhir

**Yang baru ter-commit ✅**

- `scripts/gen_audio_library.py` — lengkap, production-ready (round-robin API key, idempotent, rate-limit 0.5s)
- `scripts/gen_audio_library.bat` — wrapper Windows
- `.gitignore` — sudah block `apps/worker/static/audio_library/*.wav`
- `apps/controller/src/routes/library/+page.svelte` — page Audio Library full (filter category/product, search tag, stats, grid)

**Yang MASIH belum ada ❌** (dan bikin build masih crash)

- `apps/controller/src/lib/components/AudioLibraryGrid.svelte` — 404
- `apps/controller/src/lib/components/TwoHourTimer.svelte` — 404
- `apps/controller/src/lib/components/EmergencyStop.svelte` — 404
- `apps/controller/src/lib/components/ReplySuggestions.svelte` — 404
- `apps/controller/src/lib/components/DecisionStream.svelte` — 404
- `apps/controller/src/lib/stores/live_state.ts` — 404
- `apps/controller/src/lib/stores/audio_library.svelte` — 404 (note: `/library` impor dari `.svelte`, bukan `.ts` — perlu match)
- `apps/controller/src/lib/stores/decisions.ts` — 404
- `apps/worker/static/audio_library/index.json` — masih `{"clips": []}` (script belum dijalankan)
- Root `+page.svelte` — **masih import 5 komponen yang 404** = `pnpm dev` akan langsung gagal

**Inconsistency yang harus di-notice**

- `/library/+page.svelte` import `ClipMeta` dari `$lib/stores/audio_library.svelte` → store harus namanya `audio_library.svelte.ts` (Svelte 5 rune file), bukan `audio_library.ts` seperti rencana awal. Konsisten-kan di dokumen agent.

---

### 🎯 Plan FINAL — Urutan Eksekusi Ready-to-Run

**STEP 1 · Fix build crash (30 menit)** — paling urgent

Commit 5 placeholder komponen + 3 store minimum agar `pnpm dev` jalan:

```bash
# Di apps/controller/src/lib/components/
# Isi masing-masing cukup: <div class="text-text-secondary">ComponentName placeholder</div>
AudioLibraryGrid.svelte
TwoHourTimer.svelte
EmergencyStop.svelte
ReplySuggestions.svelte
DecisionStream.svelte

# Di apps/controller/src/lib/stores/
live_state.svelte.ts        # minimal export state {}
audio_library.svelte.ts     # minimal export type ClipMeta + state
decisions.svelte.ts         # minimal export state []
```

Verifikasi: `cd apps/controller && pnpm dev` → tidak ada error `Failed to resolve import`.

**STEP 2 · Generate 108 audio clip (1-2 jam)**

```bash
# 1. Pastikan .env punya CARTESIA_API_KEYS (boleh 1 atau lebih, comma-separated)
# 2. Run
scripts\gen_audio_library.bat
# 3. Verifikasi
curl http://localhost:8766/health
# expect: audio_ready: true, audio_library_clip_count: 108
```

**STEP 3 · Isi 3 komponen + 3 store dengan logic real (4-5 jam)**

Skeleton sudah ada di [🔬 17 · v0.4 Implementation Review — Bugs, Gaps & Completion Plan](https://www.notion.so/17-v0-4-Implementation-Review-Bugs-Gaps-Completion-Plan-3b7aa241f5284b99bd6819d091b7f067?pvs=21) §Hari 2 dan [🎨 18 · UX Navigation + Go-Live Gap Closure (Backend + Frontend)](https://www.notion.so/18-UX-Navigation-Go-Live-Gap-Closure-Backend-Frontend-fff3bef08a734370a76ca77ba4c8feeb?pvs=21) §G6. Urutan:

1. `live_state.svelte.ts` (paling dipakai semua komponen)
2. `audio_library.svelte.ts` (dipakai /library dan Grid)
3. `decisions.svelte.ts`
4. `TwoHourTimer.svelte` (hijau/kuning/merah)
5. `EmergencyStop.svelte` (sticky, confirm dialog, deadman switch)
6. `AudioLibraryGrid.svelte`
7. `DecisionStream.svelte`
8. `ReplySuggestions.svelte` (keyboard A/S/D/Q/W)

**STEP 4 · Redesign `/live` jadi Cockpit (3 jam)**

Ganti `routes/live/+page.svelte` dari passive monitor jadi 3-panel layout (lihat [🎨 18 · UX Navigation + Go-Live Gap Closure (Backend + Frontend)](https://www.notion.so/18-UX-Navigation-Go-Live-Gap-Closure-Backend-Frontend-fff3bef08a734370a76ca77ba4c8feeb?pvs=21) §Live Cockpit). Wire WS event ke store. Implement keyboard shortcuts.

**STEP 5 · Refactor root Dashboard + Layout (1 jam)**

- Hapus import 5 komponen live dari `routes/+page.svelte`, ganti tombol besar "🎙️ Mulai Live Session →" link ke `/live`
- Update `+layout.svelte`: nav rename `Live Monitor → Live Cockpit`, tambah `Audio Library` item, version `v0.1.0-dev → v0.4.0-dev`

**STEP 6 · Extend content (3 jam)**

- `clips_script.yaml`: tambah kategori `D_cctv_*`, `E_senter_*`, `F_tracker_*`, `G_question_hooks`, `H_price_safe`, `I_trust_safety`, `J_idle_human` (~70 clip tambahan → total ~180)
- `products.yaml`: extend runsheet cover 7200s tanpa loop
- Re-run `gen_audio_library.bat` (idempotent, skip yang sudah ada)

**STEP 7 · Dress rehearsal (1 jam)**

- `REPLY_ENABLED=false`, `DRY_RUN=true`
- Start worker + controller + OBS virtual camera
- Mock-live 30 menit, verifikasi: timer jalan, no silent gap >30s, emergency stop berfungsi, reply suggestion muncul

---

### Prompt Siap-Paste ke Agent Lokal (Step 1-3 sekaligus)

```
Kerjakan urut sesuai https://www.notion.so/fff3bef08a734370a76ca77ba4c8feeb §Plan FINAL Step 1-3:

1. Commit 5 komponen placeholder + 3 store minimum di apps/controller/src/lib/ 
   supaya `pnpm dev` tidak crash. Store pakai nama `*.svelte.ts` (Svelte 5 rune), 
   bukan `.ts` biasa, karena /library sudah impor dari audio_library.svelte.

2. Isi logic real per komponen dengan skeleton di https://www.notion.so/3b7aa241f5284b99bd6819d091b7f067 §Hari 2 dan 
   https://www.notion.so/fff3bef08a734370a76ca77ba4c8feeb §G6. Urutan: stores dulu, baru komponen.

3. Setelah components jadi, jalankan scripts\gen_audio_library.bat dengan 
   CARTESIA_API_KEYS aktif. Verifikasi `/health` return audio_library_clip_count: 108.

Commit per step dengan prefix [v0.4][feat:XXX]. STOP kalau ada yang tidak jelas.
Jangan ubah behavior worker v0.3 existing.
```

### Jawaban langsung untuk pertanyaanmu

1. **Sudah diperbarui GitHub?** — Ya sebagian: script audio + .bat + .gitignore + `/library` page sudah ada. Tapi **5 komponen + 3 store masih belum**, dan **itu yang bikin build crash**.
2. **Masih ada bugs?** — Ya 1 bug kritis: root `+page.svelte` masih impor komponen yang belum ada. Selain itu worker backend sudah solid (7 bug fixed).
3. **Selanjutnya bagaimana?** — Eksekusi 7 step di atas. **Wajib mulai dari Step 1** (fix build) biar bisa test end-to-end. Step 2 (generate audio) bisa paralel kalau kamu punya API key aktif.

Estimasi total: **2 hari kerja intensif** (12-14 jam) sampai bisa dress-rehearsal.