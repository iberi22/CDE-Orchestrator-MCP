# src/cde_orchestrator/adapters/state/__init__.py
"""
State Adapters - Project state persistence.

This module contains adapters for loading and saving project state
to external storage like JSON files.
"""

from .state_adapter import StateAdapter

__all__ = ["StateAdapter"]