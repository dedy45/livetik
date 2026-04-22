@echo off
setlocal enabledelayedexpansion

REM Clean script untuk reset instalasi
echo.
echo ========================================
echo  Cleaning Livetik Installation
echo ========================================
echo.
echo This will remove:
echo   - Python virtual environment (.venv)
echo   - Node modules
echo   - Build artifacts
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo Cancelled.
    pause
    exit /b 0
)

REM Get absolute paths
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "WORKER_DIR=%PROJECT_ROOT%\apps\worker"
set "CONTROLLER_DIR=%PROJECT_ROOT%\apps\controller"

echo.
echo [1/4] Cleaning Python worker...
if exist "%WORKER_DIR%\.venv" (
    rmdir /s /q "%WORKER_DIR%\.venv"
    echo [OK] Removed .venv
) else (
    echo [SKIP] .venv not found
)
echo.

echo [2/4] Cleaning controller...
if exist "%CONTROLLER_DIR%\node_modules" (
    rmdir /s /q "%CONTROLLER_DIR%\node_modules"
    echo [OK] Removed node_modules
) else (
    echo [SKIP] node_modules not found
)

if exist "%CONTROLLER_DIR%\.svelte-kit" (
    rmdir /s /q "%CONTROLLER_DIR%\.svelte-kit"
    echo [OK] Removed .svelte-kit
) else (
    echo [SKIP] .svelte-kit not found
)
echo.

echo [3/4] Cleaning logs and temp files...
if exist "%PROJECT_ROOT%\logs" (
    rmdir /s /q "%PROJECT_ROOT%\logs"
    echo [OK] Removed logs
) else (
    echo [SKIP] logs not found
)

if exist "%PROJECT_ROOT%\obs" (
    rmdir /s /q "%PROJECT_ROOT%\obs"
    echo [OK] Removed obs
) else (
    echo [SKIP] obs not found
)

if exist "%PROJECT_ROOT%\_out.mp3" (
    del /q "%PROJECT_ROOT%\_out.mp3"
    echo [OK] Removed _out.mp3
) else (
    echo [SKIP] _out.mp3 not found
)
echo.

echo [4/4] Clean complete!
echo.
echo ========================================
echo  Next Steps:
echo ========================================
echo  Run: scripts\install.bat
echo.
pause
endlocal
