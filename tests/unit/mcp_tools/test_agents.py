# tests/unit/mcp_tools/test_agents.py

import pytest
import json
from unittest.mock import patch

from mcp_tools.agents import cde_selectAgent, cde_listAvailableAgents
from cde_orchestrator.adapters.agents.agent_selection_policy import AgentSelectionPolicy, AgentType, AgentCapabilities

# Mock AgentSelectionPolicy for testing
class MockAgentSelectionPolicy:
    FALLBACK_CHAIN = [AgentType.JULES, AgentType.COPILOT]
    CAPABILITIES = {
        AgentType.JULES: AgentCapabilities(
            agent_type=AgentType.JULES,
            supports_async=True,
            supports_plan_approval=True,
            max_context_lines=100000,
            best_for=["refactoring"],
            requires_auth=True
        ),
        AgentType.COPILOT: AgentCapabilities(
            agent_type=AgentType.COPILOT,
            supports_async=False,
            supports_plan_approval=False,
            max_context_lines=4096,
            best_for=["simple-task"],
            requires_auth=False
        ),
    }

    def suggest_agent(self, task_description: str):
        if "simple" in task_description:
            return AgentType.COPILOT
        return AgentType.JULES

@pytest.fixture
def mock_policy():
    return MockAgentSelectionPolicy()

@pytest.mark.asyncio
@patch('shutil.which', return_value=True)
@patch('os.getenv', return_value='fake_key')
async def test_select_agent_simple_task(getenv_mock, which_mock, mock_policy):
    result = await cde_selectAgent("A simple task", agent_selection_policy=mock_policy)
    data = json.loads(result)
    assert data["selected_agent"] == "copilot"

@pytest.mark.asyncio
@patch('shutil.which', return_value=True)
@patch('os.getenv', return_value='fake_key')
async def test_select_agent_complex_task(getenv_mock, which_mock, mock_policy):
    result = await cde_selectAgent("A complex task", agent_selection_policy=mock_policy)
    data = json.loads(result)
    assert data["selected_agent"] == "jules"

@pytest.mark.asyncio
@patch('shutil.which', return_value=None)
@patch('os.getenv', return_value=None)
async def test_select_agent_no_agents_available(getenv_mock, which_mock, mock_policy):
    result = await cde_selectAgent("Any task", agent_selection_policy=mock_policy)
    data = json.loads(result)
    assert "error" in data
    assert data["error"] == "No suitable agent available"
