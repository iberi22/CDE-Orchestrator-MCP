# CDE Orchestrator MCP

## 1. Overview

The CDE Orchestrator is the reference implementation of the **Context-Driven Engineering (CDE)** methodology. It is a smart MCP (Model Context Protocol) server designed to guide AI coding assistants through a structured, phase-based software development lifecycle.

It acts as a high-level facade, abstracting away the complexity of underlying tools (like GitHub, file systems, etc.) and ensuring that the AI agent always has the precise context needed for its current task.

## 2. Core Concepts

- **Context-Driven Engineering (CDE):** A methodology where development is a series of state transitions, defined in a version-controlled `workflow.yml`. Each phase produces artifacts that serve as context for the next.
- **Workflow as Code:** The entire development process is defined in `.cde/workflow.yml`. This makes the process transparent, repeatable, and versionable.
- **POML-Powered Prompts:** Each phase in the workflow is powered by a **Prompt Object Markup Language (`.poml`)** file. This formalizes the instructions given to the AI, making them modular and reusable.
- **Orchestration, not just Execution:** This MCP doesn't just provide tools; it manages the project's state and guides the agent on what to do next.

## 3. Features (MCP Tools)

The orchestrator will expose the following high-level tools to the AI agent:

- `cde.startFeature(prompt: str)`: Initiates a new feature development workflow.
- `cde.getTask()`: Fetches the next available task based on the current workflow state.
- `cde.submitWork(task_id: str, results: dict)`: Submits the completed work for a given task. The orchestrator validates it and transitions to the next state.

## 4. Getting Started

1. **Clone the repository:**

    ```bash
    git clone [your-repo-url]
    cd cde-orchestrator-mcp
    ```

2. **Set up the environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
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

## 5. Project Structure

├── .cde/ # CDE Workflow definitions
│ ├── workflow.yml # The main workflow definition
│ └── prompts/ # POML prompt templates
├── src/ # Python source code for the MCP server
├── tests/ # Unit tests
├── .env # Environment variables
├── Dockerfile # Containerization
└── requirements.txt # Python dependencies
