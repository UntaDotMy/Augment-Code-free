"""
IDE Detection Module for Free AugmentCode.

This module provides intelligent detection of installed IDEs across different platforms.
Supports VSCode variants and JetBrains IDEs.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import json


class IDEInfo:
    """Information about a detected IDE."""

    def __init__(self, name: str, display_name: str, ide_type: str, config_path: str, icon: str = "📝", version: str = None, executable_path: str = None):
        self.name = name  # Internal name (e.g., "Code", "VSCodium")
        self.display_name = display_name  # Display name (e.g., "VS Code", "VSCodium")
        self.ide_type = ide_type  # "vscode" or "jetbrains"
        self.config_path = config_path  # Configuration directory path
        self.icon = icon  # Emoji icon for display
        self.version = version  # IDE version if available
        self.executable_path = executable_path  # Path to executable if found

        # Verified paths (will be populated by _verify_paths)
        self.storage_path = None
        self.db_path = None
        self.machine_id_path = None
        self.workspace_storage_path = None
        self.global_storage_path = None
        self.permanent_device_id_path = None
        self.permanent_user_id_path = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "ide_type": self.ide_type,
            "config_path": self.config_path,
            "icon": self.icon,
            "version": self.version,
            "executable_path": self.executable_path,
            "storage_path": self.storage_path,
            "db_path": self.db_path,
            "machine_id_path": self.machine_id_path,
            "workspace_storage_path": self.workspace_storage_path,
            "global_storage_path": self.global_storage_path,
            "permanent_device_id_path": self.permanent_device_id_path,
            "permanent_user_id_path": self.permanent_user_id_path
        }


class IDEDetector:
    """Cross-platform IDE detector."""

    def __init__(self):
        self.detected_ides: List[IDEInfo] = []

    def _verify_ide_paths(self, ide_info: IDEInfo) -> None:
        """Verify and find actual paths for IDE files and directories."""
        if not ide_info.config_path or not Path(ide_info.config_path).exists():
            return

        config_path = Path(ide_info.config_path)

        if ide_info.ide_type == 'jetbrains':
            # JetBrains IDE paths
            device_id_file = config_path / "PermanentDeviceId"
            user_id_file = config_path / "PermanentUserId"

            if device_id_file.exists():
                ide_info.permanent_device_id_path = str(device_id_file)
            if user_id_file.exists():
                ide_info.permanent_user_id_path = str(user_id_file)

        else:
            # VSCode series paths
            user_dir = config_path / "User"
            if user_dir.exists():
                # Look for globalStorage directory
                global_storage = user_dir / "globalStorage"
                if global_storage.exists():
                    # Set the globalStorage directory path
                    ide_info.global_storage_path = str(global_storage)

                    # Check for storage.json
                    storage_file = global_storage / "storage.json"
                    if storage_file.exists():
                        ide_info.storage_path = str(storage_file)

                    # Check for state.vscdb
                    db_file = global_storage / "state.vscdb"
                    if db_file.exists():
                        ide_info.db_path = str(db_file)

                # Check for machineid file
                machine_id_file = user_dir / "machineid"
                if machine_id_file.exists():
                    ide_info.machine_id_path = str(machine_id_file)

                # Check for workspaceStorage directory
                workspace_storage_dir = user_dir / "workspaceStorage"
                if workspace_storage_dir.exists():
                    ide_info.workspace_storage_path = str(workspace_storage_dir)

            # Also check for machineid in root config directory (some versions)
            root_machine_id = config_path / "machineid"
            if root_machine_id.exists() and not ide_info.machine_id_path:
                ide_info.machine_id_path = str(root_machine_id)

    def get_standard_directories(self) -> List[Path]:
        """Get standard directories where IDEs might store configuration."""
        dirs = []

        if sys.platform == "win32":
            # Windows
            if appdata := os.getenv("APPDATA"):
                dirs.append(Path(appdata))
            if localappdata := os.getenv("LOCALAPPDATA"):
                dirs.append(Path(localappdata))
        elif sys.platform == "darwin":
            # macOS
            home = Path.home()
            dirs.extend([
                home / "Library" / "Application Support",
                home / "Library" / "Preferences",
                home / ".config"
            ])
        else:
            # Linux and other Unix-like systems
            home = Path.home()
            dirs.extend([
                home / ".config",
                home / ".local" / "share",
                home / ".cache"
            ])

        # Add home directory as fallback
        dirs.append(Path.home())

        return [d for d in dirs if d.exists()]

    def detect_vscode_variants(self) -> List[IDEInfo]:
        """Detect VSCode and its variants."""
        vscode_variants = []

        # Known VSCode variant names and their display info
        known_variants = {
            "Code": {"display": "VS Code", "icon": "💙"},
            "Code - Insiders": {"display": "VS Code Insiders", "icon": "💙"},
            "VSCodium": {"display": "VSCodium", "icon": "🔷"},
            "Cursor": {"display": "Cursor", "icon": "🎯"},
            "Code - OSS": {"display": "Code - OSS", "icon": "🔶"},
            "code-oss": {"display": "Code - OSS", "icon": "🔶"},
            "Codium": {"display": "Codium", "icon": "🔷"},
            "code": {"display": "Code", "icon": "💙"},
        }

        base_dirs = self.get_standard_directories()

        for base_dir in base_dirs:
            try:
                # Scan for directories that might be VSCode variants
                for item in base_dir.iterdir():
                    if not item.is_dir():
                        continue

                    item_name = item.name

                    # Check if this looks like a VSCode variant
                    for variant_name, variant_info in known_variants.items():
                        if item_name == variant_name or item_name.lower() == variant_name.lower():
                            # Check if it has the expected VSCode structure
                            user_dir = item / "User"
                            global_storage = user_dir / "globalStorage"

                            if user_dir.exists() and global_storage.exists():
                                # Try to get version information
                                version = self._get_vscode_version(item)

                                ide_info = IDEInfo(
                                    name=variant_name,
                                    display_name=variant_info["display"],
                                    ide_type="vscode",
                                    config_path=str(item),
                                    icon=variant_info["icon"],
                                    version=version
                                )

                                # Verify and find actual paths
                                self._verify_ide_paths(ide_info)

                                vscode_variants.append(ide_info)
                                break
            except (PermissionError, OSError):
                # Skip directories we can't access
                continue

        return vscode_variants

    def detect_jetbrains_ides(self) -> List[IDEInfo]:
        """Detect JetBrains IDEs."""
        jetbrains_ides = []

        # Known JetBrains IDE patterns
        jetbrains_patterns = {
            "IntelliJIdea": {"display": "IntelliJ IDEA", "icon": "🧠"},
            "PyCharm": {"display": "PyCharm", "icon": "🐍"},
            "WebStorm": {"display": "WebStorm", "icon": "🚀"},
            "PhpStorm": {"display": "PhpStorm", "icon": "🐘"},
            "RubyMine": {"display": "RubyMine", "icon": "💎"},
            "CLion": {"display": "CLion", "icon": "⚙️"},
            "DataGrip": {"display": "DataGrip", "icon": "🗄️"},
            "GoLand": {"display": "GoLand", "icon": "🐹"},
            "Rider": {"display": "Rider", "icon": "🏇"},
            "AndroidStudio": {"display": "Android Studio", "icon": "🤖"},
        }

        base_dirs = self.get_standard_directories()

        for base_dir in base_dirs:
            jetbrains_dir = base_dir / "JetBrains"
            if not jetbrains_dir.exists():
                continue

            try:
                for item in jetbrains_dir.iterdir():
                    if not item.is_dir():
                        continue

                    item_name = item.name

                    # Check for JetBrains IDE patterns
                    for pattern, info in jetbrains_patterns.items():
                        if pattern.lower() in item_name.lower():
                            # Verify it's a valid JetBrains IDE directory
                            if self._is_valid_jetbrains_dir(item):
                                # Try to get version information
                                version = self._get_jetbrains_version(item)

                                ide_info = IDEInfo(
                                    name=item_name,
                                    display_name=info["display"],
                                    ide_type="jetbrains",
                                    config_path=str(item),
                                    icon=info["icon"],
                                    version=version
                                )

                                # Verify and find actual paths
                                self._verify_ide_paths(ide_info)

                                jetbrains_ides.append(ide_info)
                                break
            except (PermissionError, OSError):
                continue

        return jetbrains_ides

    def _is_valid_jetbrains_dir(self, path: Path) -> bool:
        """Check if a directory is a valid JetBrains IDE configuration directory."""
        # Look for common JetBrains configuration files/directories
        indicators = ["options", "config", "system", "plugins"]
        return any((path / indicator).exists() for indicator in indicators)

    def _get_vscode_version(self, config_path: Path) -> str:
        """Try to get VSCode version from configuration."""
        try:
            # Try to read from product.json or other version files
            product_json = config_path / "product.json"
            if product_json.exists():
                with open(product_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('version', 'Unknown')

            # Try to read from User/settings.json or other files
            user_dir = config_path / "User"
            if user_dir.exists():
                # Look for any version indicators in the user directory
                for file in user_dir.glob("*.json"):
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if 'version' in data:
                                return data['version']
                    except:
                        continue
        except:
            pass
        return None

    def _get_jetbrains_version(self, config_path: Path) -> str:
        """Try to get JetBrains IDE version from configuration."""
        try:
            # JetBrains IDEs often have version info in the directory name
            dir_name = config_path.name
            # Extract version from directory name like "IntelliJIdea2023.1"
            import re
            version_match = re.search(r'(\d{4}\.\d+)', dir_name)
            if version_match:
                return version_match.group(1)

            # Try to read from options or config files
            options_dir = config_path / "options"
            if options_dir.exists():
                for file in options_dir.glob("*.xml"):
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            version_match = re.search(r'version="([^"]+)"', content)
                            if version_match:
                                return version_match.group(1)
                    except:
                        continue
        except:
            pass
        return None

    def detect_all_ides(self) -> List[IDEInfo]:
        """Detect all supported IDEs."""
        all_ides = []

        # Detect VSCode variants
        all_ides.extend(self.detect_vscode_variants())

        # Detect JetBrains IDEs
        all_ides.extend(self.detect_jetbrains_ides())

        # Remove duplicates based on config path and display name
        seen_items = set()
        unique_ides = []
        for ide in all_ides:
            # Create a unique key combining path and display name
            unique_key = f"{ide.config_path}|{ide.display_name}"
            if unique_key not in seen_items:
                seen_items.add(unique_key)
                unique_ides.append(ide)

        # 强力去重机制：基于display_name进行最终过滤
        final_unique_ides = []
        seen_display_names = set()
        for ide in unique_ides:
            if ide.display_name not in seen_display_names:
                seen_display_names.add(ide.display_name)
                final_unique_ides.append(ide)

        # Sort by IDE type and name
        final_unique_ides.sort(key=lambda x: (x.ide_type, x.display_name))

        self.detected_ides = final_unique_ides
        return final_unique_ides

    def get_default_ides(self) -> List[IDEInfo]:
        """Get the default IDE list (VSCodium and VS Code)."""
        return [
            IDEInfo("VSCodium", "VSCodium", "vscode", "", "🔷"),
            IDEInfo("Code", "VS Code", "vscode", "", "💙")
        ]


def detect_ides() -> Dict[str, Any]:
    """
    Main function to detect IDEs.

    Returns:
        dict: Detection results with IDE list and summary
    """
    try:
        detector = IDEDetector()
        detected_ides = detector.detect_all_ides()

        return {
            "success": True,
            "ides": [ide.to_dict() for ide in detected_ides],
            "count": len(detected_ides),
            "message": f"检测到 {len(detected_ides)} 个IDE"
        }
    except Exception as e:
        return {
            "success": False,
            "ides": [],
            "count": 0,
            "message": f"检测失败: {str(e)}"
        }


if __name__ == "__main__":
    # Test the detector
    result = detect_ides()
    print(json.dumps(result, indent=2, ensure_ascii=False))
