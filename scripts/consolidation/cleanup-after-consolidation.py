#!/usr/bin/env python3
"""
Cleanup script: Deletes consolidated files after successful consolidation.

Usage:
    python cleanup-after-consolidation.py --execution-consolidated=true --sessions-consolidated=false

Features:
- Safe: Only deletes if consolidation file exists and is valid
- Preserves: All WEEKLY-*, FINAL-*, INTEGRATION-* files
- Explicit: Reads list of consolidated files from consolidation document
- Verification: Checks file size and YAML frontmatter
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List


def get_week_identifier() -> str:
    """Get current week in YYYY-WXX format."""
    now = datetime.now()
    iso_calendar = now.isocalendar()
    return f"{iso_calendar[0]}-W{iso_calendar[1]:02d}"


def parse_source_files(consolidation_file: Path) -> List[str]:
    """Extract source_files list from YAML frontmatter."""
    try:
        with open(consolidation_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Find YAML frontmatter
        yaml_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL | re.MULTILINE)
        if not yaml_match:
            print(f"⚠️ No YAML frontmatter found in {consolidation_file}")
            return []

        yaml_content = yaml_match.group(1)

        # Extract source_files section
        files = []
        in_source_files = False
        for line in yaml_content.split("\n"):
            if line.startswith("source_files:"):
                in_source_files = True
                continue

            if in_source_files:
                # Check if still in list (indented with "  - ")
                if line.startswith("  - "):
                    filename = line.strip()[2:].strip()
                    files.append(filename)
                elif line.strip() and not line.startswith(" "):
                    # New top-level key, exit source_files
                    break

        return files

    except Exception as e:
        print(f"❌ Error reading {consolidation_file}: {e}")
        return []


def verify_consolidation_file(file_path: Path) -> bool:
    """Verify consolidation file exists and is valid."""
    if not file_path.exists():
        print(f"❌ Consolidation file not found: {file_path}")
        return False

    size = file_path.stat().st_size
    if size < 1000:
        print(f"❌ Consolidation file too small ({size} bytes): {file_path}")
        return False

    # Check for YAML frontmatter
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            if first_line != "---":
                print(f"❌ Invalid frontmatter in: {file_path}")
                return False
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

    print(f"✅ Verified consolidation file: {file_path} ({size:,} bytes)")
    return True


def cleanup_folder(folder: str, consolidation_file: Path) -> int:
    """Delete consolidated files from specified folder."""
    folder_path = Path(folder)
    if not folder_path.exists():
        print(f"⚠️ Folder not found: {folder}")
        return 0

    # Verify consolidation file first
    if not verify_consolidation_file(consolidation_file):
        print("❌ Skipping cleanup: Consolidation file verification failed")
        return 0

    # Get list of files to delete from consolidation document
    source_files = parse_source_files(consolidation_file)
    if not source_files:
        print("⚠️ No source files found in consolidation document")
        return 0

    print(f"📋 Found {len(source_files)} files listed for deletion")

    # Delete files
    deleted_count = 0
    preserved_patterns = ["WEEKLY-", "FINAL-", "INTEGRATION-", "CONSOLIDATION_"]

    for filename in source_files:
        file_path = folder_path / filename

        # Safety check: Never delete preservation patterns
        if any(pattern in filename for pattern in preserved_patterns):
            print(f"⚠️ Skipping preserved file: {filename}")
            continue

        if file_path.exists():
            try:
                file_path.unlink()
                print(f"  ✅ Deleted: {filename}")
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ Failed to delete {filename}: {e}")
        else:
            print(f"  ⚠️ File not found: {filename}")

    return deleted_count


def main() -> None:
    """Main execution flow."""
    parser = argparse.ArgumentParser(
        description="Cleanup consolidated documentation files"
    )
    parser.add_argument(
        "--execution-consolidated",
        type=str,
        default="false",
        help="Whether execution consolidation succeeded (true/false)",
    )
    parser.add_argument(
        "--sessions-consolidated",
        type=str,
        default="false",
        help="Whether sessions consolidation succeeded (true/false)",
    )
    parser.add_argument(
        "--week",
        type=str,
        default=None,
        help="Week identifier (YYYY-WXX), defaults to current week",
    )

    args = parser.parse_args()

    print("🧹 Documentation Cleanup Script")
    print("=" * 60)

    week = args.week or get_week_identifier()
    print(f"📅 Week: {week}")

    execution_enabled = args.execution_consolidated.lower() == "true"
    sessions_enabled = args.sessions_consolidated.lower() == "true"

    total_deleted = 0

    # Cleanup execution/ folder
    if execution_enabled:
        print("\n📁 Cleaning up agent-docs/execution/...")
        exec_file = Path(
            f"agent-docs/execution/WEEKLY-CONSOLIDATION-EXECUTION-{week}.md"
        )
        deleted = cleanup_folder("agent-docs/execution", exec_file)
        total_deleted += deleted
        print(f"  ✅ Deleted {deleted} execution files")
    else:
        print("\n⏭️ Skipping execution/ cleanup (consolidation not completed)")

    # Cleanup sessions/ folder
    if sessions_enabled:
        print("\n📁 Cleaning up agent-docs/sessions/...")
        sess_file = Path(f"agent-docs/sessions/WEEKLY-CONSOLIDATION-SESSIONS-{week}.md")
        deleted = cleanup_folder("agent-docs/sessions", sess_file)
        total_deleted += deleted
        print(f"  ✅ Deleted {deleted} session files")
    else:
        print("\n⏭️ Skipping sessions/ cleanup (consolidation not completed)")

    # Summary
    print("\n" + "=" * 60)
    if total_deleted > 0:
        print(f"✅ Cleanup complete: {total_deleted} files deleted")
    else:
        print("⚠️ No files deleted (no consolidations or verification failed)")

    sys.exit(0)


if __name__ == "__main__":
    main()
