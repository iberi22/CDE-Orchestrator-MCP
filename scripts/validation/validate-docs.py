#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Documentation Governance Validator

Validates that all markdown files comply with DOCUMENTATION_GOVERNANCE.md rules:
- Correct file locations (specs/, agent-docs/, docs/, or root exceptions)
- YAML frontmatter with required fields
- Naming conventions (lowercase, hyphens, ISO dates)
- Agent-docs subdirectory structure
- Spec Kit Completeness (spec.md, plan.md, tasks.md in feature dirs)

Usage:
    python scripts/validation/validate-docs.py --all              # Audit all docs
    python scripts/validation/validate-docs.py file1.md file2.md # Validate specific files
    python scripts/validation/validate-docs.py --staged            # Validate staged files only (pre-commit)
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


# ANSI colors for output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


# Governance rules
ROOT_EXCEPTIONS = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "LICENSE",
    "AGENTS.md",
    ".github/copilot-instructions.md",
}

DISALLOWED_ROOT_PATTERNS = [
    r"^PHASE\d+C_.*\.md$",
    r"^SESSION.*\.md$",
    r"^SUMMARY.*\.md$",
    r"^REPORT.*\.md$",
    r"^REVIEW.*\.md$",
    r"^NOTES.*\.md$",
    r"^ANALYSIS.*\.md$",
    r"^EXECUTION.*\.md$",
    r"^FEEDBACK.*\.md$",
    r"^RESUMEN.*\.md$",
    r"^SPRINT.*\.md$",
    r"^MEETING.*\.md$",
    r"^JULIUS.*\.md$",  # Block any JULIUS_*.md in root
    r"^WEEK-.*\.md$",  # Block WEEK-*.md in root (should be in agent-docs/execution/)
    r"^TEST.*\.md$",  # Block TEST_*.md in root
    r"^GEMINI.*\.md$", # Block GEMINI files
]

VALID_TYPES = {
    "feature",
    "design",
    "task",
    "guide",
    "governance",
    "session",
    "execution",
    "feedback",
    "research",
    "migration",
}

VALID_STATUSES = {"draft", "active", "deprecated", "archived", "completed"}

# Line limit for documentation files (excluding root exceptions)
MAX_LINES = 1500
MAX_LINES_EXCEPTIONS = ROOT_EXCEPTIONS | {
    "specs/design/archive/architecture.md.deprecated"
}

ALLOWED_DIRECTORIES = {
    "specs": "feature",  # General specs bucket, refine logic handles subdirs
    "agent-docs/execution": "execution",
    "agent-docs/sessions": "session",
    "agent-docs/feedback": "feedback",
    "agent-docs/research": "research",
    "docs": "guide",
    ".cde": None,  # No type requirement
    "memory": None,  # No type requirement
}

REQUIRED_FRONTMATTER_FIELDS = {
    "title",
    "description",
    "type",
    "status",
    "created",
    "updated",
    "author",
}

# Paths to skip validation
SKIP_PATHS = {
    ".git",
    ".github",
    ".cde/issues",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "htmlcov",
    ".pre-commit-hooks.yaml",
}

NON_FEATURE_DIRS = {
    "templates",
    "design",
    "governance",
    "legacy-migration",
    "features", # Legacy
    "tasks",    # Legacy
    "plans",    # Legacy
    "api",
    "cde-dogfooding-feedback",
    "spec-kit-synchronization", # Seems like a feature but maybe infrastructure? Treating as feature for now unless excluded.
}

# Actually spec-kit-synchronization IS a feature. Removing from exclusion if possible, or keeping if it's special.
# I'll keep the list minimal.
NON_FEATURE_DIRS = {
    "templates",
    "design",
    "governance",
    "legacy-migration",
    "features",
    "tasks",
    "plans",
    "api",
}


class ValidationError:
    def __init__(
        self, file_path: str, error_type: str, message: str, severity: str = "error"
    ):
        self.file_path = file_path
        self.error_type = error_type
        self.message = message
        self.severity = severity  # "error", "warning", "info"

    def __str__(self) -> str:
        color = Colors.RED if self.severity == "error" else Colors.YELLOW
        emoji_map = {"error": "[ERR]", "warning": "[WRN]", "info": "[INF]"}
        emoji = emoji_map.get(self.severity, "[?]")
        return f"{color}{emoji}{Colors.ENDC} {self.file_path}: {self.message}"


def get_staged_files() -> List[str]:
    """Get list of staged files from git."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [f for f in result.stdout.strip().split("\n") if f.endswith(".md")]
    except subprocess.CalledProcessError:
        return []


def validate_location(file_path: str) -> Optional[ValidationError]:
    """Validate that file is in allowed location."""
    path = Path(file_path)
    # Normalize to forward slashes for consistent comparison
    norm_path = file_path.replace("\\", "/")

    # Check if in root
    if path.parent == Path("."):
        filename = path.name

        # Check exceptions
        if filename in ROOT_EXCEPTIONS:
            return None  # OK

        # Strict fail for any other root MD file
        return ValidationError(
            file_path,
            "LOCATION",
            f"[ERR] '.md' files NOT allowed in root (except {', '.join(sorted(ROOT_EXCEPTIONS))}). Move to specs/legacy-migration/ or correct folder.",
            "error",
        )

    # Check if in valid directory (normalize backslashes to forward slashes)
    for allowed_dir in ALLOWED_DIRECTORIES.keys():
        if norm_path.startswith(allowed_dir):
            return None  # OK

    return ValidationError(
        file_path,
        "LOCATION",
        "[ERR] File in unknown directory. Must be in: specs/, agent-docs/, docs/, .cde/, memory/, or root exceptions",
        "error",
    )


def validate_naming(file_path: str) -> Optional[ValidationError]:
    """Validate filename follows conventions."""
    filename = Path(file_path).name

    # Skip if in .github/ (special case)
    if ".github" in file_path:
        return None

    # Allow README.md, SKILL.md, SKILL_TEMPLATE.md in any case (Standard conventions)
    if filename.upper() in ["README.MD", "SKILL.MD", "SKILL_TEMPLATE.MD"]:
        return None

    # Check for uppercase letters (except in .md extension)
    name_part = filename.replace(".md", "")
    if name_part != name_part.lower():
        return ValidationError(
            file_path,
            "NAMING",
            f"[ERR] Filename must be lowercase. Use hyphens for spaces: '{filename.lower()}'",
            "warning",
        )

    # Check for spaces
    if " " in filename:
        return ValidationError(
            file_path,
            "NAMING",
            "[ERR] Filename must not contain spaces. Use hyphens instead.",
            "warning",
        )

    # Check for valid characters
    if not re.match(r"^[a-z0-9\-_.]+\.md$", filename):
        return ValidationError(
            file_path,
            "NAMING",
            "[ERR] Filename contains invalid characters. Use only: a-z, 0-9, hyphens, underscores, dots",
            "warning",
        )

    return None


def validate_frontmatter(file_path: str) -> List[ValidationError]:
    """Validate YAML frontmatter in markdown file."""
    errors: List[ValidationError] = []

    # Skip .github/ (special case - no frontmatter required)
    if ".github" in file_path:
        return errors

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        errors.append(
            ValidationError(file_path, "READ", f"[ERR] Cannot read file: {e}", "error")
        )
        return errors

    # Check for frontmatter
    if not content.startswith("---"):
        errors.append(
            ValidationError(
                file_path,
                "FRONTMATTER",
                "[ERR] File must start with YAML frontmatter block (---).",
                "error",
            )
        )
        return errors

    # Extract frontmatter
    try:
        end_marker = content.find("---", 3)
        if end_marker == -1:
            errors.append(
                ValidationError(
                    file_path,
                    "FRONTMATTER",
                    "[ERR] Invalid frontmatter: closing --- not found",
                    "error",
                )
            )
            return errors

        frontmatter_text = content[3:end_marker].strip()
        frontmatter = yaml.safe_load(frontmatter_text)

        if not isinstance(frontmatter, dict):
            errors.append(
                ValidationError(
                    file_path,
                    "FRONTMATTER",
                    "[ERR] Frontmatter must be valid YAML dictionary",
                    "error",
                )
            )
            return errors
    except yaml.YAMLError as e:
        errors.append(
            ValidationError(
                file_path,
                "FRONTMATTER",
                f"[ERR] Invalid YAML in frontmatter: {str(e)[:60]}",
                "error",
            )
        )
        return errors

    # Validate required fields
    missing_fields = REQUIRED_FRONTMATTER_FIELDS - set(frontmatter.keys())
    if missing_fields:
        errors.append(
            ValidationError(
                file_path,
                "FRONTMATTER",
                f"[ERR] Missing required frontmatter fields: {', '.join(sorted(missing_fields))}",
                "error",
            )
        )

    # Validate type field
    doc_type = frontmatter.get("type", "").lower()
    if doc_type and doc_type not in VALID_TYPES:
        errors.append(
            ValidationError(
                file_path,
                "FRONTMATTER",
                f"[ERR] Invalid type '{doc_type}'. Must be one of: {', '.join(sorted(VALID_TYPES))}",
                "error",
            )
        )

    # Validate status field
    status = frontmatter.get("status", "").lower()
    if status and status not in VALID_STATUSES:
        errors.append(
            ValidationError(
                file_path,
                "FRONTMATTER",
                f"[ERR] Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
                "error",
            )
        )

    # Validate date fields
    for date_field in ["created", "updated"]:
        date_str = frontmatter.get(date_field)
        if date_str:
            try:
                datetime.strptime(str(date_str), "%Y-%m-%d")
            except ValueError:
                errors.append(
                    ValidationError(
                        file_path,
                        "FRONTMATTER",
                        f"[ERR] Invalid {date_field} date format '{date_str}'. Use YYYY-MM-DD",
                        "error",
                    )
                )

    return errors


def validate_agent_docs_structure(file_path: str) -> Optional[ValidationError]:
    """Validate agent-docs/ subdirectory structure."""
    # Normalize to forward slashes for consistent comparison
    norm_path = file_path.replace("\\", "/")

    if not norm_path.startswith("agent-docs/"):
        return None

    parts = Path(file_path).parts
    if len(parts) < 2:
        return ValidationError(
            file_path,
            "STRUCTURE",
            "[ERR] agent-docs files must be in subdirectories (execution/, sessions/, feedback/, research/)",
            "error",
        )

    subdir = parts[1]
    if subdir not in {"execution", "sessions", "feedback", "research", "prompts"}:
        return ValidationError(
            file_path,
            "STRUCTURE",
            f"[ERR] agent-docs subdirectory '{subdir}' not recognized. Use: execution/, sessions/, feedback/, research/",
            "error",
        )

    # Validate filename pattern for agent-docs
    filename = Path(file_path).name
    if subdir in {"execution", "sessions", "feedback", "research"}:
        # Should have date in filename
        if not re.search(r"\d{4}-\d{2}(-\d{2})?", filename):
            return ValidationError(
                file_path,
                "STRUCTURE",
                f"[WRN] agent-docs/{subdir}/ files should include date: YYYY-MM or YYYY-MM-DD",
                "warning",
            )

    return None


def validate_line_count(file_path: str) -> Optional[ValidationError]:
    """Validate that file does not exceed maximum line count (800 lines)."""
    path = Path(file_path)

    # Check if file is in exceptions
    if path.name in MAX_LINES_EXCEPTIONS:
        return None

    if "archive" in path.parts:
        return None

    # Skip legacy migration files
    if "legacy-migration" in path.parts:
        return None

    try:
        line_count = len(path.read_text(encoding="utf-8").splitlines())

        if line_count > MAX_LINES:
            return ValidationError(
                file_path=file_path,
                error_type="line_count",
                message=(
                    f"Document exceeds maximum line count: {line_count} lines (max: {MAX_LINES}). "
                    f"Consider splitting into multiple modular documents. "
                    f"Over by: {line_count - MAX_LINES} lines"
                ),
                severity="error",
            )
    except Exception as e:
        return ValidationError(
            file_path=file_path,
            error_type="file_read",
            message=f"Could not read file to count lines: {e}",
            severity="warning",
        )

    return None

def validate_spec_kit_completeness(root_dir: str = ".") -> List[ValidationError]:
    """Ensure all feature directories have spec.md, plan.md, tasks.md."""
    errors = []
    specs_dir = Path(root_dir) / "specs"
    if not specs_dir.exists():
        return errors

    for feature_dir in specs_dir.iterdir():
        if feature_dir.is_dir() and feature_dir.name not in NON_FEATURE_DIRS:
            # Check for required files
            required = ["spec.md", "plan.md", "tasks.md"]
            missing = [f for f in required if not (feature_dir / f).exists()]
            if missing:
                 errors.append(ValidationError(str(feature_dir), "SPECKIT", f"[ERR] Feature directory missing Spec Kit files: {', '.join(missing)}", "error"))
    return errors

def validate_file(file_path: str) -> List[ValidationError]:
    """Validate a single markdown file."""
    errors = []

    # Validate location
    loc_error = validate_location(file_path)
    if loc_error:
        errors.append(loc_error)

    # Validate naming
    naming_error = validate_naming(file_path)
    if naming_error:
        errors.append(naming_error)

    # Validate line count
    line_count_error = validate_line_count(file_path)
    if line_count_error:
        errors.append(line_count_error)

    # Validate agent-docs structure
    agent_error = validate_agent_docs_structure(file_path)
    if agent_error:
        errors.append(agent_error)

    # Validate frontmatter (only if other location checks pass or warning)
    if not loc_error or loc_error.severity == "warning":
        frontmatter_errors = validate_frontmatter(file_path)
        errors.extend(frontmatter_errors)

    return errors


def find_all_md_files(root_dir: str = ".") -> List[str]:
    """Find all markdown files in the repository."""
    md_files = []
    root = Path(root_dir)

    for md_file in root.rglob("*.md"):
        # Skip paths in SKIP_PATHS
        if any(part in SKIP_PATHS for part in md_file.parts):
            continue

        md_files.append(str(md_file))

    return sorted(md_files)


def print_report(errors: List[ValidationError], verbose: bool = False) -> bool:
    """Print professional validation report."""
    if not errors:
        print(
            f"\n{Colors.GREEN}[PASS] All documentation is compliant with DOCUMENTATION_GOVERNANCE.md{Colors.ENDC}\n"
        )
        return False

    # Group by severity
    by_severity: Dict[str, List[ValidationError]] = {
        "error": [],
        "warning": [],
        "info": [],
    }
    for error in errors:
        by_severity[error.severity].append(error)

    # Print header
    total = len(errors)
    print(
        f"\n{Colors.RED}{Colors.BOLD}[AUDIT] DOCUMENTATION GOVERNANCE AUDIT{Colors.ENDC}\n"
    )
    print(f"{Colors.RED}[FAIL] Found {total} violation(s){Colors.ENDC}\n")

    # Print errors
    if by_severity["error"]:
        print(
            f"{Colors.RED}{Colors.BOLD}[ERROR] ({len(by_severity['error'])}) - MUST FIX:{Colors.ENDC}"
        )
        for error in by_severity["error"]:
            print(f"  {error}")
        print()

    # Print warnings
    if by_severity["warning"]:
        print(
            f"{Colors.YELLOW}{Colors.BOLD}[WARN] ({len(by_severity['warning'])}) - Should fix:{Colors.ENDC}"
        )
        for error in by_severity["warning"]:
            print(f"  {error}")
        print()

    # Print summary
    error_count = len(by_severity["error"])
    warning_count = len(by_severity["warning"])

    print(f"{Colors.BOLD}Summary:{Colors.ENDC}")
    print(f"  Errors:   {error_count} (blocks commits)")
    print(f"  Warnings: {warning_count} (should be fixed)")
    print()

    print(
        f"{Colors.BLUE}Reference: specs/governance/DOCUMENTATION_GOVERNANCE.md{Colors.ENDC}"
    )
    print(
        f"{Colors.BLUE}Rules: .github/copilot-instructions.md (AI Agent Governance Checklist){Colors.ENDC}\n"
    )

    return error_count > 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate documentation governance compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--all", action="store_true", help="Validate all markdown files"
    )
    parser.add_argument(
        "--staged", action="store_true", help="Validate only staged files (git)"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("files", nargs="*", help="Specific files to validate")

    args = parser.parse_args()

    # Determine which files to validate
    if args.all:
        files_to_check = find_all_md_files()
    elif args.staged:
        files_to_check = get_staged_files()
    elif args.files:
        files_to_check = args.files
    else:
        # Default to checking all if no args provided (useful for CI)
        files_to_check = find_all_md_files()

    if not files_to_check:
        print("ℹ️  No files to validate.")
        return 0

    # Validate files
    all_errors = []
    for file_path in files_to_check:
        errors = validate_file(file_path)
        all_errors.extend(errors)

    # Check Spec Kit completeness (only when running --all or default)
    if args.all or (not args.files and not args.staged):
         spec_kit_errors = validate_spec_kit_completeness()
         all_errors.extend(spec_kit_errors)

    # Print report
    has_errors = print_report(all_errors, args.verbose)

    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
