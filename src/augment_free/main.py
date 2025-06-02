"""
Main entry point for Free AugmentCode pywebview application.

This module creates and runs the pywebview application with the web interface.
"""

import os
import sys
import webview
from pathlib import Path

from .api.core import AugmentFreeAPI


def get_web_dir() -> str:
    """Get the web directory path."""
    current_dir = Path(__file__).parent
    web_dir = current_dir / "web"
    return str(web_dir)


def get_icon_path() -> str | None:
    """
    Get the application icon path.
    Works both in development and when packaged with PyInstaller.
    """
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        base_path = Path(sys._MEIPASS)
        icon_path = base_path / "app.ico"
    else:
        # Running in development - icon is in project root
        project_root = Path(__file__).parent.parent.parent
        icon_path = project_root / "app.ico"

    # Return path if file exists, otherwise return None
    return str(icon_path) if icon_path.exists() else None


def main():
    """
    Main function to start the Free AugmentCode application.
    """
    # Create API instance
    api = AugmentFreeAPI()

    # Get web directory
    web_dir = get_web_dir()
    index_path = os.path.join(web_dir, "index.html")

    # Check if web files exist
    if not os.path.exists(index_path):
        print(f"Error: Web files not found at {index_path}")
        print("Please ensure the web directory contains index.html")
        sys.exit(1)

    # Get icon path
    icon_path = get_icon_path()

    # Create webview window
    window_kwargs = {
        "title": "Free AugmentCode",
        "url": index_path,
        "js_api": api,
        "width": 1000,
        "height": 700,
        "min_size": (800, 600),
        "resizable": True,
        "shadow": True,
        "on_top": False,
    }

    # Add icon if available (supported on GTK/QT platforms)
    if icon_path:
        window_kwargs["icon"] = icon_path
        print(f"Using icon: {icon_path}")

    window = webview.create_window(**window_kwargs)

    print("Starting Free AugmentCode...")
    print(f"Web directory: {web_dir}")
    print("Close the application window to exit.")

    # Start the application
    try:
        webview.start(debug=False)
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
