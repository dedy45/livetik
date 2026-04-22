@echo off
REM Script untuk memperbaiki warning tsconfig SvelteKit
REM Generate .svelte-kit/tsconfig.json dengan sync

echo ========================================
echo MEMPERBAIKI SVELTE TSCONFIG WARNING
echo ========================================
echo.

cd /d "%~dp0..\apps\controller"

echo [1/3] Memeriksa node_modules...
if not exist "node_modules" (
    echo Node modules tidak ditemukan. Menjalankan install...
    call pnpm install
) else (
    echo Node modules sudah ada.
)
echo.

echo [2/3] Generate SvelteKit files dengan sync...
call pnpm exec svelte-kit sync
echo.

echo [3/3] Memeriksa hasil...
if exist ".svelte-kit\tsconfig.json" (
    echo ========================================
    echo BERHASIL!
    echo File .svelte-kit/tsconfig.json sudah dibuat
    echo Warning tsconfig seharusnya hilang
    echo ========================================
) else (
    echo ========================================
    echo GAGAL!
    echo File .svelte-kit/tsconfig.json tidak dibuat
    echo Coba jalankan: pnpm run dev
    echo ========================================
)

pause
