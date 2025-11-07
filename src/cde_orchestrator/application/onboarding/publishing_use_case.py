# src/cde_orchestrator/application/onboarding/publishing_use_case.py
from pathlib import Path
from typing import Dict, List


class PublishingUseCase:
    """
    Writes a collection of documents to the filesystem.
    """

    def execute(self, project_path: str, documents: Dict[str, str]) -> Dict[str, str]:
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
