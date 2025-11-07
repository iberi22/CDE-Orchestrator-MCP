---
title: "CODEX TASK 2: Fix Filename Normalization & Dates"
description: "Codex fixes 28 filename violations and missing date fields"
type: "task"
status: "active"
created: "2025-11-07"
updated: "2025-11-07"
author: "CDE-Orchestrator-MCP"
priority: "HIGH"
assigned_to: "codex"
llm_summary: "Normalize 28 filenames (README.md→readme.md, SKILL.md→skill.md) and add YYYY-MM-DD dates to agent-docs files (54 warnings)"
---

## OBJECTIVE

**Agent**: Codex  
**Task**: Filename normalization + missing date fields in agent-docs/  
**Files Affected**: 28 files  
**Estimated Time**: 15-20 minutes  
**Complexity**: Low-Medium  

---

## PART 1: Fix Filename Case & Convention (19 files)

Problem: Filenames must be lowercase with hyphens (not UPPERCASE, not underscores)

Pattern: `LICENSE-DUAL.md` → `license-dual.md`, `README.md` → `readme.md`

Files to rename:

1. `docs/LICENSE-DUAL.md` → `docs/license-dual.md`
2. `mcp-status-bar/README.md` → `mcp-status-bar/readme.md`
3. `scripts/aws-setup/README-AIDER.md` → `scripts/aws-setup/readme-aider.md`
4. `scripts/aws-setup/README-CLOUDCODE.md` → `scripts/aws-setup/readme-cloudcode.md`
5. `scripts/readme.md` (already correct, just verify)
6. `specs/PYTHON_314_MIGRATION_SUMMARY.md` → `specs/python_314_migration_summary.md`
7. `specs/api/README.md` → `specs/api/readme.md`
8. `specs/api/mcp-tools.md` (verify exists in correct location)
9. `specs/templates/SKILL.md` → `specs/templates/skill.md`
10. `specs/templates/SKILL_TEMPLATE.md` → `specs/templates/skill_template.md`
11. `agent-docs/prompts/JULES_MASTER_PROMPT_PHASE3C.md` → `agent-docs/prompts/jules_master_prompt_phase3c.md`
12. `agent-docs/prompts/JULIUS_PHASE3C_QUICK_START.md` → `agent-docs/prompts/julius_phase3c_quick_start.md`
13. `agent-docs/research/archived-2025-11-07/jules-config/README.md` → `agent-docs/research/archived-2025-11-07/jules-config/readme.md`

Command to execute (git mv for history preservation):

```powershell
cd "E:\scripts-python\CDE Orchestrator MCP"

# Example for each:
git mv "docs/LICENSE-DUAL.md" "docs/license-dual.md"
git mv "mcp-status-bar/README.md" "mcp-status-bar/readme.md"
git mv "scripts/aws-setup/README-AIDER.md" "scripts/aws-setup/readme-aider.md"
git mv "scripts/aws-setup/README-CLOUDCODE.md" "scripts/aws-setup/readme-cloudcode.md"
git mv "specs/PYTHON_314_MIGRATION_SUMMARY.md" "specs/python_314_migration_summary.md"
git mv "specs/api/README.md" "specs/api/readme.md"
git mv "specs/templates/SKILL.md" "specs/templates/skill.md"
git mv "specs/templates/SKILL_TEMPLATE.md" "specs/templates/skill_template.md"
git mv "agent-docs/prompts/JULES_MASTER_PROMPT_PHASE3C.md" "agent-docs/prompts/jules_master_prompt_phase3c.md"
git mv "agent-docs/prompts/JULIUS_PHASE3C_QUICK_START.md" "agent-docs/prompts/julius_phase3c_quick_start.md"
git mv "agent-docs/research/archived-2025-11-07/jules-config/README.md" "agent-docs/research/archived-2025-11-07/jules-config/readme.md"

# Then commit
git commit -m "fix(governance): Codex filename normalization - 13 files to lowercase-hyphens"
```

---

## PART 2: Add Date Fields to Agent-Docs Files (54 warnings)

Problem: agent-docs/ subdirectories should have dates in filenames or frontmatter

Files missing dates in filename (add `created: "2025-11-07"` and `updated: "2025-11-07"` to frontmatter):

Example files:

- `agent-docs/execution/documentation-architecture-phase-1-2-complete.md`
- `agent-docs/execution/harcos_deployment_next_steps.md`
- `agent-docs/execution/harcos_deployment_package_index.md`
- `agent-docs/execution/harcos_quick_start.md`
- `agent-docs/execution/phase-3b-testing-completion.md`
- `agent-docs/execution/phase2c-enhanced-ui-jules-tasks.md`
- `agent-docs/execution/phase2c-jules-sessions.md`
- `agent-docs/execution/python-314-migration-report.md`
- `agent-docs/feedback/ai-assistant-config-review.md`
- `agent-docs/feedback/reviews-readme.md`
- Plus 40+ more in agent-docs/research/archived-2025-11-07/

Solution: Add date fields to YAML frontmatter

```yaml
created: "2025-11-07"
updated: "2025-11-07"
```

Command:

```bash
# For each file without date, add to frontmatter
# Pattern: After "author:" field, add date fields
```

---

## SUCCESS CRITERIA

- [ ] All 13 files renamed to lowercase-hyphens (git mv used for history)
- [ ] 54 agent-docs files have `created` and `updated` YYYY-MM-DD fields
- [ ] Validation command shows <30 warnings (down from 54):

```bash
python scripts/validation/validate-docs.py --all 2>&1 | grep "Warnings:"
```

Commit message:

```
fix(governance): Codex filename normalization & date fields - 54 files

- Normalized 13 filenames to lowercase-hyphens (LICENSE-DUAL→license-dual, etc)
- Added missing created/updated dates to 54 agent-docs files
- Reduces warnings: 54 → <10
```

Then output: `✅ CODEX TASK 2 COMPLETE`

---

**Parallel**: Can start AFTER Gemini starts (NOT dependent on Gemini completion)  
**Status**: READY FOR EXECUTION  
**Priority**: 🟡 HIGH
