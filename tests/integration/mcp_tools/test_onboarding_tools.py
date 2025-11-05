# tests/integration/mcp_tools/test_onboarding_tools.py
import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.mcp_tools.onboarding import cde_onboardingProject, cde_publishOnboarding
from fastmcp import Context

class TestOnboardingTools(unittest.TestCase):

    def test_cde_onboardingProject_runs_successfully(self):
        """
        Verify that the cde_onboardingProject stub runs without errors.
        """
        # Mock the dependencies
        mock_ctx = MagicMock(spec=Context)
        mock_use_case = MagicMock()
        mock_use_case.load.return_value = {}

        # The tool is async
        import asyncio
        result_json = asyncio.run(cde_onboardingProject(
            ctx=mock_ctx,
            manage_state_use_case=mock_use_case
        ))

        self.assertIsInstance(result_json, str)
        data = json.loads(result_json)

        # Verify the new, real response
        self.assertEqual(data["status"], "Analysis complete")
        self.assertIn("file_count", data)
        self.assertIn("language_stats", data)
        mock_use_case.save.assert_called_once()

    def test_cde_publishOnboarding_runs_successfully(self):
        """
        Verify that the cde_publishOnboarding stub runs without errors.
        """
        mock_use_case = MagicMock()
        mock_use_case.load.return_value = {}

        result_json = cde_publishOnboarding(
            documents={"doc1.md": "content"},
            manage_state_use_case=mock_use_case,
            approve=True
        )

        self.assertIsInstance(result_json, str)
        data = json.loads(result_json)

        # Verify the new, real response
        self.assertEqual(data["status"], "success")
        self.assertIn("files_written", data)
        self.assertEqual(data["files_written"], ["doc1.md"])
        mock_use_case.save.assert_called_once()

    def test_cde_setupProject_runs_successfully(self):
        """
        Verify that cde_setupProject analyzes and creates config files.
        """
        from src.mcp_tools.onboarding import cde_setupProject
        import tempfile
        import asyncio

        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Create a dummy python file to be detected by the analysis
            (project_path / "main.py").touch()

            mock_ctx = MagicMock(spec=Context)

            result_json = asyncio.run(cde_setupProject(
                ctx=mock_ctx,
                project_path=str(project_path),
                force=True
            ))

            data = json.loads(result_json)

            self.assertEqual(data["status"], "success")
            self.assertIn(".gitignore", data["files_written"])
            self.assertIn("AGENTS.md", data["files_written"])

            # Verify that the files were actually created
            self.assertTrue((project_path / ".gitignore").exists())
            self.assertTrue((project_path / "AGENTS.md").exists())

            # Verify content of .gitignore
            gitignore_content = (project_path / ".gitignore").read_text()
            self.assertIn(".venv/", gitignore_content)
            self.assertIn(".pytest_cache/", gitignore_content)

if __name__ == "__main__":
    unittest.main()
