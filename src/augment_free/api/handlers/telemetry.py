import json
import os
import time
import shutil
from ...utils.paths import get_storage_path, get_machine_id_path
from ...utils.device_codes import generate_machine_id, generate_device_id

def _create_backup(file_path: str) -> str:
    """
    Creates a backup of the specified file with timestamp.

    Args:
        file_path (str): Path to the file to backup

    Returns:
        str: Path to the backup file

    Format: <filename>.bak.<timestamp>
    """
    timestamp = int(time.time())
    backup_path = f"{file_path}.bak.{timestamp}"
    shutil.copy2(file_path, backup_path)
    return backup_path

def generate_detailed_ids() -> dict:
    """
    Generate new IDs with detailed information for user visibility.

    Returns:
        dict: Generated IDs with metadata
    """
    import uuid
    import secrets
    import time

    # Generate various ID formats
    new_machine_id = str(uuid.uuid4())
    new_device_id = secrets.token_hex(16)  # 32 character hex
    new_session_id = str(uuid.uuid4())
    timestamp = int(time.time())

    return {
        'machine_id': {
            'value': new_machine_id,
            'format': 'UUID v4',
            'length': len(new_machine_id),
            'description': 'Machine identifier for telemetry'
        },
        'device_id': {
            'value': new_device_id,
            'format': 'Hex token',
            'length': len(new_device_id),
            'description': 'Device identifier for tracking'
        },
        'session_id': {
            'value': new_session_id,
            'format': 'UUID v4',
            'length': len(new_session_id),
            'description': 'Session identifier'
        },
        'generation_timestamp': timestamp,
        'generation_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
    }


def modify_telemetry_ids(editor_type: str = "VSCodium", storage_path: str = None, machine_id_path: str = None) -> dict:
    """
    Modifies the telemetry IDs in the VS Code/VSCodium storage.json file and machine ID file.
    Creates backups before modification.

    Args:
        editor_type (str): Editor type, either "VSCodium" or "Code" (VS Code)
        storage_path (str, optional): Verified path to storage.json file
        machine_id_path (str, optional): Verified path to machineid file

    This function:
    1. Creates backups of the storage.json and machine ID files
    2. Reads the storage.json file
    3. Generates new machine and device IDs
    4. Updates the telemetry.machineId and telemetry.devDeviceId values in storage.json
    5. Updates the machine ID file with the new machine ID
    6. Saves the modified files

    Returns:
        dict: A dictionary containing the old and new IDs and backup information
        {
            'old_machine_id': str,
            'new_machine_id': str,
            'old_device_id': str,
            'new_device_id': str,
            'storage_backup_path': str,
            'machine_id_backup_path': str,
            'editor_type': str
        }
    """
    # Use provided paths or fall back to system-detected paths
    if storage_path is None:
        storage_path = get_storage_path(editor_type)
    if machine_id_path is None:
        machine_id_path = get_machine_id_path(editor_type)

    # Validate that storage path exists
    if not os.path.exists(storage_path):
        raise FileNotFoundError(f"Storage file not found at: {storage_path}. Please ensure {editor_type} is properly installed and configured.")

    # Create backups before modification
    storage_backup_path = _create_backup(storage_path)
    machine_id_backup_path = None
    if os.path.exists(machine_id_path):
        machine_id_backup_path = _create_backup(machine_id_path)

    # Read the current JSON content
    with open(storage_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Store old values
    old_machine_id = data.get('telemetry.machineId', '')
    old_device_id = data.get('telemetry.devDeviceId', '')

    # Generate new IDs with detailed information
    print(f"🔄 Generating new telemetry IDs for {editor_type}...")
    new_machine_id = generate_machine_id()
    new_device_id = generate_device_id()

    # Display generated IDs to user
    print(f"✅ Generated new Machine ID: {new_machine_id}")
    print(f"   • Format: UUID v4")
    print(f"   • Length: {len(new_machine_id)} characters")
    print(f"   • Previous: {old_machine_id[:8]}...{old_machine_id[-8:] if len(old_machine_id) > 16 else old_machine_id}")

    print(f"✅ Generated new Device ID: {new_device_id}")
    print(f"   • Format: Hex token")
    print(f"   • Length: {len(new_device_id)} characters")
    print(f"   • Previous: {old_device_id[:8]}...{old_device_id[-8:] if len(old_device_id) > 16 else old_device_id}")

    # Update the values in storage.json
    print(f"🔄 Updating storage.json...")
    data['telemetry.machineId'] = new_machine_id
    data['telemetry.devDeviceId'] = new_device_id

    # Write the modified content back to storage.json
    with open(storage_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"✅ Updated storage.json at: {storage_path}")

    # Write the new machine ID to the machine ID file
    print(f"🔄 Updating machine ID file...")
    with open(machine_id_path, 'w', encoding='utf-8') as f:
        f.write(new_device_id)
    print(f"✅ Updated machine ID file at: {machine_id_path}")

    # Generate timestamp for operation
    operation_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    return {
        'old_machine_id': old_machine_id,
        'new_machine_id': new_machine_id,
        'old_device_id': old_device_id,
        'new_device_id': new_device_id,
        'storage_backup_path': storage_backup_path,
        'machine_id_backup_path': machine_id_backup_path,
        'editor_type': editor_type,
        'operation_timestamp': int(time.time()),
        'operation_time': operation_time,
        'files_modified': [storage_path, machine_id_path],
        'backups_created': [storage_backup_path, machine_id_backup_path] if machine_id_backup_path else [storage_backup_path],
        'id_details': {
            'machine_id': {
                'old': old_machine_id,
                'new': new_machine_id,
                'format': 'UUID v4',
                'length': len(new_machine_id)
            },
            'device_id': {
                'old': old_device_id,
                'new': new_device_id,
                'format': 'Hex token',
                'length': len(new_device_id)
            }
        }
    }