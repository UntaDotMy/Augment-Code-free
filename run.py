import subprocess
import sys
import os
from pathlib import Path


def is_admin():
    """Check if running as administrator on Windows."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    """Restart the script with administrator privileges."""
    try:
        if sys.platform == "win32":
            import ctypes
            # Get the current script path
            script_path = os.path.abspath(__file__)
            # Use ShellExecuteW to run as admin
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script_path}"', None, 1
            )
            return True
    except Exception as e:
        print(f"❌ Failed to run as administrator: {e}")
        return False


def main():
    """Main function with automatic admin elevation."""
    print("🚀 Free AugmentCode - Starting...")
    print("=" * 50)

    # Check if running as administrator
    admin_status = is_admin()
    print(f"Administrator privileges: {'✅ Yes' if admin_status else '❌ No'}")

    if not admin_status:
        print("\n🔄 Elevating to administrator privileges...")
        print("This is required for:")
        print("  • Closing IDE processes safely")
        print("  • Accessing protected workspace files")
        print("  • Cleaning system-level session data")
        print("  • Ensuring complete workspace cleanup")
        print()

        if run_as_admin():
            print("✅ Restarted with administrator privileges.")
            print("👋 You can close this window - the app will open in the new admin window.")
            input("Press Enter to exit this window...")
            return
        else:
            print("❌ Failed to elevate privileges automatically.")
            print("\n⚠️  MANUAL ELEVATION REQUIRED:")
            print("1. Close this window")
            print("2. Right-click on 'run.py' or 'run_admin.py'")
            print("3. Select 'Run as administrator'")
            print("\nOR run from an elevated command prompt:")
            print("   python run.py")
            print()

            choice = input("Continue without admin privileges? (y/N): ").lower().strip()
            if choice not in ['y', 'yes']:
                print("👋 Exiting... Please run as administrator for best results.")
                input("Press Enter to exit...")
                return

            print("\n⚠️  WARNING: Running without admin privileges!")
            print("Some operations may fail due to insufficient permissions.")

    # Continue with application startup
    project_root = Path(__file__).parent
    venv_activate = project_root / ".venv" / "Scripts" / "Activate.ps1"

    if not venv_activate.exists():
        print("❌ Virtual environment not found!")
        print("Please run: uv sync")
        input("Press Enter to exit...")
        sys.exit(1)

    print(f"\n🚀 Starting Free AugmentCode {'with ADMIN privileges' if admin_status else 'with LIMITED privileges'}...")

    # Command to activate venv and run app
    cmd = f"& {venv_activate}; python -c \"import sys; sys.path.insert(0, 'src'); from augment_free.main import main; main()\""

    try:
        subprocess.run(["powershell", "-Command", cmd],
                      cwd=project_root, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run application: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")


if __name__ == "__main__":
    main()
