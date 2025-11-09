"""
Jules CLI Adapter - ICodeExecutor implementation for Jules CLI execution.

Provides local execution via the jules command-line tool.
Supports both headless (background) and interactive (TUI) modes.

Headless Mode:
    - Creates session: `julius new "prompt"`
    - Polls for completion
    - Pulls results: `julius remote pull --session ID`
    - Returns results JSON

Interactive Mode:
    - Launches interactive TUI: `julius new "prompt"`
    - User completes task in terminal
    - Returns success confirmation

Example:
    >>> from pathlib import Path
    >>> from cde_orchestrator.adapters.agents import JulesCLIAdapter
    >>>
    >>> adapter = JulesCLIAdapter()
    >>> result = await adapter.execute_prompt(
    ...     project_path=Path("."),
    ...     prompt="Fix the login bug",
    ...     context={"cli_mode": "headless", "timeout": 1800}
    ... )
    >>> print(result)  # JSON with status, session_id, results
"""

import asyncio
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Dict

from ...domain.ports import ICodeExecutor


class JulesCLIError(Exception):
    """Raised when Jules CLI execution fails."""

    pass


class JulesCLIAdapter(ICodeExecutor):
    """
    Jules CLI adapter for local execution.

    Features:
        - Headless mode: Background execution with polling
        - Interactive mode: Terminal UI for user control
        - Session management: Track and retrieve sessions
        - Result parsing: Extract modified files and metadata

    Limitations:
        - Blocking during execution (no async queueing)
        - Limited context compared to API mode
        - Requires local machine setup

    Modes:
        headless: Run in background, poll for completion
        interactive: Launch TUI, wait for user completion
    """

    POLL_INTERVAL = 10  # seconds
    MAX_RETRIES = 3

    async def execute_prompt(
        self,
        project_path: Path,
        prompt: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Execute task via Jules CLI.

        Args:
            project_path: Path to project directory
            prompt: Task description
            context: Execution context with optional settings:
                - cli_mode: "headless" (default) or "interactive"
                - timeout: Max execution time (default: 1800s)
                - poll_interval: Poll status every N seconds

        Returns:
            JSON string with execution result

        Raises:
            JulesCLIError: If execution fails
        """
        cli_mode = context.get("cli_mode", "headless")
        timeout = context.get("timeout", 1800)
        poll_interval = context.get("poll_interval", self.POLL_INTERVAL)

        try:
            project_path = Path(project_path).resolve()

            # Validate project is a git repo
            if not (project_path / ".git").exists():
                raise JulesCLIError(
                    f"Project {project_path} is not a Git repository. "
                    "Jules CLI requires a Git repo to track changes."
                )

            if cli_mode == "interactive":
                return await self._execute_interactive(project_path, prompt)
            else:
                return await self._execute_headless(
                    project_path, prompt, timeout, poll_interval
                )

        except JulesCLIError as e:
            return json.dumps(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Jules CLI execution failed",
                }
            )
        except Exception as e:
            return json.dumps(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Unexpected error during Jules CLI execution",
                }
            )

    async def _execute_interactive(self, project_path: Path, prompt: str) -> str:
        """
        Execute in interactive mode (TUI).

        Launches `julius new "prompt"` without capturing output.
        User interacts with Jules in terminal.
        When user exits, consider task complete.

        Args:
            project_path: Project directory
            prompt: Task description

        Returns:
            JSON with success/completion info
        """
        try:
            # Launch interactive session
            result = subprocess.run(
                ["julius", "new", prompt],
                cwd=project_path,
                # No capture_output - let TUI display and accept input
                timeout=7200,  # 2 hours for interactive mode
            )

            if result.returncode == 0:
                return json.dumps(
                    {
                        "success": True,
                        "mode": "interactive",
                        "message": "✅ Jules interactive session completed",
                        "next_steps": [
                            "Review changes: git diff",
                            "Test your changes",
                            "Commit when ready: git commit -am 'feat: <description>'",
                        ],
                    }
                )
            else:
                raise JulesCLIError(
                    "Interactive session failed or was cancelled by user"
                )

        except subprocess.TimeoutExpired:
            raise JulesCLIError("Interactive session timed out (2 hours)")
        except Exception as e:
            raise JulesCLIError(f"Interactive session error: {str(e)}")

    async def _execute_headless(
        self,
        project_path: Path,
        prompt: str,
        timeout: int,
        poll_interval: int,
    ) -> str:
        """
        Execute in headless mode (background with polling).

        1. Create session: `julius new "prompt"`
        2. Poll status: Check session status every N seconds
        3. Pull results: `julius remote pull --session ID`
        4. Parse and return results

        Args:
            project_path: Project directory
            prompt: Task description
            timeout: Max execution time in seconds
            poll_interval: Poll interval in seconds

        Returns:
            JSON with session info and results
        """
        # Step 1: Create session
        session_id = await self._create_session(project_path, prompt)

        # Step 2: Poll for completion
        await self._wait_for_completion(session_id, timeout, poll_interval)

        # Step 3: Pull results
        modified_files = await self._pull_results(project_path, session_id)

        # Step 4: Return results
        return json.dumps(
            {
                "success": True,
                "mode": "headless",
                "session_id": session_id,
                "message": f"✅ Task completed via Jules CLI (session {session_id})",
                "modified_files": modified_files,
                "next_steps": [
                    "Review changes: git diff HEAD~1",
                    "Test your changes",
                    "Commit when ready: git commit -am 'feat: <description>'",
                ],
            }
        )

    async def _create_session(self, project_path: Path, prompt: str) -> str:
        """
        Create a new Jules session.

        Runs: `julius new "prompt"`

        Returns:
            Session ID extracted from output
        """
        try:
            result = subprocess.run(
                ["julius", "new", prompt],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                raise JulesCLIError(f"Failed to create session. Error: {result.stderr}")

            # Parse session ID from output
            # Expected format: "Session created: 123456" or similar
            session_id = self._extract_session_id(result.stdout)

            if not session_id:
                raise JulesCLIError(
                    f"Could not parse session ID from output: {result.stdout}"
                )

            return session_id

        except subprocess.TimeoutExpired:
            raise JulesCLIError("Session creation timed out")
        except Exception as e:
            raise JulesCLIError(f"Session creation failed: {str(e)}")

    async def _wait_for_completion(
        self, session_id: str, timeout: int, poll_interval: int
    ) -> None:
        """
        Poll for session completion.

        Runs: `julius remote list --session ID`
        Until status is COMPLETED or FAILED

        Args:
            session_id: Jules session ID
            timeout: Max wait time in seconds
            poll_interval: Poll interval in seconds

        Raises:
            JulesCLIError: If session fails or times out
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(
                    ["julius", "remote", "list", "--session", session_id],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    # Parse status from output
                    status = self._extract_status(result.stdout)

                    if status == "COMPLETED":
                        return  # Success!

                    elif status == "FAILED":
                        raise JulesCLIError(f"Session {session_id} failed")

                    elif status == "RUNNING":
                        # Still running, wait and poll again
                        await asyncio.sleep(poll_interval)
                        continue

                    else:
                        # Unknown status, keep polling
                        await asyncio.sleep(poll_interval)
                        continue

                else:
                    # Command failed, retry
                    await asyncio.sleep(poll_interval)

            except subprocess.TimeoutExpired:
                # Polling command timed out, retry
                await asyncio.sleep(poll_interval)
                continue
            except JulesCLIError:
                # Session failed
                raise
            except Exception:
                # Other error, retry
                await asyncio.sleep(poll_interval)
                continue

        # Timeout exceeded
        raise JulesCLIError(
            f"Session {session_id} did not complete within {timeout} seconds"
        )

    async def _pull_results(self, project_path: Path, session_id: str) -> list:
        """
        Pull results from completed session.

        Runs: `julius remote pull --session ID [--apply]`

        Returns:
            List of modified files
        """
        try:
            result = subprocess.run(
                [
                    "julius",
                    "remote",
                    "pull",
                    "--session",
                    session_id,
                ],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                raise JulesCLIError(f"Failed to pull results: {result.stderr}")

            # Parse modified files from git
            # Simple approach: run git diff --name-only
            git_result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if git_result.returncode == 0:
                modified_files = [
                    f.strip()
                    for f in git_result.stdout.strip().split("\n")
                    if f.strip()
                ]
            else:
                modified_files = []

            return modified_files

        except subprocess.TimeoutExpired:
            raise JulesCLIError("Pulling results timed out")
        except Exception as e:
            raise JulesCLIError(f"Failed to pull results: {str(e)}")

    @staticmethod
    def _extract_session_id(output: str) -> str:
        """Extract session ID from julius command output."""
        # Try different patterns
        patterns = [
            r"Session\s+(?:ID|created):\s*(\w+)",  # Session ID: 123456
            r"session[_\s]+id:\s*(\w+)",  # session_id: 123456
            r"\b([0-9a-f]{6,})\b",  # 6+ hex digits
        ]

        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)

        # Fallback: return last word that looks like an ID
        words = output.strip().split()
        if words:
            return words[-1]

        return ""

    @staticmethod
    def _extract_status(output: str) -> str:
        """Extract session status from julius command output."""
        # Look for status field
        for line in output.split("\n"):
            if "status" in line.lower():
                # Extract status value
                if ":" in line:
                    status = line.split(":", 1)[1].strip()
                    return status.upper()

        # Fallback: look for status keywords
        output_upper = output.upper()
        for status in ["COMPLETED", "FAILED", "RUNNING", "PENDING"]:
            if status in output_upper:
                return status

        return "UNKNOWN"
