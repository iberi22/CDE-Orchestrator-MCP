---
title: "Semana 2 Delegation to Jules"
description: "Delegation brief for Week 2 metadata and naming normalization tasks"
type: "execution"
status: "active"
created: "2025-11-07"
updated: "2025-11-07"
author: "GitHub Copilot"
---

# Semana 2 Delegation Brief for Jules AI

## 🎯 Overall Objective

Improve documentation governance compliance from 88 errors → <20 errors by:
1. Adding YAML metadata to 160+ files
2. Fixing metadata enums and dates
3. Normalizing filename conventions (UPPERCASE → lowercase)

---

## Task 1: Add YAML Metadata to Critical Files (HIGH PRIORITY)

**Target**: 160+ files without YAML frontmatter
**Effort**: 3-4 hours
**Priority**: 🔴 HIGH

### Subtask 1A: Large Files (>500 lines)
- AGENTS.md
- GEMINI.md
- specs/design/ARCHITECTURE.md
- specs/design/dynamic-skill-system.md

**Action**: Add YAML frontmatter with:
```yaml
---
title: "Document Title"
description: "One-sentence (50-150 chars)"
type: "feature|design|guide|governance"
status: "active|archived|deprecated|draft"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "Agent/Developer Name"
---
```

### Subtask 1B: Files in agent-docs/ (160+ remaining)
- agent-docs/execution/*.md (30+ files)
- agent-docs/sessions/*.md (15+ files)
- agent-docs/feedback/*.md (8+ files)
- agent-docs/research/*.md (5+ files)

**Action**: Batch add metadata with automation

### Subtask 1C: Generate llm_summary Fields
- Use file content to generate 2-3 sentence LLM-optimized summaries
- Critical for token optimization

---

## Task 2: Fix Metadata Errors (HIGH PRIORITY)

**Current Issues**: 88 errors blocking commits
**Effort**: 2-3 hours
**Priority**: 🔴 HIGH

### Subtask 2A: Fix Invalid Status Enums
```
WRONG: status: "completed"
RIGHT: status: "archived"

WRONG: status: "ready"
RIGHT: status: "active"

WRONG: status: "in-progress"
RIGHT: status: "draft"
```

Affected files: 25+ execution/session files

### Subtask 2B: Fix Date Formats
```
WRONG: "2025-11-05T20:45:00Z" (ISO 8601)
RIGHT: "2025-11-05" (YYYY-MM-DD)
```

Affected files: 10+ files in agent-docs/

### Subtask 2C: Fix Missing Required Fields
- created, updated, type, status, description
- Scan all .md files in agent-docs/, specs/, docs/

---

## Task 3: Normalize Filename Conventions (MEDIUM PRIORITY)

**Current Issues**: 66 warnings
**Effort**: 1-2 hours
**Priority**: 🟡 MEDIUM

### Rules
```
WRONG: ARCHITECTURE.md
RIGHT: architecture.md

WRONG: EXECUTIVE_SUMMARY.md
RIGHT: executive-summary.md

WRONG: SESSION_SUMMARY_V2_REVISION.md
RIGHT: session-summary-v2-revision.md
```

### Affected Directories
- specs/design/ (8 files)
- specs/governance/ (3 files)
- specs/templates/ (3 files)
- docs/ (20+ files)
- specs/ root (5+ files)

### Process
1. Use `git mv` to preserve history
2. Update all internal links
3. Verify no broken references

---

## 📊 Success Criteria

### Completion Metrics
- [ ] 160+ files have valid YAML frontmatter
- [ ] All dates in YYYY-MM-DD format
- [ ] All status values in [active, archived, deprecated, draft]
- [ ] llm_summary generated for files >500 lines
- [ ] All filenames lowercase-hyphens pattern
- [ ] Governance violations: <20 errors
- [ ] Pre-commit validation passes
- [ ] All commits successful

### Testing
```bash
# After completion:
python scripts/validation/validate-docs.py --all
# Expected: <20 errors, <10 warnings
```

---

## 🔗 Reference Files

- **Governance Rules**: specs/governance/DOCUMENTATION_GOVERNANCE.md
- **Metadata Template**: specs/templates/document-metadata.md
- **Pre-commit Config**: .pre-commit-config.yaml
- **Validation Script**: scripts/validation/validate-docs.py

---

## 💾 Automation Scripts to Create/Use

### Option 1: Batch Metadata Addition
```bash
python scripts/metadata/add-metadata.py --batch --directory agent-docs/
```

### Option 2: Filename Normalization
```bash
python scripts/refactor/normalize-filenames.py --dry-run
python scripts/refactor/normalize-filenames.py --apply
```

### Option 3: Fix Enum Values
```bash
python scripts/metadata/fix-enums.py --status-enum active,archived,deprecated,draft
```

---

## 📋 Suggested Execution Order

1. **Phase 1** (1-2h): Add YAML to critical files (AGENTS.md, GEMINI.md, ARCHITECTURE.md)
2. **Phase 2** (1-2h): Batch add metadata to agent-docs/ (160+ files)
3. **Phase 3** (1h): Fix enums (status, dates)
4. **Phase 4** (1-2h): Normalize filenames
5. **Phase 5** (30m): Validate and commit

---

## 🚀 Estimated Impact

- **Tokens Saved**: 56,000 tokens/month = $1.68-$37.5K/month
- **Errors Reduced**: 88 → <20 (77% improvement)
- **Compliance Score**: Current 54.8/100 → 85+/100
- **LLM Context Quality**: Significantly improved

---

## 📞 Contact/Status Updates

Report progress after each major phase. Use commit messages in format:
```
feat(metadata): Add YAML to [N] files in [directory]
- Added [count] files with frontmatter
- Fixed [count] enum violations
- Generated [count] llm_summaries

Score: [X] errors → [Y] errors
```

**Ready to Execute?** Use Jules CLI to start Phase 1 immediately.
