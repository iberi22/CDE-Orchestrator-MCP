# tests/unit/adapters/state/test_filesystem_state_repository.py
import json
from pathlib import Path
from typing import Any, Dict

import pytest
import aiofiles

from cde_orchestrator.adapters.state.filesystem_state_repository import (
    FileSystemStateRepository,
)


@pytest.fixture
def temp_state_file(tmp_path: Path) -> Path:
    """Provides a temporary state file path for testing."""
    return tmp_path / "state" / "test_state.json"


@pytest.fixture
def state_repository(temp_state_file: Path) -> FileSystemStateRepository:
    """Provides a FileSystemStateRepository instance using a temp file."""
    return FileSystemStateRepository(temp_state_file)


@pytest.mark.asyncio
async def test_load_state_non_existent_file(state_repository: FileSystemStateRepository):
    """Should return an empty dict if the state file does not exist."""
    state = await state_repository.load_state()
    assert state == {}


@pytest.mark.asyncio
async def test_save_and_load_state(
    state_repository: FileSystemStateRepository, temp_state_file: Path
):
    """Should correctly save and then load the state."""
    test_state: Dict[str, Any] = {"features": {"feat1": {"status": "defining"}}}
    await state_repository.save_state(test_state)

    assert temp_state_file.exists()

    loaded_state = await state_repository.load_state()
    assert loaded_state == test_state


@pytest.mark.asyncio
async def test_save_state_creates_backup(
    state_repository: FileSystemStateRepository, temp_state_file: Path
):
    """Should create a backup of the existing state file before saving."""
    # First save
    await state_repository.save_state({"version": 1})

    # Second save
    await state_repository.save_state({"version": 2})

    backup_dir = temp_state_file.parent / "backups"
    assert backup_dir.exists()

    backups = list(backup_dir.glob("state_*.json"))
    assert len(backups) == 1

    async with aiofiles.open(backups[0], "r") as f:
        content = await f.read()
        backup_content = json.loads(content)

    assert backup_content == {"version": 1}


@pytest.mark.asyncio
async def test_backup_rotation(tmp_path: Path):
    """Should keep only the configured number of recent backups."""
    state_file = tmp_path / "state.json"
    repository = FileSystemStateRepository(state_file, max_backups=3)

    # Create 5 versions of the state
    for i in range(5):
        await repository.save_state({"version": i})

    backup_dir = state_file.parent / "backups"
    backups = sorted(backup_dir.glob("state_*.json"))

    assert len(backups) == 3

    # Check that the backups are the latest versions (2, 3, 4)
    # Note: The original file holds version 4, and the backups are of 1, 2, 3
    # The oldest backup of version 0 should be deleted.
    backup_versions = set()
    for backup_file in backups:
        async with aiofiles.open(backup_file, "r") as f:
            content = await f.read()
            backup_versions.add(json.loads(content)["version"])

    assert backup_versions == {1, 2, 3}


@pytest.mark.asyncio
async def test_load_state_handles_json_error(
    state_repository: FileSystemStateRepository, temp_state_file: Path
):
    """Should return an empty dict if the state file is corrupted."""
    temp_state_file.parent.mkdir(parents=True, exist_ok=True)
    temp_state_file.write_text("this is not json")

    state = await state_repository.load_state()
    assert state == {}
