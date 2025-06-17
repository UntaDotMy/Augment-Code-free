"""
Automation handler for Free AugmentCode.

This module provides comprehensive automation workflows that combine
multiple operations in sequence with IDE management.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. Process management features will be limited.")

from ..handlers.telemetry import modify_telemetry_ids
from ..handlers.database import clean_augment_data
from ..handlers.workspace import clean_workspace_storage, clean_global_storage
from ..handlers.jetbrains import modify_jetbrains_ids, get_jetbrains_config_dir
from ...utils.ide_detector import detect_ides, IDEDetector
from ...utils.translation import t
from ...utils.session_manager import clear_session_data, get_session_status
from ...utils.paths import get_storage_path, get_db_path, get_workspace_storage_path, get_global_storage_path, get_machine_id_path
from ...utils.operation_reporter import report_automation_summary


def find_ide_processes(ide_info: Dict[str, Any]) -> List[psutil.Process]:
    """
    Find running processes for a specific IDE.
    
    Args:
        ide_info: IDE information dictionary
        
    Returns:
        List of running IDE processes
    """
    processes = []
    ide_name = ide_info.get("display_name", "").lower()
    
    # Common IDE process names
    process_names = []
    if "code" in ide_name or "vscode" in ide_name:
        process_names = ["code.exe", "code", "Code.exe"]
    elif "cursor" in ide_name:
        process_names = ["cursor.exe", "cursor", "Cursor.exe"]
    elif "vscodium" in ide_name:
        process_names = ["vscodium.exe", "vscodium", "VSCodium.exe"]
    elif "intellij" in ide_name:
        process_names = ["idea64.exe", "idea.exe", "idea"]
    elif "pycharm" in ide_name:
        process_names = ["pycharm64.exe", "pycharm.exe", "pycharm"]
    elif "webstorm" in ide_name:
        process_names = ["webstorm64.exe", "webstorm.exe", "webstorm"]
    
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            proc_name = proc.info['name']
            if proc_name and any(name.lower() in proc_name.lower() for name in process_names):
                processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return processes


def close_ide_processes(ide_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Close all running processes for a specific IDE.
    
    Args:
        ide_info: IDE information dictionary
        
    Returns:
        Operation result
    """
    try:
        processes = find_ide_processes(ide_info)
        closed_count = 0
        
        for proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=10)  # Wait up to 10 seconds for graceful shutdown
                closed_count += 1
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                try:
                    proc.kill()  # Force kill if graceful shutdown fails
                    closed_count += 1
                except psutil.NoSuchProcess:
                    pass
            except psutil.AccessDenied:
                continue
        
        return {
            "success": True,
            "closed_processes": closed_count,
            "message": f"已关闭 {closed_count} 个 {ide_info.get('display_name', 'IDE')} 进程"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"关闭 {ide_info.get('display_name', 'IDE')} 进程时出错"
        }


def start_ide(ide_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Start an IDE using its executable path.
    
    Args:
        ide_info: IDE information dictionary
        
    Returns:
        Operation result
    """
    try:
        editor_path = ide_info.get("editor_path")
        if not editor_path or not os.path.exists(editor_path):
            return {
                "success": False,
                "error": "IDE executable not found",
                "message": f"无法找到 {ide_info.get('display_name', 'IDE')} 可执行文件"
            }
        
        # Start the IDE process
        if sys.platform == "win32":
            subprocess.Popen([editor_path], shell=False)
        else:
            subprocess.Popen([editor_path], shell=False)
        
        return {
            "success": True,
            "message": f"已启动 {ide_info.get('display_name', 'IDE')}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"启动 {ide_info.get('display_name', 'IDE')} 时出错"
        }


def run_full_automation(ide_info: Optional[Dict[str, Any]] = None, 
                       include_signout: bool = True,
                       include_cleaning: bool = True, 
                       include_signin: bool = True,
                       include_restart: bool = True,
                       clean_all_ides: bool = False) -> Dict[str, Any]:
    """
    Run the complete automation workflow:
    1. Auto Signout (close IDE)
    2. Auto DB Cleaning (clean all data)
    3. Auto Signin (ready for new login)
    4. Auto Restart IDE
    
    Args:
        ide_info: Specific IDE to target, if None will auto-detect
        include_signout: Whether to close IDE processes
        include_cleaning: Whether to perform cleaning operations
        include_signin: Whether to prepare for signin (currently just a status)
        include_restart: Whether to restart the IDE
        clean_all_ides: Whether to clean all detected IDEs (if True, ignores ide_info parameter)
        
    Returns:
        Comprehensive automation results
    """
    results = {
        "success": True,
        "steps": {},
        "errors": [],
        "ide_info": ide_info,
        "timestamp": time.time()
    }
    
    try:
        # Step 1: Auto-detect IDE if not provided or if cleaning all IDEs
        if ide_info is None or clean_all_ides:
            detection_result = detect_ides()
            if detection_result["success"] and detection_result.get("ides"):
                if clean_all_ides:
                    # Use all detected IDEs
                    detected_ides = detection_result["ides"]
                    results["ide_info"] = detected_ides
                else:
                    # Use first detected IDE
                    ide_info = detection_result["ides"][0]
                    results["ide_info"] = ide_info
            else:
                results["success"] = False
                results["errors"].append("No IDE detected for automation")
                return results
        
        # Step 2: Auto Signout (Close IDE)
        if include_signout:
            if clean_all_ides:
                print("🔄 Step 1/4: Auto Signout - Closing all detected IDEs...")
                signout_results = {}
                for ide in detected_ides:
                    ide_name = ide.get("display_name", "Unknown IDE")
                    print(f"  - Closing {ide_name}...")
                    signout_result = close_ide_processes(ide)
                    signout_results[ide_name] = signout_result
                    if not signout_result["success"]:
                        results["errors"].append(f"{ide_name} signout failed: {signout_result.get('error', 'Unknown error')}")
                results["steps"]["signout"] = signout_results
            else:
                print(f"🔄 Step 1/4: Auto Signout - Closing {ide_info.get('display_name', 'Unknown IDE')}...")
                signout_result = close_ide_processes(ide_info)
                results["steps"]["signout"] = signout_result
                
                if not signout_result["success"]:
                    results["errors"].append(f"Signout failed: {signout_result.get('error', 'Unknown error')}")
            
            # Wait a moment for processes to fully close
            time.sleep(2)
        
        # Step 3: Auto DB Cleaning
        if include_cleaning:
            if clean_all_ides:
                print("🔄 Step 2/4: Auto Cleaning - Cleaning all detected IDEs...")
                cleaning_results = {}
                
                for ide in detected_ides:
                    ide_name = ide.get("display_name", "Unknown IDE")
                    ide_type = ide.get("ide_type", "vscode")
                    print(f"  - Cleaning {ide_name}...")
                    
                    if ide_type == "jetbrains":
                        # JetBrains: only modify IDs
                        jetbrains_config_path = ide.get("jetbrains_config_path")
                        if not jetbrains_config_path:
                            jetbrains_config_path = get_jetbrains_config_dir()
                        
                        if not jetbrains_config_path:
                            results["errors"].append(f"{ide_name}: JetBrains config path not found")
                            cleaning_results[ide_name] = {"success": False, "error": "JetBrains config path not found"}
                            continue
                        
                        cleaning_result = modify_jetbrains_ids(jetbrains_config_path)
                        cleaning_results[ide_name] = {
                            "telemetry": cleaning_result,
                            "database": {"success": True, "message": "Not applicable for JetBrains"},
                            "workspace": {"success": True, "message": "Not applicable for JetBrains"},
                            "global_storage": {"success": True, "message": "Not applicable for JetBrains"}
                        }
                    else:
                        # VSCode-based: full cleaning
                        ide_cleaning_results = {}
                        
                        # Telemetry cleaning
                        try:
                            storage_path = ide.get("storage_path")
                            machine_id_path = ide.get("machine_id_path")
                            editor_type = ide.get("name", ide.get("editor_type", "VSCodium"))
                            
                            if not storage_path:
                                storage_path = get_storage_path(editor_type)
                            
                            if not os.path.exists(storage_path):
                                raise ValueError(f"Storage file not found at {storage_path}")
                            
                            if not machine_id_path:
                                machine_id_path = get_machine_id_path(editor_type)
                            
                            telemetry_result = modify_telemetry_ids(
                                editor_type=editor_type,
                                storage_path=storage_path,
                                machine_id_path=machine_id_path
                            )
                            ide_cleaning_results["telemetry"] = {
                                "success": True,
                                "data": telemetry_result,
                                "message": "Telemetry IDs modified successfully"
                            }
                        except Exception as e:
                            ide_cleaning_results["telemetry"] = {
                                "success": False,
                                "error": str(e),
                                "message": "Failed to modify telemetry IDs"
                            }
                        
                        # Database cleaning
                        try:
                            db_path = ide.get("db_path")
                            if not db_path:
                                db_path = get_db_path(editor_type)
                            
                            if not os.path.exists(db_path):
                                raise ValueError(f"Database file not found at {db_path}")
                            
                            db_result = clean_augment_data(
                                editor_type=editor_type,
                                db_path=db_path
                            )
                            ide_cleaning_results["database"] = {
                                "success": True,
                                "data": db_result,
                                "message": f"Database cleaned: {db_result.get('deleted_rows', 0)} rows deleted"
                            }
                        except Exception as e:
                            ide_cleaning_results["database"] = {
                                "success": False,
                                "error": str(e),
                                "message": "Failed to clean database"
                            }
                        
                        # Session data clearing (before workspace cleaning)
                        try:
                            print(f"    - Clearing session data for {ide_name}...")
                            session_result = clear_session_data(editor_type)
                            ide_cleaning_results["session"] = {
                                "success": session_result["success"],
                                "data": session_result,
                                "message": f"Session data cleared: {len(session_result.get('cleared_files', []))} items"
                            }
                        except Exception as e:
                            ide_cleaning_results["session"] = {
                                "success": False,
                                "error": str(e),
                                "message": "Failed to clear session data"
                            }

                        # Workspace cleaning
                        try:
                            workspace_storage_path = ide.get("workspace_storage_path")
                            if not workspace_storage_path:
                                workspace_storage_path = get_workspace_storage_path(editor_type)

                            if not os.path.exists(workspace_storage_path):
                                raise ValueError(f"Workspace storage directory not found at {workspace_storage_path}")

                            print(f"    - Cleaning workspace storage for {ide_name}...")
                            workspace_result = clean_workspace_storage(
                                editor_type=editor_type,
                                workspace_storage_path=workspace_storage_path
                            )

                            # Enhanced success checking
                            workspace_success = workspace_result.get('success', True)
                            if not workspace_success and len(workspace_result.get('failed_operations', [])) > 0:
                                workspace_success = False

                            ide_cleaning_results["workspace"] = {
                                "success": workspace_success,
                                "data": workspace_result,
                                "message": f"Workspace cleaned: {workspace_result.get('deleted_files_count', 0)} files deleted" if workspace_success else f"Workspace cleaning had issues: {len(workspace_result.get('failed_operations', []))} failed operations"
                            }
                        except Exception as e:
                            ide_cleaning_results["workspace"] = {
                                "success": False,
                                "error": str(e),
                                "message": "Failed to clean workspace"
                            }

                        # GlobalStorage cleaning
                        try:
                            global_storage_path = ide.get("global_storage_path")
                            if not global_storage_path:
                                global_storage_path = get_global_storage_path(editor_type)

                            if not os.path.exists(global_storage_path):
                                raise ValueError(f"Global storage directory not found at {global_storage_path}")

                            print(f"    - Cleaning global storage for {ide_name}...")
                            global_result = clean_global_storage(
                                editor_type=editor_type,
                                global_storage_path=global_storage_path
                            )

                            # Enhanced success checking
                            global_success = global_result.get('success', True)
                            if not global_success and len(global_result.get('failed_operations', [])) > 0:
                                global_success = False

                            ide_cleaning_results["global_storage"] = {
                                "success": global_success,
                                "data": global_result,
                                "message": f"Global storage cleaned: {global_result.get('deleted_files_count', 0)} files deleted" if global_success else f"Global storage cleaning had issues: {len(global_result.get('failed_operations', []))} failed operations"
                            }
                        except Exception as e:
                            ide_cleaning_results["global_storage"] = {
                                "success": False,
                                "error": str(e),
                                "message": "Failed to clean global storage"
                            }
                        
                        cleaning_results[ide_name] = ide_cleaning_results
                        
                        # Check if any cleaning operation failed for this IDE
                        for operation, result in ide_cleaning_results.items():
                            if not result["success"]:
                                results["errors"].append(f"{ide_name} {operation} failed: {result.get('error', 'Unknown error')}")
                
                results["steps"]["cleaning"] = cleaning_results
            else:
                # Original single IDE cleaning logic
                ide_name = ide_info.get("display_name", "Unknown IDE")
                ide_type = ide_info.get("ide_type", "vscode")
                editor_type = ide_info.get("name", ide_info.get("editor_type", ""))
                
                # Validate that we have proper IDE information
                if not ide_info or not isinstance(ide_info, dict):
                    results["success"] = False
                    results["errors"].append("Invalid IDE information provided")
                    return results
                
                # Ensure we have the required editor type
                if not editor_type:
                    results["success"] = False
                    results["errors"].append("Editor type not found in IDE information")
                    return results
                
                print(f"🔄 Step 2/4: Auto Cleaning - Cleaning {ide_name} data...")
                
                if ide_type == "jetbrains":
                    # JetBrains: only modify IDs
                    jetbrains_config_path = ide_info.get("jetbrains_config_path")
                    if not jetbrains_config_path:
                        results["errors"].append("JetBrains config path not found in IDE information")
                        cleaning_result = {"success": False, "error": "JetBrains config path not found"}
                    else:
                        cleaning_result = modify_jetbrains_ids(jetbrains_config_path)
                    
                    results["steps"]["cleaning"] = {
                        "telemetry": cleaning_result,
                        "database": {"success": True, "message": "Not applicable for JetBrains"},
                        "workspace": {"success": True, "message": "Not applicable for JetBrains"},
                        "global_storage": {"success": True, "message": "Not applicable for JetBrains"}
                    }
                else:
                    # VSCode-based: full cleaning using system-detected paths
                    cleaning_results = {}
                    
                    # Telemetry cleaning - use system-detected paths
                    try:
                        storage_path = ide_info.get("storage_path")
                        machine_id_path = ide_info.get("machine_id_path")
                        
                        if not storage_path:
                            raise ValueError("Storage path not found in IDE information")
                        
                        telemetry_result = modify_telemetry_ids(
                            editor_type=editor_type,
                            storage_path=storage_path,
                            machine_id_path=machine_id_path
                        )
                        cleaning_results["telemetry"] = {
                            "success": True,
                            "data": telemetry_result,
                            "message": "Telemetry IDs modified successfully"
                        }
                    except Exception as e:
                        cleaning_results["telemetry"] = {
                            "success": False,
                            "error": str(e),
                            "message": "Failed to modify telemetry IDs"
                        }
                    
                    # Database cleaning - use system-detected path
                    try:
                        db_path = ide_info.get("db_path")
                        if not db_path:
                            raise ValueError("Database path not found in IDE information")
                        
                        db_result = clean_augment_data(
                            editor_type=editor_type,
                            db_path=db_path
                        )
                        cleaning_results["database"] = {
                            "success": True,
                            "data": db_result,
                            "message": f"Database cleaned: {db_result.get('deleted_rows', 0)} rows deleted"
                        }
                    except Exception as e:
                        cleaning_results["database"] = {
                            "success": False,
                            "error": str(e),
                            "message": "Failed to clean database"
                        }
                    
                    # Workspace cleaning - use system-detected path
                    try:
                        workspace_storage_path = ide_info.get("workspace_storage_path")
                        if not workspace_storage_path:
                            raise ValueError("Workspace storage path not found in IDE information")

                        workspace_result = clean_workspace_storage(
                            editor_type=editor_type,
                            workspace_storage_path=workspace_storage_path
                        )
                        cleaning_results["workspace"] = {
                            "success": True,
                            "data": workspace_result,
                            "message": f"Workspace cleaned: {workspace_result.get('deleted_files_count', 0)} files deleted"
                        }
                    except Exception as e:
                        cleaning_results["workspace"] = {
                            "success": False,
                            "error": str(e),
                            "message": "Failed to clean workspace"
                        }

                    # GlobalStorage cleaning - use system-detected path
                    try:
                        global_storage_path = ide_info.get("global_storage_path")
                        if not global_storage_path:
                            raise ValueError("Global storage path not found in IDE information")

                        global_result = clean_global_storage(
                            editor_type=editor_type,
                            global_storage_path=global_storage_path
                        )
                        cleaning_results["global_storage"] = {
                            "success": True,
                            "data": global_result,
                            "message": f"Global storage cleaned: {global_result.get('deleted_files_count', 0)} files deleted"
                        }
                    except Exception as e:
                        cleaning_results["global_storage"] = {
                            "success": False,
                            "error": str(e),
                            "message": "Failed to clean global storage"
                        }
                    
                    results["steps"]["cleaning"] = cleaning_results
                    
                    # Check if any cleaning operation failed
                    for operation, result in cleaning_results.items():
                        if not result["success"]:
                            results["errors"].append(f"Cleaning {operation} failed: {result.get('error', 'Unknown error')}")
        
        # Step 4: Auto Signin (Preparation)
        if include_signin:
            if clean_all_ides:
                print("🔄 Step 3/4: Auto Signin - Preparing all IDEs for new login...")
                signin_results = {}
                for ide in detected_ides:
                    ide_name = ide.get("display_name", "Unknown IDE")
                    signin_results[ide_name] = {
                        "success": True,
                        "message": f"{ide_name} is ready for new Augment plugin login",
                        "instructions": [
                            "1. Start the IDE",
                            "2. Install/Enable Augment plugin if needed", 
                            "3. Login with new credentials",
                            "4. Enjoy your fresh Augment experience!"
                        ]
                    }
                results["steps"]["signin"] = signin_results
            else:
                print(f"🔄 Step 3/4: Auto Signin - Preparing for new login...")
                ide_name = ide_info.get("display_name", "Unknown IDE")
                results["steps"]["signin"] = {
                    "success": True,
                    "message": f"{ide_name} is ready for new Augment plugin login",
                    "instructions": [
                        "1. Start the IDE",
                        "2. Install/Enable Augment plugin if needed", 
                        "3. Login with new credentials",
                        "4. Enjoy your fresh Augment experience!"
                    ]
                }
        
        # Step 5: Auto Restart IDE
        if include_restart:
            if clean_all_ides:
                print("🔄 Step 4/4: Auto Restart - Starting all IDEs...")
                restart_results = {}
                for ide in detected_ides:
                    ide_name = ide.get("display_name", "Unknown IDE")
                    print(f"  - Starting {ide_name}...")
                    restart_result = start_ide(ide)
                    restart_results[ide_name] = restart_result
                    if not restart_result["success"]:
                        results["errors"].append(f"{ide_name} restart failed: {restart_result.get('error', 'Unknown error')}")
                results["steps"]["restart"] = restart_results
            else:
                print(f"🔄 Step 4/4: Auto Restart - Starting {ide_info.get('display_name', 'Unknown IDE')}...")
                restart_result = start_ide(ide_info)
                results["steps"]["restart"] = restart_result
                
                if not restart_result["success"]:
                    results["errors"].append(f"Restart failed: {restart_result.get('error', 'Unknown error')}")
        
        # Determine overall success and create detailed summary
        print("\n" + "="*60)
        print("🏁 AUTOMATION SUMMARY")
        print("="*60)

        if results["errors"]:
            results["success"] = False
            print(f"❌ Automation completed with {len(results['errors'])} error(s)")
            print("\n🔍 ERROR DETAILS:")
            for i, error in enumerate(results["errors"], 1):
                print(f"   {i}. {error}")

            if clean_all_ides:
                results["message"] = f"Automation completed with {len(results['errors'])} error(s) for all IDEs"
            else:
                results["message"] = f"Automation completed with {len(results['errors'])} error(s)"
        else:
            print("✅ All automation steps completed successfully!")
            if clean_all_ides:
                results["message"] = f"Full automation completed successfully for all {len(detected_ides)} detected IDE(s)"
            else:
                results["message"] = f"Full automation completed successfully for {ide_info.get('display_name', 'Unknown IDE')}"

        # Print step-by-step results
        print(f"\n📊 STEP RESULTS:")
        for step_name, step_result in results.get("steps", {}).items():
            if step_name == "signout":
                if isinstance(step_result, dict) and "closed_processes" in step_result:
                    print(f"   🔄 Signout: Closed {step_result.get('closed_processes', 0)} processes")
                else:
                    print(f"   🔄 Signout: Multiple IDEs processed")
            elif step_name == "cleaning":
                if isinstance(step_result, dict):
                    if clean_all_ides:
                        successful_cleans = sum(1 for ide_result in step_result.values()
                                              if isinstance(ide_result, dict) and
                                              all(op.get('success', False) for op in ide_result.values() if isinstance(op, dict)))
                        print(f"   🧹 Cleaning: {successful_cleans}/{len(step_result)} IDEs cleaned successfully")
                    else:
                        successful_ops = sum(1 for op in step_result.values() if isinstance(op, dict) and op.get('success', False))
                        print(f"   🧹 Cleaning: {successful_ops}/{len(step_result)} operations successful")
            elif step_name == "signin":
                print(f"   🔑 Signin: Ready for new login")
            elif step_name == "restart":
                if isinstance(step_result, dict) and "success" in step_result:
                    print(f"   🚀 Restart: {'Success' if step_result.get('success') else 'Failed'}")
                else:
                    print(f"   🚀 Restart: Multiple IDEs processed")

        print("="*60)

        # Generate comprehensive report
        report_automation_summary(results)

        return results
        
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Automation failed: {str(e)}")
        results["message"] = "Automation workflow encountered an error"
        return results
