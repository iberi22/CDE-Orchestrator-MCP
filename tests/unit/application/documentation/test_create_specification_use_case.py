"""
Unit tests for the CreateSpecificationUseCase.
"""

from pathlib import Path

import pytest

from cde_orchestrator.application.documentation import CreateSpecificationUseCase


@pytest.fixture
def use_case():
    return CreateSpecificationUseCase()


def test_create_specification_success(use_case, tmp_path):
    """Tests that a specification file is created successfully."""
    project_path = tmp_path
    feature_name = "New Feature"
    description = "A test feature."
    author = "Test Agent"

    result = use_case.execute(project_path, feature_name, description, author)

    assert "filepath" in result
    filepath = Path(result["filepath"])
    assert filepath.exists()
    assert filepath.name == "new-feature.md"

    content = filepath.read_text()
    assert feature_name in content
    assert description in content
    assert author in content


def test_create_specification_already_exists(use_case, tmp_path):
    """Tests that an error is returned if the file already exists."""
    project_path = tmp_path
    feature_name = "Existing Feature"

    # Create the file first
    spec_dir = project_path / "specs" / "features"
    spec_dir.mkdir(parents=True)
    (spec_dir / "existing-feature.md").touch()

    result = use_case.execute(project_path, feature_name, "desc", "author")

    assert "error" in result
    assert "already exists" in result["error"]
