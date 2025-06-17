import os
import shutil
import time
import zipfile
import stat
import subprocess
import sys
from ...utils.paths import get_workspace_storage_path, get_global_storage_path
from pathlib import Path

def remove_readonly(func, path, excinfo):
    """Handle read-only files and directories during deletion"""
    try:
        # Clear read-only attribute
        if os.path.exists(path):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        return True
    except Exception as e:
        print(f"Warning: Could not remove readonly from {path}: {e}")
        return False

def kill_vscode_processes():
    """Kill all VS Code related processes to unlock files"""
    try:
        if sys.platform == "win32":
            # Kill common VS Code processes
            processes = ["code.exe", "Code.exe", "code-insiders.exe", "Code - Insiders.exe",
                        "vscodium.exe", "VSCodium.exe", "cursor.exe", "Cursor.exe"]

            for process in processes:
                try:
                    subprocess.run(["taskkill", "/F", "/IM", process],
                                 capture_output=True, check=False)
                except Exception:
                    pass

            # Wait for processes to fully terminate
            time.sleep(2)
            return True
    except Exception as e:
        print(f"Warning: Could not kill VS Code processes: {e}")
        return False

def force_delete_directory(path: Path) -> tuple[bool, list]:
    """
    Force delete a directory and all its contents.
    Returns (success, errors) tuple.
    """
    errors = []
    try:
        if not path.exists():
            return True, []

        # First try: Standard deletion
        try:
            shutil.rmtree(path, onerror=remove_readonly)
            return True, []
        except Exception as e:
            errors.append(f"Standard deletion failed: {e}")

        # Second try: Windows-specific with long path
        if os.name == 'nt':
            try:
                path_str = '\\\\?\\' + str(path.resolve())
                shutil.rmtree(path_str, onerror=remove_readonly)
                return True, []
            except Exception as e:
                errors.append(f"Long path deletion failed: {e}")

        # Third try: Use Windows rmdir command
        if os.name == 'nt':
            try:
                subprocess.run(['rmdir', '/S', '/Q', str(path)],
                             check=True, capture_output=True, shell=True)
                return True, []
            except Exception as e:
                errors.append(f"CMD rmdir failed: {e}")

        return False, errors
    except Exception as e:
        errors.append(f"Force delete failed: {e}")
        return False, errors

def clean_workspace_storage(editor_type: str = "VSCodium", workspace_storage_path: str = None) -> dict:
    """
    Cleans the workspace storage directory after creating a backup.

    Args:
        editor_type (str): Editor type, either "VSCodium" or "Code" (VS Code)
        workspace_storage_path (str, optional): Verified path to workspaceStorage directory

    This function:
    1. Kills any running IDE processes to unlock files
    2. Gets the workspace storage path
    3. Creates a zip backup of all files in the directory
    4. Deletes all files in the directory

    Returns:
        dict: A dictionary containing operation results
        {
            'backup_path': str,
            'deleted_files_count': int,
            'editor_type': str,
            'process_kill_attempted': bool,
            'deletion_errors': list
        }
    """
    result = {
        'editor_type': editor_type,
        'process_kill_attempted': False,
        'deletion_errors': [],
        'failed_operations': [],
        'failed_compressions': []
    }

    # Use provided path or fall back to system-detected path
    if workspace_storage_path is None:
        workspace_path = get_workspace_storage_path(editor_type)
    else:
        workspace_path = Path(workspace_storage_path)

    # Validate that workspace path exists
    if not os.path.exists(workspace_path):
        raise FileNotFoundError(f"Workspace storage directory not found at: {workspace_path}. Please ensure {editor_type} is properly installed and configured.")

    # Convert to Path object for better path handling
    workspace_path = Path(workspace_path)

    # Kill IDE processes to unlock files
    print(f"Attempting to close {editor_type} processes...")
    result['process_kill_attempted'] = kill_vscode_processes()

    # Create backup filename with timestamp
    timestamp = int(time.time())
    backup_path = f"{workspace_path}_backup_{timestamp}.zip"

    # Create zip backup with better error handling
    print(f"Creating backup at: {backup_path}")
    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in workspace_path.rglob('*'):
                if file_path.is_file():
                    try:
                        arcname = file_path.relative_to(workspace_path)
                        zipf.write(str(file_path), str(arcname))
                    except (OSError, PermissionError, zipfile.BadZipFile) as e:
                        result['failed_compressions'].append({
                            'file': str(file_path),
                            'error': str(e)
                        })
                        continue
    except Exception as e:
        print(f"Warning: Backup creation failed: {e}")
        result['backup_error'] = str(e)

    # Count files before deletion
    try:
        total_files = sum(1 for _ in workspace_path.rglob('*') if _.is_file())
        result['total_files_found'] = total_files
    except Exception as e:
        total_files = 0
        result['file_count_error'] = str(e)

    # Delete all files in the directory with enhanced error handling
    print(f"🗑️  Starting deletion of workspace storage: {workspace_path}")

    # Show what will be deleted
    try:
        workspace_items = list(workspace_path.rglob('*'))
        workspace_dirs = [p for p in workspace_items if p.is_dir()]
        workspace_files = [p for p in workspace_items if p.is_file()]

        print(f"📊 Workspace storage contents:")
        print(f"   • {len(workspace_dirs)} directories")
        print(f"   • {len(workspace_files)} files")

        # Show some examples
        if workspace_dirs:
            print(f"📁 Sample directories:")
            for i, dir_path in enumerate(workspace_dirs[:5]):
                rel_path = dir_path.relative_to(workspace_path)
                print(f"   {i+1}. {rel_path}")
            if len(workspace_dirs) > 5:
                print(f"   ... and {len(workspace_dirs) - 5} more directories")

        if workspace_files:
            print(f"📄 Sample files:")
            for i, file_path in enumerate(workspace_files[:5]):
                rel_path = file_path.relative_to(workspace_path)
                try:
                    size = file_path.stat().st_size
                    print(f"   {i+1}. {rel_path} ({size} bytes)")
                except:
                    print(f"   {i+1}. {rel_path}")
            if len(workspace_files) > 5:
                print(f"   ... and {len(workspace_files) - 5} more files")

    except Exception as e:
        print(f"⚠️  Could not enumerate workspace contents: {e}")

    def handle_error(e: Exception, path: Path, item_type: str):
        error_info = {
            'type': item_type,
            'path': str(path),
            'error': str(e),
            'error_type': type(e).__name__
        }
        result['failed_operations'].append(error_info)
        print(f"❌ Failed to delete {item_type}: {path.name} - {e}")

    # Strategy 1: Try to delete the entire directory tree at once
    success, errors = force_delete_directory(workspace_path)
    if success:
        print("✅ Successfully deleted workspace storage directory")
        result['deletion_method'] = 'bulk_delete'
    else:
        print("⚠️ Bulk deletion failed, trying file-by-file approach...")
        result['deletion_errors'].extend(errors)
        result['deletion_method'] = 'file_by_file'

        # Strategy 2: File-by-file deletion
        if workspace_path.exists():
            # Delete files first
            files_deleted = 0
            for file_path in workspace_path.rglob('*'):
                if file_path.is_file():
                    try:
                        # Clear read-only attribute if present
                        os.chmod(str(file_path), stat.S_IWRITE)
                        file_path.unlink(missing_ok=True)
                        files_deleted += 1
                    except (OSError, PermissionError) as e:
                        handle_error(e, file_path, 'file')

            # Delete directories from deepest to root
            dirs_to_delete = []
            try:
                dirs_to_delete = sorted(
                    [p for p in workspace_path.rglob('*') if p.is_dir()],
                    key=lambda x: len(str(x).split(os.sep)),
                    reverse=True
                )
            except Exception as e:
                result['deletion_errors'].append(f"Could not enumerate directories: {e}")

            dirs_deleted = 0
            for dir_path in dirs_to_delete:
                try:
                    dir_path.rmdir()
                    dirs_deleted += 1
                except (OSError, PermissionError) as e:
                    handle_error(e, dir_path, 'directory')

            # Try to delete the main directory
            try:
                if workspace_path.exists():
                    workspace_path.rmdir()
                    print("✅ Successfully deleted main workspace directory")
            except Exception as e:
                handle_error(e, workspace_path, 'main_directory')

            result['files_deleted_individually'] = files_deleted
            result['dirs_deleted_individually'] = dirs_deleted

    # Final verification
    workspace_still_exists = workspace_path.exists()
    result['workspace_still_exists'] = workspace_still_exists

    if not workspace_still_exists:
        print("✅ Workspace storage successfully cleaned")
        result['success'] = True
    else:
        print("⚠️ Workspace storage partially cleaned - some files may remain")
        result['success'] = len(result['failed_operations']) == 0

    # Prepare return data
    result.update({
        'backup_path': str(backup_path),
        'deleted_files_count': total_files,
    })

    return result


def clean_global_storage(editor_type: str = "VSCodium", global_storage_path: str = None) -> dict:
    """
    Cleans the globalStorage directory after creating a backup.

    Args:
        editor_type (str): Editor type, either "VSCodium" or "Code" (VS Code)
        global_storage_path (str, optional): Verified path to globalStorage directory

    This function:
    1. Gets the globalStorage path
    2. Creates a zip backup of all files in the directory
    3. Deletes all files in the directory

    Returns:
        dict: A dictionary containing operation results
        {
            'backup_path': str,
            'deleted_files_count': int,
            'editor_type': str,
            'deletion_errors': list
        }
    """
    result = {
        'editor_type': editor_type,
        'deletion_errors': [],
        'failed_operations': [],
        'failed_compressions': []
    }

    # Use provided path or fall back to system-detected path
    if global_storage_path is None:
        global_path = Path(get_global_storage_path(editor_type))
    else:
        global_path = Path(global_storage_path)

    if not global_path.exists():
        result.update({
            'success': False,
            'backup_path': '',
            'deleted_files_count': 0,
            'message': f'GlobalStorage directory not found: {global_path}'
        })
        return result

    print(f"🧹 Starting globalStorage cleaning for {editor_type}")
    print(f"📁 GlobalStorage path: {global_path}")

    # Create backup
    backup_dir = global_path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_filename = f"globalStorage_backup_{editor_type}_{timestamp}.zip"
    backup_path = backup_dir / backup_filename

    total_files = 0

    def handle_error(error, path, operation_type):
        error_msg = f"Failed to {operation_type} {path}: {error}"
        result['failed_operations'].append(error_msg)
        print(f"❌ {error_msg}")

    # Create backup zip
    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in global_path.rglob('*'):
                if file_path.is_file():
                    try:
                        # Calculate relative path for zip
                        relative_path = file_path.relative_to(global_path)
                        zipf.write(file_path, relative_path)
                        total_files += 1
                    except Exception as e:
                        result['failed_compressions'].append(f"Failed to compress {file_path}: {e}")
                        print(f"⚠️ Failed to compress {file_path}: {e}")

        print(f"💾 Created backup with {total_files} files: {backup_path}")
    except Exception as e:
        handle_error(e, backup_path, 'create backup')
        # Continue with deletion even if backup fails
        print("⚠️ Backup failed, but continuing with deletion...")

    # Strategy 1: Try to delete the entire directory tree at once
    success, errors = force_delete_directory(global_path)
    if success:
        print("✅ Successfully deleted globalStorage directory")
        result['deletion_method'] = 'bulk_delete'
    else:
        print("⚠️ Bulk deletion failed, trying file-by-file approach...")
        result['deletion_errors'].extend(errors)
        result['deletion_method'] = 'file_by_file'

        # Strategy 2: File-by-file deletion
        if global_path.exists():
            # Delete files first
            files_deleted = 0
            for file_path in global_path.rglob('*'):
                if file_path.is_file():
                    try:
                        # Clear read-only attribute if present
                        os.chmod(str(file_path), stat.S_IWRITE)
                        file_path.unlink(missing_ok=True)
                        files_deleted += 1
                    except (OSError, PermissionError) as e:
                        handle_error(e, file_path, 'file')

            # Delete directories from deepest to root
            dirs_to_delete = []
            try:
                dirs_to_delete = sorted(
                    [p for p in global_path.rglob('*') if p.is_dir()],
                    key=lambda x: len(str(x).split(os.sep)),
                    reverse=True
                )
            except Exception as e:
                result['deletion_errors'].append(f"Could not enumerate directories: {e}")

            dirs_deleted = 0
            for dir_path in dirs_to_delete:
                try:
                    dir_path.rmdir()
                    dirs_deleted += 1
                except (OSError, PermissionError) as e:
                    handle_error(e, dir_path, 'directory')

            # Try to delete the main directory
            try:
                if global_path.exists():
                    global_path.rmdir()
                    print("✅ Successfully deleted main globalStorage directory")
            except Exception as e:
                handle_error(e, global_path, 'main_directory')

            result['files_deleted_individually'] = files_deleted
            result['dirs_deleted_individually'] = dirs_deleted

    # Final verification
    global_still_exists = global_path.exists()
    result['global_still_exists'] = global_still_exists

    if not global_still_exists:
        print("✅ GlobalStorage successfully cleaned")
        result['success'] = True
    else:
        print("⚠️ GlobalStorage partially cleaned - some files may remain")
        result['success'] = len(result['failed_operations']) == 0

    # Prepare return data
    result.update({
        'backup_path': str(backup_path),
        'deleted_files_count': total_files,
    })

    return result


def clean_storage_comprehensive(editor_type: str = "VSCodium",
                               clean_global: bool = True,
                               clean_workspace: bool = True,
                               global_storage_path: str = None,
                               workspace_storage_path: str = None) -> dict:
    """
    Comprehensive storage cleaning function that can clean globalStorage, workspaceStorage, or both.

    Args:
        editor_type (str): Editor type, either "VSCodium" or "Code" (VS Code)
        clean_global (bool): Whether to clean globalStorage directory
        clean_workspace (bool): Whether to clean workspaceStorage directory
        global_storage_path (str, optional): Verified path to globalStorage directory
        workspace_storage_path (str, optional): Verified path to workspaceStorage directory

    Returns:
        dict: A dictionary containing comprehensive operation results
    """
    result = {
        'editor_type': editor_type,
        'operations_performed': [],
        'global_storage_result': None,
        'workspace_storage_result': None,
        'overall_success': True,
        'total_files_deleted': 0,
        'backup_paths': []
    }

    print(f"🧹 Starting comprehensive storage cleaning for {editor_type}")
    print(f"   - Clean globalStorage: {clean_global}")
    print(f"   - Clean workspaceStorage: {clean_workspace}")

    # Clean globalStorage if requested
    if clean_global:
        print("🗂️ Cleaning globalStorage...")
        global_result = clean_global_storage(editor_type, global_storage_path)
        result['global_storage_result'] = global_result
        result['operations_performed'].append('globalStorage')

        if global_result.get('success', False):
            result['total_files_deleted'] += global_result.get('deleted_files_count', 0)
            if global_result.get('backup_path'):
                result['backup_paths'].append(global_result['backup_path'])
        else:
            result['overall_success'] = False

    # Clean workspaceStorage if requested
    if clean_workspace:
        print("💾 Cleaning workspaceStorage...")
        workspace_result = clean_workspace_storage(editor_type, workspace_storage_path)
        result['workspace_storage_result'] = workspace_result
        result['operations_performed'].append('workspaceStorage')

        if workspace_result.get('success', False):
            result['total_files_deleted'] += workspace_result.get('deleted_files_count', 0)
            if workspace_result.get('backup_path'):
                result['backup_paths'].append(workspace_result['backup_path'])
        else:
            result['overall_success'] = False

    # Summary
    operations_text = " and ".join(result['operations_performed'])
    if result['overall_success']:
        print(f"✅ Successfully cleaned {operations_text}")
        result['message'] = f"Successfully cleaned {operations_text}. Total files deleted: {result['total_files_deleted']}"
    else:
        print(f"⚠️ Partially cleaned {operations_text}")
        result['message'] = f"Partially cleaned {operations_text}. Some operations may have failed."

    return result