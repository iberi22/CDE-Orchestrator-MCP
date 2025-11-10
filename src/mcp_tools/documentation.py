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
def cde_scanDocumentation(
    project_path: str = ".", detail_level: str = "summary"
) -> str:
    """
    Scan and analyze documentation structure in a project.

    **USE THIS TOOL TO:**
    - Audit documentation organization
    - Find missing metadata (YAML frontmatter)
    - Identify orphaned documents
    - Get recommendations for improvement

    **PROGRESSIVE DISCLOSURE** (Anthropic Best Practice):
    Use `detail_level` to control token consumption:
    - "name_only": Just file paths (~10 tokens/file) - FASTEST
    - "summary": Paths + titles + types (~50 tokens/file) - BALANCED
    - "full": Complete metadata + preview (~500 tokens/file) - COMPREHENSIVE

    Args:
        project_path: Path to project root (default: current directory)
        detail_level: Level of detail to return (default: "summary")
            Options: "name_only", "summary", "full"

    Returns:
        JSON with structure based on detail_level:

        **name_only**:
            - files: List[str] - Just file paths
            - total: int - Total count

        **summary**:
            - files: List[Dict] - Path, title, type, status
            - total: int
            - missing_metadata: List[str]
            - recommendations: List[str]

        **full**:
            - files: List[Dict] - Complete metadata + first 100 lines
            - total: int
            - by_location: Dict[str, List]
            - missing_metadata: List[str]
            - orphaned_docs: List[str]
            - large_files: List[str]
            - recommendations: List[str]

    Examples:
        >>> cde_scanDocumentation(".", detail_level="name_only")
        {
          "files": ["specs/features/auth.md", "specs/design/architecture.md"],
          "total": 2
        }

        >>> cde_scanDocumentation(".", detail_level="summary")
        {
          "files": [
            {"path": "specs/features/auth.md", "title": "Authentication", "type": "feature"},
            {"path": "specs/design/architecture.md", "title": "Architecture", "type": "design"}
          ],
          "total": 2,
          "missing_metadata": [],
          "recommendations": ["✅ All files have metadata"]
        }

        >>> cde_scanDocumentation("E:\\my-project", detail_level="full")
        # Complete scan with all details

    **Token Impact**:
    - 100 files × name_only = ~1,000 tokens (vs 50,000 with full)
    - 100 files × summary = ~5,000 tokens (vs 50,000 with full)
    - Reduction: 80-98% depending on detail level

    **Common Use Cases:**
    1. Quick inventory: `cde_scanDocumentation(".", detail_level="name_only")`
    2. Initial audit: `cde_scanDocumentation(".", detail_level="summary")`
    3. Deep analysis: `cde_scanDocumentation(".", detail_level="full")`
    """
    use_case = ScanDocumentationUseCase()

    # Resolve project path
    if project_path == ".":
        project_path = os.getcwd()

    result = use_case.execute(project_path, detail_level=detail_level)
    return json.dumps(result, indent=2)


@tool_handler
def cde_createSpecification(
    feature_name: str, description: str, author: str, project_path: str = "."
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
        author=author,
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
