"""
Profile Manager Widget Package
Phase 9 - Settings, Profiles & Network

Provides profile lifecycle management including create, clone, delete, and switch operations.
Profile bundles include INI + HAL + YAML + pinmap configuration files.
"""

from .profile_manager import ProfileManager

__all__ = ['ProfileManager']