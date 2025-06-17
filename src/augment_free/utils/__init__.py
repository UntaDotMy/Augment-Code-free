"""
Utility modules for Free AugmentCode.

This module contains utility functions for:
- paths: Cross-platform path management
- device_codes: ID generation utilities
- translation: Internationalization support
"""

from .paths import (
    get_home_dir,
    get_app_data_dir,
    get_storage_path,
    get_db_path,
    get_machine_id_path,
    get_workspace_storage_path,
    get_global_storage_path,
)
from .device_codes import generate_machine_id, generate_device_id
from .translation import get_translation_manager, t

__all__ = [
    "get_home_dir",
    "get_app_data_dir",
    "get_storage_path",
    "get_db_path",
    "get_machine_id_path",
    "get_workspace_storage_path",
    "get_global_storage_path",
    "generate_machine_id",
    "generate_device_id",
    "get_translation_manager",
    "t",
]
