#!/usr/bin/env python3
"""
Weekly Summary Generator - CDE Orchestrator MCP

Generates weekly consolidated reports from Git commits using Conventional Commits format.

Usage:
    python scripts/consolidation/generate-weekly-summary.py [--week YYYY-WW]

Example:
    python scripts/consolidation/generate-weekly-summary.py --week 2025-45
"""

import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

# Type alias for commit data
Commit = Tuple[str, str, str, str]  # (sha, type, scope, message)


def get_iso_week_range(year: int, week: int) -> Tuple[str, str]:
    """
    Get start and end date for ISO week.

    Args:
        year: Year (e.g., 2025)
        week: ISO week number (1-53)

    Returns:
        (start_date, end_date) in YYYY-MM-DD format
    """
    # ISO 8601: Week 1 is the first week with Thursday in it
    jan_4 = datetime(year, 1, 4)
    week_1_monday = jan_4 - timedelta(days=jan_4.weekday())
    target_monday = week_1_monday + timedelta(weeks=week - 1)
    target_sunday = target_monday + timedelta(days=6)

    return target_monday.strftime("%Y-%m-%d"), target_sunday.strftime("%Y-%m-%d")


def get_commits_in_range(start_date: str, end_date: str) -> List[Commit]:
    """
    Get commits between start and end date.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        List of (sha, type, scope, message) tuples
    """
    # Git log format: %H (full SHA) %s (subject)
    cmd = [
        "git",
        "log",
        f"--since={start_date}",
        f"--until={end_date}",
        "--pretty=format:%H|||%s",
        "--no-merges",  # Exclude merge commits
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    commits: List[Commit] = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue

        sha, message = line.split("|||", 1)

        # Parse Conventional Commits format
        if ":" in message:
            type_scope, description = message.split(":", 1)
            type_scope = type_scope.strip()
            description = description.strip()

            # Extract type and scope
            if "(" in type_scope and ")" in type_scope:
                type_, scope = type_scope.split("(", 1)
                scope = scope.rstrip(")")
            else:
                type_ = type_scope
                scope = ""

            commits.append((sha[:7], type_, scope, description))
        else:
            # Non-conventional commit
            commits.append((sha[:7], "other", "", message))

    return commits


def group_commits_by_type(commits: List[Commit]) -> Dict[str, List[Commit]]:
    """
    Group commits by type.

    Args:
        commits: List of (sha, type, scope, message) tuples

    Returns:
        Dictionary mapping type to list of commits
    """
    grouped: Dict[str, List[Commit]] = {
        "feat": [],
        "fix": [],
        "refactor": [],
        "docs": [],
        "test": [],
        "chore": [],
        "other": [],
    }

    for commit in commits:
        sha, type_, scope, message = commit
        if type_ in grouped:
            grouped[type_].append(commit)
        else:
            grouped["other"].append(commit)

    return grouped


def generate_markdown(
    grouped_commits: Dict[str, List[Commit]],
    year: int,
    week: int,
    start_date: str,
    end_date: str,
) -> str:
    """
    Generate markdown for weekly summary.

    Args:
        grouped_commits: Commits grouped by type
        year: Year
        week: ISO week number
        start_date: Week start date (YYYY-MM-DD)
        end_date: Week end date (YYYY-MM-DD)

    Returns:
        Markdown content
    """
    # Convert dates to readable format
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    date_range = f"{start_dt.strftime('%B %d')} - {end_dt.strftime('%d, %Y')}"

    # Count commits by type
    feat_count = len(grouped_commits["feat"])
    fix_count = len(grouped_commits["fix"])
    refactor_count = len(grouped_commits["refactor"])
    docs_count = len(grouped_commits["docs"])
    total_count = sum(len(commits) for commits in grouped_commits.values())

    markdown = f"""---
title: "Week {week} ({date_range})"
type: "execution"
status: "completed"
created: "{end_date}"
author: "CDE Orchestrator"
tags: ["weekly-summary", "{year}-{week:02d}"]
llm_summary: "Weekly consolidation of all work from {date_range}"
---

# Week {week}: {date_range}

## 📊 Summary

- **Total Commits**: {total_count}
- **Features**: {feat_count}
- **Fixes**: {fix_count}
- **Refactors**: {refactor_count}
- **Documentation**: {docs_count}

---

## 🚀 Notable Changes

"""

    # Add sections for each type
    sections = [
        ("Features", "feat", "🚀"),
        ("Bug Fixes", "fix", "🐛"),
        ("Refactoring", "refactor", "♻️"),
        ("Documentation", "docs", "📝"),
        ("Tests", "test", "✅"),
        ("Chores", "chore", "🔧"),
    ]

    for title, type_, emoji in sections:
        commits = grouped_commits.get(type_, [])
        if not commits:
            continue

        markdown += f"### {emoji} {title}\n\n"

        for sha, _, scope, message in commits:
            scope_str = f"**{scope}**: " if scope else ""
            commit_url = f"https://github.com/iberi22/CDE-Orchestrator-MCP/commit/{sha}"
            markdown += f"- {scope_str}{message} ([{sha}]({commit_url}))\n"

        markdown += "\n"

    markdown += """---

## 🔗 Related Documentation

- CHANGELOG.md updated with [Unreleased] section
- See individual commit messages for detailed context

---

## 📈 Metrics

| Metric | This Week | Previous Week | Change |
|--------|-----------|---------------|--------|
| Commits | {total_count} | - | - |
| Files Changed | - | - | - |
| Lines Added | - | - | - |
| Lines Removed | - | - | - |

---

    **Generated**: {generated_time}
    **Script**: `scripts/consolidation/generate-weekly-summary.py`
    """.format(
        total_count=total_count,
        generated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
    )

    return markdown


def save_weekly_report(markdown: str, year: int, week: int) -> Path:
    """
    Save weekly report to agent-docs/execution/.

    Args:
        markdown: Markdown content
        year: Year
        week: ISO week number

    Returns:
        Path to saved file
    """
    execution_dir = Path("agent-docs/execution")
    execution_dir.mkdir(parents=True, exist_ok=True)

    output_file = execution_dir / f"WEEK-{year}-{week:02d}.md"
    output_file.write_text(markdown, encoding="utf-8")

    return output_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate weekly summary from Git commits"
    )
    parser.add_argument(
        "--week",
        type=str,
        help="ISO week in YYYY-WW format (default: current week)",
    )
    args = parser.parse_args()

    # Determine week
    if args.week:
        year, week = map(int, args.week.split("-"))
    else:
        today = datetime.now()
        year, week, _ = today.isocalendar()

    print(f"Generating weekly summary for {year}-W{week:02d}...")

    # Get date range
    start_date, end_date = get_iso_week_range(year, week)
    print(f"Date range: {start_date} to {end_date}")

    # Get commits
    commits = get_commits_in_range(start_date, end_date)
    print(f"Found {len(commits)} commits")

    if not commits:
        print("No commits found for this week. Exiting.")
        return

    # Group commits
    grouped = group_commits_by_type(commits)

    # Generate markdown
    markdown = generate_markdown(grouped, year, week, start_date, end_date)

    # Save report
    output_file = save_weekly_report(markdown, year, week)
    print(f"✅ Weekly summary saved: {output_file}")

    # Display preview
    print("\n" + "=" * 80)
    print("PREVIEW:")
    print("=" * 80)
    print(markdown[:500] + "...")


if __name__ == "__main__":
    main()
