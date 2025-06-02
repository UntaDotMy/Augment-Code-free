import subprocess
import sys
from pathlib import Path


def main():
    """激活虚拟环境."""
    project_root = Path(__file__).parent
    venv_activate = project_root / ".venv" / "Scripts" / "Activate.ps1"
    
    if not venv_activate.exists():
        print("❌ Virtual environment not found!")
        print("Please run: uv sync")
        sys.exit(1)
    
    print("🚀 Starting Free AugmentCode...")
    
    # Command to activate venv and run app
    cmd = f"& {venv_activate}; python -m augment_free.main"
    
    try:
        subprocess.run(["powershell", "-Command", cmd], 
                      cwd=project_root, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")


if __name__ == "__main__":
    main()
