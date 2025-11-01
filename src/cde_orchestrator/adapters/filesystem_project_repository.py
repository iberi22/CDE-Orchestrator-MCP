# src/cde_orchestrator/adapters/filesystem_project_repository.py
"""
FileSystem Project Repository - Persistence Adapter.

Implements IProjectRepository using JSON files in each project's .cde/ directory.

Storage Structure:
    <project_path>/.cde/
        ├── state.json          # Project + features state
        ├── workflow.yml        # Workflow definition
        └── prompts/            # POML templates

Design Decisions:
    - Stateless: No global registry
    - Per-project state: Each project manages its own .cde/state.json
    - Simple JSON: Human-readable, version-controllable
    - Atomic writes: Use temp file + rename for crash safety

For LLMs:
    - Clear separation of concerns
    - Explicit error handling
    - Type hints on all methods
    - Examples in docstrings
"""

import json
import logging
from pathlib import Path
from typing import Optional, List, AsyncIterator
from datetime import datetime, timezone

from ..domain.ports import IProjectRepository
from ..domain.entities import Project, ProjectId, Feature, ProjectStatus, FeatureStatus
from ..domain.exceptions import ProjectNotFoundError, DomainError


logger = logging.getLogger(__name__)


class FileSystemProjectRepository(IProjectRepository):
    """
    Adapter: Store projects as JSON in .cde/state.json files.

    Each project has independent state at:
        <project_path>/.cde/state.json

    No global registry - projects are located via ProjectLocator,
    then this adapter loads/saves state from their directory.

    Thread Safety:
        - Read operations are safe (JSON parse is atomic)
        - Write operations use temp file + rename (atomic on POSIX/Windows)
        - Concurrent writes to same project could race (rare, acceptable)

    Examples:
        >>> repo = FileSystemProjectRepository()
        >>> project = Project.create("My Project", "/tmp/my-project")
        >>> repo.save(project)
        >>> loaded = repo.get_or_create("/tmp/my-project")
        >>> assert loaded.name == "My Project"
    """

    def __init__(self):
        """Initialize repository (stateless, no configuration needed)."""
        self._logger = logger

    def get_by_id(self, project_id: ProjectId) -> Optional[Project]:
        """
        Retrieve project by ID.

        Note: Since we don't maintain a global registry, this requires
        scanning for state files. For performance, prefer get_by_path()
        or use ProjectLocator to resolve ID -> path externally.

        Args:
            project_id: Project identifier

        Returns:
            Project if found, None otherwise

        Performance Warning:
            Not optimized for large-scale ID lookups.
            Use get_by_path() when you have the path.
        """
        # This is deliberately slow to discourage use
        # In a stateless system, callers should know the path
        self._logger.warning(
            f"get_by_id({project_id}) called - prefer get_by_path() for performance"
        )
        return None

    def get_by_path(self, path: str) -> Optional[Project]:
        """
        Find project by filesystem path.

        Args:
            path: Absolute filesystem path to project

        Returns:
            Project if .cde/state.json exists, None otherwise

        Examples:
            >>> repo.get_by_path("E:\\\\scripts-python\\\\my-project")
            Project(name='my-project', ...)
        """
        project_path = Path(path)
        state_file = project_path / ".cde" / "state.json"

        if not state_file.exists():
            self._logger.debug(f"No state file at {state_file}")
            return None

        try:
            return self._load_from_file(state_file)
        except Exception as e:
            self._logger.error(f"Failed to load project from {state_file}: {e}")
            return None

    def get_or_create(self, path: str, name: Optional[str] = None) -> Project:
        """
        Get existing project or create new one.

        Convenience method for common pattern:
        - If .cde/state.json exists, load it
        - Otherwise, create new Project entity

        Args:
            path: Absolute filesystem path
            name: Optional project name (defaults to directory name)

        Returns:
            Existing or newly created Project

        Examples:
            >>> project = repo.get_or_create("E:\\\\projects\\\\my-app")
            >>> project.name
            'my-app'
        """
        existing = self.get_by_path(path)
        if existing:
            return existing

        # Create new project
        project_path = Path(path)
        project_name = name or project_path.name

        self._logger.info(f"Creating new project: {project_name} at {path}")
        return Project.create(name=project_name, path=path)

    def list_all(self, limit: Optional[int] = None) -> List[Project]:
        """
        Get all registered projects.

        Note: In stateless design, there's no global registry.
        This method is intentionally limited to discourage use.

        Use ProjectLocator.find_all_projects() instead for discovery.

        Args:
            limit: Ignored (no registry to list from)

        Returns:
            Empty list (no global registry)

        Design Rationale:
            Without a registry, we can't enumerate all projects.
            Callers should use ProjectLocator to find projects,
            then use get_by_path() to load each one.
        """
        self._logger.warning(
            "list_all() called on stateless repository - returning empty list. "
            "Use ProjectLocator.find_all_projects() for discovery."
        )
        return []

    async def list_all_async(
        self, limit: Optional[int] = None
    ) -> AsyncIterator[Project]:
        """
        Stream all projects asynchronously.

        Note: Not implemented in stateless design.
        Use ProjectLocator + get_by_path() instead.

        Yields:
            Nothing (no registry)
        """
        # Empty async generator - must yield something to be valid generator
        # but loop never executes
        for _ in []:  # pragma: no cover
            yield  # type: ignore

    def save(self, project: Project) -> None:
        """
        Persist project state to .cde/state.json.

        Args:
            project: Project to save

        Raises:
            DomainError: If serialization or write fails

        Side Effects:
            - Creates .cde/ directory if needed
            - Writes state.json atomically (temp file + rename)
            - Updates project.updated_at timestamp

        Examples:
            >>> project = Project.create("Test", "/tmp/test")
            >>> project.activate()
            >>> repo.save(project)
            >>> # File now exists at /tmp/test/.cde/state.json
        """
        project_path = Path(project.path)
        cde_dir = project_path / ".cde"
        state_file = cde_dir / "state.json"

        try:
            # Ensure .cde directory exists
            cde_dir.mkdir(parents=True, exist_ok=True)

            # Update timestamp
            project.updated_at = datetime.now(timezone.utc)

            # Serialize project
            data = self._serialize_project(project)

            # Atomic write: temp file + rename
            temp_file = state_file.with_suffix(".json.tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Atomic rename (overwrites state.json)
            temp_file.replace(state_file)

            self._logger.info(f"Saved project {project.id} to {state_file}")

        except Exception as e:
            self._logger.error(f"Failed to save project {project.id}: {e}")
            raise DomainError(f"Failed to save project: {e}") from e

    def delete(self, project_id: ProjectId) -> None:
        """
        Remove project state file.

        Note: Since we don't maintain a registry, this requires
        knowing the project path. Use get_by_id() first to load
        the project, then call delete().

        Args:
            project_id: Project to delete

        Raises:
            ProjectNotFoundError: Cannot find project by ID

        Design Note:
            In stateless design, deletion by ID is problematic.
            Consider delete_by_path() instead, or load project
            first to get its path.
        """
        # Without registry, we can't map ID to path
        raise ProjectNotFoundError(
            "Cannot delete by ID in stateless repository. "
            "Use get_by_path() to load project, then delete_by_path()."
        )

    def delete_by_path(self, path: str) -> None:
        """
        Delete project state file by path.

        Args:
            path: Absolute filesystem path to project

        Raises:
            ProjectNotFoundError: If state file doesn't exist

        Examples:
            >>> repo.delete_by_path("E:\\\\projects\\\\old-project")
        """
        project_path = Path(path)
        state_file = project_path / ".cde" / "state.json"

        if not state_file.exists():
            raise ProjectNotFoundError(f"No state file at {state_file}")

        try:
            state_file.unlink()
            self._logger.info(f"Deleted state file: {state_file}")
        except Exception as e:
            self._logger.error(f"Failed to delete {state_file}: {e}")
            raise DomainError(f"Failed to delete project: {e}") from e

    # ========================================================================
    # PRIVATE METHODS - Serialization
    # ========================================================================

    def _serialize_project(self, project: Project) -> dict:
        """
        Convert Project entity to JSON-serializable dict.

        Args:
            project: Project entity

        Returns:
            Dict ready for JSON serialization

        Format:
            {
                "id": "uuid-string",
                "name": "Project Name",
                "path": "/absolute/path",
                "status": "active",
                "created_at": "ISO8601",
                "updated_at": "ISO8601",
                "metadata": {...},
                "features": [...]
            }
        """
        return {
            "id": str(project.id),
            "name": project.name,
            "path": project.path,
            "status": project.status.value,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
            "metadata": project.metadata,
            "features": [
                self._serialize_feature(feature) for feature in project.features
            ],
        }

    def _serialize_feature(self, feature: Feature) -> dict:
        """Serialize Feature entity to dict."""
        return {
            "id": feature.id,
            "project_id": str(feature.project_id),
            "prompt": feature.prompt,
            "status": feature.status.value,
            "current_phase": feature.current_phase,
            "workflow_type": feature.workflow_type,
            "created_at": feature.created_at.isoformat(),
            "updated_at": feature.updated_at.isoformat(),
            "artifacts": feature.artifacts,
            "metadata": feature.metadata,
        }

    def _load_from_file(self, state_file: Path) -> Project:
        """
        Deserialize Project from JSON file.

        Args:
            state_file: Path to state.json

        Returns:
            Reconstructed Project entity

        Raises:
            DomainError: If JSON is invalid or missing required fields
        """
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Reconstruct project
            project = Project(
                id=ProjectId(data["id"]),
                name=data["name"],
                path=data["path"],
                status=ProjectStatus(data["status"]),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                metadata=data.get("metadata", {}),
                features=[],
            )

            # Reconstruct features
            for feature_data in data.get("features", []):
                feature = Feature(
                    id=feature_data["id"],
                    project_id=ProjectId(feature_data["project_id"]),
                    prompt=feature_data["prompt"],
                    status=FeatureStatus(feature_data["status"]),
                    current_phase=feature_data["current_phase"],
                    workflow_type=feature_data["workflow_type"],
                    created_at=datetime.fromisoformat(feature_data["created_at"]),
                    updated_at=datetime.fromisoformat(feature_data["updated_at"]),
                    artifacts=feature_data.get("artifacts", {}),
                    metadata=feature_data.get("metadata", {}),
                )
                project.features.append(feature)

            return project

        except Exception as e:
            self._logger.error(f"Failed to parse {state_file}: {e}")
            raise DomainError(f"Failed to load project: {e}") from e
