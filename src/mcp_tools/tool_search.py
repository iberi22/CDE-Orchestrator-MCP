"""
Tool Search MCP Tools.

Progressive tool discovery following Anthropic's best practices.
"""

import json

from cde_orchestrator.adapters.mcp_tool_searcher import MCPToolSearcher

from ._base import tool_handler


@tool_handler
async def cde_searchTools(
    query: str = "", detail_level: str = "name_and_description"
) -> str:
    """
    Search available CDE tools by keyword with progressive detail levels.

    **PROGRESSIVE DISCLOSURE** (Anthropic Best Practice):
    Load only the tool definitions you need, not all 40+ tools upfront.

    **USE THIS TOOL TO:**
    - Discover relevant tools for your task
    - Understand tool capabilities before using them
    - Reduce token consumption (98.7% reduction vs loading all tools)

    Args:
        query: Search keywords (e.g., "skill", "workflow", "project", "documentation")
               Leave empty to list all tools
        detail_level: Level of detail to return (default: "name_and_description")
            - "name_only": Just tool names (5 tokens/tool) - FASTEST
            - "name_and_description": Names + descriptions + tags (50 tokens/tool) - BALANCED
            - "full_schema": Complete parameter schemas (200 tokens/tool) - COMPREHENSIVE

    Returns:
        JSON with:
            - tools: List of matching tools (format depends on detail_level)
            - total: Number of matches
            - detail_level: Detail level used
            - query: Search query (if provided)

    Examples:
        >>> await cde_searchTools("skill", detail_level="name_only")
        {
          "tools": ["sourceSkill", "updateSkill"],
          "total": 2,
          "detail_level": "name_only",
          "query": "skill"
        }

        >>> await cde_searchTools("workflow", detail_level="name_and_description")
        {
          "tools": [
            {
              "name": "selectWorkflow",
              "description": "Analyze user prompt and recommend optimal workflow",
              "tags": ["orchestration", "workflow"]
            },
            {
              "name": "executeFullImplementation",
              "description": "Execute complete workflow implementation",
              "tags": ["execution", "workflow"]
            }
          ],
          "total": 2,
          "detail_level": "name_and_description",
          "query": "workflow"
        }

        >>> await cde_searchTools("scanDocumentation", detail_level="full_schema")
        {
          "tools": [{
            "name": "scanDocumentation",
            "full_name": "cde_scanDocumentation",
            "description": "Scan and analyze documentation structure",
            "full_doc": "...",
            "parameters": [
              {"name": "project_path", "type": "str", "required": false, "default": "."},
              {"name": "detail_level", "type": "str", "required": false, "default": "summary"}
            ],
            "tags": ["documentation", "analysis"]
          }],
          "total": 1,
          "detail_level": "full_schema"
        }

        >>> await cde_searchTools(detail_level="name_only")
        # Lists ALL tools (just names)

    **Token Impact**:
    - Loading all 40 tools upfront: ~150,000 tokens
    - name_only for 40 tools: ~200 tokens (99.9% reduction)
    - name_and_description for 40 tools: ~2,000 tokens (98.7% reduction)
    - Searching for 2 specific tools: ~100 tokens (99.99% reduction)

    **Common Patterns**:

    **Pattern 1: Discover tools for task**
    ```python
    # Find tools related to skills
    result = await cde_searchTools("skill", detail_level="name_and_description")
    # Use returned tools: sourceSkill, updateSkill
    ```

    **Pattern 2: Progressive detail loading**
    ```python
    # Step 1: See what's available (minimal tokens)
    all_tools = await cde_searchTools(detail_level="name_only")

    # Step 2: Get details for relevant tools
    workflow_tools = await cde_searchTools("workflow", detail_level="name_and_description")

    # Step 3: Full schema only when needed
    full_details = await cde_searchTools("selectWorkflow", detail_level="full_schema")
    ```

    **Pattern 3: Tool discovery in workflow**
    ```python
    # Discover available documentation tools
    tools = await cde_searchTools("scan", detail_level="name_only")
    # Returns: ["scanDocumentation", "analyzeDocumentation"]

    # Use discovered tools
    from servers.cde import scanDocumentation
    result = scanDocumentation(project_path=".")
    ```

    **Tags Available**:
    - analysis: Scanning, analyzing tools
    - skills: Skill management tools
    - orchestration: Workflow selection tools
    - execution: Code execution tools
    - setup: Onboarding, project setup
    - documentation: Documentation tools
    - workflow: Workflow management
    - project: Project operations
    - agents: AI agent delegation

    **See Also**:
    - Anthropic's Code Execution with MCP: https://www.anthropic.com/engineering/code-execution-with-mcp
    - CDE Research: agent-docs/research/research-anthropic-mcp-code-execution-2025-11-09.md
    """
    # Import mcp_tools module
    import mcp_tools

    # Initialize searcher
    searcher = MCPToolSearcher(mcp_tools)

    # Validate detail_level
    if detail_level not in {"name_only", "name_and_description", "full_schema"}:
        return json.dumps(
            {
                "error": f"Invalid detail_level: {detail_level}",
                "valid_options": ["name_only", "name_and_description", "full_schema"],
            },
            indent=2,
        )

    # Search or list all
    if query:
        result = await searcher.search(query, detail_level=detail_level)
    else:
        result = await searcher.list_all(detail_level=detail_level)

    return json.dumps(result, indent=2)
