"""
MCP Tool Filesystem Generator (Anthropic Pattern).

Auto-generates ./servers/cde/ filesystem structure with one Python file per MCP tool
for progressive tool discovery without loading full schemas.

Based on Anthropic's "Code execution with MCP" article (2025):
https://www.anthropic.com/research/code-execution-with-mcp

Token Efficiency:
- Traditional: Load all 40+ tools = 39,568 bytes
- Filesystem: List files only = 377 bytes (99.0% reduction)
"""

import inspect
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ToolMetadata(BaseModel):
    """Metadata for a single MCP tool."""

    name: str
    description: str
    parameters: Dict[str, Any]
    tags: List[str] = []
    examples: List[str] = []


class MCPToolFilesystemGenerator:
    """
    Generate filesystem representation of MCP tools.

    Creates ./servers/cde/ with one .py file per tool, enabling:
    - List tools by scanning directory (99% token reduction)
    - Load tool schema only when needed (lazy loading)
    - Progressive disclosure: name_only → summary → full_schema

    Usage:
        >>> generator = MCPToolFilesystemGenerator()
        >>> generator.generate(mcp_tools_module, output_dir=Path("."))
        >>> # Creates: ./servers/cde/startFeature.py, submitWork.py, etc.
    """

    def __init__(self) -> None:
        """Initialize filesystem generator."""
        self.output_dir: Optional[Path] = None

    def generate(self, mcp_tools_module: Any, output_dir: Path) -> Dict[str, Any]:
        """
        Generate ./servers/cde/ filesystem structure.

        Args:
            mcp_tools_module: Module containing MCP tools (src.mcp_tools)
            output_dir: Root directory for generation (e.g., ".")

        Returns:
            {
                "generated_files": List[str],
                "total_tools": int,
                "output_dir": str
            }
        """
        self.output_dir = output_dir
        servers_dir = output_dir / "servers" / "cde"
        servers_dir.mkdir(parents=True, exist_ok=True)

        # Discover all tools
        tools = self._discover_tools(mcp_tools_module)

        # Generate one file per tool
        generated_files = []
        for tool in tools:
            tool_file = self._generate_tool_file(tool, servers_dir)
            generated_files.append(str(tool_file.relative_to(output_dir)))

        # Generate __init__.py with exports
        init_file = self._generate_init_file(tools, servers_dir)
        generated_files.append(str(init_file.relative_to(output_dir)))

        return {
            "generated_files": generated_files,
            "total_tools": len(tools),
            "output_dir": str(servers_dir),
            "status": "success",
        }

    def _discover_tools(self, mcp_tools_module: Any) -> List[ToolMetadata]:
        """
        Discover all MCP tools from module.

        Args:
            mcp_tools_module: Module to inspect

        Returns:
            List of ToolMetadata objects
        """
        tools: List[ToolMetadata] = []

        for name in dir(mcp_tools_module):
            if not name.startswith("cde_"):
                continue

            tool_func = getattr(mcp_tools_module, name)
            if not callable(tool_func):
                continue

            try:
                metadata = self._extract_metadata(name, tool_func)
                tools.append(metadata)
            except Exception as e:
                print(f"Warning: Could not extract metadata for {name}: {e}")
                continue

        return tools

    def _extract_metadata(self, name: str, tool_func: Any) -> ToolMetadata:
        """
        Extract metadata from tool function.

        Args:
            name: Tool name
            tool_func: Tool function object

        Returns:
            ToolMetadata with name, description, parameters, tags
        """
        # Get docstring
        doc = inspect.getdoc(tool_func) or "No description available"
        description = doc.split("\n")[0]  # First line as description

        # Get signature
        sig = inspect.signature(tool_func)
        parameters: Dict[str, Any] = {}

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls", "kwargs"):
                continue

            param_info: Dict[str, Any] = {"name": param_name}

            # Type annotation (clean format)
            if param.annotation != inspect.Parameter.empty:
                type_str = str(param.annotation)
                # Clean up "<class 'str'>" → "str"
                if type_str.startswith("<class '") and type_str.endswith("'>"):
                    type_str = type_str[8:-2]
                param_info["type"] = type_str

            # Default value
            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default

            parameters[param_name] = param_info

        # Auto-generate tags from name
        tags = self._extract_tags(name, doc)

        return ToolMetadata(
            name=name, description=description, parameters=parameters, tags=tags
        )

    def _extract_tags(self, name: str, doc: str) -> List[str]:
        """
        Extract tags from tool name and docstring.

        Args:
            name: Tool name
            doc: Tool docstring

        Returns:
            List of tags (e.g., ["workflow", "orchestration"])
        """
        tags = []
        text = f"{name} {doc}".lower()

        # Category mapping
        categories = {
            "workflow": ["workflow", "select", "start", "submit"],
            "project": ["project", "onboarding", "setup"],
            "documentation": ["documentation", "scan", "analyze", "publish"],
            "skill": ["skill", "source", "update"],
            "orchestration": ["orchestration", "agent", "execute"],
            "analysis": ["analysis", "analyze", "evaluate"],
            "execution": ["execution", "execute", "run"],
            "setup": ["setup", "install", "configure"],
            "agents": ["agent", "jules", "copilot", "gemini"],
        }

        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                tags.append(category)

        return tags or ["general"]

    def _generate_tool_file(self, tool: ToolMetadata, output_dir: Path) -> Path:
        """
        Generate individual tool file.

        Args:
            tool: ToolMetadata object
            output_dir: Output directory

        Returns:
            Path to generated file
        """
        # Remove cde_ prefix for filename
        filename = tool.name.replace("cde_", "") + ".py"
        file_path = output_dir / filename

        # Generate file content
        content = f'''"""
{tool.name} - MCP Tool

{tool.description}

Tags: {", ".join(tool.tags)}

Auto-generated by MCPToolFilesystemGenerator.
"""

from typing import Any, Dict, Optional

def {tool.name}(
'''

        # Add parameters
        params = []
        # Sort: required parameters first, then optional
        required_params = [
            (name, info)
            for name, info in tool.parameters.items()
            if "default" not in info
        ]
        optional_params = [
            (name, info) for name, info in tool.parameters.items() if "default" in info
        ]

        # Add required params first
        for param_name, param_info in required_params:
            param_type = param_info.get("type", "Any")
            params.append(f"    {param_name}: {param_type}")

        # Then optional params
        for param_name, param_info in optional_params:
            param_type = param_info.get("type", "Any")
            param_default = param_info.get("default")

            if isinstance(param_default, str):
                params.append(f'    {param_name}: {param_type} = "{param_default}"')
            else:
                params.append(f"    {param_name}: {param_type} = {param_default}")

        content += ",\n".join(params) if params else "    # No parameters"
        content += '''
) -> str:
    """
    {description}

    Parameters:
        {parameters}

    Returns:
        JSON string with result

    Tags: {tags}
    """
    # This is a stub - actual implementation in src/mcp_tools/{tool_name}.py
    raise NotImplementedError("Use mcp_tools.{tool_name} for actual implementation")


# Metadata for progressive disclosure
TOOL_METADATA = {{
    "name": "{name}",
    "description": "{description}",
    "parameters": {parameters_json},
    "tags": {tags_json}
}}
'''.format(
            description=tool.description,
            parameters=", ".join(
                f"{name}: {info.get('type', 'Any')}"
                for name, info in tool.parameters.items()
            )
            or "None",
            tags=", ".join(tool.tags),
            tool_name=tool.name,
            name=tool.name,
            parameters_json=json.dumps(tool.parameters, indent=8),
            tags_json=json.dumps(tool.tags),
        )

        # Write file
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def _generate_init_file(self, tools: List[ToolMetadata], output_dir: Path) -> Path:
        """
        Generate __init__.py with all tool exports.

        Args:
            tools: List of ToolMetadata objects
            output_dir: Output directory

        Returns:
            Path to __init__.py
        """
        init_path = output_dir / "__init__.py"

        # Generate content
        content = '''"""
CDE MCP Tools - Filesystem Discovery Pattern

Auto-generated tool stubs for progressive disclosure.

Usage:
    # List all tools (name_only)
    tools = [f.stem for f in Path("servers/cde").glob("*.py") if f.stem != "__init__"]

    # Load tool metadata (summary)
    from servers.cde import startFeature
    metadata = startFeature.TOOL_METADATA

    # Use actual tool (full)
    from mcp_tools import cde_startFeature
    result = cde_startFeature(user_prompt="...")

Token Efficiency:
- name_only: List files = 377 bytes (99.0% reduction)
- summary: Import + metadata = ~3KB (92% reduction)
- full: Actual implementation = ~40KB (baseline)
"""

from pathlib import Path

# Auto-discovered tools
TOOLS = [
'''

        # Add tool exports
        for tool in tools:
            stub_name = tool.name.replace("cde_", "")
            content += f'    "{tool.name}",  # servers/cde/{stub_name}.py\n'

        content += """]

# Total tools
TOTAL_TOOLS = len(TOOLS)

# Export all
__all__ = TOOLS + ["TOTAL_TOOLS"]
"""

        init_path.write_text(content, encoding="utf-8")
        return init_path
