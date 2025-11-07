"""
Unit tests for the AnalyzeDocumentationUseCase using pyfakefs.
"""

# Add project root to path
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from src.cde_orchestrator.application.documentation.analyze_documentation_use_case import (
    AnalyzeDocumentationUseCase,
)


@pytest.fixture
def use_case():
    """Provides an instance of the use case for tests."""
    return AnalyzeDocumentationUseCase()


def test_analyze_documentation_quality_score(fs, use_case):
    """Tests the quality score calculation with a fake filesystem."""
    # fs is the pyfakefs fixture
    project_path = "/fake/project"
    fs.create_dir(project_path)

    # Create a valid file with a link to another valid file
    fs.create_file(
        f"{project_path}/docs/valid.md",
        contents="---\ntitle: Valid\ndescription: d\ntype: guide\nstatus: active\ncreated: 2025-01-01\nupdated: 2025-01-01\nauthor: Test\n---\nContent",
    )
    fs.create_file(
        f"{project_path}/docs/file1.md",
        contents="---\ntitle: OK\ndescription: d\ntype: guide\nstatus: active\ncreated: 2025-01-01\nupdated: 2025-01-01\nauthor: Test\n---\n[link](valid.md)",
    )

    # Create a file with a broken link
    fs.create_file(
        f"{project_path}/docs/file2.md",
        contents="---\ntitle: Broken\ndescription: d\ntype: guide\nstatus: active\ncreated: 2025-01-01\nupdated: 2025-01-01\nauthor: Test\n---\n[link](broken.md)",
    )

    result = use_case.execute(project_path)

    assert "quality_score" in result
    assert 0 < result["quality_score"] < 100
    assert len(result["link_analysis"]["broken_links"]) == 1
    assert result["link_analysis"]["broken_links"][0]["target"] == "broken.md"


def test_analyze_documentation_no_docs(fs, use_case):
    """Tests analysis of a project with no markdown files returns a perfect score."""
    project_path = "/fake/project"
    fs.create_dir(project_path)

    result = use_case.execute(project_path)

    assert result["total_analyzed"] == 0
    assert result["quality_score"] == 100.0
