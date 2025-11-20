#!/usr/bin/env python3
"""Test the directory exclusion logic between Rust and Python."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cde_orchestrator.application.onboarding.project_analysis_use_case import (
    ProjectAnalysisUseCase,
)


def test_directory_exclusion():
    """Test if directory exclusion works correctly."""

    use_case = ProjectAnalysisUseCase()
    project_path = Path(".")

    print("🔍 TESTING DIRECTORY EXCLUSION\n")
    print(f"Excluded directories: {sorted(use_case.EXCLUDED_DIRS)}\n")

    # Test paths
    test_paths = [
        ".venv/Lib/site-packages/numpy/__init__.py",
        "src/cde_orchestrator/application/main.py",
        "node_modules/jquery/dist/jquery.js",
        "dist/build/output.js",
        "htmlcov/status.json",
        "tests/unit/test_main.py",
    ]

    print("Testing path filtering:\n")
    for test_path in test_paths:
        path = Path(test_path)

        # Python logic
        excluded_by_dir = any(
            excluded_dir in path.parts for excluded_dir in use_case.EXCLUDED_DIRS
        )

        print(f"  Path: {test_path}")
        print(f"    Parts: {path.parts}")
        print(f"    Python exclusion: {excluded_by_dir}")
        print()


if __name__ == "__main__":
    test_directory_exclusion()
