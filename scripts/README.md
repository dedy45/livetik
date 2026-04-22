# 🛠️ Scripts

Utility scripts untuk development livetik.

## 📋 Available Scripts

### `install.bat`
Install semua dependencies (worker + controller)

```cmd
scripts\install.bat
```

**What it does:**
- ✅ Check UV dan pnpm installed
- ✅ Install Python worker dependencies (UV)
- ✅ Install Svelte controller dependencies (pnpm)
- ✅ Copy .env.example ke .env (jika belum ada)

---

### `dev.bat`
Run development server (worker + controller)

```cmd
scripts\dev.bat
```

**What it does:**
- ✅ Check dependencies installed
- ✅ Check .env file exists
- ✅ Start worker di terminal baru
- ✅ Start controller di terminal baru
- ✅ Open http://localhost:5173

---

### `test.bat`
Test installation dan dependencies

```cmd
scripts\test.bat
```

**What it does:**
- ✅ Test UV installed
- ✅ Test pnpm installed
- ✅ Test worker dependencies
- ✅ Test controller dependencies
- ✅ Test .env file exists

---

### `clean.bat`
Clean/reset installation

```cmd
scripts\clean.bat
```

**What it does:**
- ❌ Remove .venv (Python virtual environment)
- ❌ Remove node_modules
- ❌ Remove .svelte-kit
- ❌ Remove logs/
- ❌ Remove obs/
- ❌ Remove _out.mp3

**Use when:**
- Dependencies corrupted
- Need fresh install
- Switching branches

---

### `init-github.bat`
Initialize dan push ke GitHub

```cmd
scripts\init-github.bat
```

**What it does:**
- ✅ Initialize git repository
- ✅ Add all files
- ✅ Create initial commit
- ✅ Add remote origin
- ✅ Push to GitHub

---

## 🔄 Typical Workflow

### First Time Setup

```cmd
REM 1. Install dependencies
scripts\install.bat

REM 2. Configure .env
notepad .env

REM 3. Test installation
scripts\test.bat

REM 4. Run development
scripts\dev.bat
```

### Daily Development

```cmd
REM Start development server
scripts\dev.bat
```

### When Dependencies Change

```cmd
REM Clean and reinstall
scripts\clean.bat
scripts\install.bat
```

### Push to GitHub

```cmd
REM First time
scripts\init-github.bat

REM Regular updates
git add .
git commit -m "feat: add feature"
git push origin main
```

---

## 🐛 Troubleshooting

### Script not working

```cmd
REM Run from project root
cd C:\Users\dedy\Documents\A-interiorhack\livetik
scripts\install.bat
```

### Dependencies error

```cmd
REM Clean and reinstall
scripts\clean.bat
scripts\install.bat
scripts\test.bat
```

### Path issues

Scripts use `%~dp0` untuk resolve paths relatif ke script location.
Jangan pindahkan scripts ke folder lain.

---

## 📖 Script Details

### Path Resolution

All scripts use `%~dp0` untuk resolve paths:
- `%~dp0` = Directory where script is located
- `%~dp0..` = Parent directory (project root)
- `%~dp0..\apps\worker` = Worker directory

### Error Handling

All scripts:
- ✅ Check prerequisites
- ✅ Validate paths exist
- ✅ Return proper exit codes
- ✅ Show clear error messages
- ✅ Pause before exit (untuk baca error)

### Directory Changes

Scripts use `pushd/popd` instead of `cd`:
- `pushd` = Change directory dan save previous
- `popd` = Return to previous directory
- Lebih reliable untuk nested operations

---

**Last Updated**: 2026-04-22
