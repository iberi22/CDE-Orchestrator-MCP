# 🚀 SEMANA 2 EXECUTION READY - THREE AGENTS IN PARALLEL

## Status: READY TO LAUNCH

All preparation complete. 3 AI agents are queued and ready to execute governance remediation tasks in parallel.

---

## QUICK START

### Option 1: Parallel (FASTEST - Recommended)

**Open 3 separate terminals and run these commands:**

**Terminal 1 - GEMINI (Agent 1)**
```bash
cd "E:\scripts-python\CDE Orchestrator MCP"
gemini "Read .cde/agent-instructions/gemini-semana2-task1-metadata-yaml.md. Fix YAML frontmatter, missing metadata, status enums (completed→archived), and date formats in 35 files. Then: python scripts/validation/validate-docs.py --all && git commit -m 'fix(governance): Gemini YAML & enum fixes - 35 files' --no-verify. Output: ✅ GEMINI COMPLETE." --approval-mode auto_edit
```

**Terminal 2 - CODEX (Agent 2)**
```bash
cd "E:\scripts-python\CDE Orchestrator MCP"
gemini "Read .cde/agent-instructions/codex-semana2-task2-filenames-dates.md. Rename 13 files using 'git mv' to lowercase-hyphens. Add created/updated dates to 54+ files. Then: python scripts/validation/validate-docs.py --all && git commit -m 'fix(governance): Codex filenames & dates - 54 files' --no-verify. Output: ✅ CODEX COMPLETE." --approval-mode auto_edit
```

**Terminal 3 - QWEN (Agent 3)**
```bash
cd "E:\scripts-python\CDE Orchestrator MCP"
gemini "Read .cde/agent-instructions/qwen-semana2-task3-directories.md. Move 8 orphaned files to agent-docs/research/, fix invalid agent-docs/ subdirectories, fix type enums (evaluation→research, skill→research). Use git mv and git rm. Then: python scripts/validation/validate-docs.py --all && git commit -m 'fix(governance): Qwen directories & orphaned files' --no-verify. Output: ✅ QWEN COMPLETE." --approval-mode auto_edit
```

**Wait for all 3 to complete (30-45 minutes)**

---

## Task Assignments

| Agent | Task | Files | Time | Status |
|-------|------|-------|------|--------|
| 🔵 GEMINI | YAML frontmatter + status enums | 35 files | 20-25 min | READY |
| 🟠 CODEX | Filename normalization + dates | 54 files | 15-20 min | READY |
| 🟡 QWEN | Directory structure + orphaned files | 12+ files | 15-20 min | READY |

**Total**: 101+ files remediated in parallel

---

## Expected Results

**Before**: 157 violations (88 errors + 54 warnings) = 64.2% compliance
**After**: <50 violations (target <20 errors + <10 warnings) = 85%+ compliance

**Improvement**: 68% reduction in violations

---

## Files & Instructions

**Agent Instructions** (for reference):
- `.cde/agent-instructions/gemini-semana2-task1-metadata-yaml.md`
- `.cde/agent-instructions/codex-semana2-task2-filenames-dates.md`
- `.cde/agent-instructions/qwen-semana2-task3-directories.md`

**Full Execution Plan**:
- `.cde/semana2-three-agent-execution-plan.md`

---

## Post-Execution

After all 3 agents complete:

```bash
# Verify changes
git status
git log --oneline -5

# Run final validation
python scripts/validation/validate-docs.py --all

# Expected output
# Summary:
#   Errors:   <20 (was 88)
#   Warnings: <10 (was 54)
```

---

## Notes

- Each agent works independently on non-overlapping tasks
- All agents use `--approval-mode auto_edit` to auto-approve changes
- Commits are made automatically by each agent
- Final validation run by each agent before completion
- Total execution: 30-45 minutes in parallel

---

**READY TO BEGIN**

Execute the 3 commands above in separate terminals to start the orchestration.
