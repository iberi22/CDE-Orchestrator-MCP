---
title: "QWEN TASK 3: Fix Directory Structure & Move Orphaned Files"
description: "Qwen moves 12+ orphaned files from wrong directories to agent-docs/research/"
type: "task"
status: "active"
created: "2025-11-07"
updated: "2025-11-07"
author: "CDE-Orchestrator-MCP"
priority: "HIGH"
assigned_to: "qwen"
llm_summary: "Move orphaned .md files from .amazonq, .copilot, .jules, scripts, specs/api to agent-docs/research/ and fix subdirectory structure"
---

## OBJECTIVE

**Agent**: Qwen
**Task**: Directory structure corrections + move orphaned files
**Files Affected**: 12+ files
**Estimated Time**: 15-20 minutes
**Complexity**: Medium

---

## PART 1: Move Orphaned Files to agent-docs/research/ (8 files)

Problem: Files in .amazonq/, .copilot/, .jules/ are in unknown directories. Must move to agent-docs/research/

Files to move:

1. `.amazonq/rules/memory-bank/product.md` → `agent-docs/research/archived-2025-11-07/amazonq-rules/memory-bank/product.md`
2. `.amazonq/rules/memory-bank/structure.md` → `agent-docs/research/archived-2025-11-07/amazonq-rules/memory-bank/structure.md`
3. `.amazonq/rules/memory-bank/tech.md` → `agent-docs/research/archived-2025-11-07/amazonq-rules/memory-bank/tech.md`
4. `.amazonq/rules/rulegeneral.md` → `agent-docs/research/archived-2025-11-07/amazonq-rules/rulegeneral.md`
5. `.copilot/skills/parallel-ai-research.md` → `agent-docs/research/archived-2025-11-07/copilot-skills/parallel-ai-research.md`
6. `.jules/README.md` → `agent-docs/research/archived-2025-11-07/jules-config/readme.md`
7. `.pytest_cache/README.md` → DELETE (cache, not documentation)
8. `scripts/readme.md` → `specs/readme.md` (specs-related)

Command pattern (git mv for history):

```powershell
cd "E:\scripts-python\CDE Orchestrator MCP"

# Move files (create directories if needed)
git mv ".amazonq/rules/memory-bank/product.md" "agent-docs/research/archived-2025-11-07/amazonq-rules/memory-bank/product.md"
git mv ".amazonq/rules/memory-bank/structure.md" "agent-docs/research/archived-2025-11-07/amazonq-rules/memory-bank/structure.md"
git mv ".amazonq/rules/memory-bank/tech.md" "agent-docs/research/archived-2025-11-07/amazonq-rules/memory-bank/tech.md"
git mv ".amazonq/rules/rulegeneral.md" "agent-docs/research/archived-2025-11-07/amazonq-rules/rulegeneral.md"
git mv ".copilot/skills/parallel-ai-research.md" "agent-docs/research/archived-2025-11-07/copilot-skills/parallel-ai-research.md"
git mv ".jules/README.md" "agent-docs/research/archived-2025-11-07/jules-config/readme.md"
git rm ".pytest_cache/README.md"

# Then commit
git commit -m "fix(governance): Qwen move orphaned files to agent-docs/research - 8 files"
```

---

## PART 2: Fix Invalid Subdirectory Names (6 files)

Problem: agent-docs/ has invalid subdirectories. Only allowed: execution, sessions, feedback, research

Files in wrong subdirectories:

1. `agent-docs/evaluation/` → MOVE to `agent-docs/research/archived-2025-11-07/evaluation-docs/`
2. `agent-docs/prompts/` → MOVE to `agent-docs/research/archived-2025-11-07/prompts-docs/`
3. `agent-docs/readme.md` → DELETE (not in allowed subdirectory)
4. `agent-docs/roadmap/` → MOVE to `specs/tasks/`
5. `agent-docs/tasks/` → MOVE to `specs/tasks/`

Command pattern:

```powershell
# Move evaluation files
git mv "agent-docs/evaluation/" "agent-docs/research/archived-2025-11-07/evaluation-docs/"

# Move prompts files
git mv "agent-docs/prompts/" "agent-docs/research/archived-2025-11-07/prompts-docs/"

# Delete readme at root of agent-docs
git rm "agent-docs/readme.md"

# Move roadmap
git mv "agent-docs/roadmap/" "specs/tasks/roadmap/"

# Move tasks
git mv "agent-docs/tasks/" "specs/tasks/old-tasks/"

# Then commit
git commit -m "fix(governance): Qwen reorganize agent-docs subdirectories - move invalid subdirs"
```

---

## PART 3: Fix Type Enums (3 files)

Problem: Files have invalid type values. Only allowed types: design, execution, feature, feedback, governance, guide, research, session, task

Files with wrong types:

1. `agent-docs/research/archived-2025-11-07/evaluation-docs/evaluation-pr4-jules-implementation-2025-01.md`
   - Change: `type: evaluation` → `type: research`

2. `agent-docs/research/archived-2025-11-07/specs-templates-docs/skill.md`
   - Change: `type: skill` → `type: research`

3. `agent-docs/research/archived-2025-11-07/specs-templates-docs/skill_template.md`
   - Change: `type: skill` → `type: research`

Command:

```bash
sed -i 's/type: evaluation/type: research/g' <files>
sed -i 's/type: skill/type: research/g' <files>
```

---

## PART 4: Delete Cache/Temporary Directories

Remove non-documentation directories:

```powershell
# These are cache/temporary, not documentation
git rm -r ".pytest_cache"
git rm -r "htmlcov"
git rm -r "mcp-monitor"
# (only if they contain .md files or are completely empty)
```

---

## SUCCESS CRITERIA

- [ ] All 8 orphaned files moved to agent-docs/research/archived-2025-11-07/
- [ ] All invalid agent-docs/ subdirectories reorganized
- [ ] All type enums changed to valid values (evaluation→research, skill→research)
- [ ] Validation command shows fewer errors:

```bash
python scripts/validation/validate-docs.py --all 2>&1 | grep -E "Summary:|Errors:|Warnings:"
# Expected: Errors reduced significantly
```

Commit message:

```
fix(governance): Qwen reorganize directory structure & move orphaned files

- Moved 8 orphaned files from .amazonq, .copilot, .jules to agent-docs/research/
- Reorganized invalid agent-docs/ subdirectories (evaluation, prompts, roadmap, tasks)
- Fixed 3 invalid type enums (evaluation→research, skill→research)
- Removed cache directories
```

Then output: `✅ QWEN TASK 3 COMPLETE`

---

**Parallel**: Can start AFTER Gemini/Codex start (NOT dependent on completion)
**Status**: READY FOR EXECUTION
**Priority**: 🟡 HIGH
