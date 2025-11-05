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

if __name__ == "__main__":
    unittest.main()
