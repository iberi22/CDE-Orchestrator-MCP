#!/usr/bin/env python3
"""
Test Structure Validation Script for CDE Orchestrator MCP.

Validates that all test files are properly organized in the tests/ directory
following the project's testing standards.

Usage:
    python scripts/validation/validate-test-structure.py
    python scripts/validation/validate-test-structure.py --staged
"""

import argparse
import sys
from pathlib import Path
from typing import List


class TestStructureValidator:
    """Validates test file organization."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.tests_dir = repo_root / "tests"
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> bool:
        """
        Validate test structure.

        Returns:
            True if validation passes, False otherwise
        """
        self.errors = []
        self.warnings = []

        # Check 1: No test files in root
        self._check_root_test_files()

        # Check 2: All test files in tests/ directory
        self._check_test_directory_structure()

        # Check 3: Test file naming convention
        self._check_test_naming()

        # Check 4: __init__.py presence
        self._check_init_files()

        return len(self.errors) == 0

    def _check_root_test_files(self) -> None:
        """Check that no test files exist in root directory."""
        root_test_files = []

        for file in self.repo_root.glob("test_*.py"):
            if file.is_file():
                root_test_files.append(file.name)

        if root_test_files:
            self.errors.append(
                f"Test files found in root directory (should be in tests/): "
                f"{', '.join(root_test_files)}"
            )

    def _check_test_directory_structure(self) -> None:
        """Validate tests/ directory structure."""
        if not self.tests_dir.exists():
            self.errors.append("tests/ directory does not exist")
            return

        # Expected structure
        expected_subdirs = ["unit", "integration"]

        for subdir in expected_subdirs:
            subdir_path = self.tests_dir / subdir
            if not subdir_path.exists():
                self.warnings.append(
                    f"tests/{subdir}/ directory does not exist (recommended)"
                )

    def _check_test_naming(self) -> None:
        """Check that test files follow naming convention."""
        if not self.tests_dir.exists():
            return

        for test_file in self.tests_dir.rglob("*.py"):
            if test_file.name == "__init__.py":
                continue

            # Skip __pycache__
            if "__pycache__" in str(test_file):
                continue

            if not test_file.name.startswith("test_"):
                self.warnings.append(
                    f"Test file does not follow naming convention (test_*.py): {test_file.relative_to(self.repo_root)}"
                )

    def _check_init_files(self) -> None:
        """Check that __init__.py files exist where needed."""
        if not self.tests_dir.exists():
            return

        # tests/ should have __init__.py
        if not (self.tests_dir / "__init__.py").exists():
            self.warnings.append("tests/__init__.py does not exist (recommended)")

        # Each subdirectory should have __init__.py
        for subdir in self.tests_dir.iterdir():
            if subdir.is_dir() and subdir.name != "__pycache__":
                init_file = subdir / "__init__.py"
                if not init_file.exists():
                    self.warnings.append(
                        f"tests/{subdir.name}/__init__.py does not exist (recommended)"
                    )


def find_misplaced_tests(repo_root: Path) -> List[Path]:
    """Find test files outside of tests/ directory."""
    misplaced = []

    for test_file in repo_root.rglob("test_*.py"):
        # Skip if in tests/ directory
        if "tests" in test_file.parts:
            continue

        # Skip hidden directories
        if any(part.startswith(".") for part in test_file.parts):
            continue

        misplaced.append(test_file)

    return misplaced


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate test structure")
    parser.add_argument(
        "--fix", action="store_true", help="Auto-fix issues (move files)"
    )
    parser.add_argument("--staged", action="store_true", help="Check staged files only")

    args = parser.parse_args()

    # Determine repo root
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent.parent

    validator = TestStructureValidator(repo_root)

    # Validate
    print("Validating test structure...")
    is_valid = validator.validate()

    # Print results
    if validator.errors:
        print("\n❌ ERRORS:")
        for error in validator.errors:
            print(f"   {error}")

    if validator.warnings:
        print("\n⚠️  WARNINGS:")
        for warning in validator.warnings:
            print(f"   {warning}")

    # Find misplaced tests
    misplaced = find_misplaced_tests(repo_root)
    if misplaced:
        print("\n🔍 MISPLACED TEST FILES:")
        for test_file in misplaced:
            print(f"   {test_file.relative_to(repo_root)}")

        if args.fix:
            print("\n🔧 AUTO-FIXING...")
            tests_dir = repo_root / "tests" / "integration"
            tests_dir.mkdir(parents=True, exist_ok=True)

            for test_file in misplaced:
                dest = tests_dir / test_file.name
                print(f"   Moving {test_file.name} -> tests/integration/")
                test_file.rename(dest)

            print("✅ Files moved successfully")

    # Summary
    print("\n" + "=" * 80)
    if is_valid and not misplaced:
        print("✅ TEST STRUCTURE VALIDATION PASSED")
        return 0
    else:
        print("❌ TEST STRUCTURE VALIDATION FAILED")
        if args.fix:
            print("\nRe-run validation to check if all issues are fixed.")
        else:
            print("\nRun with --fix to automatically move misplaced test files.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
