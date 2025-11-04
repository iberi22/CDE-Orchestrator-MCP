# src/cde_orchestrator/application/use_cases/manage_state.py
import logging
from typing import Any, Dict, List, Tuple
from pydantic import ValidationError

from ...domain.entities import Feature, FeatureState, FeatureStatus, PhaseStatus
from ...domain.ports import IStateStore

logger = logging.getLogger(__name__)


class ManageStateUseCase:
    """
    Orchestrates the loading, validation, and saving of application state.
    """

    def __init__(self, state_store: IStateStore):
        self._state_store = state_store
        self._last_state_snapshot: Dict[str, Any] = {}

    def load_and_validate_state(self) -> Dict[str, Any]:
        """Loads, migrates, and validates the state."""
        raw_state = self._state_store.load_state()
        migrated_state = self._migrate_state(raw_state)
        self._last_state_snapshot = migrated_state
        return migrated_state

    def save_state(self, state: Dict[str, Any]):
        """Validates and saves the application state."""
        validated_state = self._validate_state(state)
        self._state_store.save_state(validated_state)
        self._log_state_changes(validated_state)
        self._last_state_snapshot = validated_state

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
                feature_state = self._coerce_feature_state(feature_id, feature__data)
                new_features[feature_id] = feature_state.serialize()
            except ValidationError as exc:
                logger.error("Feature %s could not be migrated: %s", feature_id, exc)
        migrated["features"] = new_features
        return migrated

    def _log_state_changes(self, new_state: Dict[str, Any]):
        """Log high-level state changes for observability."""
        old_features = self._last_state_snapshot.get("features", {})
        new_features = new_state.get("features", {})

        created, updated, removed = self._compare_features(old_features, new_features)

        for feature_id in created:
            logger.info(
                "Feature %s created with status %s",
                feature_id,
                new_features[feature_id].get("status", "N/A"),
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
