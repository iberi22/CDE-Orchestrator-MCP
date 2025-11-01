# src/cde_orchestrator/adapters/recipe/__init__.py
"""
Recipe Adapters - POML recipe loading and management.

This module contains adapters for loading POML recipe files and
providing recipe suggestions based on context.
"""

from .recipe_adapter import RecipeAdapter

__all__ = ["RecipeAdapter"]