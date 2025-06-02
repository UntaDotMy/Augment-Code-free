"""
Core API class for Free AugmentCode pywebview application.

This module provides the main API interface between the frontend and backend.
"""

import json
import traceback
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


class AugmentFreeAPI:
    """
    Main API class for the Free AugmentCode application.

    This class provides methods that can be called from the frontend
    to perform various operations on AugmentCode data.
    """

    def __init__(self):
        """Initialize the API."""
        self.status = "ready"

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
                    "storage_path": get_storage_path(),
                    "db_path": get_db_path(),
                    "machine_id_path": get_machine_id_path(),
                    "workspace_storage_path": get_workspace_storage_path(),
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
            result = modify_telemetry_ids()
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
            result = clean_augment_data()
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
            result = clean_workspace_storage()
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
