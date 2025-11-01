# src/cde_orchestrator/application/__init__.py
"""
Application Layer - Simple Use Cases and Orchestration.

Philosophy:
    - LLM knows context (project names, locations)
    - CDE validates and executes workflows
    - Stateless: no registries, no complex state
    - Simple: each operation is independent

This layer coordinates domain entities and infrastructure adapters
to fulfill business workflows. It contains NO business logic itself.

Responsibilities:
    - Orchestrate multi-step operations
    - Call repositories and services via ports
    - Transform domain objects to/from DTOs
    - Handle application-level errors

Rules:
    - Depends only on domain layer
    - Knows about ports, not adapters
    - Returns structured data (dicts/dataclasses)
    - No I/O directly (delegates to adapters)
    - STATELESS: no caching, no registries
"""

from .project_locator import ProjectLocator, get_project_locator, configure_scan_roots

__all__ = [
    "ProjectLocator",
    "get_project_locator",
    "configure_scan_roots",
]
