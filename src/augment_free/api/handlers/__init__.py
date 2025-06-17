"""
API handlers for Free AugmentCode.

This module contains individual handlers for different operations:
- telemetry: Telemetry ID modification
- database: SQLite database cleaning
- workspace: Workspace storage cleaning
"""

from .telemetry import modify_telemetry_ids
from .database import clean_augment_data
from .workspace import clean_workspace_storage, clean_global_storage, clean_storage_comprehensive
from .jetbrains import modify_jetbrains_ids, get_jetbrains_config_dir, get_jetbrains_info
from .automation import run_full_automation, close_ide_processes, start_ide


__all__ = [
    "modify_telemetry_ids",
    "clean_augment_data",
    "clean_workspace_storage",
    "clean_global_storage",
    "clean_storage_comprehensive",
    "modify_jetbrains_ids",
    "get_jetbrains_config_dir",
    "get_jetbrains_info",
    "run_full_automation",
    "close_ide_processes",
    "start_ide",
]
