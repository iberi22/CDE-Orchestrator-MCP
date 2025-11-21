"""Integration tests for Jules dual-mode architecture."""

from pathlib import Path
from unittest.mock import patch

import pytest

from cde_orchestrator.adapters.agents import JulesFacade


class TestJulesDualModeIntegration:
    """Integration tests for dual-mode Jules execution."""

    @pytest.mark.asyncio
    async def test_setup_guide_when_no_mode_available(self) -> None:
        """Test setup guide generation when API and CLI unavailable."""
        facade = JulesFacade()

        with patch.object(facade, "_detect_modes") as mock_detect:
            from cde_orchestrator.adapters.agents.jules_facade import (
                JulesModes,
                ModeInfo,
            )

            # Mock modes with proper types
            api_mode = ModeInfo(
                available=False, reason="JULIUS_API_KEY not set", details={}
            )
            cli_mode = ModeInfo(
                available=False, reason="julius CLI not found", details={}
            )
            modes = JulesModes(api=api_mode, cli=cli_mode, preferred_mode="setup")
            mock_detect.return_value = modes

            result = await facade.execute_prompt(
                project_path=Path("/test/project"),
                prompt="Test",
                context={},
                mode="auto",
            )

            assert result["status"] == "setup_required"
            assert "options" in result
            assert len(result["options"]) > 0

    @pytest.mark.asyncio
    async def test_api_mode_execution(self) -> None:
        """Test execution with API mode."""
        facade = JulesFacade()

        with patch.object(facade, "_detect_modes") as mock_detect:
            with patch.object(facade, "_execute_api") as mock_execute_api:
                from cde_orchestrator.adapters.agents.jules_facade import (
                    JulesModes,
                    ModeInfo,
                )

                # Mock modes with proper types
                api_mode = ModeInfo(
                    available=True, reason="API key configured", details={}
                )
                cli_mode = ModeInfo(
                    available=False, reason="CLI not available", details={}
                )
                modes = JulesModes(api=api_mode, cli=cli_mode, preferred_mode="api")
                mock_detect.return_value = modes

                # Mock API execution
                mock_execute_api.return_value = {
                    "status": "success",
                    "mode": "api",
                    "session_id": "test-123",
                    "data": {"modified_files": ["src/auth.py"]},
                }

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
            with patch.object(facade, "_execute_cli_headless") as mock_execute_cli:
                from cde_orchestrator.adapters.agents.jules_facade import (
                    JulesModes,
                    ModeInfo,
                )

                # Mock modes with proper types
                api_mode = ModeInfo(
                    available=False, reason="API key not set", details={}
                )
                cli_mode = ModeInfo(available=True, reason="CLI available", details={})
                modes = JulesModes(
                    api=api_mode, cli=cli_mode, preferred_mode="cli_headless"
                )
                mock_detect.return_value = modes

                # Mock CLI execution
                mock_execute_cli.return_value = {
                    "status": "success",
                    "mode": "cli",
                    "session_id": "cli-123",
                    "data": {},
                }

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

        with patch.object(facade, "_detect_modes") as mock_detect:
            with patch.object(facade, "_execute_api") as mock_execute_api:
                from cde_orchestrator.adapters.agents.jules_facade import (
                    JulesModes,
                    ModeInfo,
                )

                # Mock modes with proper types
                api_mode = ModeInfo(
                    available=True, reason="API key configured", details={}
                )
                cli_mode = ModeInfo(available=True, reason="CLI available", details={})
                modes = JulesModes(api=api_mode, cli=cli_mode, preferred_mode="api")
                mock_detect.return_value = modes

                # Mock API execution
                mock_execute_api.return_value = {
                    "status": "success",
                    "mode": "api",
                    "session_id": "forced-123",
                    "data": {},
                }

                result = await facade.execute_prompt(
                    project_path=Path("/test/project"),
                    prompt="Test",
                    context={},
                    mode="api",
                )

                assert result["mode"] == "api"
                assert result["status"] == "success"
