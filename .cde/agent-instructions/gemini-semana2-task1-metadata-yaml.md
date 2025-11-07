---
title: "GEMINI TASK 1: Fix YAML Frontmatter & Status Enums"
description: "Gemini fixes 35+ YAML frontmatter errors and status enum violations"
type: "task"
status: "active"
created: "2025-11-07"
updated: "2025-11-07"
author: "CDE-Orchestrator-MCP"
priority: "CRITICAL"
assigned_to: "gemini"
llm_summary: "Fix invalid YAML (quoted scalars, missing fields) and change status: completed → archived. 35 files in agent-docs/execution/, agent-docs/sessions/, docs/, specs/"
---

## 🎯 PRIMARY OBJECTIVE

**Agent**: Gemini
**Task Type**: YAML Frontmatter Validation & Status Enum Fixes
**Files Affected**: 35 files
**Estimated Time**: 20-25 minutes
**Complexity**: Medium

---

## 📋 DETAILED TASK BREAKDOWN

### PART 1: Fix Invalid YAML in Frontmatter (18 files)

**Problem**: Files with `Invalid YAML in frontmatter: while scanning a quoted scalar`

**Solution**: These files have unescaped quotes in YAML string fields. Pattern: `description: "text with "nested quotes""`

**Fix Pattern**:
```yaml
# ❌ WRONG
description: "Deploy feature with "special" requirement"

# ✅ CORRECT
description: "Deploy feature with special requirement"
# OR
description: 'Deploy feature with "special" requirement'
```

**Files to fix** (Part 1A - agent-docs/):
1. `agent-docs/research/archived-2025-11-07/python_314_migration_summary.md`
2. `agent-docs/research/archived-2025-11-07/specs-templates-docs/execution-report.md`
3. `agent-docs/research/archived-2025-11-07/specs-templates-docs/session-summary.md`
4. `agent-docs/sessions/session-agent-governance-implementation-2025-11.md`

**Files to fix** (Part 1B - docs/):
5. `docs/ephemeral-smart-reuse.md`
6. `docs/index.md`
7. `docs/project-status-2025-01.md`
8. `docs/python-314-upgrade-assessment-2025-11.md`
9. `docs/quick-reference-v2.md`
10. `docs/reorganization-2025-01.md`

**Files to fix** (Part 1C - specs/):
11. `specs/tasks/detailed-analysis.md`

**YAML Validation Command** (after fixing each):
```bash
python -c "import yaml; yaml.safe_load(open('path/to/file.md').read())"
```

---

### PART 2: Add Missing YAML Frontmatter (12 files)

**Problem**: Files missing frontmatter block entirely or have incomplete YAML

**Solution**: Add complete YAML frontmatter with ALL required fields

**Required Fields**:
- `title` (string)
- `description` (string, 50-150 chars)
- `type` (enum: feature|design|task|execution|feedback|research|session|governance|guide)
- `status` (enum: active|archived|deprecated|draft)
- `created` (YYYY-MM-DD)
- `updated` (YYYY-MM-DD)
- `author` (string)

**Template**:
```yaml
---
title: "Document Title Here"
description: "One sentence summary (50-150 chars)"
type: "research"
status: "active"
created: "2025-11-07"
updated: "2025-11-07"
author: "Gemini-Agent-1"
---
```

**Files to fix** (Part 2):
1. `.cde/issues/local-20251105-205938.md`
2. `.cde/issues/local-20251105-231412.md`
3. `.cde/issues/local-20251106-010711.md`
4. `.cde/issues/local-20251106-014232.md`
5. `.cde/issues/local-20251106-032116.md`
6. `.cde/jules-instructions-semana2.md`
7. `.cde/jules_execution_plan.md`
8. `agent-docs/execution/mcp-progress-tracking-implementation-2025-11-02.md`
9. `agent-docs/execution/meta-orchestration-summary-2025-11-05.md`
10. `agent-docs/sessions/readme-session-2025-11-02.md`
11. `docs/mcp-status-bar-complete-2025-11.md`
12. `docs/mcp-status-bar-solution.md`

---

### PART 3: Fix Status Enum Violations (8 files)

**Problem**: Files have `status: completed` but spec only allows `active|archived|deprecated|draft`

**Solution**: Change `completed → archived` for completed work

**Command Pattern**:
```bash
# Find files with wrong status
grep -l "status: completed" <file>

# Fix: Change to archived
sed -i 's/status: completed/status: archived/g' <file>
```

**Files to fix** (Part 3 - Change status: completed → archived):
1. `agent-docs/execution/execution-final-status-2025-11-04.md`
2. `agent-docs/execution/execution-harcos-deployment-complete-2025-11-05.md`
3. `agent-docs/execution/execution-phase2ab-complete-2025-11.md`
4. `agent-docs/execution/execution-phase3c-deployment-2025-11-04.md`
5. `agent-docs/execution/execution-phase4-commit-summary-2025-11-06.md`
6. `agent-docs/execution/execution-phase4-unified-store-optimization-2025-11-06.md`
7. `agent-docs/execution/execution-phase5-testing-validation-2025-11-06.md`
8. `agent-docs/execution/execution-repository-ready-2025-11-04.md`
9. `agent-docs/execution/git-integration-complete-2025-11-04.md`
10. `agent-docs/execution/session-phase3c-complete-2025-11-04.md`
11. `agent-docs/sessions/session-features-license-implementation-2025-11-05.md`
12. `agent-docs/sessions/session-phase5-complete-2025-11-06.md`

---

### PART 4: Fix Date Format Violations (2 files)

**Problem**: Files have `created: "2025-11-05T20:45:00Z"` (ISO 8601) but spec requires `YYYY-MM-DD`

**Solution**: Change ISO timestamps to YYYY-MM-DD format

**Command Pattern**:
```bash
# Change ISO timestamps to simple dates
sed -i 's/created: "2025-11-05T20:45:00Z"/created: "2025-11-05"/g' <file>
sed -i 's/updated: "2025-11-05T20:45:00Z"/updated: "2025-11-05"/g' <file>
```

**Files to fix** (Part 4):
1. `agent-docs/execution/integration-review-final-2025-11-05.md` (2 fields: created + updated)

---

## ✅ SUCCESS CRITERIA

- [ ] All 18 YAML files pass `python -c "import yaml; yaml.safe_load(...)"` validation
- [ ] All 12 files have valid YAML frontmatter block (starts with `---`)
- [ ] All 12 status enum fields changed from "completed" to "archived"
- [ ] All 2 date formats changed from ISO 8601 to YYYY-MM-DD
- [ ] All 35 files pass governance validation:
  ```bash
  python scripts/validation/validate-docs.py --all 2>&1 | grep -c "ERR"
  # Should show fewer ERR count (baseline: 88 ERRs, target after this task: 50 ERRs)
  ```

---

## 📝 IMPLEMENTATION NOTES

**Tools to Use**:
- Python `yaml` module for validation
- `sed` or `grep` for bulk replacements
- Git for tracking changes

**Workflow**:
1. For PART 1 (YAML quotes): Fix quoted strings, validate with yaml module
2. For PART 2 (missing frontmatter): Add complete YAML block
3. For PART 3 (status enum): Bulk replace "completed" → "archived"
4. For PART 4 (date format): Replace ISO timestamps → YYYY-MM-DD
5. After each PART: Run validation to confirm progress
6. Final: `git add -A && git commit -m "fix(governance): Gemini YAML & enum fixes - 35 files"`

**References**:
- YAML Spec: `specs/governance/DOCUMENTATION_GOVERNANCE.md` (Section 3)
- Frontmatter Template: `specs/templates/execution-report.md`
- Validation Script: `scripts/validation/validate-docs.py`

---

## 🚀 EXECUTION INSTRUCTIONS

**Run from**: `E:\scripts-python\CDE Orchestrator MCP`

**Command**:
```bash
# Phase 1: Fix YAML quotes (18 files)
# Phase 2: Add missing frontmatter (12 files)
# Phase 3: Fix status enums (12 files)
# Phase 4: Fix date formats (1 file with 2 fields)

# After each phase:
python scripts/validation/validate-docs.py --all 2>&1 | grep -E "Summary:|Errors:|Warnings:"
```

**Completion Handoff**:
When PART 4 is done, create commit with message:
```
fix(governance): Gemini YAML frontmatter & enum fixes - 35 files

- Fixed 18 files with invalid YAML quoted scalars
- Added missing frontmatter to 12 files
- Changed status: completed → archived (12 files)
- Fixed date formats: ISO 8601 → YYYY-MM-DD (1 file)

Reduces errors: 88 → ~50
Validation passing for all 35 modified files
```

Then output: `✅ GEMINI TASK 1 COMPLETE`

---

**Assignment**: GEMINI AGENT
**Status**: READY FOR EXECUTION
**Priority**: 🔴 CRITICAL (blocks Codex & Qwen tasks)
**Estimated Duration**: 20-25 minutes
