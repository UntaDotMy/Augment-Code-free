"""
Core API class for Free AugmentCode pywebview application.

This module provides the main API interface between the frontend and backend.
"""

import json
import os
import traceback
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional

from .handlers import (
    modify_telemetry_ids,
    clean_augment_data,
    clean_workspace_storage,
    modify_jetbrains_ids,
    get_jetbrains_config_dir,
    get_jetbrains_info
)
from ..utils.paths import (
    get_home_dir,
    get_app_data_dir,
    get_storage_path,
    get_db_path,
    get_machine_id_path,
    get_workspace_storage_path,
)
from ..utils.ide_detector import detect_ides, IDEDetector


class AugmentFreeAPI:
    """
    Main API class for the Free AugmentCode application.

    This class provides methods that can be called from the frontend
    to perform various operations on AugmentCode data.
    """

    def __init__(self):
        """Initialize the API."""
        self.status = "ready"
        self.editor_type = "VSCodium"  # Default editor type
        self.current_ide_info = None  # Store current IDE information
        self._config_dir = self._get_config_dir()
        self._first_run_file = self._config_dir / ".augment_free_first_run"

    def set_editor_type(self, editor_name: str, ide_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Set the editor type for operations.

        Args:
            editor_name (str): Editor name (e.g., "VSCodium", "Code", "IntelliJ IDEA")
            ide_info (dict): Optional IDE information from detection

        Returns:
            dict: Operation result
        """
        self.editor_type = editor_name
        self.current_ide_info = ide_info

        return {
            "success": True,
            "data": {
                "editor_type": self.editor_type,
                "ide_info": self.current_ide_info
            },
            "message": f"Editor type set to {editor_name}"
        }

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information and paths.

        Returns:
            dict: System information including all relevant paths
        """
        try:
            # Determine IDE type
            ide_type = "vscode"  # Default
            if self.current_ide_info:
                ide_type = self.current_ide_info.get("ide_type", "vscode")

            data = {
                "home_dir": get_home_dir(),
                "app_data_dir": get_app_data_dir(),
                "editor_type": self.editor_type,
                "ide_type": ide_type,
            }

            if ide_type == "jetbrains":
                # JetBrains IDE paths
                jetbrains_config = get_jetbrains_config_dir()
                if jetbrains_config:
                    jetbrains_info = get_jetbrains_info(jetbrains_config)
                    data.update({
                        "jetbrains_config_path": jetbrains_config,
                        "jetbrains_info": jetbrains_info,
                        "permanent_device_id_path": os.path.join(jetbrains_config, "PermanentDeviceId"),
                        "permanent_user_id_path": os.path.join(jetbrains_config, "PermanentUserId"),
                    })
                else:
                    data.update({
                        "jetbrains_config_path": "未找到",
                        "permanent_device_id_path": "未找到",
                        "permanent_user_id_path": "未找到",
                    })
            else:
                # VSCode series paths
                data.update({
                    "storage_path": get_storage_path(self.editor_type),
                    "db_path": get_db_path(self.editor_type),
                    "machine_id_path": get_machine_id_path(self.editor_type),
                    "workspace_storage_path": get_workspace_storage_path(self.editor_type),
                })

            return {
                "success": True,
                "data": data,
                "message": "System information retrieved successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve system information"
            }

    def modify_telemetry(self) -> Dict[str, Any]:
        """
        Modify telemetry IDs based on IDE type.

        Returns:
            dict: Operation result with backup information and new IDs
        """
        try:
            # Determine IDE type
            ide_type = "vscode"  # Default
            if self.current_ide_info:
                ide_type = self.current_ide_info.get("ide_type", "vscode")

            if ide_type == "jetbrains":
                # Handle JetBrains IDE
                jetbrains_config = get_jetbrains_config_dir()
                if not jetbrains_config:
                    return {
                        "success": False,
                        "error": "JetBrains配置目录未找到",
                        "message": "无法找到JetBrains配置目录"
                    }

                result = modify_jetbrains_ids(jetbrains_config)
                return {
                    "success": result["success"],
                    "data": result.get("data", {}),
                    "message": result.get("message", "JetBrains ID处理完成")
                }
            else:
                # Handle VSCode series
                result = modify_telemetry_ids(self.editor_type)
                return {
                    "success": True,
                    "data": result,
                    "message": "Telemetry IDs modified successfully"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "message": "Failed to modify telemetry IDs"
            }

    def clean_database(self) -> Dict[str, Any]:
        """
        Clean augment data from SQLite database.

        Returns:
            dict: Operation result with backup information and deletion count
        """
        try:
            result = clean_augment_data(self.editor_type)
            return {
                "success": True,
                "data": result,
                "message": f"Database cleaned successfully. Deleted {result['deleted_rows']} rows."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "message": "Failed to clean database"
            }

    def clean_workspace(self) -> Dict[str, Any]:
        """
        Clean workspace storage.

        Returns:
            dict: Operation result with backup information and deletion count
        """
        try:
            result = clean_workspace_storage(self.editor_type)
            return {
                "success": True,
                "data": result,
                "message": f"Workspace cleaned successfully. Deleted {result['deleted_files_count']} files."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "message": "Failed to clean workspace"
            }

    def run_all_operations(self) -> Dict[str, Any]:
        """
        Run all cleaning operations in sequence based on IDE type.

        Returns:
            dict: Combined results from all operations
        """
        # Determine IDE type
        ide_type = "vscode"  # Default
        if self.current_ide_info:
            ide_type = self.current_ide_info.get("ide_type", "vscode")

        results = {
            "telemetry": None,
            "overall_success": True,
            "errors": [],
            "ide_type": ide_type
        }

        # Always modify telemetry IDs (works for both VSCode and JetBrains)
        telemetry_result = self.modify_telemetry()
        results["telemetry"] = telemetry_result
        if not telemetry_result["success"]:
            results["overall_success"] = False
            results["errors"].append(f"Telemetry: {telemetry_result.get('error', 'Unknown error')}")

        if ide_type == "vscode":
            # VSCode series: also clean database and workspace
            database_result = self.clean_database()
            results["database"] = database_result
            if not database_result["success"]:
                results["overall_success"] = False
                results["errors"].append(f"Database: {database_result.get('error', 'Unknown error')}")

            workspace_result = self.clean_workspace()
            results["workspace"] = workspace_result
            if not workspace_result["success"]:
                results["overall_success"] = False
                results["errors"].append(f"Workspace: {workspace_result.get('error', 'Unknown error')}")
        else:
            # JetBrains: only telemetry modification is needed
            results["database"] = {"success": True, "message": "不适用于JetBrains IDE"}
            results["workspace"] = {"success": True, "message": "不适用于JetBrains IDE"}

        return {
            "success": results["overall_success"],
            "data": results,
            "message": "All operations completed" if results["overall_success"] else "Some operations failed"
        }

    def get_status(self) -> Dict[str, Any]:
        """
        Get API status.

        Returns:
            dict: Current API status
        """
        return {
            "success": True,
            "data": {"status": self.status},
            "message": "API is ready"
        }

    def get_version_info(self) -> Dict[str, Any]:
        """
        Get application version information.

        Returns:
            dict: Version information from pyproject.toml
        """
        try:
            # Try to find pyproject.toml
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent.parent
            pyproject_file = project_root / "pyproject.toml"

            version = "0.1.0"  # Default version

            if pyproject_file.exists():
                with open(pyproject_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("version"):
                            # Extract version from line like: version = "0.1.0"
                            version = line.split("=")[1].strip().strip('"').strip("'")
                            break

            return {
                "success": True,
                "data": {
                    "version": version,
                    "name": "Free AugmentCode",
                    "author": "vagmr"
                },
                "message": "Version information retrieved successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve version information"
            }

    def open_external_link(self, url: str) -> Dict[str, Any]:
        """
        Open an external link in the default browser.

        Args:
            url (str): URL to open

        Returns:
            dict: Operation result
        """
        try:
            webbrowser.open(url)
            return {
                "success": True,
                "data": {"url": url},
                "message": f"Opened {url} in browser"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to open {url}"
            }

    def _get_config_dir(self) -> Path:
        """
        Get the configuration directory for storing app settings.

        Returns:
            Path: Configuration directory path
        """
        try:
            # Use user's home directory for config
            home_dir = Path.home()
            config_dir = home_dir / ".augment_free"

            # Create directory if it doesn't exist
            config_dir.mkdir(exist_ok=True)

            return config_dir
        except Exception:
            # Fallback to current directory
            return Path(".")

    def is_first_run(self) -> Dict[str, Any]:
        """
        Check if this is the first time running the application.

        Returns:
            dict: Result with first_run boolean
        """
        try:
            is_first = not self._first_run_file.exists()

            return {
                "success": True,
                "data": {"is_first_run": is_first},
                "message": "First run check completed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to check first run status"
            }

    def mark_first_run_complete(self) -> Dict[str, Any]:
        """
        Mark that the first run has been completed.

        Returns:
            dict: Operation result
        """
        try:
            # Create the marker file
            self._first_run_file.touch()

            return {
                "success": True,
                "data": {"marked": True},
                "message": "First run marked as complete"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to mark first run as complete"
            }

    def detect_ides(self) -> Dict[str, Any]:
        """
        Detect all installed IDEs on the system.

        Returns:
            dict: Detection results with IDE list and summary
        """
        try:
            result = detect_ides()
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"IDE检测失败: {str(e)}"
            }

    def get_default_ides(self) -> Dict[str, Any]:
        """
        Get the default IDE list (VSCodium and VS Code).

        Returns:
            dict: Default IDE list
        """
        try:
            detector = IDEDetector()
            default_ides = detector.get_default_ides()

            return {
                "success": True,
                "ides": [ide.to_dict() for ide in default_ides],
                "count": len(default_ides),
                "message": "默认IDE列表"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"获取默认IDE列表失败: {str(e)}"
            }

    def get_supported_operations(self) -> Dict[str, Any]:
        """
        Get supported operations for the current IDE type.

        Returns:
            dict: List of supported operations
        """
        try:
            # Determine IDE type
            ide_type = "vscode"  # Default
            if self.current_ide_info:
                ide_type = self.current_ide_info.get("ide_type", "vscode")

            if ide_type == "jetbrains":
                operations = [
                    {
                        "id": "telemetry",
                        "name": "重置设备ID",
                        "description": "重置JetBrains IDE的设备标识符",
                        "icon": "🔑",
                        "supported": True
                    }
                ]
            else:
                operations = [
                    {
                        "id": "telemetry",
                        "name": "重置机器码",
                        "description": "重置设备 ID 和机器 ID，生成新的随机标识符",
                        "icon": "🔑",
                        "supported": True
                    },
                    {
                        "id": "database",
                        "name": "清理数据库",
                        "description": "清理 SQLite 数据库中包含 'augment' 的记录",
                        "icon": "🗃️",
                        "supported": True
                    },
                    {
                        "id": "workspace",
                        "name": "清理工作区",
                        "description": "清理工作区存储文件和目录",
                        "icon": "💾",
                        "supported": True
                    }
                ]

            return {
                "success": True,
                "data": {
                    "ide_type": ide_type,
                    "operations": operations
                },
                "message": f"获取{ide_type}支持的操作列表"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"获取支持操作失败: {str(e)}"
            }
