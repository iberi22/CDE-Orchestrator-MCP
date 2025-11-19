"""
Unit tests for the AnalyzeDocumentationUseCase.
"""

# Add project root to path
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from src.cde_orchestrator.application.documentation.analyze_documentation_use_case import (  # noqa: E402
    AnalyzeDocumentationUseCase,
)


@pytest.fixture
def use_case():
    """Provides an instance of the use case for tests."""
    return AnalyzeDocumentationUseCase()


def test_analyze_documentation_quality_score(tmp_path: Path, use_case):
    """Tests the quality score calculation with a temporary filesystem."""
    project_path = tmp_path / "project"
    project_path.mkdir()

    docs_dir = project_path / "docs"
    docs_dir.mkdir()

    # Create a valid file with a link to another valid file
    (docs_dir / "valid.md").write_text(
        "---\ntitle: Valid\ndescription: d\ntype: guide\nstatus: active\ncreated: 2025-01-01\nupdated: 2025-01-01\nauthor: Test\n---\nContent"
    )
    (docs_dir / "file1.md").write_text(
        "---\ntitle: OK\ndescription: d\ntype: guide\nstatus: active\ncreated: 2025-01-01\nupdated: 2025-01-01\nauthor: Test\n---\n[link](valid.md)"
    )

    # Create a file with a broken link
    (docs_dir / "file2.md").write_text(
        "---\ntitle: Broken\ndescription: d\ntype: guide\nstatus: active\ncreated: 2025-01-01\nupdated: 2025-01-01\nauthor: Test\n---\n[link](broken.md)"
    )

    result = use_case.execute(str(project_path))

    assert "quality_score" in result
    assert 0 < result["quality_score"] < 100
    assert len(result["link_analysis"]["broken_links"]) == 1
    assert result["link_analysis"]["broken_links"][0]["target"] == "broken.md"


def test_analyze_documentation_no_docs(tmp_path: Path, use_case):
    """Tests analysis of a project with no markdown files returns a perfect score."""
    project_path = tmp_path / "project"
    project_path.mkdir()

    result = use_case.execute(str(project_path))

    assert result["total_analyzed"] == 0
    assert result["quality_score"] == 100.0
