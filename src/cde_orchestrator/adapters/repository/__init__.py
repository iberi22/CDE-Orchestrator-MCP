# src/cde_orchestrator/adapters/repository/__init__.py
"""
Repository Adapters - Git repository analysis and ingestion.

This module contains adapters for analyzing Git repositories,
reading file contents, and generating repository digests.
"""

from .repository_adapter import GitAdapter

__all__ = ["GitAdapter"]
