"""
Jules Facade - Intelligent dual-mode router with automatic fallback.

Provides unified interface for Jules execution with intelligent mode selection:
    1. API Mode: Full async agent (preferred if available)
    2. CLI Mode: Local execution via julius CLI (fallback)
    3. Setup Mode: Guided onboarding (if neither available)

This facade detects available modes and automatically selects the best option,
providing seamless user experience regardless of configuration.
"""

import json
import os
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...domain.ports import ICodeExecutor


@dataclass
class ModeInfo:
    """Information about a Jules mode's availability."""

    available: bool
    reason: str
    details: Dict[str, Any]


@dataclass
class JulesModes:
    """Complete modes detection result."""

    api: ModeInfo
    cli: ModeInfo
    preferred_mode: str  # "api", "cli_headless", or "setup"


class JulesFacade(ICodeExecutor):
    """
    Intelligent Jules router with automatic mode selection and fallback.

    Modes:
        - "api": Async agent via julius-agent-sdk (best for complex tasks)
        - "cli_headless": Local CLI execution in background
        - "cli_interactive": Local CLI with interactive TUI
        - "setup": Guided onboarding (if nothing available)

    Features:
        - Automatic mode detection and selection
        - Intelligent fallback (API → CLI → Setup)
        - Clear error messages with actionable next steps
        - Professional UX regardless of configuration
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Jules Facade."""
        self.api_key = api_key or os.getenv("JULES_API_KEY")
        self._api_adapter: Optional[Any] = None
        self._cli_adapter: Optional[Any] = None
        self._modes_cache: Optional[JulesModes] = None

    async def execute_prompt(
        self,
        project_path: Path,
        prompt: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Execute prompt with intelligent mode selection and fallback.

        Args:
            project_path: Path to project
            prompt: User prompt / task description
            context: Execution context with optional settings

        Returns:
            JSON string with execution result or setup guide
        """
        # Extract mode preference from context
        mode_preference = context.get("mode", "auto")

        # Detect available modes (with caching)
        if self._modes_cache is None:
            self._modes_cache = await self._detect_modes()

        modes = self._modes_cache

        # Select execution mode
        if mode_preference == "auto":
            # Intelligent selection: API > CLI > Setup
            selected_mode = modes.preferred_mode
        else:
            # Explicit mode requested - validate availability
            selected_mode = await self._validate_mode_available(mode_preference, modes)

        # Execute with selected mode
        if selected_mode == "api":
            return await self._execute_api(project_path, prompt, context)
        elif selected_mode == "cli_headless":
            return await self._execute_cli_headless(project_path, prompt, context)
        elif selected_mode == "cli_interactive":
            return await self._execute_cli_interactive(project_path, prompt, context)
        elif selected_mode == "setup":
            return self._generate_setup_guide(modes)
        else:
            raise ValueError(f"Unknown mode: {selected_mode}")

    async def _detect_modes(self) -> JulesModes:
        """
        Detect available Jules modes.

        Checks for:
            1. API mode: JULIUS_API_KEY + julius-agent-sdk installed
            2. CLI mode: julius command available + logged in

        Returns:
            JulesModes with availability info for each mode
        """
        api_mode = await self._check_api_mode()
        cli_mode = await self._check_cli_mode()

        # Determine preferred mode
        if api_mode.available:
            preferred_mode = "api"
        elif cli_mode.available:
            preferred_mode = "cli_headless"
        else:
            preferred_mode = "setup"

        return JulesModes(
            api=api_mode,
            cli=cli_mode,
            preferred_mode=preferred_mode,
        )

    async def _check_api_mode(self) -> ModeInfo:
        """Check if Jules API mode is available."""
        details: Dict[str, Any] = {}

        # Check 1: API key available
        has_api_key = bool(self.api_key)
        details["has_api_key"] = has_api_key

        # Check 2: julius-agent-sdk installed
        has_sdk = False
        try:
            import importlib.util

            sdk_spec = importlib.util.find_spec("julius_agent_sdk")
            has_sdk = sdk_spec is not None
            details["has_sdk"] = has_sdk

            if has_sdk:
                try:
                    import julius_agent_sdk

                    details["sdk_version"] = getattr(
                        julius_agent_sdk, "__version__", "unknown"
                    )
                except Exception:
                    details["sdk_version"] = None
        except Exception:
            has_sdk = False
            details["has_sdk"] = False

        # API mode available if both conditions met
        available = has_api_key and has_sdk

        if not available:
            reasons: List[str] = []
            if not has_api_key:
                reasons.append("JULIUS_API_KEY not set")
            if not has_sdk:
                reasons.append("julius-agent-sdk not installed")
            reason = ", ".join(reasons)
        else:
            reason = "API key and SDK available"

        return ModeInfo(available=available, reason=reason, details=details)

    async def _check_cli_mode(self) -> ModeInfo:
        """Check if Jules CLI mode is available."""
        details: Dict[str, Any] = {}

        # Check 1: julius CLI installed
        installed = False
        try:
            julius_path = shutil.which("julius")
            installed = julius_path is not None
            details["installed"] = installed
            details["path"] = julius_path
        except Exception:
            installed = False
            details["installed"] = False

        if not installed:
            return ModeInfo(
                available=False,
                reason="Jules CLI not installed",
                details=details,
            )

        # Check 2: Get version
        try:
            result = subprocess.run(
                ["julius", "version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                details["version"] = result.stdout.strip()
        except Exception:
            pass

        # Check 3: Logged in (can list sessions)
        logged_in = False
        try:
            result = subprocess.run(
                ["julius", "remote", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            logged_in = result.returncode == 0
            details["logged_in"] = logged_in
        except Exception:
            logged_in = False
            details["logged_in"] = False

        available = installed and logged_in

        if not available:
            reasons: List[str] = []
            if not installed:
                reasons.append("CLI not installed")
            if installed and not logged_in:
                reasons.append("not logged in (run: julius login)")
            reason = ", ".join(reasons)
        else:
            reason = "Jules CLI installed and logged in"

        return ModeInfo(available=available, reason=reason, details=details)

    async def _validate_mode_available(
        self, requested_mode: str, modes: JulesModes
    ) -> str:
        """
        Validate that requested mode is available.

        Returns:
            The mode name if available

        Raises:
            ValueError: If mode not available
        """
        if requested_mode == "api":
            if not modes.api.available:
                raise ValueError(
                    f"API mode requested but not available: {modes.api.reason}"
                )
            return "api"

        elif requested_mode in ("cli", "cli_headless"):
            if not modes.cli.available:
                raise ValueError(
                    f"CLI mode requested but not available: {modes.cli.reason}"
                )
            return "cli_headless"

        elif requested_mode == "cli_interactive":
            if not modes.cli.available:
                raise ValueError(
                    f"Interactive CLI mode requested but not available: {modes.cli.reason}"
                )
            return "cli_interactive"

        elif requested_mode == "setup":
            return "setup"

        else:
            raise ValueError(f"Unknown mode: {requested_mode}")

    async def _execute_api(
        self,
        project_path: Path,
        prompt: str,
        context: Dict[str, Any],
    ) -> str:
        """Execute using Jules API adapter."""
        try:
            if self._api_adapter is None:
                from .julius_async_adapter import JulesAsyncAdapter

                if not self.api_key:
                    raise ValueError("API key required for API mode")

                self._api_adapter = JulesAsyncAdapter(api_key=self.api_key)

            result = await self._api_adapter.execute_prompt(
                project_path=project_path,
                prompt=prompt,
                context=context,
            )

            # Convert result to JSON
            if hasattr(result, "__dict__"):
                # ExecutionResult dataclass
                result_dict = asdict(result)
            elif isinstance(result, str):
                result_dict = json.loads(result)
            else:
                result_dict = result

            return json.dumps(
                {
                    "success": True,
                    "mode": "api",
                    "data": result_dict,
                }
            )

        except Exception as e:
            return json.dumps(
                {
                    "success": False,
                    "mode": "api",
                    "error": str(e),
                    "message": "Jules API execution failed",
                }
            )

    async def _execute_cli_headless(
        self,
        project_path: Path,
        prompt: str,
        context: Dict[str, Any],
    ) -> str:
        """Execute using Jules CLI adapter (headless/background)."""
        try:
            if self._cli_adapter is None:
                from .julius_cli_adapter import JulesCLIAdapter

                self._cli_adapter = JulesCLIAdapter()

            result = await self._cli_adapter.execute_prompt(
                project_path=project_path,
                prompt=prompt,
                context={**context, "cli_mode": "headless"},
            )

            # Result is already JSON string from CLI adapter
            result_dict = json.loads(result)
            result_dict["mode"] = "cli_headless"
            result_dict["fallback_reason"] = "Jules API unavailable"

            return json.dumps(result_dict)

        except Exception as e:
            return json.dumps(
                {
                    "success": False,
                    "mode": "cli_headless",
                    "error": str(e),
                    "message": "Jules CLI execution failed",
                }
            )

    async def _execute_cli_interactive(
        self,
        project_path: Path,
        prompt: str,
        context: Dict[str, Any],
    ) -> str:
        """Execute using Jules CLI adapter (interactive TUI)."""
        try:
            if self._cli_adapter is None:
                from .julius_cli_adapter import JulesCLIAdapter

                self._cli_adapter = JulesCLIAdapter()

            result = await self._cli_adapter.execute_prompt(
                project_path=project_path,
                prompt=prompt,
                context={**context, "cli_mode": "interactive"},
            )

            # Result is already JSON string from CLI adapter
            result_dict = json.loads(result)
            result_dict["mode"] = "cli_interactive"

            return json.dumps(result_dict)

        except Exception as e:
            return json.dumps(
                {
                    "success": False,
                    "mode": "cli_interactive",
                    "error": str(e),
                    "message": "Jules interactive CLI failed",
                }
            )

    def _generate_setup_guide(self, modes: JulesModes) -> str:
        """Generate helpful setup guide when nothing is available."""
        guide: Dict[str, Any] = {
            "status": "setup_required",
            "message": "Jules is not fully configured. Choose a setup option below.",
            "options": [],
        }

        # Option 1: CLI Mode (easier, recommended first)
        if not modes.cli.available:
            cli_steps: List[Dict[str, Any]] = []

            # Check what's missing
            if not modes.cli.details.get("installed"):
                cli_steps.append(
                    {
                        "step": 1,
                        "action": "Install Jules CLI",
                        "instructions": [
                            "Download from: https://julius.google/",
                            "Or use package manager:",
                            "  macOS: brew install julius",
                            "  Linux: See https://julius.google/docs/cli",
                            "  Windows: Download installer from https://julius.google/",
                        ],
                    }
                )

            if modes.cli.details.get("installed") and not modes.cli.details.get(
                "logged_in"
            ):
                cli_steps.append(
                    {
                        "step": 2,
                        "action": "Login to Jules",
                        "command": "julius login",
                        "instructions": [
                            "1. Run: julius login",
                            "2. Follow browser authentication flow",
                            "3. Verify with: julius remote list",
                        ],
                    }
                )

            cli_option: Dict[str, Any] = {
                "mode": "cli",
                "title": "⚡ Jules CLI Mode (Quick Start - Recommended)",
                "description": "Local execution with interactive terminal UI",
                "pros": [
                    "✅ No API key required",
                    "✅ Easy setup (just login)",
                    "✅ Fast feedback",
                    "✅ Works offline",
                ],
                "cons": [
                    "❌ Blocks during execution",
                    "❌ Less context than API",
                ],
                "setup_steps": cli_steps,
            }
            guide["options"].append(cli_option)

        # Option 2: API Mode (full features)
        if not modes.api.available:
            api_steps: List[Dict[str, Any]] = []

            if not modes.api.details.get("has_sdk"):
                api_steps.append(
                    {
                        "step": 1,
                        "action": "Install julius-agent-sdk",
                        "command": "pip install julius-agent-sdk",
                    }
                )

            if not modes.api.details.get("has_api_key"):
                api_steps.append(
                    {
                        "step": 2,
                        "action": "Get API key",
                        "url": "https://julius.google/",
                        "instructions": [
                            "1. Go to https://julius.google/",
                            "2. Sign in with Google account",
                            "3. Navigate to: Settings → API Keys",
                            "4. Create new API key",
                            "5. Copy the key",
                        ],
                    }
                )

                api_steps.append(
                    {
                        "step": 3,
                        "action": "Add API key to .env",
                        "command": 'echo "JULIUS_API_KEY=your-key-here" >> .env',
                        "file": ".env",
                        "content": "JULIUS_API_KEY=your-actual-key-here",
                        "instructions": [
                            "Create or edit .env file in project root",
                            "Add: JULIUS_API_KEY=<your-key-from-step-2>",
                            "Save and restart your IDE/terminal",
                        ],
                    }
                )

            api_option: Dict[str, Any] = {
                "mode": "api",
                "title": "🚀 Jules API Mode (Full Features)",
                "description": "Async agent with web monitoring and unlimited context",
                "pros": [
                    "✅ Full async execution",
                    "✅ 100k+ lines context",
                    "✅ Web monitoring dashboard",
                    "✅ Plan approval workflow",
                ],
                "cons": [
                    "❌ Requires API key setup",
                    "❌ Repo must be on julius.google",
                ],
                "setup_steps": api_steps,
            }
            guide["options"].append(api_option)

        # Recommendation
        if not modes.cli.available and modes.cli.details.get("installed"):
            guide["recommendation"] = "cli"
            guide["recommendation_reason"] = (
                "Just need to login (julius login), then ready to go!"
            )
        elif not modes.api.available and not modes.cli.available:
            guide["recommendation"] = "cli"
            guide["recommendation_reason"] = (
                "Easier setup (no API key needed). Can upgrade to API later."
            )
        else:
            guide["recommendation"] = None

        return json.dumps(guide, indent=2)
