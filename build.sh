#!/bin/bash

echo "🚀 Building AugmentCode Free for Linux/macOS..."
echo

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Python on different systems
install_python() {
    echo "📥 Python not found. Attempting to install..."
    
    if command_exists apt-get; then
        # Ubuntu/Debian
        echo "🐧 Detected Ubuntu/Debian system"
        echo "Run: sudo apt-get update && sudo apt-get install python3 python3-pip python3-venv"
    elif command_exists yum; then
        # CentOS/RHEL
        echo "🐧 Detected CentOS/RHEL system"
        echo "Run: sudo yum install python3 python3-pip"
    elif command_exists dnf; then
        # Fedora
        echo "🐧 Detected Fedora system"
        echo "Run: sudo dnf install python3 python3-pip"
    elif command_exists pacman; then
        # Arch Linux
        echo "🐧 Detected Arch Linux system"
        echo "Run: sudo pacman -S python python-pip"
    elif command_exists brew; then
        # macOS with Homebrew
        echo "🍎 Detected macOS with Homebrew"
        echo "Installing Python via Homebrew..."
        brew install python
    else
        echo "❌ Could not detect package manager"
        echo "Please install Python 3.10+ manually from https://www.python.org/downloads/"
    fi
}

# Check if Python is installed
if ! command_exists python3 && ! command_exists python; then
    echo "❌ Python is not installed or not in PATH"
    install_python
    exit 1
fi

# Use python3 if available, otherwise python
if command_exists python3; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi

echo "✅ Python found:"
$PYTHON_CMD --version

# Check if we're in the right directory
if [ ! -f "src/augment_free/main.py" ]; then
    echo "❌ Error: main.py not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    echo "Please ensure requirements.txt exists in the project root"
    exit 1
fi

# Check if translation files exist
if [ ! -d "src/augment_free/translations" ]; then
    echo "❌ Error: translations directory not found"
    echo "Please ensure src/augment_free/translations exists"
    exit 1
fi

if [ ! -f "src/augment_free/translations/zh_CN.json" ]; then
    echo "❌ Error: Chinese translation file not found"
    echo "Please ensure src/augment_free/translations/zh_CN.json exists"
    exit 1
fi

if [ ! -f "src/augment_free/translations/en_US.json" ]; then
    echo "❌ Error: English translation file not found"
    echo "Please ensure src/augment_free/translations/en_US.json exists"
    exit 1
fi

echo
echo "📦 Checking dependencies..."

# Check if pip is available
if ! command_exists $PIP_CMD; then
    echo "❌ pip is not available"
    echo "Please install pip for Python"
    exit 1
fi

# Auto-install dependencies
echo "📥 Installing/updating dependencies..."
$PIP_CMD install --upgrade pip setuptools wheel
if [ $? -ne 0 ]; then
    echo "❌ Failed to upgrade pip"
    exit 1
fi

$PIP_CMD install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    echo "Please check your internet connection and try again"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Run the build script
echo
echo "🔨 Starting build process..."
$PYTHON_CMD build.py

echo
if [ -f "dist/AugmentFree_latest" ]; then
    echo "✅ Build completed successfully!"
    echo "📁 Executable location: dist/AugmentFree_latest"
    
    # Get file size
    size=$(stat -f%z "dist/AugmentFree_latest" 2>/dev/null || stat -c%s "dist/AugmentFree_latest" 2>/dev/null)
    if [ -n "$size" ]; then
        size_mb=$((size / 1024 / 1024))
        echo "📊 File size: ${size_mb} MB"
    fi
    
    # Make executable
    chmod +x "dist/AugmentFree_latest"
    
    echo
    echo "🎯 Would you like to run the executable now? (y/N)"
    read -r run_exe
    if [ "$run_exe" = "y" ] || [ "$run_exe" = "Y" ]; then
        echo "🚀 Starting AugmentCode Free..."
        ./dist/AugmentFree_latest &
    fi
else
    echo "❌ Build failed - executable not found"
    echo "Check the output above for errors"
    
    if [ -f "dist/AugmentFree_debug" ]; then
        echo
        echo "💡 Debug executable found. Would you like to run it to see error messages? (y/N)"
        read -r run_debug
        if [ "$run_debug" = "y" ] || [ "$run_debug" = "Y" ]; then
            echo "🔧 Starting debug version..."
            chmod +x "dist/AugmentFree_debug"
            ./dist/AugmentFree_debug
        fi
    fi
fi

echo
echo "Check the dist folder for the executable files"
