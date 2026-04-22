@echo off
REM Script untuk backup ke GitHub
REM Mengatasi masalah branch dan remote

echo ========================================
echo BACKUP LIVETIK KE GITHUB
echo ========================================
echo.

cd /d "%~dp0.."

echo [1/6] Memeriksa status Git...
git status
echo.

echo [2/6] Memeriksa remote...
git remote -v
echo.

echo [3/6] Menambahkan semua perubahan...
git add .
echo.

echo [4/6] Commit perubahan...
git commit -m "Backup: %date% %time%" || echo Tidak ada perubahan untuk di-commit
echo.

echo [5/6] Pull dari remote (jika ada konflik)...
git pull origin main --no-edit --allow-unrelated-histories || echo Pull gagal atau tidak diperlukan
echo.

echo [6/6] Push ke GitHub...
git push -u origin main
echo.

if %errorlevel% equ 0 (
    echo ========================================
    echo BACKUP BERHASIL!
    echo Repository: https://github.com/dedy45/livetik
    echo ========================================
) else (
    echo ========================================
    echo BACKUP GAGAL!
    echo Periksa error di atas
    echo ========================================
)

pause
