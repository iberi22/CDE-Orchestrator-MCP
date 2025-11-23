# src/cde_orchestrator/adapters/state/filesystem_state_repository.py
import json
import logging
import shutil
import asyncio
import aiofiles
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Union, cast

from ...domain.ports import IStateStore

logger = logging.getLogger(__name__)


class FileSystemStateRepository(IStateStore):
    """
    Stores the application's state as a JSON file on the filesystem.

    This adapter is responsible for the low-level mechanics of:
    - Reading and writing the state file.
    - Creating timestamped backups.
    - Rotating old backups to save space.
    """

    def __init__(
        self, state_file_path: Union[str, Path], max_backups: int = 10
    ) -> None:
        # Ensure state_file_path is a Path object
        if isinstance(state_file_path, str):
            state_file_path = Path(state_file_path)

        self.state_file_path = state_file_path
        self.backup_dir = self.state_file_path.parent / "backups"
        self.max_backups = max_backups
        self.state_file_path.parent.mkdir(parents=True, exist_ok=True)

    async def load_state(self) -> Dict[str, Any]:
        """Loads the current state from the JSON file."""
        if not self.state_file_path.exists():
            return {}
        try:
            async with aiofiles.open(self.state_file_path, "r", encoding="utf-8") as f:
                content = await f.read()
                return cast(Dict[str, Any], json.loads(content))
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load state from {self.state_file_path}: {e}")
            return {}

    async def save_state(self, state: Dict[str, Any]) -> None:
        """Saves the given state to the JSON file."""
        if self.state_file_path.exists():
            await self._create_backup()

        try:
            async with aiofiles.open(self.state_file_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(state, indent=4))
        except IOError as e:
            logger.error(f"Failed to save state to {self.state_file_path}: {e}")
            # Potentially restore backup here if needed
            raise

    async def _create_backup(self) -> Path:
        """Create a timestamped backup of the current state file."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = self.backup_dir / f"state_{timestamp}.json"

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, shutil.copy2, self.state_file_path, backup_path)

        await self._rotate_backups()
        return backup_path

    async def _rotate_backups(self) -> None:
        """Keep only the latest N backups."""
        loop = asyncio.get_running_loop()

        def _rotate():
            backups = sorted(self.backup_dir.glob("state_*.json"), reverse=True)
            for stale_backup in backups[self.max_backups :]:
                try:
                    stale_backup.unlink()
                except OSError as exc:
                    logger.warning(f"Failed to remove old backup {stale_backup}: {exc}")

        await loop.run_in_executor(None, _rotate)
