# tests/unit/application/onboarding/test_onboarding_use_cases.py
import unittest
import tempfile
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from src.cde_orchestrator.application.onboarding.project_analysis_use_case import ProjectAnalysisUseCase
from src.cde_orchestrator.application.onboarding.publishing_use_case import PublishingUseCase
from src.cde_orchestrator.application.onboarding.project_setup_use_case import ProjectSetupUseCase
from unittest.mock import MagicMock

class TestOnboardingUseCases(unittest.TestCase):
    def test_project_setup_use_case(self):
        """
        Verify that ProjectSetupUseCase orchestrates analysis and publishing.
        """
        # Mocks for dependencies
        mock_analysis_uc = MagicMock(spec=ProjectAnalysisUseCase)
        mock_publishing_uc = MagicMock(spec=PublishingUseCase)

        # Mock return values
        mock_analysis_uc.execute.return_value = {
            "language_stats": {".py": 10},
            "dependency_files": ["requirements.txt"],
            "summary": "A Python project."
        }
        mock_publishing_uc.execute.return_value = {
            "status": "success",
            "files_written": [".gitignore", "AGENTS.md"]
        }

        # Instantiate the use case with mocks
        setup_use_case = ProjectSetupUseCase(mock_analysis_uc, mock_publishing_uc)

        result = setup_use_case.execute("/fake/project")

        # Verify that dependencies were called
        mock_analysis_uc.execute.assert_called_once_with("/fake/project")

        # Verify that the correct files were generated and passed to the publisher
        expected_docs = {
            ".gitignore": "# Generic ignores\n.env\n.venv/\nvenv/\n__pycache__/\n*.pyc\n\n# Python specific\n.pytest_cache/\n",
            "AGENTS.md": """# AI Agent Guidelines (AGENTS.md)

This document provides instructions for AI agents working on this repository.

## Project Structure
- The main source code is located in the `src/` directory.
- Tests are located in the `tests/` directory.
- This project uses a Hexagonal Architecture. Keep domain, application, and infrastructure layers separate.

## Coding Conventions
- Follow PEP 8 for Python code.
- Use the pre-commit hooks configured in `.pre-commit-config.yaml`.

## Your Role
- **Analyze Before You Act:** Use tools like `cde_scanDocumentation` to understand the project state.
- **Follow the Workflow:** Do not commit directly to `main`. Follow the feature workflow.
- **Communicate Clearly:** Provide clear commit messages and pull request descriptions.
"""
        }
        mock_publishing_uc.execute.assert_called_once_with("/fake/project", expected_docs)

        # Verify the final report
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["files_written"], [".gitignore", "AGENTS.md"])


    def test_project_analysis_use_case(self):
        """
        Verify that ProjectAnalysisUseCase correctly analyzes a dummy project.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / "src").mkdir()
            (project_path / "src" / "main.py").touch()
            (project_path / "requirements.txt").touch()

            use_case = ProjectAnalysisUseCase()
            result = use_case.execute(str(project_path))

            self.assertEqual(result["file_count"], 2)
            self.assertIn(".py", result["language_stats"])
            self.assertEqual(result["language_stats"][".py"], 1)
            self.assertEqual(result["dependency_files"], ["requirements.txt"])

    def test_publishing_use_case(self):
        """
        Verify that PublishingUseCase correctly writes files.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            documents = {
                "README.md": "# Hello",
                "docs/guide.md": "A guide."
            }

            use_case = PublishingUseCase()
            result = use_case.execute(str(project_path), documents)

            self.assertEqual(result["status"], "success")
            self.assertEqual(len(result["files_written"]), 2)

            self.assertTrue((project_path / "README.md").exists())
            self.assertTrue((project_path / "docs" / "guide.md").exists())
            self.assertEqual((project_path / "docs" / "guide.md").read_text(), "A guide.")

if __name__ == "__main__":
    unittest.main()
