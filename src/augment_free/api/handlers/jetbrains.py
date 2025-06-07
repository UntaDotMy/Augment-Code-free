"""
JetBrains IDE handler for Free AugmentCode.

This module handles JetBrains IDE specific operations including:
- PermanentDeviceId file modification
- PermanentUserId file modification
- File locking to prevent regeneration
"""

import os
import sys
import stat
import uuid
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


def backup_file(file_path: Path) -> str:
    """
    Create a backup of the file.
    
    Args:
        file_path (Path): Path to the file to backup
        
    Returns:
        str: Path to the backup file
    """
    if not file_path.exists():
        return ""
    
    backup_path = file_path.with_suffix(file_path.suffix + '.backup')
    shutil.copy2(file_path, backup_path)
    return str(backup_path)


def lock_file(file_path: Path) -> bool:
    """
    Lock a file to prevent modification.
    
    Args:
        file_path (Path): Path to the file to lock
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not file_path.exists():
            return False
        
        # Set file as read-only using Python API
        current_permissions = file_path.stat().st_mode
        file_path.chmod(stat.S_IREAD)
        
        # Use platform-specific commands for additional protection
        if sys.platform == "win32":
            # Windows: Use attrib command
            try:
                subprocess.run(
                    ["attrib", "+R", str(file_path)], 
                    check=False, 
                    capture_output=True
                )
            except Exception:
                pass
        else:
            # Unix-like systems: Use chmod
            try:
                subprocess.run(
                    ["chmod", "444", str(file_path)], 
                    check=False, 
                    capture_output=True
                )
            except Exception:
                pass
            
            # macOS: Use chflags for additional protection
            if sys.platform == "darwin":
                try:
                    subprocess.run(
                        ["chflags", "uchg", str(file_path)], 
                        check=False, 
                        capture_output=True
                    )
                except Exception:
                    pass
        
        return True
    except Exception:
        return False


def update_jetbrains_id_file(file_path: Path) -> Dict[str, Any]:
    """
    Update a JetBrains ID file with a new UUID.
    
    Args:
        file_path (Path): Path to the ID file
        
    Returns:
        dict: Operation result with old and new UUIDs
    """
    try:
        # Read old UUID if file exists
        old_uuid = ""
        if file_path.exists():
            try:
                old_uuid = file_path.read_text(encoding='utf-8').strip()
            except Exception:
                old_uuid = "无法读取"
        
        # Generate new UUID
        new_uuid = generate_uuid()
        
        # Create backup
        backup_path = backup_file(file_path)
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write new UUID
        file_path.write_text(new_uuid, encoding='utf-8')
        
        # Lock the file
        lock_success = lock_file(file_path)
        
        return {
            "success": True,
            "old_uuid": old_uuid,
            "new_uuid": new_uuid,
            "backup_path": backup_path,
            "locked": lock_success,
            "file_path": str(file_path)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "file_path": str(file_path)
        }


def modify_jetbrains_ids(jetbrains_config_path: str) -> Dict[str, Any]:
    """
    Modify JetBrains IDE identification files.
    
    Args:
        jetbrains_config_path (str): Path to JetBrains configuration directory
        
    Returns:
        dict: Operation results for all ID files
    """
    try:
        config_path = Path(jetbrains_config_path)
        
        if not config_path.exists():
            return {
                "success": False,
                "error": f"JetBrains配置目录不存在: {jetbrains_config_path}",
                "message": "配置目录未找到"
            }
        
        # JetBrains ID files to process
        id_files = {
            "PermanentDeviceId": "PermanentDeviceId",
            "PermanentUserId": "PermanentUserId"
        }
        
        results = {}
        overall_success = True
        
        for file_key, file_name in id_files.items():
            file_path = config_path / file_name
            result = update_jetbrains_id_file(file_path)
            results[file_key] = result
            
            if not result["success"]:
                overall_success = False
        
        return {
            "success": overall_success,
            "data": results,
            "config_path": jetbrains_config_path,
            "message": "JetBrains ID文件处理完成" if overall_success else "部分文件处理失败"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"JetBrains ID处理失败: {str(e)}"
        }


def get_jetbrains_config_dir() -> str:
    """
    Get the JetBrains configuration directory path.
    
    Returns:
        str: Path to JetBrains config directory, empty if not found
    """
    try:
        # Standard directories where JetBrains config might be located
        if sys.platform == "win32":
            # Windows
            base_dirs = [
                Path(os.getenv("APPDATA", "")),
                Path(os.getenv("LOCALAPPDATA", "")),
                Path.home()
            ]
        elif sys.platform == "darwin":
            # macOS
            base_dirs = [
                Path.home() / "Library" / "Application Support",
                Path.home() / "Library" / "Preferences",
                Path.home() / ".config"
            ]
        else:
            # Linux and other Unix-like systems
            base_dirs = [
                Path.home() / ".config",
                Path.home() / ".local" / "share",
                Path.home()
            ]
        
        # Look for JetBrains directory
        for base_dir in base_dirs:
            if base_dir.exists():
                jetbrains_dir = base_dir / "JetBrains"
                if jetbrains_dir.exists() and jetbrains_dir.is_dir():
                    return str(jetbrains_dir)
        
        return ""
        
    except Exception:
        return ""


def get_jetbrains_info(jetbrains_config_path: str) -> Dict[str, Any]:
    """
    Get information about JetBrains configuration.
    
    Args:
        jetbrains_config_path (str): Path to JetBrains configuration directory
        
    Returns:
        dict: Information about JetBrains configuration
    """
    try:
        config_path = Path(jetbrains_config_path)
        
        if not config_path.exists():
            return {
                "exists": False,
                "path": jetbrains_config_path,
                "files": {}
            }
        
        # Check ID files
        id_files = {
            "PermanentDeviceId": "PermanentDeviceId",
            "PermanentUserId": "PermanentUserId"
        }
        
        files_info = {}
        for file_key, file_name in id_files.items():
            file_path = config_path / file_name
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8').strip()
                    files_info[file_key] = {
                        "exists": True,
                        "path": str(file_path),
                        "content": content[:16] + "..." if len(content) > 16 else content
                    }
                except Exception:
                    files_info[file_key] = {
                        "exists": True,
                        "path": str(file_path),
                        "content": "无法读取"
                    }
            else:
                files_info[file_key] = {
                    "exists": False,
                    "path": str(file_path),
                    "content": ""
                }
        
        return {
            "exists": True,
            "path": jetbrains_config_path,
            "files": files_info
        }
        
    except Exception as e:
        return {
            "exists": False,
            "path": jetbrains_config_path,
            "error": str(e),
            "files": {}
        }
