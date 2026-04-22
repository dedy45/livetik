# ⚡ Quick Start Guide

Panduan setup `livetik` dalam 5 menit.

## 📋 Prerequisites

Pastikan sudah terinstall:

- ✅ **Python 3.11+** - [Download](https://www.python.org/downloads/)
- ✅ **UV** - Python package manager
- ✅ **Node.js 20+** - [Download](https://nodejs.org/)
- ✅ **pnpm** - Node package manager
- ✅ **Git** - Version control

### Install UV (Python Package Manager)

**Windows**:
```cmd
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/Mac**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install pnpm (Node Package Manager)

```cmd
npm install -g pnpm
```

## 🚀 Setup (3 Langkah)

### 1. Install Dependencies

```cmd
scripts\install.bat
```

Script ini akan:
- ✅ Install Python worker dependencies (UV)
- ✅ Install Svelte controller dependencies (pnpm)
- ✅ Copy .env.example ke .env (jika belum ada)

### 2. Configure Environment

Edit file `.env` dan isi API keys:

```env
TIKTOK_USERNAME=interiorhack.id
DEEPSEEK_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here  # Optional
```

**Cara dapat API Key**:
- DeepSeek: [platform.deepseek.com](https://platform.deepseek.com) → API Keys
- Anthropic: [console.anthropic.com](https://console.anthropic.com) → API Keys

### 3. Run Development Server

```cmd
scripts\dev.bat
```

Akan membuka 2 terminal windows:
- **Worker** - Python backend
- **Controller** - Svelte frontend di http://localhost:5173

## 🎯 Verification

### Test Installation

```cmd
scripts\test.bat
```

### Open Browser

**http://localhost:5173**

Anda akan melihat dashboard dengan status "Disconnected" (normal, karena belum Live)

## 📚 Next Steps

### Baca Dokumentasi

1. **[DOCS_HUB.md](DOCS_HUB.md)** - Peta semua dokumen
2. **[docs/PRD.md](docs/PRD.md)** - Apa yang dibangun
3. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Bagaimana sistem bekerja
4. **[docs/STRUCTURE.md](docs/STRUCTURE.md)** - Struktur folder detail

### Push ke GitHub

```cmd
scripts\init-github.bat
```

Lihat panduan lengkap: **[docs/GITHUB.md](docs/GITHUB.md)**

## 🐛 Troubleshooting

### UV command not found

Restart terminal atau tambahkan ke PATH:
- Windows: `C:\Users\<username>\.cargo\bin`

### pnpm command not found

```cmd
npm install -g pnpm
```

### Port 5173 already in use

```cmd
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Dependencies error

```cmd
REM Clean and reinstall
scripts\clean.bat
scripts\install.bat
```

### Test installation

```cmd
scripts\test.bat
```

## 📖 Documentation

- **[DOCS_HUB.md](DOCS_HUB.md)** - Index semua dokumentasi
- **[docs/PRD.md](docs/PRD.md)** - Product requirements
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture
- **[docs/GITHUB.md](docs/GITHUB.md)** - GitHub setup & sync
- **[docs/STRUCTURE.md](docs/STRUCTURE.md)** - Project structure

---

**Ready to code! 🚀**
