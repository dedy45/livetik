@echo off
REM Install dependencies untuk livetik project
echo.
echo ========================================
echo  Installing Livetik Dependencies
echo ========================================
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

REM Check if pnpm is installed
where pnpm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pnpm not found!
    echo Please install: npm install -g pnpm
    echo.
    pause
    exit /b 1
)

echo [1/4] Installing Python worker dependencies...
cd apps\worker
call uv sync
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install worker dependencies
    cd ..\..
    pause
    exit /b 1
)
cd ..\..
echo [OK] Worker dependencies installed
echo.

echo [2/4] Installing Svelte controller dependencies...
cd apps\controller
call pnpm install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install controller dependencies
    cd ..\..
    pause
    exit /b 1
)
cd ..\..
echo [OK] Controller dependencies installed
echo.

echo [3/4] Checking .env file...
if not exist .env (
    echo [WARNING] .env file not found
    echo Copying .env.example to .env...
    copy .env.example .env
    echo.
    echo [ACTION REQUIRED] Please edit .env and add your API keys:
    echo   - TIKTOK_USERNAME
    echo   - DEEPSEEK_API_KEY
    echo   - ANTHROPIC_API_KEY (optional)
    echo.
)
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
