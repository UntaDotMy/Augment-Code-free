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

from .handlers import modify_telemetry_ids, clean_augment_data, clean_workspace_storage
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
        self._config_dir = self._get_config_dir()
        self._first_run_file = self._config_dir / ".augment_free_first_run"

    def set_editor_type(self, editor_type: str) -> Dict[str, Any]:
        """
        Set the editor type for operations.

        Args:
            editor_type (str): Editor type, either "VSCodium" or "Code"

        Returns:
            dict: Operation result
        """
        if editor_type not in ["VSCodium", "Code"]:
            return {
                "success": False,
                "error": "Invalid editor type. Must be 'VSCodium' or 'Code'",
                "message": "Invalid editor type"
            }

        self.editor_type = editor_type
        return {
            "success": True,
            "data": {"editor_type": self.editor_type},
            "message": f"Editor type set to {editor_type}"
        }

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information and paths.

        Returns:
            dict: System information including all relevant paths
        """
        try:
            return {
                "success": True,
                "data": {
                    "home_dir": get_home_dir(),
                    "app_data_dir": get_app_data_dir(),
                    "storage_path": get_storage_path(self.editor_type),
                    "db_path": get_db_path(self.editor_type),
                    "machine_id_path": get_machine_id_path(self.editor_type),
                    "workspace_storage_path": get_workspace_storage_path(self.editor_type),
                    "editor_type": self.editor_type,
                },
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
        Modify telemetry IDs.

        Returns:
            dict: Operation result with backup information and new IDs
        """
        try:
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
        Run all cleaning operations in sequence.

        Returns:
            dict: Combined results from all operations
        """
        results = {
            "telemetry": None,
            "database": None,
            "workspace": None,
            "overall_success": True,
            "errors": []
        }

        # Modify telemetry IDs
        telemetry_result = self.modify_telemetry()
        results["telemetry"] = telemetry_result
        if not telemetry_result["success"]:
            results["overall_success"] = False
            results["errors"].append(f"Telemetry: {telemetry_result['error']}")

        # Clean database
        database_result = self.clean_database()
        results["database"] = database_result
        if not database_result["success"]:
            results["overall_success"] = False
            results["errors"].append(f"Database: {database_result['error']}")

        # Clean workspace
        workspace_result = self.clean_workspace()
        results["workspace"] = workspace_result
        if not workspace_result["success"]:
            results["overall_success"] = False
            results["errors"].append(f"Workspace: {workspace_result['error']}")

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
