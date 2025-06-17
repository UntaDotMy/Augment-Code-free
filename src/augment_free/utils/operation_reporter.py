"""
Operation reporting utilities for Free AugmentCode.

This module provides detailed reporting functions for all operations
to give users comprehensive feedback on what was done.
"""

import time
from typing import Dict, Any, List


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def format_timestamp(timestamp: float) -> str:
    """Format timestamp to readable string."""
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))


def print_operation_header(operation_name: str, ide_name: str = None):
    """Print a formatted operation header."""
    header = f"🔧 {operation_name.upper()}"
    if ide_name:
        header += f" - {ide_name}"
    
    print("\n" + "="*60)
    print(header)
    print("="*60)


def print_operation_footer(success: bool, duration: float = None):
    """Print a formatted operation footer."""
    status = "✅ SUCCESS" if success else "❌ FAILED"
    footer = f"🏁 OPERATION {status}"
    if duration:
        footer += f" (took {duration:.2f}s)"
    
    print(footer)
    print("="*60)


def report_telemetry_operation(result: Dict[str, Any]) -> None:
    """Report detailed telemetry operation results."""
    print_operation_header("Telemetry ID Modification", result.get('editor_type'))
    
    # Show generated IDs
    if result.get('id_details'):
        id_details = result['id_details']
        
        print("🆔 MACHINE ID:")
        print(f"   Old: {id_details['machine_id']['old']}")
        print(f"   New: {id_details['machine_id']['new']}")
        print(f"   Format: {id_details['machine_id']['format']}")
        print(f"   Length: {id_details['machine_id']['length']} characters")
        
        print("\n🔢 DEVICE ID:")
        print(f"   Old: {id_details['device_id']['old']}")
        print(f"   New: {id_details['device_id']['new']}")
        print(f"   Format: {id_details['device_id']['format']}")
        print(f"   Length: {id_details['device_id']['length']} characters")
    
    # Show files modified
    if result.get('files_modified'):
        print(f"\n📝 FILES MODIFIED:")
        for i, file_path in enumerate(result['files_modified'], 1):
            print(f"   {i}. {file_path}")
    
    # Show backups created
    if result.get('backups_created'):
        print(f"\n💾 BACKUPS CREATED:")
        for i, backup_path in enumerate(result['backups_created'], 1):
            if backup_path:  # Skip None values
                print(f"   {i}. {backup_path}")
    
    # Show operation time
    if result.get('operation_time'):
        print(f"\n⏰ Operation completed at: {result['operation_time']}")


def report_database_operation(result: Dict[str, Any]) -> None:
    """Report detailed database operation results."""
    print_operation_header("Database Cleaning", result.get('editor_type'))
    
    # Show deletion summary
    deleted_rows = result.get('deleted_rows', 0)
    total_remaining = result.get('total_remaining_records', 0)
    
    print(f"🗑️  DELETION SUMMARY:")
    print(f"   Deleted records: {deleted_rows}")
    print(f"   Remaining records: {total_remaining}")
    
    # Show database info
    db_path = result.get('database_path')
    db_size = result.get('database_size_bytes', 0)
    if db_path:
        print(f"\n📊 DATABASE INFO:")
        print(f"   Path: {db_path}")
        print(f"   Size: {format_file_size(db_size)}")
    
    # Show deleted record keys (sample)
    deleted_keys = result.get('deleted_record_keys', [])
    if deleted_keys:
        print(f"\n🔑 DELETED RECORD KEYS:")
        for i, key in enumerate(deleted_keys[:10], 1):  # Show first 10
            print(f"   {i}. {key}")
        if len(deleted_keys) > 10:
            print(f"   ... and {len(deleted_keys) - 10} more")
    
    # Show backup info
    backup_path = result.get('backup_created')
    if backup_path:
        print(f"\n💾 BACKUP CREATED:")
        print(f"   {backup_path}")
    
    # Show operation time
    if result.get('operation_time'):
        print(f"\n⏰ Operation completed at: {result['operation_time']}")


def report_workspace_operation(result: Dict[str, Any]) -> None:
    """Report detailed workspace operation results."""
    print_operation_header("Workspace Cleaning", result.get('editor_type'))
    
    # Show deletion summary
    deleted_files = result.get('deleted_files_count', 0)
    deletion_method = result.get('deletion_method', 'unknown')
    workspace_exists = result.get('workspace_still_exists', True)
    
    print(f"🗑️  DELETION SUMMARY:")
    print(f"   Files processed: {deleted_files}")
    print(f"   Deletion method: {deletion_method}")
    print(f"   Workspace cleared: {'❌ No' if workspace_exists else '✅ Yes'}")
    
    # Show process management
    if result.get('process_kill_attempted'):
        print(f"   Process termination: ✅ Attempted")
    
    # Show failed operations
    failed_ops = result.get('failed_operations', [])
    if failed_ops:
        print(f"\n⚠️  FAILED OPERATIONS ({len(failed_ops)}):")
        for i, failure in enumerate(failed_ops[:5], 1):  # Show first 5
            print(f"   {i}. {failure.get('type', 'unknown')}: {failure.get('path', 'unknown')}")
            print(f"      Error: {failure.get('error', 'unknown')}")
        if len(failed_ops) > 5:
            print(f"   ... and {len(failed_ops) - 5} more failures")
    
    # Show backup info
    backup_path = result.get('backup_path')
    if backup_path:
        print(f"\n💾 BACKUP CREATED:")
        print(f"   {backup_path}")
    
    # Show compression failures
    failed_compressions = result.get('failed_compressions', [])
    if failed_compressions:
        print(f"\n⚠️  BACKUP COMPRESSION ISSUES ({len(failed_compressions)}):")
        for i, failure in enumerate(failed_compressions[:3], 1):
            print(f"   {i}. {failure.get('file', 'unknown')}")


def report_automation_summary(results: Dict[str, Any]) -> None:
    """Report comprehensive automation summary."""
    print("\n" + "="*80)
    print("🎯 COMPREHENSIVE AUTOMATION REPORT")
    print("="*80)
    
    # Overall status
    success = results.get('success', False)
    errors = results.get('errors', [])
    
    print(f"📊 OVERALL STATUS: {'✅ SUCCESS' if success else '❌ FAILED'}")
    if errors:
        print(f"🚨 Total Errors: {len(errors)}")
    
    # IDE information
    ide_info = results.get('ide_info')
    if ide_info:
        if isinstance(ide_info, list):
            print(f"🎯 Target: All detected IDEs ({len(ide_info)})")
        else:
            print(f"🎯 Target: {ide_info.get('display_name', 'Unknown IDE')}")
    
    # Step-by-step results
    steps = results.get('steps', {})
    print(f"\n📋 STEP RESULTS:")
    
    step_icons = {
        'signout': '🔄',
        'cleaning': '🧹', 
        'signin': '🔑',
        'restart': '🚀'
    }
    
    for step_name, step_result in steps.items():
        icon = step_icons.get(step_name, '📌')
        print(f"\n{icon} {step_name.upper()}:")
        
        if isinstance(step_result, dict):
            if 'success' in step_result:
                # Single IDE result
                status = '✅' if step_result.get('success') else '❌'
                print(f"   Status: {status}")
                if step_result.get('message'):
                    print(f"   Message: {step_result['message']}")
            else:
                # Multiple IDE results
                for ide_name, ide_result in step_result.items():
                    if isinstance(ide_result, dict):
                        if 'success' in ide_result:
                            status = '✅' if ide_result.get('success') else '❌'
                            print(f"   {ide_name}: {status}")
                        else:
                            # Nested operations (like cleaning)
                            print(f"   {ide_name}:")
                            for op_name, op_result in ide_result.items():
                                if isinstance(op_result, dict) and 'success' in op_result:
                                    op_status = '✅' if op_result.get('success') else '❌'
                                    print(f"     {op_name}: {op_status}")
    
    # Error details
    if errors:
        print(f"\n🚨 ERROR DETAILS:")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
    
    # Timestamp
    timestamp = results.get('timestamp')
    if timestamp:
        print(f"\n⏰ Completed at: {format_timestamp(timestamp)}")
    
    print("="*80)
