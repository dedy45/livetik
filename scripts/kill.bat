@echo off
setlocal enabledelayedexpansion

REM ========================================
REM  LIVETIK — KILL ALL PROCESSES
REM  Stops: worker (python), controller (node/vite), port 8765/8766/5173
REM ========================================

echo.
echo ========================================
echo  Livetik — Kill All Processes
echo ========================================
echo.

set KILLED=0

REM ── 1. Kill by window title (started via dev.bat) ──────────────────────────
echo [1/5] Killing named windows (Livetik Worker / Livetik Controller)...
taskkill /FI "WINDOWTITLE eq Livetik Worker*" /F >nul 2>&1
if !errorlevel! equ 0 (
    echo       Killed: Livetik Worker window
    set /a KILLED+=1
)
taskkill /FI "WINDOWTITLE eq Livetik Controller*" /F >nul 2>&1
if !errorlevel! equ 0 (
    echo       Killed: Livetik Controller window
    set /a KILLED+=1
)

REM ── 2. Kill python processes running banghack ───────────────────────────────
echo [2/5] Killing python processes (banghack worker)...
for /f "tokens=2" %%p in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV /NH 2^>nul') do (
    set PID=%%~p
    wmic process where "ProcessId=!PID!" get CommandLine /value 2>nul | findstr /i "banghack" >nul 2>&1
    if !errorlevel! equ 0 (
        taskkill /PID !PID! /F >nul 2>&1
        echo       Killed: python PID !PID! (banghack)
        set /a KILLED+=1
    )
)

REM ── 3. Kill by port 8765 (WebSocket) ───────────────────────────────────────
echo [3/5] Freeing port 8765 (WebSocket)...
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":8765 " ^| findstr "LISTENING"') do (
    if not "%%p"=="" (
        taskkill /PID %%p /F >nul 2>&1
        echo       Killed PID %%p on port 8765
        set /a KILLED+=1
    )
)

REM ── 4. Kill by port 8766 (HTTP API) ────────────────────────────────────────
echo [4/5] Freeing port 8766 (HTTP API)...
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":8766 " ^| findstr "LISTENING"') do (
    if not "%%p"=="" (
        taskkill /PID %%p /F >nul 2>&1
        echo       Killed PID %%p on port 8766
        set /a KILLED+=1
    )
)

REM ── 5. Kill by port 5173 (Vite / Controller) ───────────────────────────────
echo [5/5] Freeing port 5173 (Vite dev server)...
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":5173 " ^| findstr "LISTENING"') do (
    if not "%%p"=="" (
        taskkill /PID %%p /F >nul 2>&1
        echo       Killed PID %%p on port 5173
        set /a KILLED+=1
    )
)

REM ── Wait for ports to release ───────────────────────────────────────────────
timeout /t 2 /nobreak >nul

REM ── Verify ports are free ───────────────────────────────────────────────────
echo.
echo ── Port Status After Kill ──────────────────────────────────────────────
netstat -ano | findstr ":8765 " | findstr "LISTENING" >nul 2>&1
if !errorlevel! equ 0 (echo   [WARN] Port 8765 still in use) else (echo   [OK]   Port 8765 free)

netstat -ano | findstr ":8766 " | findstr "LISTENING" >nul 2>&1
if !errorlevel! equ 0 (echo   [WARN] Port 8766 still in use) else (echo   [OK]   Port 8766 free)

netstat -ano | findstr ":5173 " | findstr "LISTENING" >nul 2>&1
if !errorlevel! equ 0 (echo   [WARN] Port 5173 still in use) else (echo   [OK]   Port 5173 free)

echo.
echo ========================================
if !KILLED! gtr 0 (
    echo  Done — Killed !KILLED! process(es)
) else (
    echo  Done — No processes were running
)
echo ========================================
echo.
echo  Ready to restart:
echo    scripts\dev.bat       — start worker + controller
echo    scripts\health.bat    — run health check
echo.

endlocal
