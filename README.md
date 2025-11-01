# CDE Orchestrator MCP

[![CI](https://github.com/iberi22/CDE-Orchestrator-MCP/actions/workflows/ci.yml/badge.svg)](https://github.com/iberi22/CDE-Orchestrator-MCP/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/iberi22/CDE-Orchestrator-MCP/branch/main/graph/badge.svg)](https://codecov.io/gh/iberi22/CDE-Orchestrator-MCP)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

The CDE Orchestrator is the reference implementation of the **Context-Driven Engineering (CDE)** methodology. It is a smart MCP (Model Context Protocol) server designed to guide AI coding assistants through a structured, phase-based software development lifecycle.

## Core Concepts

### Context-Driven Engineering (CDE)
A methodology where development is a series of state transitions, defined in a version-controlled `workflow.yml`. Each phase produces artifacts that serve as context for the next.

### Workflow as Code
The entire development process is defined in `.cde/workflow.yml`. This makes the process transparent, repeatable, and versionable.

### POML-Powered Prompts
Each phase in the workflow is powered by a **Prompt Object Markup Language (`.poml`)** file. This formalizes the instructions given to the AI, making them modular and reusable.

### Orchestration, not just Execution
This MCP doesn't just provide tools; it manages the project's state and guides the agent on what to do next.

## Features (MCP Tools)

### Core Workflow Tools
- `cde_onboardingProject()`: Synthesizes the repository, proposes cleanup/relocation actions, and performs Spec-Kit onboarding with automation-ready artifacts.
- `cde_startFeature(prompt: str)`: Initiates a new feature development workflow.
- `cde_submitWork(feature_id: str, phase_id: str, results: dict)`: Submits completed work and transitions to the next phase.
- `cde_getFeatureStatus(feature_id: str)`: Gets the current status of a feature.
- `cde_listFeatures()`: Lists all features and their status.

### Recipe Management Tools
- `cde_listRecipes()`: Lists all available POML recipes.
- `cde_useRecipe(recipe_id: str, user_prompt: str, context: dict)`: Uses a specific recipe to generate a prompt.
- `cde_suggestRecipe(user_prompt: str, phase_id: str)`: Suggests the best recipe for a task.
- `cde_startFeatureWithRecipe(user_prompt: str, recipe_id: str)`: Starts a feature using a specific recipe.

### Git & GitHub Integration Tools
- `cde_createGitBranch(feature_id: str, branch_name: str, base_branch: str)`: Creates a Git branch for a feature.
- `cde_createGitHubIssue(feature_id: str, title: str, description: str, labels: list)`: Creates GitHub issues (uses external MCP if configured).
- `cde_commitWork(feature_id: str, message: str, files: list)`: Commits work to Git.
- `cde_getServiceStatus()`: Gets status of configured integrations.

> **Note:** Git/GitHub tools automatically detect and use external MCP servers when configured. See [INTEGRATION.md](INTEGRATION.md) for details.

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/iberi22/CDE-Orchestrator-MCP.git
   cd CDE-Orchestrator-MCP
   ```

2. **Set up the environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .[dev]
   ```

3. **Configure Environment Variables:**
   Create a `.env` file with the necessary credentials:
   ```
   GITHUB_TOKEN=your_github_pat
   ```

4. **Run the server:**
   ```bash
   python src/server.py
   ```

## VS Code Integration

To connect to the CDE Orchestrator MCP from VS Code, configure your MCP settings:

```json
{
  "mcpServers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": ["src/server.py"],
      "env": {
        "PYTHONPATH": "src"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Reload VS Code and verify the connection in your AI assistant extension.

## Project Structure

```
├── .cde/                 # CDE Workflow definitions
│   ├── workflow.yml      # The main workflow definition
│   └── prompts/          # POML prompt templates
├── specs/                # Specification documents
│   ├── features/         # Feature specifications
│   ├── api/              # API specifications
│   ├── design/           # Technical design documents
│   └── reviews/          # Code reviews and validations
├── src/                  # Python source code for the MCP server
├── tests/                # Unit tests
├── memory/               # Project constitution and context
├── .env                  # Environment variables
├── Dockerfile            # Containerization
└── pyproject.toml        # Python project configuration
```

## The CDE Workflow

The core of the CDE Orchestrator is the `workflow.yml` file. A typical workflow includes:

1. **`define`**: Clearly define the feature or bug to be worked on
2. **`decompose`**: Break down the work into smaller, manageable tasks
3. **`design`**: Create technical design documents
4. **`implement`**: Write the code for each task
5. **`test`**: Create and run tests to ensure the code works
6. **`review`**: Review the code for quality, correctness, and standards
7. **`integrate`**: Merge the code into the main branch

## Repository Onboarding & Cleanup

The CDE Orchestrator provides intelligent repository analysis and onboarding:

- **Repository synthesis:** Summarizes directories, file types, and tech stack
- **Automated cleanup:** Recommends test relocations and obsolete file removal
- **Spec-Kit compliance:** Ensures alignment with specification-as-code principles
- **Stateful tracking:** Maintains audit trail of all changes and recommendations

## External Service Integration

The CDE Orchestrator supports seamless integration with external MCP servers:

### Automatic MCP Detection
- **GitHub MCP**: Automatically detected from your MCP configuration
- **Git Operations**: Always available for local repositories
- **Fallback Mechanisms**: Graceful degradation when services are unavailable

### Quick Setup
```bash
export GITHUB_TOKEN=your-token-here
```

For detailed integration documentation, see [INTEGRATION.md](INTEGRATION.md). For Codex CLI usage, see [CODEX.md](CODEX.md).
