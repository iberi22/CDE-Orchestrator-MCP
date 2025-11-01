#!/usr/bin/env python3
"""
Metadata Validation Script for CDE Orchestrator MCP.

Validates YAML frontmatter in markdown files according to the standard pattern
defined in specs/templates/document-metadata.md.

Usage:
    python scripts/validation/validate-metadata.py --all
    python scripts/validation/validate-metadata.py --path specs/features/my-doc.md
    python scripts/validation/validate-metadata.py --staged  # For pre-commit
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Install with: pip install pyyaml")
    sys.exit(1)

# Valid enum values
VALID_TYPES = {
    "feature",
    "design",
    "task",
    "governance",
    "guide",
    "session",
    "execution",
    "feedback",
    "research",
}

VALID_STATUSES = {"draft", "active", "deprecated", "archived"}

# Type to directory mapping
TYPE_TO_DIR = {
    "feature": "specs/features",
    "design": "specs/design",
    "task": "specs/tasks",
    "governance": "specs/governance",
    "guide": "docs",
    "session": "agent-docs/sessions",
    "execution": "agent-docs/execution",
    "feedback": "agent-docs/feedback",
    "research": "agent-docs/research",
}

# Required fields
REQUIRED_FIELDS = {"title", "description", "type", "status", "created", "updated", "author"}


class MetadataValidator:
    """Validates YAML frontmatter in markdown files."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_file(self, file_path: Path) -> bool:
        """
        Validate a single markdown file.

        Returns:
            True if validation passes, False otherwise
        """
        self.errors = []
        self.warnings = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"Failed to read file: {e}")
            return False

        # Extract frontmatter
        metadata, has_frontmatter = self._extract_frontmatter(content)

        if not has_frontmatter:
            self.errors.append("Missing YAML frontmatter (must start with ---)")
            return False

        if metadata is None:
            self.errors.append("Invalid YAML frontmatter syntax")
            return False

        # Validate required fields
        self._validate_required_fields(metadata)

        # Validate field types and values
        if "type" in metadata:
            self._validate_type(metadata["type"])

        if "status" in metadata:
            self._validate_status(metadata["status"])

        if "created" in metadata:
            self._validate_date(metadata["created"], "created")

        if "updated" in metadata:
            self._validate_date(metadata["updated"], "updated")

        if "description" in metadata:
            self._validate_description(metadata["description"])

        if "llm_summary" in metadata:
            self._validate_llm_summary(metadata["llm_summary"])

        # Validate location matches type
        if "type" in metadata:
            self._validate_location(file_path, metadata["type"])

        # Validate related docs exist
        if "related_docs" in metadata:
            self._validate_related_docs(metadata["related_docs"])

        return len(self.errors) == 0

    def _extract_frontmatter(self, content: str) -> Tuple[Optional[Dict], bool]:
        """
        Extract YAML frontmatter from markdown content.

        Returns:
            (metadata dict, has_frontmatter bool)
        """
        if not content.startswith("---"):
            return None, False

        # Find closing ---
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if not match:
            return None, True  # Has start marker but invalid

        yaml_content = match.group(1)

        try:
            metadata = yaml.safe_load(yaml_content)
            return metadata, True
        except yaml.YAMLError:
            return None, True

    def _validate_required_fields(self, metadata: Dict) -> None:
        """Check all required fields are present."""
        missing = REQUIRED_FIELDS - set(metadata.keys())
        if missing:
            self.errors.append(f"Missing required fields: {', '.join(sorted(missing))}")

    def _validate_type(self, doc_type: str) -> None:
        """Validate document type."""
        if doc_type not in VALID_TYPES:
            self.errors.append(
                f"Invalid type '{doc_type}'. Must be one of: {', '.join(sorted(VALID_TYPES))}"
            )

    def _validate_status(self, status: str) -> None:
        """Validate status value."""
        if status not in VALID_STATUSES:
            self.errors.append(
                f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}"
            )

    def _validate_date(self, date_str: str, field_name: str) -> None:
        """Validate ISO 8601 date format."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            self.errors.append(f"Invalid {field_name} date '{date_str}'. Must be YYYY-MM-DD format")

    def _validate_description(self, description: str) -> None:
        """Validate description length."""
        length = len(description)
        if length < 50:
            self.warnings.append(f"Description too short ({length} chars). Minimum 50 recommended.")
        elif length > 150:
            self.warnings.append(f"Description too long ({length} chars). Maximum 150 recommended.")

    def _validate_llm_summary(self, summary: str) -> None:
        """Validate LLM summary length and structure."""
        length = len(summary)
        if length < 100:
            self.warnings.append(f"LLM summary too short ({length} chars). Minimum 100 recommended.")
        elif length > 500:
            self.warnings.append(f"LLM summary too long ({length} chars). Maximum 500 recommended.")

        # Check for 3-sentence pattern (very rough heuristic)
        sentences = summary.count(".") + summary.count("!") + summary.count("?")
        if sentences < 2:
            self.warnings.append(
                "LLM summary should follow 3-sentence pattern (what/covers/when)"
            )

    def _validate_location(self, file_path: Path, doc_type: str) -> None:
        """Validate file is in correct directory for its type."""
        expected_dir = TYPE_TO_DIR.get(doc_type)
        if not expected_dir:
            return

        relative_path = file_path.relative_to(self.repo_root)
        expected_path = Path(expected_dir)

        if not str(relative_path).startswith(str(expected_path)):
            self.errors.append(
                f"Document type '{doc_type}' should be in {expected_dir}/, "
                f"but found in {relative_path.parent}"
            )

    def _validate_related_docs(self, related_docs: List[str]) -> None:
        """Check that related documents exist."""
        for doc_path in related_docs:
            full_path = self.repo_root / doc_path
            if not full_path.exists():
                self.warnings.append(f"Related doc not found: {doc_path}")


def get_markdown_files(repo_root: Path, pattern: str = "**/*.md") -> List[Path]:
    """Get all markdown files matching pattern."""
    return list(repo_root.glob(pattern))


def get_staged_files(repo_root: Path) -> List[Path]:
    """Get staged markdown files from git."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )

        staged_files = result.stdout.strip().split("\n")
        md_files = [repo_root / f for f in staged_files if f.endswith(".md")]
        return md_files
    except subprocess.CalledProcessError:
        print("ERROR: Failed to get staged files from git", file=sys.stderr)
        return []


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate markdown file metadata")
    parser.add_argument("--all", action="store_true", help="Validate all markdown files")
    parser.add_argument("--path", type=str, help="Validate specific file")
    parser.add_argument("--staged", action="store_true", help="Validate staged files (pre-commit)")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    args = parser.parse_args()

    # Determine repo root
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent.parent  # scripts/validation/ -> repo root

    validator = MetadataValidator(repo_root)

    # Determine which files to validate
    files_to_validate: List[Path] = []

    if args.all:
        files_to_validate = get_markdown_files(repo_root)
        print(f"Validating {len(files_to_validate)} markdown files...")
    elif args.path:
        file_path = Path(args.path)
        if not file_path.is_absolute():
            file_path = repo_root / file_path
        files_to_validate = [file_path]
    elif args.staged:
        files_to_validate = get_staged_files(repo_root)
        if not files_to_validate:
            print("No staged markdown files to validate")
            return 0
        print(f"Validating {len(files_to_validate)} staged files...")
    else:
        parser.print_help()
        return 1

    # Validate files
    failed_files = []
    warning_files = []

    for file_path in files_to_validate:
        if not file_path.exists():
            print(f"SKIP: {file_path} (does not exist)")
            continue

        # Skip certain files
        relative_path = file_path.relative_to(repo_root)
        if any(
            part.startswith(".")
            for part in relative_path.parts
            if part not in [".github", ".cde"]
        ):
            continue  # Skip hidden directories

        is_valid = validator.validate_file(file_path)

        if not is_valid:
            failed_files.append(file_path)
            print(f"\n❌ FAIL: {relative_path}")
            for error in validator.errors:
                print(f"   ERROR: {error}")

        if validator.warnings:
            warning_files.append(file_path)
            print(f"\n⚠️  WARN: {relative_path}")
            for warning in validator.warnings:
                print(f"   WARNING: {warning}")

        if is_valid and not validator.warnings:
            print(f"✅ PASS: {relative_path}")

    # Summary
    print("\n" + "=" * 80)
    print(f"Total files validated: {len(files_to_validate)}")
    print(f"Passed: {len(files_to_validate) - len(failed_files)}")
    print(f"Failed: {len(failed_files)}")
    print(f"Warnings: {len(warning_files)}")

    if failed_files:
        print("\nFailed files:")
        for file_path in failed_files:
            print(f"  - {file_path.relative_to(repo_root)}")

    if args.strict and warning_files:
        print("\n⚠️  STRICT MODE: Treating warnings as errors")
        return 1

    return 1 if failed_files else 0


if __name__ == "__main__":
    sys.exit(main())
