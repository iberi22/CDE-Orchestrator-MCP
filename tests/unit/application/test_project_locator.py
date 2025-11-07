# tests/unit/application/test_project_locator.py
"""
Unit tests for the ProjectLocator application service.
"""
from pathlib import Path
from unittest.mock import patch

import pytest

from src.cde_orchestrator.application.project_locator import ProjectLocator


@pytest.fixture
def temp_projects(tmp_path):
    """Create a temporary directory with some mock projects."""
    projects_root = tmp_path / "projects"
    projects_root.mkdir()

    # Valid project
    project1_path = projects_root / "project1"
    project1_path.mkdir()
    (project1_path / ".git").mkdir()
    (project1_path / ".cde").mkdir()

    # Another valid project
    project2_path = projects_root / "project2"
    project2_path.mkdir()
    (project2_path / ".git").mkdir()
    (project2_path / "specs").mkdir()

    # A directory that is not a git repo
    not_a_project_path = projects_root / "not_a_project"
    not_a_project_path.mkdir()

    return projects_root


class TestProjectLocator:
    """Tests for the ProjectLocator."""

    def test_validate_project_path_valid(self, temp_projects):
        """Test that a valid project path is validated."""
        locator = ProjectLocator()
        assert locator.validate_project_path(str(temp_projects / "project1")) is True

    def test_validate_project_path_invalid(self, temp_projects):
        """Test that a path without a .git directory is invalidated."""
        locator = ProjectLocator()
        assert (
            locator.validate_project_path(str(temp_projects / "not_a_project")) is False
        )

    def test_validate_project_path_nonexistent(self, temp_projects):
        """Test that a nonexistent path is invalidated."""
        locator = ProjectLocator()
        assert (
            locator.validate_project_path(str(temp_projects / "nonexistent")) is False
        )

    def test_find_project_by_name(self, temp_projects):
        """Test finding a project by its directory name."""
        locator = ProjectLocator(scan_roots=[str(temp_projects)])
        found_path = locator.find_project_by_name("project1")
        assert found_path is not None
        assert Path(found_path).name == "project1"

    def test_find_project_by_name_case_insensitive(self, temp_projects):
        """Test case-insensitive project search."""
        locator = ProjectLocator(scan_roots=[str(temp_projects)])
        found_path = locator.find_project_by_name("PROJECT1")
        assert found_path is not None
        assert Path(found_path).name == "project1"

    def test_find_project_by_name_not_found(self, temp_projects):
        """Test that a nonexistent project is not found."""
        locator = ProjectLocator(scan_roots=[str(temp_projects)])
        found_path = locator.find_project_by_name("nonexistent")
        assert found_path is None

    def test_get_project_info(self, temp_projects):
        """Test getting basic information for a project."""
        locator = ProjectLocator()
        info = locator.get_project_info(str(temp_projects / "project1"))
        assert info["name"] == "project1"
        assert info["exists"] is True
        assert info["is_git"] is True
        assert info["has_cde"] is True
        assert info["has_specs"] is False

    def test_resolve_project_path_with_explicit_path(self, temp_projects):
        """Test resolving a project with an explicit, valid path."""
        locator = ProjectLocator()
        path = str(temp_projects / "project1")
        resolved = locator.resolve_project_path(project_path=path)
        assert resolved == path

    def test_resolve_project_path_with_name(self, temp_projects):
        """Test resolving a project by name."""
        locator = ProjectLocator(scan_roots=[str(temp_projects)])
        resolved = locator.resolve_project_path(project_name="project2")
        assert resolved is not None
        assert Path(resolved).name == "project2"

    def test_resolve_project_path_with_fallback_to_cwd(self, temp_projects):
        """Test resolving a project by falling back to the current working directory."""
        locator = ProjectLocator()
        with patch("pathlib.Path.cwd", return_value=temp_projects / "project1"):
            resolved = locator.resolve_project_path(fallback_to_cwd=True)
            assert resolved is not None
            assert Path(resolved).name == "project1"

    def test_resolve_project_path_priority(self, temp_projects):
        """Test that explicit path has priority over name."""
        locator = ProjectLocator(scan_roots=[str(temp_projects)])
        path1 = str(temp_projects / "project1")
        resolved = locator.resolve_project_path(
            project_path=path1, project_name="project2"
        )
        assert resolved == path1

    def test_resolve_project_path_invalid_path_returns_none(self, temp_projects):
        """Test that an invalid explicit path returns None."""
        locator = ProjectLocator()
        path = str(temp_projects / "not_a_project")
        resolved = locator.resolve_project_path(project_path=path)
        assert resolved is None
