#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enforce documentation governance rules during git pre-commit.

This script validates that .md files are only created in designated directories:
- specs/features/ - User-facing feature specs
- specs/design/ - Technical architecture & decisions
- specs/tasks/ - Roadmap & project tracking
- specs/governance/ - Process & rules
- docs/ - User-facing documentation
- .cde/ - Workflows, prompts, recipes
- memory/ - Constitution & principles

Allowed root-level .md files:
- README.md
- CHANGELOG.md
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- LICENSE

See: specs/governance/DOCUMENTATION_GOVERNANCE.md
"""

import sys
import os
from pathlib import Path

# Ensure UTF-8 encoding on Windows
if sys.stdout.encoding.lower() not in ['utf-8', 'utf8']:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# Configuration
ALLOWED_ROOT_FILES = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "LICENSE",
}

ALLOWED_DIRECTORIES = {
    "specs/features",
    "specs/design",
    "specs/tasks",
    "specs/governance",
    "specs/templates",  # Templates for agent-generated docs
    "docs",
    ".cde",
    ".github",  # GitHub configuration (copilot-instructions.md)
    "memory",
    "agent-docs",  # Agent-generated documentation (NEW)
}

AGENT_DOCS_SUBDIRS = {
    "agent-docs/sessions",
    "agent-docs/execution",
    "agent-docs/feedback",
    "agent-docs/research",
    "agent-docs/research/archived",  # Auto-archived research
}

# Special exception: agent-docs/README.md is allowed at root level
AGENT_DOCS_README = "agent-docs/README.md"


def validate_agent_docs_structure(file_path: str) -> tuple[bool, str]:
    """
    Validate agent-docs subdirectory structure and naming.

    Args:
        file_path: Path to file in agent-docs/

    Returns:
        (is_valid, reason) tuple
    """
    path = Path(file_path)
    path_str = str(path).replace("\\", "/")

    # Special case: agent-docs/README.md is allowed
    if path_str == AGENT_DOCS_README:
        return True, "Root README for agent-docs directory"

    # Must be in one of the defined subdirectories
    in_valid_subdir = any(path_str.startswith(subdir + "/") for subdir in AGENT_DOCS_SUBDIRS)
    if not in_valid_subdir:
        return False, (
            f"Agent document '{file_path}' must be in a valid subdirectory.\n"
            f"  Valid subdirectories:\n"
            f"    - agent-docs/sessions/ (session summaries)\n"
            f"    - agent-docs/execution/ (execution reports)\n"
            f"    - agent-docs/feedback/ (analysis and recommendations)\n"
            f"    - agent-docs/research/ (web research summaries)\n"
            f"  See: specs/governance/DOCUMENTATION_GOVERNANCE.md Section 5"
        )

    # Validate naming pattern (lowercase with hyphens, ISO date)
    filename = path.name
    if filename.isupper() or " " in filename:
        return False, (
            f"Agent document '{filename}' violates naming pattern.\n"
            f"  Required: lowercase-with-hyphens-YYYY-MM-DD.md\n"
            f"  Examples:\n"
            f"    - session-onboarding-review-2025-01-15.md\n"
            f"    - execution-onboarding-2025-01.md\n"
            f"    - feedback-governance-improvements-2025-01.md"
        )

    return True, f"Agent document in valid structure: {path_str}"


def is_governance_compliant(file_path: str) -> tuple[bool, str]:
    """
    Check if a markdown file complies with governance rules.

    Args:
        file_path: Path to the file to check

    Returns:
        (is_compliant, reason) tuple
    """
    path = Path(file_path)

    # Only check markdown files
    if path.suffix != ".md":
        return True, "Not a markdown file"

    # Check if in root
    if path.parent == Path("."):
        if path.name in ALLOWED_ROOT_FILES:
            return True, f"Root file '{path.name}' is in allowed list"
        return False, (
            f"Root markdown file '{path.name}' violates governance.\n"
            f"  Allowed root files: {', '.join(sorted(ALLOWED_ROOT_FILES))}\n"
            f"  Place this file in one of: {', '.join(sorted(ALLOWED_DIRECTORIES))}\n"
            f"  See: specs/governance/DOCUMENTATION_GOVERNANCE.md"
        )

    # Check if in allowed directory
    path_str = str(path).replace("\\", "/")  # Normalize path separators
    for allowed_dir in ALLOWED_DIRECTORIES:
        if path_str.startswith(allowed_dir + "/") or path_str == allowed_dir:
            # Special validation for agent-docs structure
            if allowed_dir == "agent-docs":
                return validate_agent_docs_structure(file_path)
            return True, f"File in compliant directory: {allowed_dir}/"

    # File is in non-compliant location
    return False, (
        f"Markdown file '{file_path}' is in non-compliant location.\n"
        f"  Allowed directories:\n"
        f"    - specs/features/ (User-facing feature specs)\n"
        f"    - specs/design/ (Technical architecture & decisions)\n"
        f"    - specs/tasks/ (Roadmap & project tracking)\n"
        f"    - specs/governance/ (Process & rules)\n"
        f"    - specs/templates/ (Templates for agents)\n"
        f"    - docs/ (User-facing documentation)\n"
        f"    - .cde/ (Workflows, prompts, recipes)\n"
        f"    - memory/ (Constitution & principles)\n"
        f"    - agent-docs/ (Agent-generated docs - NEW)\n"
        f"  See: specs/governance/DOCUMENTATION_GOVERNANCE.md"
    )


def main():
    """
    Entry point for pre-commit hook.

    Reads file paths from stdin (pre-commit format).
    Exit code: 0 = all files pass, 1 = governance violation found
    """
    violations = []

    # Read files from stdin (one per line)
    for line in sys.stdin:
        file_path = line.strip()
        if not file_path:
            continue

        is_compliant, reason = is_governance_compliant(file_path)

        if not is_compliant:
            violations.append((file_path, reason))
        else:
            # Verbose output (can be disabled with pre-commit config)
            print(f"[OK] {file_path}: {reason}")

    # Report violations
    if violations:
        print("\n[ERROR] DOCUMENTATION GOVERNANCE VIOLATIONS FOUND:\n")
        for file_path, reason in violations:
            print(f"[FAIL] {file_path}")
            print(f"  {reason}\n")
        return 1

    print("\n[OK] All files pass documentation governance checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
