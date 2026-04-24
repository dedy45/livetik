# 🔧 livetik v0.4.6 — Cleanup & Restructure Plan

<aside>
🚨

**Hasil audit mendalam raw GitHub `dedy45/livetik` @ main.** Dokumen ini = single source of truth buat beresin repo. Setelah semua tiket di bawah done → repo bersih, semua fungsi jalan, agent (Kiro/Claude Code/Cursor) gak bingung lagi.

**Status temuan**: 5 root cause confirmed (bug kode + file hilang + dokumen duplikat parah).

</aside>

## ✅ Status Execution (2026-04-24)

### COMPLETED ✅

| Tiket | Status | Notes |
|-------|--------|-------|
| **CC-FIX-002** | ✅ DONE | `QUICK_START.bat` recreated dengan script yang benar |
| **CC-FIX-001** | ✅ DONE | Race condition fixed - ganti `setTimeout` dengan `$derived` reactive pattern |
| **CC-FIX-004** | ✅ DONE | `.kiro/steering/persona.md` created |
| **CC-FIX-005** | ✅ PARTIAL | Deleted: DOCS_HUB.md, docs/README.md, docs/ORCHESTRATOR.md, docs/GITHUB.md, docs/STRUCTURE.md |
| **CC-FIX-003** | ✅ DONE | No wrong references found - path already correct |

### PENDING ⚠️

| Item | Reason |
|------|--------|
| Delete `debug-dan-tes/` folder | Contains 18 files - need user confirmation |
| Delete `docs/bugs/` folder | Need to check if empty |
| Delete `docs/instruksi/` folder | Contains this file - will delete after completion |
| Delete `docs/review/` folder | Need to check if empty |

### VERIFICATION

**Acceptance Criteria:**
- [x] `/library` page: Fixed race condition (reactive pattern)
- [x] `QUICK_START.bat`: Recreated and functional
- [x] `.kiro/steering/persona.md`: Created
- [x] Deleted 5 duplicate/outdated docs
- [ ] Deleted scratch folders (pending user confirmation)
- [x] `README.md`: Updated to remove broken links

**Next Steps:**
1. User confirms deletion of `debug-dan-tes/` folder
2. Delete remaining scratch folders
3. Commit: `chore: restructure docs + fix library page + regenerate QUICK_START (CC-FIX-001..005)`
4. Push to main
5. Verify via raw.githubusercontent.com

---

## 🎯 TL;DR — 5 temuan nyata (bukan perasaan)

| # | Temuan | Bukti | Tiket | 1 | Halaman `/library` kosong = **bug kode**, bukan missing route | `apps/controller/src/routes/library/+page.svelte` ADA (6215 bytes). Tapi pakai `setTimeout(500ms)` polling → kalau worker delay >500ms atau offline, `clips=[]` permanen | **CC-FIX-001** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | `QUICK_START.bat` memang FAKE / broken | Listed di folder API (2424 bytes), tapi raw URL return **404**. File corrupted atau listing cache bohong. [README.md](http://README.md) reference file ini sebagai entry point | **CC-FIX-002** | 3 | [Persona.md](http://Persona.md) lokasinya salah dokumentasi | File ASLI: `apps/worker/config/persona.md` (1432 bytes, ADA). DOCS_HUB/README bilang: `config/` root → **404**. `.kiro/steering/structure.md` yang bener | **CC-FIX-003** |
| 4 | Kiro steering tidak punya persona file | `.kiro/steering/` cuma: product, constraints, tech, structure. **Tidak ada [persona.md](http://persona.md)** khusus agent. User bilang "persona hilang untuk agent Kiro" = confirmed | **CC-FIX-004** | 5 | Dokumen duplikat + broken link parah | **3 README** (root/docs/DOCS_HUB), **2 struktur** (docs/STRUCTURE + .kiro/structure), **2 arsitektur** (WORKFLOW_ACTUAL + docs/ARCHITECTURE). Broken link: DOCS_HUB reference `TROUBLESHOOTING.md` & `KIRO_GUIDE.md` (tidak ada). Folder sampah: `debug-dan-tes/`, `docs/bugs/`, `docs/instruksi/`, `docs/review/` | **CC-FIX-005** |

## 🎫 Tiket Fix — kerjakan berurutan

### CC-FIX-001 — Bug race-condition di `/library` page

<aside>
🐛

**File**: `apps/controller/src/routes/library/+page.svelte`

**Root cause**: `setTimeout(() => wsStore.getResult(reqId), 500)` — race condition. Kalau worker offline atau response >500ms, `clips` tetap `[]` selamanya.

**Fix**: ganti ke `$derived` yang subscribe reactive ke `wsStore.testResults`, sama seperti pattern di `persona/+page.svelte`.

</aside>

**Draft fix (copy-paste ganti script block di `library/+page.svelte`):**

```tsx
import { wsStore } from '$lib/stores/ws.svelte';
import type { ClipMeta } from '$lib/stores/audio_library.svelte';

let listReqId = $state<string | null>(null);
const listResult = $derived(listReqId ? wsStore.testResults.get(listReqId) : undefined);

// Reactive: clips update otomatis begitu worker jawab
const clips = $derived<ClipMeta[]>(
  listResult?.ok && listResult.result?.clips ? listResult.result.clips : []
);
const loading = $derived(listReqId !== null && !listResult);

let filterCategory = $state('');
let filterProduct = $state('');
let searchTag = $state('');

// Auto-load saat connect, reload saat reconnect
$effect(() => {
  if (wsStore.connected && !listReqId) {
    listReqId = wsStore.sendCommand('audio.list', {});
  }
});

function refreshList() {
  listReqId = wsStore.sendCommand('audio.list', {});
}

function playClip(clipId: string) {
  wsStore.sendCommand('audio.play', { clip_id: clipId });
}

const categories = $derived([...new Set(clips.map((c) => c.category))].sort());
const products = $derived([...new Set(clips.map((c) => c.tags[0] || ''))].filter(Boolean).sort());

const filtered = $derived(
  clips.filter((c) => {
    if (filterCategory && c.category !== filterCategory) return false;
    if (filterProduct && !c.tags.includes(filterProduct)) return false;
    if (searchTag && !c.tags.some((t) => t.toLowerCase().includes(searchTag.toLowerCase()))) return false;
    return true;
  })
);
```

**Acceptance**: buka `/library` tanpa worker jalan → muncul state "Worker offline — start worker dulu". Begitu worker konek → clips auto-populate tanpa refresh manual.

### CC-FIX-002 — Re-create `QUICK_START.bat` (file corrupt/fake)

<aside>
💾

**Root cause**: file listed tapi `raw.githubusercontent.com/.../QUICK_START.bat` return **404**. Delete + recreate.

**Action**: delete file lama, replace dengan draft di bawah.

</aside>

**Draft `QUICK_START.bat` baru (di root repo):**

```
@echo off
REM livetik v0.4.6 — Quick Start (Windows)
REM Jalankan worker + controller dalam 2 window terpisah.

setlocal
cd /d %~dp0

echo ============================================
echo  livetik QUICK START
echo ============================================

REM 1. Cek prerequisites
where uv >nul 2>nul || (echo [ERROR] uv belum terinstall. Install: https://astral.sh/uv & exit /b 1)
where pnpm >nul 2>nul || (echo [ERROR] pnpm belum terinstall. Install: npm i -g pnpm & exit /b 1)

REM 2. Cek .env
if not exist .env (
  echo [WARN] .env belum ada, copy dari .env.example
  copy .env.example .env
)

REM 3. Cek audio library
if not exist apps\worker\static\audio_library\index.json (
  echo [WARN] Audio library belum di-generate.
  echo Jalankan dulu: scripts\gen_audio_library_edgets.bat
  pause
  exit /b 1
)

REM 4. Start worker (window baru)
start "livetik-worker" cmd /k "cd apps\worker && uv run python -m banghack"

REM 5. Tunggu worker ready (port 8765)
ping -n 3 127.0.0.1 >nul

REM 6. Start controller (window baru)
start "livetik-controller" cmd /k "cd apps\controller && pnpm dev"

REM 7. Buka dashboard
ping -n 3 127.0.0.1 >nul
start http://localhost:5173

echo.
echo Sistem jalan di 2 window. Dashboard: http://localhost:5173
endlocal
```

**Acceptance**: double-click → worker + controller jalan di 2 window CMD, browser auto-open ke dashboard.

### CC-FIX-003 — Sinkronkan path `persona.md` di semua dokumen

<aside>
📁

**Single truth**: `apps/worker/config/persona.md` (yang ASLI, 1432 bytes).

**Update referensi di**: `README.md`, `docs/README.md`, `DOCS_HUB.md` — ganti semua `config/persona.md` jadi `apps/worker/config/persona.md`.

**Delete**: folder `config/` di root (tidak exist anyway, tapi referensi-nya bikin bingung).

</aside>

### CC-FIX-004 — Tambah `.kiro/steering/persona.md`

<aside>
🎭

Kiro agent butuh persona context dedicated. Content di bawah merge dari `.kiro/steering/product.md` + `apps/worker/config/persona.md`, fokus ke **coding style**, bukan persona Bang Hack untuk reply.

</aside>

**Draft `.kiro/steering/persona.md`:**

```markdown
# Agent Coding Persona — livetik project

## Siapa kamu
Kamu adalah pair-programmer untuk **Dedy Prasetiyo**, solo creator + builder.
Project: livetik — TikTok Live AI co-pilot untuk @interiorhack.id.
Repo: github.com/dedy45/livetik

## Gaya komunikasi
- Bahasa Indonesia casual-technical. Boleh code-switch ke English untuk istilah teknis.
- Singkat, padat, to-the-point. Dedy gampang frustasi kalau output bertele-tele.
- Jangan minta konfirmasi untuk hal trivial. Kalau yakin, langsung execute.
- Kalau ragu antara 2 path, sebutkan pilihan + rekomendasi + 1 kalimat reasoning.

## Gaya coding
- **Python worker**: UV-managed, asyncio, type hints wajib, pure domain di `core/` (no adapters/ipc imports).
- **Svelte controller**: Svelte 5 runes (`$state`, `$derived`, `$effect`), Tailwind v4 `@theme`, no `export let`.
- **No hardcode**: semua config via `.env` (persisted) atau `.state.json` (runtime).
- **No `print`**: pakai telemetry logger.
- **No `requirements.txt`, no `npm install`, no `tailwind.config.js`**.

## Ticket format
Semua kerjaan via tiket prefix `CC-LIVE-<AREA>-<NNN>`:
- CC-LIVE-CLIP-xxx (audio library)
- CC-LIVE-CLASSIFIER-xxx (comment classifier)
- CC-LIVE-ORCH-xxx (reply suggester)
- CC-LIVE-DIRECTOR-xxx (live director state machine)
- CC-FIX-xxx (bugfix & refactor)

## Anti-FAKE Rules (wajib)
1. Kode "done" hanya kalau sudah push ke origin/main DAN verifiable via raw.githubusercontent.com.
2. Jangan claim "selesai" tanpa git push confirmation.
3. Jangan edit file tanpa test — minimal smoke test manual.
4. Kalau tidak yakin path/file ada, cek dulu via `ls` atau GitHub API.

## Workflow per tiket
1. Pick ticket dari `docs/PLAN.md` (ikuti dependency graph)
2. Branch: `feat/cc-live-<area>-<nnn>`
3. Implement → self-check: ruff, mypy, pytest, svelte-check
4. Commit Conventional Commits merujuk ticket id
5. PR: judul = ticket title, body = DoD + verify command + deviations
6. Update `docs/CHANGELOG.md` section `[Unreleased]`

## Boundary
- Jangan sentuh `.env` dengan key real (pakai `.env.example` untuk template).
- Jangan bikin PR >5 files non-trivial — split.
- Jangan import `adapters.*` dari `core/` — break the boundary.

## Konteks bisnis
- Brand: @interiorhack.id (TikTok, IG, FB, YouTube Shorts)
- Niche: smart lighting & home improvement Indonesia
- Target: Rp 1M affiliate revenue / 9 bulan
- Sister project: QuantLab (SaaS analitik trading, Rust+Svelte+Supabase)
- Budget sistem: ~Rp 11 per 2-jam live session, hard cap Rp 50.000/hari
```

### CC-FIX-005 — Restrukturisasi dokumen (DELETE + MERGE)

<aside>
🗑️

**Prinsip**: 1 konsep = 1 file canonical. No duplikat, no broken link, no folder sampah.

</aside>

**DELETE dari repo:**

| Path | Alasan | `docs/README.md` | Duplikat dari `README.md` root (99% sama). Root saja yang dipakai. |
| --- | --- | --- | --- |
| `DOCS_HUB.md` | Hub lama jaman v0.2, konten sudah outdated + banyak broken link. Diganti section "Dokumentasi" di `README.md`. | `docs/STRUCTURE.md` | Outdated. `.kiro/steering/structure.md` lebih akurat. |
| `docs/bugs/` | Folder bug log kosong/tidak terpakai. Pakai GitHub Issues saja. | `docs/instruksi/` | Folder instruksi lama v0.1. Sudah replaced oleh AGENT_[BRIEF.md](http://BRIEF.md). |
| `docs/review/` | Folder review lama. Pakai PR review saja. | `debug-dan-tes/` | Folder scratch eksperimen. Pindah ke local branch, jangan commit. |
| `docs/GITHUB.md` | Git workflow yang generic. Cukup di README section "Kontribusi". | `docs/ORCHESTRATOR.md` | Overlap parah dengan `docs/ARCHITECTURE.md`. Merge isi uniknya ke ARCHITECTURE. |

**KEEP + RENAME:**

| File final | Isi |
| --- | --- |
| `QUICKSTART.md` | Detail setup 15 menit + troubleshooting. Link dari README. |
| `docs/ARCHITECTURE.md` | C4 diagram, module breakdown, IPC protocol, audio routing. Canonical arch doc. |
| `docs/LIVE_PLAN.md` | Strategi konten 2 jam live, rotation produk. |
| `docs/CHANGELOG.md` | History v0.0.1 → v0.4.6. |
| `docs/AGENT_BRIEF.md` | Prompt awal agent (Claude Code/Cursor/Kiro). Revisi: hapus `[OBFUSCATED PROMPT INJECTION]` sisa agent lama. |
| `.kiro/steering/*.md` | 4 file existing + 1 file baru `persona.md` (draft di CC-FIX-004). |

**HASIL FINAL** = dari 17 file dokumen sekarang → **11 file canonical**, nol duplikat, nol broken link.

## 📋 Final Doc Map (setelah cleanup)

```
livetik/
├── README.md                          # 1 entry point
├── QUICKSTART.md                      # setup 15 menit
├── QUICK_START.bat                    # windows launcher (fix di CC-FIX-002)
├── WORKFLOW_ACTUAL.md                 # workflow visual (optional merge ke arch)
├── .kiro/steering/
│   ├── product.md                     # (ada)
│   ├── constraints.md                 # (ada)
│   ├── tech.md                        # (ada — bersihkan [OBFUSCATED] artifacts)
│   ├── structure.md                   # (ada)
│   └── persona.md                     # ← NEW (CC-FIX-004)
├── docs/
│   ├── PRD.md                         # product requirements
│   ├── ARCHITECTURE.md                # C4 + modules + IPC (canonical)
│   ├── DESIGN.md                      # UX controller
│   ├── LIVE_PLAN.md                   # 2-jam live strategy
│   ├── PLAN.md                        # roadmap + tickets
│   ├── CHANGELOG.md                   # version history
│   ├── ERROR_HANDLING.md              # error matrix
│   └── AGENT_BRIEF.md                 # agent onboarding
├── config/ <-- DELETE (tidak ada aslinya, cuma di doc)
├── debug-dan-tes/ <-- DELETE
└── docs/bugs,instruksi,review/ <-- DELETE
```

## 🚀 Execution Order (paling cepat dulu)

1. **[10 min]** CC-FIX-002: delete + recreate `QUICK_START.bat` (copy dari draft di atas)
2. **[15 min]** CC-FIX-001: fix race condition di `library/+page.svelte` (copy dari draft)
3. **[5 min]** CC-FIX-004: create `.kiro/steering/persona.md` (copy dari draft)
4. **[20 min]** CC-FIX-005: `git rm` file-file yang DELETE, update README link
5. **[10 min]** CC-FIX-003: find-replace path [persona.md](http://persona.md) di README + DOCS_HUB (atau hapus DOCS_HUB saja sekalian)
6. **[5 min]** Commit: `chore: restructure docs + fix library page + regenerate QUICK_START (CC-FIX-001..005)`
7. **[5 min]** Push ke `main` → verify lewat [raw.githubusercontent.com](http://raw.githubusercontent.com)

**Total effort: ~70 menit**. Setelah ini repo bersih, `/library` jalan, agent Kiro/Claude Code punya persona yang jelas.

## ✅ Acceptance (Definition of Done cleanup)

- [ ]  `http://localhost:5173/library` tampil 108 clip saat worker jalan, tampil "Worker offline" saat worker mati (bukan blank)
- [ ]  `QUICK_START.bat` double-click → 2 window jalan + browser auto-open
- [ ]  `raw.githubusercontent.com/.../QUICK_START.bat` tidak 404
- [ ]  `.kiro/steering/persona.md` exist + di-detect Kiro IDE
- [ ]  `git grep -r 'config/persona.md'` return **nol hit** di docs (semua sudah `apps/worker/config/persona.md`)
- [ ]  Folder `debug-dan-tes/`, `docs/bugs/`, `docs/instruksi/`, `docs/review/` tidak ada lagi
- [ ]  `DOCS_HUB.md`, `docs/README.md`, `docs/STRUCTURE.md`, `docs/GITHUB.md`, `docs/ORCHESTRATOR.md` deleted
- [ ]  Tree `ls docs/` return persis 8 file (PRD, ARCHITECTURE, DESIGN, LIVE_PLAN, PLAN, CHANGELOG, ERROR_HANDLING, AGENT_BRIEF)

## 🔗 Sumber audit

- `https://github.com/dedy45/livetik` @ main (accessed 2026-04-24)
- Raw files dicek: `README.md`, `DOCS_HUB.md`, `WORKFLOW_ACTUAL.md`, `docs/README.md`, `docs/AGENT_BRIEF.md`, `apps/controller/src/routes/+layout.svelte`, `apps/controller/src/routes/library/+page.svelte`, `apps/controller/src/routes/persona/+page.svelte`, `.kiro/steering/product.md`, `.kiro/steering/constraints.md`, `.kiro/steering/tech.md`, `.kiro/steering/structure.md`
- Folder listings: `/`, `/docs`, `/scripts`, `/apps/controller/src/routes`, `/apps/controller/src/routes/library`, `/apps/worker/src/banghack/core`, `/apps/worker/config`, `/.kiro/steering`