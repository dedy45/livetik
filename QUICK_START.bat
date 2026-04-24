@echo off
REM ============================================================
REM QUICK START SCRIPT - livetik GO-LIVE
REM ============================================================
echo.
echo ========================================
echo   livetik Quick Start
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "apps\worker" (
    echo ERROR: Must run from livetik root directory
    echo Current: %CD%
    pause
    exit /b 1
)

echo [1/5] Checking .env configuration...
if not exist ".env" (
    echo ERROR: .env not found
    echo Run: copy .env.example .env
    pause
    exit /b 1
)

findstr /C:"CARTESIA_API_KEYS" .env >nul
if errorlevel 1 (
    echo ERROR: CARTESIA_API_KEYS not set in .env
    pause
    exit /b 1
)
echo     ✓ .env exists and has Cartesia keys

echo.
echo [2/5] Checking audio library status...
type apps\worker\static\audio_library\index.json | findstr /C:"\"clips\":[]" >nul
if not errorlevel 1 (
    echo     ⚠ Audio library EMPTY - clips: []
    echo.
    echo     BLOCKER: Audio library must be generated first
    echo.
    echo     Run this command:
    echo     scripts\gen_audio_library.bat
    echo.
    echo     Estimated time: 8-12 minutes
    echo     This will generate 108 audio clips via Cartesia API
    echo.
    pause
    exit /b 1
) else (
    echo     ✓ Audio library has clips
)

echo.
echo [3/5] Checking Python environment...
where uv >nul 2>&1
if errorlevel 1 (
    echo ERROR: uv not found in PATH
    echo Install: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)
echo     ✓ uv found

echo.
echo [4/5] Checking Node.js environment...
where pnpm >nul 2>&1
if errorlevel 1 (
    echo ERROR: pnpm not found in PATH
    echo Install: npm install -g pnpm
    pause
    exit /b 1
)
echo     ✓ pnpm found

echo.
echo [5/5] All checks passed!
echo.
echo ========================================
echo   Ready to start services
echo ========================================
echo.
echo Open 3 terminals and run:
echo.
echo Terminal 1 (Worker):
echo   cd apps\worker
echo   uv sync
echo   uv run python -m banghack
echo.
echo Terminal 2 (Controller):
echo   cd apps\controller
echo   pnpm install
echo   pnpm dev
echo.
echo Terminal 3 (Health Check):
echo   curl http://localhost:8766/health
echo   Open http://localhost:5173
echo.
echo ========================================
pause
