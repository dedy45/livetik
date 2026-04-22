@echo off
REM Test script untuk verifikasi instalasi
echo.
echo ========================================
echo  Testing Livetik Installation
echo ========================================
echo.

REM Test UV
echo [1/5] Testing UV...
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] UV not found
    goto :error
)
echo [OK] UV found
echo.

REM Test pnpm
echo [2/5] Testing pnpm...
where pnpm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] pnpm not found
    goto :error
)
echo [OK] pnpm found
echo.

REM Test worker dependencies
echo [3/5] Testing worker dependencies...
if not exist "%~dp0..\apps\worker\.venv" (
    echo [FAIL] Worker .venv not found
    goto :error
)
pushd "%~dp0..\apps\worker"
call uv run python -c "import TikTokLive, openai, edge_tts, websockets, fastapi" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Worker dependencies incomplete
    popd
    goto :error
)
popd
echo [OK] Worker dependencies OK
echo.

REM Test controller dependencies
echo [4/5] Testing controller dependencies...
if not exist "%~dp0..\apps\controller\node_modules" (
    echo [FAIL] Controller node_modules not found
    goto :error
)
echo [OK] Controller dependencies OK
echo.

REM Test .env file
echo [5/5] Testing .env file...
if not exist "%~dp0..\.env" (
    echo [WARN] .env file not found (optional for testing)
) else (
    echo [OK] .env file exists
)
echo.

echo ========================================
echo  All Tests Passed!
echo ========================================
echo.
echo Ready to run: scripts\dev.bat
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo  Tests Failed!
echo ========================================
echo.
echo Please run: scripts\install.bat
echo.
pause
exit /b 1
