---
author: Auto-Generated
created: '2025-11-02'
description: To create a robust, open-source MCP that serves as the reference implementation
  for the Context-Driven Engineering (CDE) methodology. This tool will e
llm_summary: "User guide for CDE Orchestrator MCP - Planning Document.\n  > **\U0001F4CB\
  \ Note:** This document contains the original project vision and architecture. For\
  \ current status and detailed improvement plans, see: > - [Executive Summary](EXECUTIVE_SUMMARY.md)\
  \ - Current status and roadmap\n  Reference when working with guide documentation."
status: draft
tags:
- api
- architecture
- mcp
- migration
- overview
- performance
title: CDE Orchestrator MCP - Planning Document
type: task
updated: '2025-11-02'
---

# CDE Orchestrator MCP - Planning Document

> **📋 Note:** This document contains the original project vision and architecture. For current status and detailed improvement plans, see:
> - [Executive Summary](EXECUTIVE_SUMMARY.md) - Current status and roadmap
> - [Improvement Roadmap](specs/tasks/improvement-roadmap.md) - Detailed task breakdown
> - [Technical Review](INFORME_REVISION_PROFESIONAL.md) - Comprehensive analysis

## 1. Project Vision

To create a robust, open-source MCP that serves as the reference implementation for the Context-Driven Engineering (CDE) methodology. This tool will empower AI agents to build complex software with high quality and consistency by managing the development workflow and context for them.

## 2. Core Principles

- **Agent-First Design:** All interfaces and workflows are designed for clarity and machine-readability.
- **Explicit over Implicit:** The state, context, and tasks are always explicitly defined in version-controlled files.
- **Abstraction:** Hide the complexity of underlying toolchains (Git, APIs) behind a simple, task-oriented interface.

## 3. Technology Stack

- **Language:** Python 3.11+
- **Framework:** FastMCP
- **Key Libraries:**
  - `PyYAML`: For parsing `.cde/workflow.yml`.
  - `lxml`: For parsing `.poml` files.
  - `pydantic`: For data modeling (Workflows, Phases, Tasks).
  - `python-dotenv`: For managing environment variables.
  - `PyGithub` (or similar): To interact with the GitHub API (as a wrapped tool).

## 4. Architecture

The Orchestrator MCP will be built using a modular, service-oriented architecture internally.

- **`WorkflowManager`:** Responsible for loading, parsing, and interpreting the `.cde/workflow.yml` file.
- **`StateManager`:** Responsible for tracking the current state of any given feature or task (e.g., using a `.cde/state.json` file for simplicity).
- **`PromptManager`:** Responsible for loading `.poml` files, injecting dynamic context, and generating the final prompt for the agent.
- **`ToolWrapper`:** An internal module that will wrap lower-level clients (like a GitHub client or filesystem tools) to be used by the main orchestrator tools.
- **`Server`:** The FastMCP server that exposes the high-level `cde.*` tools to the agent.

## 5. LLM-First I/O Contracts

- All MCP tools return JSON strings with a top-level `status` or `error` key.
- Common fields: `feature_id`, `phase`, `prompt`, `progress`.
- Error shape: `{ "error": <code>, "message?": <details>, ... }`.
- Contracts are documented in `CODEX.md` and `AGENTS.md`.

## 6. Roadmap (execution highlights)

> **🔄 Updated Roadmap:** See [Improvement Roadmap](specs/tasks/improvement-roadmap.md) for the current 8-week plan.

### Original Roadmap Status

1. ✅ Harden error handling/timeouts; centralized logging + tool decorator.
2. ✅ Repo ingestion respects `.gitignore`, skips binaries, caches digests.
3. ⏳ In progress: async/streaming ingestion + richer token-aware chunking (PERF-01, PERF-03).
4. ⏳ Deepen Spec-Kit integration: validation and templates (DOC-01).
5. ⏳ Extend prompts for specialized phases (QA, release).
6. ⏳ Improve Git/GitHub UX; add PR workflows (future - FEAT-02).

### Current Focus (2025)

**Phase 1 - Critical Fixes (Weeks 1-2):** 🔴
- State validation with Pydantic
- Error handling with retry logic
- Prompt sanitization

**Phase 2 - Testing (Weeks 3-4):** 🟠
- 80% test coverage
- CI/CD pipeline
- Integration tests

**Phase 3 - Performance (Week 5):** 🟡
- Async/await migration
- Intelligent caching
- Token estimation with tiktoken

See full details in [Improvement Roadmap](specs/tasks/improvement-roadmap.md).
