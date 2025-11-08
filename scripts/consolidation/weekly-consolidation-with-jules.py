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
from typing import Optional

import requests


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

    def get_sources(self) -> list[dict]:
        """List available Jules sources."""
        response = requests.get(f"{self.base_url}/sources", headers=self.headers)
        response.raise_for_status()
        return response.json().get("sources", [])

    def find_github_source(self, owner: str, repo: str) -> Optional[str]:
        """Find Jules source for GitHub repository."""
        sources = self.get_sources()
        for source in sources:
            if source.get("id") == f"github/{owner}/{repo}":
                return source.get("name")
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
        return data.get("id")

    def get_session(self, session_id: str) -> dict:
        """Get session details."""
        response = requests.get(
            f"{self.base_url}/sessions/{session_id}",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    def list_activities(self, session_id: str, page_size: int = 100) -> list[dict]:
        """List activities in session."""
        response = requests.get(
            f"{self.base_url}/sessions/{session_id}/activities",
            headers=self.headers,
            params={"pageSize": page_size},
        )
        response.raise_for_status()
        return response.json().get("activities", [])

    def approve_plan(self, session_id: str) -> None:
        """Approve plan in session."""
        response = requests.post(
            f"{self.base_url}/sessions/{session_id}:approvePlan",
            headers=self.headers,
        )
        response.raise_for_status()

    def wait_for_completion(self, session_id: str, max_retries: int = None) -> dict:
        """
        Poll session until completion.

        Returns:
            Final session state
        """
        if max_retries is None:
            max_retries = self.max_retries

        for attempt in range(max_retries):
            session = self.get_session(session_id)

            # Check if session is completed
            activities = self.list_activities(session_id)
            if activities:
                last_activity = activities[-1]
                if "sessionCompleted" in last_activity:
                    print(
                        f"✅ Session {session_id} completed after {attempt * self.poll_interval}s"
                    )
                    return session

            print(
                f"⏳ Poll {attempt + 1}/{max_retries}: Session still running... "
                f"(waited {(attempt + 1) * self.poll_interval}s)"
            )
            time.sleep(self.poll_interval)

        raise TimeoutError(
            f"Session {session_id} did not complete within "
            f"{max_retries * self.poll_interval}s"
        )

    def extract_output(self, session_id: str) -> str:
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

    def read_execution_files(self, file_paths: list[str]) -> str:
        """Read and concatenate file contents from relative paths."""
        contents = []
        for rel_path in file_paths:
            file_path = self.repo_root / rel_path
            if file_path.exists():
                with open(file_path, encoding="utf-8") as f:
                    contents.append(f"## {rel_path}\n\n{f.read()}\n")
            else:
                print(f"⚠️  File not found: {rel_path}")

        return "".join(contents)

    def generate_consolidation_prompt(
        self, week_label: str, file_contents: str, commit_range: Optional[str]
    ) -> str:
        """Generate prompt for Jules to consolidate weekly reports."""
        commit_info = f"Git commits: {commit_range}\n" if commit_range else ""

        num_files = len(
            [line for line in file_contents.split("\n") if line.startswith("## ")]
        )

        prompt = f"""Consolida los reportes de la semana {week_label} del repositorio CDE-Orchestrator-MCP.

**Archivos a consolidar**: {num_files} reportes de agent-docs/execution/ y agent-docs/sessions/
{commit_info}

**Instrucciones**:
1. Lee SOLO los archivos individuales proporcionados abajo (NO busques archivos consolidados)
2. Extrae logros clave, decisiones técnicas, y patrones de cada reporte
3. Agrupa información por categorías (features, fixes, docs, testing, etc.)
4. Identifica temas transversales y conexiones entre reportes
5. Crea 1 archivo consolidado en: `agent-docs/execution/WEEKLY-CONSOLIDATION-{week_label}.md`

**Formato de salida** (markdown con YAML frontmatter):
```markdown
---
title: "Weekly Consolidation {week_label}"
description: "Consolidated summary of {num_files} execution and session reports"
type: "execution"
status: "active"
created: "{datetime.now().strftime('%Y-%m-%d')}"
author: "Jules AI"
---

# Week {week_label}: Consolidated Summary

## Executive Summary
[100-150 palabras resumen de la semana]

## Key Accomplishments
- [Logro 1: Feature/componente implementado]
- [Logro 2: Bug fix importante]
- [Logro 3: Mejora de documentación]

## Technical Details

### [Categoría 1: e.g., Features]
- **[Nombre feature]**: [Descripción técnica]

### [Categoría 2: e.g., Bug Fixes]
- **[Issue]**: [Solución aplicada]

## Issues & Blockers
[Solo si hay blockers activos o pendientes]

## Next Steps
- [Paso 1]
- [Paso 2]

## Related Commits
{commit_range if commit_range else "N/A"}
```

---

## Reportes individuales:

{file_contents}

---

**IMPORTANTE**: Genera SOLO el archivo consolidado, NO modifiques los archivos originales."""

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

        # Read execution files
        file_contents = self.read_execution_files(group.files)

        # Generate consolidation prompt
        prompt = self.generate_consolidation_prompt(
            week_label, file_contents, group.commit_range
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
            print(f"   🔗 PR Created: {pr_info.get('url', 'N/A')}")
            return Path(pr_info["url"])

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
        """Move processed files to archive."""
        archive_dir = self.execution_dir / ".archive"
        archive_dir.mkdir(exist_ok=True)

        for file_name in file_names:
            src = self.execution_dir / file_name
            dst = archive_dir / file_name
            if src.exists():
                src.rename(dst)
                print(f"   📦 Archived: {file_name}")

    def run(self) -> dict[str, Path]:
        """
        Execute full consolidation workflow.

        Returns:
            Dict of week_label -> output_path
        """
        print("=" * 80)
        print("🔄 WEEKLY CONSOLIDATION WITH JULES")
        print("=" * 80)

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

        print(
            f"✅ Found {len(groups)} weeks with {sum(len(g.files) for g in groups.values())} files"
        )

        # Process each week
        results = {}
        for week_label in sorted(groups.keys()):
            group = groups[week_label]
            output_path = self.consolidate_week(week_label, group, source_name)
            if output_path:
                results[week_label] = output_path
                # Archive original files after successful consolidation
                self.archive_files(group.files)

        # Summary
        print("\n" + "=" * 80)
        print("✅ CONSOLIDATION COMPLETE")
        print(f"   - Weeks processed: {len(results)}/{len(groups)}")
        print(f"   - Output files created: {len(results)}")
        if results:
            print("\n📋 Results:")
            for week_label, path in results.items():
                print(f"   - {week_label}: {path.name}")

        return results


def main():
    """Entry point."""
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
    print(f"📁 Processing: {execution_dir}/ and {sessions_dir}/")

    consolidator = WeeklyConsolidator(
        execution_dir, sessions_dir, repo_root, jules_api_key
    )
    results = consolidator.run()

    # Return success code
    return 0 if results else 1


if __name__ == "__main__":
    exit(main())
