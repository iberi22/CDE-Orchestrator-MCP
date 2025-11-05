---
title: "New Agent Integration Architecture"
description: "Architecture and design for integrating DeepAgents, Codex, and Rovo Dev CLI agents."
type: "design"
status: "draft"
created: "2025-11-04"
updated: "2025-11-04"
author: "Jules"
---

# New Agent Integration Architecture

## 1. Overview

This document outlines the architecture for integrating three new command-line interface (CLI) agents into the CDE Orchestrator MCP:

- **DeepAgents CLI**: For in-depth research, prototyping, and refactoring.
- **Codex CLI**: for code analysis and task review.
- **Rovo Dev CLI**: For end-to-end task completion and Jira integration.

The integration follows the existing hexagonal architecture pattern, utilizing the Ports & Adapters model to ensure a clean separation of concerns.

## 2. Design Principles

- **Adherence to Hexagonal Architecture**: All new components are implemented within the existing `application` and `adapters` layers.
- **Extensibility**: The design allows for the easy addition of future agents with minimal changes to the core logic.
- **Configuration over Code**: Agent capabilities and selection logic are defined in a central policy (`AgentSelectionPolicy`) for easy tuning.

## 3. Implementation Details

### 3.1. Agent Adapters

New adapters have been created in `src/cde_orchestrator/adapters/agents/` for each agent:

- `deep_agents_adapter.py`: Implements the `ICodeExecutor` interface for the DeepAgents CLI.
- `codex_adapter.py`: Implements the `ICodeExecutor` interface for the Codex CLI.
- `rovo_dev_adapter.py`: Implements the `ICodeExecutor` interface for the Rovo Dev CLI.

Each adapter is responsible for:
- Translating the generic `execute_prompt` call into the specific command-line arguments for its agent.
- Handling the execution of the CLI tool in a subprocess.
- Capturing and parsing the output (stdout, stderr) and returning it in a standardized JSON format.

### 3.2. Agent Selection Policy

The `AgentSelectionPolicy` (`src/cde_orchestrator/adapters/agents/agent_selection_policy.py`) has been updated to include the new agents:

- **`AgentType` Enum**: Extended to include `DEEPAGENTS`, `CODEX`, and `ROVODEV`.
- **`CAPABILITIES` Matrix**: Updated with the capabilities of the new agents, including their strengths, context size limits, and authentication requirements.
- **`FALLBACK_CHAIN`**: The fallback chain has been updated to reflect the new priority of agents.

### 3.3. MCP Tool Integration

The `src/mcp_tools/agents.py` module has been updated to integrate the new agents into the MCP tools:

- **`cde_listAvailableAgents`**: Now checks for the presence of `deepagents`, `codex`, and `rovo` in the system's PATH.
- **`cde_selectAgent`**: Incorporates the new agents into its selection logic.
- **`cde_executeWithBestAgent`**: Registers the new agent adapters with the `MultiAgentOrchestrator`.

## 4. Usage

The new agents are now available through the `cde_executeWithBestAgent` tool. The orchestrator will automatically select the best agent for the job based on the task description.

**Example:**

```python
# The orchestrator will select DeepAgents for a research task
cde_executeWithBestAgent(task_description="Research best practices for asynchronous programming in Python")

# The orchestrator will select Codex for a code review task
cde_executeWithBestAgent(task_description="Review the following code for potential bugs...")

# The orchestrator will select Rovo Dev for a task that involves Jira
cde_executeWithBestAgent(task_description="Implement the feature described in JIRA-123")
```
