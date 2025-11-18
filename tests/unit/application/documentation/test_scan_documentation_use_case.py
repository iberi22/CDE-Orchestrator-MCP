"""
Unit tests for the ScanDocumentationUseCase.
"""

import pytest

from cde_orchestrator.application.documentation import ScanDocumentationUseCase


@pytest.fixture
def project_dir(tmp_path):
    """Creates a temporary project structure for documentation scanning tests."""
    # Valid docs
    (tmp_path / "specs" / "features").mkdir(parents=True)
    (tmp_path / "specs" / "features" / "feature-a.md").write_text(
        "---\ntitle: A\n---\n"
    )

    (tmp_path / "agent-docs" / "sessions").mkdir(parents=True)
    (tmp_path / "agent-docs" / "sessions" / "session-1.md").write_text(
        "---\ntitle: S1\n---\n"
    )

    # Doc with missing metadata
    (tmp_path / "specs" / "design").mkdir(parents=True)
    (tmp_path / "specs" / "design" / "design-b.md").write_text("No frontmatter here.")

    # Orphaned doc
    (tmp_path / "orphaned.md").write_text("---\ntitle: Orphan\n---\n")

    return tmp_path


def test_scan_documentation_success(project_dir):
    """Tests scanning a project with a mix of valid and invalid docs."""
    use_case = ScanDocumentationUseCase()
    result = use_case.execute(str(project_dir))

    assert result["total_docs"] == 4
    assert len(result["missing_metadata"]) == 1
    assert any("design-b.md" in path for path in result["missing_metadata"])

    assert result["orphaned_count"] == 1


def test_scan_documentation_no_specs_dir(tmp_path):
    """Tests scanning a project with no specs directory."""
    use_case = ScanDocumentationUseCase()
    result = use_case.execute(str(tmp_path))

    assert result["total_docs"] == 0
    assert len(result["recommendations"]) > 0
    assert any(
        "No specs/features directory found" in rec for rec in result["recommendations"]
    )
