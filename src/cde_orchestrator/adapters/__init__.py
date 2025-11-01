# src/cde_orchestrator/adapters/__init__.py
"""
Adapters (Secondary Ports) - Infrastructure Implementations.

Adapters implement domain ports to interact with external systems:
    - FileSystemProjectRepository: Project persistence (JSON)
    - YAMLWorkflowEngine: Workflow definition loading
    - POMLPromptRenderer: POML template rendering
    - CopilotCLIAdapter: GitHub Copilot CLI execution
    - GitHubMCPAdapter: GitHub operations via MCP

Design Principles:
    - No business logic (that's in domain)
    - Implement port interfaces exactly
    - Handle infrastructure errors gracefully
    - Log operations for debugging

For LLMs:
    - Each adapter in separate file
    - Clear error messages
    - Explicit contracts
    - Example usage in docstrings
"""

from .filesystem_project_repository import FileSystemProjectRepository

__all__ = [
    "FileSystemProjectRepository",
]
