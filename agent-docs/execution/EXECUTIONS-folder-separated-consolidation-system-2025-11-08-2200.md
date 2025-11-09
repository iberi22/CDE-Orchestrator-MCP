---
title: "Folder-Separated Weekly Consolidation System"
description: "New automated workflow for separate execution and session consolidations using Jules AI"
type: "execution"
status: "active"
created: "2025-11-08"
updated: "2025-11-08"
author: "GitHub Copilot"
tags:
  - consolidation
  - jules
  - automation
  - workflow
llm_summary: |
  New consolidation system that maintains folder structure:
  execution/ files → execution/WEEKLY-CONSOLIDATION-EXECUTION-YYYY-WXX.md
  sessions/ files → sessions/WEEKLY-CONSOLIDATION-SESSIONS-YYYY-WXX.md
  Automated via GitHub Actions with Jules AI, includes safe cleanup.
---

# Folder-Separated Weekly Consolidation System

## 📊 Executive Summary

**Problem Solved**: Previous consolidation mixed execution + sessions in single file, violating folder structure principle.

**Solution**: New workflow generates **separate consolidations per folder**, maintaining architectural integrity.

**Status**: ✅ Implemented, ready for testing

---

## 🎯 Architecture

### Before (Incorrect)

```
agent-docs/
├── execution/
│   ├── WEEKLY-CONSOLIDATION-2025-W45.md  ⚠️ Contains BOTH execution (54) + sessions (16)
│   └── [13 other files]
└── sessions/
    └── [EMPTY - no consolidation] ❌
```

**Problem**: Mixed content, sessions/ folder has no weekly summary.

### After (Correct)

```
agent-docs/
├── execution/
│   ├── WEEKLY-CONSOLIDATION-EXECUTION-2025-W45.md  ✅ Only execution files (54)
│   ├── execution-file-1.md
│   ├── execution-file-2.md
│   └── ...
└── sessions/
    ├── WEEKLY-CONSOLIDATION-SESSIONS-2025-W45.md  ✅ Only sessions files (16)
    ├── session-log-1.md
    ├── session-log-2.md
    └── ...
```

**Benefits**:
- ✅ Folder structure integrity maintained
- ✅ Each folder gets its own weekly summary
- ✅ Clear separation of concerns
- ✅ Easier to navigate and search

---

## 🔧 Components

### 1. GitHub Actions Workflow

**File**: `.github/workflows/weekly-consolidation-jules-separated.yml`

**Schedule**: Every Sunday at 23:00 UTC

**Process**:
1. **Scan**: Count files in execution/ and sessions/ (excludes WEEKLY-*, FINAL-*)
2. **Consolidate Execution**: Call Jules API with execution/ files → generate EXECUTION consolidation
3. **Consolidate Sessions**: Call Jules API with sessions/ files → generate SESSIONS consolidation
4. **Verify**: Check both consolidations exist and are >1KB
5. **Cleanup**: Delete original files (only if consolidations succeeded)
6. **PR**: Create pull request with both consolidations

**Manual Trigger**:
```bash
gh workflow run weekly-consolidation-jules-separated.yml
```

**Skip Cleanup**:
```bash
gh workflow run weekly-consolidation-jules-separated.yml -f skip_cleanup=true
```

### 2. Python Scripts

#### `consolidate-execution-with-jules.py`

**Location**: `scripts/consolidation/`

**Purpose**: Call Jules API to consolidate execution/ folder

**Output**: `agent-docs/execution/WEEKLY-CONSOLIDATION-EXECUTION-YYYY-WXX.md`

**Features**:
- Scans execution/ for .md files (excludes WEEKLY-*, FINAL-*, INTEGRATION-*)
- Creates Jules session with detailed prompt
- Waits for completion (max 30 min, polls every 30 sec)
- Pulls changes from Jules remote
- Verifies output file exists and is >1KB

**Usage**:
```bash
export JULES_API_KEY="your-key"
python scripts/consolidation/consolidate-execution-with-jules.py
```

#### `consolidate-sessions-with-jules.py`

**Location**: `scripts/consolidation/`

**Purpose**: Call Jules API to consolidate sessions/ folder

**Output**: `agent-docs/sessions/WEEKLY-CONSOLIDATION-SESSIONS-YYYY-WXX.md`

**Features**: Same as execution script, but for sessions/ folder

**Usage**:
```bash
export JULES_API_KEY="your-key"
python scripts/consolidation/consolidate-sessions-with-jules.py
```

#### `cleanup-after-consolidation.py`

**Location**: `scripts/consolidation/`

**Purpose**: Safe deletion of consolidated files

**Features**:
- Verifies consolidation file exists (size >1KB, valid YAML)
- Extracts `source_files` list from YAML frontmatter
- Deletes only explicitly listed files
- **Preserves**: WEEKLY-*, FINAL-*, INTEGRATION-*, CONSOLIDATION_* patterns
- Supports selective cleanup (execution only, sessions only, or both)

**Usage**:
```bash
python scripts/consolidation/cleanup-after-consolidation.py \
  --execution-consolidated=true \
  --sessions-consolidated=true \
  --week=2025-W45
```

---

## 📋 Consolidation Document Structure

### Execution Consolidation

**File**: `execution/WEEKLY-CONSOLIDATION-EXECUTION-YYYY-WXX.md`

**YAML Frontmatter**:
```yaml
---
title: "Weekly Execution Consolidation - 2025-W45"
description: "Consolidated analysis of 54 execution reports for week 2025-W45"
type: "execution"
status: "active"
created: "2025-11-08"
updated: "2025-11-08"
author: "Jules AI (Consolidation Bot)"
week: "2025-W45"
file_count: 54
quality_score: 92.0
categories:
  - ux_improvements
  - performance
  - architecture
  - features
  - testing
  - documentation
source_files:
  - execution-phase3c-deployment-2025-11-04.md
  - execution-jules-integration-2025-11-05.md
  - [... 52 more files]
---
```

**Content Structure**:
1. Executive summary (2-3 paragraphs)
2. Category sections:
   - 🎨 UX Improvements
   - ⚡ Performance
   - 🏗️ Architecture
   - 🚀 Features
   - 🧪 Testing
   - 📚 Documentation
3. Key metrics and achievements
4. Lessons learned
5. Recommendations

### Sessions Consolidation

**File**: `sessions/WEEKLY-CONSOLIDATION-SESSIONS-YYYY-WXX.md`

**YAML Frontmatter**: Similar to execution, but `type: "session"` and `file_count: 16`

**Content Structure**:
1. Executive summary
2. Session highlights (key accomplishments per session)
3. Category sections (same 6 categories)
4. Patterns and trends across sessions
5. Lessons learned
6. Recommendations for improvement

---

## 🚀 Testing the New System

### Step 1: Manual Test (Recommended First)

```bash
# Set Jules API key
export JULES_API_KEY="your-key-here"

# Run execution consolidation
python scripts/consolidation/consolidate-execution-with-jules.py

# Run sessions consolidation (if sessions exist)
python scripts/consolidation/consolidate-sessions-with-jules.py

# Verify output files
ls -lh agent-docs/execution/WEEKLY-CONSOLIDATION-EXECUTION-*.md
ls -lh agent-docs/sessions/WEEKLY-CONSOLIDATION-SESSIONS-*.md

# Test cleanup (with --dry-run if you add that option)
python scripts/consolidation/cleanup-after-consolidation.py \
  --execution-consolidated=true \
  --sessions-consolidated=false
```

### Step 2: GitHub Actions Test

```bash
# Trigger workflow manually (skip cleanup first time)
gh workflow run weekly-consolidation-jules-separated.yml \
  -f skip_cleanup=true

# Monitor workflow
gh run watch

# Check PR created
gh pr list

# Review consolidation files in PR
gh pr view <number>
```

### Step 3: Full Automation Test

```bash
# Trigger with cleanup enabled
gh workflow run weekly-consolidation-jules-separated.yml

# Verify cleanup happened
gh run view <run-id>
```

---

## 🔒 Safety Features

### 1. Verification Before Cleanup

- Consolidation file must exist
- File size must be >1KB (prevents empty files)
- Valid YAML frontmatter required
- `source_files` list must be present

### 2. Preservation Rules

**Never Deleted**:
- Files matching `WEEKLY-*`
- Files matching `FINAL-*`
- Files matching `INTEGRATION-*`
- Files matching `CONSOLIDATION_*`
- Any file not listed in `source_files`

### 3. Explicit File Lists

Cleanup script reads exact filenames from consolidation document's `source_files` list. No pattern matching = no accidental deletions.

### 4. Selective Cleanup

Can cleanup execution/ only, sessions/ only, or both:
```bash
# Only execution
cleanup-after-consolidation.py --execution-consolidated=true --sessions-consolidated=false

# Only sessions
cleanup-after-consolidation.py --execution-consolidated=false --sessions-consolidated=true

# Both
cleanup-after-consolidation.py --execution-consolidated=true --sessions-consolidated=true
```

---

## 📊 Migration from W45 Mixed Consolidation

### Current State (Incorrect)

```
execution/WEEKLY-CONSOLIDATION-2025-W45.md
  - Contains: 54 execution + 16 sessions (mixed)
  - Size: 12.68 KB
```

### Required Actions

1. **Split W45 Consolidation** (manual, one-time):
   ```bash
   # Extract execution content (54 files)
   # → execution/WEEKLY-CONSOLIDATION-EXECUTION-2025-W45.md

   # Extract sessions content (16 files)
   # → sessions/WEEKLY-CONSOLIDATION-SESSIONS-2025-W45.md

   # Delete mixed file
   rm agent-docs/execution/WEEKLY-CONSOLIDATION-2025-W45.md
   ```

2. **Update YAML Frontmatter**:
   - Execution: `type: "execution"`, `file_count: 54`
   - Sessions: `type: "session"`, `file_count: 16`
   - Both: Add proper `source_files` lists

3. **Commit Changes**:
   ```bash
   git add agent-docs/
   git commit -m "refactor(docs): Split W45 consolidation into folder-separated files"
   ```

**Next Consolidation (W46+)**: Will automatically use new separated system.

---

## 🎯 Quality Targets

| Metric | Target | W44 | W45 (Mixed) | W46+ (Separated) |
|--------|--------|-----|-------------|------------------|
| Quality Score | >90% | 94% | 92% | TBD |
| Processing Time | <30 min | 18 min | 19 min | ~20 min each |
| File Size | >5 KB | 6.88 KB | 12.68 KB | ~7-8 KB each |
| Consolidation Ratio | >10:1 | 6:1 | 70:1 | ~30:1 each |

---

## 🔮 Future Enhancements

### Phase 2: Smart Consolidation

- **Incremental**: Only consolidate files added since last run
- **Thresholds**: Skip if <5 files to consolidate
- **Multi-week**: Quarterly mega-consolidations

### Phase 3: Quality Analysis

- **Automated Review**: Score consolidations before PR
- **Trend Detection**: Identify recurring patterns
- **Recommendation Engine**: Suggest process improvements

### Phase 4: Integration

- **Slack Notifications**: Weekly consolidation summaries
- **Dashboard**: Consolidation metrics over time
- **API**: Expose consolidation data for other tools

---

## 📚 References

### Documentation

- **Workflow**: `.github/workflows/weekly-consolidation-jules-separated.yml`
- **Scripts**: `scripts/consolidation/` directory
- **W44 Report**: `agent-docs/execution/FINAL-VERIFICATION-JULES-W44-2025-11-08.md`
- **W45 Report**: `agent-docs/execution/FINAL-VERIFICATION-JULES-W45-2025-11-08.md`

### Jules API

- **Documentation**: https://docs.jules.wandb.ai/
- **API Base**: `https://jules.wandb.ai/api/v1`
- **Session Endpoints**: `/sessions`, `/sessions/{id}`, `/sessions/{id}/pull`

### Git Commits

- **W45 Mixed Consolidation**: `a49806f`
- **W45 Cleanup**: `c2243f7`
- **New Separated System**: (this commit)

---

## ✅ Checklist for Agent Continuation

If you're an AI agent picking up this work:

- [ ] **Test Scripts Locally**: Run all 3 Python scripts with test data
- [ ] **Verify Jules API**: Ensure `JULES_API_KEY` is set in GitHub secrets
- [ ] **Split W45 Consolidation**: Extract execution/sessions content to separate files
- [ ] **Update W45 YAML**: Add `source_files` lists to both split documents
- [ ] **Run Workflow**: Trigger manual workflow run with `skip_cleanup=true`
- [ ] **Review PR**: Check consolidation quality before merge
- [ ] **Enable Automation**: Let workflow run on schedule (Sunday 23:00 UTC)
- [ ] **Monitor First Auto-Run**: Verify W46 consolidation works correctly
- [ ] **Update Documentation**: Add to `docs/` if workflow proves stable

---

**Status**: ✅ System implemented, ready for testing
**Next Step**: Split W45 consolidation + test workflow manually
**Owner**: GitHub Copilot + User Review
**Date**: 2025-11-08
