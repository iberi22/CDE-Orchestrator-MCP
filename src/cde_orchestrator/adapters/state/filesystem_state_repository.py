# src/cde_orchestrator/adapters/state/filesystem_state_repository.py
import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

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

    def __init__(self, state_file_path: Path, max_backups: int = 10):
        self.state_file_path = state_file_path
        self.backup_dir = self.state_file_path.parent / "backups"
        self.max_backups = max_backups
        self.state_file_path.parent.mkdir(parents=True, exist_ok=True)

    def load_state(self) -> Dict[str, Any]:
        """Loads the current state from the JSON file."""
        if not self.state_file_path.exists():
            return {}
        try:
            with open(self.state_file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load state from {self.state_file_path}: {e}")
            return {}

    def save_state(self, state: Dict[str, Any]):
        """Saves the given state to the JSON file."""
        if self.state_file_path.exists():
            self._create_backup()

        try:
            with open(self.state_file_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)
        except IOError as e:
            logger.error(f"Failed to save state to {self.state_file_path}: {e}")
            # Potentially restore backup here if needed
            raise

    def _create_backup(self) -> Path:
        """Create a timestamped backup of the current state file."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = self.backup_dir / f"state_{timestamp}.json"
        shutil.copy2(self.state_file_path, backup_path)
        self._rotate_backups()
        return backup_path

    def _rotate_backups(self):
        """Keep only the latest N backups."""
        backups = sorted(self.backup_dir.glob("state_*.json"), reverse=True)
        for stale_backup in backups[self.max_backups:]:
            try:
                stale_backup.unlink()
            except OSError as exc:
                logger.warning(f"Failed to remove old backup {stale_backup}: {exc}")
