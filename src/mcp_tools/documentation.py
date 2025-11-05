"""
Documentation MCP Tools.

Tools for scanning and analyzing documentation structure and quality.
"""

import json
import os

from cde_orchestrator.application.documentation import (
    AnalyzeDocumentationUseCase,
    CreateSpecificationUseCase,
    ScanDocumentationUseCase,
)

from ._base import tool_handler


@tool_handler
def cde_scanDocumentation(project_path: str = ".") -> str:
    """
    Scan and analyze documentation structure in a project.

    **USE THIS TOOL TO:**
    - Audit documentation organization
    - Find missing metadata (YAML frontmatter)
    - Identify orphaned documents
    - Get recommendations for improvement

    Args:
        project_path: Path to project root (default: current directory)

    Returns:
        JSON with:
            - total_docs: Total markdown files found
            - by_location: Documents grouped by directory
            - missing_metadata: Files without YAML frontmatter
            - orphaned_docs: Files not in standard directories
            - large_files: Documents exceeding 1000 lines
            - recommendations: Actionable improvement suggestions

    Examples:
        >>> cde_scanDocumentation(".")
        {
          "total_docs": 45,
          "missing_metadata": ["docs/old-guide.md", "README-backup.md"],
          "recommendations": [
            "🔴 12 documents missing YAML frontmatter metadata",
            "⚠️ 3 orphaned documents in root directory"
          ]
        }

        >>> cde_scanDocumentation("E:\\my-project")
        # Scan specific project

    **Common Use Cases:**
    1. Initial project audit: `cde_scanDocumentation(".")`
    2. Before migration: Check what needs fixing
    3. After cleanup: Verify improvements
    """
    use_case = ScanDocumentationUseCase()

    # Resolve project path
    if project_path == ".":
        project_path = os.getcwd()

    result = use_case.execute(project_path)
    return json.dumps(result, indent=2)


@tool_handler
def cde_createSpecification(
    feature_name: str,
    description: str,
    author: str,
    project_path: str = "."
) -> str:
    """
    Creates a new feature specification document.

    This tool generates a new specification file in `specs/features/`
    with the correct filename and pre-populated YAML frontmatter.

    Args:
        feature_name: The name of the feature (e.g., "User Authentication").
        description: A one-sentence description of the feature.
        author: The name or ID of the authoring agent.
        project_path: The path to the project root (default: current directory).

    Returns:
        JSON with the path to the newly created file or an error message.
    """
    use_case = CreateSpecificationUseCase()

    if project_path == ".":
        project_path = os.getcwd()

    result = use_case.execute(
        project_path=project_path,
        feature_name=feature_name,
        description=description,
        author=author
    )
    return json.dumps(result, indent=2)


@tool_handler
def cde_analyzeDocumentation(project_path: str = ".") -> str:
    """
    Deep analysis of documentation quality and structure.

    **USE THIS TOOL TO:**
    - Check link integrity (find broken links)
    - Analyze metadata consistency
    - Get quality score (0-100)
    - Identify specific issues
    - Get actionable suggestions

    Args:
        project_path: Path to project root (default: current directory)

    Returns:
        JSON with:
            - quality_score: Overall quality rating (0-100)
            - link_analysis: Broken/valid links
            - metadata_analysis: Consistency checks
            - quality_indicators: Content quality metrics
            - issues: List of problems found
            - suggestions: Actionable improvements

    Examples:
        >>> cde_analyzeDocumentation(".")
        {
          "quality_score": 72.5,
          "link_analysis": {
            "total_links": 156,
            "valid_links": 142,
            "broken_links": 14
          },
          "issues": [
            "🔴 14 broken internal links detected",
            "⚠️ 8 files missing required metadata fields"
          ],
          "suggestions": [
            "✅ Documentation quality is good. Minor improvements recommended.",
            "→ Fix broken links to improve navigation",
            "→ Add YAML frontmatter to all documents"
          ]
        }

    **Quality Score Breakdown:**
    - 90-100: Excellent (well-organized, complete metadata, no broken links)
    - 70-89: Good (minor issues, mostly organized)
    - 50-69: Needs work (missing metadata, broken links)
    - <50: Poor (major issues, needs comprehensive audit)

    **Common Use Cases:**
    1. Health check: `cde_analyzeDocumentation(".")`
    2. Pre-migration assessment: See what needs fixing
    3. Post-cleanup validation: Verify improvements
    """
    use_case = AnalyzeDocumentationUseCase()

    # Resolve project path
    if project_path == ".":
        project_path = os.getcwd()

    result = use_case.execute(project_path)
    return json.dumps(result, indent=2)
