@echo off
cd /d %~dp0..
call uv run python scripts/gen_audio_library.py %*
