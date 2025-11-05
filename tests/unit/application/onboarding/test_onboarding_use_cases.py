# tests/unit/application/onboarding/test_onboarding_use_cases.py
import unittest
import tempfile
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from src.cde_orchestrator.application.onboarding.project_analysis_use_case import ProjectAnalysisUseCase
from src.cde_orchestrator.application.onboarding.publishing_use_case import PublishingUseCase

class TestOnboardingUseCases(unittest.TestCase):

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
