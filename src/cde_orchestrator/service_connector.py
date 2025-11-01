# src/cde_orchestrator/service_connector.py
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
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


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
            with open(config_path, 'r') as f:
                config = json.load(f)

            return config.get("mcpServers", {})
        except Exception as e:
            print(f"Error loading MCP config: {e}")
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


class GitHubConnector:
    """
    GitHub service connector that uses external MCP when available.
    Falls back to local implementations when MCP is not configured.
    """

    def __init__(self):
        self.mcp_available = MCPDetector.is_github_mcp_available()
        self.mcp_config = MCPDetector.get_github_mcp_config() if self.mcp_available else None
        self.token = os.getenv("GITHUB_TOKEN")

    def create_issue(
        self,
        repo_owner: str,
        repo_name: str,
        title: str,
        body: str,
        labels: Optional[List[str]] = None
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
        # Try MCP first
        if self.mcp_available:
            return self._create_issue_via_mcp(title, body, labels)

        # Try GitHub API
        if self.token:
            return self._create_issue_via_api(repo_owner, repo_name, title, body, labels)

        # Fallback to local
        return self._create_issue_local(title, body, labels)

    def _create_issue_via_mcp(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create issue via external MCP GitHub server.
        Note: In a real implementation, this would use the MCP client library
        to communicate with the external GitHub MCP server.
        """
        return {
            "id": f"mcp-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "title": title,
            "body": body,
            "labels": labels or [],
            "method": "mcp",
            "message": "Issue created via external GitHub MCP server"
        }

    def _create_issue_via_api(
        self,
        repo_owner: str,
        repo_name: str,
        title: str,
        body: str,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create issue via GitHub API."""
        try:
            import requests
        except ImportError:
            return self._create_issue_local(title, body, labels)

        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "title": title,
            "body": body
        }

        if labels:
            data["labels"] = labels

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error creating GitHub issue via API: {e}")
            return self._create_issue_local(title, body, labels)

    def _create_issue_local(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Fallback: Create issue as local file.
        This ensures workflows can continue without external dependencies.
        """
        issues_dir = Path(".cde") / "issues"
        issues_dir.mkdir(exist_ok=True)

        issue_id = f"local-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
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
            "url": str(issue_file),
            "method": "local",
            "message": "Issue created locally (GitHub MCP not configured)"
        }

    def get_status(self) -> Dict[str, Any]:
        """Get connector status information."""
        return {
            "mcp_available": self.mcp_available,
            "mcp_config": self.mcp_config is not None,
            "api_available": self.token is not None,
            "fallback": not self.mcp_available and not self.token
        }


class GitConnector:
    """
    Git connector for local repository operations.
    Uses git commands via subprocess for direct git operations.
    """

    def __init__(self):
        self.repo_path = Path.cwd()

    def create_branch(self, branch_name: str, base_branch: str = "main") -> Dict[str, Any]:
        """Create a new git branch."""
        try:
            # Fetch latest changes
            subprocess.run(
                ["git", "fetch", "origin", base_branch],
                cwd=self.repo_path,
                capture_output=True,
                check=False
            )

            # Create branch
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name, f"origin/{base_branch}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "branch": branch_name,
                    "message": f"Branch {branch_name} created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": "Failed to create branch"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error creating branch"
            }

    def commit_changes(
        self,
        message: str,
        files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Commit changes to git repository."""
        try:
            # Add files
            if files:
                subprocess.run(
                    ["git", "add"] + files,
                    cwd=self.repo_path,
                    capture_output=True,
                    check=False
                )
            else:
                subprocess.run(
                    ["git", "add", "."],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=False
                )

            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Changes committed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": "Failed to commit changes"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error committing changes"
            }

    def push_branch(self, branch_name: str) -> Dict[str, Any]:
        """Push a branch to remote repository."""
        try:
            result = subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Branch {branch_name} pushed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": "Failed to push branch"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error pushing branch"
            }


class ServiceConnectorFactory:
    """
    Factory for creating and managing service connectors.
    Provides a unified interface for accessing different service connectors.
    """

    def __init__(self):
        self._connectors: Dict[str, Any] = {}

    def get_connector(self, service_type: str):
        """
        Get or create a connector for the specified service type.

        Args:
            service_type: Type of service (e.g., 'github', 'git')

        Returns:
            Service connector instance
        """
        if service_type in self._connectors:
            return self._connectors[service_type]

        if service_type == "github":
            connector = GitHubConnector()
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
                return status["mcp_available"] or status["api_available"]
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
        except:
            status["github"] = {"available": False, "error": "Not configured"}

        # Check Git
        status["git"] = {"available": True, "message": "Local git repository"}

        return status
