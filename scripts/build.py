#!/usr/bin/env python3
"""
Build script for Free AugmentCode.
Creates a standalone executable using PyInstaller.
"""

import os
import sys
import shutil
from datetime import datetime
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


def move_to_release(exe_path):
    """Move the built executable to the release folder with timestamp."""
    print("📦 Moving executable to release folder...")

    # Create release folder if it doesn't exist
    release_dir = project_root / "release"
    release_dir.mkdir(exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version_info = get_version_info()

    if version_info:
        release_filename = f"AugmentFree_v{version_info}_{timestamp}.exe"
    else:
        release_filename = f"AugmentFree_{timestamp}.exe"

    release_path = release_dir / release_filename

    try:
        # Copy the file to release folder
        shutil.copy2(exe_path, release_path)
        print(f"✅ Executable moved to: {release_path}")

        # Also create a "latest" copy for convenience
        latest_path = release_dir / "AugmentFree_latest.exe"
        shutil.copy2(exe_path, latest_path)
        print(f"📋 Latest copy created: {latest_path}")

        # Show release folder contents
        print("\n📁 Release folder contents:")
        for file in sorted(release_dir.glob("*.exe")):
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"   {file.name} ({size_mb:.1f} MB)")

    except Exception as e:
        print(f"❌ Failed to move executable: {e}")


def get_version_info():
    """Get version information from pyproject.toml."""
    try:
        pyproject_file = project_root / "pyproject.toml"
        if pyproject_file.exists():
            with open(pyproject_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        # Extract version from line like: version = "0.1.0"
                        version = line.split("=")[1].strip().strip('"').strip("'")
                        return version
    except Exception:
        pass
    return None


def main():
    """Build the application."""
    print("🚀 Building Free AugmentCode...")

    # Paths
    main_script = project_root / "src" / "augment_free" / "main.py"
    web_dir = project_root / "src" / "augment_free" / "web"
    icon_file = project_root / "app.ico"
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

    # Add icon if it exists
    if icon_file.exists():
        cmd.extend([
            f"--icon={icon_file}",  # Set application icon
            f"--add-data={icon_file};.",  # Include icon file in bundle
        ])
        print(f"📎 Adding icon: {icon_file}")
    else:
        print("⚠️  Icon file not found, building without icon")

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

    # Additional hidden imports for pywebview and our modules
    additional_imports = [
        "webview",
        "webview.platforms.winforms",
        "webview.platforms.cef",
        "webview.platforms.edgechromium",
        "bottle",
        "jinja2",
        # Our project modules
        "augment_free",
        "augment_free.api",
        "augment_free.api.core",
        "augment_free.api.handlers",
        "augment_free.api.handlers.database",
        "augment_free.api.handlers.telemetry",
        "augment_free.api.handlers.workspace",
        "augment_free.utils",
        "augment_free.utils.device_codes",
        "augment_free.utils.paths",
    ]

    for imp in additional_imports:
        cmd.append(f"--hidden-import={imp}")

    print("🔧 Running PyInstaller...")
    print(f"Command: {' '.join(cmd)}")

    try:
        PyInstaller.__main__.run(cmd)
        print("✅ Build completed successfully!")

        # Move to release folder
        dist_exe = project_root / "dist" / "AugmentFree.exe"
        if dist_exe.exists():
            move_to_release(dist_exe)
        else:
            print("⚠️  Executable not found in dist folder")

    except Exception as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()