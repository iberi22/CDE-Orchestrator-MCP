"""
Jules Async Adapter - ICodeExecutor implementation for Jules AI agent.

Uses jules-agent-sdk-python for async task delegation to Jules.
Supports long-running tasks, plan approval, and full repository context.

Example:
    >>> import os
    >>> from pathlib import Path
    >>> from cde_orchestrator.adapters.agents import JulesAsyncAdapter
    >>>
    >>> adapter = JulesAsyncAdapter(api_key=os.getenv("JULES_API_KEY"))
    >>> result = await adapter.execute_prompt(
    ...     project_path=Path("."),
    ...     prompt="Add comprehensive error handling to the API module",
    ...     context={"branch": "main", "require_plan_approval": False}
    ... )
    >>> print(f"Session: {result.session_id}")
    >>> print(f"State: {result.state}")
    >>> print(f"Files modified: {result.modified_files}")
"""

import asyncio
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from jules_agent_sdk import AsyncJulesClient
    from jules_agent_sdk.models import Activity, Session, SessionState

    JULES_AVAILABLE = True
except ImportError:
    JULES_AVAILABLE = False
    AsyncJulesClient = None
    SessionState = None
    Session = None
    Activity = None

from ...domain.exceptions import DomainError
from ...domain.ports import ICodeExecutor


class JulesError(DomainError):
    """Base exception for Jules adapter errors."""

    pass


class JulesNotInstalledError(JulesError):
    """Raised when jules-agent-sdk is not installed."""

    pass


class JulesSourceNotFoundError(JulesError):
    """Raised when project source is not found in Jules."""

    pass


class JulesExecutionError(JulesError):
    """Raised when Jules session fails."""

    pass


@dataclass
class ExecutionResult:
    """
    Result of Jules code execution.

    Attributes:
        success: Whether execution completed successfully
        session_id: Jules session ID
        state: Session state (COMPLETED, FAILED, etc.)
        modified_files: List of files modified by Jules
        activities: List of session activities
        log: Human-readable activity log
        metadata: Additional session metadata (URL, prompt, etc.)
    """

    success: bool
    session_id: str
    state: str
    modified_files: List[str]
    activities: List[Dict[str, Any]]
    log: str
    metadata: Dict[str, Any]


class JulesAsyncAdapter(ICodeExecutor):
    """
    Jules async agent adapter.

    Implements ICodeExecutor port using Jules API for long-running,
    complex coding tasks with full repository context.

    Features:
        - Full repository context (100,000+ lines)
        - Long-running task support (30+ minutes)
        - Plan approval workflow
        - Activity monitoring
        - Automatic source resolution
        - Session persistence

    Requirements:
        - JULES_API_KEY environment variable
        - jules-agent-sdk installed: pip install jules-agent-sdk
        - Repository connected to Jules at https://jules.google/

    Example:
        >>> adapter = JulesAsyncAdapter(
        ...     api_key=os.getenv("JULES_API_KEY"),
        ...     require_plan_approval=True
        ... )
        >>> result = await adapter.execute_prompt(
        ...     project_path=Path("/path/to/project"),
        ...     prompt="Refactor authentication module to use OAuth2",
        ...     context={"branch": "develop", "timeout": 3600}
        ... )
    """

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        default_timeout: int = 1800,  # 30 minutes
        require_plan_approval: bool = False,
    ):
        """
        Initialize Jules adapter.

        Args:
            api_key: Jules API key (get from https://jules.google/)
            base_url: Optional custom API endpoint (for testing)
            default_timeout: Default timeout for wait_for_completion (seconds)
            require_plan_approval: Whether to require manual plan approval

        Raises:
            JulesNotInstalledError: If jules-agent-sdk is not installed
        """
        if not JULES_AVAILABLE:
            raise JulesNotInstalledError(
                "jules-agent-sdk not installed. Install with: pip install jules-agent-sdk"
            )

        self.api_key = api_key
        self.base_url = base_url
        self.default_timeout = default_timeout
        self.require_plan_approval = require_plan_approval
        self._client: Optional[AsyncJulesClient] = None

    async def _get_client(self) -> AsyncJulesClient:
        """Get or create Jules client (lazy initialization)."""
        if self._client is None:
            self._client = AsyncJulesClient(
                api_key=self.api_key, base_url=self.base_url
            )
        return self._client

    async def execute_prompt(
        self, project_path: Path, prompt: str, context: Dict[str, Any]
    ) -> str:
        """
        Execute code generation with Jules.

        Workflow:
            1. Resolve project to Jules source
            2. Create Jules session
            3. Optionally approve plan
            4. Wait for completion (or return async if detached)
            5. Collect activities and results

        Args:
            project_path: Absolute path to project
            prompt: Task description
            context: Additional context:
                - branch: Starting branch (default: main)
                - timeout: Override default timeout (seconds)
                - detached: Don't wait for completion (default: False)
                - require_plan_approval: Override default

        Returns:
            JSON string with ExecutionResult

        Raises:
            JulesSourceNotFoundError: If project not found in Jules
            JulesExecutionError: If Jules session fails
        """
        import json

        client = await self._get_client()

        try:
            # 1. Resolve source
            source_id = await self._resolve_source(client, project_path)

            # 2. Extract context
            branch = context.get("branch", "main")
            timeout = context.get("timeout", self.default_timeout)
            detached = context.get("detached", False)
            require_approval = context.get(
                "require_plan_approval", self.require_plan_approval
            )

            # 3. Create session
            session = await client.sessions.create(
                prompt=prompt,
                source=source_id,
                starting_branch=branch,
                require_plan_approval=require_approval,
            )

            # 4. Handle plan approval if required
            if require_approval:
                session = await self._handle_plan_approval(client, session.id)

            # 5. Wait for completion (unless detached)
            if not detached:
                session = await client.sessions.wait_for_completion(
                    session.id, poll_interval=5, timeout=timeout
                )

            # 6. Collect activities
            activities = await client.activities.list_all(session.id)

            # 7. Extract modified files (from activities)
            modified_files = self._extract_modified_files(activities)

            result = ExecutionResult(
                success=(session.state == SessionState.COMPLETED),
                session_id=session.id,
                state=session.state.value,
                modified_files=modified_files,
                activities=[self._activity_to_dict(a) for a in activities],
                log=self._format_activities_log(activities),
                metadata={
                    "session_url": session.url,
                    "prompt": prompt,
                    "source": source_id,
                    "branch": branch,
                },
            )

            return json.dumps(
                {
                    "success": result.success,
                    "session_id": result.session_id,
                    "state": result.state,
                    "modified_files": result.modified_files,
                    "activities_count": len(result.activities),
                    "log": result.log,
                    "metadata": result.metadata,
                },
                indent=2,
            )

        except Exception as e:
            raise JulesExecutionError(f"Jules execution failed: {str(e)}") from e

    async def _resolve_source(
        self, client: AsyncJulesClient, project_path: Path
    ) -> str:
        """
        Resolve project path to Jules source ID.

        Logic:
            1. Check if project has .jules/source_id file (cached)
            2. Search Jules sources by GitHub repo URL
            3. Fallback: Search by project name

        Returns:
            Jules source ID (e.g., "sources/abc123")

        Raises:
            JulesSourceNotFoundError: If source not found
        """
        # Check cache
        cache_file = project_path / ".jules" / "source_id"
        if cache_file.exists():
            return cache_file.read_text().strip()

        # Get project Git remote
        git_remote = self._get_git_remote(project_path)

        # Search Jules sources
        sources = await client.sources.list_all()

        # Match by GitHub repo URL
        if git_remote:
            for source in sources:
                if source.github_repo:
                    repo_url = f"{source.github_repo.owner}/{source.github_repo.repo}"
                    if git_remote.endswith(repo_url):
                        # Cache for future
                        cache_file.parent.mkdir(exist_ok=True)
                        cache_file.write_text(source.name)
                        return source.name

        # Match by project name
        project_name = project_path.name
        for source in sources:
            if source.github_repo and source.github_repo.repo == project_name:
                cache_file.parent.mkdir(exist_ok=True)
                cache_file.write_text(source.name)
                return source.name

        raise JulesSourceNotFoundError(
            f"No Jules source found for project: {project_path}. "
            f"Connect the repository at https://jules.google/"
        )

    def _get_git_remote(self, project_path: Path) -> Optional[str]:
        """
        Extract Git remote URL from project.

        Returns:
            Git remote URL or None if not a Git repo
        """
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    async def _handle_plan_approval(
        self, client: AsyncJulesClient, session_id: str
    ) -> Session:
        """
        Wait for plan generation and approve.

        Current implementation: Auto-approve after plan is generated.
        Future enhancement: Interactive approval in MCP UI.

        Args:
            client: Jules client
            session_id: Session ID to monitor

        Returns:
            Updated session after plan approval
        """
        # Wait for plan to be generated
        while True:
            session = await client.sessions.get(session_id)

            if session.state == SessionState.AWAITING_PLAN_APPROVAL:
                # Auto-approve (for now)
                await client.sessions.approve_plan(session_id)
                return session

            if session.state in [SessionState.FAILED, SessionState.COMPLETED]:
                return session

            await asyncio.sleep(2)

    def _extract_modified_files(self, activities: List[Activity]) -> List[str]:
        """
        Extract list of modified files from activities.

        Args:
            activities: List of Jules session activities

        Returns:
            Unique list of modified file paths
        """
        files = []
        for activity in activities:
            if activity.code_change_made:
                change = activity.code_change_made
                if "files" in change:
                    files.extend(change["files"])
        return list(set(files))

    def _activity_to_dict(self, activity: Activity) -> Dict[str, Any]:
        """
        Convert Activity model to dict for JSON serialization.

        Args:
            activity: Jules Activity object

        Returns:
            Dictionary representation
        """
        return {
            "id": activity.id,
            "description": activity.description,
            "originator": activity.originator,
            "create_time": str(activity.create_time),
            "agent_messaged": activity.agent_messaged,
            "code_change_made": activity.code_change_made,
            "plan_generated": activity.plan_generated,
        }

    def _format_activities_log(self, activities: List[Activity]) -> str:
        """
        Format activities into human-readable log.

        Args:
            activities: List of Jules session activities

        Returns:
            Formatted multi-line log string
        """
        lines = ["Jules Session Activity Log:", "=" * 50]
        for i, activity in enumerate(activities, 1):
            lines.append(f"\n{i}. {activity.description}")
            lines.append(f"   Time: {activity.create_time}")
            lines.append(f"   Originator: {activity.originator}")

            if activity.agent_messaged:
                msg = activity.agent_messaged.get("agentMessage", "")
                if msg:
                    lines.append(f"   Message: {msg[:100]}...")

            if activity.code_change_made:
                change = activity.code_change_made
                if "files" in change:
                    lines.append(f"   Files changed: {', '.join(change['files'][:5])}")

        return "\n".join(lines)

    async def close(self):
        """Close Jules client connection."""
        if self._client:
            await self._client.close()
            self._client = None
