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
pushd "%~dp0..\apps\worker"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Cannot access worker directory
    pause
    exit /b 1
)
call uv sync
set UV_ERROR=%ERRORLEVEL%
popd
if %UV_ERROR% NEQ 0 (
    echo [ERROR] Failed to install worker dependencies
    pause
    exit /b 1
)
echo [OK] Worker dependencies installed
echo.

echo [2/4] Installing Svelte controller dependencies...
pushd "%~dp0..\apps\controller"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Cannot access controller directory
    pause
    exit /b 1
)
call pnpm install
set PNPM_ERROR=%ERRORLEVEL%
popd
if %PNPM_ERROR% NEQ 0 (
    echo [ERROR] Failed to install controller dependencies
    pause
    exit /b 1
)
echo [OK] Controller dependencies installed
echo.

echo [3/4] Checking .env file...
if not exist "%~dp0..\.env" (
    echo [WARNING] .env file not found
    echo Copying .env.example to .env...
    copy "%~dp0..\.env.example" "%~dp0..\.env"
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
