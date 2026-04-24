@echo off
REM Generate audio library using edge-tts fallback
REM This script works even without Cartesia API keys

cd /d "%~dp0.."
echo.
echo ========================================
echo  Audio Library Generator (Edge-TTS)
echo ========================================
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: 'uv' is not installed or not in PATH
    echo Please install uv first: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

REM Run the generator
echo Running audio library generator...
echo.
uv run python scripts/gen_audio_library_edgets.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo  SUCCESS! Audio library generated.
    echo ========================================
) else (
    echo.
    echo ========================================
    echo  ERROR: Generation failed.
    echo ========================================
)

echo.
pause
