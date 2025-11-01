# src/cde_orchestrator/workflow_manager.py
import re
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from .models import Workflow


class WorkflowManager:
    """Handles loading and parsing of workflow files with intelligent workflow selection."""

    def __init__(self, workflow_path: Path):
        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow file not found at {workflow_path}")
        self.workflow_path = workflow_path
        self.workflow = self._load_workflow()
        self.workflow_patterns = self._initialize_workflow_patterns()

    def _load_workflow(self) -> Workflow:
        """Loads and validates the workflow file using Pydantic models."""
        with open(self.workflow_path, 'r') as f:
            data = yaml.safe_load(f)
        return Workflow(**data)

    def _initialize_workflow_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for automatic workflow detection."""
        return {
            "web_application": [
                r"web.*app", r"website", r"frontend", r"backend", r"api",
                r"authentication", r"login", r"user.*management", r"dashboard"
            ],
            "data_processing": [
                r"data.*process", r"etl", r"pipeline", r"analytics",
                r"machine.*learning", r"ml", r"ai", r"algorithm"
            ],
            "mobile_app": [
                r"mobile.*app", r"ios", r"android", r"react.*native",
                r"flutter", r"mobile"
            ],
            "infrastructure": [
                r"deploy", r"docker", r"kubernetes", r"ci.*cd",
                r"infrastructure", r"devops", r"monitoring"
            ],
            "bug_fix": [
                r"fix", r"bug", r"error", r"issue", r"problem",
                r"broken", r"not.*working"
            ]
        }

    def detect_workflow_type(self, user_prompt: str) -> str:
        """
        Analyzes the user prompt to determine the most appropriate workflow type.
        Returns the workflow type or 'default' if no specific type is detected.
        """
        user_prompt_lower = user_prompt.lower()

        scores = {}
        for workflow_type, patterns in self.workflow_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, user_prompt_lower):
                    score += 1
            scores[workflow_type] = score

        # Return the workflow type with the highest score
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)

        return "default"

    def get_phase(self, phase_id: str):
        """Retrieves a specific phase by its ID."""
        for phase in self.workflow.phases:
            if phase.id == phase_id:
                return phase
        raise ValueError(f"Phase with ID '{phase_id}' not found in workflow.")

    def get_initial_phase(self):
        """Gets the very first phase of the workflow."""
        if not self.workflow.phases:
            raise ValueError("Workflow has no phases defined.")
        return self.workflow.phases[0]

    def get_next_phase(self, current_phase_id: str) -> Optional[str]:
        """Gets the next phase in the workflow sequence."""
        phase_ids = [phase.id for phase in self.workflow.phases]
        try:
            current_index = phase_ids.index(current_phase_id)
            if current_index + 1 < len(phase_ids):
                return phase_ids[current_index + 1]
            return None  # No next phase (workflow complete)
        except ValueError:
            raise ValueError(f"Phase '{current_phase_id}' not found in workflow.")

    def get_workflow_progress(self, current_phase_id: str) -> Dict[str, any]:
        """Returns workflow progress information."""
        phase_ids = [phase.id for phase in self.workflow.phases]
        try:
            current_index = phase_ids.index(current_phase_id)
            return {
                "current_phase": current_phase_id,
                "phase_number": current_index + 1,
                "total_phases": len(phase_ids),
                "progress_percentage": ((current_index + 1) / len(phase_ids)) * 100,
                "remaining_phases": phase_ids[current_index + 1:],
                "completed_phases": phase_ids[:current_index]
            }
        except ValueError:
            raise ValueError(f"Phase '{current_phase_id}' not found in workflow.")

