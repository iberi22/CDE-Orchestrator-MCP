# CDE MCP Dogfooding & Tool Feedback Plan

> **Status**: Ready to Execute ✅
> **Created**: 2025-11-24
> **Purpose**: Use CDE MCP on itself to gather comprehensive feedback and validate Spec-Kit conformity

---

## 🎯 What is This?

This is a **meta-development exercise**: we're using the CDE MCP tools on the CDE MCP project itself to:

1. ✅ **Test all 27 tools** with realistic scenarios
2. ✅ **Validate Spec-Kit conformity** (compare our templates vs GitHub's standard)
3. ✅ **Gather structured feedback** for UX improvements
4. ✅ **Document tool interactions** (dependencies, workflows)
5. ✅ **Measure token efficiency** (progressive disclosure benefits)

---

## 📂 What's in This Directory?

```
specs/cde-dogfooding-feedback/
├── README.md                        # This file (overview)
├── QUICKSTART.md                    # 5-minute quick start guide ⚡
├── TASK_PRIORITY_INDEX.md           # Prioritized task breakdown
├── spec.md                          # Full specification (user stories, requirements)
├── plan.md                          # Technical implementation plan
├── tasks.md                         # 67 executable tasks (tool-by-tool testing)
├── feedback-schema.json             # JSON schema for structured feedback
├── implementation/                  # Implementation resources
│   ├── IMPLEMENTATION_GUIDE.md     # Detailed step-by-step guide
│   ├── logs/                       # Session logs (created during execution)
│   └── screenshots/                # Error screenshots, visual artifacts
├── templates/                       # Feedback templates
│   ├── feedback-template.json      # Structured feedback form
│   ├── session-log-template.md     # Session logging template
│   └── professional-feedback-report-template.md
└── results/                         # Test results (created during execution)
    ├── tool-results.json           # Aggregated feedback
    ├── spec-kit-compliance.json    # Conformity validation
    └── summary-report.md           # Executive summary
```

---

## 🚀 Quick Start

### ⚡ 5-Minute Start (Recommended)

**See**: `QUICKSTART.md` for the fastest way to begin!

```powershell
# 1. Create branch
git checkout -b dogfooding-feedback

# 2. Verify MCP server (green status in VS Code)

# 3. Test first tool
cde_healthCheck()

# 4. Copy session template and start!
$session = "session-1-$(Get-Date -Format 'yyyy-MM-dd-HHmm')"
Copy-Item "specs\cde-dogfooding-feedback\templates\session-log-template.md" `
          "specs\cde-dogfooding-feedback\implementation\logs\$session.md"
```

**Then**: Open `tasks.md` and begin with T001!

---

### 📖 Comprehensive Start

**See**: `implementation/IMPLEMENTATION_GUIDE.md` for complete instructions

1. **Pre-Execution Checklist** - Verify environment
2. **Phase-by-Phase Execution** - Detailed workflow
3. **Feedback Collection** - Structured templates
4. **Troubleshooting** - Common issues solved
5. **Progress Tracking** - Stay organized

---

### 🎯 Automated (Using CDE MCP)

```python
# Use CDE to manage the dogfooding workflow
cde_startFeature(
    user_prompt="Execute dogfooding feedback plan for all CDE MCP tools",
    workflow_type="standard",
    project_path="."
)
```

---

## 📋 Execution Phases

| Phase | Tasks | Duration | Purpose |
|-------|-------|----------|---------|
| **1. Setup** | T001-T008 | 30 min | Prepare environment |
| **2. Health & Discovery** | T009-T013 | 30 min | Test foundational tools |
| **3. Documentation** | T014-T018 | 45 min | Test scanning & analysis |
| **4. Recipe & Skills** | T019-T024 | 45 min | Test skill sourcing |
| **5. Workflow** | T025-T033 | 60 min | Test orchestration |
| **6. Agent Delegation** | T034-T042 | 90 min | Test agent selection |
| **7. Onboarding** | T043-T045 | 30 min | Test project analysis |
| **8. Advanced** | T046-T048 | 45 min | Test specialized tools |
| **9. Validation** | T049-T051 | 30 min | Spec-Kit conformity check |
| **10. Reporting** | T052-T060 | 60 min | Generate feedback reports |
| **11. Cleanup** | T061-T067 | 30 min | Documentation & merge |
| **TOTAL** | 67 tasks | **6-7 hours** | Full dogfooding cycle |

---

## 🔧 Tools to Test (27 Total)

### Orchestration (5 tools)
- `cde_selectWorkflow` - Workflow recommendation
- `cde_sourceSkill` - Skill sourcing
- `cde_updateSkill` - Skill updating
- `cde_startFeature` - Feature initialization
- `cde_submitWork` - Phase submission

### Documentation (3 tools)
- `cde_scanDocumentation` - Doc scanning
- `cde_analyzeDocumentation` - Quality analysis
- `cde_createSpecification` - Spec generation

### Agents (4 tools)
- `cde_listAvailableAgents` - Agent discovery
- `cde_selectAgent` - Agent selection
- `cde_executeWithBestAgent` - Best agent execution
- `cde_delegateToJules` - Jules-specific delegation

### CEO Orchestration (5 tools)
- `cde_delegateTask` - Task delegation
- `cde_getTaskStatus` - Status tracking
- `cde_listActiveTasks` - Active task list
- `cde_getWorkerStats` - Worker statistics
- `cde_cancelTask` - Task cancellation

### Onboarding (3 tools)
- `cde_onboardingProject` - Project analysis
- `cde_setupProject` - Config generation
- `cde_publishOnboarding` - Doc publishing

### Recipes (2 tools)
- `cde_downloadRecipes` - Recipe downloads
- `cde_checkRecipes` - Recipe verification

### Extensions (1 tool)
- `cde_installMcpExtension` - Extension installer

### Health (1 tool)
- `cde_healthCheck` - System health check

### Full Implementation (1 tool)
- `cde_executeFullImplementation` - Full workflow execution

### Utilities (2 tools)
- `cde_searchTools` - Tool discovery
- `cde_testProgressReporting` - Progress testing

---

## 📊 Success Metrics

- ✅ **Tool Coverage**: 27/27 tools tested (100%)
- ✅ **Spec-Kit Conformity**: 95%+ template compliance
- ✅ **Bug Discovery**: 10+ actionable issues
- ✅ **Documentation Gaps**: 20+ examples/clarifications
- ✅ **UX Improvements**: 15+ enhancements proposed
- ✅ **Token Efficiency**: 90%+ reduction (progressive disclosure)

---

## 🎓 Key Learnings Expected

### 1. Spec-Kit Conformity
Compare CDE templates vs GitHub Spec-Kit:
- YAML frontmatter alignment
- Section structure matching
- Naming convention consistency
- Task organization patterns

### 2. Tool Interactions
Document how tools depend on each other:
- `cde_selectWorkflow` → `cde_startFeature` → `cde_submitWork`
- `cde_downloadRecipes` before using workflow
- `cde_sourceSkill` for knowledge gaps

### 3. UX Patterns
Identify common pain points:
- Unclear error messages
- Missing examples
- Confusing parameter names
- Incomplete documentation

### 4. Token Efficiency
Measure progressive disclosure benefits:
- `detail_level="name_only"` vs `"full"`
- 90%+ token reduction expected
- Demonstrate Anthropic best practices

---

## 📝 Feedback Collection

### Structured Format (JSON)

Every tool test must produce feedback matching `feedback-schema.json`:

```json
{
  "tool_name": "cde_selectWorkflow",
  "category": "orchestration",
  "test_date": "2025-11-24T10:30:00Z",
  "result": "success",
  "feedback": {
    "usability": {"rating": 4, "comments": "..."},
    "accuracy": {"rating": 5, "comments": "..."},
    "performance": {"duration_ms": 1250},
    "documentation": {"rating": 3, "comments": "..."},
    "improvement_suggestions": ["..."]
  }
}
```

### Rating Scale

- **5/5**: Excellent - No improvements needed
- **4/5**: Good - Minor improvements helpful
- **3/5**: Adequate - Several improvements needed
- **2/5**: Poor - Major issues present
- **1/5**: Unusable - Requires redesign

---

## 🐛 Bug Reporting

When bugs are found:

1. **Document in feedback**:
   ```json
   "errors_encountered": [{
     "error_type": "ValueError",
     "message": "Invalid workflow_type: 'unknown'",
     "reproducible": true
   }]
   ```

2. **Create GitHub issue**:
   ```bash
   gh issue create \
       --title "Bug: cde_selectWorkflow fails with unknown workflow_type" \
       --body "See feedback: agent-docs/execution/feedback-orchestration-tools-2025-11-24.md" \
       --label bug
   ```

3. **Link in feedback**:
   ```json
   "follow_up_actions": [{
     "action": "Fix ValueError handling",
     "priority": "high",
     "github_issue": "https://github.com/user/repo/issues/123"
   }]
   ```

---

## 📈 Progress Tracking

Use `tasks.md` as your checklist. Mark tasks as complete:

```markdown
- [x] T001 Create feature branch `dogfooding-feedback` from main
- [x] T002 [P] Verify CDE MCP server is running in VS Code
- [ ] T003 [P] Create `specs/cde-dogfooding-feedback/feedback-schema.json`
```

Or use CDE's workflow system:

```python
cde_submitWork(
    feature_id="<uuid>",
    phase_id="implement",
    results={"completed_tasks": ["T001", "T002", "T009", "T010"]}
)
```

---

## 📚 Documentation Index

### 🚀 Getting Started
- **QUICKSTART.md** - 5-minute guide to first test ⚡
- **TASK_PRIORITY_INDEX.md** - Prioritized task breakdown
- **implementation/IMPLEMENTATION_GUIDE.md** - Complete step-by-step guide

### 📋 Planning Documents
- **spec.md** - User stories, requirements, success metrics
- **plan.md** - Technical architecture, validation strategy
- **tasks.md** - 67 executable tasks organized by phase

### 📝 Templates
- **templates/feedback-template.json** - Structured feedback form
- **templates/session-log-template.md** - Session documentation
- **templates/professional-feedback-report-template.md** - Final reports

### 🔗 Related Documents

**Internal**:
- **Governance**: `specs/governance/DOCUMENTATION_GOVERNANCE.md`
- **Architecture**: `specs/design/architecture/README.md`
- **Roadmap**: `specs/tasks/improvement-roadmap.md`
- **Constitution**: `memory/constitution.md`
- **Agent Instructions**: `AGENTS.md`, `.github/copilot-instructions.md`

**External**:
- **Spec-Kit**: https://github.com/github/spec-kit
- **Spec-Kit Docs**: https://github.github.io/spec-kit/
- **MCP Protocol**: https://modelcontextprotocol.io/
- **FastMCP**: https://github.com/jlowin/fastmcp
- **Anthropic MCP**: https://www.anthropic.com/engineering/code-execution-with-mcp

---

## 💡 Tips for Success

1. **Start Small**: Test foundational tools first (health, search, recipes)
2. **Parallelize**: Run [P] marked tasks simultaneously to save time
3. **Document Everything**: Structured feedback is more valuable than ad-hoc notes
4. **Test Edge Cases**: Don't just test happy path - try invalid inputs
5. **Measure Performance**: Track execution time and memory usage
6. **Create Issues**: File bugs and improvements as you find them
7. **Stay Organized**: Keep feedback in category-specific files

---

## 🤝 Contributing

Found issues during dogfooding? Great! Here's how to contribute:

1. **File Issues**: Use GitHub issues for bugs and enhancements
2. **Update Docs**: Fix documentation gaps with PRs
3. **Share Feedback**: Add to feedback reports in `agent-docs/execution/`
4. **Improve Templates**: Submit PRs for Spec-Kit conformity fixes

---

## 📞 Questions?

- **GitHub Issues**: https://github.com/iberi22/CDE-Orchestrator-MCP/issues
- **Discussions**: https://github.com/iberi22/CDE-Orchestrator-MCP/discussions
- **Documentation**: See `docs/` and `specs/` directories

---

## 🎉 Let's Get Started!

Ready to dogfood? Pick one:

### Path 1: Automated (Recommended)
```python
cde_startFeature(
    user_prompt="Execute dogfooding feedback plan",
    workflow_type="standard"
)
```

### Path 2: Manual
```bash
git checkout -b dogfooding-feedback
code specs/cde-dogfooding-feedback/tasks.md
# Start with T001!
```

**Happy dogfooding! 🐕🍲**
