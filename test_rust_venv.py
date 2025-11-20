#!/usr/bin/env python3
# pyrefly: disable-error-code = "missing-attribute"
"""Test Rust implementation details."""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import cde_rust_core  # type: ignore


def test_rust_venv_exclusion():
    """Test if Rust correctly excludes .venv directory."""

    project_path = str(Path(".").absolute())

    excluded_dirs = [".venv", "node_modules", "__pycache__"]
    excluded_patterns = ["*.pyc", "*.pyo", "*.pyd"]

    print("🔍 Testing Rust directory exclusion\n")
    print(f"Project path: {project_path}")
    print(f"Excluded dirs: {excluded_dirs}\n")

    # Call Rust
    result_json = cde_rust_core.scan_project_py(
        project_path,
        excluded_dirs,
        excluded_patterns,
    )

    result = json.loads(result_json)

    print(f"Files analyzed: {result['file_count']}")
    print(f"Files excluded: {result['excluded_count']}")
    print(f"Analysis time: {result['analysis_time_ms']}ms\n")

    # Check if .py files from .venv are being counted
    py_count = result["language_stats"].get(".py", 0)
    print(f"Python files (.py) detected: {py_count}")
    print("Expected (without .venv): ~170-180")
    print("With .venv included: ~4900+")

    if py_count > 1000:
        print("\n❌ ERROR: .venv directory is NOT being excluded!")
        print("    Rust is analyzing .venv/Lib/site-packages files")
    elif py_count < 200:
        print("\n✅ OK: .venv directory is properly excluded")
    else:
        print("\n⚠️  WARNING: File count is within expected range")


if __name__ == "__main__":
    test_rust_venv_exclusion()
