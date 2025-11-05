#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constitution Validator

Validates the project's constitution as defined in memory/constitution.md.
- Ensures the constitution file exists.
- (Future) Parses the constitution to extract key principles for validation.

Usage:
    python scripts/validation/validate-constitution.py
"""

import sys
from pathlib import Path

# ANSI colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

CONSTITUTION_PATH = Path("memory/constitution.md")

def validate_constitution_exists() -> bool:
    """Check if the constitution file exists."""
    if not CONSTITUTION_PATH.is_file():
        print(f"{Colors.RED}{Colors.BOLD}[FAIL] Constitution not found!{Colors.ENDC}")
        print(f"  - Expected at: {CONSTITUTION_PATH}")
        print("  - The constitution is essential for guiding AI agent behavior.")
        print("  - Please create this file and define the project's core principles.")
        return False

    print(f"{Colors.GREEN}[PASS] Project constitution found at {CONSTITUTION_PATH}{Colors.ENDC}")
    return True

def main() -> int:
    """Main validation function."""
    print(f"\n{Colors.BOLD}Validating Project Constitution...{Colors.ENDC}")

    exists = validate_constitution_exists()

    if not exists:
        return 1

    # Future enhancements:
    # - Parse the constitution file for key principles.
    # - Validate other documents against these principles.

    print(f"\n{Colors.GREEN}{Colors.BOLD}Constitution validation successful.{Colors.ENDC}\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
