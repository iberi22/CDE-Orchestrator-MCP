# src/cde_orchestrator/application/onboarding/publishing_use_case.py
import re
from pathlib import Path
from typing import Any, Dict, List

# Governance: Root-level .md files allowed (exceptions)
ROOT_ALLOWED_MD_FILES = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "LICENSE",
    "AGENTS.md",
    "GEMINI.md",
}

# Governance: Patterns blocked in root
ROOT_BLOCKED_PATTERNS = [
    r"^PHASE\d+C_.*\.md$",
    r"^SESSION.*\.md$",
    r"^SUMMARY.*\.md$",
    r"^REPORT.*\.md$",
    r"^REVIEW.*\.md$",
    r"^NOTES.*\.md$",
    r"^ANALYSIS.*\.md$",
    r"^EXECUTION.*\.md$",
    r"^FEEDBACK.*\.md$",
    r"^RESUMEN.*\.md$",
    r"^JULIUS.*\.md$",
    r"^WEEK-.*\.md$",
    r"^TEST.*\.md$",
]


class PublishingUseCase:
    """
    Writes a collection of documents to the filesystem.
    Enforces documentation governance rules (NO .md in root except approved files).
    """

    def execute(self, project_path: str, documents: Dict[str, str]) -> Dict[str, Any]:
        """
        Writes the given documents to the project path.

        Args:
            project_path: The root path of the project.
            documents: A dictionary where keys are relative file paths and values are content.

        Returns:
            A dictionary containing the status and a list of files written.
        """
        project = Path(project_path)
        files_written: List[str] = []

        for rel_path, content in documents.items():
            # GOVERNANCE CHECK: Block .md files in root (except approved)
            if self._violates_governance(rel_path):
                return {
                    "status": "error",
                    "message": f"❌ GOVERNANCE VIOLATION: {rel_path} blocked. "
                    f"Root .md files only allowed: {', '.join(ROOT_ALLOWED_MD_FILES)}. "
                    f"Use specs/, agent-docs/, or docs/ directories. "
                    f"See specs/governance/DOCUMENTATION_GOVERNANCE.md",
                    "files_written": files_written,
                }

            try:
                file_path = project / rel_path
                # Ensure parent directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                files_written.append(rel_path)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to write file {rel_path}: {e}",
                    "files_written": files_written,
                }

        return {
            "status": "success",
            "files_written": files_written,
        }

    def _violates_governance(self, rel_path: str) -> bool:
        """
        Check if file path violates documentation governance.

        Args:
            rel_path: Relative file path from project root

        Returns:
            True if violates governance (should be blocked), False otherwise
        """
        # Only check .md files
        if not rel_path.endswith(".md"):
            return False

        # Allow .github/copilot-instructions.md (special case)
        if rel_path == ".github/copilot-instructions.md":
            return False

        # Check if it's in root (no directory separator or starts with ./)
        path_parts = Path(rel_path).parts
        if len(path_parts) != 1:
            return False  # Not in root, allow

        filename = path_parts[0]

        # Check if it's an approved root file
        if filename in ROOT_ALLOWED_MD_FILES:
            return False  # Approved, allow

        # Check if matches blocked patterns
        for pattern in ROOT_BLOCKED_PATTERNS:
            if re.match(pattern, filename):
                return True  # Blocked pattern

        # Any other .md file in root is blocked
        return True
