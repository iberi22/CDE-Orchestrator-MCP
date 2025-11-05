# tests/unit/mcp_tools/test_agents.py

import pytest
import json
from unittest.mock import patch, MagicMock

from mcp_tools.agents import cde_selectAgent
from cde_orchestrator.adapters.agents.agent_selection_policy import AgentType

@pytest.mark.asyncio
@patch('shutil.which', return_value=True)
@patch('os.getenv', return_value='fake_key')
@patch('cde_orchestrator.adapters.agents.agent_selection_policy.AgentSelectionPolicy.suggest_agent', return_value=AgentType.COPILOT)
async def test_select_agent_simple_task(suggest_mock, getenv_mock, which_mock):
    result = await cde_selectAgent("A simple task")
    data = json.loads(result)
    assert data["selected_agent"] == "copilot"

@pytest.mark.asyncio
@patch('shutil.which', return_value=True)
@patch('os.getenv', return_value='fake_key')
@patch('cde_orchestrator.adapters.agents.agent_selection_policy.AgentSelectionPolicy.suggest_agent', return_value=AgentType.JULES)
async def test_select_agent_complex_task(suggest_mock, getenv_mock, which_mock):
    result = await cde_selectAgent("A complex task")
    data = json.loads(result)
    assert data["selected_agent"] == "jules"

@pytest.mark.asyncio
@patch('shutil.which', return_value=None)
@patch('os.getenv', return_value=None)
@patch('cde_orchestrator.adapters.agents.agent_selection_policy.AgentSelectionPolicy.suggest_agent', side_effect=ValueError("No suitable agent"))
async def test_select_agent_no_agents_available(suggest_mock, getenv_mock, which_mock):
    result = await cde_selectAgent("Any task")
    data = json.loads(result)
    assert "error" in data
