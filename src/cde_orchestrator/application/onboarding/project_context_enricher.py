# src/cde_orchestrator/application/onboarding/project_context_enricher.py
"""
Project Context Enricher - Orchestrates deep project analysis.

Combines:
- GitHistoryAnalyzer: Git history and commit patterns
- DocumentationSynthesizer: README, CONTRIBUTING, dependency files
- FrameworkDetector: Framework and architecture detection

Produces EnrichedProjectContext with comprehensive project information.
"""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from .documentation_synthesizer import DocumentationSynthesizer
from .framework_detector import FrameworkDetector
from .git_history_analyzer import GitHistoryAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class EnrichedProjectContext:
    """
    Comprehensive project context combining multiple analysis sources.

    Used to generate rich, context-aware AI assistant documentation.
    """

    # Basic analysis (from ProjectAnalysisUseCase)
    file_count: int
    language_stats: Dict[str, int]
    dependency_files: List[str]

    # Git insights
    git_insights: Dict[str, Any]
    recent_commits: List[Dict[str, str]]
    active_branches: List[str]
    main_contributors: List[str]
    commit_frequency: str

    # Documentation synthesis
    architecture_description: str
    tech_stack: List[str]
    build_commands: List[str]
    test_commands: List[str]
    coding_conventions: List[str]

    # Framework detection
    detected_frameworks: List[str]
    architecture_pattern: str
    project_type: str


class ProjectContextEnricher:
    """
    Enriches basic project analysis with deep contextual information.

    Orchestrates three specialized analyzers:
    1. GitHistoryAnalyzer: Recent commits, branches, contributors
    2. DocumentationSynthesizer: README, CONTRIBUTING, dependency files
    3. FrameworkDetector: Frameworks, architecture patterns, project type

    Example usage:
        enricher = ProjectContextEnricher(Path("/path/to/project"))
        context = await enricher.enrich(basic_analysis)

        # Use context to generate rich documentation
        agents_md = generate_agents_md(context)
    """

    def __init__(self, project_path: Path):
        """
        Initialize enricher for a project.

        Args:
            project_path: Root directory of the project to analyze
        """
        self.project_path = project_path
        self.git_analyzer = GitHistoryAnalyzer(project_path)
        self.doc_synthesizer = DocumentationSynthesizer(project_path)
        self.framework_detector = FrameworkDetector(project_path)

    async def enrich(self, basic_analysis: Dict[str, Any]) -> EnrichedProjectContext:
        """
        Transform basic analysis into rich contextual information.

        Args:
            basic_analysis: Output from ProjectAnalysisUseCase containing:
                - file_count: int
                - language_stats: Dict[str, int]
                - dependency_files: List[str]

        Returns:
            EnrichedProjectContext with comprehensive project information

        Example basic_analysis:
            {
                "file_count": 150,
                "language_stats": {".py": 80, ".md": 30},
                "dependency_files": ["pyproject.toml", "requirements.txt"]
            }
        """
        logger.info(f"Enriching context for project: {self.project_path.name}")

        # Run all analyzers concurrently
        git_insights = await self.git_analyzer.analyze(days=30)
        docs = await self.doc_synthesizer.synthesize()
        frameworks = await self.framework_detector.detect()

        # Build enriched context
        context = EnrichedProjectContext(
            # Basic (from input)
            file_count=basic_analysis.get("file_count", 0),
            language_stats=basic_analysis.get("language_stats", {}),
            dependency_files=basic_analysis.get("dependency_files", []),
            # Git
            git_insights=git_insights,
            recent_commits=git_insights.get("recent_commits", []),
            active_branches=git_insights.get("branches", []),
            main_contributors=git_insights.get("contributors", []),
            commit_frequency=git_insights.get("commit_frequency", "Unknown"),
            # Documentation
            architecture_description=docs.get("architecture", "Not documented"),
            tech_stack=docs.get("tech_stack", []),
            build_commands=docs.get("build_commands", []),
            test_commands=docs.get("test_commands", []),
            coding_conventions=docs.get("conventions", []),
            # Frameworks
            detected_frameworks=frameworks.get("frameworks", []),
            architecture_pattern=frameworks.get("architecture_pattern", "Unknown"),
            project_type=frameworks.get("project_type", "unknown"),
        )

        logger.info(
            f"Enrichment complete: {len(context.tech_stack)} technologies, "
            f"{len(context.recent_commits)} commits, "
            f"{len(context.detected_frameworks)} frameworks"
        )

        return context

    def to_dict(self, context: EnrichedProjectContext) -> Dict[str, Any]:
        """
        Convert EnrichedProjectContext to dictionary for serialization.

        Args:
            context: EnrichedProjectContext instance

        Returns:
            Dictionary representation
        """
        return {
            "file_count": context.file_count,
            "language_stats": context.language_stats,
            "dependency_files": context.dependency_files,
            "git_insights": context.git_insights,
            "recent_commits": context.recent_commits,
            "active_branches": context.active_branches,
            "main_contributors": context.main_contributors,
            "commit_frequency": context.commit_frequency,
            "architecture_description": context.architecture_description,
            "tech_stack": context.tech_stack,
            "build_commands": context.build_commands,
            "test_commands": context.test_commands,
            "coding_conventions": context.coding_conventions,
            "detected_frameworks": context.detected_frameworks,
            "architecture_pattern": context.architecture_pattern,
            "project_type": context.project_type,
        }
