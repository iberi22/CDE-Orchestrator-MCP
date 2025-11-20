# src/cde_orchestrator/application/onboarding/project_analysis_use_case.py
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Dict, List

import pathspec


class ProjectAnalysisUseCase:
    """
    Analyzes a software project to understand its structure, languages, and dependencies.
    """

    # Directories to always exclude from analysis (even if not in .gitignore)
    EXCLUDED_DIRS = {
        "node_modules",
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "env",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "dist",
        "build",
        "out",
        "htmlcov",
        "ci-wheels",
        "temp-wheels",
        "target",  # Rust
        ".cargo",  # Rust
        "vendor",  # Go, PHP
        ".gradle",  # Java
        ".m2",  # Maven
        "bin",  # Generic binaries
        "obj",  # .NET
    }

    # File patterns to exclude
    EXCLUDED_PATTERNS = {
        "*.map",  # Source maps
        "*.vsix",  # VS Code extensions
        "*.whl",  # Python wheels
        "*.pyc",  # Python compiled
        "*.pyo",  # Python optimized
        "*.pyd",  # Python DLL
        "*.so",  # Shared objects
        "*.dylib",  # macOS libraries
        "*.dll",  # Windows libraries
        "*.exe",  # Executables
        "*.lock",  # Lock files
    }

    def execute(self, project_path: str) -> Dict[str, Any]:
        # Import here to avoid circular import
        from mcp_tools._progress_http import report_progress_http

        project = Path(project_path)

        # Report initial progress
        report_progress_http("onboardingProject", 0.0, "Starting project analysis")

        files = self._list_files(project, report_progress_http)

        # Report progress after file listing
        report_progress_http("onboardingProject", 0.25, f"Found {len(files)} files")

        language_stats = self._analyze_languages(files)

        # Report progress after language analysis
        report_progress_http("onboardingProject", 0.5, "Analyzed language distribution")

        dependency_files = self._find_dependency_files(files)

        # Report progress after dependency analysis
        report_progress_http("onboardingProject", 0.75, "Found dependency files")

        # Get top languages (exclude common generated files)
        relevant_languages = [
            (lang, count)
            for lang, count in language_stats.most_common(10)
            if lang not in {".map", ".lock", ".json", ".xml"}
        ][:3]

        summary = (
            f"Project '{project.name}' contains {len(files)} files. "
            f"Primary languages: {', '.join(lang for lang, _ in relevant_languages)}. "
            f"Found dependency files: {', '.join(dependency_files) if dependency_files else 'None'}."
        )

        result = {
            "status": "Analysis complete",
            "file_count": len(files),
            "language_stats": language_stats,
            "dependency_files": dependency_files,
            "summary": summary,
            "excluded_directories": sorted(list(self.EXCLUDED_DIRS)),
        }

        # Report completion
        report_progress_http("onboardingProject", 1.0, "Analysis complete")

        return result

    def _list_files(
        self,
        project_path: Path,
        report_progress_http: Callable[[str, float, str], None],
    ) -> List[Path]:
        """Lists all files in the project, respecting .gitignore and excluding common dependency directories."""
        gitignore_path = project_path / ".gitignore"
        spec = None
        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                spec = pathspec.PathSpec.from_lines("gitwildmatch", f)

        all_files = list(project_path.rglob("*"))
        total_items = len(all_files)

        files_to_process = []
        excluded_count = 0

        for idx, file in enumerate(all_files):
            if file.is_dir():
                continue

            relative_path = file.relative_to(project_path)

            # Skip excluded directories (node_modules, .git, etc.)
            if any(
                excluded_dir in relative_path.parts
                for excluded_dir in self.EXCLUDED_DIRS
            ):
                excluded_count += 1
                continue

            # Skip excluded file patterns (*.map, *.vsix, etc.)
            if any(file.match(pattern) for pattern in self.EXCLUDED_PATTERNS):
                excluded_count += 1
                continue

            # Skip ignored files from .gitignore
            if spec and spec.match_file(str(relative_path)):
                excluded_count += 1
                continue

            files_to_process.append(file)

            # Report progress every 100 items or at regular intervals
            if (idx + 1) % max(1, total_items // 10) == 0:
                progress = 0.01 + (idx / total_items) * 0.24  # 1%-25%
                report_progress_http(
                    "onboardingProject",
                    progress,
                    f"Processing {idx + 1}/{total_items} files",
                )

        return files_to_process

    def _analyze_languages(self, files: List[Path]) -> Counter:
        """Analyzes the programming languages based on file extensions."""
        extensions = [file.suffix for file in files if file.suffix]
        return Counter(extensions)

    def _find_dependency_files(self, files: List[Path]) -> List[str]:
        """Finds common dependency management files."""
        common_files = [
            "requirements.txt",
            "package.json",
            "pyproject.toml",
            "pom.xml",
            "build.gradle",
            "Cargo.toml",
        ]

        found_files = []
        for file in files:
            if file.name in common_files:
                found_files.append(file.name)

        return sorted(list(set(found_files)))
