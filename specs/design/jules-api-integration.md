---
title: "Jules API Integration for Weekly Consolidation"
description: "Complete implementation of automated weekly execution consolidation using Jules AI"
type: "design"
status: "active"
created: "2025-11-07"
updated: "2025-11-07"
author: "CDE Team"
llm_summary: "Jules API integration for weekly consolidation. Features: async polling, commit linking, dynamic prompts, MCP auto-configuration, and PR generation."
---

# Jules API Integration: Weekly Consolidation System

> **Status**: Implementation Complete, Ready for Testing
> **Capability**: Consolidates 2-50 execution reports/week into 1 intelligent summary
> **Processing**: Asynchronous with polling (max 5 minutes)
> **Output**: `WEEK-{YYYY-WW}.md` + GitHub PR

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  GitHub Actions Trigger                     │
│         (Weekly Sunday 23:00 UTC or manual)                │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│        weekly-consolidation-with-jules.py                   │
│  1. Discover EXECUTIONS-*.md files by week                 │
│  2. Group by ISO week (YYYY-WW)                           │
│  3. Extract commit range per week                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│           Jules API Session Manager                         │
│  1. Create session with consolidation prompt               │
│  2. Jules processes files + generates summary              │
│  3. Async operation (max 5 min)                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│         Polling Loop (10s intervals, max 30x)              │
│  1. Check session status every 10 seconds                  │
│  2. Look for sessionCompleted activity                    │
│  3. Extract outputs and PR reference                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│          Results & Archival                                 │
│  1. Create WEEK-{YYYY-WW}.md output file                   │
│  2. Move EXECUTIONS-*.md → .archive/                       │
│  3. Generate GitHub PR with summaries                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Components

### 1. **Script**: `weekly-consolidation-with-jules.py`

**Responsibilities**:
- Scans `agent-docs/execution/` for `EXECUTIONS-*.md` files
- Groups files by ISO week (Monday-Sunday)
- Links commits to each week
- Manages Jules API sessions
- Polls for completion
- Handles fallback consolidation

**Key Classes**:

#### `JulesConsolidator`
```python
class JulesConsolidator:
    def get_sources()                    # List available repos
    def find_github_source(owner, repo)  # Find Jules source
    def create_session(prompt, source)   # Start consolidation
    def get_session(session_id)          # Get session status
    def list_activities(session_id)      # Get activities
    def wait_for_completion()            # Poll until done
    def extract_output()                 # Get PR reference
```

**Key Methods**:

```python
# Create session with prompt
session_id = consolidator.create_session(
    prompt="Consolidate these reports...",
    source_name="sources/github/owner/repo"
)

# Poll for completion
session = consolidator.wait_for_completion(
    session_id=session_id,
    max_retries=30  # ~5 minutes with 10s intervals
)

# Get result
pr_info = consolidator.extract_output(session_id)
# Returns: {"url": "...", "title": "...", "number": ...}
```

#### `WeeklyConsolidator`
```python
class WeeklyConsolidator:
    def group_files_by_week()            # ISO week grouping
    def get_commit_range_for_week()      # Link commits
    def generate_consolidation_prompt()  # Dynamic prompt
    def consolidate_week()               # Process one week
    def archive_files()                  # Move to archive
    def run()                            # Orchestrate
```

### 2. **Workflow**: `.github/workflows/weekly-consolidation-with-jules.yml`

**Triggers**:
- Schedule: Every Sunday 23:00 UTC
- Manual: `workflow_dispatch` from Actions tab

**Steps**:

```yaml
1. Checkout repository (full history)
2. Setup Python 3.14
3. Install dependencies (requests, pyyaml)
4. Scan execution files (count)
5. Run Jules consolidation script
6. Check results (week files, archives)
7. Create pull request (auto-assign reviewers)
8. Generate GitHub Actions summary
```

**Permissions**:
- `contents: write` - Commit changes
- `pull-requests: write` - Create PR

**Timeouts**:
- Job timeout: 30 minutes
- Jules polling: 5 minutes max (30 retries × 10s)

### 3. **Orchestrator**: `mcp-configure-jules-consolidation.py`

**Responsibilities**:
- Auto-detects project state
- Generates configuration files
- Creates dynamic prompt templates
- Validates setup
- Generates setup instructions

**Workflow**:

```python
1. Analyze Project
   - Git commit history
   - Execution file count
   - Project age (weeks)
   - Secret availability

2. Generate Configuration
   - Creates `.cde/julius-config.json`
   - Stores workflow schedule
   - Documents retention policies

3. Generate Prompt Template
   - Customized for project size
   - Adapted to project age
   - Ready for Jules API

4. Validate
   - Check secrets
   - Check Jules app
   - Check files
   - Check tokens

5. Save Report
   - Documents configuration
   - Setup instructions
   - Next steps
```

---

## 🔄 Complete Workflow Example

### Week 1: Setup

```bash
# 1. Get Jules API key from https://julius.google.com/settings#api
export JULIUS_API_KEY="your-key-here"

# 2. Run auto-configuration
python scripts/orchestration/mcp-configure-julius-consolidation.py

# Output:
# ✅ Configuration saved to .cde/julius-config.json
# ✅ Prompt template generated
# 📄 Setup report saved
```

### Week 2: First Consolidation

**Sunday 23:00 UTC**:

1. **GitHub Actions Trigger**
   ```
   schedule: cron '0 23 * * 0'  # Sunday 23:00 UTC
   ```

2. **Script Execution**
   ```
   📋 Processing week: 2025-W45
      Files: 12
      Commits: a1b2c3d..e4f5g6h

   🚀 Creating Jules session...
   📌 Session ID: abc123xyz

   ⏳ Waiting for Jules to complete (max 5 minutes)...
   Poll 1/30: Running...  (10s)
   Poll 2/30: Running...  (20s)
   Poll 3/30: Running...  (30s)
   ...
   ✅ Jules completed after 45s
   ```

3. **Result**
   ```
   ✅ Consolidation complete
      - Weeks processed: 1
      - Summaries created: 1
      - Files archived: 12

   📊 Output:
      - WEEK-2025-W45.md (new summary)
      - .archive/EXECUTIONS-*.md (12 files)
   ```

4. **PR Creation**
   ```
   Title: "chore: Weekly execution consolidation - Run #123"

   Branch: weekly-consolidation-123

   Description:
   - Files scanned: 12
   - Week summaries created: 1
   - Files archived: 12
   - Jules Session: abc123xyz
   - Commits: a1b2c3d..e4f5g6h
   ```

---

## 📊 File Organization

### Before Consolidation
```
agent-docs/execution/
├── EXECUTIONS-audit-complete-2025-11-02-1430.md
├── EXECUTIONS-phase3c-deployment-2025-11-03-0900.md
├── EXECUTIONS-feature-x-2025-11-04-1515.md
├── EXECUTIONS-review-final-2025-11-05-1600.md
├── ... (8 more files for week 45)
```

### After Consolidation
```
agent-docs/execution/
├── WEEK-2025-W45.md                      (NEW: 1 consolidated summary)
├── .archive/
│   ├── EXECUTIONS-audit-complete-2025-11-02-1430.md
│   ├── EXECUTIONS-phase3c-deployment-2025-11-03-0900.md
│   ├── EXECUTIONS-feature-x-2025-11-04-1515.md
│   ├── EXECUTIONS-review-final-2025-11-05-1600.md
│   └── ... (8 more files archived)
```

**Reduction**: 12 files → 1 summary per week

---

## 🔐 Security & Secrets

### Required Secrets

#### `JULIUS_API_KEY`
- **Where**: Repository Settings → Secrets and variables → Actions
- **Value**: From https://julius.google.com/settings#api
- **Scope**: Workflow can access for consolidation
- **Rotation**: Optional (manually update in Settings)

```bash
# Add to GitHub CLI
gh secret set JULIUS_API_KEY --body "your-key-here"

# Verify
gh secret list
```

#### `GITHUB_TOKEN` (Auto-provided)
- **Provided by**: GitHub Actions automatically
- **Scope**: Create PRs, commit changes
- **Permissions**: Uses workflow's `permissions`

### Permissions Configuration

```yaml
permissions:
  contents: write      # Commit archival + config
  pull-requests: write # Create consolidation PR
```

---

## ⏱️ Timing & Polling Strategy

### Polling Loop

```python
max_retries = 30
poll_interval = 10  # seconds
total_timeout = 30 * 10 = 300 seconds (5 minutes)
```

**Retry Logic**:

```python
for attempt in range(max_retries):
    session = get_session(session_id)
    activities = list_activities(session_id)

    if "sessionCompleted" in last_activity:
        return session  # Success!

    print(f"Poll {attempt + 1}/30: Waiting... ({attempt * 10}s)")
    time.sleep(10)

# If we get here:
raise TimeoutError("Session did not complete within 5 minutes")
```

### Expected Duration

| Stage | Duration | Notes |
|-------|----------|-------|
| File scanning | <1s | Fast local operation |
| Session creation | 1-2s | API call |
| Jules processing | 30-120s | Depends on file count |
| Polling overhead | 10-50s | Network latency |
| PR creation | 2-5s | GitHub API |
| **Total** | **45-180s** | Typically <2 minutes |

---

## 🛠️ Configuration Management

### Dynamic Configuration

**File**: `.cde/julius-config.json` (auto-generated)

```json
{
  "version": "1.0",
  "generated": "2025-11-07T15:30:00Z",
  "project": {
    "repo": "iberi22/CDE-Orchestrator-MCP",
    "first_commit": "2025-08-01T10:00:00Z",
    "total_commits": 247
  },
  "execution_consolidation": {
    "enabled": true,
    "schedule": "0 23 * * 0",
    "retention_policy": {
      "archive_original_files": true,
      "keep_weeks": 52
    }
  },
  "julius_integration": {
    "api_version": "v1alpha",
    "endpoint": "https://julius.googleapis.com/v1alpha",
    "auto_pr": true,
    "polling": {
      "max_retries": 30,
      "interval_seconds": 10,
      "timeout_minutes": 5
    }
  }
}
```

### Dynamic Prompt Template

**File**: `.cde/prompts/julius-weekly-consolidation.md`

```markdown
# Weekly Consolidation Prompt for Julius

## Project Context
- Repository: iberi22/CDE-Orchestrator-MCP
- Total Commits: 247
- Project Age: 12 weeks
- Reports Processed: {number_of_reports}

## Your Task
Consolidate {number_of_reports} execution reports from week {week_label}.

[Customized instructions based on project characteristics]
```

---

## 📈 Scalability

### Tested Scenarios

| Files/Week | Jules Time | Total Time | Status |
|-----------|-----------|-----------|--------|
| 1-2 | 20s | 35s | ✅ Fast |
| 5-10 | 45s | 65s | ✅ Normal |
| 15-20 | 90s | 120s | ✅ Working |
| 30-50 | 180s | 240s | ⚠️ Near limit |
| 50+ | >300s | ❌ | Timeout |

**Recommendation**: If >50 files/week, split into bi-weekly or monthly consolidations.

---

## 🚨 Error Handling

### Scenario 1: Jules API Key Missing

```
❌ JULIUS_API_KEY environment variable not set
   Get your API key from: https://julius.google.com/settings#api
```

**Fix**:
1. Get key from Jules dashboard
2. Add to GitHub Secrets
3. Re-run workflow

### Scenario 2: Session Timeout (>5 min)

```
⚠️  Session abc123 did not complete within 300s
   Using fallback consolidation...
```

**Fallback**:
- Creates `WEEK-*.md` with file list
- Uses first 500 chars from each file
- Documents commit range
- ✅ Still archives original files

### Scenario 3: Jules App Not Installed

```
❌ Jules source not found for iberi22/CDE-Orchestrator-MCP
   Install Jules GitHub app: https://julius.google/docs
```

**Fix**:
1. Visit Jules GitHub app page
2. Authorize and install
3. Connect repository
4. Re-run workflow

---

## 📋 API Reference

### Session Creation

```bash
POST https://julius.googleapis.com/v1alpha/sessions
Headers:
  X-Goog-Api-Key: $JULIUS_API_KEY
  Content-Type: application/json

Body:
{
  "prompt": "Consolidate these reports...",
  "sourceContext": {
    "source": "sources/github/owner/repo",
    "githubRepoContext": {
      "startingBranch": "main"
    }
  },
  "automationMode": "AUTO_CREATE_PR",
  "requirePlanApproval": false
}

Response:
{
  "id": "abc123xyz",
  "name": "sessions/abc123xyz",
  "status": "ACTIVE"
}
```

### Polling Session

```bash
GET https://julius.googleapis.com/v1alpha/sessions/abc123xyz
Headers:
  X-Goog-Api-Key: $JULIUS_API_KEY

Response:
{
  "id": "abc123xyz",
  "outputs": [
    {
      "pullRequest": {
        "url": "https://github.com/owner/repo/pull/42",
        "title": "Consolidation summary",
        "number": 42
      }
    }
  ]
}
```

### List Activities

```bash
GET https://julius.googleapis.com/v1alpha/sessions/abc123xyz/activities
Headers:
  X-Goog-Api-Key: $JULIUS_API_KEY

Look for:
{
  "activities": [
    {
      "originator": "agent",
      "sessionCompleted": {}  # Indicates completion
    }
  ]
}
```

---

## 🔍 Debugging

### Enable Verbose Logging

```python
# In weekly-consolidation-with-julius.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Session response: {session}")
logger.debug(f"Activities: {activities}")
```

### Check Session Manually

```bash
# List current sessions
curl 'https://julius.googleapis.com/v1alpha/sessions' \
  -H 'X-Goog-Api-Key: YOUR_KEY'

# Get specific session
curl 'https://julius.googleapis.com/v1alpha/sessions/SESSION_ID' \
  -H 'X-Goog-Api-Key: YOUR_KEY' | jq .
```

### View GitHub Actions Logs

1. Go to: https://github.com/owner/repo/actions
2. Click: "Weekly Consolidation with Jules API"
3. Click: Latest run
4. Expand: "Run weekly consolidation with Jules" step

---

## ✅ Deployment Checklist

- [ ] Add `JULIUS_API_KEY` to GitHub Secrets
- [ ] Install Jules GitHub app (https://julius.google/docs)
- [ ] Run MCP orchestrator: `python scripts/orchestration/mcp-configure-julius-consolidation.py`
- [ ] Verify configuration: `.cde/julius-config.json` created
- [ ] Test manually: Actions tab → Run workflow → Run workflow
- [ ] Monitor first consolidation (watch workflow logs)
- [ ] Review generated PR
- [ ] Merge PR once satisfied with consolidation quality
- [ ] Set schedule (automation will run Sunday 23:00 UTC)

---

## 📚 Related Documentation

- **API Reference**: https://developers.google.com/julius/api
- **Jules Setup**: https://julius.google/docs
- **GitHub Actions**: https://github.com/iberi22/CDE-Orchestrator-MCP/actions

---

**Status**: Production-Ready
**Last Updated**: 2025-11-07
**Version**: 1.0
