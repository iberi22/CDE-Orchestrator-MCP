# src/cde_orchestrator/application/project_locator.py
"""
Project Locator - Simple Stateless Project Discovery.

Philosophy:
    - LLM knows project names/contexts
    - CDE just validates and executes
    - NO registries, NO caching, NO complexity
    - Stateless: every call is independent

Example:
    Agent: "Start feature in CDE Orchestrator: Add auth"
    CDE: Finds project, validates exists, executes workflow
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ProjectLocator:
    """
    Ultra-simple project locator.

    Responsibilities:
        1. Given a path, check if it's a valid project (has .git)
        2. Extract basic metadata if needed
        3. That's it!

    NO state, NO registration, NO complexity.
    """

    def __init__(self, scan_roots: Optional[list] = None):
        """
        Initialize locator.

        Args:
            scan_roots: Optional list of root paths to search in
                       (e.g., ["E:\\scripts-python", "C:\\work"])
        """
        self.scan_roots = scan_roots or []

    def validate_project_path(self, path: str) -> bool:
        """
        Check if path is a valid project.

        Args:
            path: Absolute path to check

        Returns:
            True if valid project (has .git), False otherwise

        Simple rules:
            - Path must exist
            - Must have .git directory
            - That's it!
        """
        project_path = Path(path)

        if not project_path.exists():
            logger.debug(f"Path does not exist: {path}")
            return False

        git_dir = project_path / ".git"
        if not git_dir.exists():
            logger.debug(f"Not a Git repository: {path}")
            return False

        return True

    def find_project_by_name(self, name: str) -> Optional[str]:
        """
        Search for project by name in scan_roots.

        Args:
            name: Project directory name (e.g., "CDE Orchestrator MCP")

        Returns:
            Absolute path if found, None otherwise

        Example:
            >>> locator = ProjectLocator(["E:\\\\scripts-python"])
            >>> path = locator.find_project_by_name("CDE Orchestrator MCP")
            >>> # Returns: "E:\\\\scripts-python\\\\CDE Orchestrator MCP"
        """
        if not self.scan_roots:
            logger.warning("No scan_roots configured")
            return None

        for root in self.scan_roots:
            root_path = Path(root)
            if not root_path.exists():
                continue

            # Check direct child
            candidate = root_path / name
            if self.validate_project_path(str(candidate)):
                return str(candidate.resolve())

            # Case-insensitive search
            for item in root_path.iterdir():
                if item.is_dir() and item.name.lower() == name.lower():
                    if self.validate_project_path(str(item)):
                        return str(item.resolve())

        return None

    def get_project_info(self, path: str) -> Dict[str, Any]:
        """
        Get basic project information.

        Args:
            path: Project path

        Returns:
            Dict with name, path, has_cde, has_specs

        Minimal metadata, no heavy analysis.
        """
        project_path = Path(path)

        info = {
            "name": project_path.name,
            "path": str(project_path.resolve()),
            "exists": project_path.exists(),
            "is_git": (project_path / ".git").exists(),
            "has_cde": (project_path / ".cde").exists(),
            "has_specs": (project_path / "specs").exists(),
        }

        return info

    def resolve_project_path(
        self,
        project_path: Optional[str] = None,
        project_name: Optional[str] = None,
        fallback_to_cwd: bool = True,
    ) -> Optional[str]:
        """
        Resolve project location from various inputs.

        Args:
            project_path: Explicit path (highest priority)
            project_name: Project name to search for
            fallback_to_cwd: Use current working dir if nothing else

        Returns:
            Resolved absolute path or None

        Priority:
            1. Explicit project_path (if valid)
            2. Search by project_name in scan_roots
            3. Current working directory (if fallback enabled)

        Examples:
            >>> # Explicit path
            >>> locator.resolve_project_path(
            ...     project_path="E:\\\\scripts-python\\\\my-app"
            ... )
            "E:\\\\scripts-python\\\\my-app"

            >>> # Search by name
            >>> locator.resolve_project_path(
            ...     project_name="CDE Orchestrator MCP"
            ... )
            "E:\\\\scripts-python\\\\CDE Orchestrator MCP"

            >>> # Fallback to CWD
            >>> locator.resolve_project_path()
            "/current/working/directory"
        """
        # Priority 1: Explicit path
        if project_path:
            if self.validate_project_path(project_path):
                return str(Path(project_path).resolve())
            else:
                logger.warning(f"Invalid project path: {project_path}")
                return None

        # Priority 2: Search by name
        if project_name:
            found = self.find_project_by_name(project_name)
            if found:
                return found
            else:
                logger.warning(f"Project not found: {project_name}")
                return None

        # Priority 3: Current working directory
        if fallback_to_cwd:
            cwd = str(Path.cwd())
            if self.validate_project_path(cwd):
                return cwd
            else:
                logger.warning(f"CWD is not a valid project: {cwd}")

        return None


# Singleton-like instance (but stateless)
_default_locator: Optional[ProjectLocator] = None


def get_project_locator() -> ProjectLocator:
    """Get or create default project locator."""
    global _default_locator
    if _default_locator is None:
        import os

        scan_roots_env = os.getenv("CDE_SCAN_ROOTS")
        scan_roots = scan_roots_env.split(";") if scan_roots_env else []
        _default_locator = ProjectLocator(scan_roots)
    return _default_locator


def configure_scan_roots(roots: list):
    """Configure scan roots globally."""
    global _default_locator
    _default_locator = ProjectLocator(roots)
