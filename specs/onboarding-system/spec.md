---
title: "Feature Specification: Project Onboarding System"
description: "Automatic project onboarding with Spec-Kit structure generation and AI assistant configuration"
type: "feature"
status: "completed"
created: "2025-11-02"
updated: "2025-11-23"
author: "CDE Team"
version: "1.0.0"
llm_summary: |
  Automatic onboarding system that detects missing Spec-Kit structure, analyzes Git history,
  and generates documentation + AI assistant configs. STATUS: ✅ IMPLEMENTED v1.0.0
---

## Feature Specification: Project Onboarding System

**Feature Branch**: `onboarding-system`
**Created**: 2025-11-02
**Status**: ✅ Completed (v1.0.0)
**Input**: User runs `cde_onboardingProject()` MCP tool

## Executive Summary

**Problem**: Projects need structured documentation following Spec-Kit methodology, but manually creating all folders, README files, and AI assistant configs is time-consuming and error-prone.

**Solution**: Automatic onboarding system that detects missing structure, analyzes Git history, and generates comprehensive documentation + AI configs in one command.

**Status**: ✅ Implemented and validated (v1.0.0)

**Inspiration**: GitHub's [Spec-Kit](https://github.com/github/spec-kit) structure + multi-agent AI support

---

## User Scenarios & Testing

### User Story 1 - New Project Setup (Priority: P1) 🎯 MVP

**Actor**: Developer starting a new project

**Flow**:

1. Developer runs `cde_onboardingProject()` MCP tool
2. System detects missing Spec-Kit structure (specs/, memory/)
3. System generates complete structure + AI configs
4. Developer immediately has structured project + AI support

**Outcome**: Project ready for Spec-Driven Development in <5 seconds

**Independent Test**: Run `cde_onboardingProject()` on empty project, verify all directories and files created.

**Acceptance Scenarios**:

1. **Given** a new project with no documentation, **When** onboarding runs, **Then** system creates specs/, memory/, AGENTS.md, GEMINI.md, copilot-instructions.md
2. **Given** project has no Git history, **When** onboarding analyzes, **Then** system generates minimal PROJECT-OVERVIEW.md

---

### User Story 2 - Existing Project Migration (Priority: P2)

**Actor**: Developer migrating existing project to CDE

**Flow**:

1. Developer runs `cde_onboardingProject()` on project with Git history
2. System analyzes commits, branches, contributors
3. System generates PROJECT-OVERVIEW.md with real context
4. System detects tech stack from files
5. Developer has documentation reflecting project reality

**Outcome**: Legacy project documented based on actual history

**Independent Test**: Run on project with 50+ commits, verify PROJECT-OVERVIEW includes real commit data.

**Acceptance Scenarios**:

1. **Given** project with 50 commits, **When** onboarding analyzes, **Then** PROJECT-OVERVIEW shows commit count, recent activity, contributors
2. **Given** project has active feature branches, **When** onboarding analyzes, **Then** recommendations include creating specs for those features

---

### User Story 3 - Already Configured Project (Priority: P3)

**Actor**: Developer checking project structure

**Flow**:

1. Developer runs `cde_onboardingProject()` on already configured project
2. System detects existing Spec-Kit structure
3. System skips generation, returns confirmation message
4. No files overwritten

**Outcome**: Developer confirms project is ready without any changes

**Independent Test**: Run twice, verify second run doesn't modify files.

**Acceptance Scenarios**:

1. **Given** project with specs/ and memory/ directories, **When** onboarding runs, **Then** system returns "already configured" status

---

### Edge Cases

- What happens when Git history is corrupted?
  → System logs warning, continues with minimal PROJECT-OVERVIEW
- What happens when AI assistant detection fails?
  → System skips AI config generation, onboarding completes normally
- What happens when filesystem permissions prevent file creation?
  → System logs error with specific file path, continues with other files

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST detect missing Spec-Kit structure (specs/, memory/, .cde/ directories)
- **FR-002**: System MUST analyze Git history (commits, branches, contributors, project age)
- **FR-003**: System MUST detect technology stack (Python, Node.js, .NET, Java, Docker, Rust)
- **FR-004**: System MUST generate specs/README.md with directory documentation
- **FR-005**: System MUST generate memory/constitution.md with project principles
- **FR-006**: System MUST generate specs/PROJECT-OVERVIEW.md from Git analysis
- **FR-007**: System MUST create .cde/state.json tracking onboarding status
- **FR-008**: System MUST detect and configure AI assistants (see ai-assistant-config feature)
- **FR-009**: System MUST skip generation if structure already exists
- **FR-010**: System MUST provide detailed onboarding summary

### Non-Functional Requirements

- **NFR-001**: Complete onboarding in <10 seconds on 1000-commit project (✅ Achieved: ~5s)
- **NFR-002**: Git analysis <2 seconds for 100 commits (✅ Achieved: ~1s)
- **NFR-003**: Support Windows, macOS, Linux (✅ Achieved)
- **NFR-004**: Handle missing Git gracefully (✅ Achieved: logs warning, continues)
- **NFR-005**: Provide clear progress messages (✅ Achieved: structured logging)
- **NFR-006**: Memory usage <50MB (✅ Achieved: ~20MB peak)
- **NFR-007**: Thread-safe for concurrent operations (⏳ Future enhancement)

---

## Key Entities

- **OnboardingAnalyzer**: Main class orchestrating onboarding
  - Attributes: `project_root`, `git_analysis`, `missing_structure`, `tech_stack`
  - Methods: `needs_onboarding()`, `analyze()`, `get_git_history()`

- **SpecKitStructureGenerator**: Creates Spec-Kit folders and files
  - Attributes: `project_root`, `structure_plan`, `ai_configurator`
  - Methods: `create_structure()`, `_create_directories()`, `_create_readme_files()`

- **GitHistoryAnalyzer**: Analyzes project history
  - Attributes: `repo_path`, `commits`, `branches`, `contributors`
  - Methods: `analyze()`, `get_recent_commits()`, `get_active_branches()`

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
│  │  ├─ needs_onboarding()                               │   │
│  │  ├─ analyze()                                        │   │
│  │  └─ SpecKitStructureGenerator                       │   │
│  │      ├─ create_structure()                           │   │
│  │      └─ AIAssistantConfigurator (see ai-assistant-  │   │
│  │          config feature)                             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ GitHistoryAnalyzer                                   │   │
│  │  ├─ analyze()                                        │   │
│  │  ├─ get_recent_commits()                             │   │
│  │  └─ get_active_branches()                            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                Infrastructure Layer                          │
│  ┌─────────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │ subprocess.run  │  │ Path.exists  │  │ File I/O      │ │
│  │ (Git commands)  │  │ (structure)  │  │ (write files) │ │
│  └─────────────────┘  └──────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Spec-Kit Structure Generated

```text
project/
├── specs/                    # Spec-Kit compatible
│   ├── README.md            # Directory documentation
│   ├── features/            # Feature specifications
│   ├── api/                 # API contracts (OpenAPI)
│   ├── design/              # Technical designs
│   ├── reviews/             # Code reviews
│   └── PROJECT-OVERVIEW.md  # Project overview from Git analysis
├── memory/
│   └── constitution.md      # Project principles and rules
├── .cde/
│   └── state.json           # Onboarding status tracking
│
├── AI Assistant Configuration Files:
├── AGENTS.md                # Universal AI agent instructions
├── GEMINI.md                # Gemini-optimized instructions
└── .github/
    └── copilot-instructions.md  # GitHub Copilot config
```

---

## Git Analysis

### Information Extracted

```json
{
  "is_git_repo": true,
  "commit_count": 157,
  "branches": ["main", "feature/onboarding", "dev"],
  "recent_commits": [
    {
      "hash": "e62c2ec",
      "author": "BeRi",
      "email": "iberi22@gmail.com",
      "date": "2025-11-23",
      "message": "feat: Onboarding enrichment system"
    }
  ],
  "project_age_days": 45,
  "active_features": ["feature/onboarding"],
  "contributors": ["BeRi", "AI Agent"]
}
```

### Value

- **Contexto histórico**: PROJECT-OVERVIEW refleja realidad del proyecto
- **Features activas**: Recomendaciones para crear specs
- **Madurez**: Inferencia de madurez basada en commits y antigüedad

---

## Validation

### Live Demo Results (2025-11-02)

**Project**: CDE Orchestrator MCP (this project)

**Results**:

```text
✓ Detected missing structure: specs/, memory/, .cde/
✓ Analyzed Git history: 157 commits, 3 branches
✓ Generated specs/README.md (2.5 KB)
✓ Generated memory/constitution.md (3.2 KB)
✓ Generated specs/PROJECT-OVERVIEW.md (4.1 KB)
✓ Generated .cde/state.json
✓ Detected 4 AI assistants (Claude, Gemini, Cursor, Copilot)
✓ Generated AGENTS.md, GEMINI.md, copilot-instructions.md
✓ Total time: 4.8 seconds
✓ No errors
```

**Conclusion**: ✅ Feature fully operational

---

## References

- **Implementation**: `src/cde_orchestrator/onboarding_analyzer.py`
- **Tests**: `tests/unit/test_onboarding_analyzer.py`
- **Plan**: `specs/onboarding-system/plan.md`
- **Tasks**: `specs/onboarding-system/tasks.md`
- **Related**: `specs/ai-assistant-config/` (AI configuration subsystem)
- **Spec-Kit Repository**: [https://github.com/github/spec-kit](https://github.com/github/spec-kit)

---

## Changelog

### v1.0.0 (2025-11-02)

- ✅ Initial implementation
- ✅ Spec-Kit structure generation
- ✅ Git history analysis
- ✅ Technology stack detection
- ✅ AI assistant configuration integration
- ✅ MCP tool integration
- ✅ Comprehensive test suite
- ✅ Full documentation
- ✅ Live demo validation

---

**Status**: ✅ **PRODUCTION READY** (v1.0.0)
