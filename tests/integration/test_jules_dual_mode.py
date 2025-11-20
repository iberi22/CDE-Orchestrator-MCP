"""Integration tests for Jules dual-mode architecture."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cde_orchestrator.adapters.agents import JulesFacade


class TestJulesDualModeIntegration:
    """Integration tests for dual-mode Jules execution."""

    @pytest.mark.asyncio
    async def test_setup_guide_when_no_mode_available(self) -> None:
        """Test setup guide generation when API and CLI unavailable."""
        facade = JulesFacade()

        with patch.object(facade, "_detect_modes") as mock_detect:
            modes = MagicMock()
            modes.api.available = False
            modes.cli.available = False
            modes.preferred_mode = None
            mock_detect.return_value = modes

            result = await facade.execute_prompt(
                project_path=Path("/test/project"),
                prompt="Test",
                context={},
                mode="auto",
            )

            assert result["status"] == "setup_required"
            assert "steps" in result["data"]

    @pytest.mark.asyncio
    async def test_api_mode_execution(self) -> None:
        """Test execution with API mode."""
        facade = JulesFacade()

        with patch.object(facade, "_detect_modes") as mock_detect:
            with patch.object(facade, "_get_api_adapter") as mock_get_api:
                modes = MagicMock()
                modes.api.available = True
                modes.cli.available = False
                modes.preferred_mode = "api"
                mock_detect.return_value = modes

                mock_adapter = AsyncMock()
                mock_adapter.execute_prompt.return_value = {
                    "status": "success",
                    "session_id": "test-123",
                    "data": {"modified_files": ["src/auth.py"]},
                }
                mock_get_api.return_value = mock_adapter

                result = await facade.execute_prompt(
                    project_path=Path("/test/project"),
                    prompt="Add auth",
                    context={},
                    mode="auto",
                )

                assert result["status"] == "success"
                assert result["mode"] == "api"

    @pytest.mark.asyncio
    async def test_cli_fallback(self) -> None:
        """Test CLI fallback when API unavailable."""
        facade = JulesFacade()

        with patch.object(facade, "_detect_modes") as mock_detect:
            with patch.object(facade, "_get_cli_adapter") as mock_get_cli:
                modes = MagicMock()
                modes.api.available = False
                modes.cli.available = True
                modes.preferred_mode = "cli"
                mock_detect.return_value = modes

                mock_adapter = AsyncMock()
                mock_adapter.execute_prompt.return_value = {
                    "status": "success",
                    "session_id": "cli-123",
                    "data": {},
                }
                mock_get_cli.return_value = mock_adapter

                result = await facade.execute_prompt(
                    project_path=Path("/test/project"),
                    prompt="Test",
                    context={},
                    mode="auto",
                )

                assert result["status"] == "success"
                assert result["mode"] == "cli"

    @pytest.mark.asyncio
    async def test_force_mode(self) -> None:
        """Test forcing a specific mode."""
        facade = JulesFacade()

        with patch.object(facade, "_get_api_adapter") as mock_get_api:
            mock_adapter = AsyncMock()
            mock_adapter.execute_prompt.return_value = {
                "status": "success",
                "session_id": "forced-123",
                "data": {},
            }
            mock_get_api.return_value = mock_adapter

            result = await facade.execute_prompt(
                project_path=Path("/test/project"),
                prompt="Test",
                context={},
                mode="api",
            )

            assert result["mode"] == "api"
            assert result["status"] == "success"
