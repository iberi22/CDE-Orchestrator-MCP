"""
Unit tests for MCP agent tools.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

from mcp_tools.agents import cde_selectAgent, cde_listAvailableAgents


class TestCdeSelectAgent:
    """Test cde_selectAgent MCP tool."""

    @pytest.mark.asyncio
    async def test_select_agent_simple_task(self):
        """Test agent selection for simple task."""
        result = await cde_selectAgent("Fix typo in README")

        data = json.loads(result)

        assert "selected_agent" in data
        assert data["complexity"] == "trivial"
        assert "reasoning" in data
        assert "capabilities" in data

    @pytest.mark.asyncio
    async def test_select_agent_complex_task(self):
        """Test agent selection for complex task."""
        result = await cde_selectAgent("Implement complete authentication system")

        data = json.loads(result)

        assert "selected_agent" in data
        assert data["complexity"] == "complex"
        assert "reasoning" in data

    @pytest.mark.asyncio
    async def test_select_agent_epic_task(self):
        """Test agent selection for epic task."""
        result = await cde_selectAgent("Refactor entire system architecture")

        data = json.loads(result)

        assert "selected_agent" in data
        assert data["complexity"] == "epic"
        assert "reasoning" in data

    @pytest.mark.asyncio
    async def test_select_agent_no_agents_available(self):
        """Test behavior when no agents are available."""
        with patch('mcp_tools.agents.shutil.which', return_value=None):
            with patch.dict('os.environ', {}, clear=True):
                result = await cde_selectAgent("Any task")

                data = json.loads(result)
                assert "error" in data
                assert data["error"] == "No suitable agent available"


class TestCdeListAvailableAgents:
    """Test cde_listAvailableAgents MCP tool."""

    @pytest.mark.asyncio
    async def test_list_agents_with_all_available(self):
        """Test listing agents when all are available."""
        with patch('mcp_tools.agents.shutil.which', return_value='/usr/bin/gh'):
            with patch.dict('os.environ', {'JULES_API_KEY': 'test-key'}):
                with patch('importlib.util.find_spec', return_value=MagicMock()):
                    result = await cde_listAvailableAgents()

                    data = json.loads(result)
                    assert "available_agents" in data
                    assert "unavailable_agents" in data
                    assert "recommendations" in data

                    # Should have multiple agents available
                    assert len(data["available_agents"]) > 0

    @pytest.mark.asyncio
    async def test_list_agents_with_none_available(self):
        """Test listing agents when none are available."""
        with patch('mcp_tools.agents.shutil.which', return_value=None):
            with patch.dict('os.environ', {}, clear=True):
                with patch('importlib.util.find_spec', return_value=None):
                    result = await cde_listAvailableAgents()

                    data = json.loads(result)
                    assert "available_agents" in data
                    assert "unavailable_agents" in data

                    # Should have no agents available
                    assert len(data["available_agents"]) == 0
                    assert len(data["unavailable_agents"]) > 0