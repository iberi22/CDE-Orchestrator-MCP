#!/usr/bin/env python3
"""
Weekly Consolidation with Jules API

Groups execution files by ISO week, uses Jules API to generate weekly summaries,
and relates them to git commits.

Features:
- Discovers execution files by creation date
- Groups by ISO week (YYYY-WW)
- Calls Jules API to consolidate with AI context
- Polls for completion (async handling)
- Creates PR with results
- Handles fallback if Jules API unavailable

Usage:
    python weekly-consolidation-with-jules.py

Environment variables:
    JULES_API_KEY: API key for Jules
    GITHUB_TOKEN: GitHub token for PR creation
"""

import os
import re
import subprocess
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import requests  # type: ignore[import-untyped]


@dataclass
class WeeklyGroup:
    """Represents files grouped by ISO week."""

    year: int
    week: int
    files: list[str]
    commit_range: Optional[str] = None

    @property
    def week_label(self) -> str:
        return f"{self.year}-W{self.week:02d}"

    @property
    def output_filename(self) -> str:
        return f"WEEK-{self.week_label}.md"


class JulesConsolidator:
    """Consolidates weekly execution reports using Jules API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://jules.googleapis.com/v1alpha"
        self.headers = {
            "X-Goog-Api-Key": api_key,
            "Content-Type": "application/json",
        }
        self.source_name = None
        self.max_retries = 30
        self.poll_interval = 10  # seconds

    def get_sources(self) -> list[dict[Any, Any]]:
        """List available Jules sources."""
        response = requests.get(f"{self.base_url}/sources", headers=self.headers)
        response.raise_for_status()
        sources: list[dict[Any, Any]] = response.json().get("sources", [])
        return sources if sources else []

    def find_github_source(self, owner: str, repo: str) -> Optional[str]:
        """Find Jules source for GitHub repository."""
        sources = self.get_sources()
        for source in sources:
            source_id = source.get("id")
            if source_id == f"github/{owner}/{repo}":
                name = source.get("name")
                return str(name) if name else None
        return None

    def create_session(
        self,
        prompt: str,
        source_name: str,
        starting_branch: str = "main",
        require_plan_approval: bool = False,
    ) -> str:
        """Create new Jules session.

        Returns:
            Session ID
        """
        payload = {
            "prompt": prompt,
            "sourceContext": {
                "source": source_name,
                "githubRepoContext": {
                    "startingBranch": starting_branch,
                },
            },
            "automationMode": "AUTO_CREATE_PR",
            "requirePlanApproval": require_plan_approval,
        }

        response = requests.post(
            f"{self.base_url}/sessions",
            json=payload,
            headers=self.headers,
        )
        response.raise_for_status()
        data = response.json()
        session_id = data.get("id")
        return str(session_id) if session_id else ""

    def get_session(self, session_id: str) -> dict[Any, Any]:
        """Get session details."""
        response = requests.get(
            f"{self.base_url}/sessions/{session_id}",
            headers=self.headers,
        )
        response.raise_for_status()
        data: dict[Any, Any] = response.json()
        return data

    # def list_activities(
    #     self, session_id: str, page_size: int = 100
    # ) -> list[dict[Any, Any]]:
    #     """List activities in session - NOT AVAILABLE in Jules API v1alpha."""
    #     response = requests.get(
    #         f"{self.base_url}/sessions/{session_id}/activities",
    #         headers=self.headers,
    #         params={"pageSize": page_size},
    #     )
    #     response.raise_for_status()
    #     activities: list[dict[Any, Any]] = response.json().get("activities", [])
    #     return activities if activities else []

    def approve_plan(self, session_id: str) -> None:
        """Approve plan in session."""
        response = requests.post(
            f"{self.base_url}/sessions/{session_id}:approvePlan",
            headers=self.headers,
        )
        response.raise_for_status()

    def wait_for_completion(
        self, session_id: str, max_retries: Optional[int] = None
    ) -> dict[Any, Any]:
        """
        Poll session until completion.

        Returns:
            Final session state
        """
        if max_retries is None:
            max_retries = self.max_retries

        for attempt in range(max_retries):
            session = self.get_session(session_id)

            # Check session state (use state field instead of activities)
            state = session.get("state", "UNKNOWN")
            print(
                f"⏳ Poll {attempt + 1}/{max_retries}: Session state: {state} "
                f"(waited {(attempt + 1) * self.poll_interval}s)"
            )

            # Check if session is completed
            if state in ["COMPLETED", "FAILED", "CANCELLED"]:
                if state == "COMPLETED":
                    print(
                        f"✅ Session {session_id} completed after {attempt * self.poll_interval}s"
                    )
                else:
                    print(f"⚠️  Session {session_id} ended with state: {state}")
                return session

            time.sleep(self.poll_interval)

        raise TimeoutError(
            f"Session {session_id} did not complete within "
            f"{max_retries * self.poll_interval}s"
        )

    def extract_output(self, session_id: str) -> Optional[dict[str, Any]]:
        """Extract PR output from completed session."""
        session = self.get_session(session_id)
        outputs = session.get("outputs", [])

        for output in outputs:
            if "pullRequest" in output:
                pr = output["pullRequest"]
                return {
                    "url": pr.get("url"),
                    "title": pr.get("title"),
                    "number": pr.get("number"),
                }

        return None


class WeeklyConsolidator:
    """Main consolidation orchestrator."""

    def __init__(
        self,
        execution_dir: Path,
        sessions_dir: Path,
        repo_root: Path,
        jules_api_key: str,
    ):
        self.execution_dir = execution_dir
        self.sessions_dir = sessions_dir
        self.repo_root = repo_root
        self.jules = JulesConsolidator(jules_api_key)

    def get_git_info(self) -> tuple[str, str]:
        """Extract repo owner and name from git remote."""
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        url = result.stdout.strip()

        # Parse: https://github.com/owner/repo.git or git@github.com:owner/repo.git
        match = re.search(r"[:/]([^/:]+)/([^/]+?)(\.git)?$", url)
        if match:
            return match.group(1), match.group(2)

        raise ValueError(f"Could not parse git remote: {url}")

    def get_commit_range_for_week(
        self, year: int, week: int
    ) -> Optional[tuple[str, str]]:
        """Get git commit range for ISO week.

        Returns:
            (start_commit_sha, end_commit_sha) or None
        """
        # Calculate Monday and Sunday of the week
        jan4 = datetime(year, 1, 4)
        week_one_monday = jan4 - __import__("datetime").timedelta(days=jan4.weekday())
        monday = week_one_monday + __import__("datetime").timedelta(weeks=week - 1)
        sunday = monday + __import__("datetime").timedelta(days=6)

        # Get commits for the week
        result = subprocess.run(
            [
                "git",
                "log",
                "--format=%H",
                f"--after={monday.isoformat()}",
                f"--before={sunday.isoformat()}",
            ],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )

        commits = result.stdout.strip().split("\n")
        commits = [c for c in commits if c]

        if len(commits) >= 2:
            return (commits[-1], commits[0])  # oldest, newest
        elif len(commits) == 1:
            return (commits[0], commits[0])

        return None

    def group_files_by_week(self) -> dict[str, WeeklyGroup]:
        """Group execution and session files by ISO week, excluding already consolidated files."""
        groups = defaultdict(lambda: WeeklyGroup(0, 0, []))

        # Patterns for consolidated files to skip
        skip_patterns = [
            r"^WEEKLY-CONSOLIDATION-.*\.md$",
            r"^WEEK-\d{4}-W\d{2}\.md$",
            r"^weekly-.*\.md$",
        ]

        # Process both execution and sessions directories
        for directory in [self.execution_dir, self.sessions_dir]:
            if not directory.exists():
                print(f"⚠️  Directory not found: {directory}")
                continue

            print(f"\n📁 Scanning {directory.name}/")

            for file_path in directory.glob("*.md"):
                # Skip consolidated files
                if any(re.match(pattern, file_path.name) for pattern in skip_patterns):
                    print(f"⏭️  Skipping consolidated file: {file_path.name}")
                    continue

                # Extract date from filename
                # Supports: EXECUTIONS-{title}-{YYYY-MM-DD-HHmm}.md
                #           execution-{title}-{YYYY-MM-DD}.md
                #           session-{title}-{YYYY-MM-DD}.md
                match = re.search(r"(\d{4})-(\d{2})-(\d{2})", file_path.name)
                if not match:
                    print(f"⚠️  Could not extract date from {file_path.name}, skipping")
                    continue

                year, month, day = map(int, match.groups())
                date = datetime(year, month, day)
                iso_calendar = date.isocalendar()
                week_label = f"{iso_calendar.year}-W{iso_calendar.week:02d}"

                if week_label not in groups:
                    groups[week_label] = WeeklyGroup(
                        year=iso_calendar.year,
                        week=iso_calendar.week,
                        files=[],
                    )

                # Store relative path from repo root
                relative_path = file_path.relative_to(self.repo_root)
                groups[week_label].files.append(str(relative_path))
                print(f"  ✅ {file_path.name} → {week_label}")

        # Enrich with commit ranges
        for label, group in groups.items():
            commit_range = self.get_commit_range_for_week(group.year, group.week)
            if commit_range:
                group.commit_range = f"{commit_range[0][:7]}..{commit_range[1][:7]}"

        return groups

    # REMOVED: read_execution_files() - Jules reads files directly from repo
    # No need to pass 1500+ lines in prompt

    def generate_consolidation_prompt(
        self, week_label: str, file_paths: list[str], commit_range: Optional[str]
    ) -> str:
        """Generate enhanced prompt - Jules reads files from repo with detailed output requirements (English only)."""
        # Build file list as numbered bullets for clarity
        file_list_text = "\n".join(
            f"{i+1}. `{path}`" for i, path in enumerate(file_paths)
        )

        prompt = f"""🎯 TASK: Consolidate Weekly Documentation {week_label}

## 📋 FILES TO PROCESS ({len(file_paths)} execution/session reports):
{file_list_text}

## 🔗 GIT CONTEXT:
- Commit range: {commit_range if commit_range else 'N/A'}
- Your access: Full repository (can read any file)
- Commit type: Use 'git log' to get details for range {commit_range if commit_range else '[range not available]'}

## 🔍 YOUR TASK (Step by Step):

1. **Read Source Files**
   - Read ALL {len(file_paths)} files listed above
   - Extract: key achievements, new features, critical fixes, technical decisions
   - Note: Files are in agent-docs/execution/ and agent-docs/sessions/

2. **Analyze Commit Range**
   - If range {commit_range if commit_range else '[N/A]'} is available, analyze those commits
   - Extract: titles, architecture changes, system impact
   - Correlate: Which commits generated which documents?

3. **Intelligent Categorization**
   - **Category 1: UX & User Experience**: Interface improvements, feedback, usability
   - **Category 2: Performance & Optimization**: Speed, memory, scalability (include improvement metrics)
   - **Category 3: Architecture & Technical Debt**: Refactorings, cleanup, hexagonal patterns
   - **Category 4: Features & New Capabilities**: New features, extensions
   - **Category 5: Testing & Stability**: Test coverage, bug fixes, quality gates
   - **Category 6: Documentation & Governance**: Specs, governance, process improvements

4. **Output Structuring**
   - Group achievements by category (above)
   - For each achievement: Include technical context, impact, success metrics

## 📄 REQUIRED OUTPUT:

File: `agent-docs/execution/WEEKLY-CONSOLIDATION-{week_label}.md`

**EXACT FORMAT (copy this structure):**

```markdown
---
title: "Weekly Consolidation {week_label}"
description: "Weekly consolidation of execution documentation for {week_label}. Summary of {len(file_paths)} execution reports."
type: "execution"
status: "active"
created: "{datetime.now().strftime('%Y-%m-%d')}"
updated: "{datetime.now().strftime('%Y-%m-%d')}"
author: "Jules AI Agent"
llm_summary: |
  Executive week summary: [2 lines max with key facts and metrics]
---

## Executive Summary

[Paragraph 1: Week overview - what was achieved in business/product terms]
[Paragraph 2: Technical impact - performance improvements, architecture, stability]
[Paragraph 3: Milestones achieved - completeness, blockers resolved, new capabilities]

## 📊 Key Metrics & Impact
| Metric | Value | Category |
|--------|-------|----------|
| Commits Processed | [N] | Git |
| Reports Consolidated | {len(file_paths)} | Documentation |
| [Performance Metric] | [Value] | Performance |
| [Feature Metric] | [Value] | Features |

## 🎯 Key Accomplishments by Category

### 1️⃣ UX & User Experience
- **[Achievement Title]**: [Technical description + user impact]
- **[Achievement Title]**: [Description + metrics]

### 2️⃣ Performance & Optimization
- **[Achievement Title]**: [Description + speedup/memory/optimization metrics]
- **[Achievement Title]**: [Description + performance impact]

### 3️⃣ Architecture & Technical Debt
- **[Achievement Title]**: [Refactoring description + benefit]
- **[Achievement Title]**: [Description + code cleanup metrics]

### 4️⃣ Features & New Capabilities
- **[Achievement Title]**: [Technical description + enabled capabilities]
- **[Achievement Title]**: [Description + new functionality]

### 5️⃣ Testing & Stability
- **[Achievement Title]**: [Fix/test description + coverage improvement]
- **[Achievement Title]**: [Description + quality metrics]

### 6️⃣ Documentation & Governance
- **[Achievement Title]**: [Governance improvement description]
- **[Achievement Title]**: [Spec/architecture doc description]

## 🔧 Technical Deep Dive

### [Category 1: Main Technical Area]
- **Component**: `path/to/component`
- **Change**: Technical description of change
- **Before/After**: Comparison of previous vs new state
- **Impact**: Quantifiable impact

### [Category 2: Second Technical Area]
- **Component**: `path/to/component`
- **Change**: Technical description
- **Before/After**: Comparison
- **Impact**: Quantifiable impact

## 📁 Source Files Analyzed
These {len(file_paths)} files were processed:
{file_list_text.replace(chr(10), chr(10) + "- ")}

## 🔗 Related Git Activity
- **Commit Range**: {commit_range if commit_range else 'N/A'}
- **Commits in Range**: [Use 'git log --oneline {commit_range}' if available]
- **Files Modified**: [Statistics of changed files]

## ✅ Week Status
- **Completeness**: [Percentage of planned work completed]
- **Blockers Resolved**: [Number of technical blockers resolved]
- **New Capabilities**: [Number of new features]
- **Code Quality**: [Changes in test coverage, debt reduction, etc.]

## 📌 Next Steps & Recommendations
- [Based on reviewed documents, what's next?]
- [Identified improvement areas]
- [Technical risks or debt to monitor]
```

## ⚠️ CRITICAL INSTRUCTIONS:

**IMPORTANT**: Read files directly from repository using filesystem access. Do NOT expect content to be in this prompt.

**Validation**:
- ✅ Include YAML metadata with ALL fields (title, type, status, created, updated, author, llm_summary)
- ✅ Group by categories (UX, Performance, Architecture, Features, Testing, Governance)
- ✅ Include metrics table
- ✅ Explicitly list {len(file_paths)} files processed
- ✅ Relate to commits in range {commit_range if commit_range else '[N/A]'}
- ✅ Provide detailed technical context (not just vague summary)
- ✅ Include quantifiable numbers (375x, 180 tests, etc.)

**Output Path**: MUST be `agent-docs/execution/WEEKLY-CONSOLIDATION-{week_label}.md`
**Output Format**: Markdown with YAML frontmatter (see example above)
**Output Language**: ENGLISH ONLY - all documentation in English
"""
        return prompt

    def consolidate_week(
        self,
        week_label: str,
        group: WeeklyGroup,
        source_name: str,
    ) -> Optional[Path]:
        """
        Consolidate single week using Jules API.

        Returns:
            Path to output file or None if failed
        """
        print(f"\n📋 Processing week: {week_label}")
        print(f"   Files: {len(group.files)}")
        if group.commit_range:
            print(f"   Commits: {group.commit_range}")

        # Generate consolidation prompt (Jules reads files from repo)
        prompt = self.generate_consolidation_prompt(
            week_label, group.files, group.commit_range
        )

        # Create Jules session
        print("   🚀 Creating Jules session...")
        try:
            session_id = self.jules.create_session(
                prompt=prompt,
                source_name=source_name,
                require_plan_approval=False,
            )
            print(f"   📌 Session ID: {session_id}")
        except Exception as e:
            print(f"   ❌ Failed to create session: {e}")
            return self._fallback_consolidation(week_label, group)

        # Wait for completion
        print("   ⏳ Waiting for Jules to complete (max 5 minutes)...")
        try:
            _session = self.jules.wait_for_completion(session_id, max_retries=30)
            print("   ✅ Jules completed successfully")
        except TimeoutError as e:
            print(f"   ⚠️  {e}")
            return self._fallback_consolidation(week_label, group)

        # Extract result
        pr_info = self.jules.extract_output(session_id)
        if pr_info:
            pr_url = pr_info.get("url", "N/A")
            print(f"   🔗 PR Created: {pr_url}")
            print("   ⚠️  NOTE: Files not archived yet (PR branch not merged to main)")
            print(
                "   📋 Archive will happen after PR merge (manual or auto-merge required)"
            )
            # Return special marker to indicate PR creation (but not local completion)
            # Archive should NOT run until PR is merged
            return None  # Changed: Don't archive until PR merged

        # Fallback if no PR output
        return self._fallback_consolidation(week_label, group)

    def _fallback_consolidation(
        self, week_label: str, group: WeeklyGroup
    ) -> Optional[Path]:
        """
        Fallback consolidation if Jules API fails.
        Creates simple consolidation from file list.
        """
        print("   📝 Using fallback consolidation...")

        output_path = self.execution_dir / group.output_filename
        content = f"""---
title: "Weekly Summary - {week_label}"
description: "Consolidation of execution reports for week {week_label}"
type: "execution"
status: "active"
created: "{datetime.now().isoformat()}"
updated: "{datetime.now().isoformat()}"
author: "Jules Consolidator (Fallback)"
---

# Weekly Summary - {week_label}

## Consolidated Reports

"""

        # Add file list with links
        content += "### Included Reports\n\n"
        for file_name in group.files:
            content += f"- [{file_name}]({file_name})\n"

        if group.commit_range:
            content += f"\n### Related Commits\n\n{group.commit_range}\n"

        # Add first 500 chars of each file as preview
        content += "\n### Report Previews\n\n"
        for file_name in group.files[:5]:  # Limit to first 5
            file_path = self.execution_dir / file_name
            if file_path.exists():
                with open(file_path) as f:
                    preview = f.read()[:300]
                content += f"\n#### {file_name}\n\n{preview}...\n"

        with open(output_path, "w") as f:
            f.write(content)

        print(f"   ✅ Fallback consolidation created: {group.output_filename}")
        return output_path

    def archive_files(self, file_names: list[str]) -> None:
        """Move processed files to archive subdirectory."""
        print("\n📦 ARCHIVE: Starting archive process...")
        print(f"   Files to archive: {len(file_names)}")

        archive_dir = self.execution_dir / ".archive"
        archive_dir.mkdir(exist_ok=True)
        print(f"   Archive directory: {archive_dir} (exists: {archive_dir.exists()})")

        archived_count = 0
        for file_name in file_names:
            src = self.execution_dir / file_name
            dst = archive_dir / file_name

            print(f"\n   Processing: {file_name}")
            print(f"      Source: {src}")
            print(f"      Source exists: {src.exists()}")

            if src.exists():
                try:
                    src.rename(dst)
                    print(f"      ✅ Archived successfully → {dst}")
                    archived_count += 1
                except Exception as e:
                    print(f"      ❌ Failed to archive: {type(e).__name__}: {e}")
            else:
                print("      ⚠️  File not found at source path")

        print(
            f"\n📦 ARCHIVE COMPLETE: {archived_count}/{len(file_names)} files archived"
        )
        if archived_count < len(file_names):
            print(
                f"   ⚠️  WARNING: {len(file_names) - archived_count} files could not be archived"
            )

    def run(self, skip_current_week: bool = False) -> dict[str, Path]:
        """
        Execute full consolidation workflow.

        Args:
            skip_current_week: If True, skip consolidation of current week

        Returns:
            Dict of week_label -> output_path
        """
        print("=" * 80)
        print("🔄 WEEKLY CONSOLIDATION WITH JULES")
        print("=" * 80)

        # Get current week if skipping
        current_week_label = None
        if skip_current_week:
            today = datetime.now()
            iso_week = today.isocalendar()
            current_week_label = f"{iso_week.year}-W{iso_week.week:02d}"
            print(f"\n⏭️  Current week {current_week_label} will be skipped")

        # Get git info
        try:
            owner, repo = self.get_git_info()
            print(f"\n📍 Repository: {owner}/{repo}")
        except Exception as e:
            print(f"❌ Failed to get git info: {e}")
            return {}

        # Find Jules source
        source_name = self.jules.find_github_source(owner, repo)
        if not source_name:
            print(f"❌ Jules source not found for {owner}/{repo}")
            print("   Install Jules GitHub app first: https://jules.google.com/docs")
            return {}

        print(f"✅ Jules source found: {source_name}")

        # Group files by week
        print("\n📂 Scanning execution files...")
        groups = self.group_files_by_week()
        if not groups:
            print("⚠️  No execution files found")
            return {}

        # Filter out current week if requested
        if (
            skip_current_week
            and current_week_label is not None
            and current_week_label in groups
        ):
            current_week_files = len(groups[current_week_label].files)
            del groups[current_week_label]
            print(
                f"⏭️  Skipped current week {current_week_label} ({current_week_files} files)"
            )

        if not groups:
            print(
                "⚠️  No weeks to consolidate (all files are from current week, skipped)"
            )
            return {}

        print(
            f"✅ Found {len(groups)} weeks with {sum(len(g.files) for g in groups.values())} files"
        )

        # Process each week
        results = {}
        for week_label in sorted(groups.keys()):
            group = groups[week_label]
            print(f"\n🔄 Processing week: {week_label}")
            print(f"   Files in group: {len(group.files)}")

            output_path = self.consolidate_week(week_label, group, source_name)

            print(f"\n🔍 CHECKPOINT: consolidate_week returned: {output_path}")
            print(f"   Type: {type(output_path)}")
            print(f"   Is truthy: {bool(output_path)}")

            if output_path:
                results[week_label] = output_path
                print("✅ Consolidation successful, proceeding to archive...")
                # Archive original files after successful consolidation
                self.archive_files(group.files)
            else:
                print("❌ Consolidation returned None/False, skipping archive")

        # Summary
        print("\n" + "=" * 80)
        print("✅ CONSOLIDATION COMPLETE")
        print(f"   - Weeks processed: {len(results)}/{len(groups)}")
        print(f"   - PRs created: {len(results)}")
        if results:
            print("\n📋 Results:")
            for week_label, path in results.items():
                print(f"   - {week_label}: {path.name}")

        # Important note about archiving
        if results:
            print("\n⚠️  ARCHIVING STATUS:")
            print("   Original files NOT archived yet (waiting for PR merge)")
            print("   Archive will happen when PR is merged to main")
            print("   Consider enabling auto-merge or merge PRs manually")

        return results


def main() -> int:
    """Entry point."""
    import argparse

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Consolidate weekly execution and session reports using Jules API"
    )
    parser.add_argument(
        "--skip-current-week",
        action="store_true",
        help="Skip consolidation of current week (leave for Sunday)",
    )
    args = parser.parse_args()

    # Configuration
    execution_dir = Path("agent-docs/execution")
    sessions_dir = Path("agent-docs/sessions")
    repo_root = Path(".")
    jules_api_key = os.getenv("JULES_API_KEY")

    if not jules_api_key:
        print("❌ JULES_API_KEY environment variable not set")
        print("   Get your API key from: https://jules.google.com/settings#api")
        return 1

    if not execution_dir.exists():
        print(f"❌ Execution directory not found: {execution_dir}")
        return 1

    if not sessions_dir.exists():
        print(f"⚠️  Sessions directory not found: {sessions_dir} (optional)")

    # Run consolidation
    print("\n🚀 Starting weekly consolidation...")
    if args.skip_current_week:
        print("⏭️  Skipping current week (will be consolidated on Sunday)")

    print(f"📁 Processing: {execution_dir}/ and {sessions_dir}/")

    consolidator = WeeklyConsolidator(
        execution_dir, sessions_dir, repo_root, jules_api_key
    )
    results = consolidator.run(skip_current_week=args.skip_current_week)

    # Return success code
    return 0 if results else 1


if __name__ == "__main__":
    exit(main())
