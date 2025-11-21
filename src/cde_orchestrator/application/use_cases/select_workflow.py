# src/cde_orchestrator/application/use_cases/select_workflow.py
import re
from typing import Dict, List


class SelectWorkflowUseCase:
    """
    Use case for intelligently selecting the best workflow based on user input.
    """

    def __init__(self, workflow_patterns: Dict[str, List[str]]):
        self._workflow_patterns = workflow_patterns

    def execute(self, user_prompt: str) -> str:
        """
        Analyzes the user prompt to determine the most appropriate workflow type.
        Returns the workflow type or 'default' if no specific type is detected.
        """
        user_prompt_lower = user_prompt.lower()

        scores = {}
        for workflow_type, patterns in self._workflow_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, user_prompt_lower):
                    score += 1
            scores[workflow_type] = score

        if scores and max(scores.values()) > 0:
            return max(scores, key=lambda k: scores[k])

        return "default"
