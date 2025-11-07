# src/cde_orchestrator/adapters/service/__init__.py
"""
Service Adapters - External service integrations.

This module contains adapters for connecting to external services like
GitHub MCP, Git operations, and other external APIs.
"""

from .service_adapter import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    GitConnector,
    GitHubConnector,
    MCPDetector,
    ServiceConnectorFactory,
)

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "GitConnector",
    "GitHubConnector",
    "MCPDetector",
    "ServiceConnectorFactory",
]
