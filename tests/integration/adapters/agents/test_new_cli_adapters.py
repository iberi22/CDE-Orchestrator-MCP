"""
Integration tests for New CLI Code Adapters.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

from cde_orchestrator.adapters.agents.deep_agents_adapter import DeepAgentsAdapter
from cde_orchestrator.adapters.agents.codex_adapter import CodexAdapter
from cde_orchestrator.adapters.agents.rovo_dev_adapter import RovoDevAdapter

@pytest.mark.asyncio
class TestDeepAgentsAdapter:
    """Test DeepAgents CLI adapter integration."""

    @pytest.fixture
    def adapter(self):
        return DeepAgentsAdapter()

    async def test_execute_prompt_success(self, adapter, tmp_path):
        """Test successful prompt execution."""
        mock_response = '{"status": "success", "result": "research complete"}'

        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = mock_response
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result_str = await adapter.execute_prompt(tmp_path, "research topic", {})
            result = json.loads(result_str)

            mock_run.assert_called_once_with(
                ["deepagents", "--non-interactive", "research topic"],
                cwd=tmp_path,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )
            assert result["success"] is True
            assert "research complete" in result["output"]

    async def test_execute_prompt_not_found(self, adapter, tmp_path):
        with patch('subprocess.run', side_effect=FileNotFoundError):
            result_str = await adapter.execute_prompt(tmp_path, "test", {})
            result = json.loads(result_str)
            assert result["success"] is False
            assert "not found" in result["error"]

@pytest.mark.asyncio
class TestCodexAdapter:
    """Test Codex CLI adapter integration."""

    @pytest.fixture
    def adapter(self):
        return CodexAdapter()

    async def test_execute_prompt_success(self, adapter, tmp_path):
        """Test successful prompt execution."""
        mock_response = '{"status": "success", "analysis": "code is good"}'

        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = mock_response
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result_str = await adapter.execute_prompt(tmp_path, "analyze code", {})
            result = json.loads(result_str)

            mock_run.assert_called_once_with(
                ["codex", "--non-interactive", "analyze code"],
                cwd=tmp_path,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )
            assert result["success"] is True
            assert "code is good" in result["output"]

@pytest.mark.asyncio
class TestRovoDevAdapter:
    """Test Rovo Dev CLI adapter integration."""

    @pytest.fixture
    def adapter(self):
        return RovoDevAdapter()

    async def test_execute_prompt_success(self, adapter, tmp_path):
        """Test successful prompt execution."""
        mock_response = '{"status": "success", "task": "JIRA-123 done"}'

        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = mock_response
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result_str = await adapter.execute_prompt(tmp_path, "complete JIRA-123", {})
            result = json.loads(result_str)

            mock_run.assert_called_once_with(
                ["rovo", "dev", "--non-interactive", "complete JIRA-123"],
                cwd=tmp_path,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )
            assert result["success"] is True
            assert "JIRA-123 done" in result["output"]
