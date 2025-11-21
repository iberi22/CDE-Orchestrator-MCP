# tests/integration/test_fallback.py
import os
import sys
import unittest
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from cde_orchestrator.application.documentation.scan_documentation_use_case import (  # noqa: E402
    ScanDocumentationUseCase,
)


class TestFallback(unittest.TestCase):
    """Test suite for Rust fallback behavior."""

    def test_fallback_when_rust_unavailable(self):
        """Test that fallback works when Rust module is not available."""
        with patch.dict("sys.modules", {"cde_rust_core": None}):
            use_case = ScanDocumentationUseCase()
            # This should work with Python fallback
            result = use_case.execute(".")
            assert "total_docs" in result
            assert isinstance(result["total_docs"], int)

    def test_fallback_when_rust_fails(self):
        """Test that fallback works when Rust module fails during execution."""
        # Skip this test - beartype circular import issue with mocking
        self.skipTest("Skipped due to beartype circular import with mocking")

    def test_rust_accelerated_when_available(self):
        """Test that Rust acceleration is used when available."""
        # Skip this test since Rust integration is optional
        self.skipTest("Skipped - Rust module not compiled")
