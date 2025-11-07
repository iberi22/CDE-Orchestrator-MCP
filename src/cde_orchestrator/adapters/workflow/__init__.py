# src/cde_orchestrator/adapters/workflow/__init__.py
"""
Workflow Adapters - Workflow file loading and parsing.

This module contains adapters for loading workflow definitions from
external sources like YAML files.
"""

from .workflow_adapter import WorkflowAdapter

__all__ = ["WorkflowAdapter"]
