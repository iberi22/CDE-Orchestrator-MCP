"""
MCP Tool Search Adapter.

Provides progressive tool discovery following Anthropic's best practices.
"""

import asyncio
import inspect
from typing import Any, Dict, List, Literal

from ..infrastructure.cache import CacheManager

DetailLevel = Literal["name_only", "name_and_description", "full_schema"]


class MCPToolSearcher:
    """
    Search MCP tools by keyword with progressive detail levels.

    Implements Anthropic's recommendation for efficient tool discovery:
    - name_only: Just tool names (5 tokens/tool) - FASTEST
    - name_and_description: Names + descriptions (50 tokens/tool) - BALANCED
    - full_schema: Complete parameter schemas (200 tokens/tool) - COMPREHENSIVE

    Usage:
        >>> searcher = MCPToolSearcher(mcp_tools_module)
        >>> result = await searcher.search("skill", detail_level="name_only")
        >>> # Returns: {"tools": ["sourceSkill", "updateSkill"], "total": 2}
    """

    def __init__(self, mcp_tools_module: Any) -> None:
        self.cache_manager = CacheManager()
        """
        Initialize tool searcher.

        Args:
            mcp_tools_module: The mcp_tools module containing all tools
        """
        self.mcp_tools_module = mcp_tools_module

    async def search(
        self, query: str, detail_level: DetailLevel = "name_and_description"
    ) -> Dict[str, Any]:
        """
        Search tools by keyword with progressive detail.

        Args:
            query: Search keywords (e.g., "skill", "workflow", "project")
            detail_level: Level of detail to return

        Returns:
            {
                "tools": [...],  # Format depends on detail_level
                "total": int,
                "detail_level": str,
                "query": str
            }
        """
        # Lazy load tools (cached)
        tools = await self._discover_all_tools()

        # Search by keyword (case-insensitive)
        query_lower = query.lower()
        matches = [
            tool
            for tool in tools
            if query_lower in tool["name"].lower()
            or query_lower in tool["description"].lower()
            or any(query_lower in tag.lower() for tag in tool.get("tags", []))
        ]

        return {
            "tools": self._format_results(matches, detail_level),
            "total": len(matches),
            "detail_level": detail_level,
            "query": query,
        }

    async def list_all(self, detail_level: DetailLevel = "name_only") -> Dict[str, Any]:
        """
        List all available tools.

        Args:
            detail_level: Level of detail to return

        Returns:
            {
                "tools": [...],
                "total": int,
                "detail_level": str
            }
        """
        tools = await self._discover_all_tools()

        return {
            "tools": self._format_results(tools, detail_level),
            "total": len(tools),
            "detail_level": detail_level,
        }

    async def _discover_all_tools(self) -> List[Dict[str, Any]]:
        """
        Discover all MCP tools from the mcp_tools module.

        Executed in thread pool to avoid blocking event loop during introspection.

        Returns:
            List of tool metadata dictionaries
        """
        cache_key = "mcp_tools"
        cached_tools = self.cache_manager.get(cache_key)
        if cached_tools:
            return cached_tools

        loop = asyncio.get_running_loop()
        tools = await loop.run_in_executor(None, self._discover_all_tools_sync)
        self.cache_manager.set(cache_key, tools, expire=300)  # Cache for 5 minutes
        return tools

    def _discover_all_tools_sync(self) -> List[Dict[str, Any]]:
        """Synchronous implementation of tool discovery."""
        tools = []

        # Get all exported tools from __all__
        if hasattr(self.mcp_tools_module, "__all__"):
            tool_names = self.mcp_tools_module.__all__
        else:
            # Fallback: inspect module for callables starting with cde_
            tool_names = [
                name
                for name in dir(self.mcp_tools_module)
                if name.startswith("cde_")
                and callable(getattr(self.mcp_tools_module, name))
            ]

        for tool_name in tool_names:
            try:
                tool_func = getattr(self.mcp_tools_module, tool_name)
                tool_metadata = self._extract_tool_metadata(tool_name, tool_func)
                tools.append(tool_metadata)
            except Exception as e:
                # Skip tools that can't be inspected
                print(f"Warning: Could not inspect tool {tool_name}: {e}")
                continue

        return tools

    def _extract_tool_metadata(self, tool_name: str, tool_func: Any) -> Dict[str, Any]:
        """
        Extract metadata from tool function.

        Args:
            tool_name: Name of the tool
            tool_func: Tool function object

        Returns:
            Dictionary with tool metadata
        """
        # Get signature
        sig = inspect.signature(tool_func)

        # Get docstring
        doc = inspect.getdoc(tool_func) or "No description available"

        # Extract first line as short description
        doc_lines = doc.split("\n")
        short_desc = doc_lines[0].strip()

        # Extract parameters
        parameters = []
        for param_name, param in sig.parameters.items():
            param_info = {
                "name": param_name,
                "type": (
                    str(param.annotation)
                    if param.annotation != inspect.Parameter.empty
                    else "Any"
                ),
                "required": param.default == inspect.Parameter.empty,
                "default": (
                    str(param.default)
                    if param.default != inspect.Parameter.empty
                    else None
                ),
            }
            parameters.append(param_info)

        # Auto-detect tags based on name and description
        tags = self._extract_tags(tool_name, doc)

        return {
            "name": tool_name,
            "display_name": tool_name.replace("cde_", ""),  # Remove prefix
            "description": short_desc,
            "full_doc": doc,
            "parameters": parameters,
            "tags": tags,
        }

    def _extract_tags(self, tool_name: str, doc: str) -> List[str]:
        """
        Auto-detect tags from tool name and description.

        Args:
            tool_name: Name of the tool
            doc: Tool docstring

        Returns:
            List of relevant tags
        """
        tags = []

        # Tag by name patterns
        if "scan" in tool_name.lower() or "analyze" in tool_name.lower():
            tags.append("analysis")
        if "source" in tool_name.lower() or "update" in tool_name.lower():
            tags.append("skills")
        if "select" in tool_name.lower():
            tags.append("orchestration")
        if "execute" in tool_name.lower() or "delegate" in tool_name.lower():
            tags.append("execution")
        if "onboarding" in tool_name.lower() or "setup" in tool_name.lower():
            tags.append("setup")

        # Tag by keywords in description
        doc_lower = doc.lower()
        if "documentation" in doc_lower:
            tags.append("documentation")
        if "workflow" in doc_lower:
            tags.append("workflow")
        if "project" in doc_lower:
            tags.append("project")
        if "agent" in doc_lower or "jules" in doc_lower:
            tags.append("agents")

        return list(set(tags))  # Remove duplicates

    def _format_results(
        self, tools: List[Dict[str, Any]], detail_level: DetailLevel
    ) -> Any:
        """
        Format tool results based on detail level.

        Args:
            tools: List of tool metadata
            detail_level: Requested detail level

        Returns:
            Formatted results (List[str], List[Dict], or List[Dict])
        """
        if detail_level == "name_only":
            # Minimal: Just names (5 tokens/tool)
            return [t["display_name"] for t in tools]

        elif detail_level == "name_and_description":
            # Balanced: Names + descriptions (50 tokens/tool)
            return [
                {
                    "name": t["display_name"],
                    "description": t["description"],
                    "tags": t["tags"],
                }
                for t in tools
            ]

        else:  # full_schema
            # Complete: Full schemas (200 tokens/tool)
            return [
                {
                    "name": t["display_name"],
                    "full_name": t["name"],
                    "description": t["description"],
                    "full_doc": t["full_doc"],
                    "parameters": t["parameters"],
                    "tags": t["tags"],
                }
                for t in tools
            ]
