@echo off
setlocal enabledelayedexpansion

REM Install dependencies untuk livetik project
echo.
echo ========================================
echo  Installing Livetik Dependencies
echo ========================================
echo.

REM Get absolute paths
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "WORKER_DIR=%PROJECT_ROOT%\apps\worker"
set "CONTROLLER_DIR=%PROJECT_ROOT%\apps\controller"

echo [DEBUG] Script directory: %SCRIPT_DIR%
echo [DEBUG] Project root: %PROJECT_ROOT%
echo [DEBUG] Worker directory: %WORKER_DIR%
echo [DEBUG] Controller directory: %CONTROLLER_DIR%
echo.

REM Check if UV is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] UV not found!
    echo Please install UV first: https://github.com/astral-sh/uv
    echo.
    pause
    exit /b 1
)
echo [OK] UV found
echo.

REM Check if pnpm is installed
where pnpm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pnpm not found!
    echo Please install: npm install -g pnpm
    echo.
    pause
    exit /b 1
)
echo [OK] pnpm found
echo.

REM Check if worker directory exists
if not exist "%WORKER_DIR%" (
    echo [ERROR] Worker directory not found: %WORKER_DIR%
    pause
    exit /b 1
)

REM Check if pyproject.toml exists
if not exist "%WORKER_DIR%\pyproject.toml" (
    echo [ERROR] pyproject.toml not found in: %WORKER_DIR%
    pause
    exit /b 1
)
echo [OK] Worker directory found
echo.

REM Check if controller directory exists
if not exist "%CONTROLLER_DIR%" (
    echo [ERROR] Controller directory not found: %CONTROLLER_DIR%
    pause
    exit /b 1
)

REM Check if package.json exists
if not exist "%CONTROLLER_DIR%\package.json" (
    echo [ERROR] package.json not found in: %CONTROLLER_DIR%
    pause
    exit /b 1
)
echo [OK] Controller directory found
echo.

echo [1/4] Installing Python worker dependencies...
cd /d "%WORKER_DIR%"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Cannot change to worker directory
    pause
    exit /b 1
)
echo [DEBUG] Current directory: %CD%
call uv sync
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install worker dependencies
    cd /d "%SCRIPT_DIR%"
    pause
    exit /b 1
)
cd /d "%SCRIPT_DIR%"
echo [OK] Worker dependencies installed
echo.

echo [2/4] Installing Svelte controller dependencies...
cd /d "%CONTROLLER_DIR%"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Cannot change to controller directory
    pause
    exit /b 1
)
echo [DEBUG] Current directory: %CD%
call pnpm install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install controller dependencies
    cd /d "%SCRIPT_DIR%"
    pause
    exit /b 1
)
cd /d "%SCRIPT_DIR%"
echo [OK] Controller dependencies installed
echo.

echo [3/4] Checking .env file...
cd /d "%PROJECT_ROOT%"
if not exist ".env" (
    echo [WARNING] .env file not found
    echo Copying .env.example to .env...
    copy ".env.example" ".env"
    echo.
    echo [ACTION REQUIRED] Please edit .env and add your API keys:
    echo   - TIKTOK_USERNAME
    echo   - DEEPSEEK_API_KEY
    echo   - ANTHROPIC_API_KEY (optional)
    echo.
) else (
    echo [OK] .env file exists
)
cd /d "%SCRIPT_DIR%"
echo.

echo [4/4] Installation complete!
echo.
echo ========================================
echo  Next Steps:
echo ========================================
echo  1. Edit .env file with your API keys
echo  2. Run: scripts\dev.bat
echo  3. Open: http://localhost:5173
echo.
pause
endlocal
