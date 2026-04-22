# Troubleshooting Guide - Livetik

## Masalah Git & GitHub

### Error: "src refspec main does not match any"

**Penyebab:**
- Branch lokal bernama `master`, tapi mencoba push ke `main`
- Remote `origin` belum dikonfigurasi

**Solusi:**

```bash
# 1. Tambahkan remote origin
git remote add origin https://github.com/dedy45/livetik.git

# 2. Ubah branch master ke main
git branch -M main

# 3. Pull dari remote (jika repo sudah ada di GitHub)
git pull origin main --allow-unrelated-histories --no-edit

# 4. Push ke GitHub
git push -u origin main
```

**Atau gunakan script otomatis:**
```bash
cd livetik/scripts
backup-github.bat
```

---

## Masalah TypeScript & SvelteKit

### Warning: "Cannot find base config file ./.svelte-kit/tsconfig.json"

**Penyebab:**
- File `.svelte-kit/tsconfig.json` belum di-generate
- SvelteKit perlu di-sync atau di-build dulu

**Solusi:**

```bash
cd apps/controller

# Opsi 1: Sync SvelteKit (tercepat)
pnpm exec svelte-kit sync

# Opsi 2: Jalankan dev server (akan auto-generate)
pnpm run dev

# Opsi 3: Build project
pnpm run build
```

**Atau gunakan script otomatis:**
```bash
cd livetik/scripts
fix-svelte-tsconfig.bat
```

**Penjelasan:**
- SvelteKit generate file tsconfig otomatis di folder `.svelte-kit/`
- File ini berisi konfigurasi TypeScript yang disesuaikan dengan struktur project
- File ini di-gitignore karena auto-generated

---

## Masalah 404 Favicon

### Error: "[404] GET /favicon.png"

**Penyebab:**
- Browser mencari favicon tapi file tidak ada
- Ini warning biasa, tidak mempengaruhi fungsi aplikasi

**Solusi (opsional):**

1. Tambahkan favicon di `apps/controller/static/favicon.png`
2. Atau tambahkan di `apps/controller/src/app.html`:

```html
<link rel="icon" href="/favicon.png" />
```

---

## Script Perbaikan Otomatis

### 1. Perbaiki Semua Masalah Sekaligus

```bash
cd livetik/scripts
fix-all.bat
```

Script ini akan:
1. Generate SvelteKit tsconfig
2. Backup ke GitHub

### 2. Hanya Perbaiki SvelteKit

```bash
cd livetik/scripts
fix-svelte-tsconfig.bat
```

### 3. Hanya Backup ke GitHub

```bash
cd livetik/scripts
backup-github.bat
```

---

## Checklist Debugging

Sebelum backup ke GitHub, pastikan:

- [ ] Git sudah terinstall
- [ ] Remote origin sudah dikonfigurasi
- [ ] Branch sudah diubah ke `main`
- [ ] Tidak ada konflik merge
- [ ] Credentials GitHub sudah dikonfigurasi

Untuk SvelteKit:

- [ ] Node.js sudah terinstall
- [ ] pnpm sudah terinstall
- [ ] Dependencies sudah di-install (`pnpm install`)
- [ ] `.svelte-kit/` folder sudah di-generate

---

## Perintah Debugging Berguna

### Git

```bash
# Cek status
git status

# Cek branch
git branch -a

# Cek remote
git remote -v

# Cek log
git log --oneline -5

# Reset jika ada masalah
git reset --soft HEAD~1
```

### SvelteKit

```bash
# Cek versi
pnpm --version
node --version

# Clean install
rm -rf node_modules .svelte-kit
pnpm install

# Cek struktur
ls -la .svelte-kit/
```

---

## Kontak & Support

Jika masalah masih berlanjut:

1. Cek log error lengkap
2. Cek dokumentasi di `docs/`
3. Buat issue di GitHub repository

---

**Terakhir diupdate:** 2026-04-22
