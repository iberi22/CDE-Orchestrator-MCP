---
title: "Feature Specification: AI Assistant Configuration System"
description: "Automatic detection and configuration of AI coding assistants during project onboarding"
type: "feature"
status: "completed"
created: "2025-11-01"
updated: "2025-11-23"
author: "CDE Team"
version: "1.0.0"
llm_summary: |
  Feature specification for automatic AI assistant configuration. Detects installed
  AI coding tools (Copilot, Gemini, Claude, Cursor, Windsurf, Amp) and generates
  optimized instruction files during project onboarding. Inspired by Spec-Kit's
  multi-agent approach. STATUS: ✅ IMPLEMENTED v1.0.0
---

## Feature Specification: AI Assistant Configuration System

**Feature Branch**: `ai-assistant-config`
**Created**: 2025-11-01
**Status**: ✅ Completed (v1.0.0)
**Input**: User runs `cde_onboardingProject()` MCP tool

## Executive Summary

**Problem**: AI coding assistants require project-specific instruction files (AGENTS.md, GEMINI.md, copilot-instructions.md) to understand project context. Manually creating these files is time-consuming and error-prone.

**Solution**: Automatic detection of installed AI assistants during onboarding, followed by generation of optimized, project-aware instruction files.

**Status**: ✅ Implemented and validated (v1.0.0)

**Inspiration**: GitHub's [Spec-Kit](https://github.com/github/spec-kit) multi-agent support patterns.

---

## User Scenarios & Testing

### User Story 1 - New Project Onboarding (Priority: P1) 🎯 MVP

**Actor**: Developer onboarding a new project

**Flow**:

1. Developer runs `cde_onboardingProject()` MCP tool
2. System detects installed AI assistants (e.g., Copilot, Gemini, Cursor)
3. System generates AGENTS.md, GEMINI.md, copilot-instructions.md
4. Developer immediately uses any detected AI assistant with project context

**Outcome**: Project is ready for multi-agent development in <10 seconds

**Independent Test**: Run `cde_onboardingProject()` on fresh project, verify all 3 instruction files are created.

**Acceptance Scenarios**:

1. **Given** a new project with no AI config files, **When** developer runs onboarding, **Then** system generates AGENTS.md, GEMINI.md, and copilot-instructions.md
2. **Given** Copilot and Gemini are installed, **When** onboarding completes, **Then** both assistants can read their specific instruction files

---

### User Story 2 - Existing Project Update (Priority: P2)

**Actor**: Developer updating AI instructions

**Flow**:

1. Developer modifies project structure or adds new conventions
2. Developer re-runs onboarding with `force=True`
3. System regenerates instruction files with updated context
4. All AI assistants receive updated instructions

**Outcome**: AI assistants stay synchronized with project evolution

**Independent Test**: Modify project, re-run onboarding with force, verify instruction files are updated.

**Acceptance Scenarios**:

1. **Given** existing AI config files, **When** developer runs onboarding with `force=True`, **Then** system overwrites files with updated context
2. **Given** project has new architecture docs, **When** onboarding regenerates files, **Then** new context appears in instruction files

---

### User Story 3 - Team Standardization (Priority: P3)

**Actor**: Team lead standardizing AI usage

**Flow**:

1. Team lead configures CDE with company-specific templates
2. All team members run onboarding on their projects
3. All projects generate consistent AI instruction files
4. Team has standardized AI assistant behavior

**Outcome**: Consistent AI coding patterns across team

**Independent Test**: Configure templates, run onboarding on 3 projects, verify all use same template structure.

**Acceptance Scenarios**:

1. **Given** custom templates in `.cde/templates/`, **When** team members run onboarding, **Then** all projects use custom templates

---

### Edge Cases

- What happens when no AI assistants are detected?
  → System skips AI config generation, onboarding completes normally
- What happens when CLI tools timeout (>2s)?
  → System logs warning, continues with folder detection
- What happens when file write fails (permissions)?
  → System logs error, adds to errors list, continues with other files

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST detect CLI-based AI tools (gemini, claude, amp) via subprocess execution
- **FR-002**: System MUST detect IDE-based AI tools (Copilot, Cursor, Windsurf) via folder detection
- **FR-003**: System MUST generate AGENTS.md with universal instructions for all agents
- **FR-004**: System MUST generate GEMINI.md with Gemini-optimized format
- **FR-005**: System MUST generate .github/copilot-instructions.md for Copilot
- **FR-006**: System MUST skip existing files by default to preserve user edits
- **FR-007**: System MUST support force overwrite mode via `force=True` parameter
- **FR-008**: System MUST include project-specific context (name, architecture, tech stack) in templates
- **FR-009**: System MUST handle detection failures gracefully without crashing
- **FR-010**: System MUST provide configuration summary showing detected agents and generated files

### Non-Functional Requirements

- **NFR-001**: Detection completes in <3 seconds (✅ Achieved: ~2s)
- **NFR-002**: Template generation <1 second per file (✅ Achieved: <0.5s)
- **NFR-003**: Support Windows, macOS, Linux (✅ Achieved via cross-platform subprocess)
- **NFR-004**: Handle missing CLI tools gracefully (✅ Achieved: logs debug, continues)
- **NFR-005**: Provide clear error messages (✅ Achieved: structured error logging)
- **NFR-006**: Log all detection and generation operations (✅ Achieved: debug, info, warning levels)
- **NFR-007**: Thread-safe for concurrent operations (⏳ Future enhancement)

---

## Key Entities

- **AIAssistantConfigurator**: Main class orchestrating detection and generation
  - Attributes: `project_root`, `detected_agents`, `generated_files`
  - Methods: `detect_installed_agents()`, `generate_config_files()`, `get_configuration_summary()`

- **AgentConfig**: Configuration for each AI assistant
  - Attributes: `name`, `key`, `folder`, `install_url`, `requires_cli`, `config_files`

- **Template**: Instruction file content (AGENTS.md, GEMINI.md, copilot-instructions.md)
  - Attributes: `content`, `variables`, `file_path`

---

## AI Assistants Supported

| Assistant | Key | Detection Method | CLI Tool | Config Files Generated |
|-----------|-----|------------------|----------|------------------------|
| **GitHub Copilot** | `copilot` | Folder: `.github/copilot/` | ❌ | `.github/copilot-instructions.md`, `AGENTS.md` |
| **Gemini CLI** | `gemini` | CLI: `gemini --version` | ✅ | `GEMINI.md`, `AGENTS.md` |
| **Claude Code** | `claude` | CLI: `claude --version` | ✅ | `AGENTS.md` |
| **Cursor** | `cursor` | Folder: `.cursor/` | ❌ | `AGENTS.md` |
| **Windsurf** | `windsurf` | Folder: `.windsurf/` | ❌ | `AGENTS.md` |
| **Amp** | `amp` | CLI: `amp --version` | ✅ | `AGENTS.md` |

---

## Architecture

### Component Diagram

```text
┌─────────────────────────────────────────────────────────────┐
│                    MCP Tool Layer                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ cde_onboardingProject()                              │   │
│  └───────────────────────┬─────────────────────────────┘   │
└────────────────────────────┼─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  Application Layer                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ OnboardingAnalyzer                                   │   │
│  │  ├─ analyze()                                        │   │
│  │  └─ SpecKitStructureGenerator                       │   │
│  │      └─ create_structure()                           │   │
│  └───────────────────────┬─────────────────────────────┘   │
└────────────────────────────┼─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ AIAssistantConfigurator                              │   │
│  │  ├─ detect_installed_agents()                        │   │
│  │  │   ├─ _check_cli_tool()                            │   │
│  │  │   └─ _check_folder()                              │   │
│  │  ├─ generate_config_files()                          │   │
│  │  │   ├─ _generate_agents_md()                        │   │
│  │  │   ├─ _generate_gemini_md()                        │   │
│  │  │   └─ _generate_copilot_config()                   │   │
│  │  └─ get_configuration_summary()                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                Infrastructure Layer                          │
│  ┌─────────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │ subprocess.run  │  │ Path.exists  │  │ File I/O      │ │
│  │ (CLI detection) │  │ (folder det.)│  │ (write files) │ │
│  └─────────────────┘  └──────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Validation

### Live Demo Results (2025-11-01)

**Project**: CDE Orchestrator MCP (this project)

**Results**:

```text
✓ Detected: 4 AI assistants (Claude, Gemini, Cursor, Copilot)
✓ Generated: AGENTS.md (9.2 KB)
✓ Generated: GEMINI.md (16.3 KB)
✓ Generated: copilot-instructions.md (23.2 KB)
✓ Detection time: <2 seconds
✓ No errors
```

**Conclusion**: ✅ Feature fully operational

---

## References

- **Implementation**: `src/cde_orchestrator/ai_assistant_configurator.py`
- **Tests**: `tests/unit/test_ai_assistant_configurator.py`
- **Plan**: `specs/ai-assistant-config/plan.md`
- **Tasks**: `specs/ai-assistant-config/tasks.md`
- **Spec-Kit Repository**: [https://github.com/github/spec-kit](https://github.com/github/spec-kit)

---

## Changelog

### v1.0.0 (2025-11-01)

- ✅ Initial implementation
- ✅ Support for 6 AI assistants
- ✅ Auto-detection (CLI + folders)
- ✅ Template generation (3 files)
- ✅ Integration with onboarding
- ✅ Comprehensive test suite (20+ tests)
- ✅ Full documentation
- ✅ Live demo validation

---

**Status**: ✅ **PRODUCTION READY** (v1.0.0)
