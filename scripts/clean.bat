@echo off
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

echo.
echo [1/4] Cleaning Python worker...
if exist "%~dp0..\apps\worker\.venv" (
    rmdir /s /q "%~dp0..\apps\worker\.venv"
    echo [OK] Removed .venv
) else (
    echo [SKIP] .venv not found
)
echo.

echo [2/4] Cleaning controller...
if exist "%~dp0..\apps\controller\node_modules" (
    rmdir /s /q "%~dp0..\apps\controller\node_modules"
    echo [OK] Removed node_modules
) else (
    echo [SKIP] node_modules not found
)

if exist "%~dp0..\apps\controller\.svelte-kit" (
    rmdir /s /q "%~dp0..\apps\controller\.svelte-kit"
    echo [OK] Removed .svelte-kit
) else (
    echo [SKIP] .svelte-kit not found
)
echo.

echo [3/4] Cleaning logs and temp files...
if exist "%~dp0..\logs" (
    rmdir /s /q "%~dp0..\logs"
    echo [OK] Removed logs
) else (
    echo [SKIP] logs not found
)

if exist "%~dp0..\obs" (
    rmdir /s /q "%~dp0..\obs"
    echo [OK] Removed obs
) else (
    echo [SKIP] obs not found
)

if exist "%~dp0..\_out.mp3" (
    del /q "%~dp0..\_out.mp3"
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
