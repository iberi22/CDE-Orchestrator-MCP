# src/cde_orchestrator/adapters/prompt/__init__.py
"""
Prompt Adapters - POML template loading and context injection.

This module contains adapters for loading POML recipe files and
injecting sanitized context into prompt templates.
"""

from .prompt_adapter import PromptAdapter, PromptValidationError

__all__ = ["PromptAdapter", "PromptValidationError"]
