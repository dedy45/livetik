@echo off
REM Script Master untuk memperbaiki semua masalah
REM 1. Fix SvelteKit tsconfig warning
REM 2. Backup ke GitHub

echo ========================================
echo PERBAIKAN LENGKAP LIVETIK
echo ========================================
echo.

cd /d "%~dp0"

echo LANGKAH 1: Memperbaiki SvelteKit tsconfig...
echo ----------------------------------------
call fix-svelte-tsconfig.bat
echo.
echo.

echo LANGKAH 2: Backup ke GitHub...
echo ----------------------------------------
call backup-github.bat
echo.
echo.

echo ========================================
echo SEMUA PERBAIKAN SELESAI!
echo ========================================
pause
