"""
Main entry point for Free AugmentCode pywebview application.

This module creates and runs the pywebview application with the web interface.
"""

import os
import sys
import webview
from pathlib import Path

try:
    # Try relative import first (for development)
    from .api.core import AugmentFreeAPI
except ImportError:
    # Fall back to absolute import (for packaged executable)
    from augment_free.api.core import AugmentFreeAPI

# Windows-specific imports for icon setting
if sys.platform == "win32":
    try:
        import ctypes
    except ImportError:
        ctypes = None


def get_web_dir() -> str:
    """Get the web directory path."""
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        base_path = Path(sys._MEIPASS)
        web_dir = base_path / "web"
    else:
        # Running in development
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


def set_windows_icon(icon_path: str) -> None:
    """
    Set application icon on Windows using Win32 API.
    This is called after the window is created.
    """
    if sys.platform != "win32" or not ctypes:
        return

    try:
        # Wait for window to be created
        import time
        time.sleep(0.5)

        # Get the window handle
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if hwnd == 0:
            return

        # Load the icon
        hicon = ctypes.windll.user32.LoadImageW(
            None,  # hInst
            icon_path,  # name
            1,  # IMAGE_ICON
            0,  # cx (use default)
            0,  # cy (use default)
            0x00000010 | 0x00000040  # LR_LOADFROMFILE | LR_DEFAULTSIZE
        )

        if hicon != 0:
            # Set both small and large icons
            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, hicon)  # WM_SETICON, ICON_SMALL
            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, hicon)  # WM_SETICON, ICON_LARGE
            print("✅ Successfully set Windows icon")
        else:
            print(f"❌ Failed to load icon: {icon_path}")

    except Exception as e:
        print(f"❌ Error setting Windows icon: {e}")


def main():
    """
    Main function to start the Free AugmentCode application.
    """
    try:
        # Set UTF-8 encoding for console output
        if sys.platform == "win32":
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

        print("Starting AugmentCode Free...")
        print(f"Python version: {sys.version}")
        print(f"Platform: {sys.platform}")

        # Check if running as PyInstaller bundle
        if getattr(sys, "frozen", False):
            print(f"Running as PyInstaller bundle from: {sys._MEIPASS}")
        else:
            print("Running in development mode")

        # Create API instance
        print("Initializing API...")
        api = AugmentFreeAPI()

        # Get web directory
        print("Locating web files...")
        web_dir = get_web_dir()
        index_path = os.path.join(web_dir, "index.html")

        print(f"Web directory: {web_dir}")
        print(f"Index path: {index_path}")

        # Check if web files exist
        if not os.path.exists(index_path):
            print(f"ERROR: Web files not found at {index_path}")
            print("Please ensure the web directory contains index.html")

            # List what's actually in the directory
            if os.path.exists(web_dir):
                print(f"Contents of {web_dir}:")
                for item in os.listdir(web_dir):
                    print(f"  - {item}")
            else:
                print(f"Web directory {web_dir} does not exist")

                # If running as PyInstaller bundle, check what's in _MEIPASS
                if getattr(sys, "frozen", False):
                    print(f"Contents of {sys._MEIPASS}:")
                    for item in os.listdir(sys._MEIPASS):
                        print(f"  - {item}")

                    # Try to find web files in augment_free subdirectory
                    augment_free_dir = os.path.join(sys._MEIPASS, "augment_free")
                    if os.path.exists(augment_free_dir):
                        print(f"Contents of {augment_free_dir}:")
                        for item in os.listdir(augment_free_dir):
                            print(f"  - {item}")

                        # Check if web files are in augment_free/web
                        web_in_augment = os.path.join(augment_free_dir, "web")
                        if os.path.exists(web_in_augment):
                            print(f"Found web directory at: {web_in_augment}")
                            index_in_augment = os.path.join(web_in_augment, "index.html")
                            if os.path.exists(index_in_augment):
                                print("Found index.html! Using this path instead.")
                                web_dir = web_in_augment
                                index_path = index_in_augment
                            else:
                                print("Web directory found but no index.html")
                                input("Press Enter to exit...")
                                sys.exit(1)
                        else:
                            print("No web directory found in augment_free")
                            input("Press Enter to exit...")
                            sys.exit(1)
                    else:
                        print("No augment_free directory found")
                        input("Press Enter to exit...")
                        sys.exit(1)
                else:
                    input("Press Enter to exit...")
                    sys.exit(1)

        # Get icon path
        print("Locating icon...")
        icon_path = get_icon_path()
        if icon_path:
            print(f"Icon path: {icon_path}")
        else:
            print("No icon found")

        # Create webview window
        print("Creating webview window...")
        window_kwargs = {
            "title": "Augment-Code-Free",
            "url": index_path,
            "js_api": api,
            "width": 1000,
            "height": 700,
            "min_size": (800, 600),
            "resizable": True,
            "shadow": True,
            "on_top": False,
        }

        # Print icon path if available (icon will be set via webview.start())
        if icon_path:
            print(f"Using icon: {icon_path}")

        window = webview.create_window(**window_kwargs)

        # Set up window loaded callback for Windows icon setting
        if icon_path and sys.platform == "win32":
            window.events.loaded += window_loaded

        print("Starting Free AugmentCode...")
        print("Close the application window to exit.")

        # Start the application
        try:
            # Start webview (icon parameter only works on GTK/QT, not Windows)
            if sys.platform == "win32":
                # On Windows, start without icon parameter and set it manually
                webview.start(debug=False)
            else:
                # On Linux/Mac, use the icon parameter
                start_kwargs = {"debug": False}
                if icon_path:
                    start_kwargs["icon"] = icon_path
                webview.start(**start_kwargs)

        except KeyboardInterrupt:
            print("\nApplication interrupted by user")
        except Exception as e:
            print(f"Error starting application: {e}")
            import traceback
            traceback.print_exc()

            # If running as executable, keep console open
            if getattr(sys, "frozen", False):
                input("Press Enter to exit...")

            sys.exit(1)

    except Exception as e:
        print(f"Fatal error during initialization: {e}")
        import traceback
        traceback.print_exc()

        # If running as executable, keep console open
        if getattr(sys, "frozen", False):
            input("Press Enter to exit...")

        sys.exit(1)


def window_loaded():
    """Callback function called when window is loaded."""
    icon_path = get_icon_path()
    if icon_path and sys.platform == "win32":
        # Set Windows icon after window is created
        import threading
        threading.Thread(target=set_windows_icon, args=(icon_path,), daemon=True).start()


if __name__ == "__main__":
    main()
