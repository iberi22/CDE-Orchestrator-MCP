"""
GitHub Recipe Downloader Adapter.

Downloads recipe files from GitHub using raw.githubusercontent.com URLs.
"""

from typing import Dict

import aiohttp

from cde_orchestrator.domain.ports import IRecipeDownloader
from cde_orchestrator.infrastructure.circuit_breaker import circuit_breaker


class GitHubRecipeDownloader(IRecipeDownloader):
    """
    Downloads recipe files from GitHub repositories using HTTP.

    Uses raw.githubusercontent.com for direct file access without authentication.
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize downloader.

        Args:
            timeout: HTTP timeout in seconds
        """
        self.timeout = timeout

    @circuit_breaker(
        name="github_raw_api",
        failure_threshold=5,
        timeout=60.0,
        expected_exception=aiohttp.ClientError,
    )
    async def download_file(self, repo_url: str, branch: str, file_path: str) -> str:
        """
        Download a single file from GitHub.

        Args:
            repo_url: Full repository URL (e.g., https://github.com/iberi22/agents-flows-recipes)
            branch: Branch name (e.g., "main")
            file_path: Path to file within repo (e.g., "poml/engineering/ai-engineer.poml")

        Returns:
            File content as string

        Raises:
            Exception: If download fails
        """
        # Convert GitHub URL to raw URL
        # https://github.com/iberi22/agents-flows-recipes
        # -> https://raw.githubusercontent.com/iberi22/agents-flows-recipes/main/file_path

        # Extract owner and repo from URL
        parts = repo_url.rstrip("/").split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid repo URL: {repo_url}")

        owner = parts[-2]
        repo = parts[-1]

        # Build raw URL
        raw_url = (
            f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
        )

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as session:
                async with session.get(raw_url) as response:
                    if response.status == 404:
                        raise FileNotFoundError(
                            f"File not found: {file_path} (branch: {branch})"
                        )
                    elif response.status != 200:
                        raise Exception(
                            f"HTTP error {response.status} downloading {file_path}"
                        )

                    return await response.text(encoding="utf-8")
        except aiohttp.ClientError as e:
            raise Exception(f"Network error downloading {file_path}: {str(e)}")
        except Exception as e:
            raise Exception(f"Error downloading {file_path}: {str(e)}")

    async def download_directory(
        self, repo_url: str, branch: str, dir_path: str
    ) -> Dict[str, str]:
        """
        Download all files from a directory.

        NOTE: This requires GitHub API access. For now, we only support
        downloading individual files. To download directories, the use case
        should specify which files to download.

        Args:
            repo_url: Full repository URL
            branch: Branch name
            dir_path: Directory path within repo

        Returns:
            Dict mapping file_path -> content

        Raises:
            NotImplementedError: Always
        """
        raise NotImplementedError(
            "Directory download not yet implemented for GitHub raw access"
        )
