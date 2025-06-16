@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo   AUGMENTCODE FREE - BUILD SCRIPT
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if we're in the right directory
if not exist "src\augment_free\main.py" (
    echo ERROR: main.py not found
    echo Please run this script from the project root directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found
    pause
    exit /b 1
)

if not exist "src\augment_free\translations" (
    echo ERROR: translations directory not found
    pause
    exit /b 1
)

if not exist "src\augment_free\translations\zh_CN.json" (
    echo ERROR: Chinese translation file not found
    pause
    exit /b 1
)

if not exist "src\augment_free\translations\en_US.json" (
    echo ERROR: English translation file not found
    pause
    exit /b 1
)

echo [1/5] Fixing common PyInstaller issues...

REM Fix the typing package conflict
echo Removing conflicting 'typing' package...
pip uninstall typing -y >nul 2>&1
echo Done.

REM Clean any previous builds
if exist "dist" rmdir /s /q "dist" >nul 2>&1
if exist "build" rmdir /s /q "build" >nul 2>&1
if exist "*.spec" del "*.spec" >nul 2>&1

echo [2/5] Installing dependencies...
pip install --upgrade pip setuptools wheel --quiet
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    pause
    exit /b 1
)

pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Trying with verbose output...
    pip install -r requirements.txt
    pause
    exit /b 1
)

echo [3/5] Building debug version (with console)...
python -m PyInstaller --onefile --console --name=AugmentFree_debug --clean --noconfirm --add-data="src/augment_free/web;web" --add-data="src/augment_free/translations;translations" --icon=app.ico --hidden-import=pywebview --hidden-import=jinja2 --hidden-import=augment_free --hidden-import=augment_free.api --hidden-import=augment_free.utils --hidden-import=augment_free.api.handlers.automation --hidden-import=psutil src/augment_free/main.py

if not exist "dist\AugmentFree_debug.exe" (
    echo ERROR: Debug build failed
    pause
    exit /b 1
)

echo [4/5] Building release version (no console)...
python -m PyInstaller --onefile --windowed --name=AugmentFree_latest --clean --noconfirm --add-data="src/augment_free/web;web" --add-data="src/augment_free/translations;translations" --icon=app.ico --hidden-import=pywebview --hidden-import=jinja2 --hidden-import=augment_free --hidden-import=augment_free.api --hidden-import=augment_free.utils --hidden-import=augment_free.api.handlers.automation --hidden-import=psutil src/augment_free/main.py

echo [5/5] Checking results...
if exist "dist\AugmentFree_latest.exe" (
    echo SUCCESS: Release version created
    for %%A in ("dist\AugmentFree_latest.exe") do (
        set /a size_mb=%%~zA/1024/1024
        echo Size: !size_mb! MB
    )
) else (
    echo ERROR: Release build failed
)

if exist "dist\AugmentFree_debug.exe" (
    echo SUCCESS: Debug version created
    for %%A in ("dist\AugmentFree_debug.exe") do (
        set /a size_mb=%%~zA/1024/1024
        echo Size: !size_mb! MB
    )
) else (
    echo ERROR: Debug build failed
)

echo.
echo ==========================================
echo BUILD COMPLETED
echo ==========================================
echo.

if exist "dist\AugmentFree_latest.exe" (
    echo TIP: Run AugmentFree_latest.exe for normal use
    echo TIP: Run AugmentFree_debug.exe if you encounter issues
    echo.
    set /p run=Run the release version now? (y/N):
    if /i "!run!"=="y" (
        start "" "dist\AugmentFree_latest.exe"
    )
) else (
    echo Build failed. Running debug version to see errors...
    if exist "dist\AugmentFree_debug.exe" (
        "dist\AugmentFree_debug.exe"
    )
)

pause
