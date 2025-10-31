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

The orchestrator exposes the following high-level tools to the AI agent:

### Core Workflow Tools
- `cde_onboardingProject()`: Analyzes project structure and performs onboarding setup with Spec-Kit compatibility.
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

## 6. Consuming the MCP from VS Code

To connect to the CDE Orchestrator MCP from VS Code, you need to configure the Gemini extension to use the `STDIO` transport.

1. **Open the VS Code settings:**
    Press `Ctrl + ,` to open the settings.

2. **Open the `settings.json` file:**
    Click the "Open Settings (JSON)" icon in the top right corner.

3. **Add the following configuration to your `settings.json` or .vscode/mcp.json file:**

    ```json

   {
      "mcpServers": {
        "CDE_Orchestrator": {
            "command": "python",
            "args": [
                "src/server.py"
            ],
            "env": {
                "PYTHONPATH": "src"
            },
            "disabled": false,
            "autoApprove": []
            }
        }
   }

    ```

4.  **Reload VS Code:**
    Reload the VS Code window to apply the changes.

5. **Verify the connection:**
    Open the Gemini extension and you should see the `CDE_Orchestrator` tools available.

## 7. Professional Project Management with the CDE Orchestrator

The CDE Orchestrator is not just a tool, but a methodology for professional project management. By enforcing a structured workflow, it ensures that every phase of development is deliberate, documented, and aligned with the project's goals.

### The CDE Workflow

The core of the CDE Orchestrator is the `workflow.yml` file. This file defines the phases of your development process. A typical workflow might include:

1.  **`define`**: Clearly define the feature or bug to be worked on. This phase ensures that there is a clear understanding of the requirements before any code is written.
2.  **`decompose`**: Break down the work into smaller, manageable tasks. This is crucial for tracking progress and for parallelizing work when possible.
3.  **`implement`**: Write the code for each task.
4.  **`test`**: Create and run tests to ensure the code is working as expected.
5.  **`review`**: Review the code for quality, correctness, and adherence to coding standards.
6.  **`integrate`**: Merge the code into the main branch.

### Using the CDE Orchestrator in your Project

To use the CDE Orchestrator, you start by defining your workflow in `.cde/workflow.yml`. Then, you use the provided MCP tools to move through the phases of the workflow.

-   `cde.startFeature(prompt: str)`: This command initiates a new feature. The orchestrator will create a new branch and set up the initial state for the workflow.
-   `cde.getTask()`: This command retrieves the next task from the current phase. The orchestrator uses the `workflow.yml` and the project's state to determine the next task.
-   `cde.submitWork(task_id: str, results: dict)`: Once you have completed a task, you use this command to submit your work. The orchestrator will validate the work and, if it's complete, move the project to the next phase in the workflow.

By using the CDE Orchestrator, you can ensure that your project is always in a well-defined state, that all work is tracked, and that your development process is consistent and repeatable.

## 8. External Service Integration

The CDE Orchestrator supports seamless integration with external MCP servers for enhanced functionality:

### Automatic MCP Detection

The orchestrator automatically detects and uses external MCP servers when configured:
- **GitHub MCP**: Automatically detected from your MCP configuration
- **Git Operations**: Always available for local repositories
- **Fallback Mechanisms**: Graceful degradation when services are unavailable

### Quick Setup

1. **Configure GitHub MCP** (optional):
   ```json
   {
     "mcpServers": {
       "github": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-github"],
         "env": {
           "GITHUB_TOKEN": "your-token-here"
         }
       }
     }
   }
   ```

2. **Or use GitHub API** (alternative):
   ```bash
   export GITHUB_TOKEN=your-token-here
   ```

3. **Check service status**:
   ```
   cde_getServiceStatus()
   ```

For detailed integration documentation, see [INTEGRATION.md](INTEGRATION.md). For Codex CLI usage, see [CODEX.md](CODEX.md).
