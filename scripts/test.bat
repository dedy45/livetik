@echo off
setlocal enabledelayedexpansion

REM Test installation dan dependencies
echo.
echo ========================================
echo  Testing Livetik Installation
echo ========================================
echo.

REM Get absolute paths
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "WORKER_DIR=%PROJECT_ROOT%\apps\worker"
set "CONTROLLER_DIR=%PROJECT_ROOT%\apps\controller"

set "ALL_OK=1"

REM Test UV
echo [1/6] Testing UV...
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] UV not found
    set "ALL_OK=0"
) else (
    echo [OK] UV found
)
echo.

REM Test pnpm
echo [2/6] Testing pnpm...
where pnpm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] pnpm not found
    set "ALL_OK=0"
) else (
    echo [OK] pnpm found
)
echo.

REM Test worker dependencies
echo [3/6] Testing worker dependencies...
if not exist "%WORKER_DIR%\.venv" (
    echo [FAIL] Worker .venv not found
    set "ALL_OK=0"
) else (
    echo [OK] Worker .venv exists
)
echo.

REM Test controller dependencies
echo [4/6] Testing controller dependencies...
if not exist "%CONTROLLER_DIR%\node_modules" (
    echo [FAIL] Controller node_modules not found
    set "ALL_OK=0"
) else (
    echo [OK] Controller node_modules exists
)
echo.

REM Test .env file
echo [5/6] Testing .env file...
if not exist "%PROJECT_ROOT%\.env" (
    echo [FAIL] .env file not found
    set "ALL_OK=0"
) else (
    echo [OK] .env file exists
)
echo.

REM Test project structure
echo [6/6] Testing project structure...
if not exist "%WORKER_DIR%\pyproject.toml" (
    echo [FAIL] pyproject.toml not found
    set "ALL_OK=0"
) else if not exist "%CONTROLLER_DIR%\package.json" (
    echo [FAIL] package.json not found
    set "ALL_OK=0"
) else (
    echo [OK] Project structure valid
)
echo.

REM Summary
echo ========================================
if "%ALL_OK%"=="1" (
    echo  Result: ALL TESTS PASSED
    echo ========================================
    echo.
    echo Ready to run: scripts\dev.bat
) else (
    echo  Result: SOME TESTS FAILED
    echo ========================================
    echo.
    echo Please run: scripts\install.bat
)
echo.
pause
endlocal
