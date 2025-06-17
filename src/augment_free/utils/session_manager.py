"""
Session management utilities for Free AugmentCode.

This module provides functions to manage IDE sessions, clear session data,
and handle session-related files that might prevent proper cleaning.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional


def find_session_files(editor_type: str) -> List[Dict[str, Any]]:
    """
    Find session-related files that might need special handling.
    
    Args:
        editor_type: The editor type (e.g., "Code", "VSCodium", "Code - Insiders")
        
    Returns:
        List of session file information
    """
    session_files = []
    
    try:
        if os.name == 'nt':  # Windows
            appdata = os.getenv("APPDATA", "")
            editor_path = os.path.join(appdata, editor_type)
            
            # Common session-related paths
            session_paths = [
                os.path.join(editor_path, "User", "globalStorage", "storage.json"),
                os.path.join(editor_path, "User", "globalStorage", "state.vscdb"),
                os.path.join(editor_path, "User", "workspaceStorage"),
                os.path.join(editor_path, "logs"),
                os.path.join(editor_path, "CachedExtensions"),
                os.path.join(editor_path, "CachedExtensionVSIXs"),
                os.path.join(editor_path, "User", "History"),
            ]
            
            for path in session_paths:
                if os.path.exists(path):
                    try:
                        stat_info = os.stat(path)
                        session_files.append({
                            'path': path,
                            'type': 'directory' if os.path.isdir(path) else 'file',
                            'size': stat_info.st_size if os.path.isfile(path) else None,
                            'modified': stat_info.st_mtime,
                            'accessible': os.access(path, os.R_OK | os.W_OK)
                        })
                    except Exception as e:
                        session_files.append({
                            'path': path,
                            'type': 'unknown',
                            'error': str(e),
                            'accessible': False
                        })
    
    except Exception as e:
        print(f"Error finding session files: {e}")
    
    return session_files


def clear_session_data(editor_type: str) -> Dict[str, Any]:
    """
    Clear session data that might interfere with workspace cleaning.
    
    Args:
        editor_type: The editor type
        
    Returns:
        Operation result
    """
    result = {
        'success': True,
        'cleared_files': [],
        'errors': [],
        'editor_type': editor_type
    }
    
    try:
        session_files = find_session_files(editor_type)
        
        for file_info in session_files:
            path = file_info['path']
            
            # Skip workspace storage - that's handled separately
            if 'workspaceStorage' in path:
                continue
                
            try:
                if file_info['type'] == 'file':
                    # For files, try to clear content or delete
                    if path.endswith('.json'):
                        # Clear JSON files by writing empty object
                        with open(path, 'w') as f:
                            json.dump({}, f)
                        result['cleared_files'].append(f"Cleared: {path}")
                    elif path.endswith('.vscdb'):
                        # For database files, just note them (handled by database cleaner)
                        result['cleared_files'].append(f"Database file noted: {path}")
                    else:
                        # For other files, try to delete
                        os.remove(path)
                        result['cleared_files'].append(f"Deleted: {path}")
                        
                elif file_info['type'] == 'directory':
                    # For directories like logs, clear contents but keep directory
                    if 'logs' in path.lower():
                        for item in os.listdir(path):
                            item_path = os.path.join(path, item)
                            try:
                                if os.path.isfile(item_path):
                                    os.remove(item_path)
                                elif os.path.isdir(item_path):
                                    import shutil
                                    shutil.rmtree(item_path)
                            except Exception as e:
                                result['errors'].append(f"Could not clear {item_path}: {e}")
                        result['cleared_files'].append(f"Cleared directory: {path}")
                        
            except Exception as e:
                result['errors'].append(f"Could not clear {path}: {e}")
    
    except Exception as e:
        result['success'] = False
        result['errors'].append(f"Session clearing failed: {e}")
    
    if result['errors']:
        result['success'] = len(result['errors']) < len(result['cleared_files'])
    
    return result


def get_session_status(editor_type: str) -> Dict[str, Any]:
    """
    Get the current session status for an editor.
    
    Args:
        editor_type: The editor type
        
    Returns:
        Session status information
    """
    try:
        session_files = find_session_files(editor_type)
        
        total_files = len(session_files)
        accessible_files = sum(1 for f in session_files if f.get('accessible', False))
        locked_files = total_files - accessible_files
        
        return {
            'success': True,
            'editor_type': editor_type,
            'total_session_files': total_files,
            'accessible_files': accessible_files,
            'locked_files': locked_files,
            'session_files': session_files,
            'has_active_session': locked_files > 0
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'editor_type': editor_type
        }
