# tests/integration/test_fallback.py
import json
import os

# Add src to path for imports
import sys
from unittest.mock import MagicMock, patch


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from cde_orchestrator.application.documentation.scan_documentation_use_case import (
    ScanDocumentationUseCase,
)


def test_fallback_when_rust_unavailable():
    """Test that fallback works when Rust module is not available."""
    with patch.dict("sys.modules", {"cde_rust_core": None}):
        use_case = ScanDocumentationUseCase()
        # This should work with Python fallback
        result = use_case.execute(".")
        assert "total_docs" in result
        assert isinstance(result["total_docs"], int)


def test_fallback_when_rust_fails():
    """Test that fallback works when Rust module fails during execution."""
    mock_rust_core = MagicMock()
    mock_rust_core.scan_documentation_py.side_effect = Exception("Rust scan failed")

    with patch.dict("sys.modules", {"cde_rust_core": mock_rust_core}):
        use_case = ScanDocumentationUseCase()
        result = use_case.execute(".")
        assert "total_docs" in result


def test_rust_accelerated_when_available():
    """Test that Rust acceleration is used when available."""
    mock_rust_core = MagicMock()
    # Rust returns a JSON string of a list of dicts
    mock_rust_core.scan_documentation_py.return_value = json.dumps(
        [{"path": "doc1.md", "content": "content", "word_count": 1}]
    )

    with patch.dict("sys.modules", {"cde_rust_core": mock_rust_core}):
        use_case = ScanDocumentationUseCase()
        result = use_case.execute(".")

        # Verify Rust was called
        mock_rust_core.scan_documentation_py.assert_called_once_with(".")

        # Verify result has enhanced fields from Python processing
        assert "scanned_at" in result
        assert "recommendations" in result
        assert result["total_docs"] == 1
