# src/cde_orchestrator/application/ai_config/__init__.py
"""
AI Config Application - AI assistant configuration use cases.

This module contains use cases for configuring AI coding assistants
during project onboarding.
"""

from .ai_config_use_case import AIConfigUseCase, AgentConfig

__all__ = ["AIConfigUseCase", "AgentConfig"]