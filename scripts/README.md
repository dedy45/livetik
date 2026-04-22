# 🛠️ Scripts

Utility scripts untuk development livetik.

## 📋 Available Scripts

### Development

#### `install.bat`
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

#### `dev.bat`
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

### Health & Monitoring

#### `health-check.bat` ⭐ NEW
**Comprehensive system diagnostics** - 10 categories, 40+ checks

```cmd
scripts\health-check.bat
```

**What it checks:**
1. ✅ Environment & dependencies (Python, UV, Node, pnpm, FFmpeg)
2. ✅ Project structure (worker, controller, docs)
3. ✅ Configuration files (.env, pyproject.toml, package.json)
4. ✅ Worker dependencies (TikTokLive, openai, edge-tts, FastAPI, websockets)
5. ✅ Controller dependencies (SvelteKit, Tailwind, .svelte-kit)
6. ✅ Runtime directories (logs/, obs/, persona.md)
7. ✅ Network ports (8765, 8766, 5173)
8. ✅ Git repository (branch, remote, status)
9. ✅ External services (API keys, internet)
10. ✅ System resources (disk, memory)

**Output:**
- Health score (0-100%)
- Status: HEALTHY / DEGRADED / CRITICAL
- Detailed error messages with fix suggestions
- References to ERROR_HANDLING.md for each error type

---

#### `monitor-runtime.bat` ⭐ NEW
**Runtime monitoring** - Monitor system while running

```cmd
scripts\monitor-runtime.bat
```

**What it monitors:**
1. ✅ Process status (worker & controller PIDs)
2. ✅ Port status (8765 WebSocket, 8766 REST, 5173 UI)
3. ✅ Runtime files (obs/last_reply.txt, logs, persona.md)
4. ✅ Connectivity (REST API, WebSocket, internet)
5. ✅ Recent errors (from log files)

**Output:**
- Overall status: HEALTHY / DEGRADED / PARTIAL / STOPPED
- Quick links to controller pages
- Error codes mapped to ERROR_HANDLING.md

---

### Testing

#### `test.bat`
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

### Backup & Maintenance

#### `backup-github.bat`
Automated backup to GitHub

```cmd
scripts\backup-github.bat
```

**What it does:**
- ✅ Check Git status
- ✅ Add all changes
- ✅ Commit with timestamp
- ✅ Pull from remote (handle conflicts)
- ✅ Push to GitHub

---

#### `fix-svelte-tsconfig.bat`
Fix SvelteKit TypeScript warnings

```cmd
scripts\fix-svelte-tsconfig.bat
```

**What it does:**
- ✅ Check node_modules
- ✅ Run svelte-kit sync
- ✅ Generate .svelte-kit/tsconfig.json
- ✅ Verify results

---

#### `fix-all.bat`
Run all fixes (tsconfig + backup)

```cmd
scripts\fix-all.bat
```

**What it does:**
- ✅ Fix SvelteKit tsconfig
- ✅ Backup to GitHub

---

#### `clean.bat`
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

### GitHub Setup

#### `init-github.bat`
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

REM 3. Run health check
scripts\health-check.bat

REM 4. Test installation
scripts\test.bat

REM 5. Run development
scripts\dev.bat
```

### Daily Development

```cmd
REM 1. Check system health
scripts\health-check.bat

REM 2. Start development server
scripts\dev.bat

REM 3. Monitor runtime (in another terminal)
scripts\monitor-runtime.bat
```

### Before Going Live

```cmd
REM 1. Full health check
scripts\health-check.bat

REM 2. Verify all systems
scripts\monitor-runtime.bat

REM 3. Start worker & controller
scripts\dev.bat

REM 4. Open controller UI
start http://localhost:5173
```

### When Dependencies Change

```cmd
REM Clean and reinstall
scripts\clean.bat
scripts\install.bat
scripts\health-check.bat
```

### Troubleshooting Errors

```cmd
REM 1. Check health
scripts\health-check.bat

REM 2. Monitor runtime
scripts\monitor-runtime.bat

REM 3. Check error handling docs
notepad docs\ERROR_HANDLING.md
notepad docs\TROUBLESHOOTING.md
```

### Push to GitHub

```cmd
REM First time
scripts\init-github.bat

REM Regular updates
scripts\backup-github.bat

REM Or manual
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

All scripts use `%~dp0` and absolute paths untuk resolve paths:
- `%~dp0` = Directory where script is located (with trailing backslash)
- `%SCRIPT_DIR%` = `%~dp0` (script directory)
- `%PROJECT_ROOT%` = `%SCRIPT_DIR%..` (parent directory)
- `%WORKER_DIR%` = `%PROJECT_ROOT%\apps\worker`
- `%CONTROLLER_DIR%` = `%PROJECT_ROOT%\apps\controller`

Scripts use `cd /d` untuk change directory dengan drive letter support.

### Error Handling

All scripts:
- ✅ Check prerequisites (UV, pnpm, git)
- ✅ Validate paths exist before operations
- ✅ Return proper exit codes
- ✅ Show clear error messages
- ✅ Pause before exit (untuk baca error)
- ✅ Use `setlocal enabledelayedexpansion` untuk variable handling

---

**Last Updated**: 2026-04-22
