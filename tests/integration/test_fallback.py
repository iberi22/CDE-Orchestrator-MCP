#!/usr/bin/env python3
"""
Test fallback mechanism for Rust core unavailability.

Tests that the system gracefully falls back to Python implementation
when the Rust module is not available or fails.
"""

import sys
import os
import json
import unittest.mock as mock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_fallback_when_rust_unavailable():
    """Test that fallback works when Rust module is not available."""
    from cde_orchestrator.application.documentation.scan_documentation_use_case import ScanDocumentationUseCase

    # Mock import to simulate Rust module not available
    with mock.patch.dict('sys.modules', {'cde_rust_core': None}):
        with mock.patch('builtins.__import__', side_effect=ImportError("No module named 'cde_rust_core'")):
            use_case = ScanDocumentationUseCase()

            # This should work with Python fallback
            project_path = os.path.join(os.path.dirname(__file__), '..', '..')
            result = use_case.execute(project_path)

            # Verify result structure
            assert "total_docs" in result
            assert "scanned_at" in result
            assert "missing_metadata" in result
            assert "recommendations" in result
            assert isinstance(result["total_docs"], int)

            print("✅ Fallback to Python implementation works")
            return True

def test_fallback_when_rust_fails():
    """Test that fallback works when Rust module fails during execution."""
    from cde_orchestrator.application.documentation.scan_documentation_use_case import ScanDocumentationUseCase

    # Mock the Rust function to fail
    mock_rust_core = mock.MagicMock()
    mock_rust_core.documentation.scan_documentation_fast.side_effect = Exception("Rust scan failed")

    with mock.patch.dict('sys.modules', {'cde_rust_core': mock_rust_core}):
        use_case = ScanDocumentationUseCase()

        # This should work with Python fallback
        project_path = os.path.join(os.path.dirname(__file__), '..', '..')
        result = use_case.execute(project_path)

        # Verify result structure
        assert "total_docs" in result
        assert "scanned_at" in result
        assert "missing_metadata" in result
        assert "recommendations" in result

        print("✅ Fallback after Rust failure works")
        return True

def test_rust_accelerated_when_available():
    """Test that Rust acceleration is used when available."""
    from cde_orchestrator.application.documentation.scan_documentation_use_case import ScanDocumentationUseCase

    # Mock successful Rust execution
    mock_result = {
        "total_docs": 10,
        "by_location": {"specs/features": []},
        "missing_metadata": [],
        "orphaned_docs": [],
        "large_files": []
    }

    mock_rust_core = mock.MagicMock()
    mock_rust_core.documentation.scan_documentation_fast.return_value = json.dumps(mock_result)

    with mock.patch.dict('sys.modules', {'cde_rust_core': mock_rust_core}):
        use_case = ScanDocumentationUseCase()

        project_path = os.path.join(os.path.dirname(__file__), '..', '..')
        result = use_case.execute(project_path)

        # Verify Rust was called
        mock_rust_core.documentation.scan_documentation_fast.assert_called_once_with(project_path)

        # Verify result has enhanced fields from Python processing
        assert "scanned_at" in result  # Added by Python
        assert "recommendations" in result  # Added by Python

        print("✅ Rust acceleration works when available")
        return True

def main():
    """Run all fallback tests."""
    print("🧪 Testing Fallback Mechanisms")
    print("=" * 30)

    tests = [
        test_fallback_when_rust_unavailable,
        test_fallback_when_rust_fails,
        test_rust_accelerated_when_available,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        print(f"\n🔍 Running {test.__name__}...")
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")

    print("\n" + "=" * 30)
    print(f"📊 Fallback Tests: {passed}/{total} passed")

    if passed == total:
        print("🎉 All fallback mechanisms working correctly!")
        return 0
    else:
        print("⚠️  Some fallback tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())