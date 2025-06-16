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
        # Install from requirements.txt to match GitHub Actions
        run_command("uv add pyinstaller pillow")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("uv not found, using pip")
        # Install from requirements.txt to match GitHub Actions
        run_command("pip install --upgrade pip setuptools wheel")
        run_command("pip install -r requirements.txt")

        # Add src to Python path instead of editable install
        import sys
        src_path = str(Path("src").absolute())
        if src_path not in sys.path:
            sys.path.insert(0, src_path)


def build_executable():
    """Build the executable using PyInstaller."""
    print("🔨 Building executable...")

    # Get the current platform
    current_platform = platform.system().lower()

    # Base PyInstaller command - match GitHub Actions exactly
    base_cmd = [
        "python", "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=AugmentFree_latest",
        "--clean",  # Clean PyInstaller cache
        "--noconfirm",  # Replace output without asking
    ]

    # Add data files - match GitHub Actions path structure
    if current_platform == "windows":
        base_cmd.append("--add-data=src/augment_free/web;augment_free/web")
    else:
        base_cmd.append("--add-data=src/augment_free/web:augment_free/web")

    # Add icon if it exists
    if Path("app.ico").exists():
        base_cmd.append("--icon=app.ico")
        if current_platform == "windows":
            base_cmd.append("--add-data=app.ico;.")
        else:
            base_cmd.append("--add-data=app.ico:.")

    # Add essential hidden imports only
    hidden_imports = [
        "pywebview",
        "jinja2",
        "augment_free",
        "augment_free.api",
        "augment_free.utils",
    ]

    for imp in hidden_imports:
        base_cmd.append(f"--hidden-import={imp}")

    # Add main script
    base_cmd.append("src/augment_free/main.py")

    cmd = " ".join(base_cmd)
    run_command(cmd)


def build_debug_executable():
    """Build a debug version with console output."""
    print("🔨 Building DEBUG executable (with console)...")

    # Get the current platform
    current_platform = platform.system().lower()

    # Debug PyInstaller command - with console for debugging
    base_cmd = [
        "python", "-m", "PyInstaller",
        "--onefile",
        "--console",  # Show console for debugging
        "--name=AugmentFree_debug",
        "--clean",
        "--noconfirm",
    ]

    # Add data files
    if current_platform == "windows":
        base_cmd.append("--add-data=src/augment_free/web;web")
        base_cmd.append("--add-data=src/augment_free/translations;translations")
    else:
        base_cmd.append("--add-data=src/augment_free/web:web")
        base_cmd.append("--add-data=src/augment_free/translations:translations")

    # Add icon if it exists
    if Path("app.ico").exists():
        base_cmd.append("--icon=app.ico")
        if current_platform == "windows":
            base_cmd.append("--add-data=app.ico;.")
        else:
            base_cmd.append("--add-data=app.ico:.")

    # Add hidden imports
    hidden_imports = [
        "pywebview",
        "jinja2",
        "bottle",
        "cffi",
        "clr-loader",
        "markupsafe",
        "proxy-tools",
        "pycparser",
        "pythonnet",
        "typing-extensions",
        "webview.platforms.winforms",
        "webview.platforms.cef",
        "webview.platforms.edgechromium",
        "augment_free",
        "augment_free.api",
        "augment_free.api.core",
        "augment_free.api.handlers",
        "augment_free.api.handlers.database",
        "augment_free.api.handlers.telemetry",
        "augment_free.api.handlers.workspace",
        "augment_free.api.handlers.jetbrains",
        "augment_free.utils",
        "augment_free.utils.device_codes",
        "augment_free.utils.paths",
        "augment_free.utils.ide_detector",
        "augment_free.utils.translation",
        "augment_free.api.handlers.automation",
        "psutil",
    ]

    for imp in hidden_imports:
        base_cmd.append(f"--hidden-import={imp}")

    # Add main script
    base_cmd.append("src/augment_free/main.py")

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

    # Check if web files exist
    if not Path("src/augment_free/web/index.html").exists():
        print("❌ Error: Web files not found. Please ensure src/augment_free/web/index.html exists.")
        sys.exit(1)

    # Check if translation files exist
    if not Path("src/augment_free/translations").exists():
        print("❌ Error: Translation directory not found. Please ensure src/augment_free/translations exists.")
        sys.exit(1)

    translation_files = list(Path("src/augment_free/translations").glob("*.json"))
    if not translation_files:
        print("❌ Error: No translation files found. Please ensure translation JSON files exist.")
        sys.exit(1)

    print(f"✅ Found {len(translation_files)} translation files: {[f.name for f in translation_files]}")

    # Install dependencies
    install_dependencies()

    # Build both versions automatically (non-interactive)
    print("\n🎯 Building both debug and release versions automatically...")
    choice = "3"  # Always build both

    if choice in ["2", "3"]:
        print("\n🔧 Building debug version...")
        build_debug_executable()

    if choice in ["1", "3", ""]:
        print("\n🚀 Building release version...")
        build_executable()

    # Check if build was successful
    dist_dir = Path("dist")
    current_platform = platform.system().lower()

    built_files = []

    # Check release version
    if choice in ["1", "3", ""]:
        if current_platform == "windows":
            executable_name = "AugmentFree_latest.exe"
        else:
            executable_name = "AugmentFree_latest"

        executable_path = dist_dir / executable_name
        if executable_path.exists():
            built_files.append(("Release", executable_path))

    # Check debug version
    if choice in ["2", "3"]:
        if current_platform == "windows":
            debug_name = "AugmentFree_debug.exe"
        else:
            debug_name = "AugmentFree_debug"

        debug_path = dist_dir / debug_name
        if debug_path.exists():
            built_files.append(("Debug", debug_path))

    if built_files:
        print(f"\n✅ Build successful!")
        for build_type, path in built_files:
            print(f"📁 {build_type} executable: {path.absolute()}")
            print(f"📊 {build_type} file size: {path.stat().st_size / 1024 / 1024:.1f} MB")

        if choice in ["2", "3"]:
            print(f"\n💡 Tip: Run the debug version first to see any error messages!")
    else:
        print("❌ Build failed - no executables found")
        sys.exit(1)


if __name__ == "__main__":
    main()
