# CDE Orchestrator MCP - Planning Document

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

1. ✅ Harden error handling/timeouts; centralized logging + tool decorator.
2. ✅ Repo ingestion respects `.gitignore`, skips binaries, caches digests.
3. In progress: async/streaming ingestion + richer token-aware chunking.
4. Deepen Spec-Kit integration: validation and templates.
5. Extend prompts for specialized phases (QA, release).
6. Improve Git/GitHub UX; add PR workflows (future).
