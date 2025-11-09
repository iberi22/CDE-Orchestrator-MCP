"""
Unit tests for Jules Facade and dual-mode architecture.

Tests mode detection, routing logic, and fallback mechanisms.
"""

import json
import os
from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cde_orchestrator.adapters.agents import JulesFacade


class TestJulesFacadeModeDetection:
    """Test mode detection logic."""

    @pytest.mark.asyncio
    async def test_detect_api_mode_available(self) -> None:
        """Test detection when API mode is available."""
        with patch.dict(os.environ, {"JULES_API_KEY": "test-key"}):
            with patch("importlib.util.find_spec") as mock_spec:
                mock_spec.return_value = MagicMock()
                facade = JulesFacade()

                modes = await facade._detect_modes()

                assert modes.api.available is True
                assert modes.api.details["has_api_key"] is True
                assert modes.api.details["has_sdk"] is True

    @pytest.mark.asyncio
    async def test_detect_api_mode_unavailable_no_key(self) -> None:
        """Test detection when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("importlib.util.find_spec") as mock_spec:
                mock_spec.return_value = MagicMock()
                facade = JulesFacade()

                modes = await facade._detect_modes()

                assert modes.api.available is False
                assert modes.api.details["has_api_key"] is False

    @pytest.mark.asyncio
    async def test_detect_api_mode_unavailable_no_sdk(self) -> None:
        """Test detection when SDK is not installed."""
        with patch.dict(os.environ, {"JULES_API_KEY": "test-key"}):
            with patch("importlib.util.find_spec") as mock_spec:
                mock_spec.return_value = None
                facade = JulesFacade()

                modes = await facade._detect_modes()

                assert modes.api.available is False
                assert modes.api.details["has_sdk"] is False

    @pytest.mark.asyncio
    async def test_detect_cli_mode_available(self) -> None:
        """Test detection when CLI mode is available."""
        with patch("shutil.which") as mock_which:
            with patch("subprocess.run") as mock_run:
                mock_which.return_value = "/usr/bin/julius"
                mock_run.return_value = MagicMock(returncode=0, stdout="3.0.0")

                facade = JulesFacade()
                modes = await facade._detect_modes()

                assert modes.cli.available is True
                assert modes.cli.details["installed"] is True
                assert modes.cli.details["logged_in"] is True

    @pytest.mark.asyncio
    async def test_detect_cli_mode_unavailable_not_installed(self) -> None:
        """Test detection when CLI is not installed."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None

            facade = JulesFacade()
            modes = await facade._detect_modes()

            assert modes.cli.available is False
            assert modes.cli.details["installed"] is False

    @pytest.mark.asyncio
    async def test_detect_cli_mode_unavailable_not_logged_in(self) -> None:
        """Test detection when CLI is installed but user not logged in."""
        with patch("shutil.which") as mock_which:
            with patch("subprocess.run") as mock_run:
                mock_which.return_value = "/usr/bin/julius"

                def run_side_effect(*args: object, **kwargs: object) -> MagicMock:
                    result = MagicMock(returncode=0, stdout="3.0.0")
                    args_list = cast(list, args)
                    if args_list and "remote" in str(args_list[0]):
                        result.returncode = 1  # Not logged in
                    return result

                mock_run.side_effect = run_side_effect

                facade = JulesFacade()
                modes = await facade._detect_modes()

                assert modes.cli.available is False
                assert modes.cli.details["installed"] is True
                assert modes.cli.details["logged_in"] is False


class TestJulesFacadePreferredMode:
    """Test preferred mode selection logic."""

    @pytest.mark.asyncio
    async def test_preferred_mode_api_available(self) -> None:
        """Test that API mode is preferred when available."""
        with patch.dict(os.environ, {"JULES_API_KEY": "test-key"}):
            with patch("importlib.util.find_spec") as mock_spec:
                with patch("shutil.which") as mock_which:
                    mock_spec.return_value = MagicMock()
                    mock_which.return_value = "/usr/bin/julius"

                    facade = JulesFacade()
                    modes = await facade._detect_modes()

                    assert modes.preferred_mode == "api"

    @pytest.mark.asyncio
    async def test_preferred_mode_cli_when_api_unavailable(self) -> None:
        """Test that CLI mode is preferred when API unavailable."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("shutil.which") as mock_which:
                with patch("subprocess.run") as mock_run:
                    mock_which.return_value = "/usr/bin/julius"
                    mock_run.return_value = MagicMock(returncode=0, stdout="3.0.0")

                    facade = JulesFacade()
                    modes = await facade._detect_modes()

                    assert modes.preferred_mode == "cli_headless"

    @pytest.mark.asyncio
    async def test_preferred_mode_setup_when_nothing_available(self) -> None:
        """Test that setup mode is selected when nothing is available."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("shutil.which") as mock_which:
                mock_which.return_value = None

                facade = JulesFacade()
                modes = await facade._detect_modes()

                assert modes.preferred_mode == "setup"


class TestJulesFacadeAutoRouting:
    """Test automatic mode routing."""

    @pytest.mark.asyncio
    async def test_auto_mode_selects_api(self) -> None:
        """Test that auto mode selects API when available."""
        with patch.dict(os.environ, {"JULES_API_KEY": "test-key"}):
            with patch("importlib.util.find_spec") as mock_spec:
                with patch.object(
                    JulesFacade, "_execute_api", new_callable=AsyncMock
                ) as mock_execute_api:
                    mock_spec.return_value = MagicMock()
                    mock_execute_api.return_value = json.dumps({"success": True})

                    facade = JulesFacade()
                    result = await facade.execute_prompt(
                        project_path=Path("."),
                        prompt="Test prompt",
                        context={"mode": "auto"},
                    )

                    result_dict = json.loads(result)
                    assert result_dict["success"] is True
                    mock_execute_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_auto_mode_falls_back_to_cli(self) -> None:
        """Test that auto mode falls back to CLI when API unavailable."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("shutil.which") as mock_which:
                with patch("subprocess.run") as mock_run:
                    with patch.object(
                        JulesFacade, "_execute_cli_headless", new_callable=AsyncMock
                    ) as mock_execute_cli:
                        mock_which.return_value = "/usr/bin/julius"
                        mock_run.return_value = MagicMock(returncode=0, stdout="3.0.0")
                        mock_execute_cli.return_value = json.dumps({"success": True})

                        facade = JulesFacade()
                        result = await facade.execute_prompt(
                            project_path=Path("."),
                            prompt="Test prompt",
                            context={"mode": "auto"},
                        )

                        result_dict = json.loads(result)
                        assert result_dict["success"] is True
                        mock_execute_cli.assert_called_once()


class TestJulesFacadeExplicitMode:
    """Test explicit mode selection."""

    @pytest.mark.asyncio
    async def test_force_api_mode_succeeds(self) -> None:
        """Test forcing API mode when available."""
        with patch.dict(os.environ, {"JULES_API_KEY": "test-key"}):
            with patch("importlib.util.find_spec") as mock_spec:
                with patch.object(
                    JulesFacade, "_execute_api", new_callable=AsyncMock
                ) as mock_execute_api:
                    mock_spec.return_value = MagicMock()
                    mock_execute_api.return_value = json.dumps({"success": True})

                    facade = JulesFacade()
                    result = await facade.execute_prompt(
                        project_path=Path("."),
                        prompt="Test prompt",
                        context={"mode": "api"},
                    )

                    assert json.loads(result)["success"] is True

    @pytest.mark.asyncio
    async def test_force_api_mode_fails_when_unavailable(self) -> None:
        """Test that forcing API mode fails with clear error when unavailable."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("importlib.util.find_spec") as mock_spec:
                mock_spec.return_value = None

                facade = JulesFacade()

                with pytest.raises(
                    ValueError, match="API mode requested but not available"
                ):
                    await facade.execute_prompt(
                        project_path=Path("."),
                        prompt="Test prompt",
                        context={"mode": "api"},
                    )

    @pytest.mark.asyncio
    async def test_force_cli_mode_succeeds(self) -> None:
        """Test forcing CLI mode when available."""
        with patch("shutil.which") as mock_which:
            with patch("subprocess.run") as mock_run:
                with patch.object(
                    JulesFacade, "_execute_cli_headless", new_callable=AsyncMock
                ) as mock_execute_cli:
                    mock_which.return_value = "/usr/bin/julius"
                    mock_run.return_value = MagicMock(returncode=0, stdout="3.0.0")
                    mock_execute_cli.return_value = json.dumps({"success": True})

                    facade = JulesFacade()
                    result = await facade.execute_prompt(
                        project_path=Path("."),
                        prompt="Test prompt",
                        context={"mode": "cli"},
                    )

                    assert json.loads(result)["success"] is True


class TestSetupGuide:
    """Test setup guide generation."""

    def test_setup_guide_cli_not_installed(self) -> None:
        """Test setup guide when CLI not installed."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("shutil.which") as mock_which:
                mock_which.return_value = None

                facade = JulesFacade()
                from cde_orchestrator.adapters.agents.jules_facade import (
                    JulesModes,
                    ModeInfo,
                )

                modes = JulesModes(
                    api=ModeInfo(
                        available=False,
                        reason="API key not set",
                        details={"has_api_key": False, "has_sdk": False},
                    ),
                    cli=ModeInfo(
                        available=False,
                        reason="CLI not installed",
                        details={"installed": False},
                    ),
                    preferred_mode="setup",
                )

                guide_json = facade._generate_setup_guide(modes)
                guide = json.loads(guide_json)

                assert guide["status"] == "setup_required"
                assert len(guide["options"]) >= 1
                assert any(opt["mode"] == "cli" for opt in guide["options"])

    def test_setup_guide_has_both_options(self) -> None:
        """Test that setup guide provides both API and CLI options."""
        from cde_orchestrator.adapters.agents.jules_facade import JulesModes, ModeInfo

        modes = JulesModes(
            api=ModeInfo(
                available=False,
                reason="Missing API key and SDK",
                details={"has_api_key": False, "has_sdk": False},
            ),
            cli=ModeInfo(
                available=False,
                reason="CLI not installed",
                details={"installed": False, "logged_in": False},
            ),
            preferred_mode="setup",
        )

        facade = JulesFacade()
        guide_json = facade._generate_setup_guide(modes)
        guide = json.loads(guide_json)

        assert guide["status"] == "setup_required"
        assert len(guide["options"]) == 2
        modes_in_options = [opt["mode"] for opt in guide["options"]]
        assert "cli" in modes_in_options
        assert "api" in modes_in_options


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
