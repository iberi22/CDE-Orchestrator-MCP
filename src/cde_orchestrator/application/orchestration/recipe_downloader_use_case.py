"""
Recipe Downloader Use Case.

Downloads workflow recipes (POML files, prompts, and workflow.yml)
from the agents-flows-recipes GitHub repository.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from cde_orchestrator.domain.ports import IRecipeDownloader


class RecipeDownloaderUseCase:
    """
    Downloads recipes from external repositories (GitHub).

    This use case:
    1. Checks if .cde/ directory exists
    2. If not, downloads from agents-flows-recipes repo
    3. Creates local .cde/ structure with:
       - workflow.yml (workflow definition)
       - prompts/ (POML prompt templates)
       - recipes/ (specialized agent recipes)
    """

    def __init__(self, downloader: IRecipeDownloader):
        """
        Initialize use case with downloader adapter.

        Args:
            downloader: Adapter that handles HTTP/GitHub downloads
        """
        self.downloader = downloader

    async def execute(
        self,
        project_path: str = ".",
        repo_url: str = "https://github.com/iberi22/agents-flows-recipes",
        branch: str = "main",
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Download recipes to project .cde/ directory.

        Args:
            project_path: Path to project root (where .cde/ will be created)
            repo_url: GitHub repository URL
            branch: Branch to download from
            force: If True, overwrite existing .cde/ directory

        Returns:
            {
                "status": "success" | "skipped" | "error",
                "message": str,
                "files_downloaded": List[str],
                "destination": str (path to .cde/)
            }
        """
        project_root = Path(project_path).resolve()
        cde_dir = project_root / ".cde"

        # Check if .cde/ already exists
        if cde_dir.exists() and not force:
            return {
                "status": "skipped",
                "message": f".cde/ directory already exists at {cde_dir}. Use force=True to overwrite.",
                "files_downloaded": [],
                "destination": str(cde_dir)
            }

        # Create .cde/ structure if needed
        if not cde_dir.exists():
            cde_dir.mkdir(parents=True, exist_ok=True)

        # Define what to download from the repo
        files_to_download = self._get_recipe_file_list()

        downloaded_files: List[str] = []
        errors: List[str] = []

        for file_info in files_to_download:
            try:
                # Download file from GitHub
                content = await self.downloader.download_file(
                    repo_url=repo_url,
                    branch=branch,
                    file_path=file_info["source"]
                )

                # Save to local .cde/ directory
                local_path = cde_dir / file_info["destination"]
                local_path.parent.mkdir(parents=True, exist_ok=True)

                # Write content
                if isinstance(content, bytes):
                    local_path.write_bytes(content)
                else:
                    local_path.write_text(content, encoding="utf-8")

                downloaded_files.append(str(local_path.relative_to(project_root)))

            except Exception as e:
                errors.append(f"Failed to download {file_info['source']}: {str(e)}")

        if errors:
            return {
                "status": "partial",
                "message": f"Downloaded {len(downloaded_files)} files with {len(errors)} errors",
                "files_downloaded": downloaded_files,
                "destination": str(cde_dir),
                "errors": errors
            }

        return {
            "status": "success",
            "message": f"Successfully downloaded {len(downloaded_files)} recipe files",
            "files_downloaded": downloaded_files,
            "destination": str(cde_dir)
        }

    def _get_recipe_file_list(self) -> List[Dict[str, str]]:
        """
        Define which files to download from the recipes repo.

        Returns:
            List of dicts with 'source' (path in repo) and 'destination' (path in .cde/)
        """
        return [
            # Workflow definition (if exists in repo)
            # NOTE: Your repo uses POML recipes, so we'll create a minimal workflow.yml

            # Download key POML recipes from poml/engineering/
            {
                "source": "poml/engineering/ai-engineer.poml",
                "destination": "recipes/engineering/ai-engineer.poml"
            },
            {
                "source": "poml/engineering/backend-architect.poml",
                "destination": "recipes/engineering/backend-architect.poml"
            },
            {
                "source": "poml/engineering/test-writer-fixer.poml",
                "destination": "recipes/engineering/test-writer-fixer.poml"
            },

            # Documentation writers
            {
                "source": "poml/design/brand-guardian.poml",
                "destination": "recipes/design/brand-guardian.poml"
            },

            # Product management
            {
                "source": "poml/product/sprint-prioritizer.poml",
                "destination": "recipes/product/sprint-prioritizer.poml"
            },

            # Testing
            {
                "source": "poml/testing/workflow-optimizer.poml",
                "destination": "recipes/testing/workflow-optimizer.poml"
            },

            # Bonus agents
            {
                "source": "poml/bonus/studio-coach.poml",
                "destination": "recipes/bonus/studio-coach.poml"
            },

            # Documentation helpers
            {
                "source": "docs/qwen-rules.md",
                "destination": "docs/qwen-rules.md"
            },
            {
                "source": "docs/advanced-techniques.md",
                "destination": "docs/advanced-techniques.md"
            },
        ]

    def check_cde_exists(self, project_path: str = ".") -> bool:
        """
        Check if .cde/ directory exists in project.

        Args:
            project_path: Path to project root

        Returns:
            True if .cde/ exists, False otherwise
        """
        cde_dir = Path(project_path).resolve() / ".cde"
        return cde_dir.exists()

    def ensure_workflow_yml(self, project_path: str = ".") -> Dict[str, Any]:
        """
        Create a minimal workflow.yml if it doesn't exist.

        Since your repo doesn't have workflow.yml, we create one based on
        CDE's 6-phase workflow (define → decompose → design → implement → test → review).

        Args:
            project_path: Path to project root

        Returns:
            Status of operation
        """
        cde_dir = Path(project_path).resolve() / ".cde"
        workflow_file = cde_dir / "workflow.yml"

        if workflow_file.exists():
            return {
                "status": "exists",
                "message": "workflow.yml already exists",
                "path": str(workflow_file)
            }

        # Create minimal workflow.yml
        workflow_content = """# CDE Workflow Definition
name: standard_workflow
version: "1.0"
description: Context-Driven Engineering 6-phase workflow

phases:
  - id: define
    name: Define
    description: Write feature specification
    prompt_template: prompts/01_define.poml
    inputs:
      - user_prompt
      - project_context
    outputs:
      - specification
      - acceptance_criteria

  - id: decompose
    name: Decompose
    description: Break feature into tasks
    prompt_template: prompts/02_decompose.poml
    inputs:
      - specification
      - project_context
    outputs:
      - tasks
      - dependencies

  - id: design
    name: Design
    description: Create technical design
    prompt_template: prompts/03_design.poml
    inputs:
      - specification
      - tasks
      - architecture
    outputs:
      - technical_design
      - file_changes

  - id: implement
    name: Implement
    description: Write code
    prompt_template: prompts/04_implement.poml
    inputs:
      - technical_design
      - tasks
    outputs:
      - code_changes
      - files_modified

  - id: test
    name: Test
    description: Create and run tests
    prompt_template: prompts/05_test.poml
    inputs:
      - code_changes
      - specification
    outputs:
      - test_files
      - test_results

  - id: review
    name: Review
    description: Code review and QA
    prompt_template: prompts/06_review.poml
    inputs:
      - code_changes
      - test_results
      - specification
    outputs:
      - review_notes
      - approval_status

# Workflow types (can skip phases)
workflow_types:
  standard:
    phases: [define, decompose, design, implement, test, review]

  quick-fix:
    phases: [implement, test]
    skip: [define, decompose, design, review]

  research:
    phases: [define, decompose, design]
    skip: [implement, test, review]

  documentation:
    phases: [define, design]
    skip: [decompose, implement, test, review]

  hotfix:
    phases: [implement]
    skip: [define, decompose, design, test, review]
"""

        cde_dir.mkdir(parents=True, exist_ok=True)
        workflow_file.write_text(workflow_content, encoding="utf-8")

        return {
            "status": "created",
            "message": "Created minimal workflow.yml",
            "path": str(workflow_file)
        }
