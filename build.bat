@echo off
echo 🚀 Building AugmentCode Free for Windows...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Run the build script
python build.py

echo.
echo ✅ Build process completed!
echo Check the dist folder for the executable
pause
