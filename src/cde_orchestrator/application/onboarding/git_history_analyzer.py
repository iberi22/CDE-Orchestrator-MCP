# src/cde_orchestrator/application/onboarding/git_history_analyzer.py
"""
Git History Analyzer - Extracts insights from Git repository history.

Provides context about:
- Recent commits (last 30 days)
- Active branches
- Main contributors
- Commit frequency
- Architectural decisions (refactorings, migrations)
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from git import GitCommandError, Repo

    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    Repo = Any  # type: ignore
    GitCommandError = Exception  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class GitInsights:
    """Insights extracted from Git repository."""

    recent_commits: List[Dict[str, str]]  # {"hash", "message", "author", "date"}
    branches: List[str]
    contributors: List[str]
    commit_frequency: str  # "Very active", "Moderate", "Low", "Unknown"
    architectural_decisions: List[str]  # Commits with refactor/architecture keywords


class GitHistoryAnalyzer:
    """
    Analyzes Git repository history to extract project context.

    Provides:
    - Recent commits (last 30 days by default)
    - Active branches
    - Main contributors
    - Development frequency (commits per week)
    - Architectural decisions (refactoring commits)

    This enriches onboarding documentation with real project activity context.
    """

    def __init__(self, project_path: Path):
        """
        Initialize analyzer for a project.

        Args:
            project_path: Root directory of the project to analyze
        """
        self.project_path = project_path
        self.repo_path = self._find_git_root()

    def _find_git_root(self) -> Optional[Path]:
        """
        Find Git repository root by walking up directory tree.

        Returns:
            Path to Git repository root or None if not found
        """
        current = self.project_path
        while current != current.parent:
            git_dir = current / ".git"
            if git_dir.exists():
                logger.debug(f"Found Git repository at: {current}")
                return current
            current = current.parent

        logger.debug("Not a Git repository")
        return None

    async def analyze(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze Git repository and extract insights.

        Args:
            days: Number of days to look back for recent commits

        Returns:
            Dictionary with Git insights:
            {
                "recent_commits": [...],
                "branches": [...],
                "contributors": [...],
                "commit_frequency": "Very active",
                "architectural_decisions": [...]
            }
        """
        if not GIT_AVAILABLE:
            logger.warning("GitPython not available, skipping Git analysis")
            return self._empty_insights()

        if not self.repo_path:
            logger.info("Not a Git repository, skipping Git analysis")
            return self._empty_insights()

        try:
            repo = Repo(self.repo_path)

            # Recent commits
            recent_commits = self._get_recent_commits(repo, days=days)

            # Branches
            branches = self._get_branches(repo)

            # Contributors
            contributors = self._get_contributors(repo)

            # Commit frequency
            commit_frequency = self._calculate_frequency(recent_commits)

            # Architectural decisions
            arch_decisions = self._find_architectural_commits(recent_commits)

            return {
                "recent_commits": recent_commits,
                "branches": branches,
                "contributors": contributors,
                "commit_frequency": commit_frequency,
                "architectural_decisions": arch_decisions,
            }

        except GitCommandError as e:
            logger.error(f"Git command failed: {e}")
            return self._empty_insights()
        except Exception as e:
            logger.error(f"Unexpected error during Git analysis: {e}")
            return self._empty_insights()

    def _get_recent_commits(
        self, repo: Repo, days: int = 30, max_count: int = 100
    ) -> List[Dict[str, str]]:
        """
        Get commits from the last N days.

        Args:
            repo: Git repository object
            days: Number of days to look back
            max_count: Maximum number of commits to retrieve

        Returns:
            List of commit dictionaries
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        commits = []

        try:
            for commit in list(repo.iter_commits("HEAD", max_count=max_count)):
                commit_date = datetime.fromtimestamp(commit.committed_date)
                if commit_date < cutoff_date:
                    break

                # Extract first line of commit message
                message = commit.message.strip().split("\n")[0]

                commits.append(
                    {
                        "hash": commit.hexsha[:7],
                        "message": message,
                        "author": commit.author.name,
                        "date": commit_date.strftime("%Y-%m-%d"),
                    }
                )

            logger.debug(f"Found {len(commits)} commits in last {days} days")

        except Exception as e:
            logger.error(f"Error reading commits: {e}")

        return commits

    def _get_branches(self, repo: Repo, max_branches: int = 10) -> List[str]:
        """
        Get list of branch names.

        Args:
            repo: Git repository object
            max_branches: Maximum number of branches to return

        Returns:
            List of branch names
        """
        try:
            branches = [b.name for b in repo.branches][:max_branches]
            logger.debug(f"Found {len(branches)} branches")
            return branches
        except Exception as e:
            logger.error(f"Error reading branches: {e}")
            return []

    def _get_contributors(self, repo: Repo, max_commits: int = 200) -> List[str]:
        """
        Get list of unique contributors.

        Args:
            repo: Git repository object
            max_commits: Number of commits to scan for contributors

        Returns:
            List of contributor names (sorted by commit count)
        """
        contributors: Dict[str, int] = {}

        try:
            for commit in list(repo.iter_commits("HEAD", max_count=max_commits)):
                author = commit.author.name
                contributors[author] = contributors.get(author, 0) + 1

            # Sort by commit count (descending)
            sorted_contributors = sorted(
                contributors.items(), key=lambda x: x[1], reverse=True
            )

            contributor_names = [name for name, _ in sorted_contributors]
            logger.debug(f"Found {len(contributor_names)} unique contributors")

            return contributor_names

        except Exception as e:
            logger.error(f"Error reading contributors: {e}")
            return []

    def _calculate_frequency(self, commits: List[Dict[str, str]]) -> str:
        """
        Calculate development frequency based on commit count.

        Args:
            commits: List of commits from last N days

        Returns:
            Frequency label: "Very active", "Moderate", "Low", "Unknown"
        """
        commit_count = len(commits)

        if commit_count > 20:
            return "Very active"
        elif commit_count > 10:
            return "Moderate"
        elif commit_count > 0:
            return "Low"
        else:
            return "Unknown"

    def _find_architectural_commits(self, commits: List[Dict[str, str]]) -> List[str]:
        """
        Find commits related to architecture changes.

        Looks for keywords: refactor, architecture, redesign, restructure, migration

        Args:
            commits: List of commits to analyze

        Returns:
            List of architectural decision commits (formatted strings)
        """
        keywords = [
            "refactor",
            "architecture",
            "redesign",
            "restructure",
            "migration",
            "migrate",
        ]
        arch_commits = []

        for commit in commits:
            message = commit["message"].lower()
            if any(keyword in message for keyword in keywords):
                formatted = f"{commit['hash']}: {commit['message']}"
                arch_commits.append(formatted)

        logger.debug(f"Found {len(arch_commits)} architectural decision commits")
        return arch_commits

    def _empty_insights(self) -> Dict[str, Any]:
        """
        Return empty insights when Git is not available or not a Git repo.

        Returns:
            Dictionary with empty values
        """
        return {
            "recent_commits": [],
            "branches": [],
            "contributors": [],
            "commit_frequency": "Unknown",
            "architectural_decisions": [],
        }
