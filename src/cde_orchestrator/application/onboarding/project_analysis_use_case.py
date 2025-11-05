# src/cde_orchestrator/application/onboarding/project_analysis_use_case.py
import os
from pathlib import Path
from typing import Dict, Any, List
from collections import Counter
import pathspec

class ProjectAnalysisUseCase:
    """
    Analyzes a software project to understand its structure, languages, and dependencies.
    """

    def execute(self, project_path: str) -> Dict[str, Any]:
        project = Path(project_path)

        files = self._list_files(project)

        language_stats = self._analyze_languages(files)

        dependency_files = self._find_dependency_files(files)

        summary = (
            f"Project '{project.name}' contains {len(files)} files. "
            f"Primary languages: {', '.join(lang for lang, _ in language_stats.most_common(3))}. "
            f"Found dependency files: {', '.join(dependency_files) if dependency_files else 'None'}."
        )

        return {
            "status": "Analysis complete",
            "file_count": len(files),
            "language_stats": language_stats,
            "dependency_files": dependency_files,
            "summary": summary,
        }

    def _list_files(self, project_path: Path) -> List[Path]:
        """Lists all files in the project, respecting .gitignore."""
        gitignore_path = project_path / ".gitignore"
        spec = None
        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                spec = pathspec.PathSpec.from_lines('gitwildmatch', f)

        all_files = project_path.rglob("*")

        files_to_process = []
        for file in all_files:
            if file.is_dir():
                continue

            relative_path = file.relative_to(project_path)

            # Skip ignored files
            if spec and spec.match_file(str(relative_path)):
                continue

            # Skip .git directory
            if '.git' in relative_path.parts:
                continue

            files_to_process.append(file)

        return files_to_process

    def _analyze_languages(self, files: List[Path]) -> Counter:
        """Analyzes the programming languages based on file extensions."""
        extensions = [file.suffix for file in files if file.suffix]
        return Counter(extensions)

    def _find_dependency_files(self, files: List[Path]) -> List[str]:
        """Finds common dependency management files."""
        common_files = [
            "requirements.txt", "package.json", "pyproject.toml",
            "pom.xml", "build.gradle", "Cargo.toml"
        ]

        found_files = []
        for file in files:
            if file.name in common_files:
                found_files.append(file.name)

        return sorted(list(set(found_files)))
