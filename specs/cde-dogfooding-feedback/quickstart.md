---
title: "Quick Start Guide - CDE MCP Dogfooding"
description: "5-minute guide to start dogfooding CDE MCP immediately"
type: "quickstart"
status: "active"
created: "2025-11-24"
updated: "2025-11-24"
author: "CDE Orchestrator Team"
llm_summary: |
  Quick start guide for CDE MCP dogfooding. Get started in 5 minutes
  with essential setup and first tool tests. Perfect for jumping in quickly.
---

# Quick Start Guide - CDE MCP Dogfooding

> ⏱️ **Time to first test**: 5 minutes
> 🎯 **Goal**: Test your first CDE MCP tool and collect feedback

---

## 🚀 5-Minute Setup

### Step 1: Create Branch (30 seconds)

```powershell
cd "e:\scripts-python\CDE Orchestrator MCP"
git checkout -b dogfooding-feedback
```

### Step 2: Verify Environment (1 minute)

```powershell
# Check CDE MCP server is running
# Look for MCP status in VS Code status bar (should show green)

# Quick test
# In VS Code, use GitHub Copilot to run:
cde_healthCheck()
```

✅ If you see JSON output with health status, you're ready!

### Step 3: Copy Templates (30 seconds)

```powershell
# Session log for today
$session = "session-1-$(Get-Date -Format 'yyyy-MM-dd-HHmm')"
Copy-Item "specs\cde-dogfooding-feedback\templates\session-log-template.md" `
          "specs\cde-dogfooding-feedback\implementation\logs\$session.md"

# Open it
code "specs\cde-dogfooding-feedback\implementation\logs\$session.md"
```

### Step 4: Start Testing (3 minutes)

Open `specs\cde-dogfooding-feedback\tasks.md` and start with **T001**!

---

## 🎯 Your First Test: cde_healthCheck

### Execute the Tool

In VS Code, ask GitHub Copilot:

```
Use cde_healthCheck to check the system health
```

### Record Feedback

1. Copy `templates/feedback-template.json` to `results/cde-healthCheck-feedback.json`
2. Fill in these key fields:
   - `tool_name`: "cde_healthCheck"
   - `category`: "health"
   - `test_date`: Current timestamp
   - `result`: "success" | "partial" | "failure"
   - `feedback.usability.rating`: 1-5
   - `feedback.accuracy.rating`: 1-5
   - `feedback.performance.duration_ms`: Time it took
   - `feedback.documentation.rating`: 1-5

3. Add at least one improvement suggestion

### Mark Complete

In `tasks.md`, change:
```markdown
- [ ] T009 [P] [Health] Test cde_healthCheck
```
To:
```markdown
- [x] T009 [P] [Health] Test cde_healthCheck ✅
```

---

## 📋 Recommended Session 1 Tasks

**Duration**: 1.5 hours
**Tasks**: T001-T024

### Quick Wins (30 minutes)
- T009: `cde_healthCheck` ✅ (you just did this!)
- T010-T012: `cde_searchTools` (3 variants)
- T013: `cde_checkRecipes`

### Documentation Tools (45 minutes)
- T014-T016: `cde_scanDocumentation` (3 variants)
- T017: `cde_analyzeDocumentation`
- T018: `cde_createSpecification`

### Recipes & Skills (30 minutes)
- T019-T021: `cde_downloadRecipes` (3 scenarios)
- T022-T024: `cde_sourceSkill` and `cde_updateSkill`

---

## 💡 Pro Tips

### 1. Test Fast, Document Later
- Run tool first, observe behavior
- Take quick notes in session log
- Complete detailed feedback JSON after 3-5 tools

### 2. Use Parallel Tasks
Tasks marked `[P]` can run simultaneously:
```
T010 [P] cde_searchTools (name_only)
T011 [P] cde_searchTools (name_and_description)
T012 [P] cde_searchTools (full_schema)
```
Run all 3, compare results, document together.

### 3. Screenshot Errors
```powershell
# When you see an error, screenshot it
# Save to: specs\cde-dogfooding-feedback\implementation\screenshots\
# Name: [tool-name]-[issue]-[timestamp].png
```

### 4. Commit Frequently
```powershell
# After each phase
git add .
git commit -m "test: Complete Phase 2 - Health & Discovery tools"
```

---

## 🆘 Quick Troubleshooting

### Tool Won't Execute
**Problem**: Nothing happens when calling tool
**Solution**:
1. Check MCP server status in VS Code
2. Restart VS Code
3. Verify `.vscode/mcp.json` is configured

### "Module not found" Error
**Problem**: Import errors
**Solution**:
```powershell
$env:PYTHONPATH = "e:\scripts-python\CDE Orchestrator MCP"
```

### Can't Save Feedback
**Problem**: Permission errors
**Solution**:
```powershell
# Save to temp first
$temp = "$env:TEMP\feedback.json"
# Edit, then move
Move-Item $temp "specs\cde-dogfooding-feedback\results\tool-feedback.json"
```

---

## 📊 Track Your Progress

### Quick Progress Check

```powershell
# Count completed tasks
Select-String -Path "specs\cde-dogfooding-feedback\tasks.md" -Pattern "- \[x\]" | Measure-Object | Select-Object Count

# Count total tasks
Select-String -Path "specs\cde-dogfooding-feedback\tasks.md" -Pattern "- \[ \]" | Measure-Object | Select-Object Count
```

### Visual Progress

Update this in your session log:
```
Progress: [████████────────────] 40% (27/67 tasks)
```

---

## 🎓 Next Steps

After your first session:

1. **Review Feedback**: Check your JSON files validate
2. **Update Session Log**: Complete the session summary
3. **Plan Session 2**: Schedule next 2-hour block
4. **Share Progress**: Post update in team channel

---

## 📚 Full Documentation

- **Complete Guide**: `implementation/IMPLEMENTATION_GUIDE.md`
- **All Tasks**: `tasks.md` (67 tasks total)
- **Detailed Spec**: `spec.md` (user stories, requirements)
- **Technical Plan**: `plan.md` (architecture, validation)

---

## ✅ Checklist for Today

- [ ] Branch created: `dogfooding-feedback`
- [ ] MCP server verified running
- [ ] First tool tested: `cde_healthCheck`
- [ ] Feedback JSON created
- [ ] Session log started
- [ ] Progress tracked in `tasks.md`
- [ ] Changes committed to git

---

## 🎉 You're Ready!

**Time spent**: ~5 minutes setup
**Next**: Open `tasks.md` and continue with T010

**Remember**:
- Test systematically (follow task order)
- Document thoroughly (use templates)
- Commit frequently (after each phase)
- Take breaks (this is 6-7 hours of work)

**Good luck with your dogfooding! 🐕🍲**

---

## 📞 Need Help?

- **Implementation Guide**: `implementation/IMPLEMENTATION_GUIDE.md` (troubleshooting section)
- **GitHub Issues**: File bugs as you find them
- **Team Chat**: Ask questions in team channel

---

**Last Updated**: 2025-11-24
**Version**: 1.0
**Status**: Ready to Use ✅
