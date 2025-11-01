# src/cde_orchestrator/adapters/state/state_adapter.py
import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from pydantic import ValidationError

from ..serialization import FeatureState, FeatureStatus, PhaseStatus

logger = logging.getLogger(__name__)


class StateAdapter:
    """Manages the project's state by reading/writing to a JSON file."""

    def __init__(self, state_file_path: Path):
        self.state_file_path = state_file_path
        self.backup_dir = self.state_file_path.parent / "backups"
        self._last_state_snapshot: Dict[str, Any] = {}

    def load_state(self) -> Dict[str, Any]:
        """Loads the current state from the JSON file."""
        if not self.state_file_path.exists():
            self._last_state_snapshot = {}
            return {}

        with open(self.state_file_path, "r", encoding="utf-8") as f:
            raw_state = json.load(f)

        migrated_state = self._migrate_state(raw_state)
        # Keep snapshot for change detection
        self._last_state_snapshot = json.loads(json.dumps(migrated_state))
        return migrated_state

    def save_state(self, state: Dict[str, Any]):
        """Saves the given state to the JSON file."""
        validated_state = self._validate_state(state)

        if self.state_file_path.exists():
            self._create_backup()

        self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file_path, "w", encoding="utf-8") as f:
            json.dump(validated_state, f, indent=4)

        self._log_state_changes(validated_state)
        # Update snapshot after successful write
        self._last_state_snapshot = json.loads(json.dumps(validated_state))

    # --- Internal helpers -------------------------------------------------

    def _validate_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize state before persisting."""
        normalized = dict(state)
        features = normalized.get("features", {})
        validated_features = {}
        for feature_id, feature_data in features.items():
            try:
                feature_state = self._coerce_feature_state(feature_id, feature_data)
                validated_features[feature_id] = feature_state.serialize()
            except ValidationError as exc:
                logger.error("Feature %s failed validation: %s", feature_id, exc)
                raise
        normalized["features"] = validated_features
        return normalized

    def _coerce_feature_state(
        self, feature_id: str, feature_data: Dict[str, Any]
    ) -> FeatureState:
        """Coerce loose dict data into a validated FeatureState instance."""
        if not isinstance(feature_data, dict):
            logger.warning("Feature %s contains non-dict state; coercing", feature_id)
            feature_data = {"prompt": str(feature_data)}

        status = feature_data.get("status", FeatureStatus.DEFINING.value)
        current_phase = feature_data.get("current_phase") or PhaseStatus.DEFINE.value

        created_at = (
            feature_data.get("created_at") or datetime.now(timezone.utc).isoformat()
        )
        updated_at = feature_data.get("updated_at")
        previous_features = self._last_state_snapshot.get("features") or {}
        if feature_id in previous_features:
            previous = previous_features[feature_id]
            if feature_data != previous:
                updated_at = datetime.now(timezone.utc).isoformat()

        issues = feature_data.get("issues") or []
        if not isinstance(issues, list):
            issues = [issues]

        commits = feature_data.get("commits") or []
        if not isinstance(commits, list):
            commits = [commits]

        progress = feature_data.get("progress") or {}
        if not isinstance(progress, dict):
            progress = {"raw": progress}

        prompt = feature_data.get("prompt", "")
        completed_at = feature_data.get("completed_at")

        return FeatureState(
            status=status,
            current_phase=current_phase,
            workflow_type=feature_data.get("workflow_type", "default"),
            prompt=prompt,
            created_at=created_at,
            updated_at=updated_at,
            branch=feature_data.get("branch"),
            issues=issues,
            progress=progress,
            recipe_id=feature_data.get("recipe_id"),
            recipe_name=feature_data.get("recipe_name"),
            commits=commits,
            completed_at=completed_at,
        )

    def _migrate_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate legacy state structures to the current schema."""
        if not state:
            return {}

        migrated = dict(state)
        features = migrated.get("features", {})
        new_features = {}
        for feature_id, feature_data in features.items():
            try:
                feature_state = self._coerce_feature_state(feature_id, feature_data)
                new_features[feature_id] = feature_state.serialize()
            except ValidationError as exc:
                logger.error("Feature %s could not be migrated: %s", feature_id, exc)
        migrated["features"] = new_features
        return migrated

    def _create_backup(self) -> Path:
        """Create a timestamped backup of the current state file."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = self.backup_dir / f"state_{timestamp}.json"
        shutil.copy2(self.state_file_path, backup_path)
        self._rotate_backups(max_files=10)
        return backup_path

    def _rotate_backups(self, max_files: int = 10):
        """Keep only the latest N backups."""
        backups = sorted(self.backup_dir.glob("state_*.json"), reverse=True)
        for stale_backup in backups[max_files:]:
            try:
                stale_backup.unlink()
            except OSError as exc:
                logger.warning("Failed to remove old backup %s: %s", stale_backup, exc)

    def _log_state_changes(self, new_state: Dict[str, Any]):
        """Log high-level state changes for observability."""
        old_features = (self._last_state_snapshot or {}).get("features", {})
        new_features = new_state.get("features", {})

        created, updated, removed = self._compare_features(old_features, new_features)

        for feature_id in created:
            logger.info(
                "Feature %s created with status %s",
                feature_id,
                new_features[feature_id]["status"],
            )
        for feature_id, changes in updated.items():
            change_str = ", ".join(f"{k}: {v[0]} -> {v[1]}" for k, v in changes.items())
            logger.info("Feature %s updated (%s)", feature_id, change_str)
        for feature_id in removed:
            logger.info("Feature %s removed from state", feature_id)

    def _compare_features(
        self,
        old_features: Dict[str, Any],
        new_features: Dict[str, Any],
    ) -> Tuple[List[str], Dict[str, Dict[str, Tuple[Any, Any]]], List[str]]:
        """Compare old and new feature dictionaries."""
        created = [fid for fid in new_features if fid not in old_features]
        removed = [fid for fid in old_features if fid not in new_features]
        updated: Dict[str, Dict[str, Tuple[Any, Any]]] = {}

        for fid, new_data in new_features.items():
            if fid in created:
                continue
            old_data = old_features.get(fid, {})
            changes: Dict[str, Tuple[Any, Any]] = {}
            for key in ["status", "current_phase", "branch"]:
                if old_data.get(key) != new_data.get(key):
                    changes[key] = (old_data.get(key), new_data.get(key))
            if changes:
                updated[fid] = changes

        return created, updated, removed
