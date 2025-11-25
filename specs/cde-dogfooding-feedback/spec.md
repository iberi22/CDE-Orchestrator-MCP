---
title: "Feature Specification: CDE MCP Dogfooding & Tool Feedback"
description: "Comprehensive tool-by-tool feedback plan using CDE MCP on its own codebase"
type: "feature"
status: "active"
created: "2025-11-24"
updated: "2025-11-24"
author: "CDE Orchestrator Team"
llm_summary: |
  Dogfooding plan for CDE MCP. Use all 27 MCP tools on the CDE project itself
  to gather feedback, identify issues, and improve UX. Validates Spec-Kit
  conformity and tool ergonomics through real-world usage.
---

## Feature Specification: CDE MCP Dogfooding & Tool Feedback

**Feature Branch**: `dogfooding-feedback`
**Created**: 2025-11-24
**Status**: Active
**Input**: Use CDE MCP tools on the CDE MCP project itself to gather comprehensive feedback

---

## 🎯 Objectives

1. **Validate Spec-Kit Conformity**: Ensure our templates match GitHub's Spec-Kit standard
2. **Test All 27 Tools**: Execute every `cde_*` tool in realistic scenarios
3. **Gather Feedback**: Document UX issues, bugs, and improvement opportunities
4. **Improve Documentation**: Identify gaps in tool descriptions and examples
5. **Dogfooding Loop**: Use CDE to improve CDE (meta-development)

---

## 🧪 User Scenarios & Testing *(mandatory)*

### User Story 1 - Project Health Check (Priority: P1)

**As a** developer using CDE MCP for the first time
**I want to** validate that my project is properly configured
**So that** I can start using CDE tools with confidence

**Why this priority**: Foundation for all other usage - must work before any other tool

**Independent Test**: Can be fully tested by running health check on CDE project and getting comprehensive status report

**Acceptance Scenarios**:

1. **Given** CDE MCP project is opened in VS Code with MCP server running
   **When** I invoke `cde_healthCheck()`
   **Then** I receive JSON status for Python, Rust, and external tools (git, gh, etc.)

2. **Given** health check shows missing dependencies
   **When** I review the output
   **Then** I get actionable error messages with installation instructions

3. **Given** all dependencies are installed
   **When** I run health check
   **Then** All components report "healthy" status

---

### User Story 2 - Documentation Audit (Priority: P1)

**As a** project maintainer
**I want to** audit all documentation for Spec-Kit conformity
**So that** I ensure consistent metadata and organization

**Why this priority**: Documentation quality impacts all downstream tool usage

**Independent Test**: Scan CDE project docs and generate compliance report

**Acceptance Scenarios**:

1. **Given** CDE project has mixed documentation (some with frontmatter, some without)
   **When** I run `cde_scanDocumentation(".", detail_level="summary")`
   **Then** I get a list of files with metadata status and recommendations

2. **Given** documentation scan identifies missing frontmatter
   **When** I run `cde_analyzeDocumentation(".")`
   **Then** I get quality score, broken links report, and actionable suggestions

3. **Given** documentation has inconsistent naming
   **When** I review scan results
   **Then** I receive recommendations for standardized naming patterns

---

### User Story 3 - Workflow Selection for Real Feature (Priority: P1)

**As a** developer starting a new feature
**I want to** get intelligent workflow recommendations
**So that** I follow the optimal development process

**Why this priority**: Entry point for all feature development workflows

**Independent Test**: Test with various prompts (trivial, simple, moderate, complex, epic)

**Acceptance Scenarios**:

1. **Given** I want to add a new tool to CDE MCP
   **When** I run `cde_selectWorkflow("Add tool for exporting workflow history to JSON")`
   **Then** I receive workflow_type, complexity, recipe_id, required_skills, and confidence score

2. **Given** workflow selector recommends "moderate" complexity
   **When** I review the response
   **Then** Estimated duration and required skills are realistic and actionable

3. **Given** workflow selector has low confidence (<0.6)
   **When** I receive the response
   **Then** I get clarifying questions to improve recommendation

---

### User Story 4 - Skill Sourcing & Management (Priority: P2)

**As a** developer working in unfamiliar domain
**I want to** download relevant skills from external repositories
**So that** I have best practices and patterns available

**Why this priority**: Enhances development quality but not blocking

**Independent Test**: Source skills for Python 3.14, FastMCP, and MCP protocol

**Acceptance Scenarios**:

1. **Given** I need skills for a new technology
   **When** I run `cde_sourceSkill("python 3.14 best practices", destination="base")`
   **Then** Relevant skills are downloaded to `.copilot/skills/base/` with CDE frontmatter

2. **Given** a skill references outdated library versions
   **When** I run `cde_updateSkill("redis-caching", topics=["redis 7.x breaking changes"])`
   **Then** Skill is updated with latest research from official docs and GitHub

3. **Given** skills are downloaded
   **When** I review the files
   **Then** Each skill has YAML frontmatter, structured sections, and source attribution

---

### User Story 5 - Recipe Management (Priority: P2)

**As a** developer setting up CDE in a project
**I want to** download and manage workflow recipes
**So that** I can use pre-built workflows for common patterns

**Why this priority**: Nice-to-have for standardized workflows

**Independent Test**: Download recipes and check against expected structure

**Acceptance Scenarios**:

1. **Given** `.cde/` directory doesn't exist
   **When** I run `cde_downloadRecipes()`
   **Then** Recipes are downloaded from agents-flows-recipes repo to `.cde/recipes/`

2. **Given** recipes are already downloaded
   **When** I run `cde_checkRecipes()`
   **Then** I get confirmation of existing recipes and their paths

3. **Given** I want to force refresh recipes
   **When** I run `cde_downloadRecipes(force=True)`
   **Then** Existing recipes are overwritten with latest versions

---

### User Story 6 - Feature Lifecycle (Priority: P1)

**As a** developer implementing a feature
**I want to** track feature lifecycle through phases
**So that** I follow structured development process

**Why this priority**: Core CDE workflow - must work reliably

**Independent Test**: Start a real feature in CDE project and submit work for each phase

**Acceptance Scenarios**:

1. **Given** workflow is selected
   **When** I run `cde_startFeature(user_prompt="Add JSON export tool", workflow_type="standard")`
   **Then** Feature directory is created in `specs/add-json-export-tool/` with spec.md, plan.md, tasks.md

2. **Given** feature is started (phase: define)
   **When** I complete specification and run `cde_submitWork(feature_id="uuid", phase_id="define", results={"specification": "..."})`
   **Then** Feature advances to next phase (decompose) with new prompt

3. **Given** all phases are completed
   **When** I submit final review phase
   **Then** Feature status changes to "completed" and workflow ends

---

### User Story 7 - Agent Delegation (Priority: P2)

**As a** developer managing complex tasks
**I want to** delegate work to specialized AI agents
**So that** tasks run in parallel without blocking

**Why this priority**: Advanced feature for power users

**Independent Test**: Delegate tasks to Jules, Copilot, Gemini, Qwen and track status

**Acceptance Scenarios**:

1. **Given** I have a complex refactoring task
   **When** I run `cde_selectAgent("Refactor adapters to use dependency injection")`
   **Then** I get recommended agent (Jules for complex tasks) with reasoning

2. **Given** agent is selected
   **When** I run `cde_executeWithBestAgent("Refactor adapters...")`
   **Then** Task executes with selected agent and returns detailed results

3. **Given** task is delegated via CEO orchestrator
   **When** I run `cde_delegateTask(task_description="...", preferred_agent="jules")`
   **Then** Task is queued and I receive task_id for tracking

4. **Given** task is running
   **When** I run `cde_getTaskStatus(task_id="uuid")`
   **Then** I get current status (queued, running, completed, failed, cancelled)

---

### User Story 8 - Onboarding & Project Setup (Priority: P2)

**As a** new developer joining the project
**I want to** auto-analyze project structure and generate onboarding docs
**So that** I understand the codebase quickly

**Why this priority**: Improves developer experience but not critical

**Independent Test**: Run onboarding on CDE project itself

**Acceptance Scenarios**:

1. **Given** CDE project is open
   **When** I run `cde_onboardingProject(project_path=".")`
   **Then** Project structure is analyzed and onboarding recommendations are generated

2. **Given** onboarding analysis is complete
   **When** I run `cde_setupProject(project_path=".")`
   **Then** Configuration files (.gitignore, AGENTS.md) are generated

3. **Given** onboarding documents are reviewed
   **When** I run `cde_publishOnboarding(documents={...}, approve=True)`
   **Then** Documents are written to repository with proper frontmatter

---

### User Story 9 - Progress Reporting & Extensions (Priority: P3)

**As a** developer using long-running tools
**I want to** see real-time progress in VS Code
**So that** I know tasks are executing successfully

**Why this priority**: Nice-to-have UX enhancement

**Independent Test**: Install extension and test progress reporting

**Acceptance Scenarios**:

1. **Given** MCP status bar extension is not installed
   **When** I run `cde_installMcpExtension(extension_name="mcp-status-bar")`
   **Then** Extension is installed and activated in VS Code

2. **Given** extension is installed
   **When** I run `cde_testProgressReporting(duration=10, steps=5)`
   **Then** Progress updates appear in VS Code status bar at each step

3. **Given** long-running tool is executing
   **When** Progress is reported
   **Then** Status bar shows current operation and percentage complete

---

### User Story 10 - Tool Discovery (Priority: P2)

**As a** developer learning CDE MCP
**I want to** search available tools by keyword
**So that** I discover relevant tools without reading full docs

**Why this priority**: Improves discoverability and reduces cognitive load

**Independent Test**: Search for tools by category (workflow, skills, agents, documentation)

**Acceptance Scenarios**:

1. **Given** I want to find workflow-related tools
   **When** I run `cde_searchTools("workflow", detail_level="name_only")`
   **Then** I get list of tool names: ["cde_selectWorkflow", "cde_startFeature", "cde_submitWork"]

2. **Given** I want details about specific tools
   **When** I run `cde_searchTools("skill", detail_level="name_and_description")`
   **Then** I get tool names, descriptions, and tags for skill-related tools

3. **Given** I need full schema for a tool
   **When** I run `cde_searchTools("scanDocumentation", detail_level="full_schema")`
   **Then** I get complete parameter schemas and return types

---

### Edge Cases

- **Empty project**: What happens when running tools on a project with no `.cde/` or `specs/`?
- **Invalid frontmatter**: How do tools handle .md files with malformed YAML?
- **Network failures**: How does `cde_sourceSkill` handle GitHub API rate limits?
- **Concurrent operations**: What happens if two features are started simultaneously?
- **Missing dependencies**: How do agent tools (Jules, Copilot) handle missing CLI tools?
- **Circular skill references**: What if skill A references skill B which references skill A?
- **Large repositories**: How do documentation tools perform on repos with 1000+ .md files?
- **Permission errors**: How do file-writing tools handle read-only directories?

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST execute all 27 `cde_*` tools successfully on CDE project
- **FR-002**: System MUST identify Spec-Kit conformity gaps and generate fixes
- **FR-003**: System MUST track feedback for each tool (usability, bugs, improvements)
- **FR-004**: System MUST generate compliance report comparing CDE templates vs Spec-Kit
- **FR-005**: System MUST validate tool outputs against documented return schemas
- **FR-006**: System MUST test tools in realistic user scenarios (not just unit tests)
- **FR-007**: System MUST document tool interactions (which tools depend on others)
- **FR-008**: System MUST measure token efficiency for documentation tools
- **FR-009**: System MUST validate pre-commit hooks block governance violations
- **FR-010**: System MUST test tool error handling with invalid inputs

### Non-Functional Requirements

- **NFR-001**: Tool execution MUST complete within documented timeout (30 min default)
- **NFR-002**: Documentation scans MUST handle 500+ files without memory issues
- **NFR-003**: Feedback collection MUST be structured (JSON schema for consistency)
- **NFR-004**: Tool testing MUST be reproducible (deterministic results)
- **NFR-005**: Feedback report MUST be actionable (specific line numbers, file paths)
- **NFR-006**: Progress reporting MUST update at least every 10 seconds
- **NFR-007**: Tool discovery MUST return results in <2 seconds
- **NFR-008**: Skill sourcing MUST handle 10+ skills without rate limiting
- **NFR-009**: Agent delegation MUST support 5+ concurrent tasks
- **NFR-010**: Health checks MUST complete in <5 seconds

---

## Success Metrics

1. **Tool Coverage**: 27/27 tools tested (100%)
2. **Spec-Kit Conformity**: 95%+ template compliance
3. **Bug Discovery**: 10+ actionable issues identified
4. **Documentation Gaps**: 20+ missing examples/clarifications found
5. **UX Improvements**: 15+ usability enhancements proposed
6. **Feedback Completeness**: 100% of tools have structured feedback
7. **Reproducibility**: 100% of tests can be re-run deterministically
8. **Token Efficiency**: 90%+ reduction using progressive disclosure (vs loading all docs)

---

## Out of Scope

- **Performance benchmarking**: Focus on functionality, not optimization
- **UI development**: No custom dashboards (use existing VS Code UI)
- **External integrations**: No new tool adapters (Jules, Copilot, etc.)
- **Refactoring existing code**: Only document issues, don't fix architecture
- **Multi-language support**: Only test with Python/English
- **Security audits**: Trust existing security practices

---

## Dependencies

### Tools Required
- VS Code with MCP extension
- GitHub CLI (`gh`)
- Git
- Python 3.11+
- FastMCP server running

### Project Requirements
- CDE MCP project with latest code
- `.cde/` recipes downloaded
- `specs/` documentation structure
- Pre-commit hooks installed

### External Services
- GitHub (for skill sourcing)
- awesome-claude-skills repo (public, no auth)
- agents-flows-recipes repo (public, no auth)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Tools modify production code | HIGH | Run in feature branch, review all changes |
| Network failures during skill sourcing | MEDIUM | Cache downloaded skills, retry logic |
| Long execution times block workflow | MEDIUM | Use async delegation for complex tasks |
| Feedback collection is subjective | LOW | Use structured JSON schema with categories |
| Documentation changes break links | LOW | Run link checker before committing |
| Rate limiting on GitHub API | LOW | Respect rate limits, use tokens if needed |

---

## Appendix: All 27 CDE MCP Tools

### Orchestration (5 tools)
1. `cde_selectWorkflow` - Analyze prompt and recommend workflow
2. `cde_sourceSkill` - Download skills from external repos
3. `cde_updateSkill` - Research and update skill with latest info
4. `cde_startFeature` - Start new feature in project
5. `cde_submitWork` - Submit phase results and advance workflow

### Documentation (3 tools)
6. `cde_scanDocumentation` - Scan and analyze documentation structure
7. `cde_analyzeDocumentation` - Deep analysis of documentation quality
8. `cde_createSpecification` - Create specification document

### Agents (4 tools)
9. `cde_listAvailableAgents` - Check which agents are ready
10. `cde_selectAgent` - Select best agent for task
11. `cde_executeWithBestAgent` - Execute with best available agent
12. `cde_delegateToJules` - Delegate to Jules agent specifically

### CEO Orchestration (5 tools)
13. `cde_delegateTask` - Delegate task to CEO agent manager
14. `cde_getTaskStatus` - Check status of delegated task
15. `cde_listActiveTasks` - List all active tasks
16. `cde_getWorkerStats` - Get worker pool statistics
17. `cde_cancelTask` - Cancel queued or running task

### Onboarding (3 tools)
18. `cde_onboardingProject` - Analyze project and generate onboarding
19. `cde_setupProject` - Generate configuration files
20. `cde_publishOnboarding` - Publish onboarding documents

### Recipes (2 tools)
21. `cde_downloadRecipes` - Download workflow recipes from GitHub
22. `cde_checkRecipes` - Check if recipes exist

### Extensions (1 tool)
23. `cde_installMcpExtension` - Install MCP-related VS Code extensions

### Health (1 tool)
24. `cde_healthCheck` - Check system health status

### Full Implementation (1 tool)
25. `cde_executeFullImplementation` - Execute complete workflow implementation

### Utilities (2 tools)
26. `cde_searchTools` - Search available tools by keyword
27. `cde_testProgressReporting` - Test progress reporting for status bar

---

## References

- **Spec-Kit Official**: https://github.com/github/spec-kit
- **CDE Governance**: `specs/governance/DOCUMENTATION_GOVERNANCE.md`
- **CDE Architecture**: `specs/design/architecture/README.md`
- **CDE Constitution**: `memory/constitution.md`
- **Agent Instructions**: `AGENTS.md`, `.github/copilot-instructions.md`
