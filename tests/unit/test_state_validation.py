import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from cde_orchestrator.models import FeatureState, FeatureStatus, PhaseStatus
from cde_orchestrator.state_manager import StateManager


def _state_manager(tmp_path: Path) -> StateManager:
    state_file = tmp_path / "state.json"
    return StateManager(state_file)


def _feature_state(status: FeatureStatus, phase: PhaseStatus, prompt: str = "prompt") -> dict:
    feature = FeatureState(
        status=status,
        current_phase=phase,
        prompt=prompt,
        workflow_type="default",
        created_at=datetime.now(timezone.utc),
        progress={"phase": phase.value},
    )
    return feature.serialize()


def test_save_state_creates_backup_and_updates_timestamp(tmp_path):
    manager = _state_manager(tmp_path)
    feature_id = "feature-1"

    state = {"features": {feature_id: _feature_state(FeatureStatus.DEFINING, PhaseStatus.DEFINE)}}
    manager.save_state(state)

    # Update status and phase to trigger new save + backup creation
    state["features"][feature_id] = _feature_state(FeatureStatus.DESIGNING, PhaseStatus.DESIGN)
    manager.save_state(state)

    backups_dir = tmp_path / "backups"
    backups = list(backups_dir.glob("state_*.json"))

    assert backups, "Expected backup file to be created on subsequent save"
    # Latest state should reflect new phase/status
    loaded_state = manager.load_state()
    saved_feature = loaded_state["features"][feature_id]
    assert saved_feature["status"] == FeatureStatus.DESIGNING.value
    assert saved_feature["current_phase"] == PhaseStatus.DESIGN.value
    assert saved_feature["updated_at"] is not None


def test_invalid_feature_status_raises_validation_error(tmp_path):
    manager = _state_manager(tmp_path)
    invalid_state = {
        "features": {
            "feature-2": {
                "status": "unknown",
                "current_phase": "define",
                "prompt": "invalid status example",
            }
        }
    }

    with pytest.raises(ValidationError):
        manager.save_state(invalid_state)


def test_load_state_migrates_legacy_structure(tmp_path):
    state_file = tmp_path / "state.json"
    legacy_state = {
        "features": {
            "legacy-feature": {
                "status": "defining",
                "current_phase": "define",
                "prompt": "legacy prompt",
            }
        }
    }
    state_file.write_text(json.dumps(legacy_state))

    manager = StateManager(state_file)
    migrated = manager.load_state()
    feature = migrated["features"]["legacy-feature"]

    assert feature["status"] == "defining"
    assert "created_at" in feature
    assert feature["progress"] == {}
