# 🐙 09 · GitHub - Setup & Sync Guide

> **Canonical**: panduan lengkap setup dan sinkronisasi repository ke GitHub sebagai backup.

---

## 🚀 Quick Setup

### Windows

```cmd
scripts\init-github.bat
```

Script akan:
1. ✅ Initialize git repository
2. ✅ Add all files
3. ✅ Create initial commit
4. ✅ Add remote origin
5. ✅ Push to GitHub

## 📋 Prerequisites

- ✅ Git installed
- ✅ GitHub account
- ✅ Repository created: https://github.com/dedy45/livetik

## 🔧 Manual Setup

Jika prefer manual atau script gagal:

```cmd
REM 1. Initialize
git init

REM 2. Add files
git add .

REM 3. Commit
git commit -m "chore: initial commit - complete project structure"

REM 4. Add remote
git remote add origin https://github.com/dedy45/livetik.git

REM 5. Set main branch
git branch -M main

REM 6. Push
git push -u origin main
```

## 🔐 Authentication

### Option 1: Personal Access Token (Recommended)

1. **Generate Token**:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control)
   - Copy token

2. **Use Token as Password**:
   ```cmd
   git push -u origin main
   Username: dedy45
   Password: <paste-your-token>
   ```

3. **Cache Credentials** (Windows):
   ```cmd
   git config --global credential.helper wincred
   ```

### Option 2: SSH Key

1. **Generate SSH Key**:
   ```cmd
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. **Add to GitHub**:
   - Copy public key: `type %USERPROFILE%\.ssh\id_ed25519.pub`
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Paste key

3. **Change Remote to SSH**:
   ```cmd
   git remote set-url origin git@github.com:dedy45/livetik.git
   ```

## 🔄 Daily Sync Workflow

### Push Changes

```cmd
REM 1. Check status
git status

REM 2. Add changes
git add .

REM 3. Commit with message
git commit -m "docs: update documentation"

REM 4. Push to GitHub
git push origin main
```

### Pull Changes

```cmd
REM Pull latest from another device
git pull origin main
```

## 📝 Commit Message Convention

Gunakan **Conventional Commits**:

| Type | Usage | Example |
|------|-------|---------|
| `feat` | New feature | `feat(worker): add TikTok adapter` |
| `fix` | Bug fix | `fix(controller): resolve WS connection` |
| `docs` | Documentation | `docs: update PRD` |
| `chore` | Maintenance | `chore: update dependencies` |
| `refactor` | Code refactor | `refactor(core): simplify queue` |
| `test` | Tests | `test(guardrail): add test cases` |

### Examples

```cmd
REM Simple
git commit -m "docs: update README"

REM With scope
git commit -m "feat(worker): add Claude fallback"

REM With body
git commit -m "fix(controller): resolve WebSocket issue

Added exponential backoff retry logic.
Fixes #42"
```

## 📦 What Gets Pushed

### ✅ Included

- Documentation (docs/)
- Source code (apps/)
- Configuration files
- Scripts
- VSCode settings
- README, LICENSE

### ❌ Excluded (.gitignore)

- .env (secrets)
- .venv/ (Python virtual environment)
- node_modules/ (Node dependencies)
- __pycache__/ (Python cache)
- logs/ (log files)
- obs/ (OBS bridge files)

## 🛠️ Troubleshooting

### Error: "remote origin already exists"

```cmd
git remote remove origin
git remote add origin https://github.com/dedy45/livetik.git
```

### Error: "failed to push some refs"

```cmd
git pull origin main --rebase
git push origin main
```

### Error: "Authentication failed"

Use Personal Access Token instead of password (see Authentication section)

### Undo Last Commit (Keep Changes)

```cmd
git reset --soft HEAD~1
```

### Discard Local Changes

```cmd
REM Single file
git checkout -- <file>

REM All files
git reset --hard HEAD
```

## 🌿 Branching Strategy

### Simple (Solo Development)

```cmd
REM Work directly on main
git add .
git commit -m "feat: add new feature"
git push origin main
```

### Feature Branches (Team)

```cmd
REM Create feature branch
git checkout -b feat/new-feature

REM Work on feature
git add .
git commit -m "feat: implement feature"
git push origin feat/new-feature

REM Merge to main
git checkout main
git merge feat/new-feature
git push origin main
```

## 📊 Repository Settings

### Recommended Settings

1. **Visibility**: Private (untuk development)
2. **Features**:
   - ✅ Issues (tracking bugs)
   - ❌ Wiki (gunakan docs/)
   - ❌ Projects (gunakan PLAN.md)
   - ❌ Actions (no CI/CD untuk backup)

### Configure on GitHub

1. Go to: https://github.com/dedy45/livetik/settings
2. **General**:
   - Description: "TikTok Live AI Co-Pilot - Bang Hack"
   - Topics: `tiktok`, `ai`, `python`, `svelte`
3. **Features**:
   - Disable Actions
   - Disable Wiki

## 🔍 Verify Push

### Check GitHub

Visit: https://github.com/dedy45/livetik

### Check Locally

```cmd
REM View remote
git remote -v

REM View log
git log --oneline --graph

REM View status
git status
```

## 📚 Best Practices

1. **Commit sering** - Jangan tunggu terlalu banyak perubahan
2. **Pesan jelas** - Gunakan conventional commits
3. **Pull sebelum push** - Hindari conflicts
4. **Review changes** - Gunakan `git diff` sebelum commit
5. **Jangan commit .env** - Sudah di .gitignore

## 📖 Quick Reference

```cmd
REM Status
git status

REM Add all
git add .

REM Commit
git commit -m "message"

REM Push
git push origin main

REM Pull
git pull origin main

REM View log
git log --oneline --graph

REM View diff
git diff
```

---

**Repository**: https://github.com/dedy45/livetik
