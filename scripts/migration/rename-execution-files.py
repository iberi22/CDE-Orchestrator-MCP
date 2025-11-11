#!/usr/bin/env python3
"""
Execution Files Renamer

Renames all execution files to new standard format:
EXECUTIONS-{titulo}-{YYYY-MM-DD-HHmm}.md

Usage:
    python scripts/migration/rename-execution-files.py [--dry-run]
"""

import argparse
import re
from datetime import datetime
from pathlib import Path


def extract_date_from_filename(filename: str) -> str:
    """Extract date from filename, return current date if not found."""
    match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    if match:
        return match.group(1)
    return datetime.now().strftime("%Y-%m-%d")


def extract_title_from_filename(filename: str) -> str:
    """Extract descriptive title from filename."""
    # Remove .md extension
    base = filename.replace(".md", "").replace(".md.rej", "")

    # Remove common prefixes
    base = base.replace("execution-", "")
    base = base.replace("audit-complete-cde-mcp-", "audit-complete-")
    base = base.replace("EXECUTIVE_SUMMARY_AUDIT_", "audit-summary-")
    base = base.replace("README-AUDIT-", "audit-readme-")
    base = base.replace("decision-matrix-implementation-", "decision-matrix-")
    base = base.replace("optimization-roadmap-", "optimization-roadmap-")

    # Remove date from base
    base = re.sub(r"-?\d{4}-\d{2}-\d{2}", "", base)

    # Remove trailing hyphens
    base = base.strip("-")

    return base


def generate_new_filename(old_filename: str) -> str:
    """
    Generate new filename following standard format.

    Format: EXECUTIONS-{titulo}-{YYYY-MM-DD-HHmm}.md

    Args:
        old_filename: Current filename

    Returns:
        New standardized filename
    """
    # Extract components
    title = extract_title_from_filename(old_filename)
    date = extract_date_from_filename(old_filename)

    # Default time (12:00 if unknown)
    time = "1200"

    # Try to extract time from filename if present
    time_match = re.search(r"-(\d{4})\.md", old_filename)
    if time_match:
        time = time_match.group(1)

    return f"EXECUTIONS-{title}-{date}-{time}.md"


def rename_execution_files(execution_dir: Path, dry_run: bool = False) -> None:
    """
    Rename all execution files to new standard.

    Args:
        execution_dir: Path to agent-docs/execution/
        dry_run: If True, only print what would be done
    """
    print(f"📂 Processing directory: {execution_dir}")
    print(f"{'🔍 DRY RUN MODE' if dry_run else '✍️  RENAME MODE'}\n")

    files = list(execution_dir.glob("*.md"))
    renamed_count = 0
    skipped_count = 0

    for file in files:
        # Skip weekly summaries and .rej files
        if file.name.startswith("WEEK-"):
            print(f"⏭️  Skip (weekly summary): {file.name}")
            skipped_count += 1
            continue

        if file.name.endswith(".md.rej"):
            print(f"⏭️  Skip (.rej file): {file.name}")
            skipped_count += 1
            continue

        # Skip files already in new format
        if file.name.startswith("EXECUTIONS-"):
            print(f"✅ Already compliant: {file.name}")
            skipped_count += 1
            continue

        # Generate new filename
        new_name = generate_new_filename(file.name)
        new_path = file.parent / new_name

        # Check for conflicts
        if new_path.exists():
            print(f"⚠️  Conflict: {file.name} → {new_name} (target exists)")
            skipped_count += 1
            continue

        # Rename
        print(f"📝 {file.name}")
        print(f"   → {new_name}")

        if not dry_run:
            file.rename(new_path)
            renamed_count += 1
        else:
            renamed_count += 1

        print()

    # Summary
    print("=" * 80)
    print("📊 Summary:")
    print(f"   - Total files: {len(files)}")
    print(f"   - Renamed: {renamed_count}")
    print(f"   - Skipped: {skipped_count}")

    if dry_run:
        print("\n💡 Run without --dry-run to apply changes")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rename execution files to standard format"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    execution_dir = Path("agent-docs/execution")
    if not execution_dir.exists():
        print(f"❌ Directory not found: {execution_dir}")
        return 1

    rename_execution_files(execution_dir, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
