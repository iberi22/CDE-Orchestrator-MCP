---
title: "Tasks: CDE MCP Dogfooding & Tool Feedback"
description: "Executable task list for comprehensive tool testing and feedback collection"
type: "task"
status: "active"
created: "2025-11-24"
updated: "2025-11-24"
author: "CDE Orchestrator Team"
llm_summary: |
  Executable checklist for dogfooding CDE MCP. Organized by tool category
  (orchestration, documentation, agents, etc.). Each task tests a specific
  tool with realistic scenarios and collects structured feedback.
---

## Tasks: CDE MCP Dogfooding & Tool Feedback

**Input**: Design documents from `/specs/cde-dogfooding-feedback/`
**Prerequisites**: plan.md (required), spec.md (required), feedback-schema.json

**Organization**: Tasks grouped by tool category to enable independent testing

---

## Format: `[ID] [P?] [Category] Description`

- **[P]**: Can run in parallel (no dependencies)
- **[Category]**: Tool category (orchestration, docs, agents, etc.)
- Include exact file paths and expected outputs

---

## Phase 1: Setup & Preparation

**Purpose**: Prepare environment and validation infrastructure

- [x] T001 Create feature branch `dogfooding-feedback` from main
- [x] T002 [P] Verify CDE MCP server is running in VS Code
- [x] T003 [P] Create `specs/cde-dogfooding-feedback/feedback-schema.json`
- [x] T004 [P] Create `specs/cde-dogfooding-feedback/results/` directory
- [x] T005 Create `scripts/validate_spec_kit_conformity.py`
- [x] T006 [P] Create `scripts/estimate_token_usage.py`
- [x] T007 [P] Create `scripts/run_dogfooding_suite.py`
- [x] T008 Create `tests/integration/dogfooding/` directory structure

**Checkpoint**: Environment ready for tool testing

---

## Phase 2: Health & Discovery Tools (No Dependencies)

**Purpose**: Test foundational tools that don't depend on others

### T009 [x] [Health] Test cde_healthCheck

**Input**: None
**Expected Output**: JSON with Python, Rust, and external tool status
**Success Criteria**:
- Returns valid JSON

- Shows status for git, gh, python, rust
- Provides actionable error messages if dependencies missing

**Execution**:
```python
result = cde_healthCheck()
# Verify structure: {"python": {...}, "rust": {...}, "external_tools": {...}}
```

**Feedback Collection**:
- Document response time
- Rate usability (1-5)
- Note missing information
- Suggest improvements

---

### T010 [P] [Utility] Test cde_searchTools (name_only)

**Input**: `query="workflow", detail_level="name_only"`
**Expected Output**: List of tool names
**Success Criteria**:
- Returns ["cde_selectWorkflow", "cde_startFeature", "cde_submitWork"]
- Response < 2 seconds
- Token count < 200

**Execution**:
```python
result = cde_searchTools("workflow", detail_level="name_only")
```

**Feedback**: Token efficiency, discoverability, accuracy

---

### T011 [P] [Utility] Test cde_searchTools (name_and_description)

**Input**: `query="skill", detail_level="name_and_description"`
**Expected Output**: Tool names + descriptions + tags
**Success Criteria**:
- Includes descriptions and tags
- Token count ~500 (vs ~1000 for full_schema)

**Feedback**: Balance between detail and efficiency

---

### T012 [P] [Utility] Test cde_searchTools (full_schema)

**Input**: `query="scanDocumentation", detail_level="full_schema"`
**Expected Output**: Complete parameter schemas
**Success Criteria**:
- Shows all parameters with types and defaults
- Includes full docstring

**Feedback**: Schema completeness, documentation quality

---

### T013 [P] [Recipes] Test cde_checkRecipes

**Input**: `project_path="."`
**Expected Output**: Status of .cde/ directory
**Success Criteria**:
- Reports exists: true/false
- Shows path to .cde/ directory
- Indicates if download needed

**Execution**:
```python
result = cde_checkRecipes()
# Expected: {"exists": true/false, "path": "...", "needs_download": bool}
```

**Feedback**: Clear messaging, actionable next steps

---

## Phase 3: Documentation Tools

**Purpose**: Test documentation scanning and analysis

### T014 [Documentation] Test cde_scanDocumentation (name_only)

**Input**: `project_path=".", detail_level="name_only"`
**Expected Output**: List of .md file paths
**Success Criteria**:
- Lists all .md files in specs/, agent-docs/, etc.
- Token count ~1,000 for 100 files (10 tokens/file)
- Response < 5 seconds

**Execution**:
```python
result = cde_scanDocumentation(".", detail_level="name_only")
# Measure: token count, execution time, file count
```

**Feedback**: Performance on large repos (500+ files)

---

### T015 [Documentation] Test cde_scanDocumentation (summary)

**Input**: `project_path=".", detail_level="summary"`
**Expected Output**: Files with path, title, type, status
**Success Criteria**:
- Includes metadata summary
- Shows missing_metadata list
- Provides recommendations
- Token count ~5,000 for 100 files (50 tokens/file)

**Feedback**: Recommendation quality, missing metadata detection

---

### T016 [Documentation] Test cde_scanDocumentation (full)

**Input**: `project_path=".", detail_level="full"`
**Expected Output**: Complete metadata + content preview
**Success Criteria**:
- Includes first 100 lines of each file
- Shows by_location grouping
- Identifies orphaned docs and large files
- Memory usage < 500MB for 500 files

**Feedback**: Memory efficiency, large file handling

---

### T017 [Documentation] Test cde_analyzeDocumentation

**Input**: `project_path="."`
**Expected Output**: Quality score, link analysis, issues, suggestions
**Success Criteria**:
- Quality score 0-100
- Broken link detection
- Metadata consistency checks
- Actionable improvement suggestions

**Execution**:
```python
result = cde_analyzeDocumentation(".")
# Expected: {"quality_score": 72.5, "link_analysis": {...}, "issues": [...]}
```

**Feedback**: Accuracy of quality score, usefulness of suggestions

---

### T018 [P] [Documentation] Test cde_createSpecification

**Input**: `feature_name="test-feature", user_prompt="Test feature description"`
**Expected Output**: Generated spec.md file
**Success Criteria**:
- Creates valid spec.md with YAML frontmatter
- Includes placeholder user stories
- Follows Spec-Kit template

**Feedback**: Template quality, placeholder usefulness

---

**Checkpoint**: Documentation tools validated, token efficiency measured

---

## Phase 4: Recipe & Skill Management

**Purpose**: Test recipe downloads and skill sourcing

### T019 [Recipes] Test cde_downloadRecipes (first time)

**Input**: `project_path=".", force=False`
**Expected Output**: Downloaded recipes to .cde/recipes/
**Success Criteria**:
- Creates .cde/recipes/engineering/, design/, product/, testing/, bonus/
- Downloads 9+ recipe files (.poml format)
- Creates .cde/workflow.yml
- Returns status: "success", files_downloaded: [...]

**Execution**:
```python
# If .cde/ exists, delete it first for clean test
result = cde_downloadRecipes()
```

**Feedback**: Download speed, error handling, file organization

---

### T020 [Recipes] Test cde_downloadRecipes (already exists)

**Input**: `project_path=".", force=False`
**Expected Output**: Skipped with message
**Success Criteria**:
- Returns status: "skipped"
- Message explains .cde/ already exists
- Suggests force=True to overwrite

**Feedback**: Clear messaging, user-friendly

---

### T021 [Recipes] Test cde_downloadRecipes (force refresh)

**Input**: `project_path=".", force=True`
**Expected Output**: Overwrites existing recipes
**Success Criteria**:
- Replaces .cde/ contents
- Returns status: "success"
- All files updated

**Feedback**: Confirmation prompts (if any), data safety

---

### T022 [Orchestration] Test cde_sourceSkill (python best practices)

**Input**: `skill_query="python 3.14 best practices", destination="base"`
**Expected Output**: Skills downloaded to .copilot/skills/base/
**Success Criteria**:
- Downloads relevant skills from awesome-claude-skills
- Files have CDE-compatible YAML frontmatter
- Includes source attribution
- Returns skills_downloaded: [...]

**Execution**:
```python
result = cde_sourceSkill("python 3.14 best practices", destination="base")
```

**Feedback**: Skill relevance, frontmatter adaptation, source links

---

### T023 [P] [Orchestration] Test cde_sourceSkill (FastMCP patterns)

**Input**: `skill_query="fastmcp mcp server patterns", destination="ephemeral"`
**Expected Output**: Skills to .copilot/skills/ephemeral/
**Success Criteria**:
- Downloads MCP-specific skills
- Saved to ephemeral (temporary) location

**Feedback**: Search accuracy, skill quality

---

### T024 [Orchestration] Test cde_updateSkill (if skill exists)

**Input**: `skill_name="redis-caching", topics=["redis 7.x breaking changes"]`
**Expected Output**: Updated skill with research findings
**Success Criteria**:
- Performs web research (official docs, GitHub, blogs)
- Extracts insights (breaking changes, deprecations, new features)
- Generates update note with sources
- Detects version changes

**Execution**:
```python
# First, source a skill to update
cde_sourceSkill("redis caching patterns", destination="base")
# Then update it
result = cde_updateSkill("redis-caching", topics=["redis 7.x breaking changes"])
```

**Feedback**: Research quality, source credibility, update usefulness

---

**Checkpoint**: Recipes and skills managed successfully

---

## Phase 5: Workflow Orchestration (Sequential)

**Purpose**: Test full workflow lifecycle

### T025 [Orchestration] Test cde_selectWorkflow (trivial)

**Input**: `user_prompt="Fix typo in README: documenation → documentation"`
**Expected Output**: workflow_type="quick-fix", complexity="trivial"
**Success Criteria**:
- Detects trivial complexity
- Recommends quick-fix workflow
- Suggests skipping define/decompose/design phases
- Confidence > 0.9

**Execution**:
```python
result = cde_selectWorkflow("Fix typo in README: documenation → documentation")
# Expected: {"workflow_type": "quick-fix", "complexity": "trivial", "confidence": 0.95}
```

**Feedback**: Complexity detection accuracy, workflow recommendation quality

---

### T026 [P] [Orchestration] Test cde_selectWorkflow (simple)

**Input**: `user_prompt="Add logging to main.py"`
**Expected Output**: complexity="simple", duration="15-30 min"

**Feedback**: Duration estimates, skill recommendations

---

### T027 [P] [Orchestration] Test cde_selectWorkflow (moderate)

**Input**: `user_prompt="Add Redis caching to authentication module"`
**Expected Output**: complexity="moderate", duration="1-2 hours"

**Feedback**: Required skills detection, domain classification

---

### T028 [P] [Orchestration] Test cde_selectWorkflow (complex)

**Input**: `user_prompt="Refactor adapters to use dependency injection"`
**Expected Output**: complexity="complex", duration="4-8 hours"

**Feedback**: Confidence scoring, reasoning quality

---

### T029 [P] [Orchestration] Test cde_selectWorkflow (epic)

**Input**: `user_prompt="Rewrite entire system using microservices architecture"`
**Expected Output**: complexity="epic", duration="2-5 days"

**Feedback**: Epic detection, workflow customization

---

### T030 [Orchestration] Test cde_startFeature (real feature)

**Input**: `user_prompt="Add JSON export tool for workflow history", workflow_type="standard"`
**Expected Output**: Feature created in specs/add-json-export-tool/
**Success Criteria**:
- Creates specs/add-json-export-tool/ directory
- Generates spec.md, plan.md, tasks.md with placeholders
- All files have valid YAML frontmatter
- Returns feature_id (UUID)

**Execution**:
```python
result = cde_startFeature(
    user_prompt="Add JSON export tool for workflow history",
    workflow_type="standard"
)
# Save feature_id for next tasks
feature_id = json.loads(result)["feature_id"]
```

**Feedback**: Template quality, placeholder relevance, file organization

---

### T031 [Orchestration] Test cde_submitWork (define phase)

**Input**: `feature_id="<from T030>", phase_id="define", results={"specification": "..."}`
**Expected Output**: Phase advances to "decompose"
**Success Criteria**:
- Feature status updates
- Next phase prompt returned
- Workflow state persists

**Execution**:
```python
result = cde_submitWork(
    feature_id=feature_id,
    phase_id="define",
    results={"specification": "Export workflow history as JSON"}
)
# Expected: {"status": "success", "next_phase": "decompose", "prompt": "..."}
```

**Feedback**: State management, phase transition logic

---

### T032 [Orchestration] Test cde_submitWork (decompose phase)

**Input**: `feature_id="<from T030>", phase_id="decompose", results={"tasks": [...]}`
**Expected Output**: Phase advances to "design"

**Feedback**: Task breakdown validation

---

### T033 [Orchestration] Continue through all phases

**Input**: Submit work for design, implement, test, review
**Expected Output**: Feature completes successfully
**Success Criteria**:
- All 6 phases complete
- Feature status: "completed"
- All artifacts saved to specs/add-json-export-tool/

**Feedback**: Full workflow experience, pain points, missing features

---

**Checkpoint**: Workflow orchestration validated end-to-end

---

## Phase 6: Agent Delegation

**Purpose**: Test agent selection and delegation

### T034 [Agents] Test cde_listAvailableAgents

**Input**: None
**Expected Output**: List of available agents with capabilities
**Success Criteria**:
- Shows Jules, Copilot, Gemini, Qwen
- Indicates availability status
- Lists capabilities for each agent
- Provides setup instructions for unavailable agents

**Execution**:
```python
result = cde_listAvailableAgents()
# Expected: {"available_agents": [...], "unavailable_agents": [...]}
```

**Feedback**: Agent discovery, setup clarity

---

### T035 [P] [Agents] Test cde_selectAgent (trivial task)

**Input**: `task_description="Fix typo in error message"`
**Expected Output**: Selected agent + reasoning
**Success Criteria**:
- Detects trivial complexity
- Recommends quick agent (Copilot or Gemini)
- Provides reasoning

**Feedback**: Selection logic, reasoning transparency

---

### T036 [P] [Agents] Test cde_selectAgent (complex task)

**Input**: `task_description="Refactor authentication system to use OAuth2"`
**Expected Output**: Selected agent (likely Jules for complex work)
**Success Criteria**:
- Detects complex task
- Recommends agent with plan approval capability
- Explains why Jules is best fit

**Feedback**: Complexity detection, agent matching

---

### T037 [Agents] Test cde_executeWithBestAgent (simple task)

**Input**: `task_description="Add type hints to helpers.py"`
**Expected Output**: Task executed with best available agent
**Success Criteria**:
- Selects appropriate agent
- Executes task successfully
- Returns execution results
- Includes execution time

**Execution**:
```python
result = cde_executeWithBestAgent("Add type hints to helpers.py")
# Expected: {"selected_agent": "copilot", "success": true, "execution_result": "..."}
```

**Feedback**: Agent selection accuracy, execution reliability

---

### T038 [CEO] Test cde_delegateTask (background execution)

**Input**: `task_description="Generate test coverage report", task_type="documentation"`
**Expected Output**: Task queued, task_id returned
**Success Criteria**:
- Task added to queue
- Returns task_id (UUID)
- Assigned to available worker
- Status: "queued" or "running"

**Execution**:
```python
result = cde_delegateTask(
    task_description="Generate test coverage report",
    task_type="documentation"
)
# Save task_id for next tasks
task_id = json.loads(result)["task_id"]
```

**Feedback**: Delegation UX, task ID visibility

---

### T039 [CEO] Test cde_getTaskStatus (polling)

**Input**: `task_id="<from T038>"`
**Expected Output**: Current task status
**Success Criteria**:
- Returns status: queued/running/completed/failed/cancelled
- Shows assigned agent
- Includes created_at, updated_at timestamps
- Shows result when completed

**Execution**:
```python
# Poll every 5 seconds
import time
for _ in range(10):
    result = cde_getTaskStatus(task_id)
    status = json.loads(result)["status"]
    if status in ["completed", "failed", "cancelled"]:
        break
    time.sleep(5)
```

**Feedback**: Status tracking, result visibility

---

### T040 [P] [CEO] Test cde_listActiveTasks

**Input**: None
**Expected Output**: List of all active tasks
**Success Criteria**:
- Shows queued + running tasks
- Includes task descriptions
- Shows assigned agents

**Feedback**: Task visibility, filtering options

---

### T041 [P] [CEO] Test cde_getWorkerStats

**Input**: None
**Expected Output**: Worker pool statistics
**Success Criteria**:
- Shows max_workers, active_workers
- Lists individual worker status
- Shows tasks_completed per worker

**Feedback**: Transparency, debugging utility

---

### T042 [CEO] Test cde_cancelTask (if task is running)

**Input**: `task_id="<task to cancel>"`
**Expected Output**: Task cancelled
**Success Criteria**:
- Task status changes to "cancelled"
- Graceful shutdown (if already running)
- Clear confirmation message

**Feedback**: Cancellation reliability, cleanup

---

**Checkpoint**: Agent delegation working, CEO orchestration reliable

---

## Phase 7: Onboarding & Setup

**Purpose**: Test project analysis and setup

### T043 [Onboarding] Test cde_onboardingProject (CDE itself)

**Input**: `project_path="."`
**Expected Output**: Project analysis with onboarding recommendations
**Success Criteria**:
- Analyzes directory structure
- Identifies project type (Python library)
- Lists key technologies (FastMCP, MCP, pytest)
- Generates onboarding document recommendations

**Execution**:
```python
result = cde_onboardingProject(project_path=".")
# Expected: {"status": "success", "analysis": {...}, "recommendations": [...]}
```

**Feedback**: Analysis accuracy, recommendation quality

---

### T044 [Onboarding] Test cde_setupProject (in test directory)

**Input**: `project_path="./tests/integration/dogfooding/sample_project/"`
**Expected Output**: Generated configuration files
**Success Criteria**:
- Creates .gitignore (if missing)
- Creates AGENTS.md with project context
- Does not overwrite existing files (unless force=True)

**Execution**:
```python
# Create test directory first
import os
os.makedirs("./tests/integration/dogfooding/sample_project/", exist_ok=True)

result = cde_setupProject(
    project_path="./tests/integration/dogfooding/sample_project/"
)
```

**Feedback**: Config quality, safety (no overwrites)

---

### T045 [Onboarding] Test cde_publishOnboarding (approve=False)

**Input**: `documents={"README.md": "..."}, approve=False`
**Expected Output**: Documents NOT written (dry-run)
**Success Criteria**:
- Shows what would be written
- Does not modify filesystem
- Returns preview of documents

**Execution**:
```python
documents = {
    "README.md": "# Test Project\n\nGenerated by onboarding"
}
result = cde_publishOnboarding(
    documents=documents,
    project_path="./tests/integration/dogfooding/sample_project/",
    approve=False
)
```

**Feedback**: Dry-run behavior, safety

---

**Checkpoint**: Onboarding tools tested safely

---

## Phase 8: Advanced Features

**Purpose**: Test remaining specialized tools

### T046 [Extensions] Test cde_installMcpExtension

**Input**: `extension_name="mcp-status-bar", force=False`
**Expected Output**: Extension installed in VS Code
**Success Criteria**:
- Extension downloaded/installed
- Activated in VS Code
- Status bar shows MCP tools
- If already installed, returns status: "already_installed"

**Execution**:
```python
result = cde_installMcpExtension(extension_name="mcp-status-bar")
```

**Feedback**: Installation reliability, VS Code integration

---

### T047 [Utility] Test cde_testProgressReporting

**Input**: `duration=10, steps=5`
**Expected Output**: Progress updates in status bar
**Success Criteria**:
- Reports progress at each step
- Status bar updates visible in VS Code
- Completes after specified duration
- Returns completion summary

**Execution**:
```python
result = cde_testProgressReporting(duration=10, steps=5)
# Watch status bar in VS Code for updates
```

**Feedback**: Progress visibility, update frequency

---

### T048 [Orchestration] Test cde_executeFullImplementation (small feature)

**Input**: `start_phase="phase1", phases=["phase1", "phase2"]`
**Expected Output**: Partial workflow execution
**Success Criteria**:
- Executes specified phases only
- Uses MultiAgentOrchestrator for delegation
- Returns results for each phase
- Allows resuming from checkpoint

**Execution**:
```python
# Start small feature first (from T030)
result = cde_executeFullImplementation(
    start_phase="phase1",
    phases=["phase1", "phase2"]
)
```

**Feedback**: Multi-agent coordination, checkpoint/resume

---

**Checkpoint**: All 27 tools tested successfully

---

## Phase 9: Spec-Kit Conformity Validation

**Purpose**: Compare CDE templates against GitHub Spec-Kit

### T049 [Validation] Download Spec-Kit reference templates

**Execution**:
```bash
# Clone Spec-Kit repo (or fetch templates)
git clone --depth 1 https://github.com/github/spec-kit.git /tmp/spec-kit
```

**Output**: Spec-Kit templates in /tmp/spec-kit/templates/

---

### T050 [Validation] Run conformity validation script

**Input**: CDE templates vs Spec-Kit templates
**Expected Output**: Conformity report with score
**Success Criteria**:
- Conformity score 95%+
- All required sections present
- All YAML frontmatter fields match
- Naming conventions aligned

**Execution**:
```bash
python scripts/validate_spec_kit_conformity.py \
    --cde-templates specs/templates/ \
    --spec-kit-templates /tmp/spec-kit/templates/ \
    --output specs/cde-dogfooding-feedback/results/spec-kit-compliance.json
```

**Feedback**: Template alignment, gaps identified

---

### T051 [P] [Validation] Measure token efficiency

**Input**: Documentation scan results (from T014-T016)
**Expected Output**: Token usage report
**Success Criteria**:
- name_only: 95%+ reduction vs full
- summary: 85%+ reduction vs full
- Demonstrates progressive disclosure value

**Execution**:
```bash
python scripts/estimate_token_usage.py \
    --scan-results specs/cde-dogfooding-feedback/results/ \
    --output specs/cde-dogfooding-feedback/results/token-efficiency.json
```

**Feedback**: Token optimization effectiveness

---

**Checkpoint**: Spec-Kit conformity validated

---

## Phase 10: Feedback Collection & Reporting

**Purpose**: Generate comprehensive feedback reports

### T052 [Reporting] Aggregate feedback for orchestration tools

**Input**: Feedback from T025-T033, T022-T024
**Output**: `agent-docs/execution/feedback-orchestration-tools-2025-11-24.md`
**Success Criteria**:
- Structured feedback for 5 orchestration tools
- Includes usability ratings, bugs, improvements
- Actionable recommendations

**Template**:
```markdown
---
title: "Feedback: Orchestration Tools"
type: "feedback"
date: "2025-11-24"
---

## cde_selectWorkflow
- Usability: 4/5
- Issues: Low confidence scenarios need examples
- Improvements: Add clarifying questions when <0.6
...
```

---

### T053 [P] [Reporting] Aggregate feedback for documentation tools

**Input**: Feedback from T014-T018
**Output**: `agent-docs/execution/feedback-documentation-tools-2025-11-24.md`

---

### T054 [P] [Reporting] Aggregate feedback for agent tools

**Input**: Feedback from T034-T037
**Output**: `agent-docs/execution/feedback-agent-tools-2025-11-24.md`

---

### T055 [P] [Reporting] Aggregate feedback for CEO orchestration

**Input**: Feedback from T038-T042
**Output**: `agent-docs/execution/feedback-ceo-orchestration-2025-11-24.md`

---

### T056 [P] [Reporting] Aggregate feedback for onboarding tools

**Input**: Feedback from T043-T045
**Output**: `agent-docs/execution/feedback-onboarding-tools-2025-11-24.md`

---

### T057 [P] [Reporting] Aggregate feedback for utility tools

**Input**: Feedback from T009-T013, T046-T048
**Output**: `agent-docs/execution/feedback-utility-tools-2025-11-24.md`

---

### T058 [Reporting] Generate executive summary

**Input**: All feedback reports + validation results
**Output**: `agent-docs/execution/feedback-summary-2025-11-24.md`
**Success Criteria**:
- Highlights top 10 improvements
- Shows conformity score
- Lists critical bugs
- Provides next steps

**Template**:
```markdown
---
title: "CDE MCP Dogfooding Summary"
date: "2025-11-24"
---

## Executive Summary
- Tools tested: 27/27 (100%)
- Spec-Kit conformity: 97%
- Critical bugs: 2
- High-priority improvements: 8

## Top Findings
1. ...
2. ...

## Next Steps
- [ ] Fix critical bugs
- [ ] Implement top 5 improvements
- [ ] Update documentation
```

---

### T059 [Reporting] Generate JSON results file

**Input**: All test results
**Output**: `specs/cde-dogfooding-feedback/results/tool-results.json`
**Success Criteria**:
- Structured JSON matching feedback-schema.json
- All 27 tools included
- Machine-readable for future analysis

---

### T060 [Reporting] Create GitHub issues for improvements

**Input**: Improvement suggestions from all feedback
**Expected Output**: 10+ GitHub issues created
**Success Criteria**:
- Each issue has clear description
- Includes reproduction steps (if bug)
- Tagged appropriately (enhancement, bug, documentation)
- Linked to relevant feedback report

**Execution**:
```bash
# Create issues using GitHub CLI
gh issue create \
    --title "Improvement: Add clarifying questions to cde_selectWorkflow" \
    --body "See feedback report: agent-docs/execution/feedback-orchestration-tools-2025-11-24.md" \
    --label enhancement
```

---

**Checkpoint**: All feedback collected and reported

---

## Phase 11: Cleanup & Documentation

**Purpose**: Finalize documentation and merge

### T061 [Docs] Update CHANGELOG.md

**Input**: Summary of dogfooding results
**Output**: Updated CHANGELOG.md with entry for dogfooding initiative

---

### T062 [P] [Docs] Update README.md (if needed)

**Input**: New insights about tool usage
**Output**: Improved README with dogfooding results

---

### T063 [P] [Docs] Update tool docstrings (if issues found)

**Input**: Documentation gaps from feedback
**Output**: Improved docstrings in `src/mcp_tools/*.py`

---

### T064 [Git] Commit all changes

**Execution**:
```bash
git add specs/cde-dogfooding-feedback/
git add agent-docs/execution/feedback-*-2025-11-24.md
git add scripts/validate_spec_kit_conformity.py
git add scripts/estimate_token_usage.py
git commit -m "feat: Complete CDE MCP dogfooding feedback initiative

- Tested all 27 tools with realistic scenarios
- Validated 97% Spec-Kit conformity
- Identified 10 improvement opportunities
- Generated comprehensive feedback reports"
```

---

### T065 [Git] Create pull request

**Execution**:
```bash
gh pr create \
    --title "CDE MCP Dogfooding Feedback Initiative" \
    --body "See specs/cde-dogfooding-feedback/spec.md for full details" \
    --label documentation,enhancement
```

---

### T066 [Review] Review PR with team

**Success Criteria**:
- All feedback reports reviewed
- Improvement priorities agreed
- Conformity gaps addressed
- Next steps clear

---

### T067 [Git] Merge to main

**Execution**:
```bash
# After PR approval
gh pr merge --squash
```

---

**Checkpoint**: Dogfooding initiative complete! 🎉

---

## Success Metrics

- ✅ 27/27 tools tested (100%)
- ✅ 67/67 tasks completed
- ✅ 10+ GitHub issues created
- ✅ 6 feedback reports generated
- ✅ 95%+ Spec-Kit conformity achieved
- ✅ 90%+ token reduction demonstrated

---

## Notes for Execution

### Parallel Execution
Tasks marked [P] can be executed in parallel to save time:
- Phase 2: T010-T013 (4 tools)
- Phase 3: T018 (1 tool)
- Phase 5: T026-T029 (4 workflow tests)
- Phase 6: T035-T036, T040-T041 (4 agent tests)
- Phase 10: T053-T057 (5 feedback reports)
- Phase 11: T062-T063 (2 docs updates)

### Time Estimates
- **Sequential execution**: 8-10 hours
- **With parallelization**: 6-7 hours
- **Split over multiple sessions**: 2-3 days

### Feedback Template
Use this template for each tool:

```json
{
  "tool_name": "cde_xxx",
  "test_date": "2025-11-24T10:30:00Z",
  "result": "success",
  "feedback": {
    "usability": {"rating": 4, "comments": "..."},
    "accuracy": {"rating": 5, "comments": "..."},
    "performance": {"duration_ms": 1250},
    "documentation": {"rating": 3, "comments": "..."},
    "errors_encountered": [],
    "improvement_suggestions": ["..."]
  }
}
```

---

## References

- **Spec**: `specs/cde-dogfooding-feedback/spec.md`
- **Plan**: `specs/cde-dogfooding-feedback/plan.md`
- **Feedback Schema**: `specs/cde-dogfooding-feedback/feedback-schema.json`
- **Tool Docs**: Inline docstrings in `src/mcp_tools/*.py`
- **Spec-Kit**: https://github.com/github/spec-kit
