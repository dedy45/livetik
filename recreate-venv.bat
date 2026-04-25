@echo off
echo Recreating venv...
cd apps\worker
rmdir /s /q .venv
uv venv
uv sync
echo Done!
