# tests/integration/test_rust_scanner_integration.py
import json
import os

# Add src to path
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from cde_orchestrator.application.onboarding.project_analysis_use_case import (
    ProjectAnalysisUseCase,
)


class TestRustScannerIntegration(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory with various files."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name
        self.root = Path(self.project_path)

        # Create standard files
        (self.root / "main.py").write_text("print('hello')")
        (self.root / "requirements.txt").write_text("requests")
        (self.root / "README.md").write_text("# Project")

        # Create excluded directory
        (self.root / "node_modules").mkdir()
        (self.root / "node_modules" / "lib.js").write_text("console.log('hi')")

        # Create excluded file pattern
        (self.root / "test.pyc").write_bytes(b"binary")

        # Create .gitignore
        (self.root / ".gitignore").write_text("ignored.log\nsecret.key")
        (self.root / "ignored.log").write_text("log")
        (self.root / "secret.key").write_text("secret")
        (self.root / "included.txt").write_text("included")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_rust_scan_project_py(self):
        """Test that the Rust scan_project_py function works correctly."""
        try:
            import cde_rust_core

        except ImportError:
            self.fail(
                "Failed to import cde_rust_core. Make sure it's compiled and installed."
            )

        excluded_dirs = ["node_modules"]
        excluded_patterns = ["*.pyc"]

        # Execute Rust function
        json_result = cde_rust_core.scan_project_py(
            str(self.root), excluded_dirs, excluded_patterns
        )

        result = json.loads(json_result)

        # Verify structure
        self.assertIn("file_count", result)
        self.assertIn("language_stats", result)
        self.assertIn("dependency_files", result)
        self.assertIn("excluded_count", result)

        # Verify counts
        # Expected files: main.py, requirements.txt, README.md, .gitignore, included.txt = 5
        self.assertEqual(result["file_count"], 5)

        # Verify dependency files
        self.assertIn("requirements.txt", result["dependency_files"])

        # Verify language stats
        stats = result["language_stats"]
        self.assertEqual(stats.get(".py"), 1)
        self.assertEqual(stats.get(".txt"), 2)  # requirements.txt, included.txt

        # Verify exclusions
        # node_modules/lib.js (1), test.pyc (1), ignored.log (1), secret.key (1) = 4
        self.assertGreaterEqual(result["excluded_count"], 4)

    def test_compare_rust_vs_python(self):
        """Compare Rust implementation results with Python implementation."""
        try:
            import cde_rust_core
        except ImportError:
            self.skipTest("cde_rust_core not available")

        use_case = ProjectAnalysisUseCase()

        # Run Python implementation explicitly
        python_result = use_case._execute_python(str(self.root), lambda *args: None)

        # Run Rust implementation explicitly
        rust_result = use_case._execute_rust(str(self.root), lambda *args: None)

        # Compare file counts
        # Note: Python implementation might count differently depending on exact logic
        # But for this simple case they should match
        # Python implementation in _execute_python calls _list_files which respects gitignore?
        # Let's check _list_files implementation if needed, but assuming they should match.

        # Rust returns raw counts, Python returns processed summary.
        # But _execute_rust returns a dict with "file_count".

        self.assertEqual(rust_result["file_count"], python_result["file_count"])

        # Check dependency files match
        self.assertEqual(
            sorted(rust_result["dependency_files"]),
            sorted(python_result["dependency_files"]),
        )

        # Check language stats match (at least for main extensions)
        # Python uses Counter, Rust uses dict.
        self.assertEqual(
            rust_result["language_stats"].get(".py"),
            python_result["language_stats"].get(".py"),
        )
