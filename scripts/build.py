#!/usr/bin/env python3
"""
Build script for Free AugmentCode.
Creates a standalone executable using PyInstaller.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    import PyInstaller.__main__
except ImportError:
    print("❌ PyInstaller not found. Installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    import PyInstaller.__main__


def main():
    """Build the application."""
    print("🚀 Building Free AugmentCode...")

    # Paths
    main_script = project_root / "src" / "augment_free" / "main.py"
    web_dir = project_root / "src" / "augment_free" / "web"
    requirements_file = project_root / "requirements.txt"

    # PyInstaller command
    cmd = [
        str(main_script),
        "--name=AugmentFree",
        "--clean",  # Clean PyInstaller cache
        "--onefile",  # Create single executable
        "--noconfirm",  # Replace output without asking
        "--distpath=./dist",  # Output directory
        f"--add-data={web_dir};web",  # Include web files
        "--noconsole",  # Hide console window (Windows)
    ]

    # Add hidden imports from requirements.txt
    if requirements_file.exists():
        print("📦 Adding dependencies from requirements.txt...")
        with open(requirements_file, "r", encoding="utf-8") as reader:
            for line in reader:
                line = line.strip()
                if line and not line.startswith("#") and "==" in line:
                    package = line.split("==")[0].strip()
                    cmd.append(f"--hidden-import={package}")
                    print(f"   Added: {package}")

    # Additional hidden imports for pywebview
    additional_imports = [
        "webview",
        "webview.platforms.winforms",
        "webview.platforms.cef",
        "webview.platforms.edgechromium",
        "bottle",
        "jinja2",
    ]

    for imp in additional_imports:
        cmd.append(f"--hidden-import={imp}")

    print("🔧 Running PyInstaller...")
    print(f"Command: {' '.join(cmd)}")

    try:
        PyInstaller.__main__.run(cmd)
        print("✅ Build completed successfully!")
        print(f"📁 Executable created: {project_root / 'dist' / 'AugmentFree.exe'}")
    except Exception as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()