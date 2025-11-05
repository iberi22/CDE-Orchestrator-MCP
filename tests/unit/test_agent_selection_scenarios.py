"""
Unit tests for agent selection policy scenarios.

Validates that the AgentSelectionPolicy.suggest_agent method selects the
correct agent for various real-world task descriptions.
"""

import pytest
from cde_orchestrator.adapters.agents.agent_selection_policy import AgentSelectionPolicy, AgentType

# A list of tuples: (task_description, expected_agent)
SCENARIOS = [
    # DeepAgents Scenarios (Research, Prototyping, Refactoring)
    ("Investigate the best Python libraries for asynchronous programming in 2025", AgentType.DEEPAGENTS),
    ("Create a prototype for a new feature that uses websockets", AgentType.DEEPAGENTS),
    ("Refactor the entire authentication module to improve security", AgentType.DEEPAGENTS),

    # Codex Scenarios (Analysis, Review)
    ("Analyze this code snippet for potential bugs and style issues", AgentType.CODEX),
    ("Review the logic in `user_service.py` and suggest improvements", AgentType.CODEX),
    ("What is the cyclomatic complexity of the `calculate_metrics` function?", AgentType.CODEX),

    # Rovo Dev Scenarios (Jira, Task Completion)
    ("Implement the feature described in ticket JIRA-456", AgentType.ROVODEV),
    ("Fix the bug reported in bug-tracker issue #1234", AgentType.ROVODEV),
    ("Close the loop on task TICKET-789 by committing the changes and updating the status.", AgentType.ROVODEV),

    # Gemini Scenarios (Code Completion, Light Research, Docs)
    ("Help me finish this function to calculate the average of a list", AgentType.GEMINI),
    ("What's a quick way to read a CSV file in Python?", AgentType.GEMINI),
    ("Generate documentation for the `api/v1/users` endpoint", AgentType.GEMINI),

    # Copilot Scenarios (Code Completion, Quick Fixes)
    ("There's a typo in the `README.md` file, please fix it", AgentType.COPILOT),
    ("Complete this line of code for me: `for i in range...`", AgentType.COPILOT),
    ("Fix the syntax error in `main.py` on line 52", AgentType.COPILOT),
]

@pytest.mark.parametrize("task_description, expected_agent", SCENARIOS)
def test_agent_selection_scenarios(task_description, expected_agent):
    """
    Tests that the agent selection policy suggests the correct agent for a given task.
    """
    suggested_agent = AgentSelectionPolicy.suggest_agent(task_description)
    assert suggested_agent == expected_agent, \
        f"For task '{task_description}', expected {expected_agent.value} but got {suggested_agent.value}"
