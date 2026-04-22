@echo off
setlocal enabledelayedexpansion

REM ========================================
REM  LIVETIK — HEALTH CHECK (Python-based)
REM  Runs: apps/worker/scripts/health_check.py
REM  Checks: ffplay, 9router, LLM, Cartesia, edge-tts, WS commands
REM ========================================

cd /d "%~dp0.."

echo.
echo ========================================
echo  Livetik Health Check
echo ========================================
echo.

REM Check worker venv exists
if not exist "apps\worker\.venv" (
    echo [ERROR] Worker dependencies not installed.
    echo         Run: scripts\install.bat
    echo.
    pause
    exit /b 1
)

REM Check health_check.py exists
if not exist "apps\worker\scripts\health_check.py" (
    echo [ERROR] health_check.py not found at apps\worker\scripts\health_check.py
    echo.
    pause
    exit /b 1
)

REM Run health check from worker directory (so relative imports work)
echo Running health check...
echo.
cd apps\worker
uv run python scripts\health_check.py
set EXIT_CODE=!errorlevel!
cd ..\..

echo.
if !EXIT_CODE! equ 0 (
    echo ========================================
    echo  Result: READY
    echo ========================================
) else (
    echo ========================================
    echo  Result: NOT READY — fix errors above
    echo ========================================
    echo.
    echo  Quick fixes:
    echo    Kill stale processes : scripts\kill.bat
    echo    Start worker         : scripts\dev.bat
    echo    Install deps         : scripts\install.bat
)

echo.
pause
endlocal
