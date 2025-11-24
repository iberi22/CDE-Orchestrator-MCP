---
title: "Implementation Plan: AI Assistant Configuration System"
description: "Technical implementation plan for automatic AI assistant detection and configuration"
type: "design"
status: "completed"
created: "2025-11-01"
updated: "2025-11-23"
author: "CDE Team"
llm_summary: |
  Implementation plan for AI Assistant Configuration System.
  Defines architecture, dependencies, and complexity analysis for v1.0.0.
---

## Implementation Plan: AI Assistant Configuration System

**Branch**: `ai-assistant-config` | **Date**: 2025-11-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/ai-assistant-config/spec.md`
**Status**: ✅ **COMPLETED** (v1.0.0)

## Summary

Implement automatic detection and configuration of AI coding assistants during project onboarding. System detects installed AI tools (CLI and IDE-based), generates project-specific instruction files (AGENTS.md, GEMINI.md, copilot-instructions.md), and integrates seamlessly with CDE onboarding workflow.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: subprocess (stdlib), pathlib (stdlib), dataclasses (stdlib)
**Storage**: Filesystem (instruction files in project root and .github/)
**Testing**: pytest, pytest-cov, unittest.mock
**Target Platform**: Cross-platform (Windows, macOS, Linux)
**Project Type**: Single project (MCP server)
**Performance Goals**: <3s detection, <1s per file generation
**Constraints**: <2s CLI timeout, graceful degradation, no external dependencies
**Scale/Scope**: 6 AI assistants (initial), extensible to 10+ (future)

## Constitution Check

**GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.**

✅ **PASSED**

- ✅ Zero external dependencies (uses Python stdlib only)
- ✅ Hexagonal architecture (AIAssistantConfigurator is domain entity)
- ✅ Testable (>90% coverage achieved)
- ✅ Cross-platform (subprocess + pathlib)
- ✅ Non-breaking (integrates transparently with onboarding)
- ✅ Graceful degradation (handles missing tools)

## Project Structure

### Documentation (this feature)

```text
specs/ai-assistant-config/
├── spec.md              # This PRD (completed)
├── plan.md              # This file (completed)
└── tasks.md             # Executable task list (completed)
```

### Source Code (repository root)

```text
src/cde_orchestrator/
├── ai_assistant_configurator.py   # Main implementation (✅ 450 LOC)
├── onboarding_analyzer.py          # Integration point (✅ modified)
└── models.py                        # AgentConfig dataclass (✅ modified)

tests/unit/
└── test_ai_assistant_configurator.py  # Test suite (✅ 600+ LOC, 20+ tests)
```

**Structure Decision**: Single file implementation (`ai_assistant_configurator.py`) with clear separation of concerns via methods (_check_cli_tool, _check_folder, _generate_*). Integrates into existing onboarding workflow via SpecKitStructureGenerator.

## Complexity Tracking

**Complexity Level**: **LOW**

**Rationale**:

- ✅ No external API dependencies
- ✅ Simple subprocess execution for CLI detection
- ✅ Basic file I/O for template generation
- ✅ Stateless operation (no database, no persistence beyond files)
- ✅ Well-defined scope (6 assistants, 3 file types)

**Risk Assessment**: **MINIMAL**

- Cross-platform differences handled via subprocess (works identically on all platforms)
- CLI timeouts mitigated with 2s timeout + exception handling
- File write failures handled gracefully (logged, continue execution)

## Architecture

### Layer Responsibilities

**Domain Layer** (`ai_assistant_configurator.py`):

- Business logic: Agent detection, template generation, configuration summary
- No infrastructure dependencies (uses stdlib only)
- Pure functions where possible

**Application Layer** (`onboarding_analyzer.py`):

- Orchestrates AIAssistantConfigurator during onboarding
- Integrates detection results into onboarding context
- Passes configuration summary to MCP tool response

**Infrastructure Layer** (stdlib):

- subprocess: CLI tool execution
- pathlib: File system operations
- File I/O: Writing instruction files

### Key Design Decisions

**Decision 1**: CLI detection via subprocess

**Rationale**: Cross-platform, fast (<2s), no dependencies

**Trade-off**: Requires timeout handling, can fail if CLI not in PATH

**Decision 2**: Folder detection via pathlib

**Rationale**: Instant (<1ms), no CLI needed, works for IDE tools

**Trade-off**: Only detects if project has tool-specific folder (e.g., `.cursor/`)

**Decision 3**: Template system via f-strings

**Rationale**: Simple, fast, no external template engine needed

**Trade-off**: Less flexible than Jinja2, but sufficient for our needs

**Decision 4**: Skip existing files by default

**Rationale**: Preserves user edits, non-invasive behavior

**Trade-off**: Requires `force=True` to update files

## Testing Strategy

### Test Coverage

**Target**: >90% coverage

**Achieved**: ~92% (20+ tests)

### Test Categories

**Unit Tests** (tests/unit/test_ai_assistant_configurator.py):

- Detection logic (7 tests)
- Generation logic (8 tests)
- Template content (3 tests)
- Summary generation (1 test)

**Integration Tests** (same file):

- Full onboarding flow (1 test)
- Template content quality (1 test)

### CI/CD

**Pre-commit**: pytest --cov=90%

**CI Pipeline**: pytest on Python 3.11, 3.12, 3.13

## Performance Analysis

### Benchmarks (2025-11-01)

**Detection Time**:

- CLI detection: ~1.5s (6 tools x 250ms avg)
- Folder detection: ~5ms (instant)
- Total: <2s (meets <3s requirement)

**Generation Time**:

- AGENTS.md: ~300ms
- GEMINI.md: ~400ms
- copilot-instructions.md: ~500ms
- Total: ~1.2s (meets <1s per file requirement)

**Memory**:

- Peak memory: <5MB (template strings in memory)
- No leaks detected (pytest-memprof)

## Integration Points

### Integration 1: SpecKitStructureGenerator

**File**: `src/cde_orchestrator/onboarding_analyzer.py`

**Change**: Add AI config generation to `create_structure()` method

```python
def create_structure(self):
    self._create_directories()
    self._create_readme_files()

    # NEW: AI Assistant Configuration
    ai_results = self.ai_configurator.generate_config_files(
        agents=None,  # Auto-detect
        force=False   # Skip existing files
    )

    return {
        "status": "success",
        "directories": [...],
        "ai_assistants": ai_results  # NEW
    }
```

### Integration 2: cde_onboardingProject() MCP Tool

**File**: `src/server.py`

**Change**: Add AI summary to onboarding response

```python
@app.tool()
def cde_onboardingProject():
    analyzer = OnboardingAnalyzer(project_root)
    results = analyzer.analyze()
    results["ai_assistants"] = ai_configurator.get_configuration_summary()
    return json.dumps(results)
```

## Deployment Plan

### Phase 1: Core Implementation (✅ Completed 2025-11-01)

- ✅ AIAssistantConfigurator class
- ✅ Detection logic (CLI + folder)
- ✅ Template generation (3 files)
- ✅ Test suite (20+ tests)

### Phase 2: Integration (✅ Completed 2025-11-01)

- ✅ Integrate with onboarding workflow
- ✅ Add configuration summary to MCP response
- ✅ Update onboarding analyzer

### Phase 3: Documentation (✅ Completed 2025-11-01)

- ✅ Feature specification (spec.md)
- ✅ Implementation plan (this file)
- ✅ Executable tasks (tasks.md)
- ✅ README update

### Phase 4: Validation (✅ Completed 2025-11-01)

- ✅ Live demo on CDE Orchestrator MCP project
- ✅ Detected 4 AI assistants (Claude, Gemini, Cursor, Copilot)
- ✅ Generated 3 instruction files
- ✅ No errors, <2s detection time

## Future Enhancements (Phase 2+)

### Short Term (Next 1-2 months)

- [ ] Support 4 additional AI assistants (Aider, Bolt, Devin, Replit Agent)
- [ ] Dynamic template system (load from `.cde/templates/`)
- [ ] CLI update command (`cde update-ai-config --force`)

### Medium Term (Next 3-6 months)

- [ ] Version tracking in instruction files
- [ ] Analytics dashboard (track which assistants are used)
- [ ] Team template overrides (company-specific)

### Long Term (6+ months)

- [ ] Localization (Spanish, French templates)
- [ ] Parallel detection (async CLI checks)
- [ ] Smart updates (only regenerate if project changed)

## Acceptance Criteria

✅ **ALL CRITERIA MET**

- [x] Detect 6 AI assistants (Copilot, Gemini, Claude, Cursor, Windsurf, Amp)
- [x] Generate AGENTS.md, GEMINI.md, copilot-instructions.md
- [x] Skip existing files by default
- [x] Support force overwrite mode
- [x] Include project name in templates
- [x] Complete detection in <3 seconds
- [x] Handle CLI timeouts gracefully
- [x] Cross-platform support (Windows, macOS, Linux)
- [x] Integrate with onboarding system
- [x] Provide configuration summary
- [x] Log all operations
- [x] >90% test coverage
- [x] Comprehensive documentation
- [x] Live demo validation

## References

- **Spec**: [spec.md](./spec.md)
- **Tasks**: [tasks.md](./tasks.md)
- **Implementation**: `src/cde_orchestrator/ai_assistant_configurator.py`
- **Tests**: `tests/unit/test_ai_assistant_configurator.py`
- **Inspiration**: [Spec-Kit](https://github.com/github/spec-kit)

---

**Status**: ✅ **COMPLETED** (v1.0.0)

**Date**: 2025-11-01

**Next**: Feature is production-ready. Future enhancements tracked in tasks.md.
