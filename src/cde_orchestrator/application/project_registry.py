# src/cde_orchestrator/application/project_registry.py
"""
Project Registry - Multi-Project Management System.

Handles discovery, registration, and management of 1000+ projects
from a single VS Code window.

Features:
    - Auto-discovery via filesystem scanning
    - Git repository detection
    - Tech stack analysis
    - Lazy loading for performance
    - Context isolation per project
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import subprocess
import json

from ..domain.entities import Project, ProjectId, ProjectStatus
from ..domain.ports import IProjectRepository
from ..domain.exceptions import RepositoryError

logger = logging.getLogger(__name__)


class ProjectRegistry:
    """
    Manages multiple projects simultaneously with auto-discovery.

    Example Usage:
        >>> registry = ProjectRegistry(repo)
        >>> projects = registry.scan_directory("E:\\\\scripts-python")
        >>> print(f"Discovered {len(projects)} projects")
        >>>
        >>> # Get project by path
        >>> project = registry.get_project_by_path("E:\\\\scripts-python\\\\CDE")
        >>> feature = project.start_feature("Add login")
    """

    def __init__(self, repository: IProjectRepository):
        """
        Initialize registry.

        Args:
            repository: Project persistence adapter
        """
        self.repo = repository
        self._loaded_projects: Dict[str, Project] = {}
        self._scan_cache: Dict[str, Any] = {}

    def scan_directory(
        self,
        root_path: str,
        max_depth: int = 10,
        skip_patterns: Optional[List[str]] = None
    ) -> List[Project]:
        """
        Scan directory tree for Git repositories and register as projects.

        This is the core multi-project discovery feature. It recursively
        scans the filesystem looking for .git directories and registers
        each as an independent project.

        Args:
            root_path: Absolute path to scan (e.g., "E:\\\\scripts-python")
            max_depth: Maximum directory depth to scan (default: 10)
            skip_patterns: Directory names to skip (default: common patterns)

        Returns:
            List of discovered/registered Project instances

        Algorithm:
            1. Validate root path exists
            2. Find all .git directories recursively
            3. For each .git dir:
                a. Check if already registered (skip if so)
                b. Extract project metadata (name, remote, tech stack)
                c. Create Project entity
                d. Save to repository
            4. Update scan cache

        Performance:
            - Handles 1000+ projects efficiently
            - Uses lazy loading (projects not loaded into memory)
            - Caches scan results to avoid re-scanning

        Examples:
            >>> registry.scan_directory("E:\\\\scripts-python")
            [Project(...), Project(...), ...]  # 47 projects found

            >>> # Scan multiple roots
            >>> for root in ["E:\\\\scripts-python", "C:\\\\work"]:
            ...     registry.scan_directory(root)
        """
        root = Path(root_path)
        if not root.exists():
            raise ValueError(f"Path does not exist: {root_path}")

        logger.info(f"Scanning for projects in: {root_path}")

        # Default skip patterns
        if skip_patterns is None:
            skip_patterns = [
                "node_modules",
                ".venv",
                "venv",
                "__pycache__",
                ".pytest_cache",
                ".mypy_cache",
                "dist",
                "build",
                ".tox",
                ".eggs"
            ]

        discovered = []
        skip_set = set(skip_patterns)

        # Find all .git directories
        git_dirs = self._find_git_directories(root, max_depth, skip_set)

        logger.info(f"Found {len(git_dirs)} Git repositories")

        for git_dir in git_dirs:
            project_path = str(git_dir.parent.resolve())

            # Check if already registered
            existing = self.repo.get_by_path(project_path)
            if existing:
                logger.debug(f"Project already registered: {project_path}")
                discovered.append(existing)
                continue

            # Create and register new project
            try:
                project = self._create_project_from_git_repo(git_dir)
                self.repo.save(project)
                discovered.append(project)
                logger.info(f"Registered new project: {project.name} ({project.id.value})")
            except Exception as e:
                logger.error(f"Failed to register project at {project_path}: {e}")
                continue

        # Update scan cache
        self._update_scan_cache(root_path, discovered)

        return discovered

    def _find_git_directories(
        self,
        root: Path,
        max_depth: int,
        skip_patterns: Set[str]
    ) -> List[Path]:
        """
        Recursively find all .git directories.

        Args:
            root: Root directory to start search
            max_depth: Maximum depth to recurse
            skip_patterns: Directory names to skip

        Returns:
            List of .git directory paths
        """
        git_dirs = []

        def _scan(path: Path, depth: int):
            if depth > max_depth:
                return

            try:
                for item in path.iterdir():
                    # Skip hidden directories (except .git)
                    if item.name.startswith('.') and item.name != '.git':
                        continue

                    # Skip patterns
                    if item.name in skip_patterns:
                        continue

                    if item.is_dir():
                        if item.name == '.git':
                            git_dirs.append(item)
                            # Don't recurse into .git contents
                        else:
                            _scan(item, depth + 1)
            except PermissionError:
                logger.warning(f"Permission denied: {path}")
            except Exception as e:
                logger.error(f"Error scanning {path}: {e}")

        _scan(root, 0)
        return git_dirs

    def _create_project_from_git_repo(self, git_dir: Path) -> Project:
        """
        Create Project entity from Git repository.

        Args:
            git_dir: Path to .git directory

        Returns:
            Project instance with metadata
        """
        project_path = git_dir.parent
        project_name = project_path.name

        # Extract Git metadata
        git_metadata = self._extract_git_metadata(git_dir)

        # Detect tech stack
        tech_stack = self._detect_tech_stack(project_path)

        # Create project
        project = Project.create(
            name=project_name,
            path=str(project_path)
        )

        # Populate metadata
        project.metadata.update({
            "auto_discovered": True,
            "git_remote": git_metadata.get("remote_url"),
            "git_branch": git_metadata.get("current_branch"),
            "tech_stack": tech_stack,
            "discovery_timestamp": str(project.created_at)
        })

        return project

    def _extract_git_metadata(self, git_dir: Path) -> Dict[str, Any]:
        """
        Extract Git repository metadata.

        Args:
            git_dir: Path to .git directory

        Returns:
            Dict with remote_url, current_branch, etc.
        """
        metadata = {
            "remote_url": None,
            "current_branch": None
        }

        project_path = git_dir.parent

        try:
            # Get remote URL
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                metadata["remote_url"] = result.stdout.strip()
        except Exception as e:
            logger.debug(f"Could not get Git remote: {e}")

        try:
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                metadata["current_branch"] = result.stdout.strip()
        except Exception as e:
            logger.debug(f"Could not get Git branch: {e}")

        return metadata

    def _detect_tech_stack(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze project files to detect technology stack.

        Args:
            project_path: Project root directory

        Returns:
            Dict with detected technologies
        """
        stack = {
            "languages": [],
            "frameworks": [],
            "tools": []
        }

        # Python detection
        if (project_path / "pyproject.toml").exists():
            stack["languages"].append("Python")
            stack["tools"].append("Poetry/PDM")
        elif (project_path / "requirements.txt").exists():
            stack["languages"].append("Python")
            stack["tools"].append("pip")
        elif (project_path / "setup.py").exists():
            stack["languages"].append("Python")
            stack["tools"].append("setuptools")

        # JavaScript/TypeScript detection
        if (project_path / "package.json").exists():
            stack["languages"].append("JavaScript/TypeScript")
            stack["tools"].append("npm/yarn")

            # Check for frameworks
            try:
                with open(project_path / "package.json") as f:
                    package_data = json.load(f)
                    deps = {
                        **package_data.get("dependencies", {}),
                        **package_data.get("devDependencies", {})
                    }

                    if "react" in deps:
                        stack["frameworks"].append("React")
                    if "vue" in deps:
                        stack["frameworks"].append("Vue")
                    if "next" in deps:
                        stack["frameworks"].append("Next.js")
                    if "express" in deps:
                        stack["frameworks"].append("Express")
            except Exception:
                pass

        # Rust detection
        if (project_path / "Cargo.toml").exists():
            stack["languages"].append("Rust")
            stack["tools"].append("Cargo")

        # Go detection
        if (project_path / "go.mod").exists():
            stack["languages"].append("Go")
            stack["tools"].append("Go Modules")

        # Docker
        if (project_path / "Dockerfile").exists():
            stack["tools"].append("Docker")

        # CDE Orchestrator specific
        if (project_path / ".cde" / "workflow.yml").exists():
            stack["tools"].append("CDE Orchestrator")

        return stack

    def _update_scan_cache(self, root_path: str, projects: List[Project]):
        """Update scan cache with results."""
        self._scan_cache[root_path] = {
            "count": len(projects),
            "project_ids": [p.id.value for p in projects],
            "last_scan": str(projects[0].created_at) if projects else None
        }

    def get_project(self, project_id: str) -> Optional[Project]:
        """
        Get project by ID with lazy loading.

        Args:
            project_id: Project identifier

        Returns:
            Project if found, None otherwise
        """
        # Check cache first
        if project_id in self._loaded_projects:
            return self._loaded_projects[project_id]

        # Load from repository
        project = self.repo.get_by_id(ProjectId(project_id))
        if project:
            self._loaded_projects[project_id] = project
        return project

    def get_project_by_path(self, path: str) -> Optional[Project]:
        """
        Find project by filesystem path.

        Args:
            path: Absolute filesystem path

        Returns:
            Project if registered, None otherwise
        """
        return self.repo.get_by_path(path)

    def list_all(self, limit: Optional[int] = None) -> List[Project]:
        """
        Get all registered projects.

        Args:
            limit: Optional max number to return

        Returns:
            List of all projects
        """
        return self.repo.list_all(limit=limit)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Dict with total count, active count, etc.
        """
        all_projects = self.repo.list_all()

        active = sum(1 for p in all_projects if p.status == ProjectStatus.ACTIVE)
        onboarding = sum(1 for p in all_projects if p.status == ProjectStatus.ONBOARDING)
        archived = sum(1 for p in all_projects if p.status == ProjectStatus.ARCHIVED)

        return {
            "total": len(all_projects),
            "active": active,
            "onboarding": onboarding,
            "archived": archived,
            "scan_cache": self._scan_cache
        }
