#!/usr/bin/env python3
"""
Detect old weeks needing consolidation.
Outputs to GITHUB_OUTPUT for workflow use.
"""

import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def main() -> None:
    """Main detection logic."""
    # Get current ISO week
    today = datetime.now()
    current_week = today.isocalendar()
    current_week_label = f"{current_week.year}-W{current_week.week:02d}"

    print(f"📅 Current week: {current_week_label}")

    # Scan execution and sessions directories
    directories = [
        Path("agent-docs/execution"),
        Path("agent-docs/sessions"),
    ]

    # Skip patterns (already consolidated)
    skip_patterns = [
        r"^WEEKLY-CONSOLIDATION-.*\.md$",
        r"^WEEK-\d{4}-W\d{2}\.md$",
        r"^weekly-.*\.md$",
    ]

    # Group files by week
    weeks: dict[str, list[str]] = defaultdict(list)
    for directory in directories:
        if not directory.exists():
            continue

        for file_path in directory.glob("*.md"):
            # Skip consolidated files
            if any(re.match(pattern, file_path.name) for pattern in skip_patterns):
                continue

            # Extract date
            match = re.search(r"(\d{4})-(\d{2})-(\d{2})", file_path.name)
            if not match:
                continue

            year, month, day = map(int, match.groups())
            date = datetime(year, month, day)
            iso_week = date.isocalendar()
            week_label = f"{iso_week.year}-W{iso_week.week:02d}"

            weeks[week_label].append(file_path.name)

    # Find old weeks (not current week)
    old_weeks = sorted([week for week in weeks.keys() if week != current_week_label])

    if old_weeks:
        print(f"\n✅ Found {len(old_weeks)} old weeks needing consolidation:")
        for week in old_weeks:
            print(f"   - {week}: {len(weeks[week])} files")

        # Export to GitHub Actions
        github_output = os.getenv("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                f.write("has_old_weeks=true\n")
                f.write(f"old_weeks_count={len(old_weeks)}\n")
                f.write(f"oldest_week={old_weeks[0]}\n")
                f.write(f"current_week={current_week_label}\n")
            print(f"\n✅ Wrote outputs to GITHUB_OUTPUT: {github_output}")
        else:
            print("\n⚠️  GITHUB_OUTPUT not set (running locally?)")
            print("   has_old_weeks=true")
            print(f"   old_weeks_count={len(old_weeks)}")
            print(f"   oldest_week={old_weeks[0]}")
            print(f"   current_week={current_week_label}")
    else:
        print(
            f"\n⏭️  No old weeks found. All files are from current week {current_week_label}"
        )
        github_output = os.getenv("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                f.write("has_old_weeks=false\n")
                f.write(f"current_week={current_week_label}\n")
            print(f"\n✅ Wrote outputs to GITHUB_OUTPUT: {github_output}")
        else:
            print("\n⚠️  GITHUB_OUTPUT not set (running locally?)")
            print("   has_old_weeks=false")
            print(f"   current_week={current_week_label}")


if __name__ == "__main__":
    main()
