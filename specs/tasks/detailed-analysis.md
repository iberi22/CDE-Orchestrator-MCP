---
title: 'TASK.md: CDE Orchestrator MCP Implementation'
description: '| ID | Task | Priority | Status | |---|---|---|---|'
type: guide
status: draft
created: '2025-11-02'
updated: '2025-11-02'
author: Auto-Generated
tags:
- analysis
- detailed
- documentation
- mcp
- python
- testing
llm_summary: "User guide for TASK.md: CDE Orchestrator MCP Implementation.\n  | ID\
  \ | Task | Priority | Status | |---|---|---|---| | SETUP-01 | Create the project\
  \ directory structure as defined in `README.md`. | HIGH | ✅ Complete | | SETUP-02\
  \ | Initialize a Python virtual environment and create `requirements.txt`. | HIGH\
  \ | ✅ Complete |\n  Reference when working with guide documentation."
---

# TASK.md: CDE Orchestrator MCP Implementation

## Phase 1: Project Setup & Core Models

| ID | Task | Priority | Status |
|---|---|---|---|
| SETUP-01 | Create the project directory structure as defined in `README.md`. | HIGH | ✅ Complete |
| SETUP-02 | Initialize a Python virtual environment and create `requirements.txt`. | HIGH | ✅ Complete |
| SETUP-03 | Add initial dependencies to `requirements.txt`: `fastmcp`, `pyyaml`, `pydantic`, `python-dotenv`. | HIGH | ✅ Complete |
| MODEL-01 | Create `src/cde_orchestrator/models.py`. | HIGH | ✅ Complete |
| MODEL-02 | In `models.py`, define Pydantic models for `Workflow`, `Phase`, `Input`, and `Output`. | HIGH | ✅ Complete |

## Phase 2: Core Logic Implementation

| ID | Task | Priority | Status |
|---|---|---|---|
| LOGIC-01 | Create `src/cde_orchestrator/workflow_manager.py`. | HIGH | ✅ Complete |
| LOGIC-02 | Implement a `WorkflowManager` class that can load and parse `.cde/workflow.yml` into the Pydantic models. | HIGH | ✅ Complete |
| LOGIC-03 | Create `src/cde_orchestrator/prompt_manager.py`. | HIGH | ✅ Complete |
| LOGIC-04 | Implement a `PromptManager` class with a method to read a `.poml` file and inject context variables (e.g., `{{USER_PROMPT}}`). | HIGH | ✅ Complete |
| LOGIC-05 | Create `src/cde_orchestrator/state_manager.py`. | HIGH | ✅ Complete |
| LOGIC-06 | Implement a `StateManager` class to read and write project state to a simple `.cde/state.json` file. | HIGH | ✅ Complete |

## Phase 3: FastMCP Server and Tool Implementation

| ID | Task | Priority | Status |
|---|---|---|---|
| MCP-01 | Create the main server file `src/server.py`. | HIGH | ✅ Complete |
| MCP-02 | In `server.py`, set up a basic FastMCP server instance. | HIGH | ✅ Complete |
| MCP-03 | Implement the `cde.startFeature(prompt: str)` tool. | HIGH | ✅ Complete |
| MCP-04 | The `startFeature` tool should: 1. Use `StateManager` to create a new feature entry. 2. Use `WorkflowManager` to get the first phase ('define'). 3. Use `PromptManager` to load the corresponding POML recipe and inject the user prompt. 4. Return the generated, contextualized prompt to the AI agent to execute. | HIGH | ✅ Complete |
| MCP-05 | Implement the `cde.submitWork(task_id: str, results: dict)` tool. This is more complex and will be tackled later. Start with a placeholder. | MEDIUM | ✅ Complete (Placeholder) |

## Phase 4: Testing and Documentation

| ID | Task | Priority | Status |
|---|---|---|---|
| TEST-01 | Create unit tests for the `WorkflowManager` to ensure it correctly parses the YAML file. | MEDIUM | ☐ Pending |
| TEST-02 | Create unit tests for the `PromptManager` to ensure it correctly replaces context variables. | MEDIUM | ☐ Pending |
| DOC-01 | Review and finalize all comments and docstrings in the code. | MEDIUM | ☐ Pending |
