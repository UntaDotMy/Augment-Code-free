@echo off
echo 🚀 AugmentCode Free Release Tool
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Run the release script
python scripts/release.py

echo.
echo ✅ Release process completed!
pause
