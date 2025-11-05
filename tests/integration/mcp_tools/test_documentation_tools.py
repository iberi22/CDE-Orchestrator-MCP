# tests/integration/mcp_tools/test_documentation_tools.py
import json
import os
import unittest
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.mcp_tools.documentation import cde_scanDocumentation

class TestDocumentationTools(unittest.TestCase):

    def test_cde_scanDocumentation_runs_successfully(self):
        """
        Verify that cde_scanDocumentation runs and returns a valid JSON report.
        """
        # We run it on the current project directory as a simple test case
        project_path = str(Path(__file__).resolve().parents[3])

        result_json = cde_scanDocumentation(project_path=project_path)

        self.assertIsInstance(result_json, str)

        data = json.loads(result_json)

        self.assertIn("total_docs", data)
        self.assertIn("recommendations", data)
        self.assertIsInstance(data["total_docs"], int)

    def test_cde_analyzeDocumentation_runs_successfully(self):
        """
        Verify that cde_analyzeDocumentation runs and returns the expected JSON structure.
        """
        from src.mcp_tools.documentation import cde_analyzeDocumentation

        project_path = str(Path(__file__).resolve().parents[3])
        result_json = cde_analyzeDocumentation(project_path=project_path)

        self.assertIsInstance(result_json, str)
        data = json.loads(result_json)

        self.assertIn("quality_score", data)
        self.assertIn("link_analysis", data)
        self.assertIn("issues", data)
        self.assertIsInstance(data["quality_score"], (int, float))

    def test_cde_createSpecification_runs_successfully(self):
        """
        Verify that cde_createSpecification creates a file and returns its path.
        """
        from src.mcp_tools.documentation import cde_createSpecification
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / "specs" / "features").mkdir(parents=True)

            result_json = cde_createSpecification(
                feature_name="Test Feature",
                description="A feature for testing.",
                author="Test Runner",
                project_path=str(project_path)
            )

            self.assertIsInstance(result_json, str)
            data = json.loads(result_json)

            self.assertIn("filepath", data)
            self.assertTrue((project_path / data["filepath"]).exists())
            self.assertIn("test-feature.md", data["filepath"])

if __name__ == "__main__":
    unittest.main()
