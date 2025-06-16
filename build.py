#!/usr/bin/env python3
"""
Build script for AugmentCode Free
Creates executable files using PyInstaller
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(f"✅ Success: {cmd}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {cmd}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)


def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    # Check if uv is available
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("Using uv for dependency management")
        run_command("uv sync")
        run_command("uv add pyinstaller pillow")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("uv not found, using pip")
        run_command("pip install -e .")
        run_command("pip install pyinstaller pillow")


def build_executable():
    """Build the executable using PyInstaller."""
    print("🔨 Building executable...")
    
    # Get the current platform
    current_platform = platform.system().lower()
    
    # Base PyInstaller command
    base_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=AugmentFree_latest",
        "--add-data=src/augment_free/web{}augment_free/web".format(
            ";" if current_platform == "windows" else ":"
        ),
        "--optimize=2",
        "--strip",
        "src/augment_free/main.py"
    ]

    # Add icon if it exists
    if Path("app.ico").exists():
        base_cmd.insert(-1, "--icon=app.ico")
        base_cmd.insert(-1, "--add-data=app.ico{}".format(
            ";." if current_platform == "windows" else ":."
        ))
    
    cmd = " ".join(base_cmd)
    run_command(cmd)


def main():
    """Main build function."""
    print("🚀 Starting AugmentCode Free build process...")
    print(f"Platform: {platform.system()} {platform.machine()}")
    
    # Check if we're in the right directory
    if not Path("src/augment_free/main.py").exists():
        print("❌ Error: main.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check if icon exists
    if not Path("app.ico").exists():
        print("⚠️  Warning: app.ico not found. Building without icon.")
    
    # Install dependencies
    install_dependencies()
    
    # Build executable
    build_executable()
    
    # Check if build was successful
    dist_dir = Path("dist")
    current_platform = platform.system().lower()
    if current_platform == "windows":
        executable_name = "AugmentFree_latest.exe"
    else:
        executable_name = "AugmentFree_latest"
    
    executable_path = dist_dir / executable_name
    
    if executable_path.exists():
        print(f"✅ Build successful!")
        print(f"📁 Executable location: {executable_path.absolute()}")
        print(f"📊 File size: {executable_path.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print("❌ Build failed - executable not found")
        sys.exit(1)


if __name__ == "__main__":
    main()
