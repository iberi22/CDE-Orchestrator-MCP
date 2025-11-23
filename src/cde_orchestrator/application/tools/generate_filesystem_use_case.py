"""
Generate MCP Tool Filesystem Use Case.

Business logic for auto-generating ./servers/cde/ structure.
"""

from pathlib import Path
from typing import Any, Dict

from ...adapters.mcp_tool_filesystem_generator import MCPToolFilesystemGenerator
from ...infrastructure.telemetry import trace_execution


class GenerateFilesystemUseCase:
    """
    Use case: Generate filesystem representation of MCP tools.

    Orchestrates filesystem generation following Anthropic's progressive
    disclosure pattern for minimal token overhead.
    """

    def __init__(self) -> None:
        """Initialize use case with filesystem generator."""
        self.generator = MCPToolFilesystemGenerator()

    @trace_execution
    async def execute(self, mcp_tools_module: Any, output_dir: Path) -> Dict[str, Any]:
        """
        Execute filesystem generation.

        Args:
            mcp_tools_module: Module containing MCP tools
            output_dir: Root directory for generation

        Returns:
            {
                "status": "success",
                "generated_files": List[str],
                "total_tools": int,
                "output_dir": str
            }
        """
        result = await self.generator.generate(mcp_tools_module, output_dir)
        return result
