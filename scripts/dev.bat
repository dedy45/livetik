@echo off
setlocal enabledelayedexpansion

REM Development server untuk livetik (worker + controller)
echo.
echo ========================================
echo  Starting Livetik Development Server
echo ========================================
echo.

REM Get absolute paths
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "WORKER_DIR=%PROJECT_ROOT%\apps\worker"
set "CONTROLLER_DIR=%PROJECT_ROOT%\apps\controller"

REM Check if dependencies are installed
if not exist "%WORKER_DIR%\.venv" (
    echo [ERROR] Worker dependencies not installed
    echo Please run: scripts\install.bat
    echo.
    pause
    exit /b 1
)

if not exist "%CONTROLLER_DIR%\node_modules" (
    echo [ERROR] Controller dependencies not installed
    echo Please run: scripts\install.bat
    echo.
    pause
    exit /b 1
)

REM Check .env file
if not exist "%PROJECT_ROOT%\.env" (
    echo [ERROR] .env file not found
    echo Please copy .env.example to .env and configure it
    echo.
    pause
    exit /b 1
)

echo [INFO] Starting worker and controller...
echo [INFO] Press Ctrl+C to stop all services
echo.

REM Start worker in new window
start "Livetik Worker" cmd /k "cd /d "%WORKER_DIR%" && uv run python -m banghack"

REM Wait 2 seconds
timeout /t 2 /nobreak >nul

REM Start controller in new window
start "Livetik Controller" cmd /k "cd /d "%CONTROLLER_DIR%" && pnpm dev"

echo.
echo ========================================
echo  Development Server Started!
echo ========================================
echo.
echo  Worker: Running in separate window
echo  Controller: http://localhost:5173
echo.
echo  Close the terminal windows to stop
echo.
pause
endlocal
