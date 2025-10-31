# src/cde_orchestrator/state_manager.py
import json
from pathlib import Path
from typing import Dict, Any

class StateManager:
    """Manages the project's state by reading/writing to a JSON file."""

    def __init__(self, state_file_path: Path):
        self.state_file_path = state_file_path

    def load_state(self) -> Dict[str, Any]:
        """Loads the current state from the JSON file."""
        if not self.state_file_path.exists():
            return {}
        with open(self.state_file_path, 'r') as f:
            return json.load(f)

    def save_state(self, state: Dict[str, Any]):
        """Saves the given state to the JSON file."""
        self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file_path, 'w') as f:
            json.dump(state, f, indent=4)
