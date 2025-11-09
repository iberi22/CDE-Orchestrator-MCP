#!/usr/bin/env python3
"""
Consolidate execution documentation using Jules API.
Generates: agent-docs/execution/WEEKLY-CONSOLIDATION-EXECUTION-YYYY-WXX.md
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List

try:
    import requests  # type: ignore
except ImportError:
    print("❌ Error: 'requests' module not found. Install with: pip install requests")
    sys.exit(1)

# Constants
JULES_API_URL = "https://jules.wandb.ai/api/v1"
REPO_OWNER = "iberi22"
REPO_NAME = "CDE-Orchestrator-MCP"
FOLDER_PATH = "agent-docs/execution"
MAX_WAIT_TIME = 1800  # 30 minutes
POLL_INTERVAL = 30  # 30 seconds


def get_week_identifier() -> str:
    """Get current week in YYYY-WXX format."""
    now = datetime.now()
    iso_calendar = now.isocalendar()
    return f"{iso_calendar[0]}-W{iso_calendar[1]:02d}"


def get_execution_files() -> List[str]:
    """Get all markdown files in execution/ folder (excluding consolidations)."""
    execution_dir = Path("agent-docs/execution")
    if not execution_dir.exists():
        print(f"❌ Directory not found: {execution_dir}")
        return []

    files = []
    for file in execution_dir.glob("*.md"):
        # Skip consolidation and verification files
        if any(
            prefix in file.name
            for prefix in ["WEEKLY-", "FINAL-", "INTEGRATION-", "CONSOLIDATION_"]
        ):
            continue
        files.append(file.name)

    files.sort()
    return files


def create_jules_session(api_key: str, files: List[str]) -> str | None:
    """Create new Jules session for consolidation."""
    week = get_week_identifier()

    prompt = f"""🔄 **Weekly Execution Documentation Consolidation - {week}**

**Objective**: Consolidate {len(files)} execution report files from `agent-docs/execution/` into a single weekly summary.

**Output File**: `agent-docs/execution/WEEKLY-CONSOLIDATION-EXECUTION-{week}.md`

**Files to Consolidate**:
{chr(10).join(f'- {f}' for f in files)}

**Instructions**:

1. **Analyze** all execution reports from `agent-docs/execution/` listed above
2. **Extract** key insights categorized by:
   - 🎨 **UX Improvements**: User experience enhancements, workflow optimizations
   - ⚡ **Performance**: Speed improvements, optimizations, benchmarks
   - 🏗️ **Architecture**: System design, patterns, structural changes
   - 🚀 **Features**: New capabilities, integrations, functionality
   - 🧪 **Testing**: Test coverage, quality assurance, validation
   - 📚 **Documentation**: Guides, specs, governance improvements

3. **Generate** a consolidated document with this YAML frontmatter:

```yaml
---
title: "Weekly Execution Consolidation - {week}"
description: "Consolidated analysis of {len(files)} execution reports for week {week}"
type: "execution"
status: "active"
created: "{datetime.now().strftime('%Y-%m-%d')}"
updated: "{datetime.now().strftime('%Y-%m-%d')}"
author: "Jules AI (Consolidation Bot)"
week: "{week}"
file_count: {len(files)}
quality_score: 0.0
categories:
  - ux_improvements
  - performance
  - architecture
  - features
  - testing
  - documentation
source_files:
{chr(10).join(f'  - {f}' for f in files)}
---
```

4. **Structure** the document:
   - Executive summary (2-3 paragraphs)
   - Category sections with bullet points
   - Key metrics and achievements
   - Lessons learned
   - Recommendations for next week

5. **Quality**: Aim for 90%+ quality score (concise, insightful, actionable)

**Important**:
- Create ONLY the consolidation file
- Do NOT delete original files (cleanup handled separately)
- Use professional technical writing style
- Focus on insights, not just listing changes
- Include cross-references between related items

**Repository**: {REPO_OWNER}/{REPO_NAME}

---
Begin consolidation now. 🚀
"""

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "repo": f"{REPO_OWNER}/{REPO_NAME}",
        "prompt": prompt,
        "metadata": {
            "type": "execution_consolidation",
            "week": week,
            "file_count": len(files),
            "folder": FOLDER_PATH,
        },
    }

    print(f"📤 Creating Jules session for {len(files)} execution files...")

    try:
        response = requests.post(
            f"{JULES_API_URL}/sessions", headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()

        session_data = response.json()
        session_id: str | None = session_data.get("id")

        if not session_id:
            print(f"❌ No session ID in response: {session_data}")
            return None

        print(f"✅ Jules session created: {session_id}")
        return str(session_id)

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to create Jules session: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


def wait_for_completion(api_key: str, session_id: str) -> bool:
    """Wait for Jules session to complete."""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    start_time = time.time()
    print(f"⏳ Waiting for Jules to complete (max {MAX_WAIT_TIME//60} minutes)...")

    while time.time() - start_time < MAX_WAIT_TIME:
        try:
            response = requests.get(
                f"{JULES_API_URL}/sessions/{session_id}", headers=headers, timeout=30
            )
            response.raise_for_status()

            session = response.json()
            status = session.get("status", "unknown")

            elapsed = int(time.time() - start_time)
            print(f"  [{elapsed}s] Status: {status}")

            if status == "completed":
                print("✅ Jules session completed successfully!")
                return True
            elif status in ["failed", "error", "cancelled"]:
                print(f"❌ Jules session failed with status: {status}")
                return False

            time.sleep(POLL_INTERVAL)

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error checking status: {e}")
            time.sleep(POLL_INTERVAL)

    print(f"❌ Timeout: Session didn't complete within {MAX_WAIT_TIME//60} minutes")
    return False


def pull_changes(api_key: str, session_id: str) -> bool:
    """Pull changes from Jules remote."""
    print("📥 Pulling changes from Jules...")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        response = requests.post(
            f"{JULES_API_URL}/sessions/{session_id}/pull", headers=headers, timeout=60
        )
        response.raise_for_status()

        print("✅ Changes pulled successfully")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to pull changes: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response: {e.response.text}")
        return False


def main() -> None:
    """Main execution flow."""
    print("🤖 Jules Execution Consolidation Script")
    print("=" * 60)

    # Check API key
    api_key = os.getenv("JULES_API_KEY")
    if not api_key:
        print("❌ JULES_API_KEY environment variable not set")
        sys.exit(1)

    # Get files to consolidate
    files = get_execution_files()
    if not files:
        print("⚠️ No execution files found to consolidate")
        sys.exit(0)

    print(f"📁 Found {len(files)} execution files to consolidate")

    # Create Jules session
    session_id = create_jules_session(api_key, files)
    if not session_id:
        sys.exit(1)

    # Wait for completion
    if not wait_for_completion(api_key, session_id):
        sys.exit(1)

    # Pull changes
    if not pull_changes(api_key, session_id):
        sys.exit(1)

    # Verify output file exists
    week = get_week_identifier()
    output_file = Path(f"agent-docs/execution/WEEKLY-CONSOLIDATION-EXECUTION-{week}.md")

    if output_file.exists():
        size = output_file.stat().st_size
        print(f"✅ Consolidation file created: {output_file} ({size} bytes)")

        if size < 1000:
            print("⚠️ Warning: File seems too small, may be incomplete")
            sys.exit(1)
    else:
        print(f"❌ Expected output file not found: {output_file}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ Execution consolidation complete!")


if __name__ == "__main__":
    main()
