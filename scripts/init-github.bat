@echo off
REM Initialize and push to GitHub repository
echo.
echo ========================================
echo  GitHub Repository Initialization
echo ========================================
echo.

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git not found!
    echo Please install Git first: https://git-scm.com/
    echo.
    pause
    exit /b 1
)

REM Check if already initialized
if exist .git (
    echo [WARNING] Git repository already initialized
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 0
) else (
    echo [1/6] Initializing git repository...
    git init
)

REM Add all files
echo [2/6] Adding files...
git add .

REM Create initial commit
echo [3/6] Creating initial commit...
git commit -m "chore: initial commit - complete project structure

- Add 9 documentation files (PRD, Architecture, Design, etc.)
- Setup monorepo structure (worker + controller)
- Add development scripts (install.bat, dev.bat)
- Configure VSCode workspace
- Add .env.example with all required variables
- Setup .gitignore for Python, Node, and sensitive files"

REM Check if remote exists
git remote | findstr "origin" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Remote 'origin' already exists
    git remote -v
    set /p update="Update remote? (y/n): "
    if /i "%update%"=="y" (
        git remote remove origin
        git remote add origin https://github.com/dedy45/livetik.git
    )
) else (
    echo [4/6] Adding remote repository...
    git remote add origin https://github.com/dedy45/livetik.git
)

REM Set main branch
echo [5/6] Setting main branch...
git branch -M main

REM Push to GitHub
echo [6/6] Pushing to GitHub...
echo.
echo [INFO] You may need to authenticate with GitHub
echo        Use Personal Access Token as password
echo.
set /p push="Ready to push? (y/n): "
if /i "%push%"=="y" (
    git push -u origin main
    echo.
    echo ========================================
    echo  Successfully Pushed to GitHub!
    echo ========================================
    echo.
    echo  Repository: https://github.com/dedy45/livetik
    echo.
) else (
    echo.
    echo [INFO] Push cancelled. You can push manually later:
    echo        git push -u origin main
    echo.
)

pause
