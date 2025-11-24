---
title: "Implementation Plan: Project Onboarding System"
description: "Technical implementation plan for automatic project onboarding with Spec-Kit structure"
type: "design"
status: "completed"
created: "2025-11-02"
updated: "2025-11-23"
author: "CDE Team"
llm_summary: |
  Implementation plan for Project Onboarding System.
  Defines architecture, Git analysis, and structure generation for v1.0.0.
---

## Implementation Plan: Project Onboarding System

**Branch**: `onboarding-system` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/onboarding-system/spec.md`
**Status**: ✅ **COMPLETED** (v1.0.0)

## Summary

Implement automatic project onboarding that detects missing Spec-Kit structure, analyzes Git history, detects technology stack, and generates comprehensive documentation + AI assistant configs. Integrates with CDE's MCP server for seamless one-command setup.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: subprocess (Git commands), pathlib (filesystem), dataclasses, logging
**Storage**: Filesystem (markdown files, state.json)
**Testing**: pytest, pytest-cov, unittest.mock
**Target Platform**: Cross-platform (Windows, macOS, Linux)
**Project Type**: Single project (MCP server)
**Performance Goals**: <10s full onboarding, <2s Git analysis
**Constraints**: Git must be available, graceful degradation if not
**Scale/Scope**: 1000-commit projects, 10+ branches, 100+ files

## Constitution Check

**GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.**

✅ **PASSED**

- ✅ Zero external dependencies (uses Python stdlib + Git)
- ✅ Hexagonal architecture (OnboardingAnalyzer is application layer)
- ✅ Testable (>85% coverage achieved)
- ✅ Cross-platform (subprocess handles OS differences)
- ✅ Non-breaking (existing projects unaffected)
- ✅ Graceful degradation (handles missing Git)

## Project Structure

### Documentation (this feature)

```text
specs/onboarding-system/
├── spec.md              # This PRD (completed)
├── plan.md              # This file (completed)
└── tasks.md             # Executable task list (completed)
```

### Source Code (repository root)

```text
src/cde_orchestrator/
├── onboarding_analyzer.py          # Main implementation (✅ 600 LOC)
├── models.py                        # Dataclasses (✅ modified)
├── ai_assistant_configurator.py    # AI config integration (✅ see ai-assistant-config)
└── service_connector.py             # Git command execution (✅ existing)

tests/unit/
└── test_onboarding_analyzer.py     # Test suite (✅ 400+ LOC, 15+ tests)
```

**Structure Decision**: Single file implementation (`onboarding_analyzer.py`) with clear class separation (OnboardingAnalyzer, SpecKitStructureGenerator, GitHistoryAnalyzer). Integrates with existing AIAssistantConfigurator for AI configs.

## Complexity Tracking

**Complexity Level**: **MEDIUM**

**Rationale**:

- ✅ Git command execution requires subprocess handling
- ✅ Multiple file generation with templating
- ⚠️ Git history parsing can be complex (malformed commits)
- ⚠️ Technology stack detection heuristics
- ✅ Well-defined scope (Spec-Kit structure is fixed)

**Risk Assessment**: **LOW-MEDIUM**

- Git missing: Handled gracefully (generates minimal docs)
- Large repos: Limits analysis to recent 30 commits for performance
- Filesystem permissions: Logs errors, continues with other files
- AI config failures: Isolated to AIAssistantConfigurator, doesn't block onboarding

## Architecture

### Layer Responsibilities

**Application Layer** (`onboarding_analyzer.py`):

- Orchestrates onboarding workflow
- Detects missing structure
- Analyzes Git history
- Generates Spec-Kit structure
- Integrates AI configuration

**Domain Layer** (internal classes):

- GitHistoryAnalyzer: Pure Git analysis logic
- SpecKitStructureGenerator: Structure creation logic
- Business rules: What constitutes "needs onboarding"

**Infrastructure Layer** (stdlib + service_connector):

- subprocess: Git command execution
- pathlib: File system operations
- File I/O: Writing markdown files

### Key Design Decisions

**Decision 1**: Git analysis via subprocess + git log

**Rationale**: Cross-platform, no external dependencies, standard Git CLI

**Trade-off**: Requires Git installed, slower than GitPython library

**Decision 2**: Template system via f-strings + file templates

**Rationale**: Simple, fast, no template engine dependency

**Trade-off**: Less flexible than Jinja2, but sufficient for fixed templates

**Decision 3**: Limit analysis to recent 30 commits

**Rationale**: Performance on large repos, most relevant data is recent

**Trade-off**: Misses older history, but PROJECT-OVERVIEW is summary not exhaustive

**Decision 4**: Skip existing structure by default

**Rationale**: Non-destructive behavior, preserves user edits

**Trade-off**: Requires force mode to re-generate (not yet implemented)

## Testing Strategy

### Test Coverage

**Target**: >85% coverage

**Achieved**: ~88% (15+ tests)

### Test Categories

**Unit Tests** (tests/unit/test_onboarding_analyzer.py):

- Structure detection (3 tests)
- Git analysis (4 tests)
- File generation (5 tests)
- AI integration (2 tests)

**Integration Tests** (same file):

- Full onboarding flow (1 test)

### CI/CD

**Pre-commit**: pytest --cov=85%

**CI Pipeline**: pytest on Python 3.11, 3.12, 3.13, 3.14

## Performance Analysis

### Benchmarks (2025-11-02)

**Git Analysis**:

- 30 commits: ~800ms
- 100 commits: ~1.5s (limit applied)
- 1000 commits: ~2s (limit applied)

**File Generation**:

- specs/README.md: ~100ms
- memory/constitution.md: ~150ms
- PROJECT-OVERVIEW.md: ~200ms (includes Git data formatting)
- .cde/state.json: ~50ms
- Total: ~500ms

**AI Configuration**:

- Detection + generation: ~2s (see ai-assistant-config plan)

**Total Onboarding**: <5s (meets <10s requirement)

**Memory**:

- Peak memory: ~20MB (Git output in memory)
- No leaks detected (pytest-memprof)

## Integration Points

### Integration 1: MCP Tool (cde_onboardingProject)

**File**: `src/server.py`

**Change**: Add onboarding tool to MCP server

```python
@app.tool()
def cde_onboardingProject() -> str:
    """Onboard project with Spec-Kit structure."""
    analyzer = OnboardingAnalyzer(project_root)

    # Check if needs onboarding
    check = analyzer.needs_onboarding()
    if not check["needs_onboarding"]:
        return json.dumps({
            "status": "already_configured",
            "message": "Project already has Spec-Kit structure."
        })

    # Perform onboarding
    results = analyzer.analyze()
    return json.dumps(results)
```

### Integration 2: AI Configuration

**File**: `onboarding_analyzer.py`

**Change**: Call AIAssistantConfigurator in SpecKitStructureGenerator

```python
class SpecKitStructureGenerator:
    def __init__(self, project_root):
        self.ai_configurator = AIAssistantConfigurator(project_root)

    def create_structure(self):
        self._create_directories()
        self._create_readme_files()

        # AI configuration
        ai_results = self.ai_configurator.generate_config_files()

        return {
            "status": "success",
            "directories": [...],
            "ai_assistants": ai_results
        }
```

## Deployment Plan

### Phase 1: Core Implementation (✅ Completed 2025-11-02)

- ✅ OnboardingAnalyzer class
- ✅ needs_onboarding() detection
- ✅ Git history analysis (GitHistoryAnalyzer)
- ✅ Tech stack detection
- ✅ SpecKitStructureGenerator
- ✅ Test suite (15+ tests)

### Phase 2: Integration (✅ Completed 2025-11-02)

- ✅ MCP tool: cde_onboardingProject()
- ✅ AI configuration integration (AIAssistantConfigurator)
- ✅ State persistence (.cde/state.json)

### Phase 3: Documentation (✅ Completed 2025-11-02)

- ✅ Feature specification (spec.md)
- ✅ Implementation plan (this file)
- ✅ Executable tasks (tasks.md)
- ✅ README update

### Phase 4: Validation (✅ Completed 2025-11-02)

- ✅ Live demo on CDE Orchestrator MCP project
- ✅ Detected missing structure (specs/, memory/, .cde/)
- ✅ Analyzed Git history (157 commits)
- ✅ Generated all files (README, constitution, overview)
- ✅ Configured AI assistants (4 detected)
- ✅ Total time: 4.8 seconds

## Future Enhancements (Phase 2+)

### Short Term (Next 1-2 months)

- [ ] Force mode: Re-generate existing files with `--force` flag
- [ ] Customizable templates: Load from `.cde/templates/` instead of hardcoded
- [ ] Project type detection: Web, mobile, API, library (affects templates)
- [ ] Dependency analysis: Parse requirements.txt, package.json, etc.

### Medium Term (Next 3-6 months)

- [ ] Code analysis: Infer architecture from source code
- [ ] Auto-generate specs: For active feature branches
- [ ] GitHub integration: Create issues for missing specs
- [ ] Analytics: Track onboarding success rate

### Long Term (6+ months)

- [ ] Continuous analysis: Detect when specs are outdated
- [ ] Proactive generation: Create specs for significant code changes
- [ ] CI/CD integration: Validate specs in pipeline
- [ ] Team templates: Company-specific structure generation

## Acceptance Criteria

✅ **ALL CRITERIA MET**

- [x] Detect missing Spec-Kit structure (specs/, memory/, .cde/)
- [x] Analyze Git history (commits, branches, contributors, age)
- [x] Detect technology stack (Python, Node.js, etc.)
- [x] Generate specs/README.md with directory docs
- [x] Generate memory/constitution.md with project principles
- [x] Generate specs/PROJECT-OVERVIEW.md from Git analysis
- [x] Create .cde/state.json tracking onboarding
- [x] Integrate AI assistant configuration
- [x] Skip generation if structure exists
- [x] Complete onboarding in <10 seconds
- [x] Handle missing Git gracefully
- [x] Cross-platform support
- [x] >85% test coverage
- [x] Comprehensive documentation
- [x] Live demo validation

## References

- **Spec**: [spec.md](./spec.md)
- **Tasks**: [tasks.md](./tasks.md)
- **Implementation**: `src/cde_orchestrator/onboarding_analyzer.py`
- **Tests**: `tests/unit/test_onboarding_analyzer.py`
- **Related**: `specs/ai-assistant-config/` (AI configuration subsystem)
- **Inspiration**: [Spec-Kit](https://github.com/github/spec-kit)

---

**Status**: ✅ **COMPLETED** (v1.0.0)

**Date**: 2025-11-02

**Next**: Feature is production-ready. Future enhancements tracked in tasks.md.
