"""
Core API class for Free AugmentCode pywebview application.

This module provides the main API interface between the frontend and backend.
"""

import json
import os
import time
import traceback
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional

from .handlers import (
    modify_telemetry_ids,
    clean_augment_data,
    clean_workspace_storage,
    clean_global_storage,
    clean_storage_comprehensive,
    modify_jetbrains_ids,
    get_jetbrains_config_dir,
    get_jetbrains_info,
    run_full_automation,
    close_ide_processes,
    start_ide,
)
from ..utils.session_manager import get_session_status, clear_session_data
from ..utils.paths import (
    get_home_dir,
    get_app_data_dir,
    get_storage_path,
    get_db_path,
    get_machine_id_path,
    get_workspace_storage_path,
    get_global_storage_path,
)
from ..utils.ide_detector import detect_ides, IDEDetector
from ..utils.translation import get_translation_manager, t


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
        self._translation_manager = get_translation_manager()

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
                    "global_storage_path": get_global_storage_path(self.editor_type),
                })

            return {
                "success": True,
                "data": data,
                "message": t("messages.info.system_info_retrieved")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": t("messages.error.system_info_failed")
            }

    def modify_telemetry(self) -> Dict[str, Any]:
        """
        Modify telemetry IDs for all detected IDEs.

        Returns:
            dict: Operation result with backup information and new IDs for all IDEs
        """
        try:
            # Ensure system information is available
            if not self.ensure_system_info_available():
                return {
                    "success": False,
                    "error": "System information not available",
                    "message": "Unable to detect IDE configuration. Please ensure the IDE is properly installed."
                }

            results = {
                "overall_success": True,
                "processed_ides": [],
                "errors": [],
                "results": {}
            }

            # Get all detected IDEs
            detection_result = self.detect_ides()
            if not detection_result["success"] or not detection_result.get("ides"):
                return {
                    "success": False,
                    "error": "No IDEs detected",
                    "message": "Unable to detect any IDEs on the system"
                }

            detected_ides = detection_result["ides"]
            results["processed_ides"] = [ide["display_name"] for ide in detected_ides]

            # Process each detected IDE
            for ide in detected_ides:
                # Validate IDE information
                if not ide or not isinstance(ide, dict):
                    results["errors"].append(f"Invalid IDE information for {ide.get('display_name', 'Unknown IDE')}")
                    continue

                ide_name = ide.get("display_name", "Unknown IDE")
                ide_type = ide.get("ide_type", "vscode")

                try:
                    if ide_type == "jetbrains":
                        # Handle JetBrains IDE
                        jetbrains_config = ide.get("jetbrains_config_path")
                        if not jetbrains_config:
                            jetbrains_config = get_jetbrains_config_dir()
                        
                        if not jetbrains_config:
                            results["errors"].append(f"{ide_name}: JetBrains config directory not found")
                            continue

                        result = modify_jetbrains_ids(jetbrains_config)
                        results["results"][ide_name] = {
                            "success": result["success"],
                            "data": result.get("data", {}),
                            "message": result.get("message", "JetBrains ID处理完成")
                        }
                        
                        if not result["success"]:
                            results["overall_success"] = False
                            results["errors"].append(f"{ide_name}: {result.get('error', 'Unknown error')}")
                    else:
                        # Handle VSCode series
                        storage_path = ide.get("storage_path")
                        machine_id_path = ide.get("machine_id_path")
                        editor_type = ide.get("name", ide.get("editor_type", "VSCodium"))

                        # If no verified paths, try to detect them
                        if not storage_path:
                            storage_path = get_storage_path(editor_type)
                            # Check if the path actually exists
                            if not os.path.exists(storage_path):
                                results["errors"].append(f"{ide_name}: Storage file not found at {storage_path}")
                                continue

                        if not machine_id_path:
                            machine_id_path = get_machine_id_path(editor_type)

                        print(f"🔧 Modifying telemetry IDs for {ide_name}...")
                        result = modify_telemetry_ids(
                            editor_type=editor_type,
                            storage_path=storage_path,
                            machine_id_path=machine_id_path
                        )

                        # Enhanced success message with details
                        success_msg = f"Telemetry IDs modified successfully for {ide_name}"
                        if result.get('id_details'):
                            success_msg += f"\n   • Machine ID: {result['id_details']['machine_id']['new'][:8]}...{result['id_details']['machine_id']['new'][-8:]}"
                            success_msg += f"\n   • Device ID: {result['id_details']['device_id']['new'][:8]}...{result['id_details']['device_id']['new'][-8:]}"

                        results["results"][ide_name] = {
                            "success": True,
                            "data": result,
                            "message": success_msg
                        }

                except Exception as e:
                    results["errors"].append(f"{ide_name}: {str(e)}")
                    results["overall_success"] = False
                    results["results"][ide_name] = {
                        "success": False,
                        "error": str(e),
                        "message": "Failed to modify telemetry IDs"
                    }

            return {
                "success": results["overall_success"],
                "data": results,
                "message": f"Telemetry modification completed for {len(results['processed_ides'])} IDE(s)" if results["overall_success"] else f"Telemetry modification completed with {len(results['errors'])} error(s)"
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
        Clean augment data from SQLite database for all detected VSCode-based IDEs.

        Returns:
            dict: Operation result with backup information and deletion count for all IDEs
        """
        try:
            # Ensure system information is available
            if not self.ensure_system_info_available():
                return {
                    "success": False,
                    "error": "System information not available",
                    "message": "Unable to detect IDE configuration. Please ensure the IDE is properly installed."
                }

            results = {
                "overall_success": True,
                "processed_ides": [],
                "errors": [],
                "results": {}
            }

            # Get all detected IDEs
            detection_result = self.detect_ides()
            if not detection_result["success"] or not detection_result.get("ides"):
                return {
                    "success": False,
                    "error": "No IDEs detected",
                    "message": "Unable to detect any IDEs on the system"
                }

            detected_ides = detection_result["ides"]
            vscode_ides = [ide for ide in detected_ides if ide.get("ide_type") == "vscode"]
            
            if not vscode_ides:
                return {
                    "success": True,
                    "data": {
                        "overall_success": True,
                        "processed_ides": [],
                        "errors": [],
                        "results": {},
                        "message": "No VSCode-based IDEs found (database cleaning not applicable for JetBrains IDEs)"
                    },
                    "message": "No VSCode-based IDEs found for database cleaning"
                }

            results["processed_ides"] = [ide["display_name"] for ide in vscode_ides]

            # Process each VSCode-based IDE
            for ide in vscode_ides:
                # Validate IDE information
                if not ide or not isinstance(ide, dict):
                    results["errors"].append(f"Invalid IDE information for {ide.get('display_name', 'Unknown IDE')}")
                    continue

                ide_name = ide.get("display_name", "Unknown IDE")
                db_path = ide.get("db_path")
                editor_type = ide.get("name", ide.get("editor_type", "VSCodium"))

                try:
                    # If no verified path, try to detect it
                    if not db_path:
                        db_path = get_db_path(editor_type)
                        
                        # Check if the path actually exists
                        if not os.path.exists(db_path):
                            results["errors"].append(f"{ide_name}: Database file not found at {db_path}")
                            continue

                    print(f"🗃️  Cleaning database for {ide_name}...")
                    result = clean_augment_data(
                        editor_type=editor_type,
                        db_path=db_path
                    )

                    # Enhanced success message with details
                    success_msg = f"Database cleaned successfully for {ide_name}"
                    success_msg += f"\n   • Deleted {result['deleted_rows']} Augment-related records"
                    success_msg += f"\n   • {result.get('total_remaining_records', 0)} total records remaining"
                    success_msg += f"\n   • Database size: {result.get('database_size_bytes', 0)} bytes"
                    if result.get('deleted_record_keys'):
                        success_msg += f"\n   • Sample deleted keys: {', '.join(result['deleted_record_keys'][:3])}"
                        if len(result['deleted_record_keys']) > 3:
                            success_msg += f" (and {len(result['deleted_record_keys']) - 3} more)"

                    results["results"][ide_name] = {
                        "success": True,
                        "data": result,
                        "message": success_msg
                    }

                except Exception as e:
                    results["errors"].append(f"{ide_name}: {str(e)}")
                    results["overall_success"] = False
                    results["results"][ide_name] = {
                        "success": False,
                        "error": str(e),
                        "message": "Failed to clean database"
                    }

            return {
                "success": results["overall_success"],
                "data": results,
                "message": f"Database cleaning completed for {len(results['processed_ides'])} IDE(s)" if results["overall_success"] else f"Database cleaning completed with {len(results['errors'])} error(s)"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "message": "Failed to clean database"
            }

    def check_admin_privileges(self) -> Dict[str, Any]:
        """
        Check if the application is running with administrator privileges.

        Returns:
            dict: Admin status information
        """
        try:
            import ctypes
            is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())

            return {
                "success": True,
                "is_admin": is_admin,
                "message": "Administrator privileges detected" if is_admin else "Not running as administrator"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "is_admin": False,
                "message": "Could not check administrator privileges"
            }

    def clean_workspace(self) -> Dict[str, Any]:
        """
        Clean workspace storage for all detected VSCode-based IDEs.

        Returns:
            dict: Operation result with backup information and deletion count for all IDEs
        """
        try:
            # Check admin privileges first
            admin_check = self.check_admin_privileges()
            if not admin_check.get("is_admin", False):
                print("⚠️ Warning: Not running as administrator. Some files may not be deletable.")

            # Ensure system information is available
            if not self.ensure_system_info_available():
                return {
                    "success": False,
                    "error": "System information not available",
                    "message": "Unable to detect IDE configuration. Please ensure the IDE is properly installed."
                }

            results = {
                "overall_success": True,
                "processed_ides": [],
                "errors": [],
                "results": {}
            }

            # Get all detected IDEs
            detection_result = self.detect_ides()
            if not detection_result["success"] or not detection_result.get("ides"):
                return {
                    "success": False,
                    "error": "No IDEs detected",
                    "message": "Unable to detect any IDEs on the system"
                }

            detected_ides = detection_result["ides"]
            vscode_ides = [ide for ide in detected_ides if ide.get("ide_type") == "vscode"]
            
            if not vscode_ides:
                return {
                    "success": True,
                    "data": {
                        "overall_success": True,
                        "processed_ides": [],
                        "errors": [],
                        "results": {},
                        "message": "No VSCode-based IDEs found (workspace cleaning not applicable for JetBrains IDEs)"
                    },
                    "message": "No VSCode-based IDEs found for workspace cleaning"
                }

            results["processed_ides"] = [ide["display_name"] for ide in vscode_ides]

            # Process each VSCode-based IDE
            for ide in vscode_ides:
                # Validate IDE information
                if not ide or not isinstance(ide, dict):
                    results["errors"].append(f"Invalid IDE information for {ide.get('display_name', 'Unknown IDE')}")
                    continue

                ide_name = ide.get("display_name", "Unknown IDE")
                workspace_storage_path = ide.get("workspace_storage_path")
                editor_type = ide.get("name", ide.get("editor_type", "VSCodium"))

                try:
                    # If no verified path, try to detect it
                    if not workspace_storage_path:
                        workspace_storage_path = get_workspace_storage_path(editor_type)
                        
                        # Check if the path actually exists
                        if not os.path.exists(workspace_storage_path):
                            results["errors"].append(f"{ide_name}: Workspace storage directory not found at {workspace_storage_path}")
                            continue

                    print(f"💾 Cleaning workspace storage for {ide_name}...")
                    result = clean_workspace_storage(
                        editor_type=editor_type,
                        workspace_storage_path=workspace_storage_path
                    )

                    # Enhanced success message with details
                    success_msg = f"Workspace cleaned for {ide_name}"
                    success_msg += f"\n   • Files processed: {result.get('deleted_files_count', 0)}"
                    success_msg += f"\n   • Deletion method: {result.get('deletion_method', 'unknown')}"
                    success_msg += f"\n   • Workspace still exists: {'Yes' if result.get('workspace_still_exists') else 'No'}"
                    if result.get('failed_operations'):
                        success_msg += f"\n   • Failed operations: {len(result['failed_operations'])}"
                    if result.get('backup_path'):
                        success_msg += f"\n   • Backup created: {result['backup_path']}"

                    workspace_success = result.get('success', True) and not result.get('workspace_still_exists', True)

                    results["results"][ide_name] = {
                        "success": workspace_success,
                        "data": result,
                        "message": success_msg
                    }

                except Exception as e:
                    results["errors"].append(f"{ide_name}: {str(e)}")
                    results["overall_success"] = False
                    results["results"][ide_name] = {
                        "success": False,
                        "error": str(e),
                        "message": "Failed to clean workspace"
                    }

            return {
                "success": results["overall_success"],
                "data": results,
                "message": f"Workspace cleaning completed for {len(results['processed_ides'])} IDE(s)" if results["overall_success"] else f"Workspace cleaning completed with {len(results['errors'])} error(s)"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "message": "Failed to clean workspace"
            }

    def clean_global_storage(self) -> Dict[str, Any]:
        """
        Clean globalStorage directory for all detected VSCode-based IDEs.

        Returns:
            dict: Operation results for all IDEs
        """
        try:
            # Ensure system information is available
            if not self.ensure_system_info_available():
                return {
                    "success": False,
                    "error": "System information not available",
                    "message": "Unable to detect IDE configuration. Please ensure the IDE is properly installed."
                }

            results = {
                "overall_success": True,
                "errors": [],
                "processed_ides": [],
                "results": {}
            }

            # Get detected IDEs
            detection_result = self.detect_ides()
            if not detection_result["success"] or not detection_result.get("ides"):
                return {
                    "success": False,
                    "error": "No IDEs detected",
                    "message": "No IDEs found for globalStorage cleaning"
                }

            vscode_ides = [ide for ide in detection_result["ides"] if ide.get("type") == "vscode"]
            if not vscode_ides:
                return {
                    "success": False,
                    "error": "No VSCode-based IDEs detected",
                    "message": "GlobalStorage cleaning is only applicable to VSCode-based IDEs"
                }

            # Process each VSCode-based IDE
            for ide in vscode_ides:
                ide_name = ide.get("display_name", "Unknown IDE")
                editor_type = ide.get("editor_type", "VSCodium")
                global_storage_path = ide.get("global_storage_path")

                results["processed_ides"].append(ide_name)

                try:
                    # If no verified path, try to detect it
                    if not global_storage_path:
                        global_storage_path = get_global_storage_path(editor_type)

                        # Check if the path actually exists
                        if not os.path.exists(global_storage_path):
                            results["errors"].append(f"{ide_name}: GlobalStorage directory not found at {global_storage_path}")
                            continue

                    print(f"🗂️ Cleaning globalStorage for {ide_name}...")
                    result = clean_global_storage(
                        editor_type=editor_type,
                        global_storage_path=global_storage_path
                    )

                    # Determine success
                    global_success = result.get('success', True)
                    if not global_success and len(result.get('failed_operations', [])) > 0:
                        global_success = False

                    success_msg = f"GlobalStorage cleaned: {result.get('deleted_files_count', 0)} files deleted"
                    if result.get('backup_path'):
                        success_msg += f", backup created at {result['backup_path']}"

                    results["results"][ide_name] = {
                        "success": global_success,
                        "data": result,
                        "message": success_msg
                    }

                except Exception as e:
                    results["errors"].append(f"{ide_name}: {str(e)}")
                    results["overall_success"] = False
                    results["results"][ide_name] = {
                        "success": False,
                        "error": str(e),
                        "message": "Failed to clean globalStorage"
                    }

            return {
                "success": results["overall_success"],
                "data": results,
                "message": f"GlobalStorage cleaning completed for {len(results['processed_ides'])} IDE(s)" if results["overall_success"] else f"GlobalStorage cleaning completed with {len(results['errors'])} error(s)"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "message": "Failed to clean globalStorage"
            }

    def clean_storage_comprehensive(self, clean_global: bool = True, clean_workspace: bool = True) -> Dict[str, Any]:
        """
        Comprehensive storage cleaning for all detected VSCode-based IDEs.
        Can clean globalStorage, workspaceStorage, or both.

        Args:
            clean_global (bool): Whether to clean globalStorage directories
            clean_workspace (bool): Whether to clean workspaceStorage directories

        Returns:
            dict: Operation results for all IDEs
        """
        try:
            # Ensure system information is available
            if not self.ensure_system_info_available():
                return {
                    "success": False,
                    "error": "System information not available",
                    "message": "Unable to detect IDE configuration. Please ensure the IDE is properly installed."
                }

            results = {
                "overall_success": True,
                "errors": [],
                "processed_ides": [],
                "results": {}
            }

            # Get detected IDEs
            detection_result = self.detect_ides()
            if not detection_result["success"] or not detection_result.get("ides"):
                return {
                    "success": False,
                    "error": "No IDEs detected",
                    "message": "No IDEs found for storage cleaning"
                }

            vscode_ides = [ide for ide in detection_result["ides"] if ide.get("type") == "vscode"]
            if not vscode_ides:
                return {
                    "success": False,
                    "error": "No VSCode-based IDEs detected",
                    "message": "Storage cleaning is only applicable to VSCode-based IDEs"
                }

            # Process each VSCode-based IDE
            for ide in vscode_ides:
                ide_name = ide.get("display_name", "Unknown IDE")
                editor_type = ide.get("editor_type", "VSCodium")
                global_storage_path = ide.get("global_storage_path")
                workspace_storage_path = ide.get("workspace_storage_path")

                results["processed_ides"].append(ide_name)

                try:
                    print(f"🧹 Comprehensive storage cleaning for {ide_name}...")
                    result = clean_storage_comprehensive(
                        editor_type=editor_type,
                        clean_global=clean_global,
                        clean_workspace=clean_workspace,
                        global_storage_path=global_storage_path,
                        workspace_storage_path=workspace_storage_path
                    )

                    # Determine success
                    storage_success = result.get('overall_success', True)

                    operations = result.get('operations_performed', [])
                    operations_text = " and ".join(operations) if operations else "storage"
                    success_msg = f"{operations_text.title()} cleaned: {result.get('total_files_deleted', 0)} files deleted"

                    if result.get('backup_paths'):
                        success_msg += f", {len(result['backup_paths'])} backup(s) created"

                    results["results"][ide_name] = {
                        "success": storage_success,
                        "data": result,
                        "message": success_msg
                    }

                    if not storage_success:
                        results["overall_success"] = False

                except Exception as e:
                    results["errors"].append(f"{ide_name}: {str(e)}")
                    results["overall_success"] = False
                    results["results"][ide_name] = {
                        "success": False,
                        "error": str(e),
                        "message": "Failed to clean storage"
                    }

            return {
                "success": results["overall_success"],
                "data": results,
                "message": f"Storage cleaning completed for {len(results['processed_ides'])} IDE(s)" if results["overall_success"] else f"Storage cleaning completed with {len(results['errors'])} error(s)"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "message": "Failed to clean storage"
            }

    def run_all_operations(self) -> Dict[str, Any]:
        """
        Run all cleaning operations in sequence for all detected IDEs.
        This method orchestrates the individual operations that now handle all IDEs.

        Returns:
            dict: Combined results from all operations
        """
        try:
            # Ensure system information is available
            if not self.ensure_system_info_available():
                return {
                    "success": False,
                    "error": "System information not available",
                    "message": "Unable to detect IDE configuration. Please ensure the IDE is properly installed."
                }

            results = {
                "overall_success": True,
                "errors": [],
                "steps": {}
            }

            # Step 1: Modify telemetry IDs for all IDEs
            print("🔄 Step 1/3: Modifying telemetry IDs for all IDEs...")
            telemetry_result = self.modify_telemetry()
            results["steps"]["telemetry"] = telemetry_result
            if not telemetry_result["success"]:
                results["overall_success"] = False
                results["errors"].append(f"Telemetry: {telemetry_result.get('error', 'Unknown error')}")

            # Step 2: Clean database for all VSCode-based IDEs
            print("🔄 Step 2/3: Cleaning databases for all VSCode-based IDEs...")
            database_result = self.clean_database()
            results["steps"]["database"] = database_result
            if not database_result["success"]:
                results["overall_success"] = False
                results["errors"].append(f"Database: {database_result.get('error', 'Unknown error')}")

            # Step 3: Clean workspace for all VSCode-based IDEs
            print("🔄 Step 3/3: Cleaning workspaces for all VSCode-based IDEs...")
            workspace_result = self.clean_workspace()
            results["steps"]["workspace"] = workspace_result
            if not workspace_result["success"]:
                results["overall_success"] = False
                results["errors"].append(f"Workspace: {workspace_result.get('error', 'Unknown error')}")

            # Compile summary
            total_processed = 0
            if telemetry_result.get("data", {}).get("processed_ides"):
                total_processed = max(total_processed, len(telemetry_result["data"]["processed_ides"]))
            if database_result.get("data", {}).get("processed_ides"):
                total_processed = max(total_processed, len(database_result["data"]["processed_ides"]))
            if workspace_result.get("data", {}).get("processed_ides"):
                total_processed = max(total_processed, len(workspace_result["data"]["processed_ides"]))

            return {
                "success": results["overall_success"],
                "data": results,
                "message": t("messages.success.all_operations_completed") if results["overall_success"] else t("messages.error.some_operations_failed")
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "message": "Failed to run all operations"
            }

    def run_full_automation(self, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run the complete automation workflow:
        1. Auto Signout (close IDE)
        2. Auto DB Cleaning (clean all data)
        3. Auto Signin (ready for new login)
        4. Auto Restart IDE

        Args:
            options: Automation options
                - include_signout: bool (default: True)
                - include_cleaning: bool (default: True)
                - include_signin: bool (default: True)
                - include_restart: bool (default: True)
                - target_ide: str (optional, IDE display name to target)
                - clean_all_ides: bool (default: False, if True cleans all detected IDEs)

        Returns:
            dict: Automation results
        """
        try:
            if options is None:
                options = {}

            # Ensure system information is available
            if not self.ensure_system_info_available():
                return {
                    "success": False,
                    "error": "System information not available",
                    "message": "Unable to detect IDE configuration. Please ensure the IDE is properly installed."
                }

            # Get target IDE (only if not cleaning all IDEs)
            target_ide = None
            clean_all_ides = options.get("clean_all_ides", False)
            
            if not clean_all_ides:
                target_ide_name = options.get("target_ide")

                if target_ide_name:
                    # Find specific IDE
                    detection_result = self.detect_ides()
                    if detection_result["success"] and detection_result.get("ides"):
                        for ide in detection_result["ides"]:
                            if ide.get("display_name") == target_ide_name:
                                target_ide = ide
                                break

                    if target_ide is None:
                        return {
                            "success": False,
                            "error": f"Target IDE '{target_ide_name}' not found",
                            "message": t("messages.error.ide_not_found")
                        }
                else:
                    # Use current IDE or auto-detect
                    target_ide = self.current_ide_info

                # Validate target IDE has required information
                if not target_ide or not isinstance(target_ide, dict):
                    return {
                        "success": False,
                        "error": "No valid IDE information available",
                        "message": "Unable to find valid IDE configuration for automation"
                    }

            # Run automation
            result = run_full_automation(
                ide_info=target_ide,
                include_signout=options.get("include_signout", True),
                include_cleaning=options.get("include_cleaning", True),
                include_signin=options.get("include_signin", True),
                include_restart=options.get("include_restart", True),
                clean_all_ides=clean_all_ides
            )

            return {
                "success": result["success"],
                "data": result,
                "message": result["message"]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": t("messages.error.automation_failed")
            }

    def run_full_automation_all_ides(self, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run the complete automation workflow for all detected IDEs:
        1. Auto Signout (close all IDEs)
        2. Auto DB Cleaning (clean all data for all IDEs)
        3. Auto Signin (ready for new login)
        4. Auto Restart IDE (start all IDEs)

        Args:
            options: Automation options
                - include_signout: bool (default: True)
                - include_cleaning: bool (default: True)
                - include_signin: bool (default: True)
                - include_restart: bool (default: True)

        Returns:
            dict: Automation results for all IDEs
        """
        try:
            if options is None:
                options = {}

            # Ensure system information is available
            if not self.ensure_system_info_available():
                return {
                    "success": False,
                    "error": "System information not available",
                    "message": "Unable to detect IDE configuration. Please ensure the IDE is properly installed."
                }

            # Set clean_all_ides to True
            options["clean_all_ides"] = True

            # Run automation for all IDEs
            result = run_full_automation(
                ide_info=None,  # Will be ignored when clean_all_ides is True
                include_signout=options.get("include_signout", True),
                include_cleaning=options.get("include_cleaning", True),
                include_signin=options.get("include_signin", True),
                include_restart=options.get("include_restart", True),
                clean_all_ides=True
            )

            return {
                "success": result["success"],
                "data": result,
                "message": result["message"]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": t("messages.error.automation_failed")
            }

    def close_ide(self, ide_name: str = None) -> Dict[str, Any]:
        """
        Close IDE processes.

        Args:
            ide_name: Specific IDE name to close, if None uses current IDE

        Returns:
            dict: Operation result
        """
        try:
            target_ide = None

            if ide_name:
                # Find specific IDE
                detection_result = self.detect_ides()
                if detection_result["success"] and detection_result.get("ides"):
                    for ide in detection_result["ides"]:
                        if ide.get("display_name") == ide_name:
                            target_ide = ide
                            break
            else:
                target_ide = self.current_ide_info

            if target_ide is None:
                return {
                    "success": False,
                    "error": "No IDE specified or detected",
                    "message": t("messages.error.no_ide_detected")
                }

            result = close_ide_processes(target_ide)

            return {
                "success": result["success"],
                "data": result,
                "message": result["message"]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": t("messages.error.close_ide_failed")
            }

    def start_ide(self, ide_name: str = None) -> Dict[str, Any]:
        """
        Start IDE.

        Args:
            ide_name: Specific IDE name to start, if None uses current IDE

        Returns:
            dict: Operation result
        """
        try:
            target_ide = None

            if ide_name:
                # Find specific IDE
                detection_result = self.detect_ides()
                if detection_result["success"] and detection_result.get("ides"):
                    for ide in detection_result["ides"]:
                        if ide.get("display_name") == ide_name:
                            target_ide = ide
                            break
            else:
                target_ide = self.current_ide_info

            if target_ide is None:
                return {
                    "success": False,
                    "error": "No IDE specified or detected",
                    "message": t("messages.error.no_ide_detected")
                }

            result = start_ide(target_ide)

            return {
                "success": result["success"],
                "data": result,
                "message": result["message"]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": t("messages.error.start_ide_failed")
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
            "message": t("messages.info.api_ready")
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

            version = "0.1.2"  # Default version

            if pyproject_file.exists():
                with open(pyproject_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Use regex to extract version more reliably (same as build.py)
                    import re
                    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        version = match.group(1)

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

    def get_current_language(self) -> Dict[str, Any]:
        """
        Get the current language setting.

        Returns:
            dict: Current language information
        """
        try:
            current_lang = self._translation_manager.get_current_language()
            available_langs = self._translation_manager.get_available_languages()

            return {
                "success": True,
                "data": {
                    "current_language": current_lang,
                    "available_languages": available_langs
                },
                "message": t("messages.info.language_retrieved")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": t("messages.error.language_get_failed")
            }

    def set_language(self, language_code: str) -> Dict[str, Any]:
        """
        Set the application language.

        Args:
            language_code (str): Language code (e.g., "zh_CN", "en_US")

        Returns:
            dict: Operation result
        """
        try:
            success = self._translation_manager.set_language(language_code)

            if success:
                return {
                    "success": True,
                    "data": {
                        "language": language_code,
                        "display_name": self._translation_manager.get_available_languages().get(language_code, language_code)
                    },
                    "message": t("messages.success.language_changed")
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid language code",
                    "message": t("messages.error.language_change_failed")
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": t("messages.error.language_change_failed")
            }

    def get_translations(self, language_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all translations for a specific language.

        Args:
            language_code (str, optional): Language code. Uses current language if not specified.

        Returns:
            dict: All translations for the specified language
        """
        try:
            translations = self._translation_manager.get_all_translations(language_code)
            current_lang = language_code or self._translation_manager.get_current_language()

            return {
                "success": True,
                "data": {
                    "language": current_lang,
                    "translations": translations
                },
                "message": t("messages.info.translations_retrieved")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": t("messages.error.translations_get_failed")
            }

    def refresh_system_info(self) -> Dict[str, Any]:
        """
        Refresh system information by re-detecting IDE paths and configurations.
        This ensures we always use the most up-to-date system information.

        Returns:
            dict: Updated system information
        """
        try:
            # Re-detect IDEs to get fresh information
            detection_result = self.detect_ides()
            if detection_result["success"] and detection_result.get("ides"):
                # Update current IDE info with the most relevant one
                for ide in detection_result["ides"]:
                    if ide.get("name") == self.editor_type or ide.get("display_name") == self.editor_type:
                        self.current_ide_info = ide
                        break
                else:
                    # If current editor not found, use the first detected IDE
                    self.current_ide_info = detection_result["ides"][0]
                    self.editor_type = self.current_ide_info.get("name", self.current_ide_info.get("editor_type", "VSCodium"))

            # Get updated system info
            return self.get_system_info()
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to refresh system information"
            }

    def get_diagnostic_info(self) -> Dict[str, Any]:
        """
        Get comprehensive diagnostic information for troubleshooting.

        Returns:
            dict: Diagnostic information
        """
        try:
            print("\n" + "="*60)
            print("🔍 SYSTEM DIAGNOSTIC INFORMATION")
            print("="*60)

            diagnostic = {
                'timestamp': time.time(),
                'admin_status': self.check_admin_privileges(),
                'system_info': self.get_system_info(),
                'ide_detection': self.detect_ides(),
                'session_status': {}
            }

            # Display admin status
            admin_info = diagnostic['admin_status']
            print(f"🔐 Administrator Status: {'✅ Running as Admin' if admin_info.get('is_admin') else '❌ Not Admin'}")

            # Display system info
            sys_info = diagnostic['system_info']
            if sys_info.get('success'):
                data = sys_info.get('data', {})
                print(f"🏠 Home Directory: {data.get('home_dir', 'Unknown')}")
                print(f"📁 App Data Directory: {data.get('app_data_dir', 'Unknown')}")
                print(f"🎯 Current Editor: {data.get('editor_type', 'Unknown')}")

            # Display IDE detection results
            ide_info = diagnostic['ide_detection']
            if ide_info.get('success'):
                ides = ide_info.get('ides', [])
                print(f"\n🔍 Detected IDEs ({len(ides)}):")
                for i, ide in enumerate(ides, 1):
                    print(f"   {i}. {ide.get('display_name', 'Unknown')} ({ide.get('ide_type', 'unknown')})")
                    if ide.get('editor_path'):
                        exists = os.path.exists(ide.get('editor_path', ''))
                        print(f"      Path: {ide.get('editor_path')} {'✅' if exists else '❌'}")

                    # Check key paths for VSCode-based IDEs
                    if ide.get('ide_type') == 'vscode':
                        storage_path = ide.get('storage_path')
                        db_path = ide.get('db_path')
                        workspace_path = ide.get('workspace_storage_path')

                        if storage_path:
                            exists = os.path.exists(storage_path)
                            print(f"      Storage: {'✅ Found' if exists else '❌ Missing'}")
                        if db_path:
                            exists = os.path.exists(db_path)
                            print(f"      Database: {'✅ Found' if exists else '❌ Missing'}")
                        if workspace_path:
                            exists = os.path.exists(workspace_path)
                            print(f"      Workspace: {'✅ Found' if exists else '❌ Missing'}")

            # Get session status for each detected IDE
            print(f"\n📊 Session Status:")
            if diagnostic['ide_detection'].get('success'):
                for ide in diagnostic['ide_detection'].get('ides', []):
                    editor_type = ide.get('name', ide.get('editor_type', 'Unknown'))
                    try:
                        session_status = get_session_status(editor_type)
                        diagnostic['session_status'][editor_type] = session_status

                        if session_status.get('success'):
                            total_files = session_status.get('total_session_files', 0)
                            locked_files = session_status.get('locked_files', 0)
                            print(f"   {editor_type}: {total_files} session files, {locked_files} locked")
                        else:
                            print(f"   {editor_type}: Error - {session_status.get('error', 'Unknown')}")
                    except Exception as e:
                        diagnostic['session_status'][editor_type] = {
                            'success': False,
                            'error': str(e)
                        }
                        print(f"   {editor_type}: Exception - {e}")

            print("="*60)

            return {
                'success': True,
                'data': diagnostic,
                'message': 'Diagnostic information collected and displayed'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to collect diagnostic information'
            }

    def ensure_system_info_available(self) -> bool:
        """
        Ensure that system information is available before performing operations.
        This method validates that we have the necessary paths and configurations.

        Returns:
            bool: True if system information is available and valid
        """
        try:
            # If we don't have current IDE info, try to detect it
            if not self.current_ide_info:
                self.refresh_system_info()
                return self.current_ide_info is not None

            # Validate that we have the necessary paths for the current IDE type
            ide_type = self.current_ide_info.get("ide_type", "vscode")

            if ide_type == "jetbrains":
                # For JetBrains, we need the config path
                if not self.current_ide_info.get("jetbrains_config_path"):
                    self.refresh_system_info()
                    return self.current_ide_info.get("jetbrains_config_path") is not None
            else:
                # For VSCode series, we need at least storage path
                if not self.current_ide_info.get("storage_path"):
                    self.refresh_system_info()
                    return self.current_ide_info.get("storage_path") is not None

            return True
        except Exception:
            return False


