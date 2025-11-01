# src/cde_orchestrator/onboarding_analyzer.py
"""
Onboarding Analyzer - Detects project structure and analyzes Git history
for intelligent project onboarding aligned with Spec-Kit methodology.
"""
import logging
import subprocess
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ai_assistant_configurator import AIAssistantConfigurator

logger = logging.getLogger(__name__)


class OnboardingAnalyzer:
    """
    Analyzes project structure and Git history to determine if onboarding is needed
    and what documentation/structure should be created.
    Compatible with Spec-Kit methodology: https://github.com/github/spec-kit
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.specs_root = project_root / "specs"
        self.memory_root = project_root / "memory"
        self.tests_root = project_root / "tests"

    def needs_onboarding(self) -> Dict[str, Any]:
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

        # Analyze Git history
        git_info = self._analyze_git_history()
        analysis["project_info"]["git"] = git_info

        # Generate recommendations based on what's missing
        analysis["recommendations"] = self._generate_recommendations(analysis)

        return analysis

    def _analyze_git_history(self) -> Dict[str, Any]:
        """
        Analyze Git history to understand project evolution.

        Returns:
            Dict with Git analysis information
        """
        git_info = {
            "is_git_repo": self._is_git_repo(),
            "commit_count": 0,
            "branches": [],
            "recent_commits": [],
            "project_age_days": 0,
            "active_features": [],
        }

        if not git_info["is_git_repo"]:
            return git_info

        try:
            # Total commits
            result = self._run_git(["git", "rev-list", "--count", "HEAD"])
            if result and result.returncode == 0:
                git_info["commit_count"] = int(result.stdout.strip())

            # Branch discovery
            result = self._run_git(["git", "branch", "-a", "--format=%(refname:short)"])
            if result and result.returncode == 0:
                branches = [b.strip() for b in result.stdout.splitlines() if b.strip()]
                git_info["branches"] = branches
                feature_branches = [
                    b
                    for b in branches
                    if any(prefix in b for prefix in ("feature/", "feat/", "dev/"))
                ]
                git_info["active_features"] = feature_branches

            # Recent commits (limit 10)
            result = self._run_git(
                [
                    "git",
                    "log",
                    "--pretty=format:%H|%an|%ae|%ad|%s",
                    "--date=short",
                    "-n",
                    "20",
                ]
            )
            if result and result.returncode == 0:
                commits: List[Dict[str, Any]] = []
                for line in result.stdout.splitlines():
                    parts = line.split("|")
                    if len(parts) >= 5:
                        commits.append(
                            {
                                "hash": parts[0][:8],
                                "author": parts[1],
                                "email": parts[2],
                                "date": parts[3],
                                "message": parts[4],
                            }
                        )
                git_info["recent_commits"] = commits[:10]

            # Project age (days)
            result = self._run_git(
                ["git", "log", "--reverse", "--pretty=%ad", "--date=iso"]
            )
            if result and result.returncode == 0:
                lines = [line for line in result.stdout.splitlines() if line.strip()]
                if lines:
                    try:
                        first_commit = datetime.fromisoformat(lines[0])
                        if first_commit.tzinfo is None:
                            first_commit = first_commit.replace(tzinfo=timezone.utc)
                        git_info["project_age_days"] = (
                            datetime.now(timezone.utc)
                            - first_commit.astimezone(timezone.utc)
                        ).days
                    except ValueError:
                        logger.debug("Unable to parse first commit date: %s", lines[0])

        except Exception as exc:
            logger.warning("Error analyzing git history: %s", exc, exc_info=True)

        return git_info

    def _run_git(
        self, args: List[str], timeout: int = 10
    ) -> Optional[subprocess.CompletedProcess]:
        """Execute git command with timeout, returning result or None."""
        try:
            t0 = time.time()
            result = subprocess.run(
                args,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            elapsed = time.time() - t0
            logger.debug("git command succeeded in %.3fs: %s", elapsed, " ".join(args))
            return result
        except subprocess.TimeoutExpired:
            logger.warning(
                "git command timed out after %ss: %s", timeout, " ".join(args)
            )
            return None
        except Exception as exc:
            logger.warning("git command failed: %s (%s)", " ".join(args), exc)
            return None

    def _synthesize_repository(self) -> Dict[str, Any]:
        """Generate a high-level synthesis of the repository."""
        total_files = 0
        total_dirs = 0
        language_counter: Counter[str] = Counter()
        top_level_counter: Counter[str] = Counter()

        for path in self.project_root.rglob("*"):
            if path.is_dir():
                if path == self.project_root:
                    continue
                total_dirs += 1
                continue

            total_files += 1

            try:
                rel = path.relative_to(self.project_root)
            except ValueError:
                rel = path

            # top level directory stats
            parts = rel.parts
            if parts:
                top_level_counter[parts[0]] += 1
            else:
                top_level_counter["."] += 1

            suffix = path.suffix.lower().lstrip(".")
            if suffix:
                language_counter[suffix] += 1

        summary = {
            "total_files": total_files,
            "total_directories": total_dirs,
            "top_directories": top_level_counter.most_common(6),
            "top_extensions": language_counter.most_common(8),
        }
        return summary

    def _detect_structure_anomalies(self) -> Dict[str, Any]:
        """Detect misplaced tests, redundant files, and cleanup opportunities."""
        tests_to_move: List[Dict[str, str]] = []
        orphan_tests: List[str] = []
        for test_file in self.project_root.rglob("test_*.py"):
            if self.tests_root in test_file.parents:
                continue
            try:
                rel = test_file.relative_to(self.project_root)
            except ValueError:
                rel = test_file
            tests_to_move.append(
                {"path": str(rel), "suggested_destination": f"tests/{rel.name}"}
            )

        # Heuristic: tests referencing modules that do not exist anymore
        # For simplicity, mark tests under tests/ that import modules not present.
        if self.tests_root.exists():
            for py_test in self.tests_root.rglob("test_*.py"):
                try:
                    rel = py_test.relative_to(self.project_root)
                except ValueError:
                    rel = py_test
                try:
                    content = py_test.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("from ") or line.startswith("import "):
                        module = (
                            line.replace("from ", "").replace("import ", "").split()[0]
                        )
                        module_path = module.replace(".", "/")
                        candidate = self.project_root / f"{module_path}.py"
                        # Skip stdlib heuristically
                        if module.startswith(
                            ("os", "sys", "typing", "pytest", "unittest", "pathlib")
                        ):
                            continue
                        if not candidate.exists():
                            orphan_tests.append(str(rel))
                            break

        obsolete_files = []
        for candidate in ["TASK.md", "TODO.md", "CHANGELOG.txt"]:
            path = self.project_root / candidate
            if path.exists():
                obsolete_files.append(str(candidate))

        return {
            "tests_to_move": tests_to_move,
            "orphan_tests": orphan_tests[:20],
            "obsolete_files": obsolete_files,
        }

    def _identify_document_updates(self) -> List[Dict[str, str]]:
        """Identify documentation that may need regeneration or relocation."""
        updates: List[Dict[str, str]] = []
        specs_readme = self.specs_root / "README.md"
        if specs_readme.exists():
            updates.append(
                {
                    "path": "specs/README.md",
                    "action": "refresh",
                    "reason": "Ensure Spec-Kit README reflects current workflow and toolchain.",
                }
            )

        root_readme = self.project_root / "README.md"
        if root_readme.exists():
            updates.append(
                {
                    "path": "README.md",
                    "action": "align",
                    "reason": "Align overview with Integrated Management System principles.",
                }
            )

        return updates

    def _is_git_repo(self) -> bool:
        """Check if current directory is a Git repository."""
        git_dir = self.project_root / ".git"
        return git_dir.exists()

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

    def generate_onboarding_plan(self) -> Dict[str, Any]:
        """
        Generate a comprehensive onboarding plan based on analysis.

        Returns:
            Dict with onboarding plan including tasks and structure
        """
        analysis = self.needs_onboarding()

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
                "repository_synthesis": self._synthesize_repository(),
                "cleanup_plan": self._detect_structure_anomalies(),
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

        repo_synthesis = self._synthesize_repository()
        cleanup = self._detect_structure_anomalies()
        doc_updates = self._identify_document_updates()

        plan["cleanup_plan"] = {
            "tests_to_move": cleanup["tests_to_move"],
            "orphan_tests": cleanup["orphan_tests"],
            "obsolete_files": cleanup["obsolete_files"],
            "documentation_updates": doc_updates,
        }

        if cleanup["tests_to_move"]:
            plan["tasks"].append(
                {
                    "priority": "medium",
                    "action": "relocate_tests",
                    "description": "Align all automated tests under tests/ for consistent discovery.",
                    "affected_files": cleanup["tests_to_move"],
                }
            )

        if cleanup["obsolete_files"]:
            plan["tasks"].append(
                {
                    "priority": "medium",
                    "action": "archive_or_remove",
                    "description": "Archive or remove planning artifacts superseded by Spec-as-Code.",
                    "files": cleanup["obsolete_files"],
                }
            )

        if doc_updates:
            plan["tasks"].append(
                {
                    "priority": "medium",
                    "action": "refresh_documentation",
                    "description": "Refresh core documentation with the Integrated Management System framing.",
                    "targets": doc_updates,
                }
            )

        # Set context for generation
        plan["context"] = {
            "git": git_info,
            "missing_structure": analysis["missing_structure"],
            "existing_structure": analysis["existing_structure"],
            "tech_stack": self._detect_tech_stack(),
            "repository_synthesis": repo_synthesis,
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
