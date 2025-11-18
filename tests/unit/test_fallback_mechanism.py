# tests/unit/test_fallback_mechanism.py
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

# Ensure src is in the path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
)

from cde_orchestrator.application.documentation.scan_documentation_use_case import (  # noqa: E402
    ScanDocumentationUseCase,
)


class TestFallbackMechanism(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory with dummy markdown files."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name

        # Create a more complete directory structure
        os.makedirs(os.path.join(self.project_path, "specs", "features"))
        os.makedirs(os.path.join(self.project_path, "docs"))

        # Add a file to specs/features to satisfy the check
        with open(
            os.path.join(self.project_path, "specs", "features", "feature.md"), "w"
        ) as f:
            f.write("---\ntitle: Feature\n---\n")

        # Create a README with frontmatter
        with open(os.path.join(self.project_path, "README.md"), "w") as f:
            f.write("---\n")
            f.write("title: Test Readme\n")
            f.write("---\n")
            f.write("This is a test.")

        # Create a doc in a standard location
        with open(os.path.join(self.project_path, "docs", "guide.md"), "w") as f:
            f.write("---\n")
            f.write("title: Guide\n")
            f.write("---\n")
            f.write("A guide.")

    def tearDown(self):
        """Clean up the temporary directory."""
        self.temp_dir.cleanup()

    @patch("importlib.util.find_spec")
    def test_scan_with_python_fallback(self, mock_find_spec):
        """
        Verify that the Python implementation is used when the Rust module is not available.
        """

        # Simulate that cde_rust_core is not available
        mock_find_spec.return_value = None

        use_case = ScanDocumentationUseCase()

        # We need to mock the internal python scan method to check if it was called
        with patch.object(
            use_case, "_scan_with_python", wraps=use_case._scan_with_python
        ) as spy_python_scan:
            result = use_case.execute(self.project_path)

            # Verify that the Python method was called
            spy_python_scan.assert_called_once_with(self.project_path, "summary")

            # Verify the results are from the Python implementation
            self.assertEqual(result["total_docs"], 3)
            # In summary mode, files are in a flat list with location info
            file_paths = [f["path"] for f in result["files"]]
            self.assertIn("README.md", file_paths)
            # Handle Windows path separators
            self.assertTrue(any("guide.md" in path for path in file_paths))
            self.assertTrue(any("feature.md" in path for path in file_paths))
            self.assertIn(
                "✅", result["recommendations"][0]
            )  # Should be a success message

    def test_scan_with_rust_preferred(self):
        """
        Verify that the Rust implementation is used and the result is processed correctly.
        """
        # This test requires the actual cde_rust_core module to be compiled.
        try:
            import importlib.util

            if importlib.util.find_spec("cde_rust_core") is None:
                raise ImportError("cde_rust_core not found")
        except (ImportError, ValueError):
            self.skipTest("Rust module not compiled, skipping full integration test.")

        use_case = ScanDocumentationUseCase()

        # Execute the use case, which should now use the Rust path
        result = use_case.execute(self.project_path)

        # Verify the structure of the result, confirming full processing
        self.assertEqual(result["total_docs"], 3)
        # Check that we have files in the result
        self.assertIn("files", result)
        file_paths = [f["path"] for f in result["files"]]
        self.assertIn("README.md", file_paths)
        # Handle Windows path separators
        self.assertTrue(any("guide.md" in path for path in file_paths))
        self.assertTrue(any("feature.md" in path for path in file_paths))
        self.assertIn("✅", result["recommendations"][0])


if __name__ == "__main__":
    unittest.main()
