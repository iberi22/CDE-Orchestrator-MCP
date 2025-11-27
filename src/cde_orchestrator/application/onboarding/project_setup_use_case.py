# src/cde_orchestrator/application/onboarding/project_setup_use_case.py
from pathlib import Path
from typing import Any, Dict

from .project_analysis_use_case import ProjectAnalysisUseCase
from .publishing_use_case import PublishingUseCase


class ProjectSetupUseCase:
    """
    Orchestrates the setup of a project by analyzing it and generating
    essential configuration files for AI agent collaboration.
    """

    def __init__(
        self,
        analysis_use_case: ProjectAnalysisUseCase,
        publishing_use_case: PublishingUseCase,
    ):
        self._analysis_use_case = analysis_use_case
        self._publishing_use_case = publishing_use_case

    async def execute(self, project_path: str, force: bool = False) -> Dict[str, Any]:
        """
        Executes the project setup process.

        Args:
            project_path: The path to the project.
            force: Whether to overwrite existing configuration files.

        Returns:
            A dictionary summarizing the actions taken.
        """
        # Step 1: Analyze the project (async)
        analysis_result = await self._analysis_use_case.execute(project_path)

        # Step 2: Generate content for config files
        documents_to_publish = {}

        # .gitignore
        gitignore_content = self._generate_gitignore(analysis_result)
        documents_to_publish[".gitignore"] = gitignore_content

        # AGENTS.md
        agents_md_content = self._generate_agents_md(analysis_result)
        documents_to_publish["AGENTS.md"] = agents_md_content

        # (Future: GEMINI.md, etc.)

        # Step 3: Publish the files
        # Note: PublishingUseCase needs to be adapted to handle the 'force' flag,
        # or we handle the logic here. We'll handle it here for simplicity.

        final_documents = {}
        project = Path(project_path)

        for path, content in documents_to_publish.items():
            if not (project / path).exists() or force:
                final_documents[path] = content

        publish_result = self._publishing_use_case.execute(
            project_path, final_documents
        )

        # Step 4: Generate report
        report = {
            "status": "success",
            "analysis_summary": analysis_result.get("summary"),
            "actions": [
                f"Generated content for {len(documents_to_publish)} config files."
            ],
            "files_written": publish_result.get("files_written", []),
            "files_skipped": [
                p for p in documents_to_publish if p not in final_documents
            ],
        }

        return report

    def _generate_gitignore(self, analysis: Dict[str, Any]) -> str:
        """Generates a .gitignore file based on project analysis."""
        content = "# Generic ignores\n.env\n.venv/\nvenv/\n__pycache__/\n*.pyc\n.cde/\n\n"

        if ".py" in analysis.get("language_stats", {}):
            content += "# Python specific\n.pytest_cache/\n"

        if "package.json" in analysis.get("dependency_files", []):
            content += "# Node.js specific\nnode_modules/\n"

        return content

    def _generate_agents_md(self, analysis: Dict[str, Any]) -> str:
        """Generates an AGENTS.md file with guidelines."""
        content = """# AI Agent Instructions - CDE Orchestrator MCP

> **Quick Reference for AI Coding Agents**
> **Enforced by Validation Scripts**

---

## 🚨 Critical Rules (STRICTLY ENFORCED)

1.  **NO .md files in root** except: `README.md`, `AGENTS.md`, `CHANGELOG.md`, `CONTRIBUTING.md`.
    *   All other documentation must go to `specs/` or `agent-docs/`.
    *   VIOLATION: Placing files like `todo.md` or `report.md` in the root.

2.  **Spec-Kit Structure**: All features must follow the strict directory structure:
    ```
    specs/[feature-name]/
    ├── spec.md   (Requirements & User Stories)
    ├── plan.md   (Technical Architecture)
    └── tasks.md  (Implementation Checklist)
    ```
    *   **Action**: Use `cde_startFeature` to generate this automatically. Do NOT create manually if possible.

3.  **MCP-First Workflow**:
    *   Use `cde_selectWorkflow` to start tasks.
    *   Use `cde_startFeature` to create feature contexts.
    *   Use `cde_submitWork` to track progress.

---

## 🏗️ Architecture

**Pattern**: Hexagonal (Ports & Adapters)

```
Domain (entities) → Application (use_cases) → Adapters (infrastructure)
```

*   **Domain**: Pure business logic. No external imports.
*   **Application**: Use cases orchestration.
*   **Adapters**: Implementation details (Git, FileSystem, OpenAI).

---

## 📂 Directory Structure

```
specs/
├── [feature-name]/        # Feature-specific documentation
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
├── templates/            # Golden master templates
└── legacy-migration/     # Archived root files

agent-docs/
├── execution/            # General execution logs & session notes
└── ...
```

---

## 🔧 Development Guidelines

1.  **Always Verify**: After creating a file, read it back to confirm.
2.  **Run Tests**: When available. Note that `mcp-status-bar` has no tests.
3.  **Clean Up**: Do not leave temporary scripts in the root. Move them to `scripts/scratch/` or `tests/`.

---

**Remember**: This file is the LAW. Deviations will be rejected by pre-commit hooks.
"""
        return content
