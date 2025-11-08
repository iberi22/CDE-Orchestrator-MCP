#!/usr/bin/env python3
"""
Weekly Cleanup with Grok AI Consolidation

Uses Grok (xAI API - free tier) to intelligently consolidate execution reports
from the past week into a single weekly summary, then archives processed files.

Usage:
    python scripts/consolidation/weekly-cleanup-with-grok.py

Environment:
    XAI_API_KEY: Grok API key (get free at https://x.ai/)
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import requests


class GrokConsolidator:
    """Consolidates execution reports using Grok AI."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.model = "grok-2-1212"  # Latest Grok model (free tier available)

    def consolidate_reports(self, reports: List[Dict[str, str]], week: str) -> str:
        """
        Use Grok to consolidate multiple execution reports into one weekly summary.

        Args:
            reports: List of {filename, content} dicts
            week: ISO week string (YYYY-WW)

        Returns:
            Consolidated markdown content
        """
        # Prepare prompt for Grok
        reports_text = "\n\n---\n\n".join(
            [f"## File: {r['filename']}\n\n{r['content']}" for r in reports]
        )

        prompt = f"""You are a technical documentation consolidator for CDE Orchestrator MCP.

Your task: Consolidate the following execution reports from week {week} into ONE comprehensive weekly summary.

**Guidelines**:
1. Extract KEY accomplishments (features, fixes, refactors)
2. Identify PATTERNS (common themes, recurring issues)
3. Highlight METRICS (files changed, tests added, coverage)
4. Note BLOCKERS or NEXT STEPS
5. Use CONCISE language (no fluff)
6. Format with Markdown (headers, lists, tables)

**Output Format**:
```markdown
---
title: "Week {week.split('-')[1]} (Date Range)"
type: "execution"
status: "completed"
created: "{datetime.now().strftime('%Y-%m-%d')}"
author: "CDE Orchestrator (Grok AI)"
tags: ["weekly-summary", "{week}"]
llm_summary: "Weekly consolidation of all execution reports from week {week}"
---

# Week {week.split('-')[1]}: [Date Range]

## 📊 Summary
- Total Reports: X
- Key Accomplishments: Y
- Blockers: Z

## 🚀 Notable Changes
### Features
- Item 1
- Item 2

### Fixes
- Item 1

### Refactors
- Item 1

## 📈 Metrics
| Metric | This Week | Previous Week | Change |
|--------|-----------|---------------|--------|
| Files Changed | X | - | - |

## 🔗 Related Documentation
- Links to relevant specs/docs

## 🎯 Next Steps
- Action 1
- Action 2
```

**Execution Reports to Consolidate**:

{reports_text}

Now generate the consolidated weekly summary following the format above.
"""

        # Call Grok API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a technical documentation expert specializing in software development summaries.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,  # Lower temperature for consistent output
            "max_tokens": 4000,
        }

        try:
            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=60
            )
            response.raise_for_status()

            result = response.json()
            consolidated = result["choices"][0]["message"]["content"]

            # Clean up markdown code fences if Grok wrapped output
            if consolidated.startswith("```markdown"):
                consolidated = consolidated.replace("```markdown\n", "").replace(
                    "\n```", ""
                )

            return consolidated

        except requests.exceptions.RequestException as e:
            print(f"❌ Grok API error: {e}")
            # Fallback to basic consolidation
            return self._fallback_consolidation(reports, week)

    def _fallback_consolidation(self, reports: List[Dict[str, str]], week: str) -> str:
        """Simple consolidation if Grok API fails."""
        content = f"""---
title: "Week {week.split('-')[1]} Summary"
type: "execution"
status: "completed"
created: "{datetime.now().strftime('%Y-%m-%d')}"
author: "CDE Orchestrator (Fallback)"
---

# Week {week.split('-')[1]} Summary

## Reports Processed

"""
        for report in reports:
            content += f"- {report['filename']}\n"

        content += "\n⚠️ Note: This is a basic consolidation (Grok API unavailable)\n"
        return content


def get_execution_files_from_week(
    execution_dir: Path, week_start: datetime
) -> List[Path]:
    """
    Get all execution files created during the specified week.

    Args:
        execution_dir: Path to agent-docs/execution/
        week_start: Start of the week (Monday)

    Returns:
        List of file paths
    """
    week_end = week_start + timedelta(days=7)

    files = []
    for file in execution_dir.glob("*.md"):
        # Skip existing weekly summaries
        if file.name.startswith("WEEK-"):
            continue

        # Check file modification time
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        if week_start <= mtime < week_end:
            files.append(file)

    return files


def main():
    """Main execution."""
    # Get API key
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("❌ XAI_API_KEY not found in environment")
        print("Get your free API key at: https://console.x.ai/")
        return

    # Calculate week
    today = datetime.now()
    year, week, _ = today.isocalendar()
    week_str = f"{year}-W{week:02d}"

    # Get week start (last Monday)
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    print(f"🗓️  Processing week: {week_str}")
    print(
        f"📅 Date range: {week_start.strftime('%Y-%m-%d')} to {(week_start + timedelta(days=6)).strftime('%Y-%m-%d')}"
    )

    # Find execution files
    execution_dir = Path("agent-docs/execution")
    files = get_execution_files_from_week(execution_dir, week_start)

    if not files:
        print("ℹ️  No execution files found for this week")
        return

    print(f"📄 Found {len(files)} execution reports to consolidate")

    # Read file contents
    reports = []
    for file in files:
        try:
            content = file.read_text(encoding="utf-8")
            reports.append({"filename": file.name, "content": content})
            print(f"  ✅ Read: {file.name}")
        except Exception as e:
            print(f"  ⚠️  Failed to read {file.name}: {e}")

    # Consolidate using Grok
    print("\n🤖 Consolidating with Grok AI...")
    consolidator = GrokConsolidator(api_key)
    consolidated = consolidator.consolidate_reports(reports, week_str)

    # Save weekly summary
    output_file = execution_dir / f"WEEK-{week_str}.md"
    output_file.write_text(consolidated, encoding="utf-8")
    print(f"✅ Created: {output_file}")

    # Archive processed files
    archive_dir = execution_dir / ".archive"
    archive_dir.mkdir(exist_ok=True)

    for file in files:
        try:
            dest = archive_dir / file.name
            file.rename(dest)
            print(f"  📦 Archived: {file.name}")
        except Exception as e:
            print(f"  ⚠️  Failed to archive {file.name}: {e}")

    print("\n✅ Weekly cleanup complete!")
    print(f"📊 Summary: {len(files)} files archived, 1 weekly report created")


if __name__ == "__main__":
    main()
