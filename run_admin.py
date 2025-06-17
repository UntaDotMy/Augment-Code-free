#!/usr/bin/env python3
"""
Admin-aware launcher for Free AugmentCode.

This script checks for administrator privileges and provides options
to run with elevated permissions if needed.
"""

import sys
import os
import subprocess
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
            # Use PowerShell to run as admin
            script_path = Path(__file__).parent / "run.py"
            cmd = f'Start-Process python -ArgumentList "{script_path}" -Verb RunAs'
            subprocess.run(["powershell", "-Command", cmd], check=True)
            return True
    except Exception as e:
        print(f"❌ Failed to run as administrator: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Free AugmentCode - Admin Launcher")
    print("=" * 50)
    
    # Check current privileges
    admin_status = is_admin()
    print(f"Administrator privileges: {'✅ Yes' if admin_status else '❌ No'}")
    
    if not admin_status:
        print("\n⚠️  WARNING: Not running as administrator!")
        print("Some cleaning operations may fail due to insufficient permissions.")
        print("This can happen when:")
        print("  • IDE processes are running and have files locked")
        print("  • System files require elevated permissions")
        print("  • Workspace storage contains protected files")
        print()
        
        choice = input("Do you want to run as administrator? (y/n): ").lower().strip()
        
        if choice in ['y', 'yes']:
            print("🔄 Attempting to restart with administrator privileges...")
            if run_as_admin():
                print("✅ Restarted with admin privileges. You can close this window.")
                return
            else:
                print("❌ Failed to restart as administrator.")
                print("You can:")
                print("  1. Right-click on the script and 'Run as administrator'")
                print("  2. Run from an elevated command prompt")
                print("  3. Continue without admin privileges (some operations may fail)")
                print()
                
                continue_choice = input("Continue without admin privileges? (y/n): ").lower().strip()
                if continue_choice not in ['y', 'yes']:
                    print("👋 Exiting...")
                    return
    
    # Run the main application
    print("\n🚀 Starting Free AugmentCode...")
    try:
        # Import and run the main application
        from run import main as run_main
        run_main()
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        import traceback
        traceback.print_exc()
        
        if not admin_status:
            print("\n💡 Tip: Some errors might be resolved by running as administrator.")
        
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
