"""
Integration tests for the enrichment pipeline.

Tests the complete flow: GitHistoryAnalyzer -> DocumentationSynthesizer ->
FrameworkDetector -> ProjectContextEnricher -> AIConfigUseCase templates.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cde_orchestrator.application.ai_config import AIConfigUseCase
from cde_orchestrator.application.onboarding.project_context_enricher import (
    ProjectContextEnricher,
)


class TestEnrichmentPipeline:
    """Integration tests for enrichment pipeline."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project structure for testing."""
        temp_dir = Path(tempfile.mkdtemp())

        # Create basic project structure
        (temp_dir / "src").mkdir()
        (temp_dir / "tests").mkdir()
        (temp_dir / ".git").mkdir()

        # Create README.md
        readme = temp_dir / "README.md"
        readme.write_text(
            """# Test Project

## Architecture

This project uses Hexagonal (Ports & Adapters) architecture with FastMCP.

## Tech Stack

- Python 3.14
- FastMCP
- pytest
"""
        )

        # Create pyproject.toml
        pyproject = temp_dir / "pyproject.toml"
        pyproject.write_text(
            """[project]
name = "test-project"
version = "1.0.0"
dependencies = [
    "fastmcp>=2.0.0",
    "pytest>=7.0.0"
]
"""
        )

        yield temp_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    @patch("cde_orchestrator.application.onboarding.git_history_analyzer.Repo")
    def test_enrichment_pipeline_integration(self, mock_repo, temp_project):
        """Test complete enrichment pipeline produces enriched context."""
        # Mock Git repository
        mock_repo_instance = MagicMock()
        mock_repo_instance.heads = []
        mock_repo_instance.git.log.return_value = ""
        mock_repo.return_value = mock_repo_instance

        # Create enricher
        enricher = ProjectContextEnricher(temp_project)

        # Create basic analysis result
        basic_analysis = {
            "file_count": 10,
            "language_stats": {".py": 8, ".md": 2},
        }

        # Run enrichment
        enriched = enricher.enrich_sync(basic_analysis)

        # Verify enriched context has expected fields
        assert enriched.file_count == 10
        assert enriched.language_stats == {".py": 8, ".md": 2}
        assert enriched.architecture_description is not None
        assert "Hexagonal" in enriched.architecture_description
        assert "FastMCP" in enriched.tech_stack
        assert "pytest" in enriched.tech_stack

    @patch("cde_orchestrator.application.onboarding.git_history_analyzer.Repo")
    def test_enriched_context_in_templates(self, mock_repo, temp_project):
        """Test that enriched context populates templates correctly."""
        # Mock Git
        mock_repo_instance = MagicMock()
        mock_repo_instance.heads = []
        mock_repo_instance.git.log.return_value = ""
        mock_repo.return_value = mock_repo_instance

        # Create enriched context
        enricher = ProjectContextEnricher(temp_project)
        basic_analysis = {
            "file_count": 10,
            "language_stats": {".py": 8, ".md": 2},
        }
        enriched = enricher.enrich_sync(basic_analysis)
        enriched_dict = enricher.to_dict(enriched)

        # Create AI config use case
        ai_config = AIConfigUseCase(temp_project)

        # Generate AGENTS.md with enriched context
        agents_md = ai_config._get_agents_md_template("test-project", enriched_dict)

        # Verify template has real data, not placeholders
        assert "[Architecture pattern]" not in agents_md
        assert "[Primary language]" not in agents_md
        assert "[Tech stack]" not in agents_md

        # Verify actual data is present
        assert "Hexagonal" in agents_md
        assert "Python" in agents_md
        assert "FastMCP" in agents_md or "pytest" in agents_md

    def test_enriched_context_handles_missing_files(self, temp_project):
        """Test enrichment gracefully handles missing documentation files."""
        # Remove README
        readme = temp_project / "README.md"
        if readme.exists():
            readme.unlink()

        # Create enricher
        enricher = ProjectContextEnricher(temp_project)

        # Should not crash
        basic_analysis = {
            "file_count": 5,
            "language_stats": {".py": 5},
        }

        enriched = enricher.enrich_sync(basic_analysis)

        # Should have default values
        assert enriched.file_count == 5
        assert enriched.architecture_description == ""
        assert enriched.tech_stack == []

    @patch("cde_orchestrator.application.onboarding.git_history_analyzer.Repo")
    def test_framework_detection_in_enrichment(self, mock_repo, temp_project):
        """Test that framework detection works in enrichment pipeline."""
        # Mock Git
        mock_repo_instance = MagicMock()
        mock_repo_instance.heads = []
        mock_repo_instance.git.log.return_value = ""
        mock_repo.return_value = mock_repo_instance

        # Create FastMCP indicator file
        (temp_project / "src" / "server.py").write_text(
            """
from fastmcp import FastMCP

mcp = FastMCP("test-server")
"""
        )

        # Create enricher
        enricher = ProjectContextEnricher(temp_project)

        basic_analysis = {
            "file_count": 10,
            "language_stats": {".py": 10},
        }

        enriched = enricher.enrich_sync(basic_analysis)

        # Verify FastMCP was detected
        assert (
            "FastMCP" in enriched.detected_frameworks
            or "fastmcp" in enriched.detected_frameworks
        )


class TestEnrichmentEdgeCases:
    """Test edge cases and error handling."""

    def test_enrichment_with_empty_project(self):
        """Test enrichment with minimal/empty project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            enricher = ProjectContextEnricher(temp_path)

            basic_analysis = {
                "file_count": 0,
                "language_stats": {},
            }

            # Should not crash
            enriched = enricher.enrich_sync(basic_analysis)

            assert enriched.file_count == 0
            assert enriched.language_stats == {}

    def test_enrichment_without_git(self):
        """Test enrichment when Git is not available."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # No .git directory
            enricher = ProjectContextEnricher(temp_path)

            basic_analysis = {
                "file_count": 5,
                "language_stats": {".py": 5},
            }

            # Should not crash, should fall back gracefully
            enriched = enricher.enrich_sync(basic_analysis)

            assert enriched.file_count == 5
            # Git insights should be empty or default
            assert enriched.recent_commits == []
