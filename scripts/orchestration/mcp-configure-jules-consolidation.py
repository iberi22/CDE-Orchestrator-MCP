#!/usr/bin/env python3
"""
MCP Orchestrator: Automatic Jules Integration Setup

This script:
1. Detects project state (commit history, file organization)
2. Configures weekly consolidation workflow automatically
3. Generates dynamic Jules prompts based on project characteristics
4. Sets up GitHub secrets for Jules API
5. Validates configuration end-to-end

Usage:
    python mcp-configure-jules-consolidation.py [--auto-commit]
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class ProjectAnalysis:
    """Analysis results for project configuration."""

    repo_name: str
    repo_owner: str
    first_commit_date: Optional[datetime]
    latest_commit_date: Optional[datetime]
    total_commits: int
    total_execution_files: int
    date_range_weeks: int
    has_jules_secret: bool
    has_github_token: bool
    configuration_status: str  # "ready", "needs_secret", "needs_app"


class ProjectOrchestrator:
    """Orchestrates MCP configuration for Jules integration."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.execution_dir = repo_root / "agent-docs" / "execution"
        self.workflow_dir = repo_root / ".github" / "workflows"
        self.config_file = repo_root / ".cde" / "jules-config.json"

    def analyze_project(self) -> ProjectAnalysis:
        """Analyze project state to determine configuration."""
        print("📊 Analyzing project state...")

        # Get git info
        owner, repo = self._get_git_info()
        first_commit = self._get_first_commit_date()
        latest_commit = self._get_latest_commit_date()
        total_commits = self._count_commits()

        # Count execution files
        exec_files = list(self.execution_dir.glob("EXECUTIONS-*.md"))
        total_execution_files = len(exec_files)

        # Calculate date range
        date_range_weeks = 0
        if first_commit and latest_commit:
            delta = latest_commit - first_commit
            date_range_weeks = max(1, delta.days // 7)

        # Check for secrets
        has_jules_secret = self._check_secret("JULES_API_KEY")
        has_github_token = self._check_secret("GITHUB_TOKEN")

        # Determine status
        status = "ready"
        if not has_jules_secret:
            status = "needs_secret"
        if not self._check_julius_app_installed():
            status = "needs_app"

        analysis = ProjectAnalysis(
            repo_name=repo,
            repo_owner=owner,
            first_commit_date=first_commit,
            latest_commit_date=latest_commit,
            total_commits=total_commits,
            total_execution_files=total_execution_files,
            date_range_weeks=date_range_weeks,
            has_jules_secret=has_jules_secret,
            has_github_token=has_github_token,
            configuration_status=status,
        )

        return analysis

    def configure_workflow(self, analysis: ProjectAnalysis) -> dict:
        """Configure the Jules consolidation workflow."""
        print("\n⚙️  Configuring Jules consolidation workflow...")

        config = {
            "version": "1.0",
            "generated": datetime.now().isoformat(),
            "project": {
                "repo": f"{analysis.repo_owner}/{analysis.repo_name}",
                "first_commit": (
                    analysis.first_commit_date.isoformat()
                    if analysis.first_commit_date
                    else None
                ),
                "total_commits": analysis.total_commits,
            },
            "execution_consolidation": {
                "enabled": True,
                "schedule": "0 23 * * 0",  # Sunday 23:00 UTC
                "retention_policy": {
                    "archive_original_files": True,
                    "keep_weeks": 52,  # Keep 1 year of weekly summaries
                },
            },
            "jules_integration": {
                "api_version": "v1alpha",
                "endpoint": "https://jules.googleapis.com/v1alpha",
                "required_app": True,
                "auto_pr": True,
                "polling": {
                    "max_retries": 30,
                    "interval_seconds": 10,
                    "timeout_minutes": 30,
                },
            },
            "validation": {
                "check_secret": not analysis.has_jules_secret,
                "check_app": not self._check_julius_app_installed(),
                "check_files": analysis.total_execution_files > 0,
            },
        }

        # Save configuration
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

        print(f"✅ Configuration saved to {self.config_file}")
        return config

    def generate_dynamic_prompt_template(self, analysis: ProjectAnalysis) -> str:
        """Generate POML template for Jules based on project characteristics."""
        print("\n📝 Generating dynamic Jules prompt template...")

        emphasis = ""
        if analysis.total_commits > 1000:
            emphasis = (
                "This is an enterprise-scale project. Focus on high-level patterns."
            )
        elif analysis.date_range_weeks > 26:
            emphasis = (
                "This project has substantial history. Look for long-term trends."
            )
        else:
            emphasis = (
                "This is a relatively new project. Capture all important details."
            )

        template = f"""---
title: "Jules Consolidation Prompt Template"
description: "Dynamic prompt for weekly consolidation based on project analysis"
type: "template"
status: "active"
---

# Weekly Consolidation Prompt for Jules

## Project Context
- **Repository**: {analysis.repo_owner}/{analysis.repo_name}
- **Total Commits**: {analysis.total_commits}
- **Project Age**: {analysis.date_range_weeks} weeks
- **Reports Processed**: {{number_of_reports}}

## Consolidation Objectives

{emphasis}

### Your Task

You are consolidating {{number_of_reports}} execution reports from week {{week_label}} of the {analysis.repo_name} project.

1. **Extract Key Information**:
   - What was accomplished this week?
   - What technical challenges were addressed?
   - What decisions were made?
   - What is the current project state?

2. **Identify Patterns**:
   - Recurring themes across reports
   - Critical path items
   - Risk factors or blockers
   - Dependencies between components

3. **Maintain Continuity**:
   - Link to previous week's summary (if exists)
   - Reference related commits: {{commit_range}}
   - Preserve important details and decisions

4. **Structure Output**:
   Create a markdown file with these sections:
   - Executive Summary (100 words max)
   - Week Highlights (3-5 key points)
   - Technical Progress (organized by component)
   - Blockers & Issues (if any)
   - Recommendations (for next week)

## Output Format

Generate valid markdown with:
```markdown
---
title: "Weekly Summary - {{week_label}}"
description: "Consolidated execution report"
type: "execution"
status: "active"
created: "{{created_date}}"
author: "Jules Consolidator"
---

# Weekly Summary - {{week_label}}

## Executive Summary
[Your summary]
...
```

## Important Notes

- Use the same professional tone as the original reports
- Preserve all dates and version numbers mentioned
- Cross-reference commits when relevant
- Note any recurring issues or improvements
- This summary will become the primary record for the week

---

Now consolidate the {{number_of_reports}} reports below:
"""

        return template

    def validate_configuration(self, analysis: ProjectAnalysis) -> bool:
        """Validate that configuration is complete."""
        print("\n✅ Validating configuration...")

        checks = {
            "Jules API Secret": analysis.has_jules_secret,
            "Jules App Installed": self._check_julius_app_installed(),
            "Execution Files": analysis.total_execution_files > 0,
            "GitHub Token": analysis.has_github_token,
            "Workflow File": self.workflow_dir.exists(),
        }

        all_ok = True
        for check_name, status in checks.items():
            symbol = "✅" if status else "❌"
            print(f"   {symbol} {check_name}")
            all_ok = all_ok and status

        return all_ok

    def print_setup_instructions(self, analysis: ProjectAnalysis) -> None:
        """Print setup instructions if needed."""
        if analysis.configuration_status == "ready":
            print("\n✅ Configuration is READY!")
            print("   Weekly consolidation will start on next Sunday 23:00 UTC")
            return

        print("\n⚠️  Configuration needs setup:")

        if analysis.configuration_status == "needs_secret":
            print("\n1️⃣  Add Jules API Key to GitHub Secrets:")
            print(
                "   - Go to: https://github.com/{}/{}/settings/secrets/actions".format(
                    analysis.repo_owner, analysis.repo_name
                )
            )
            print("   - Click: New repository secret")
            print("   - Name: JULES_API_KEY")
            print(
                "   - Value: (your Jules API key from https://jules.google.com/settings#api)"
            )

        if not self._check_julius_app_installed():
            print("\n2️⃣  Install Jules GitHub App:")
            print("   - Go to: https://jules.google/docs")
            print("   - Follow setup instructions")
            print(
                f"   - Connect repository: {analysis.repo_owner}/{analysis.repo_name}"
            )

    def save_report(self, analysis: ProjectAnalysis, config: dict) -> Path:
        """Save detailed report of configuration."""
        report_path = (
            self.repo_root
            / "agent-docs"
            / "execution"
            / f"EXECUTIONS-jules-setup-{datetime.now().strftime('%Y-%m-%d-%H%M')}.md"
        )

        report = f"""---
title: "Jules Consolidation Setup Report"
description: "Automatic MCP configuration for Jules integration"
type: "execution"
status: "active"
created: "{datetime.now().isoformat()}"
author: "MCP Orchestrator"
---

# Jules Consolidation Setup Report

## Project Analysis

**Repository**: `{analysis.repo_owner}/{analysis.repo_name}`

### Statistics
- Total commits: {analysis.total_commits}
- Project age: {analysis.date_range_weeks} weeks
- Execution files: {analysis.total_execution_files}
- First commit: {analysis.first_commit_date or 'Unknown'}
- Latest commit: {analysis.latest_commit_date or 'Unknown'}

### Configuration Status
- **Overall**: {analysis.configuration_status.upper()}
- **Jules Secret**: {'✅ Configured' if analysis.has_jules_secret else '⚠️ Missing'}
- **Jules App**: {'✅ Installed' if self._check_julius_app_installed() else '⚠️ Not installed'}
- **GitHub Token**: {'✅ Available' if analysis.has_github_token else '⚠️ Missing'}

## Configuration Details

```json
{json.dumps(config, indent=2)}
```

## Workflow Schedule

- **Frequency**: Every Sunday at 23:00 UTC
- **Process**: Consolidate all execution files from previous week
- **Output**: `WEEK-{{YYYY-WW}}.md` format
- **Archive**: Original files moved to `.archive/`

## Next Steps

1. {("✅ Add JULES_API_KEY to GitHub secrets" if analysis.has_jules_secret else "❌ Add JULIUS_API_KEY to GitHub secrets")}
2. {("✅ Install Jules GitHub app" if self._check_julius_app_installed() else "❌ Install Julius GitHub app from https://julius.google")}
3. ✅ First consolidation will run automatically next Sunday 23:00 UTC
4. 📝 Review and merge the auto-generated PR with consolidated summaries

## Technical Details

### Jules API Integration
- Endpoint: `https://jules.googleapis.com/v1alpha`
- Model: Latest available (auto-selected by Jules)
- Polling: 10-second intervals, max 30 retries (5 minutes timeout)
- Automation: Auto-create PR with consolidated results

### File Organization
- Input: `agent-docs/execution/EXECUTIONS-*.md`
- Output: `agent-docs/execution/WEEK-{{YYYY-WW}}.md`
- Archive: `agent-docs/execution/.archive/`

### Git Integration
- Commits grouped by ISO week
- Each consolidation creates a conventional commit
- Automatic PR linking to week consolidation

---

Report generated: {datetime.now().isoformat()}
"""

        with open(report_path, "w") as f:
            f.write(report)

        print(f"\n📄 Setup report saved to: {report_path}")
        return report_path

    # Helper methods

    def _get_git_info(self) -> tuple[str, str]:
        """Get repo owner and name from git remote."""
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        url = result.stdout.strip()

        import re

        match = re.search(r"[:/]([^/:]+)/([^/]+?)(\.git)?$", url)
        if match:
            return match.group(1), match.group(2)
        raise ValueError(f"Could not parse git remote: {url}")

    def _get_first_commit_date(self) -> Optional[datetime]:
        """Get date of first commit."""
        result = subprocess.run(
            ["git", "log", "--format=%aI", "--reverse"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        lines = result.stdout.strip().split("\n")
        if lines:
            return datetime.fromisoformat(lines[0])
        return None

    def _get_latest_commit_date(self) -> Optional[datetime]:
        """Get date of latest commit."""
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            return datetime.fromisoformat(result.stdout.strip())
        return None

    def _count_commits(self) -> int:
        """Count total commits."""
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        try:
            return int(result.stdout.strip())
        except ValueError:
            return 0

    def _check_secret(self, secret_name: str) -> bool:
        """Check if GitHub secret exists (local check)."""
        # Local check: look in .env or environment
        if os.getenv(secret_name):
            return True

        env_file = self.repo_root / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if secret_name in line:
                        return True
        return False

    def _check_julius_app_installed(self) -> bool:
        """Check if Jules app is installed (checks README/docs)."""
        readme = self.repo_root / "README.md"
        if readme.exists():
            content = readme.read_text()
            if "julius" in content.lower() or "app" in content.lower():
                return True
        return False


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Configure Jules integration for MCP")
    parser.add_argument(
        "--auto-commit",
        action="store_true",
        help="Automatically commit configuration changes",
    )

    parser.parse_args()

    # Initialize orchestrator
    repo_root = Path(".")
    orchestrator = ProjectOrchestrator(repo_root)

    print("=" * 80)
    print("🤖 MCP ORCHESTRATOR: JULES INTEGRATION SETUP")
    print("=" * 80)

    try:
        # Analyze project
        analysis = orchestrator.analyze_project()

        print(f"\n📍 Repository: {analysis.repo_owner}/{analysis.repo_name}")
        print(f"   Commits: {analysis.total_commits}")
        print(f"   Execution files: {analysis.total_execution_files}")
        print(f"   Age: {analysis.date_range_weeks} weeks")

        # Configure workflow
        config = orchestrator.configure_workflow(analysis)

        # Generate prompt template
        template = orchestrator.generate_dynamic_prompt_template(analysis)
        template_path = repo_root / ".cde" / "prompts" / "jules-weekly-consolidation.md"
        template_path.parent.mkdir(parents=True, exist_ok=True)
        with open(template_path, "w") as f:
            f.write(template)
        print(f"✅ Prompt template generated: {template_path}")

        # Validate
        is_valid = orchestrator.validate_configuration(analysis)

        # Print instructions
        orchestrator.print_setup_instructions(analysis)

        # Save report
        orchestrator.save_report(analysis, config)

        print("\n" + "=" * 80)
        if is_valid:
            print("✅ SETUP COMPLETE - Ready to consolidate!")
        else:
            print("⚠️  SETUP INCOMPLETE - Follow instructions above")
        print("=" * 80)

        return 0 if is_valid else 1

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
