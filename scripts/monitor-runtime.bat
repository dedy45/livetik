@echo off
REM ========================================
REM LIVETIK RUNTIME MONITOR
REM Monitor worker & controller saat berjalan
REM Based on: docs/ERROR_HANDLING.md
REM ========================================

setlocal enabledelayedexpansion

cd /d "%~dp0.."

echo.
echo ========================================
echo   LIVETIK RUNTIME MONITOR
echo ========================================
echo.

REM ========================================
REM 1. CHECK PROCESSES
REM ========================================
echo [1/5] PROCESS STATUS
echo ----------------------------------------

REM Check Python worker
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
set ERR=!errorlevel!
if !ERR! equ 0 (
    echo [RUNNING] Python worker detected
    for /f "tokens=2" %%p in ('tasklist /FI "IMAGENAME eq python.exe" /NH 2^>nul') do (
        echo           PID: %%p
        goto :worker_found
    )
    :worker_found
) else (
    echo [STOPPED] Python worker not running
    echo           Start: cd apps\worker ^&^& uv run python -m banghack
)

REM Check Node controller
tasklist /FI "IMAGENAME eq node.exe" 2>NUL | find /I /N "node.exe">NUL
set ERR=!errorlevel!
if !ERR! equ 0 (
    echo [RUNNING] Node.js controller detected
) else (
    echo [STOPPED] Node.js controller not running
    echo           Start: cd apps\controller ^&^& pnpm dev
)

echo.

REM ========================================
REM 2. CHECK PORTS
REM ========================================
echo [2/5] PORT STATUS
echo ----------------------------------------

REM WebSocket port 8765
netstat -ano | findstr ":8765" >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    echo [LISTENING] Port 8765 ^(WebSocket IPC^)
    for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8765" 2^>nul') do (
        echo              PID: %%p
        goto :ws_found
    )
    :ws_found
) else (
    echo [CLOSED] Port 8765 - Worker WebSocket not listening
    echo         Error: IPC_WS_DISCONNECT
)

REM REST API port 8766
netstat -ano | findstr ":8766" >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    echo [LISTENING] Port 8766 ^(REST API^)
) else (
    echo [CLOSED] Port 8766 - Worker REST API not listening
    echo         Error: IPC_HTTP_BIND_FAIL
)

REM Vite dev port 5173
netstat -ano | findstr ":5173" >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    echo [LISTENING] Port 5173 ^(Controller UI^)
    echo              URL: http://localhost:5173
) else (
    echo [CLOSED] Port 5173 - Controller not running
)

echo.

REM ========================================
REM 3. CHECK FILES
REM ========================================
echo [3/5] RUNTIME FILES
echo ----------------------------------------

REM Check OBS bridge file
if exist "obs\last_reply.txt" (
    echo [EXISTS] obs\last_reply.txt
    for %%F in ("obs\last_reply.txt") do (
        echo          Size: %%~zF bytes
        echo          Modified: %%~tF
    )
) else (
    echo [MISSING] obs\last_reply.txt - No replies sent yet or OBS_WRITE_FAIL
)

REM Check latest log
if exist "logs" (
    set LASTLOG=
    for /f %%f in ('dir /b /od logs\*.log 2^>nul') do set LASTLOG=%%f
    if defined LASTLOG (
        echo [EXISTS] logs\!LASTLOG!
        for %%F in ("logs\!LASTLOG!") do (
            echo          Size: %%~zF bytes
            echo          Modified: %%~tF
        )
    ) else (
        echo [MISSING] No log files - Worker not started yet
    )
) else (
    echo [MISSING] logs/ directory
)

REM Check persona
if exist "apps\worker\src\banghack\config\persona.md" (
    echo [EXISTS] persona.md
) else (
    echo [MISSING] persona.md - Using default persona
)

echo.

REM ========================================
REM 4. CHECK CONNECTIVITY
REM ========================================
echo [4/5] CONNECTIVITY
echo ----------------------------------------

REM Test REST API
echo Testing REST API...
curl -s -o nul -w "%%{http_code}" http://localhost:8766/api/status >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    echo [OK] REST API responding
) else (
    echo [FAIL] REST API not responding
    echo       Error: Worker not running or IPC_HTTP_BIND_FAIL
)

REM Test WebSocket (basic check)
echo Testing WebSocket...
powershell -Command "try { $ws = New-Object System.Net.WebSockets.ClientWebSocket; $ct = New-Object System.Threading.CancellationToken; $uri = [System.Uri]'ws://localhost:8765'; $task = $ws.ConnectAsync($uri, $ct); $task.Wait(1000); if ($ws.State -eq 'Open') { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    echo [OK] WebSocket accepting connections
) else (
    echo [FAIL] WebSocket not accepting connections
    echo       Error: Worker not running or IPC_WS_DISCONNECT
)

REM Test internet
echo Testing internet...
ping -n 1 8.8.8.8 >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 (
    echo [OK] Internet connectivity
) else (
    echo [FAIL] No internet connection
    echo       Errors: TIKTOK_DISCONNECT, LLM_TIMEOUT, TTS_NETWORK
)

echo.

REM ========================================
REM 5. RECENT ERRORS ^(from logs^)
REM ========================================
echo [5/5] RECENT ERRORS
echo ----------------------------------------

if exist "logs" (
    set LASTLOG=
    for /f %%f in ('dir /b /od logs\*.log 2^>nul') do set LASTLOG=%%f
    if defined LASTLOG (
        echo Checking logs\!LASTLOG! for errors...
        echo.
        
        REM Find last 5 error lines
        findstr /C:"ERROR" /C:"FAIL" /C:"CRITICAL" "logs\!LASTLOG!" 2>nul | more +0 | findstr /N "^" | findstr "^[1-5]:" 2>nul
        set ERR=!errorlevel!
        
        if !ERR! neq 0 (
            echo [CLEAN] No recent errors in log
        )
    ) else (
        echo [INFO] No log files found
    )
) else (
    echo [INFO] logs/ directory not found
)

echo.
echo.

REM ========================================
REM SUMMARY
REM ========================================
echo ========================================
echo   RUNTIME STATUS
echo ========================================
echo.

REM Quick status check
set STATUS=UNKNOWN
set WORKER_OK=0
set CONTROLLER_OK=0
set API_OK=0

tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
set ERR=!errorlevel!
if !ERR! equ 0 set WORKER_OK=1

tasklist /FI "IMAGENAME eq node.exe" 2>NUL | find /I /N "node.exe">NUL
set ERR=!errorlevel!
if !ERR! equ 0 set CONTROLLER_OK=1

netstat -ano | findstr ":8766" >nul 2>&1
set ERR=!errorlevel!
if !ERR! equ 0 set API_OK=1

if !WORKER_OK!==1 (
    if !CONTROLLER_OK!==1 (
        if !API_OK!==1 (
            set STATUS=HEALTHY
        ) else (
            set STATUS=DEGRADED
        )
    ) else (
        set STATUS=PARTIAL
    )
) else (
    set STATUS=STOPPED
)

echo Overall Status: [!STATUS!]
echo.

if "!STATUS!"=="HEALTHY" (
    echo All systems operational
    echo.
    echo Access controller: http://localhost:5173
    echo.
    echo Pages:
    echo   - Dashboard:    http://localhost:5173/
    echo   - Live Monitor: http://localhost:5173/live
    echo   - Errors:       http://localhost:5173/errors
    echo   - Persona:      http://localhost:5173/persona
    echo   - Config:       http://localhost:5173/config
    echo   - Cost:         http://localhost:5173/cost
)

if "!STATUS!"=="DEGRADED" (
    echo Worker running but API not responding
    echo Check worker logs for errors
)

if "!STATUS!"=="PARTIAL" (
    echo Worker running but controller not started
    echo Start controller: cd apps\controller ^&^& pnpm dev
)

if "!STATUS!"=="STOPPED" (
    echo System not running
    echo Start with: scripts\dev.bat
)

echo.
echo ========================================
echo.
echo Refresh: Run this script again
echo Stop all: Ctrl+C in terminal windows
echo.
echo For error details, see:
echo   - docs\ERROR_HANDLING.md
echo   - logs\*.log
echo.
echo ========================================
echo.

pause
