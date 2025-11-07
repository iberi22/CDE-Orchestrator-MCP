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

    def execute(self, project_path: str, force: bool = False) -> Dict[str, Any]:
        """
        Executes the project setup process.

        Args:
            project_path: The path to the project.
            force: Whether to overwrite existing configuration files.

        Returns:
            A dictionary summarizing the actions taken.
        """
        # Step 1: Analyze the project
        analysis_result = self._analysis_use_case.execute(project_path)

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
        content = "# Generic ignores\n.env\n.venv/\nvenv/\n__pycache__/\n*.pyc\n\n"

        if ".py" in analysis.get("language_stats", {}):
            content += "# Python specific\n.pytest_cache/\n"

        if "package.json" in analysis.get("dependency_files", []):
            content += "# Node.js specific\nnode_modules/\n"

        return content

    def _generate_agents_md(self, analysis: Dict[str, Any]) -> str:
        """Generates an AGENTS.md file with guidelines."""
        content = """# AI Agent Guidelines (AGENTS.md)

This document provides instructions for AI agents working on this repository.

## Project Structure
- The main source code is located in the `src/` directory.
- Tests are located in the `tests/` directory.
- This project uses a Hexagonal Architecture. Keep domain, application, and infrastructure layers separate.

## Coding Conventions
- Follow PEP 8 for Python code.
- Use the pre-commit hooks configured in `.pre-commit-config.yaml`.

## Your Role
- **Analyze Before You Act:** Use tools like `cde_scanDocumentation` to understand the project state.
- **Follow the Workflow:** Do not commit directly to `main`. Follow the feature workflow.
- **Communicate Clearly:** Provide clear commit messages and pull request descriptions.
"""
        return content
