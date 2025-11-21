"""
Repository Adapter - Lightweight repository ingestion utilities inspired by gitingest.
Provides a small digest (tree, top files, content snippets) suitable to include in
LLM prompts. Non-invasive: does not write files or modify repo.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, List

from cde_orchestrator.domain.git import Commit, Modification
from cde_orchestrator.domain.ports import IGitAdapter

logger = logging.getLogger(__name__)


class GitAdapter(IGitAdapter):
    """
    Adapter for interacting with a local Git repository.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root

    async def _run_git_stream(self, args: list[str]) -> AsyncGenerator[str, None]:
        """
        Runs a git command as a subprocess and yields lines from stdout.
        """
        process = await asyncio.create_subprocess_exec(
            "git",
            *args,
            cwd=self.project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        assert process.stdout is not None
        assert process.stderr is not None

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            yield line.decode("utf-8").strip()

        # Wait for the subprocess to exit and check for errors
        await process.wait()
        if process.returncode != 0:
            stderr = (await process.stderr.read()).decode("utf-8").strip()
            raise RuntimeError("Git command failed: " + " ".join(args) + "\n" + stderr)

    async def traverse_commits(self) -> AsyncGenerator[Commit, None]:
        """
        Traverses the Git commit history and yields Commit objects.
        """
        # Format: hash|author|author_email|date|subject
        # Using --date=iso-strict for easier parsing
        commit_format = "%H|%an|%ae|%aI|%s"
        args = ["log", f"--pretty=format:{commit_format}"]

        async for line in self._run_git_stream(args):
            parts = line.split("|")
            if len(parts) == 5:
                commit_hash, author, author_email, date_str, message = parts
                # Parse date string to datetime object
                date = datetime.fromisoformat(date_str)
                yield Commit(
                    hash=commit_hash,
                    author=f"{author} <{author_email}>",
                    date=date,
                    message=message,
                )
            else:
                # Log a warning if a line doesn't match the expected format
                print(f"Warning: Could not parse commit line: {line}")

    async def get_modifications(self, commit_hash: str) -> List[Modification]:
        """
        Gets the file modifications for a given commit.
        """
        modifications: List[Modification] = []
        args = ["show", "--name-status", "--pretty=format:", commit_hash]

        async for line in self._run_git_stream(args):
            if not line.strip():
                continue

            parts = line.split("\t")
            if len(parts) < 2:
                continue

            change_type = parts[0].strip()
            old_path = Path(parts[1].strip()) if change_type != "A" else Path("")
            new_path = Path(parts[-1].strip())

            modifications.append(
                Modification(
                    change_type=change_type,
                    old_path=old_path,
                    new_path=new_path,
                )
            )
        return modifications
