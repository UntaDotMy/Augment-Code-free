import sqlite3
import shutil
import time
import os
from ...utils.paths import get_db_path

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

def clean_augment_data(editor_type: str = "VSCodium", db_path: str = None) -> dict:
    """
    Cleans augment-related data from the SQLite database.
    Creates a backup before modification.

    Args:
        editor_type (str): Editor type, either "VSCodium" or "Code" (VS Code)
        db_path (str, optional): Verified path to state.vscdb file

    This function:
    1. Gets the SQLite database path
    2. Creates a backup of the database file
    3. Opens the database connection
    4. Deletes records where key contains 'augment'

    Returns:
        dict: A dictionary containing operation results
        {
            'db_backup_path': str,
            'deleted_rows': int,
            'editor_type': str
        }
    """
    # Use provided path or fall back to system-detected path
    if db_path is None:
        db_path = get_db_path(editor_type)

    # Validate that database path exists
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at: {db_path}. Please ensure {editor_type} is properly installed and configured.")

    # Create backup before modification
    db_backup_path = _create_backup(db_path)

    # Connect to the database
    print(f"🔄 Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # First, check what records exist
        print(f"🔍 Scanning for Augment-related records...")
        cursor.execute("SELECT key FROM ItemTable WHERE key LIKE '%augment%'")
        records_to_delete = cursor.fetchall()

        if records_to_delete:
            print(f"📋 Found {len(records_to_delete)} Augment-related records:")
            for i, (key,) in enumerate(records_to_delete[:10]):  # Show first 10
                print(f"   {i+1}. {key}")
            if len(records_to_delete) > 10:
                print(f"   ... and {len(records_to_delete) - 10} more records")
        else:
            print("✅ No Augment-related records found in database")

        # Execute the delete query
        print(f"🗑️  Deleting Augment-related records...")
        cursor.execute("DELETE FROM ItemTable WHERE key LIKE '%augment%'")
        deleted_rows = cursor.rowcount

        # Commit the changes
        conn.commit()

        if deleted_rows > 0:
            print(f"✅ Successfully deleted {deleted_rows} records from database")
        else:
            print("ℹ️  No records were deleted (none found)")

        # Get database statistics
        cursor.execute("SELECT COUNT(*) FROM ItemTable")
        total_remaining = cursor.fetchone()[0]

        operation_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        return {
            'db_backup_path': db_backup_path,
            'deleted_rows': deleted_rows,
            'editor_type': editor_type,
            'operation_timestamp': int(time.time()),
            'operation_time': operation_time,
            'database_path': db_path,
            'total_remaining_records': total_remaining,
            'deleted_record_keys': [key for (key,) in records_to_delete],
            'backup_created': db_backup_path,
            'database_size_bytes': os.path.getsize(db_path) if os.path.exists(db_path) else 0
        }
    finally:
        # Always close the connection
        cursor.close()
        conn.close()