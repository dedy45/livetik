# 💾 Panduan Backup ke GitHub - Livetik

## Quick Start

```cmd
cd livetik\scripts
backup-github.bat
```

Script ini akan otomatis:
1. ✅ Cek status Git
2. ✅ Add semua perubahan
3. ✅ Commit dengan timestamp
4. ✅ Pull dari remote (handle konflik)
5. ✅ Push ke GitHub

---

## Masalah yang Sudah Diperbaiki

### ✅ 1. Git Branch Mismatch

**Masalah:**
```
error: src refspec main does not match any
```

**Penyebab:**
- Branch lokal bernama `master`
- Mencoba push ke `main`

**Solusi:**
```cmd
git branch -M main
```

### ✅ 2. Git Remote Tidak Terkonfigurasi

**Masalah:**
```
error: failed to push some refs to 'origin'
```

**Penyebab:**
- Remote `origin` belum ditambahkan

**Solusi:**
```cmd
git remote add origin https://github.com/dedy45/livetik.git
```

### ✅ 3. SvelteKit TypeScript Warning

**Masalah:**
```
Cannot find base config file "./.svelte-kit/tsconfig.json"
```

**Penyebab:**
- File auto-generated belum dibuat
- Perlu run `svelte-kit sync` atau `pnpm dev`

**Solusi:**
```cmd
cd apps\controller
pnpm exec svelte-kit sync
```

**Status:** ✅ File `.svelte-kit/tsconfig.json` sudah ada

---

## Script yang Tersedia

### 1. `backup-github.bat` - Backup Lengkap

Backup semua perubahan ke GitHub dengan satu command.

```cmd
cd livetik\scripts
backup-github.bat
```

**Fitur:**
- Auto-add semua file
- Commit dengan timestamp
- Handle merge conflicts
- Push ke GitHub

### 2. `fix-svelte-tsconfig.bat` - Fix TypeScript Warning

Generate file SvelteKit yang diperlukan.

```cmd
cd livetik\scripts
fix-svelte-tsconfig.bat
```

**Fitur:**
- Cek node_modules
- Run svelte-kit sync
- Verify hasil

### 3. `fix-all.bat` - Perbaiki Semua

Jalankan semua perbaikan sekaligus.

```cmd
cd livetik\scripts
fix-all.bat
```

**Fitur:**
- Fix SvelteKit tsconfig
- Backup ke GitHub
- All-in-one solution

---

## Manual Backup (Jika Script Gagal)

### Step 1: Cek Status

```cmd
cd livetik
git status
git branch -a
git remote -v
```

### Step 2: Konfigurasi (Jika Perlu)

```cmd
# Tambah remote (jika belum ada)
git remote add origin https://github.com/dedy45/livetik.git

# Ubah branch ke main (jika masih master)
git branch -M main
```

### Step 3: Commit & Push

```cmd
# Add semua perubahan
git add .

# Commit
git commit -m "Backup: update dokumentasi dan scripts"

# Pull (jika repo sudah ada di GitHub)
git pull origin main --no-edit --allow-unrelated-histories

# Push
git push -u origin main
```

---

## Troubleshooting

### Error: "Updates were rejected"

**Solusi:**
```cmd
git pull origin main --allow-unrelated-histories --no-edit
git push origin main
```

### Error: "Permission denied"

**Solusi:**
1. Cek GitHub credentials
2. Gunakan Personal Access Token (PAT)
3. Atau setup SSH key

### Warning: "Cannot find base config file"

**Solusi:**
```cmd
cd apps\controller
pnpm exec svelte-kit sync
```

---

## Checklist Sebelum Backup

- [ ] Semua file sudah disave
- [ ] `.env` tidak di-commit (sudah di `.gitignore`)
- [ ] Tidak ada file sensitif (API keys, passwords)
- [ ] Code sudah di-test (minimal smoke test)
- [ ] Commit message jelas dan deskriptif

---

## File yang Ditambahkan

Dokumentasi dan scripts baru:

```
livetik/
├── scripts/
│   ├── backup-github.bat          # ✅ Script backup otomatis
│   ├── fix-svelte-tsconfig.bat    # ✅ Fix TypeScript warning
│   └── fix-all.bat                # ✅ All-in-one fix
├── docs/
│   └── TROUBLESHOOTING.md         # ✅ Panduan troubleshooting
├── BACKUP_GUIDE.md                # ✅ Panduan ini
├── README.md                      # ✅ Updated dengan backup section
└── DOCS_HUB.md                    # ✅ Updated dengan troubleshooting link
```

---

## Repository GitHub

**URL:** https://github.com/dedy45/livetik

**Branch:** main

**Status:** ✅ Siap untuk backup

---

## Next Steps

1. ✅ Jalankan `scripts\backup-github.bat`
2. ✅ Verify di GitHub: https://github.com/dedy45/livetik
3. ✅ Lanjutkan development dengan tenang

---

**Terakhir diupdate:** 2026-04-22
