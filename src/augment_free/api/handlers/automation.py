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
from ..handlers.workspace import clean_workspace_storage
from ..handlers.jetbrains import modify_jetbrains_ids
from ...utils.ide_detector import detect_ides, IDEDetector
from ...utils.translation import t


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
                       include_restart: bool = True) -> Dict[str, Any]:
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
        # Step 1: Auto-detect IDE if not provided
        if ide_info is None:
            detection_result = detect_ides()
            if detection_result["success"] and detection_result.get("ides"):
                ide_info = detection_result["ides"][0]  # Use first detected IDE
                results["ide_info"] = ide_info
            else:
                results["success"] = False
                results["errors"].append("No IDE detected for automation")
                return results
        
        ide_name = ide_info.get("display_name", "Unknown IDE")
        ide_type = ide_info.get("ide_type", "vscode")
        
        # Step 2: Auto Signout (Close IDE)
        if include_signout:
            print(f"🔄 Step 1/4: Auto Signout - Closing {ide_name}...")
            signout_result = close_ide_processes(ide_info)
            results["steps"]["signout"] = signout_result
            
            if not signout_result["success"]:
                results["errors"].append(f"Signout failed: {signout_result.get('error', 'Unknown error')}")
            
            # Wait a moment for processes to fully close
            time.sleep(2)
        
        # Step 3: Auto DB Cleaning
        if include_cleaning:
            print(f"🔄 Step 2/4: Auto Cleaning - Cleaning {ide_name} data...")
            
            if ide_type == "jetbrains":
                # JetBrains: only modify IDs
                cleaning_result = modify_jetbrains_ids(ide_info.get("jetbrains_config_path"))
                results["steps"]["cleaning"] = {
                    "telemetry": cleaning_result,
                    "database": {"success": True, "message": "Not applicable for JetBrains"},
                    "workspace": {"success": True, "message": "Not applicable for JetBrains"}
                }
            else:
                # VSCode-based: full cleaning
                cleaning_results = {}
                
                # Telemetry cleaning
                try:
                    telemetry_result = modify_telemetry_ids(
                        editor_type=ide_info.get("editor_type", "Code"),
                        storage_path=ide_info.get("storage_path"),
                        machine_id_path=ide_info.get("machine_id_path")
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
                
                # Database cleaning
                try:
                    db_result = clean_augment_data(
                        editor_type=ide_info.get("editor_type", "Code"),
                        db_path=ide_info.get("db_path")
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
                
                # Workspace cleaning
                try:
                    workspace_result = clean_workspace_storage(
                        editor_type=ide_info.get("editor_type", "Code"),
                        workspace_storage_path=ide_info.get("workspace_storage_path")
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
                
                results["steps"]["cleaning"] = cleaning_results
                
                # Check if any cleaning operation failed
                for operation, result in cleaning_results.items():
                    if not result["success"]:
                        results["errors"].append(f"Cleaning {operation} failed: {result.get('error', 'Unknown error')}")
        
        # Step 4: Auto Signin (Preparation)
        if include_signin:
            print(f"🔄 Step 3/4: Auto Signin - Preparing for new login...")
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
            print(f"🔄 Step 4/4: Auto Restart - Starting {ide_name}...")
            restart_result = start_ide(ide_info)
            results["steps"]["restart"] = restart_result
            
            if not restart_result["success"]:
                results["errors"].append(f"Restart failed: {restart_result.get('error', 'Unknown error')}")
        
        # Determine overall success
        if results["errors"]:
            results["success"] = False
            results["message"] = f"Automation completed with {len(results['errors'])} error(s)"
        else:
            results["message"] = f"Full automation completed successfully for {ide_name}"
        
        return results
        
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Automation failed: {str(e)}")
        results["message"] = "Automation workflow encountered an error"
        return results
