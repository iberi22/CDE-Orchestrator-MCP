---
title: "Implementation Plan: CDE MCP Dogfooding & Tool Feedback"
description: "Technical plan for executing comprehensive tool feedback on CDE project"
type: "design"
status: "active"
created: "2025-11-24"
updated: "2025-11-24"
author: "CDE Orchestrator Team"
llm_summary: |
  Technical implementation plan for dogfooding CDE MCP. Defines test scenarios,
  feedback schema, tool execution order, and validation criteria. Uses CDE on
  itself to validate Spec-Kit conformity and tool ergonomics.
---

## Implementation Plan: CDE MCP Dogfooding & Tool Feedback

**Branch**: `dogfooding-feedback` | **Date**: 2025-11-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/cde-dogfooding-feedback/spec.md`

---

## Summary

Execute all 27 CDE MCP tools on the CDE Orchestrator MCP project itself to gather comprehensive feedback. Validate Spec-Kit conformity, test tool interactions, document UX issues, and collect structured feedback for improvements. This is a meta-development exercise: using CDE to improve CDE.

**Primary Goal**: Ensure CDE MCP tools work reliably in real-world scenarios and conform to GitHub Spec-Kit standards.

---

## Technical Context

**Language/Version**: Python 3.11+ (tested on 3.11, 3.12, 3.13, 3.14)
**Primary Dependencies**: FastMCP, mcp SDK, httpx, pyyaml, pydantic
**Storage**: Filesystem (specs/, agent-docs/, .cde/, .copilot/)
**Testing**: Manual execution + automated validation scripts
**Target Platform**: VS Code with MCP extension (Windows, Linux, macOS)
**Project Type**: Single Python project with hexagonal architecture
**Performance Goals**:
- Tools complete within documented timeout (30 min default)
- Documentation scans handle 500+ files
- Progressive disclosure reduces tokens by 90%+

**Constraints**:
- No production code changes (feedback only)
- All tests run in feature branch
- JSON feedback schema required
- Pre-commit hooks must pass

**Scale/Scope**:
- 27 tools to test
- 500+ .md files in repository
- 10+ user stories with acceptance criteria
- 3-5 feedback points per tool (avg)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Alignment with CDE Constitution** (`memory/constitution.md`):

✅ **Explicitness over cleverness**: All feedback structured as JSON
✅ **Contracts over implementations**: Validate tool outputs against schemas
✅ **Isolation over shared state**: Each tool tested independently
✅ **LLM-readability**: All feedback documents have YAML frontmatter
✅ **Progressive disclosure**: Use detail_level parameters to reduce tokens
✅ **Spec-first development**: Following Spec-Kit workflow (spec → plan → tasks)

**Governance Compliance** (`specs/governance/DOCUMENTATION_GOVERNANCE.md`):

✅ All feedback docs → `agent-docs/execution/feedback-[tool]-2025-11-24.md`
✅ YAML frontmatter required in all documents
✅ No .md files in root (except README, CHANGELOG, etc.)
✅ Use lowercase-with-hyphens naming convention
✅ Max 1500 lines per document (split if longer)

---

## Project Structure

### Documentation (this feature)

```text
specs/cde-dogfooding-feedback/
├── spec.md              # This feature's specification
├── plan.md              # This file (technical plan)
├── tasks.md             # Executable task list (tool-by-tool)
├── feedback-schema.json # JSON schema for structured feedback
└── results/             # Test execution results
    ├── tool-results.json
    ├── spec-kit-compliance.json
    └── summary-report.md
```

### Feedback Collection (repository root)

```text
agent-docs/execution/
├── feedback-orchestration-tools-2025-11-24.md
├── feedback-documentation-tools-2025-11-24.md
├── feedback-agent-tools-2025-11-24.md
├── feedback-ceo-orchestration-2025-11-24.md
├── feedback-onboarding-tools-2025-11-24.md
├── feedback-utility-tools-2025-11-24.md
└── feedback-summary-2025-11-24.md
```

### Test Execution

```text
tests/integration/dogfooding/
├── test_orchestration_tools.py
├── test_documentation_tools.py
├── test_agent_tools.py
├── test_onboarding_tools.py
└── fixtures/
    ├── sample_project/
    └── expected_outputs/
```

---

## Feedback Schema

### JSON Structure

```json
{
  "tool_name": "cde_selectWorkflow",
  "category": "orchestration",
  "test_date": "2025-11-24T10:30:00Z",
  "tested_by": "AI Agent (GitHub Copilot)",
  "test_scenario": "Select workflow for moderate complexity feature",
  "input": {
    "user_prompt": "Add JSON export tool for workflow history"
  },
  "output": {
    "workflow_type": "standard",
    "complexity": "moderate",
    "confidence": 0.85
  },
  "result": "success|partial|failure",
  "feedback": {
    "usability": {
      "rating": 4,
      "comments": "Clear recommendations but could add more examples"
    },
    "accuracy": {
      "rating": 5,
      "comments": "Complexity detection was spot-on"
    },
    "performance": {
      "duration_ms": 1250,
      "comments": "Fast response time"
    },
    "documentation": {
      "rating": 3,
      "comments": "Missing example for low-confidence scenarios"
    },
    "errors_encountered": [],
    "improvement_suggestions": [
      "Add example outputs for each complexity level",
      "Include clarifying questions when confidence < 0.6"
    ]
  }
}
```

### Feedback Categories

1. **Usability** (1-5): How intuitive is the tool?
2. **Accuracy** (1-5): Does output match expectations?
3. **Performance**: Execution time and resource usage
4. **Documentation** (1-5): Are docs clear and complete?
5. **Errors**: Bugs, exceptions, unexpected behavior
6. **Improvements**: Specific actionable suggestions

---

## Tool Execution Strategy

### Phase 1: Independent Tools (No Dependencies)

Test tools that don't depend on other tools:

```
1. cde_healthCheck
2. cde_searchTools (all detail levels)
3. cde_checkRecipes
4. cde_scanDocumentation (all detail levels)
5. cde_analyzeDocumentation
6. cde_listAvailableAgents
7. cde_testProgressReporting
```

**Expected Duration**: 30 minutes
**Success Criteria**: All tools execute without errors, return valid JSON

### Phase 2: Recipe & Skill Management

Test recipe and skill tools:

```
8. cde_downloadRecipes (check, download, force refresh)
9. cde_checkRecipes (verify downloads)
10. cde_sourceSkill (multiple skills: python-best-practices, fastmcp-patterns, mcp-protocol)
11. cde_updateSkill (test with redis-caching skill if exists)
```

**Expected Duration**: 45 minutes (includes web research)
**Success Criteria**: Recipes downloaded, skills sourced with proper frontmatter

### Phase 3: Workflow Orchestration

Test workflow lifecycle:

```
12. cde_selectWorkflow (5 different prompts: trivial, simple, moderate, complex, epic)
13. cde_startFeature (start real feature: "Add JSON export tool")
14. cde_submitWork (submit work for define phase)
15. cde_submitWork (submit work for decompose phase)
... (continue through all phases)
```

**Expected Duration**: 60 minutes
**Success Criteria**: Feature created, phases advance correctly, specs/ directory populated

### Phase 4: Agent Delegation

Test agent selection and execution:

```
16. cde_selectAgent (5 different task descriptions)
17. cde_executeWithBestAgent (simple task: "Fix typo in README")
18. cde_delegateTask (via CEO orchestrator)
19. cde_getTaskStatus (poll status)
20. cde_listActiveTasks
21. cde_getWorkerStats
22. cde_cancelTask (if needed)
```

**Expected Duration**: 90 minutes (includes agent execution time)
**Success Criteria**: Agents execute correctly, delegation works, status tracking accurate

### Phase 5: Onboarding & Setup

Test project analysis:

```
23. cde_onboardingProject (analyze CDE project)
24. cde_setupProject (generate configs in test directory)
25. cde_publishOnboarding (with approve=False for safety)
```

**Expected Duration**: 30 minutes
**Success Criteria**: Project analyzed, configs generated, no production files modified

### Phase 6: Advanced Features

Test remaining tools:

```
26. cde_installMcpExtension (if not already installed)
27. cde_executeFullImplementation (test with small feature)
28. cde_createSpecification (create spec for test feature)
```

**Expected Duration**: 45 minutes
**Success Criteria**: Extension installed, full implementation works, specs created

---

## Spec-Kit Conformity Validation

### Comparison Checklist

Compare CDE templates vs GitHub Spec-Kit:

**Template Files**:
- `specs/templates/spec.md` ↔ Spec-Kit spec.md
- `specs/templates/plan.md` ↔ Spec-Kit plan.md
- `specs/templates/tasks.md` ↔ Spec-Kit tasks.md

**Validation Points**:

1. **YAML Frontmatter**:
   - ✅ title, description, type, status, created, updated, author
   - ✅ llm_summary for AI agents
   - ⚠️ Check if Spec-Kit uses additional fields

2. **Section Structure**:
   - ✅ User Scenarios & Testing (spec.md)
   - ✅ Requirements (spec.md)
   - ✅ Technical Context (plan.md)
   - ✅ Project Structure (plan.md)
   - ⚠️ Check if Spec-Kit has additional sections

3. **Task Organization**:
   - ✅ Tasks grouped by user story
   - ✅ [P] markers for parallel tasks
   - ✅ File path conventions
   - ⚠️ Check if Spec-Kit uses different format

4. **Naming Conventions**:
   - ✅ Feature directory: `specs/[feature-name]/`
   - ✅ Lowercase with hyphens
   - ⚠️ Verify against Spec-Kit standard

### Automated Validation Script

```python
# scripts/validate_spec_kit_conformity.py

import json
from pathlib import Path
import yaml

def validate_template(template_path: Path, spec_kit_reference: dict) -> dict:
    """Compare CDE template against Spec-Kit reference."""

    with open(template_path) as f:
        content = f.read()

    # Extract frontmatter
    if content.startswith("---"):
        frontmatter = yaml.safe_load(content.split("---")[1])
    else:
        frontmatter = {}

    # Check required fields
    required_fields = ["title", "description", "type", "status"]
    missing_fields = [f for f in required_fields if f not in frontmatter]

    # Check section structure
    required_sections = spec_kit_reference.get("required_sections", [])
    missing_sections = [s for s in required_sections if s not in content]

    return {
        "template": str(template_path),
        "conformity_score": calculate_score(missing_fields, missing_sections),
        "missing_fields": missing_fields,
        "missing_sections": missing_sections,
        "recommendations": generate_recommendations(missing_fields, missing_sections)
    }
```

---

## Token Efficiency Testing

### Progressive Disclosure Validation

Test documentation tools with different detail levels:

**Scenario 1: Large Repository (500+ files)**

```python
# Baseline: Load all files with full detail
result_full = cde_scanDocumentation(".", detail_level="full")
tokens_full = estimate_tokens(result_full)  # ~50,000 tokens

# Progressive: Load only names
result_names = cde_scanDocumentation(".", detail_level="name_only")
tokens_names = estimate_tokens(result_names)  # ~1,000 tokens

# Progressive: Load summary
result_summary = cde_scanDocumentation(".", detail_level="summary")
tokens_summary = estimate_tokens(result_summary)  # ~5,000 tokens

# Calculate savings
savings_names = (tokens_full - tokens_names) / tokens_full * 100
savings_summary = (tokens_full - tokens_summary) / tokens_full * 100
```

**Target Metrics**:
- name_only: 95%+ token reduction
- summary: 85%+ token reduction
- Verify output is still actionable

---

## Error Handling & Edge Cases

### Test Scenarios

1. **Empty Project**:
   - Create temp directory with no .cde/ or specs/
   - Run tools and verify graceful error messages

2. **Invalid Frontmatter**:
   - Create .md file with malformed YAML
   - Run cde_scanDocumentation and verify handling

3. **Network Failures**:
   - Simulate GitHub API rate limit
   - Verify cde_sourceSkill retries or provides helpful error

4. **Missing Dependencies**:
   - Run tools with missing CLI tools (gh, git)
   - Verify clear error messages with installation instructions

5. **Permission Errors**:
   - Run tools in read-only directory
   - Verify graceful failure with actionable error

6. **Large Files**:
   - Test with 2000+ line .md file
   - Verify performance and memory usage

7. **Concurrent Operations**:
   - Start two features simultaneously
   - Verify no race conditions or data corruption

---

## Success Criteria

### Tool Execution
- ✅ 27/27 tools execute successfully
- ✅ 100% of tools return valid JSON (when applicable)
- ✅ 0 unhandled exceptions
- ✅ 100% of documented parameters work as expected

### Spec-Kit Conformity
- ✅ 95%+ template conformity score
- ✅ All required sections present in templates
- ✅ All YAML frontmatter fields match Spec-Kit
- ✅ Naming conventions match Spec-Kit standard

### Feedback Quality
- ✅ Structured JSON feedback for all 27 tools
- ✅ 10+ actionable improvement suggestions
- ✅ 5+ UX issues documented
- ✅ 3+ documentation gaps identified

### Performance
- ✅ All tools complete within documented timeout
- ✅ Documentation scans handle 500+ files
- ✅ 90%+ token reduction with progressive disclosure
- ✅ Agent delegation supports 5+ concurrent tasks

### Reproducibility
- ✅ 100% of tests can be re-run
- ✅ Deterministic outputs for same inputs
- ✅ Clear execution logs for debugging

---

## Deliverables

1. **Feedback Reports** (agent-docs/execution/):
   - feedback-orchestration-tools-2025-11-24.md
   - feedback-documentation-tools-2025-11-24.md
   - feedback-agent-tools-2025-11-24.md
   - feedback-ceo-orchestration-2025-11-24.md
   - feedback-onboarding-tools-2025-11-24.md
   - feedback-utility-tools-2025-11-24.md
   - feedback-summary-2025-11-24.md

2. **Test Results** (specs/cde-dogfooding-feedback/results/):
   - tool-results.json (structured feedback for all tools)
   - spec-kit-compliance.json (conformity validation)
   - summary-report.md (human-readable summary)

3. **Validation Scripts** (scripts/):
   - validate_spec_kit_conformity.py
   - estimate_token_usage.py
   - run_dogfooding_suite.py

4. **Improvement Backlog**:
   - GitHub issues for each identified bug
   - Enhancement proposals for UX improvements
   - Documentation PRs for missing examples

---

## Timeline Estimate

| Phase | Duration | Tasks |
|-------|----------|-------|
| Phase 1: Independent Tools | 30 min | 7 tools |
| Phase 2: Recipe & Skill Mgmt | 45 min | 4 tools |
| Phase 3: Workflow Orchestration | 60 min | 5 tools |
| Phase 4: Agent Delegation | 90 min | 7 tools |
| Phase 5: Onboarding | 30 min | 3 tools |
| Phase 6: Advanced Features | 45 min | 3 tools |
| Spec-Kit Validation | 30 min | Analysis |
| Report Generation | 30 min | Documentation |
| **TOTAL** | **6 hours** | **27 tools + analysis** |

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Tool modifies production code | HIGH | LOW | Run in feature branch, review all changes |
| Long execution blocks workflow | MEDIUM | MEDIUM | Use async delegation for slow tools |
| Network failures during testing | MEDIUM | MEDIUM | Cache results, retry logic, offline mode |
| Spec-Kit changes during testing | LOW | LOW | Pin to specific Spec-Kit version/commit |
| Feedback collection is inconsistent | MEDIUM | LOW | Use JSON schema validation |
| Rate limiting on GitHub API | LOW | MEDIUM | Respect rate limits, use authenticated requests |

---

## References

- **Spec-Kit Official**: https://github.com/github/spec-kit
- **Spec-Kit Docs**: https://github.github.io/spec-kit/
- **CDE Governance**: `specs/governance/DOCUMENTATION_GOVERNANCE.md`
- **CDE Architecture**: `specs/design/architecture/README.md`
- **CDE Roadmap**: `specs/tasks/improvement-roadmap.md`
- **Tool Documentation**: Inline docstrings in `src/mcp_tools/*.py`
- **MCP Protocol**: https://modelcontextprotocol.io/
- **FastMCP Docs**: https://github.com/jlowin/fastmcp

---

## Next Steps

1. Review this plan with stakeholders
2. Set up feature branch: `dogfooding-feedback`
3. Create validation scripts in `scripts/`
4. Execute tasks.md in sequential order
5. Collect feedback using JSON schema
6. Generate reports in `agent-docs/execution/`
7. Create GitHub issues for improvements
8. Submit PRs for documentation fixes
