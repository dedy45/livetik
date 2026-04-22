@echo off
REM ========================================
REM LIVETIK HEALTH CHECK - Comprehensive System Diagnostics
REM Based on: docs/ARCHITECTURE.md, docs/ERROR_HANDLING.md
REM ========================================

setlocal enabledelayedexpansion

cd /d "%~dp0.."

echo.
echo ========================================
echo   LIVETIK HEALTH CHECK v1.0
echo ========================================
echo.
echo Checking all system components...
echo.

REM Initialize counters
set PASS=0
set WARN=0
set FAIL=0
set TOTAL=0

REM ========================================
REM 1. ENVIRONMENT ^& DEPENDENCIES
REM ========================================
echo [1/10] ENVIRONMENT ^& DEPENDENCIES
echo ----------------------------------------

REM Check Python
set /a TOTAL+=1
python --version >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
    echo [PASS] Python !PYVER! detected
    set /a PASS+=1
) else (
    echo [FAIL] Python not found - Required: Python 3.11+
    set /a FAIL+=1
)

REM Check UV
set /a TOTAL+=1
uv --version >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    for /f "tokens=2" %%v in ('uv --version 2^>^&1') do set UVVER=%%v
    echo [PASS] UV !UVVER! detected
    set /a PASS+=1
) else (
    echo [FAIL] UV not found - Install: https://github.com/astral-sh/uv
    set /a FAIL+=1
)

REM Check Node.js
set /a TOTAL+=1
node --version >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    for /f %%v in ('node --version 2^>^&1') do set NODEVER=%%v
    echo [PASS] Node.js !NODEVER! detected
    set /a PASS+=1
) else (
    echo [FAIL] Node.js not found - Required: Node.js 20+
    set /a FAIL+=1
)

REM Check pnpm
set /a TOTAL+=1
where pnpm >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    for /f "delims=" %%v in ('pnpm --version 2^>^&1') do set PNPMVER=%%v
    echo [PASS] pnpm !PNPMVER! detected
    set /a PASS+=1
) else (
    echo [FAIL] pnpm not found - Install: npm install -g pnpm
    set /a FAIL+=1
)

REM Check FFmpeg
set /a TOTAL+=1
ffplay -version >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    echo [PASS] FFmpeg/ffplay detected
    set /a PASS+=1
) else (
    echo [WARN] FFmpeg not found - TTS audio will fail ^(TTS_FFPLAY_NOT_FOUND^)
    echo        Install: https://ffmpeg.org/download.html
    set /a WARN+=1
)

echo.

REM ========================================
REM 2. PROJECT STRUCTURE
REM ========================================
echo [2/10] PROJECT STRUCTURE
echo ----------------------------------------

REM Check worker directory
set /a TOTAL+=1
if exist "apps\worker\src\banghack" (
    echo [PASS] Worker directory structure OK
    set /a PASS+=1
) else (
    echo [FAIL] Worker directory missing: apps\worker\src\banghack
    set /a FAIL+=1
)

REM Check controller directory
set /a TOTAL+=1
if exist "apps\controller\src" (
    echo [PASS] Controller directory structure OK
    set /a PASS+=1
) else (
    echo [FAIL] Controller directory missing: apps\controller\src
    set /a FAIL+=1
)

REM Check docs
set /a TOTAL+=1
if exist "docs\ARCHITECTURE.md" (
    echo [PASS] Documentation present
    set /a PASS+=1
) else (
    echo [WARN] Documentation incomplete
    set /a WARN+=1
)

echo.

REM ========================================
REM 3. CONFIGURATION FILES
REM ========================================
echo [3/10] CONFIGURATION FILES
echo ----------------------------------------

REM Check .env
set /a TOTAL+=1
if exist ".env" (
    echo [PASS] .env file exists
    set /a PASS+=1
    
    REM Check critical env vars
    set /a TOTAL+=1
    findstr /C:"DEEPSEEK_API_KEY" .env >nul 2>&1
    set ERR=!errorlevel!
    if !ERR! equ 0 (
        echo [PASS] DEEPSEEK_API_KEY configured
        set /a PASS+=1
    ) else (
        echo [FAIL] DEEPSEEK_API_KEY missing - LLM will fail ^(LLM_INVALID_KEY^)
        set /a FAIL+=1
    )
    
    set /a TOTAL+=1
    findstr /C:"TIKTOK_USERNAME" .env >nul 2>&1
    set ERR=!errorlevel!
    if !ERR! equ 0 (
        echo [PASS] TIKTOK_USERNAME configured
        set /a PASS+=1
    ) else (
        echo [WARN] TIKTOK_USERNAME missing - Set target room
        set /a WARN+=1
    )
) else (
    echo [FAIL] .env file missing - Copy from .env.example
    set /a FAIL+=1
    set /a TOTAL+=2
    set /a FAIL+=2
)

REM Check pyproject.toml
set /a TOTAL+=1
if exist "apps\worker\pyproject.toml" (
    echo [PASS] Worker pyproject.toml exists
    set /a PASS+=1
) else (
    echo [FAIL] Worker pyproject.toml missing
    set /a FAIL+=1
)

REM Check package.json
set /a TOTAL+=1
if exist "apps\controller\package.json" (
    echo [PASS] Controller package.json exists
    set /a PASS+=1
) else (
    echo [FAIL] Controller package.json missing
    set /a FAIL+=1
)

echo.

REM ========================================
REM 4. WORKER DEPENDENCIES
REM ========================================
echo [4/10] WORKER DEPENDENCIES ^(Python^)
echo ----------------------------------------

set /a TOTAL+=1
if exist "apps\worker\.venv" (
    echo [PASS] Python virtual environment exists
    set /a PASS+=1
    
    REM Check critical packages
    pushd apps\worker
    
    set /a TOTAL+=1
    uv pip list 2>nul | findstr "TikTokLive" >nul 2>&1
    set ERR=!errorlevel!
    if !ERR! equ 0 (
        echo [PASS] TikTokLive installed
        set /a PASS+=1
    ) else (
        echo [FAIL] TikTokLive missing - Run: uv pip install TikTokLive
        set /a FAIL+=1
    )
    
    set /a TOTAL+=1
    uv pip list 2>nul | findstr "openai" >nul 2>&1
    set ERR=!errorlevel!
    if !ERR! equ 0 (
        echo [PASS] openai SDK installed
        set /a PASS+=1
    ) else (
        echo [FAIL] openai SDK missing - Run: uv pip install openai
        set /a FAIL+=1
    )
    
    set /a TOTAL+=1
    uv pip list 2>nul | findstr "edge-tts" >nul 2>&1
    set ERR=!errorlevel!
    if !ERR! equ 0 (
        echo [PASS] edge-tts installed
        set /a PASS+=1
    ) else (
        echo [FAIL] edge-tts missing - Run: uv pip install edge-tts
        set /a FAIL+=1
    )
    
    set /a TOTAL+=1
    uv pip list 2>nul | findstr "fastapi" >nul 2>&1
    set ERR=!errorlevel!
    if !ERR! equ 0 (
        echo [PASS] FastAPI installed
        set /a PASS+=1
    ) else (
        echo [FAIL] FastAPI missing - Run: uv pip install fastapi
        set /a FAIL+=1
    )
    
    set /a TOTAL+=1
    uv pip list 2>nul | findstr "websockets" >nul 2>&1
    set ERR=!errorlevel!
    if !ERR! equ 0 (
        echo [PASS] websockets installed
        set /a PASS+=1
    ) else (
        echo [FAIL] websockets missing - Run: uv pip install websockets
        set /a FAIL+=1
    )
    
    popd
) else (
    echo [FAIL] Python virtual environment missing - Run: scripts\install.bat
    set /a FAIL+=1
    set /a TOTAL+=5
    set /a FAIL+=5
)

echo.

REM ========================================
REM 5. CONTROLLER DEPENDENCIES
REM ========================================
echo [5/10] CONTROLLER DEPENDENCIES ^(Node.js^)
echo ----------------------------------------

set /a TOTAL+=1
if exist "apps\controller\node_modules" (
    echo [PASS] Node modules installed
    set /a PASS+=1
    
    REM Check SvelteKit
    set /a TOTAL+=1
    if exist "apps\controller\node_modules\@sveltejs\kit" (
        echo [PASS] SvelteKit installed
        set /a PASS+=1
    ) else (
        echo [FAIL] SvelteKit missing - Run: cd apps\controller ^&^& pnpm install
        set /a FAIL+=1
    )
    
    REM Check Tailwind
    set /a TOTAL+=1
    if exist "apps\controller\node_modules\tailwindcss" (
        echo [PASS] Tailwind CSS installed
        set /a PASS+=1
    ) else (
        echo [FAIL] Tailwind CSS missing - Run: cd apps\controller ^&^& pnpm install
        set /a FAIL+=1
    )
) else (
    echo [FAIL] Node modules missing - Run: cd apps\controller ^&^& pnpm install
    set /a FAIL+=1
    set /a TOTAL+=2
    set /a FAIL+=2
)

REM Check .svelte-kit
set /a TOTAL+=1
if exist "apps\controller\.svelte-kit\tsconfig.json" (
    echo [PASS] SvelteKit generated files OK
    set /a PASS+=1
) else (
    echo [WARN] SvelteKit not synced - Run: cd apps\controller ^&^& pnpm exec svelte-kit sync
    echo        Or start dev server to auto-generate
    set /a WARN+=1
)

echo.

REM ========================================
REM 6. RUNTIME DIRECTORIES
REM ========================================
echo [6/10] RUNTIME DIRECTORIES
echo ----------------------------------------

REM Check/create logs directory
set /a TOTAL+=1
if not exist "logs" mkdir logs 2>nul
if exist "logs" (
    echo [PASS] logs/ directory ready
    set /a PASS+=1
) else (
    echo [FAIL] Cannot create logs/ directory
    set /a FAIL+=1
)

REM Check/create obs directory
set /a TOTAL+=1
if not exist "obs" mkdir obs 2>nul
if exist "obs" (
    echo [PASS] obs/ directory ready
    set /a PASS+=1
) else (
    echo [FAIL] Cannot create obs/ directory - OBS bridge will fail ^(OBS_WRITE_FAIL^)
    set /a FAIL+=1
)

REM Check persona file
set /a TOTAL+=1
if exist "apps\worker\src\banghack\config\persona.md" (
    echo [PASS] Persona file exists
    set /a PASS+=1
) else (
    echo [WARN] Persona file missing - Create default persona.md
    set /a WARN+=1
)

echo.

REM ========================================
REM 7. NETWORK PORTS
REM ========================================
echo [7/10] NETWORK PORTS
echo ----------------------------------------

REM Check if ports are available
set /a TOTAL+=1
netstat -ano | findstr ":8765" >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    echo [WARN] Port 8765 ^(WebSocket^) already in use - May cause IPC_WS_DISCONNECT
    set /a WARN+=1
) else (
    echo [PASS] Port 8765 ^(WebSocket^) available
    set /a PASS+=1
)

set /a TOTAL+=1
netstat -ano | findstr ":8766" >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    echo [WARN] Port 8766 ^(REST API^) already in use - May cause IPC_HTTP_BIND_FAIL
    set /a WARN+=1
) else (
    echo [PASS] Port 8766 ^(REST API^) available
    set /a PASS+=1
)

set /a TOTAL+=1
netstat -ano | findstr ":5173" >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    echo [WARN] Port 5173 ^(Vite dev^) already in use
    set /a WARN+=1
) else (
    echo [PASS] Port 5173 ^(Vite dev^) available
    set /a PASS+=1
)

echo.

REM ========================================
REM 8. GIT REPOSITORY
REM ========================================
echo [8/10] GIT REPOSITORY
echo ----------------------------------------

set /a TOTAL+=1
git --version >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    echo [PASS] Git installed
    set /a PASS+=1
    
    REM Check if in git repo
    set /a TOTAL+=1
    git rev-parse --git-dir >nul 2>&1
    set ERR=!errorlevel!
    if !ERR! equ 0 (
        echo [PASS] Git repository initialized
        set /a PASS+=1
        
        REM Check remote
        set /a TOTAL+=1
        git remote -v | findstr "origin" >nul 2>&1
        set ERR=!errorlevel!
        if !ERR! equ 0 (
            echo [PASS] Git remote configured
            set /a PASS+=1
        ) else (
            echo [WARN] Git remote not configured - Run: scripts\backup-github.bat
            set /a WARN+=1
        )
        
        REM Check branch
        set /a TOTAL+=1
        for /f %%b in ('git branch --show-current 2^>nul') do set BRANCH=%%b
        if "!BRANCH!"=="main" (
            echo [PASS] On main branch
            set /a PASS+=1
        ) else (
            echo [WARN] Not on main branch ^(current: !BRANCH!^)
            set /a WARN+=1
        )
    ) else (
        echo [FAIL] Not a git repository
        set /a FAIL+=1
        set /a TOTAL+=2
        set /a FAIL+=2
    )
) else (
    echo [WARN] Git not installed - Backup will not work
    set /a WARN+=1
    set /a TOTAL+=3
    set /a WARN+=3
)

echo.

REM ========================================
REM 9. EXTERNAL SERVICES ^(API Keys^)
REM ========================================
echo [9/10] EXTERNAL SERVICES
echo ----------------------------------------

echo [INFO] Testing API connectivity...
echo.

REM Test DeepSeek API (if key exists)
set /a TOTAL+=1
if exist ".env" (
    findstr /C:"DEEPSEEK_API_KEY=sk-" .env >nul 2>&1
    set ERR=!errorlevel!
    if !ERR! equ 0 (
        echo [INFO] DeepSeek API key format OK ^(not testing actual call^)
        echo [PASS] DeepSeek configured
        set /a PASS+=1
    ) else (
        echo [FAIL] DeepSeek API key invalid format - Check .env
        set /a FAIL+=1
    )
) else (
    echo [FAIL] .env file missing
    set /a FAIL+=1
)

REM Test Anthropic API (optional)
set /a TOTAL+=1
if exist ".env" (
    findstr /C:"ANTHROPIC_API_KEY=sk-" .env >nul 2>&1
    set ERR=!errorlevel!
    if !ERR! equ 0 (
        echo [PASS] Anthropic API key configured ^(fallback ready^)
        set /a PASS+=1
    ) else (
        echo [WARN] Anthropic API key not configured - No LLM fallback ^(LLM_FALLBACK_FAIL risk^)
        set /a WARN+=1
    )
) else (
    echo [WARN] .env file missing
    set /a WARN+=1
)

REM Test internet connectivity
set /a TOTAL+=1
ping -n 1 8.8.8.8 >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    echo [PASS] Internet connectivity OK
    set /a PASS+=1
) else (
    echo [FAIL] No internet connection - All external services will fail
    echo        ^(TIKTOK_DISCONNECT, LLM_TIMEOUT, TTS_NETWORK^)
    set /a FAIL+=1
)

echo.

REM ========================================
REM 10. SYSTEM RESOURCES
REM ========================================
echo [10/10] SYSTEM RESOURCES
echo ----------------------------------------

REM Check disk space
set /a TOTAL+=1
for /f "tokens=3" %%a in ('dir /-c 2^>nul ^| findstr "bytes free"') do set FREESPACE=%%a
if defined FREESPACE (
    echo [PASS] Disk space available
    set /a PASS+=1
) else (
    echo [WARN] Cannot check disk space
    set /a WARN+=1
)

REM Check memory (basic)
set /a TOTAL+=1
wmic OS get FreePhysicalMemory /value >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    echo [PASS] System memory check OK
    set /a PASS+=1
) else (
    echo [WARN] Cannot check system memory
    set /a WARN+=1
)

echo.
echo.

REM ========================================
REM SUMMARY
REM ========================================
echo ========================================
echo   HEALTH CHECK SUMMARY
echo ========================================
echo.
echo Total Checks: !TOTAL!
echo [PASS] Passed: !PASS!
echo [WARN] Warnings: !WARN!
echo [FAIL] Failed: !FAIL!
echo.

REM Calculate health score
if !TOTAL! gtr 0 (
    set /a SCORE=^(!PASS! * 100^) / !TOTAL!
    echo Health Score: !SCORE!%%
) else (
    echo Health Score: N/A
)
echo.

if !FAIL! equ 0 (
    if !WARN! equ 0 (
        echo Status: [HEALTHY] All systems operational
        echo.
        echo Ready to start:
        echo   - Worker: cd apps\worker ^&^& uv run python -m banghack
        echo   - Controller: cd apps\controller ^&^& pnpm dev
        echo   - Or use: scripts\dev.bat
    ) else (
        echo Status: [DEGRADED] System operational with warnings
        echo.
        echo Review warnings above and fix if needed.
    )
) else (
    echo Status: [CRITICAL] System has failures
    echo.
    echo Fix critical issues above before starting.
    echo.
    echo Common fixes:
    echo   - Missing dependencies: scripts\install.bat
    echo   - Missing .env: copy .env.example .env
    echo   - Missing API keys: edit .env
)

echo.
echo ========================================
echo.
echo For detailed troubleshooting, see:
echo   - docs\TROUBLESHOOTING.md
echo   - docs\ERROR_HANDLING.md
echo   - docs\ARCHITECTURE.md
echo.
echo ========================================
echo.

pause
