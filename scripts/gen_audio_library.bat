@echo off
REM Generate audio library from clips_script.yaml using Cartesia TTS
REM This script must be run from the project root or scripts directory

cd /d %~dp0..
echo Generating audio library...
echo.

uv run --directory apps/worker python scripts/gen_audio_library.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Audio generation failed!
    pause
    exit /b 1
)

echo.
echo SUCCESS: Audio library generated!
pause
