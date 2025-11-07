import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from cde_orchestrator.domain.ports import IGitAdapter


logger = logging.getLogger(__name__)


class OnboardingUseCase:
    """
    Analyzes project structure and Git history to determine if onboarding is needed
    and what documentation/structure should be created.
    Compatible with Spec-Kit methodology: https://github.com/github/spec-kit
    """

    def __init__(self, project_root: Path, git_adapter: IGitAdapter):
        self.project_root = project_root
        self.specs_root = project_root / "specs"
        self.memory_root = project_root / "memory"
        self.tests_root = project_root / "tests"
        self.git_adapter = git_adapter

    async def needs_onboarding(self) -> Dict[str, Any]:
        """
        Check if the project needs onboarding.

        Returns:
            Dict with analysis results including what's missing
        """
        analysis = {
            "needs_onboarding": False,
            "missing_structure": [],
            "existing_structure": [],
            "recommendations": [],
            "project_info": {},
        }

        # Check for Spec-Kit compatible structure
        required_specs_dirs = [
            "specs",
            "specs/features",
            "specs/api",
            "specs/design",
            "specs/reviews",
        ]

        required_docs = ["specs/README.md", "memory/constitution.md"]

        for dir_path in required_specs_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                analysis["existing_structure"].append(dir_path)
            else:
                analysis["missing_structure"].append(dir_path)
                analysis["needs_onboarding"] = True

        for doc_path in required_docs:
            full_path = self.project_root / doc_path
            if full_path.exists() and full_path.is_file():
                analysis["existing_structure"].append(doc_path)
            else:
                analysis["missing_structure"].append(doc_path)
                analysis["needs_onboarding"] = True

        # Analyze Git history using the adapter
        git_info = await self._analyze_git_history_with_adapter()
        analysis["project_info"]["git"] = git_info

        # Generate recommendations based on what's missing
        analysis["recommendations"] = self._generate_recommendations(analysis)

        return analysis

    async def _analyze_git_history_with_adapter(self) -> Dict[str, Any]:
        """
        Analyze Git history using the GitAdapter to understand project evolution.

        Returns:
            Dict with Git analysis information
        """
        git_info = {
            "is_git_repo": False,
            "commit_count": 0,
            "branches": [],
            "recent_commits": [],
            "project_age_days": 0,
            "active_features": [],
        }

        # Check if it's a Git repo
        if (self.project_root / ".git").exists():
            git_info["is_git_repo"] = True
        else:
            return git_info

        try:
            commits = []
            first_commit_date: Optional[datetime] = None
            async for commit in self.git_adapter.traverse_commits():
                commits.append(commit)
                if first_commit_date is None:
                    first_commit_date = commit.date

            git_info["commit_count"] = len(commits)
            git_info["recent_commits"] = [
                {
                    "hash": c.hash[:8],
                    "author": c.author,
                    "date": c.date.isoformat(),
                    "message": c.message,
                }
                for c in commits[:10]
            ]

            if first_commit_date:
                git_info["project_age_days"] = (
                    datetime.now(timezone.utc)
                    - first_commit_date.astimezone(timezone.utc)
                ).days

            # For branches, we might need a separate git command or a more sophisticated adapter method
            # For now, we'll leave it as an empty list or derive from commit messages if possible
            # This is a simplification for the initial refactoring
            git_info["branches"] = []  # Placeholder
            git_info["active_features"] = []  # Placeholder

        except Exception as exc:
            logger.warning(
                "Error analyzing git history with adapter: %s", exc, exc_info=True
            )

        return git_info

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on analysis.

        Args:
            analysis: Results from needs_onboarding check

        Returns:
            List of recommendation strings
        """
        recommendations = []

        missing = analysis["missing_structure"]
        git_info = analysis["project_info"]["git"]

        # Structure recommendations
        if any("specs" in item for item in missing):
            recommendations.append(
                "Create 'specs/' directory structure following Spec-Kit methodology"
            )

        if "memory/constitution.md" in missing:
            recommendations.append(
                "Create 'memory/constitution.md' to define project principles and rules"
            )

        # Git-based recommendations
        if git_info["commit_count"] > 10:
            if not any("README" in item for item in analysis["existing_structure"]):
                recommendations.append(
                    "Generate project documentation from existing Git history"
                )

            if git_info["active_features"]:
                recommendations.append(
                    f"Create feature specifications for {len(git_info['active_features'])} active feature branches"
                )

        # Technology stack recommendations
        if self.project_root.exists():
            detected_tech = self._detect_tech_stack()
            if detected_tech:
                recommendations.append(
                    f"Generate technical specifications for detected stack: {', '.join(detected_tech)}"
                )

        return recommendations

    def _detect_tech_stack(self) -> List[str]:
        """
        Detect technology stack from existing files.

        Returns:
            List of detected technologies
        """
        tech_stack = []

        # Check for common files
        checks = {
            "Python": ["requirements.txt", "pyproject.toml", "setup.py"],
            "Node.js": ["package.json"],
            ".NET": ["*.csproj", "*.sln"],
            "Java": ["pom.xml", "build.gradle"],
            "Docker": ["Dockerfile"],
            "TypeScript": ["tsconfig.json"],
            "React": ["package.json"],
        }

        for tech, files in checks.items():
            for pattern in files:
                matches = list(self.project_root.glob(pattern))
                if matches:
                    if tech not in tech_stack:
                        tech_stack.append(tech)
                    break

        # Detect from subdirectories
        dirs = [d.name for d in self.project_root.iterdir() if d.is_dir()]
        if any("src" in d.lower() for d in dirs):
            if "Python" not in tech_stack and "Node.js" not in tech_stack:
                pass  # Could be any language

        return tech_stack

    async def generate_onboarding_plan(self) -> Dict[str, Any]:
        """
        Generate a comprehensive onboarding plan based on analysis.

        Returns:
            Dict with onboarding plan including tasks and structure
        """
        analysis = await self.needs_onboarding()  # needs to be awaited now

        plan = {
            "project_root": str(self.project_root),
            "needs_onboarding": analysis["needs_onboarding"],
            "structure_to_create": [],
            "docs_to_generate": [],
            "tasks": [],
            "cleanup_plan": {},
            "context": {},
        }

        if not analysis["needs_onboarding"]:
            plan["tasks"].append(
                {
                    "priority": "low",
                    "action": "review",
                    "description": "Project already has Spec-Kit structure. Review existing docs.",
                }
            )
            plan["context"] = {
                "git": analysis["project_info"]["git"],
                "existing_structure": analysis["existing_structure"],
                # These will be derived from GitAdapter in future tasks
                "repository_synthesis": {},
                "cleanup_plan": {},
                "recommendations": self._generate_recommendations(analysis),
            }
            return plan

        git_info = analysis["project_info"]["git"]

        # Priority 1: Create directory structure
        for missing_dir in analysis["missing_structure"]:
            if missing_dir.endswith("/") or "/" in missing_dir:
                plan["structure_to_create"].append(
                    {
                        "type": "directory",
                        "path": missing_dir,
                        "description": f"Create {missing_dir} directory",
                    }
                )

        # Priority 2: Generate essential documentation
        plan["docs_to_generate"].append(
            {
                "file": "specs/README.md",
                "description": "Spec-Kit compatible specs directory README",
                "priority": "high",
            }
        )

        plan["docs_to_generate"].append(
            {
                "file": "memory/constitution.md",
                "description": "Project constitution defining principles and rules",
                "priority": "high",
            }
        )

        # Priority 3: Generate project documentation based on Git history
        if git_info["commit_count"] > 0:
            plan["docs_to_generate"].append(
                {
                    "file": "specs/PROJECT-OVERVIEW.md",
                    "description": "Project overview generated from Git history",
                    "priority": "medium",
                    "context": {
                        "commit_count": git_info["commit_count"],
                        "project_age": git_info["project_age_days"],
                        "branches": git_info["branches"],
                    },
                }
            )

        # Priority 4: Create specifications for active features
        if git_info["active_features"]:
            for feature_branch in git_info["active_features"][:5]:  # Limit to 5
                feature_name = feature_branch.replace("feature/", "").replace(
                    "feat/", ""
                )
                plan["tasks"].append(
                    {
                        "priority": "medium",
                        "action": "create_feature_spec",
                        "branch": feature_branch,
                        "spec_file": f"specs/features/{feature_name}.md",
                        "description": f"Create specification for {feature_branch}",
                    }
                )

        # Placeholder for future tasks that will use GitAdapter for cleanup and synthesis
        plan["cleanup_plan"] = {}
        plan["tasks"].append(
            {
                "priority": "medium",
                "action": "refactor_cleanup_and_synthesis",
                "description": "Refactor cleanup and repository synthesis to use GitAdapter.",
            }
        )

        # Set context for generation
        plan["context"] = {
            "git": git_info,
            "missing_structure": analysis["missing_structure"],
            "existing_structure": analysis["existing_structure"],
            "tech_stack": self._detect_tech_stack(),
            "repository_synthesis": {},  # Placeholder
            "cleanup_plan": plan["cleanup_plan"],
            "recommendations": self._generate_recommendations(analysis),
        }

        return plan


class SpecKitStructureGenerator:
    """
    Generates Spec-Kit compatible directory structure and initial files.
    Now includes AI assistant configuration following Spec-Kit best practices.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ai_configurator = AIAssistantConfigurator(project_root)

    def create_structure(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create the directory structure according to plan.
        Now includes AI assistant configuration files.

        Args:
            plan: Onboarding plan from analyzer

        Returns:
            Dict with creation results
        """
        results = {
            "created": [],
            "failed": [],
            "skipped": [],
            "ai_assistants": {"generated": [], "skipped": [], "errors": []},
        }

        # Create directory structure
        for structure_item in plan.get("structure_to_create", []):
            if structure_item["type"] == "directory":
                path = self.project_root / structure_item["path"]

                if path.exists():
                    results["skipped"].append(str(path))
                    continue

                try:
                    path.mkdir(parents=True, exist_ok=True)
                    results["created"].append(str(path))
                except Exception as e:
                    results["failed"].append({"path": str(path), "error": str(e)})

        # Configure AI assistants (auto-detect + defaults)
        try:
            logger.info("Configuring AI assistants...")
            ai_results = self.ai_configurator.generate_config_files(
                agents=None,  # Auto-detect + defaults
                force=False,  # Don't overwrite existing
            )
            results["ai_assistants"] = ai_results

            # Log summary
            if ai_results["generated"]:
                logger.info(
                    f"Generated {len(ai_results['generated'])} AI assistant configuration files"
                )
            if ai_results["skipped"]:
                logger.debug(f"Skipped {len(ai_results['skipped'])} existing files")
            if ai_results["errors"]:
                logger.warning(
                    f"Failed to generate {len(ai_results['errors'])} files: {ai_results['errors']}"
                )

        except Exception as e:
            logger.error(f"Failed to configure AI assistants: {e}")
            results["ai_assistants"]["errors"].append(f"Configuration failed: {str(e)}")

        return results

    def generate_readme_template(self) -> str:
        """Generate a Spec-Kit compatible specs README."""
        return """# Project Specifications

This directory contains all project specifications following the [Spec-Kit methodology](https://github.com/github/spec-kit).

## Directory Structure

```
specs/
├── README.md          # This file
├── features/          # Feature specifications
├── api/               # API specifications (OpenAPI)
├── design/            # Technical design documents
└── reviews/           # Code reviews and validations
```

## Workflow

1. **Define**: Create feature specifications in `features/`
2. **Plan**: Break down into tasks and create design docs
3. **Implement**: Build based on specifications
4. **Review**: Document reviews in `reviews/`

## How to Add a New Feature

1. Create a specification file in `features/`
2. Define user stories and acceptance criteria
3. Use the CDE Orchestrator to generate tasks
4. Track implementation progress

## Links

- [Spec-Kit Documentation](https://github.com/github/spec-kit)
- [CDE Orchestrator Workflows](.cde/workflow.yml)
- [Project Constitution](../memory/constitution.md)
"""

    def generate_constitution_template(self) -> str:
        """Generate a basic project constitution template."""
        return """# Project Constitution

This document defines the principles, rules, and standards that guide this project.

## Core Principles

### 1. Spec-Driven Development
All features must start with a specification in `specs/features/` before implementation.

### 2. Context-Driven Engineering
Follow the CDE workflow: Define → Decompose → Design → Implement → Test → Review

### 3. Quality First
- Write tests before implementation
- Review code before merging
- Document decisions and rationale

### 4. Continuous Improvement
- Learn from each iteration
- Update documentation regularly
- Refine processes based on experience

## Workflow Rules

### Feature Development
1. Create feature spec in `specs/features/`
2. Get approval/consensus
3. Create GitHub issues for tasks
4. Implement following spec
5. Test and review
6. Document in `specs/reviews/`

### Code Standards
- Follow language-specific style guides
- Write self-documenting code
- Add comments for complex logic
- Keep functions focused and small

### Git Workflow
- Use feature branches
- Write clear commit messages
- Create PRs for all changes
- Link PRs to issues

## Decision Making

When making technical decisions:
1. Consider the project constitution
2. Research alternatives
3. Document rationale
4. Update this document if principles change

## Resources

- [Specifications](../specs/)
- [Workflows](.cde/)
- [Project Overview](../README.md)
"""


class SpecKitStructureGenerator:
    """
    Generates Spec-Kit compatible directory structure and initial files.
    Now includes AI assistant configuration following Spec-Kit best practices.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ai_configurator = AIAssistantConfigurator(project_root)

    def create_structure(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create the directory structure according to plan.
        Now includes AI assistant configuration files.

        Args:
            plan: Onboarding plan from analyzer

        Returns:
            Dict with creation results
        """
        results = {
            "created": [],
            "failed": [],
            "skipped": [],
            "ai_assistants": {"generated": [], "skipped": [], "errors": []},
        }

        # Create directory structure
        for structure_item in plan.get("structure_to_create", []):
            if structure_item["type"] == "directory":
                path = self.project_root / structure_item["path"]

                if path.exists():
                    results["skipped"].append(str(path))
                    continue

                try:
                    path.mkdir(parents=True, exist_ok=True)
                    results["created"].append(str(path))
                except Exception as e:
                    results["failed"].append({"path": str(path), "error": str(e)})

        # Configure AI assistants (auto-detect + defaults)
        try:
            logger.info("Configuring AI assistants...")
            ai_results = self.ai_configurator.generate_config_files(
                agents=None,  # Auto-detect + defaults
                force=False,  # Don't overwrite existing
            )
            results["ai_assistants"] = ai_results

            # Log summary
            if ai_results["generated"]:
                logger.info(
                    f"Generated {len(ai_results['generated'])} AI assistant configuration files"
                )
            if ai_results["skipped"]:
                logger.debug(f"Skipped {len(ai_results['skipped'])} existing files")
            if ai_results["errors"]:
                logger.warning(
                    f"Failed to generate {len(ai_results['errors'])} files: {ai_results['errors']}"
                )

        except Exception as e:
            logger.error(f"Failed to configure AI assistants: {e}")
            results["ai_assistants"]["errors"].append(f"Configuration failed: {str(e)}")

        return results

    def generate_readme_template(self) -> str:
        """Generate a Spec-Kit compatible specs README."""
        return """# Project Specifications

This directory contains all project specifications following the [Spec-Kit methodology](https://github.com/github/spec-kit).

## Directory Structure

```
specs/
├── README.md          # This file
├── features/          # Feature specifications
├── api/               # API specifications (OpenAPI)
├── design/            # Technical design documents
└── reviews/           # Code reviews and validations
```

## Workflow

1. **Define**: Create feature specifications in `features/`
2. **Plan**: Break down into tasks and create design docs
3. **Implement**: Build based on specifications
4. **Review**: Document reviews in `reviews/`

## How to Add a New Feature

1. Create a specification file in `features/`
2. Define user stories and acceptance criteria
3. Use the CDE Orchestrator to generate tasks
4. Track implementation progress

## Links

- [Spec-Kit Documentation](https://github.com/github/spec-kit)
- [CDE Orchestrator Workflows](.cde/workflow.yml)
- [Project Constitution](../memory/constitution.md)
"""

    def generate_constitution_template(self) -> str:
        """Generate a basic project constitution template."""
        return """# Project Constitution

This document defines the principles, rules, and standards that guide this project.

## Core Principles

### 1. Spec-Driven Development
All features must start with a specification in `specs/features/` before implementation.

### 2. Context-Driven Engineering
Follow the CDE workflow: Define → Decompose → Design → Implement → Test → Review

### 3. Quality First
- Write tests before implementation
- Review code before merging
- Document decisions and rationale

### 4. Continuous Improvement
- Learn from each iteration
- Update documentation regularly
- Refine processes based on experience

## Workflow Rules

### Feature Development
1. Create feature spec in `specs/features/`
2. Get approval/consensus
3. Create GitHub issues for tasks
4. Implement following spec
5. Test and review
6. Document in `specs/reviews/`

### Code Standards
- Follow language-specific style guides
- Write self-documenting code
- Add comments for complex logic
- Keep functions focused and small

### Git Workflow
- Use feature branches
- Write clear commit messages
- Create PRs for all changes
- Link PRs to issues

## Decision Making

When making technical decisions:
1. Consider the project constitution
2. Research alternatives
3. Document rationale
4. Update this document if principles change

## Resources

- [Specifications](../specs/)
- [Workflows](.cde/)
- [Project Overview](../README.md)
"""
