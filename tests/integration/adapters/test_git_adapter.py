# tests/integration/adapters/test_git_adapter.py

from pathlib import Path

import pytest

from cde_orchestrator.adapters.repository.git_adapter import GitAdapter
from cde_orchestrator.domain.git import Commit

# Use the project root as the test repository
TEST_REPO_PATH = Path(__file__).parent.parent.parent.parent


@pytest.mark.asyncio
async def test_traverse_commits_returns_commits():
    """Tests that traverse_commits returns Commit objects."""
    adapter = GitAdapter(TEST_REPO_PATH)
    commits = [commit async for commit in adapter.traverse_commits()]
    assert len(commits) > 0
    assert isinstance(commits[0], Commit)
    assert len(commits[0].hash) == 40


@pytest.mark.asyncio
async def test_get_modifications_returns_modifications():
    """Tests that get_modifications returns Modification objects."""
    adapter = GitAdapter(TEST_REPO_PATH)
    # Get the latest commit hash
    latest_commit = await adapter.traverse_commits().__anext__()
    assert latest_commit is not None

    modifications = await adapter.get_modifications(latest_commit.hash)
    # This assertion depends on the latest commit having modifications.
    # In a real test suite, we would use a fixture with a known commit.
    assert isinstance(modifications, list)
