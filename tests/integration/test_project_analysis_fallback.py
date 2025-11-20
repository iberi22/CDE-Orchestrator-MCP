# tests/integration/test_project_analysis_fallback.py
import os
import sys
import unittest
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from cde_orchestrator.application.onboarding.project_analysis_use_case import (
    ProjectAnalysisUseCase,
)


class TestProjectAnalysisFallback(unittest.TestCase):

    def test_fallback_when_rust_unavailable(self):
        """Test that fallback works when Rust module is not available."""
        use_case = ProjectAnalysisUseCase()

        # Mock _execute_rust to raise Exception (simulating ImportError wrapped in Exception)
        use_case._execute_rust = MagicMock(
            side_effect=Exception("cde_rust_core not available")
        )

        # Mock _execute_python to verify it gets called
        use_case._execute_python = MagicMock(return_value={"status": "fallback"})

        # Execute
        result = use_case.execute(".")

        # Verify
        self.assertEqual(result["status"], "fallback")
        use_case._execute_python.assert_called_once()

    def test_fallback_when_rust_fails(self):
        """Test that fallback works when Rust module fails during execution."""
        use_case = ProjectAnalysisUseCase()

        # Mock _execute_rust to raise Exception
        use_case._execute_rust = MagicMock(side_effect=Exception("Rust analysis error"))

        # Mock _execute_python
        use_case._execute_python = MagicMock(return_value={"status": "fallback"})

        # Execute
        result = use_case.execute(".")

        # Verify
        self.assertEqual(result["status"], "fallback")
        use_case._execute_python.assert_called_once()

    def test_rust_used_when_available(self):
        """Test that Rust is used when available and working."""
        use_case = ProjectAnalysisUseCase()

        # Mock _execute_rust to return success
        use_case._execute_rust = MagicMock(
            return_value={"file_count": 10, "status": "success"}
        )

        # Mock _execute_python to ensure it's NOT called
        use_case._execute_python = MagicMock()

        # Execute
        result = use_case.execute(".")

        # Verify
        self.assertEqual(result["file_count"], 10)
        use_case._execute_python.assert_not_called()
        use_case._execute_rust.assert_called_once()
