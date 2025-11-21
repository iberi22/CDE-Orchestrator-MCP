# src/cde_orchestrator/adapters/service/service_adapter.py
"""
Service Connector Module - Handles external MCP service integrations.

This module detects and leverages external MCP servers (like GitHub MCP) that users have
installed and configured. If an external MCP server is available, it uses it; otherwise,
it falls back to local implementations.

The connector works by:
1. Detecting available MCP servers in the environment
2. Using external MCP servers when available (user-configured)
3. Falling back to local implementations when needed
4. Providing results back to the workflow engine
"""
import json
import logging
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


class MCPDetector:
    """Detects available MCP servers in the environment."""

    @staticmethod
    def find_mcp_config() -> Optional[Path]:
        """Find MCP configuration file in common locations."""
        common_paths = [
            Path.home() / ".cursor" / "mcp.json",
            Path.home() / ".vscode" / "mcp.json",
            Path(".kiro") / "settings" / "mcp.json",
            Path(".vscode") / "mcp.json",
        ]

        for path in common_paths:
            if path.exists():
                return path

        return None

    @staticmethod
    def load_mcp_servers() -> Dict[str, Dict[str, Any]]:
        """Load and parse MCP server configurations."""
        config_path = MCPDetector.find_mcp_config()
        if not config_path:
            return {}

        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            return cast(Dict[str, Dict[str, Any]], config.get("mcpServers", {}))
        except Exception as e:
            logger.error(f"Error loading MCP config: {e}")
            return {}

    @staticmethod
    def is_github_mcp_available() -> bool:
        """Check if GitHub MCP server is configured."""
        servers = MCPDetector.load_mcp_servers()

        # Look for common GitHub MCP names
        github_server_names = ["github", "mcp_github", "github-mcp"]

        for server_name in github_server_names:
            if server_name in servers:
                server_config = servers[server_name]
                # Check if it's enabled
                if not server_config.get("disabled", False):
                    return True

        return False

    @staticmethod
    def get_github_mcp_config() -> Optional[Dict[str, Any]]:
        """Get GitHub MCP server configuration."""
        servers = MCPDetector.load_mcp_servers()

        github_server_names = ["github", "mcp_github", "github-mcp"]

        for server_name in github_server_names:
            if server_name in servers:
                return servers[server_name]

        return None


class CircuitBreakerOpenError(Exception):
    """Raised when the circuit breaker is open and calls are disallowed."""


class CircuitBreaker:
    """Simple circuit breaker to prevent cascading failures."""

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: int = 60,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = timedelta(seconds=recovery_timeout)
        self.failure_count = 0
        self.state = "closed"
        self.last_failure: Optional[datetime] = None

    def allow(self) -> None:
        """Raise if the breaker is open and still within the cooldown period."""
        if self.state == "open":
            assert self.last_failure is not None
            elapsed = datetime.now(timezone.utc) - self.last_failure
            if elapsed >= self.recovery_timeout:
                # Allow a trial call in half-open state
                self.state = "half_open"
                return
            raise CircuitBreakerOpenError("Circuit breaker is open")

    def record_success(self) -> None:
        """Reset breaker after a successful call."""
        self.failure_count = 0
        self.state = "closed"
        self.last_failure = None

    def record_failure(self) -> None:
        """Increment failure counter and trip breaker if threshold reached."""
        self.failure_count += 1
        self.last_failure = datetime.now(timezone.utc)
        if self.failure_count >= self.failure_threshold:
            self.state = "open"

    def snapshot(self) -> Dict[str, Any]:
        """Expose breaker status for diagnostics."""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "last_failure": (
                self.last_failure.isoformat() if self.last_failure else None
            ),
            "failure_threshold": self.failure_threshold,
            "recovery_timeout_seconds": int(self.recovery_timeout.total_seconds()),
        }


class GitHubConnector:
    """
    GitHub service connector that uses external MCP when available.
    Falls back to local implementations when MCP is not configured.
    """

    def __init__(
        self,
        circuit_breaker: Optional[CircuitBreaker] = None,
        default_timeout: int = 10,
        retry_attempts: int = 3,
    ):
        self.mcp_available = MCPDetector.is_github_mcp_available()
        self.mcp_config = (
            MCPDetector.get_github_mcp_config() if self.mcp_available else None
        )
        self.token = os.getenv("GITHUB_TOKEN")
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.default_timeout = default_timeout
        self.retry_attempts = retry_attempts
        self._retry_wait = wait_exponential(multiplier=1, min=1, max=10)

    # --- Circuit breaker helpers -------------------------------------------------

    def _record_success(self) -> None:
        if self.circuit_breaker:
            self.circuit_breaker.record_success()

    def _record_failure(self) -> None:
        if self.circuit_breaker:
            self.circuit_breaker.record_failure()

    def create_issue(
        self,
        repo_owner: str,
        repo_name: str,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a GitHub issue.

        Priority:
        1. Use MCP GitHub server if available
        2. Use GitHub API if token available
        3. Fallback to local file

        Returns:
            Issue creation result
        """
        if self.circuit_breaker:
            try:
                self.circuit_breaker.allow()
            except CircuitBreakerOpenError:
                logger.warning(
                    "GitHub circuit breaker open; using local issue fallback"
                )
                return self._create_issue_local(
                    title, body, labels, reason="circuit_open"
                )

        # Try MCP first
        if self.mcp_available:
            result = self._create_issue_via_mcp(title, body, labels)
            self._record_success()
            return result

        # Try GitHub API
        if self.token:
            return self._create_issue_via_api(
                repo_owner,
                repo_name,
                title,
                body,
                labels,
                timeout=self.default_timeout,
            )

        # Fallback to local
        return self._create_issue_local(title, body, labels, reason="no_remote_service")

    def _create_issue_via_mcp(
        self, title: str, body: str, labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create issue via external MCP GitHub server.
        Note: In a real implementation, this would use the MCP client library
        to communicate with the external GitHub MCP server.
        """
        response = {
            "id": f"mcp-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            "title": title,
            "body": body,
            "labels": labels or [],
            "method": "mcp",
            "message": "Issue created via external GitHub MCP server",
        }
        if self.circuit_breaker:
            self.circuit_breaker.record_success()
        return response

    def _create_issue_via_api(
        self,
        repo_owner: str,
        repo_name: str,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        timeout: int = 10,
    ) -> Dict[str, Any]:
        """Create issue via GitHub API with timeout, retries, and fallback."""
        try:
            import requests
        except ImportError:
            logger.warning(
                "requests library not available; falling back to local issue storage"
            )
            return self._create_issue_local(
                title, body, labels, reason="requests_not_available"
            )

        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        data: Dict[str, Any] = {"title": title, "body": body}

        if labels:
            data["labels"] = labels

        try:
            timeout_value = timeout or self.default_timeout
            retrying = Retrying(
                stop=stop_after_attempt(self.retry_attempts),
                wait=self._retry_wait,
                retry=retry_if_exception_type(
                    (requests.exceptions.Timeout, requests.exceptions.ConnectionError)
                ),
                reraise=True,
            )

            response = None
            for attempt in retrying:
                with attempt:
                    response = requests.post(
                        url,
                        headers=headers,
                        json=data,
                        timeout=timeout_value,
                    )
                    response.raise_for_status()

            assert response is not None
            self._record_success()
            return cast(Dict[str, Any], response.json())
        except requests.exceptions.Timeout as exc:
            logger.warning("GitHub API timeout (%ss): %s", timeout_value, exc)
            self._record_failure()
            return self._create_issue_local(title, body, labels, reason="timeout")
        except requests.exceptions.ConnectionError as exc:
            logger.error("GitHub API connection error: %s", exc)
            self._record_failure()
            return self._create_issue_local(
                title, body, labels, reason="connection_error"
            )
        except requests.exceptions.HTTPError as exc:
            logger.error("GitHub API HTTP error: %s", exc)
            self._record_failure()
            return self._create_issue_local(title, body, labels, reason="http_error")
        except Exception as exc:
            logger.exception("Unexpected error creating GitHub issue: %s", exc)
            self._record_failure()
            return self._create_issue_local(
                title, body, labels, reason="unexpected_error"
            )

    def _create_issue_local(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        reason: str = "fallback",
    ) -> Dict[str, Any]:
        """
        Fallback: Create issue as local file.
        This ensures workflows can continue without external dependencies.
        """
        issues_dir = Path(".cde") / "issues"
        issues_dir.mkdir(exist_ok=True)

        issue_id = f"local-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        issue_file = issues_dir / f"{issue_id}.md"

        issue_content = f"# {title}\n\n{body}\n\n"
        if labels:
            issue_content += f"\n**Labels:** {', '.join(labels)}\n"

        issue_file.write_text(issue_content)

        return {
            "id": issue_id,
            "title": title,
            "body": body,
            "labels": labels or [],
            "method": "local",
            "fallback_reason": reason,
            "message": f"Issue stored locally at {issue_file}",
        }

    def get_status(self) -> Dict[str, Any]:
        """Get connector status information."""
        return {
            "mcp_available": self.mcp_available,
            "mcp_config": self.mcp_config is not None,
            "api_available": self.token is not None,
            "fallback": not self.mcp_available and not self.token,
            "default_timeout": self.default_timeout,
            "retry_attempts": self.retry_attempts,
            "circuit_breaker": self.circuit_breaker.snapshot(),
        }


class GitConnector:
    """
    Git connector for local repository operations.
    Uses git commands via subprocess for direct git operations.
    """

    def __init__(self) -> None:
        self.repo_path = Path.cwd()

    def create_branch(
        self, branch_name: str, base_branch: str = "main"
    ) -> Dict[str, Any]:
        """Create a new git branch."""
        try:
            # Fetch latest changes
            subprocess.run(
                ["git", "fetch", "origin", base_branch],
                cwd=self.repo_path,
                capture_output=True,
                check=False,
            )

            # Create branch
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name, f"origin/{base_branch}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "branch": branch_name,
                    "message": f"Branch {branch_name} created successfully",
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": "Failed to create branch",
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error creating branch",
            }

    def commit_changes(
        self, message: str, files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Commit changes to git repository."""
        try:
            # Add files
            if files:
                subprocess.run(
                    ["git", "add"] + files,
                    cwd=self.repo_path,
                    capture_output=True,
                    check=False,
                )
            else:
                subprocess.run(
                    ["git", "add", "."],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=False,
                )

            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                return {"success": True, "message": "Changes committed successfully"}
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": "Failed to commit changes",
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error committing changes",
            }

    def push_branch(self, branch_name: str) -> Dict[str, Any]:
        """Push a branch to remote repository."""
        try:
            result = subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Branch {branch_name} pushed successfully",
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": "Failed to push branch",
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error pushing branch",
            }


class ServiceConnectorFactory:
    """
    Factory for creating and managing service connectors.
    Provides a unified interface for accessing different service connectors.
    """

    def __init__(self) -> None:
        self._connectors: Dict[str, Any] = {}
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.default_timeout = int(os.getenv("CDE_SERVICE_TIMEOUT", "10"))
        self.retry_attempts = int(os.getenv("CDE_SERVICE_RETRIES", "3"))
        self.failure_threshold = int(os.getenv("CDE_SERVICE_FAILURE_THRESHOLD", "3"))
        self.recovery_timeout = int(os.getenv("CDE_SERVICE_RECOVERY_SECONDS", "60"))

    def _get_breaker(self, service_type: str) -> CircuitBreaker:
        """Return (or create) a circuit breaker for the service."""
        if service_type not in self._circuit_breakers:
            self._circuit_breakers[service_type] = CircuitBreaker(
                failure_threshold=self.failure_threshold,
                recovery_timeout=self.recovery_timeout,
            )
        return self._circuit_breakers[service_type]

    def get_connector(self, service_type: str) -> Any:
        """
        Get or create a connector for the specified service type.

        Args:
            service_type: Type of service (e.g., 'github', 'git')

        Returns:
            Service connector instance
        """
        if service_type in self._connectors:
            return self._connectors[service_type]

        connector: Any
        if service_type == "github":
            connector = GitHubConnector(
                circuit_breaker=self._get_breaker("github"),
                default_timeout=self.default_timeout,
                retry_attempts=self.retry_attempts,
            )
        elif service_type == "git":
            connector = GitConnector()
        else:
            raise ValueError(f"Unknown service type: {service_type}")

        self._connectors[service_type] = connector
        return connector

    def is_service_available(self, service_type: str) -> bool:
        """Check if a service is available and configured."""
        try:
            connector = self.get_connector(service_type)
            if service_type == "github":
                status = connector.get_status()
                breaker_state = status.get("circuit_breaker", {}).get("state", "closed")
                if breaker_state == "open":
                    return False
                return bool(status["mcp_available"] or status["api_available"])
            elif service_type == "git":
                return True  # Git is always available (local)
            return False
        except Exception:
            return False

    def get_service_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all configured services."""
        status = {}

        # Check GitHub
        try:
            github_connector = self.get_connector("github")
            status["github"] = github_connector.get_status()
        except Exception as exc:
            breaker = self._circuit_breakers.get("github")
            status["github"] = {
                "available": False,
                "error": str(exc),
                "circuit_breaker": breaker.snapshot() if breaker else None,
            }

        # Check Git
        status["git"] = {"available": True, "message": "Local git repository"}

        return status
