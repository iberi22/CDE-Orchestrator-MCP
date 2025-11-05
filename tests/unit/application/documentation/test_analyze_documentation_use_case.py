"""
Unit tests for the AnalyzeDocumentationUseCase.
"""
import pytest
from unittest.mock import patch, MagicMock
from cde_orchestrator.application.documentation import AnalyzeDocumentationUseCase

@pytest.fixture
def use_case():
    return AnalyzeDocumentationUseCase()

@patch('pathlib.Path.rglob')
def test_analyze_documentation_quality_score(mock_rglob, use_case):
    """Tests the quality score calculation."""
    # Simulate finding two files, one good, one with a broken link
    mock_file_ok = MagicMock()
    mock_file_ok.read_text.return_value = "---\ntitle: OK\n---\n[link](valid.md)"

    mock_file_broken = MagicMock()
    mock_file_broken.read_text.return_value = "---\ntitle: Broken\n---\n[link](broken.md)"

    mock_rglob.return_value = [mock_file_ok, mock_file_broken]

    # Mock exists to control link validation
    with patch('pathlib.Path.exists', side_effect=[True, False]): # valid.md exists, broken.md does not
        result = use_case.execute("/fake/project")

    assert "quality_score" in result
    assert 0 < result["quality_score"] < 100
    assert len(result["link_analysis"]["broken_links"]) == 1

@patch('pathlib.Path.rglob')
def test_analyze_documentation_no_docs(mock_rglob, use_case):
    """Tests analysis of a project with no markdown files."""
    mock_rglob.return_value = []
    result = use_case.execute("/fake/project")

    assert result["quality_score"] == 0
    assert "No markdown files found" in result["suggestions"][0]
