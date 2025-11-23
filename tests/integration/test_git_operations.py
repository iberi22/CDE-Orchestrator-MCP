import asyncio
import os
import shutil
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest

from cde_orchestrator.adapters.repository.git_adapter import GitAdapter
from cde_orchestrator.domain.git import Commit, Modification


import stat

@pytest.fixture
def temp_git_repo() -> Generator[Path, None, None]:
    """
    Creates a temporary Git repository with some history.
    """
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir)

    try:
        # Initialize Git repo
        subprocess_run(["git", "init"], cwd=repo_path)
        subprocess_run(["git", "config", "user.name", "Test User"], cwd=repo_path)
        subprocess_run(["git", "config", "user.email", "test@example.com"], cwd=repo_path)

        # Commit 1: Add file1.txt
        (repo_path / "file1.txt").write_text("Content 1")
        subprocess_run(["git", "add", "file1.txt"], cwd=repo_path)
        subprocess_run(["git", "commit", "-m", "Initial commit"], cwd=repo_path)

        # Commit 2: Modify file1.txt and add file2.txt
        (repo_path / "file1.txt").write_text("Content 1 Modified")
        (repo_path / "file2.txt").write_text("Content 2")
        subprocess_run(["git", "add", "."], cwd=repo_path)
        subprocess_run(["git", "commit", "-m", "Second commit"], cwd=repo_path)

        yield repo_path

    finally:
        # Cleanup with robust error handling for Windows
        def on_rm_error(func, path, exc_info):
            # If access is denied, try to change permissions and retry
            os.chmod(path, stat.S_IWRITE)
            func(path)

        shutil.rmtree(temp_dir, onerror=on_rm_error)


def subprocess_run(args: list[str], cwd: Path) -> None:
    """Helper to run subprocess commands synchronously for setup."""
    import subprocess

    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


@pytest.mark.asyncio
async def test_git_adapter_traverse_commits(temp_git_repo: Path):
    """
    Test that GitAdapter correctly traverses commits in a temp repo.
    """
    adapter = GitAdapter(temp_git_repo)

    commits: list[Commit] = []
    async for commit in adapter.traverse_commits():
        commits.append(commit)

    # Should have 2 commits
    assert len(commits) == 2

    # Commits are usually returned in reverse chronological order (newest first)
    assert commits[0].message == "Second commit"
    assert commits[0].author == "Test User <test@example.com>"

    assert commits[1].message == "Initial commit"


@pytest.mark.asyncio
async def test_git_adapter_get_modifications(temp_git_repo: Path):
    """
    Test that GitAdapter correctly identifies modifications.
    """
    adapter = GitAdapter(temp_git_repo)

    # Get commits
    commits: list[Commit] = []
    async for commit in adapter.traverse_commits():
        commits.append(commit)

    latest_commit = commits[0]  # Second commit
    initial_commit = commits[1] # Initial commit

    # Check modifications for second commit
    mods_latest = await adapter.get_modifications(latest_commit.hash)

    # Expecting: M file1.txt, A file2.txt
    assert len(mods_latest) == 2

    changes = {str(m.new_path): m.change_type for m in mods_latest}
    assert changes.get("file1.txt") == "M"
    assert changes.get("file2.txt") == "A"

    # Check modifications for initial commit
    mods_initial = await adapter.get_modifications(initial_commit.hash)

    # Expecting: A file1.txt
    assert len(mods_initial) == 1
    assert mods_initial[0].change_type == "A"
    assert str(mods_initial[0].new_path) == "file1.txt"
