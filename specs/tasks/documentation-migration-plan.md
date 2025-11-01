---
title: "Documentation Migration Plan"
description: "Plan for reorganizing root-level markdown files to comply with governance rules"
type: "task"
status: "active"
created: "2025-11-01"
updated: "2025-11-01"
author: "KERNEL (GPT-5)"
tags:
  - "documentation"
  - "governance"
  - "migration"
  - "organization"
llm_summary: |
  Migration plan for moving root-level markdown files to their proper locations.
  Documents the source and destination for each file based on governance rules.
  Reference when executing the documentation reorganization.
---

# Documentation Migration Plan

## 📋 Overview

This document outlines the plan for moving all root-level markdown files to their appropriate directories according to `specs/governance/DOCUMENTATION_GOVERNANCE.md`.

**Status**: Ready for Execution
**Estimated Time**: 20 minutes
**Risk Level**: Low (Git-tracked, reversible)

---

## 🎯 Files to Move

### High-Level Documentation → `docs/`

| Current Location | New Location | Reason |
|------------------|--------------|--------|
| `AGENTS.md` | `docs/AGENTS.md` | Agent usage guide |
| `CODEX.md` | `docs/CODEX.md` | Development codex |
| `EXECUTIVE_SUMMARY.md` | `docs/EXECUTIVE_SUMMARY.md` | Project overview |
| `GEMINI.md` | `docs/GEMINI.md` | Gemini-specific guide |
| `INTEGRATION.md` | `docs/INTEGRATION.md` | Integration guide |
| `QUICK_REFERENCE.md` | `docs/QUICK_REFERENCE.md` | Quick reference guide |

### Technical Architecture → `specs/design/`

| Current Location | New Location | Reason |
|------------------|--------------|--------|
| `ARCHITECTURE.md` | `specs/design/ARCHITECTURE.md` | Technical architecture document |

### Feature Documentation → `specs/features/`

| Current Location | New Location | Reason |
|------------------|--------------|--------|
| `ONBOARDING_FEATURE.md` | `specs/features/onboarding-system.md` | Feature specification |

### Task/Planning Documents → `specs/tasks/`

| Current Location | New Location | Reason |
|------------------|--------------|--------|
| `PLANNING.md` | `specs/tasks/planning-overview.md` | Planning document |
| `TASK.md` | `specs/tasks/detailed-analysis.md` | Detailed task analysis |

### Migration Instructions → `docs/` or `agent-docs/execution/`

| Current Location | New Location | Reason |
|------------------|--------------|--------|
| `INSTRUCCIONES_MIGRACION_PYTHON_314.md` | `docs/python-314-migration-guide.md` | User-facing guide |

### Files That Stay in Root ✅

| File | Reason |
|------|--------|
| `README.md` | Project identity (allowed) |
| `CHANGELOG.md` | Version history (allowed) |
| `CONTRIBUTING.md` | Contribution guidelines (allowed) |

---

## 🔧 Migration Steps

### Step 1: Backup Current State

```bash
# Create backup branch
git checkout -b docs-migration-backup
git add -A
git commit -m "Backup before documentation migration"
git checkout main
```

### Step 2: Move Documentation Files

```bash
# Navigate to repo root
cd "E:\scripts-python\CDE Orchestrator MCP"

# Move to docs/
git mv AGENTS.md docs/AGENTS.md
git mv CODEX.md docs/CODEX.md
git mv EXECUTIVE_SUMMARY.md docs/EXECUTIVE_SUMMARY.md
git mv GEMINI.md docs/GEMINI.md
git mv INTEGRATION.md docs/INTEGRATION.md
git mv QUICK_REFERENCE.md docs/QUICK_REFERENCE.md
git mv INSTRUCCIONES_MIGRACION_PYTHON_314.md docs/python-314-migration-guide.md

# Move to specs/design/
git mv ARCHITECTURE.md specs/design/ARCHITECTURE.md

# Move to specs/features/
git mv ONBOARDING_FEATURE.md specs/features/onboarding-system.md

# Move to specs/tasks/
git mv PLANNING.md specs/tasks/planning-overview.md
git mv TASK.md specs/tasks/detailed-analysis.md
```

### Step 3: Update Cross-References

Update references in files that point to moved documents:

```bash
# Find all references to moved files
grep -r "AGENTS.md" .
grep -r "ARCHITECTURE.md" .
grep -r "EXECUTIVE_SUMMARY.md" .
# ... etc
```

**Files likely to need updates:**

- `README.md` (main project readme)
- `docs/INDEX.md` (documentation index)
- `.github/copilot-instructions.md` (Copilot instructions)
- Various spec documents

### Step 4: Add Metadata to Moved Files

```bash
# Add metadata to all moved files
python scripts/metadata/add-metadata.py --directory docs/
python scripts/metadata/add-metadata.py --directory specs/design/
python scripts/metadata/add-metadata.py --directory specs/features/
python scripts/metadata/add-metadata.py --directory specs/tasks/
```

### Step 5: Validate

```bash
# Run governance validation
python scripts/validation/enforce-doc-governance.py < <(git diff --name-only --cached)

# Run metadata validation
python scripts/validation/validate-metadata.py --staged

# Run pre-commit hooks
pre-commit run --all-files
```

### Step 6: Commit Changes

```bash
git add -A
git commit -m "refactor(docs): reorganize documentation per governance rules

- Move agent guides to docs/
- Move architecture to specs/design/
- Move features to specs/features/
- Move tasks to specs/tasks/
- Add metadata frontmatter to all moved files
- Update cross-references

Closes #<issue-number> (if applicable)"
```

---

## 📝 Reference Update Checklist

After moving files, update these references:

### In `README.md`

- [ ] Links to ARCHITECTURE.md → `specs/design/ARCHITECTURE.md`
- [ ] Links to EXECUTIVE_SUMMARY.md → `docs/EXECUTIVE_SUMMARY.md`
- [ ] Links to AGENTS.md → `docs/AGENTS.md`

### In `docs/INDEX.md`

- [ ] Update all file paths to new locations
- [ ] Verify all links work

### In `.github/copilot-instructions.md`

- [ ] Update references to moved documentation
- [ ] Verify agent instructions still accurate

### In Spec Documents

- [ ] Search for `TASK.md` → update to `specs/tasks/detailed-analysis.md`
- [ ] Search for `PLANNING.md` → update to `specs/tasks/planning-overview.md`

---

## 🧪 Testing Plan

### Pre-Migration Tests

- [ ] All links in README.md work
- [ ] All links in docs/INDEX.md work
- [ ] Pre-commit hooks pass

### Post-Migration Tests

- [ ] All links in README.md work (updated paths)
- [ ] All links in docs/INDEX.md work (updated paths)
- [ ] Pre-commit hooks pass
- [ ] Metadata validation passes
- [ ] No broken references in any .md files

### Validation Command

```bash
# Check for broken markdown links (if tool available)
find . -name "*.md" -exec markdown-link-check {} \;

# Or manual verification
grep -r "\[.*\](.*\.md)" . | grep -v ".git"
```

---

## 🔄 Rollback Plan

If issues arise:

```bash
# Option 1: Git reset
git reset --hard HEAD~1

# Option 2: Restore from backup branch
git checkout docs-migration-backup
git checkout -b main-restored
git branch -D main
git branch -m main-restored main
```

---

## 📊 Expected Outcomes

### Before Migration

```text
Root directory:
├── 14 .md files (only 3 allowed)
├── 1 test file in root
└── Disorganized scripts/
```

### After Migration

```text
Root directory:
├── 3 .md files (README, CHANGELOG, CONTRIBUTING) ✅
├── 0 test files in root ✅
└── Organized structure:
    ├── docs/ (6 guides)
    ├── specs/
    │   ├── design/ (1 architecture doc)
    │   ├── features/ (1 feature spec)
    │   └── tasks/ (2 planning docs)
    └── scripts/ (organized subdirectories) ✅
```

---

## ⏱️ Timeline

| Phase | Duration | Description |
|-------|----------|-------------|
| **Preparation** | 5 min | Backup, review plan |
| **Execution** | 10 min | Move files, update refs |
| **Validation** | 5 min | Run tests, verify links |
| **Total** | 20 min | End-to-end |

---

## ✅ Success Criteria

- [ ] Only 3 .md files remain in root (README, CHANGELOG, CONTRIBUTING)
- [ ] All moved files have proper YAML frontmatter
- [ ] All cross-references updated
- [ ] Pre-commit hooks pass
- [ ] Metadata validation passes
- [ ] No broken links
- [ ] Documentation index up to date

---

## 📚 Related Documents

- `specs/governance/DOCUMENTATION_GOVERNANCE.md` - Governance rules
- `specs/templates/document-metadata.md` - Metadata pattern
- `docs/INDEX.md` - Documentation index
- `.pre-commit-config.yaml` - Pre-commit hooks

---

**Ready to Execute**: Yes
**Approval Required**: No (internal reorganization)
**Risk Assessment**: Low (Git-tracked, reversible)
