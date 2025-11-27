---
title: "CDE MCP Dogfooding - Implementation Guide"
description: "Step-by-step guide for executing the dogfooding feedback plan"
type: "implementation"
status: "active"
created: "2025-11-24"
updated: "2025-11-24"
author: "CDE Orchestrator Team"
llm_summary: |
  Practical implementation guide for dogfooding CDE MCP. Includes setup
  instructions, execution checklist, feedback collection procedures, and
  troubleshooting tips. Start here before executing tasks.md.
---

# CDE MCP Dogfooding - Implementation Guide

> **Status**: Ready for Execution ✅
> **Prerequisites**: CDE MCP server running, VS Code with MCP extension
> **Estimated Time**: 6-7 hours (can be split across multiple sessions)

---

## 🎯 Overview

This guide walks you through the practical execution of the dogfooding feedback plan. Follow these steps to test all 27 CDE MCP tools on the CDE project itself.

---

## 📋 Pre-Execution Checklist

### Environment Setup

- [ ] **VS Code** with MCP extension installed and configured
- [ ] **CDE MCP Server** running (check status in VS Code)
- [ ] **Git** installed and configured
- [ ] **GitHub CLI** (`gh`) installed (for issue creation)
- [ ] **Python 3.11+** available
- [ ] **Internet connection** (for skill sourcing, web research)

### Verify Installation

```powershell
# Check CDE MCP server is running
# In VS Code: Check MCP status in status bar

# Verify git
git --version

# Verify GitHub CLI
gh --version

# Verify Python
python --version

# Test a simple CDE tool
# In VS Code, use Copilot to call:
# cde_healthCheck()
```

### Create Feature Branch

```powershell
# Navigate to project root
cd "e:\scripts-python\CDE Orchestrator MCP"

# Create and checkout feature branch
git checkout -b dogfooding-feedback

# Verify branch
git branch --show-current
# Should output: dogfooding-feedback
```

---

## 📂 Directory Structure Setup

Create necessary directories for feedback collection:

```powershell
# Create results directories
New-Item -ItemType Directory -Force -Path "specs\cde-dogfooding-feedback\results"
New-Item -ItemType Directory -Force -Path "specs\cde-dogfooding-feedback\implementation\logs"
New-Item -ItemType Directory -Force -Path "specs\cde-dogfooding-feedback\implementation\screenshots"

# Create feedback output directories
New-Item -ItemType Directory -Force -Path "agent-docs\execution\dogfooding-2025-11-24"

# Verify structure
tree /F specs\cde-dogfooding-feedback
```

Expected structure:
```
specs\cde-dogfooding-feedback\
├── README.md
├── spec.md
├── plan.md
├── tasks.md
├── feedback-schema.json
├── implementation\
│   ├── IMPLEMENTATION_GUIDE.md (this file)
│   ├── logs\
│   └── screenshots\
├── results\
└── templates\
```

---

## 🚀 Execution Workflow

### Phase-by-Phase Execution

Execute tasks in order from `tasks.md`. Mark completed tasks with `[x]`.

#### Session 1: Foundation (1.5 hours)
**Tasks**: T001-T024 (Setup + Health + Documentation + Recipes)

```powershell
# Start session log
$session = "session-1-$(Get-Date -Format 'yyyy-MM-dd-HHmm')"
New-Item -ItemType File -Path "specs\cde-dogfooding-feedback\implementation\logs\$session.md"

# Execute tasks T001-T008 (Setup)
# Execute tasks T009-T013 (Health & Discovery)
# Execute tasks T014-T018 (Documentation)
# Execute tasks T019-T024 (Recipes & Skills)

# Record feedback after each tool test
# Use feedback template (see below)
```

#### Session 2: Orchestration (2 hours)
**Tasks**: T025-T033 (Workflow lifecycle)

```powershell
$session = "session-2-$(Get-Date -Format 'yyyy-MM-dd-HHmm')"
New-Item -ItemType File -Path "specs\cde-dogfooding-feedback\implementation\logs\$session.md"

# Execute tasks T025-T033
# Test workflow with different complexity levels
# Document phase transitions
```

#### Session 3: Agents (2 hours)
**Tasks**: T034-T042 (Agent delegation)

```powershell
$session = "session-3-$(Get-Date -Format 'yyyy-MM-dd-HHmm')"
New-Item -ItemType File -Path "specs\cde-dogfooding-feedback\implementation\logs\$session.md"

# Execute tasks T034-T042
# Test agent selection and delegation
# Monitor CEO orchestration
```

#### Session 4: Finalization (1.5 hours)
**Tasks**: T043-T067 (Onboarding + Advanced + Reporting)

```powershell
$session = "session-4-$(Get-Date -Format 'yyyy-MM-dd-HHmm')"
New-Item -ItemType File -Path "specs\cde-dogfooding-feedback\implementation\logs\$session.md"

# Execute tasks T043-T051 (Onboarding + Advanced + Validation)
# Execute tasks T052-T060 (Feedback aggregation)
# Execute tasks T061-T067 (Cleanup + PR)
```

---

## 📝 Feedback Collection Procedure

### For Each Tool Test

1. **Prepare Test Scenario**
   - Read tool docstring in `src/mcp_tools/*.py`
   - Identify realistic test scenario
   - Prepare input parameters

2. **Execute Tool**
   ```python
   # In VS Code, use GitHub Copilot to call tool
   # Example:
   result = cde_healthCheck()
   ```

3. **Record Observations**
   - Start timer before execution
   - Observe VS Code status bar (if progress reporting)
   - Note any errors or warnings
   - Check output validity

4. **Complete Feedback Form**
   - Copy template from `templates/feedback-template.json`
   - Fill in all required fields
   - Rate usability, accuracy, performance, documentation (1-5)
   - Add improvement suggestions

5. **Save Feedback**
   ```powershell
   # Save to results directory
   # Naming: tool-name-feedback.json
   # Example:
   Copy-Item "templates\feedback-template.json" "results\cde-healthCheck-feedback.json"
   # Edit the file with your feedback
   ```

6. **Take Screenshots (if needed)**
   - Capture interesting output
   - Document errors visually
   - Save to `implementation/screenshots/`

---

## 📊 Feedback Template Usage

### JSON Feedback Template

Location: `specs/cde-dogfooding-feedback/templates/feedback-template.json`

```json
{
  "tool_name": "cde_[toolname]",
  "category": "orchestration|documentation|agents|...",
  "test_date": "2025-11-24T10:30:00Z",
  "tested_by": "Your Name or AI Agent Name",
  "test_scenario": "Brief description of what you tested",
  "input": {
    "param1": "value1",
    "param2": "value2"
  },
  "expected_output": {
    "key": "expected value"
  },
  "actual_output": {
    "key": "actual value"
  },
  "result": "success|partial|failure",
  "feedback": {
    "usability": {
      "rating": 4,
      "comments": "Clear parameters, but could use more examples"
    },
    "accuracy": {
      "rating": 5,
      "comments": "Output matched expectations perfectly"
    },
    "performance": {
      "duration_ms": 1250,
      "memory_mb": 45,
      "comments": "Fast execution, reasonable memory usage"
    },
    "documentation": {
      "rating": 3,
      "comments": "Missing edge case examples",
      "missing_examples": [
        "How to handle empty project",
        "What happens with invalid paths"
      ]
    },
    "errors_encountered": [],
    "improvement_suggestions": [
      "Add parameter validation with clear error messages",
      "Include example output in docstring"
    ],
    "edge_cases_tested": [
      {
        "scenario": "Empty project directory",
        "result": "pass",
        "notes": "Handled gracefully with clear message"
      }
    ]
  },
  "dependencies": ["cde_checkRecipes"],
  "notes": "Additional observations..."
}
```

### Markdown Session Log Template

Location: `specs/cde-dogfooding-feedback/templates/session-log-template.md`

```markdown
# Dogfooding Session Log - [Date] [Session Number]

**Date**: 2025-11-24
**Session**: 1 of 4
**Duration**: [Start] - [End]
**Tasks Covered**: T001-T024

---

## Tools Tested

### Tool 1: cde_healthCheck
- **Time**: 10:30 AM
- **Duration**: 2.5 seconds
- **Result**: ✅ Success
- **Quick Notes**: All components healthy, clear status messages
- **Feedback File**: `results/cde-healthCheck-feedback.json`

### Tool 2: cde_searchTools
- **Time**: 10:35 AM
- **Duration**: 1.8 seconds
- **Result**: ✅ Success
- **Quick Notes**: Fast search, accurate results, good token efficiency
- **Feedback File**: `results/cde-searchTools-feedback.json`

[... continue for all tools in session ...]

---

## Session Summary

### Highlights
- ✅ 12 tools tested successfully
- 🐛 2 minor bugs discovered
- 💡 8 improvement suggestions documented

### Challenges
- Network timeout during skill sourcing (resolved with retry)
- Unclear error message from tool X (documented in feedback)

### Next Session Plan
- Continue with T025-T033 (Workflow orchestration)
- Address any blocking issues from this session

---

## Action Items
- [ ] File GitHub issue for bug in tool X
- [ ] Update documentation for tool Y
- [ ] Test edge case Z in next session
```

---

## 🔍 Quality Assurance Checklist

### Per Tool Test

- [ ] **Input parameters** validated and documented
- [ ] **Expected output** defined before execution
- [ ] **Actual output** recorded accurately
- [ ] **Execution time** measured (in milliseconds)
- [ ] **Memory usage** noted (if significant)
- [ ] **Errors** captured with stack traces (if any)
- [ ] **Edge cases** tested (at least 2 per tool)
- [ ] **Ratings** provided for all 4 categories (1-5)
- [ ] **Improvement suggestions** specific and actionable
- [ ] **Screenshots** taken (if visual issues)
- [ ] **Feedback JSON** validates against schema

### Per Session

- [ ] **Session log** created and maintained
- [ ] **All feedback files** saved to `results/`
- [ ] **Git commits** made with clear messages
- [ ] **Progress** tracked in `tasks.md` (mark [x])
- [ ] **Blockers** documented and escalated if needed
- [ ] **Next session** plan documented

### Per Phase

- [ ] **Phase summary** documented in session log
- [ ] **Key findings** highlighted
- [ ] **GitHub issues** created for critical bugs
- [ ] **Checkpoint** verified (can pause and resume)

---

## 🐛 Troubleshooting Guide

### Common Issues

#### Issue: MCP Server Not Responding
**Symptoms**: Tools don't execute, timeout errors
**Solution**:
```powershell
# Restart VS Code
# Check MCP server logs
# Verify .vscode/mcp.json configuration
```

#### Issue: Tool Execution Fails with ImportError
**Symptoms**: "Module not found" or "Cannot import"
**Solution**:
```powershell
# Verify Python environment
python -c "from src.mcp_tools.health import cde_healthCheck; print('OK')"

# If fails, check PYTHONPATH
$env:PYTHONPATH = "e:\scripts-python\CDE Orchestrator MCP"
```

#### Issue: Network Timeout During Skill Sourcing
**Symptoms**: `cde_sourceSkill` or `cde_updateSkill` timeout
**Solution**:
- Check internet connection
- Retry with increased timeout (if parameter available)
- Document issue in feedback
- Continue with other tools, return later

#### Issue: Can't Save Feedback JSON
**Symptoms**: Permission errors, file locked
**Solution**:
```powershell
# Check file permissions
Get-Acl "specs\cde-dogfooding-feedback\results"

# Close any open editors on the file
# Save to temp location first, then move
```

#### Issue: Tool Modifies Production Code Unexpectedly
**Symptoms**: Uncommitted changes in src/
**Solution**:
```powershell
# Immediately stash changes
git stash

# Document the behavior in feedback
# Mark tool as "high risk" in feedback
# Add to edge_cases_tested with result: "unexpected"
```

---

## 📈 Progress Tracking

### Task Completion Tracking

Use `tasks.md` as the single source of truth:

```markdown
- [x] T001 Create feature branch ✅
- [x] T002 Verify CDE MCP server running ✅
- [ ] T003 Create feedback schema ⏳
```

Update after each task completion.

### Visual Progress Indicator

Create a progress chart in your session log:

```
Phase Progress:
[████████████████████────────] 67% (45/67 tasks)

Current Phase: 6 - Agent Delegation
Tasks in Phase: 9
Completed: 6
Remaining: 3
```

### Time Tracking

Log start/end times for each session:

```
Session 1: 10:00 AM - 11:30 AM (1.5h)
Session 2: 2:00 PM - 4:00 PM (2h)
Session 3: [Scheduled for next day]
Session 4: [Scheduled for next day]

Total Time: 3.5h / 6-7h estimated
```

---

## 🎓 Best Practices

### 1. Test Systematically
- Follow task order in `tasks.md`
- Don't skip tasks (dependencies matter)
- Complete one phase before moving to next

### 2. Document Thoroughly
- Capture both successes and failures
- Be specific in improvement suggestions
- Include reproduction steps for bugs

### 3. Stay Objective
- Rate tools fairly (1-5 scale)
- Focus on UX from user perspective
- Separate bugs from design decisions

### 4. Maintain Context
- Reference related tools in feedback
- Note tool dependencies
- Track recurring issues across tools

### 5. Commit Frequently
```powershell
# After each phase
git add .
git commit -m "chore: Complete Phase [N] dogfooding tasks

- Tested tools: [list]
- Feedback collected: [count]
- Issues found: [count]"
```

### 6. Take Breaks
- 6-7 hours is substantial
- Split across 2-3 days if needed
- Fresh perspective improves feedback quality

---

## 📊 Metrics to Track

### Quantitative Metrics

1. **Tool Success Rate**: `(successful tests / total tests) * 100`
2. **Average Execution Time**: Sum of all durations / tool count
3. **Bug Discovery Rate**: Bugs found / tools tested
4. **Documentation Gaps**: Missing examples / total tools
5. **Token Efficiency**: (baseline tokens - optimized tokens) / baseline tokens

### Qualitative Metrics

1. **Usability Score**: Average rating across all tools
2. **Documentation Quality**: Average doc rating
3. **Error Handling**: Quality of error messages
4. **Tool Discoverability**: Ease of finding right tool

Record these in `results/metrics-summary.json` at the end.

---

## 🎯 Success Criteria

### Minimum Requirements

- ✅ All 27 tools executed at least once
- ✅ Feedback collected for each tool (JSON format)
- ✅ At least 10 improvement suggestions documented
- ✅ Spec-Kit conformity validated (score calculated)
- ✅ Summary report generated

### Stretch Goals

- 🎯 95%+ Spec-Kit conformity score
- 🎯 20+ improvement suggestions
- 🎯 10+ GitHub issues created
- 🎯 Token efficiency demonstrated (90%+ reduction)
- 🎯 All edge cases tested

---

## 📝 Reporting Requirements

### Phase Reports (After Each Session)

Create brief summary in session log:
- Tools tested
- Time spent
- Issues found
- Next steps

### Final Report (After All Phases)

Generate comprehensive report:
1. **Executive Summary** (1 page)
2. **Tools Overview** (1 tool = 1 paragraph)
3. **Spec-Kit Conformity** (comparison table)
4. **Improvement Backlog** (prioritized list)
5. **Metrics Dashboard** (quantitative results)

Location: `agent-docs/execution/dogfooding-2025-11-24/summary-report.md`

---

## 🚀 Ready to Start?

### Pre-flight Checklist

- [ ] Environment verified
- [ ] Feature branch created
- [ ] Directories created
- [ ] Templates copied
- [ ] This guide read and understood
- [ ] Session 1 scheduled
- [ ] Feedback forms ready

### Launch Command

```powershell
# Start your first session!
cd "e:\scripts-python\CDE Orchestrator MCP"
git checkout dogfooding-feedback

# Open tasks.md and begin with T001
code specs\cde-dogfooding-feedback\tasks.md

# Open session log template
$session = "session-1-$(Get-Date -Format 'yyyy-MM-dd-HHmm')"
Copy-Item "specs\cde-dogfooding-feedback\templates\session-log-template.md" `
          "specs\cde-dogfooding-feedback\implementation\logs\$session.md"
code "specs\cde-dogfooding-feedback\implementation\logs\$session.md"
```

**Good luck! 🎉**

---

## 📞 Need Help?

- **Stuck on a task?** Check troubleshooting section above
- **Found a critical bug?** Document in feedback, file GitHub issue immediately
- **Question about process?** Refer to `plan.md` for technical details
- **Clarification on requirements?** Check `spec.md` for user stories

---

## 🔗 Quick Reference

- **Full Spec**: `specs/cde-dogfooding-feedback/spec.md`
- **Technical Plan**: `specs/cde-dogfooding-feedback/plan.md`
- **Task List**: `specs/cde-dogfooding-feedback/tasks.md`
- **Feedback Schema**: `specs/cde-dogfooding-feedback/feedback-schema.json`
- **This Guide**: `specs/cde-dogfooding-feedback/implementation/IMPLEMENTATION_GUIDE.md`

---

**Last Updated**: 2025-11-24
**Version**: 1.0
**Status**: Ready for Use ✅
