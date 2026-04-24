@echo off
REM livetik v0.4.6 — Quick Start (Windows)
REM Jalankan worker + controller dalam 2 window terpisah.

setlocal
cd /d %~dp0

echo ============================================
echo  livetik QUICK START
echo ============================================

REM 1. Cek prerequisites
where uv >nul 2>nul || (echo [ERROR] uv belum terinstall. Install: https://astral.sh/uv & pause & exit /b 1)
where pnpm >nul 2>nul || (echo [ERROR] pnpm belum terinstall. Install: npm i -g pnpm & pause & exit /b 1)

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
