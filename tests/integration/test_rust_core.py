# tests/integration/test_rust_core.py
import json
import os
import tempfile
import unittest

class TestRustCoreIntegration(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory with dummy markdown files."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name

        # Create some dummy files
        with open(os.path.join(self.project_path, "README.md"), "w") as f:
            f.write("This is the main readme.")
        with open(os.path.join(self.project_path, "doc1.md"), "w") as f:
            f.write("Hello world.")

        # Create a subdirectory with a file
        os.makedirs(os.path.join(self.project_path, "subdir"))
        with open(os.path.join(self.project_path, "subdir", "doc2.md"), "w") as f:
            f.write("Another document.")

        # Create a non-markdown file that should be ignored
        with open(os.path.join(self.project_path, "config.txt"), "w") as f:
            f.write("some config")

    def tearDown(self):
        """Clean up the temporary directory."""
        self.temp_dir.cleanup()

    def test_scan_documentation_py(self):
        """Test that the Rust scan_documentation_py function works correctly."""
        try:
            from cde_rust_core import scan_documentation_py
        except ImportError:
            self.fail("Failed to import cde_rust_core. Make sure it's compiled and installed.")

        # Execute the Rust function
        json_result = scan_documentation_py(self.project_path)
        self.assertIsInstance(json_result, str)

        # Parse and verify the result
        documents = json.loads(json_result)
        self.assertIsInstance(documents, list)
        self.assertEqual(len(documents), 3)

        paths = sorted([doc['path'] for doc in documents])
        expected_paths = sorted([
            os.path.join(self.project_path, "README.md"),
            os.path.join(self.project_path, "doc1.md"),
            os.path.join(self.project_path, "subdir", "doc2.md"),
        ])
        self.assertEqual(paths, expected_paths)

        # Check content of one document
        for doc in documents:
            if "README.md" in doc['path']:
                self.assertEqual(doc['content'], "This is the main readme.")
                self.assertEqual(doc['word_count'], 5)
                break
        else:
            self.fail("README.md not found in scanned documents")

if __name__ == "__main__":
    unittest.main()
