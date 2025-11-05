"""
Codex CLI Adapter
"""
import json
import subprocess
from pathlib import Path
from typing import Dict, Any
from ...domain.ports import ICodeExecutor

class CodexAdapter(ICodeExecutor):
    """
    Adapter for Codex CLI.
    """
    async def execute_prompt(self, project_path: Path, prompt: str, context: Dict[str, Any]) -> str:
        """
        Execute a prompt using the Codex CLI.
        """
        try:
            command = ["codex", "--non-interactive", prompt]
            result = subprocess.run(
                command,
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )
            return json.dumps({
                "success": True,
                "output": result.stdout
            })
        except FileNotFoundError:
            return json.dumps({
                "success": False,
                "error": "codex command not found. Please install Codex CLI."
            })
        except subprocess.CalledProcessError as e:
            return json.dumps({
                "success": False,
                "error": f"Codex CLI failed with exit code {e.returncode}",
                "stdout": e.stdout,
                "stderr": e.stderr
            })
