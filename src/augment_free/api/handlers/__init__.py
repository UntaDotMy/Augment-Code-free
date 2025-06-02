"""
API handlers for Free AugmentCode.

This module contains individual handlers for different operations:
- telemetry: Telemetry ID modification
- database: SQLite database cleaning
- workspace: Workspace storage cleaning
"""

from .telemetry import modify_telemetry_ids
from .database import clean_augment_data
from .workspace import clean_workspace_storage

__all__ = ["modify_telemetry_ids", "clean_augment_data", "clean_workspace_storage"]
