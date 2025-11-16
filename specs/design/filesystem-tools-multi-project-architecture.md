---
title: "Design: Filesystem-Based Tools for Multi-Project Management"
description: "Architecture for progressive tool disclosure in CDE Orchestrator managing 1000+ projects"
type: "design"
status: "active"
created: "2025-11-09"
updated: "2025-11-09"
author: "GitHub Copilot"
related_research: "agent-docs/research/research-anthropic-mcp-code-execution-2025-11-09.md"
related_task: "specs/tasks/implement-anthropic-mcp-best-practices.md"
llm_summary: |
  CDE Orchestrator uses GLOBAL ./servers/cde/ for tool discovery (not per-project).
  Tools accept project_path parameter to operate on any project. This enables
  98.7% token reduction via progressive disclosure while managing 1000+ projects.
---

# Design: Filesystem-Based Tools for Multi-Project Management

**Problem**: CDE Orchestrator manages 1000+ projects. Anthropic recommends filesystem-based tool discovery, but where should `./servers/cde/` live?

**Solution**: Single **GLOBAL** `./servers/cde/` directory in CDE Orchestrator repository. Tools accept `project_path` to operate on any project.

---

## 🎯 Architecture Decision

### Option 1: Global `./servers/cde/` (✅ CHOSEN)

```
E:\scripts-python\CDE Orchestrator MCP\
├── src\
│   ├── server.py
│   └── mcp_tools\
├── servers\                     # NEW: Global tool filesystem
│   └── cde\
│       ├── __init__.py
│       ├── scanDocumentation.py
│       ├── sourceSkill.py
│       ├── selectWorkflow.py
│       └── ... (40+ tools)
└── .cde\
    └── state.json               # CDE's own state
```

**Usage by agents managing other projects**:

```python
# Agent managing project "E:\my-app"
from servers.cde import scanDocumentation

result = await scanDocumentation(project_path="E:\\my-app")
# Scans E:\my-app\docs\, not CDE Orchestrator's docs
```

**Pros**:
- ✅ Single source of truth for tool definitions
- ✅ Works with ANY project (1000+ projects managed from one place)
- ✅ Agents discover tools ONCE, use them on all projects
- ✅ Updates to tools automatically apply to all projects
- ✅ Matches CDE's stateless philosophy (tools are project-agnostic)

**Cons**:
- ⚠️ Requires `project_path` parameter on all tools (already done!)
- ⚠️ Adds `./servers/` to CDE Orchestrator repo (minimal overhead)

### Option 2: Per-Project `./servers/cde/` (❌ REJECTED)

```
E:\my-app\
├── .cde\
│   ├── state.json
│   └── servers\               # Tool definitions copied here
│       └── cde\
│           └── ... (40+ files)
```

**Pros**:
- ✅ Tools live with project state

**Cons**:
- ❌ Must copy 40+ tool files to EVERY project (1000+ projects = 40,000 files!)
- ❌ Tool updates require regenerating in all projects
- ❌ Violates DRY principle
- ❌ Agents must re-discover tools for each project (defeats progressive disclosure)
- ❌ Storage overhead (40 * 1000 = 40MB wasted)

---

## 📐 Design Pattern: Tools as Pure Functions

All MCP tools follow this pattern:

```python
# ./servers/cde/scanDocumentation.py
"""
Scan and analyze documentation structure in a project.

Parameters:
    project_path (str): Path to project root (default: ".")

Returns:
    JSON with total_docs, missing_metadata, recommendations

Example:
    >>> from servers.cde import scanDocumentation
    >>> result = await scanDocumentation(project_path="E:\\my-app")
"""

from cde_orchestrator.mcp_client import call_mcp_tool
from typing import Dict, Any

async def scanDocumentation(
    project_path: str = "."
) -> Dict[str, Any]:
    """
    Scan and analyze documentation structure in a project.
    """
    return await call_mcp_tool("cde_scanDocumentation", {
        "project_path": project_path
    })
```

**Key Properties**:
1. **Stateless**: No internal state, operates on external project
2. **Pure**: Same inputs = same outputs
3. **Project-agnostic**: Works with any project via `project_path`
4. **Typed**: Clear parameter/return types for LLM comprehension

---

## 🔄 Workflow: Multi-Project Management

### Scenario: Agent Managing 3 Projects Simultaneously

```python
# Agent discovers tools ONCE (global ./servers/cde/)
import os
servers = os.listdir('./servers/')  # ['cde']
tools = os.listdir('./servers/cde/')  # ['scanDocumentation.py', 'sourceSkill.py', ...]

# Import tools
from servers.cde import scanDocumentation, sourceSkill, selectWorkflow

# Operate on Project 1
proj1_docs = await scanDocumentation(project_path="E:\\my-app")
# Returns: {"total_docs": 45, "missing_metadata": [...]}

# Operate on Project 2
proj2_docs = await scanDocumentation(project_path="E:\\other-app")
# Returns: {"total_docs": 78, "missing_metadata": [...]}

# Operate on Project 3
proj3_workflow = await selectWorkflow(
    project_path="E:\\third-app",
    user_prompt="Add authentication"
)
# Returns: {"workflow_type": "standard", "recipe_id": "ai-engineer"}
```

**Token Efficiency**:
- **WITHOUT filesystem tools**: 150,000 tokens × 3 projects = 450,000 tokens
- **WITH filesystem tools**: 2,000 tokens (discover once) + 3 × minimal ops = ~5,000 tokens
- **Reduction**: 98.9%

---

## 🛠️ Implementation Strategy

### Phase 1: Generate Global `./servers/cde/`

```python
# NEW: src/cde_orchestrator/infrastructure/tool_filesystem_generator.py

from pathlib import Path
from typing import List, Dict
import inspect

class ToolFilesystemGenerator:
    """Generate ./servers/cde/ from MCP tools."""

    def __init__(self, mcp_tools_module):
        self.mcp_tools = mcp_tools_module
        self.output_dir = Path(__file__).parent.parent.parent.parent / "servers" / "cde"

    def generate_all(self):
        """Generate filesystem structure for all MCP tools."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        tools = self._discover_tools()

        for tool in tools:
            self._write_tool_file(tool)

        self._write_index_file(tools)

    def _discover_tools(self) -> List[Dict]:
        """Discover all MCP tools from mcp_tools package."""
        from mcp_tools import __all__

        tools = []
        for tool_name in __all__:
            tool_func = getattr(self.mcp_tools, tool_name)

            # Extract metadata
            sig = inspect.signature(tool_func)
            doc = inspect.getdoc(tool_func) or "No description"

            tools.append({
                "name": tool_name.replace("cde_", ""),  # Remove prefix
                "full_name": tool_name,
                "signature": str(sig),
                "docstring": doc,
                "parameters": [
                    {
                        "name": p.name,
                        "type": str(p.annotation) if p.annotation != inspect.Parameter.empty else "Any",
                        "default": str(p.default) if p.default != inspect.Parameter.empty else None
                    }
                    for p in sig.parameters.values()
                ]
            })

        return tools

    def _write_tool_file(self, tool: Dict):
        """Write individual tool as importable function."""
        params = ", ".join(
            f"{p['name']}: {p['type']}" + (f" = {p['default']}" if p['default'] else "")
            for p in tool["parameters"]
        )

        content = f'''"""
{tool['docstring']}
"""

from cde_orchestrator.mcp_client import call_mcp_tool
from typing import Dict, Any

async def {tool['name']}({params}) -> Dict[str, Any]:
    """
    {tool['docstring'].split(chr(10))[0]}
    """
    return await call_mcp_tool("{tool['full_name']}", {{
        {chr(10).join(f'        "{p["name"]}": {p["name"]},' for p in tool["parameters"])}
    }})
'''

        path = self.output_dir / f"{tool['name']}.py"
        path.write_text(content, encoding="utf-8")

    def _write_index_file(self, tools: List[Dict]):
        """Write __init__.py with exports."""
        imports = [f"from .{t['name']} import {t['name']}" for t in tools]
        all_list = [f'    "{t["name"]}"' for t in tools]

        content = f'''"""
CDE Orchestrator MCP Tools (Filesystem-Based Discovery)

This module provides progressive tool disclosure following Anthropic's
code execution with MCP best practices.

Available tools:
{chr(10).join(f"    - {t['name']}: {t['docstring'].split(chr(10))[0]}" for t in tools)}

Usage:
    >>> import os
    >>> tools = os.listdir('./servers/cde/')  # Discover available tools
    >>>
    >>> from servers.cde import scanDocumentation
    >>> result = await scanDocumentation(project_path="E:\\\\my-app")
"""

{chr(10).join(imports)}

__all__ = [
{chr(10).join(all_list)}
]
'''

        path = self.output_dir / "__init__.py"
        path.write_text(content, encoding="utf-8")
```

### Phase 2: Auto-Generate on Server Startup

```python
# src/server.py (modified)

import logging
import os

from dotenv import load_dotenv
from fastmcp import FastMCP

from mcp_tools import (
    # ... existing imports
)

# NEW: Auto-generate filesystem tools
from cde_orchestrator.infrastructure.tool_filesystem_generator import ToolFilesystemGenerator
import mcp_tools

# Generate ./servers/cde/ on startup
logger.info("Generating filesystem-based tool discovery structure...")
generator = ToolFilesystemGenerator(mcp_tools)
generator.generate_all()
logger.info("✅ ./servers/cde/ generated with progressive disclosure support")

# Configuration
load_dotenv()
logging.basicConfig(level=os.environ.get("CDE_LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# ... rest of server.py
```

**Benefits**:
- ✅ Always up-to-date (regenerated on every startup)
- ✅ No manual maintenance
- ✅ Works with new tools automatically

---

## 📊 Scalability Analysis

### Managing 1000+ Projects

**Scenario**: Agent managing 1000 projects simultaneously

**WITHOUT filesystem tools**:
- Load all 40 tools × 1000 projects = 40,000 tool loads
- Context per operation: 150,000 tokens × 1000 = 150M tokens
- Cost: ~$300 per batch operation (at $2/M tokens)

**WITH filesystem tools** (Global `./servers/cde/`):
- Discover tools ONCE: 2,000 tokens
- Operations on 1000 projects: ~5,000 tokens each = 5M tokens total
- Cost: ~$10 per batch operation
- **Savings**: 97% cost reduction

**Storage**:
- Global approach: 40 files × 10KB = 400KB
- Per-project approach: 40 files × 10KB × 1000 = 40MB
- **Savings**: 99% storage reduction

---

## 🔒 Security Considerations

### Path Validation

All tools MUST validate `project_path` parameter:

```python
def validate_project_path(project_path: str) -> Path:
    """
    Validate project path for security.

    Raises:
        ValueError: If path is invalid or malicious
    """
    path = Path(project_path).resolve()

    # Prevent path traversal
    if ".." in str(path):
        raise ValueError("Path traversal detected")

    # Ensure path exists
    if not path.exists():
        raise ValueError(f"Project path does not exist: {path}")

    # Ensure it's a directory
    if not path.is_dir():
        raise ValueError(f"Project path must be a directory: {path}")

    return path
```

### Sandboxing (Future)

For code execution (Phase 3), implement sandboxing:
- Run agent code in isolated container
- Restrict filesystem access to project path only
- Resource limits (CPU, memory, time)
- Network isolation for sensitive data

---

## 🎯 Acceptance Criteria

### Phase 1 Complete When:

- [ ] `./servers/cde/` exists in CDE Orchestrator repo
- [ ] Contains one `.py` file per MCP tool (40+ files)
- [ ] `__init__.py` exports all tools
- [ ] Auto-regenerated on server startup
- [ ] All tools accept `project_path` parameter
- [ ] Agents can import: `from servers.cde import scanDocumentation`
- [ ] Works with multiple projects simultaneously
- [ ] Documentation updated with examples

### Token Reduction Verified:

- [ ] Benchmark: Tool discovery without filesystem = 150,000 tokens
- [ ] Benchmark: Tool discovery with filesystem = 2,000 tokens
- [ ] Reduction: ≥98% achieved
- [ ] Multi-project scenario tested (3+ projects)

---

## 📚 Documentation Updates

### Files to Update:

1. **AGENTS.md** - Add section on filesystem-based tool discovery
2. **README.md** - Add performance metrics
3. **docs/mcp-tools-manual.md** - Add progressive disclosure examples
4. **specs/governance/DOCUMENTATION_GOVERNANCE.md** - Clarify that `./servers/` is infrastructure

### Example for AGENTS.md:

```markdown
## 🔍 Tool Discovery (Anthropic Best Practice)

CDE Orchestrator uses **filesystem-based tool discovery** for 98.7% token reduction.

### Progressive Disclosure Pattern

**Step 1: Discover available tools**
\`\`\`python
import os
tools = os.listdir('./servers/cde/')
# ['scanDocumentation.py', 'sourceSkill.py', 'selectWorkflow.py', ...]
\`\`\`

**Step 2: Read only tools you need**
\`\`\`python
with open('./servers/cde/scanDocumentation.py') as f:
    tool_def = f.read()  # See signature and docstring
\`\`\`

**Step 3: Import and use**
\`\`\`python
from servers.cde import scanDocumentation

# Operate on ANY project
result = await scanDocumentation(project_path="E:\\\\my-app")
\`\`\`

### Multi-Project Management

\`\`\`python
# Manage 3 projects with SINGLE tool discovery
from servers.cde import scanDocumentation, sourceSkill

proj1 = await scanDocumentation(project_path="E:\\\\app1")
proj2 = await scanDocumentation(project_path="E:\\\\app2")
proj3 = await scanDocumentation(project_path="E:\\\\app3")
\`\`\`

**Token Efficiency**:
- WITHOUT: 150,000 tokens × 3 = 450,000 tokens
- WITH: 2,000 tokens + 3 × ops = ~5,000 tokens
- **Reduction**: 98.9%
```

---

## 🚀 Next Steps

1. Implement `ToolFilesystemGenerator` class
2. Integrate into `server.py` startup
3. Run generation and verify structure
4. Update documentation
5. Benchmark token usage
6. Proceed to Phase 1 remaining tasks (detail_level, searchTools)

---

*End of Design Document*
