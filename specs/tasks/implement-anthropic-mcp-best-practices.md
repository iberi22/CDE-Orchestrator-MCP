---
title: "Task: Implement Anthropic MCP Best Practices"
description: "Actionable tasks to implement filesystem-based tool discovery and progressive disclosure patterns"
type: "task"
status: "draft"
created: "2025-11-09"
updated: "2025-11-09"
author: "GitHub Copilot"
related_research: "agent-docs/research/research-anthropic-mcp-code-execution-2025-11-09.md"
---

# Task: Implement Anthropic MCP Best Practices

**Research Source**: `agent-docs/research/research-anthropic-mcp-code-execution-2025-11-09.md`

**Goal**: Achieve 90%+ token reduction by implementing progressive disclosure and filesystem-based tool discovery patterns.

---

## Phase 1: Quick Wins (1-2 Days) 🔴 HIGH PRIORITY

### TASK-MCP-01: Add Progressive Detail Levels to Existing Tools

**Effort**: 4-6 hours | **Priority**: 🔴 CRITICAL

**Description**: Add `detail_level` parameter to existing MCP tools to reduce token consumption.

**Implementation**:

1. **Update `cde_scanDocumentation`**:

```python
@mcp.tool()
def cde_scanDocumentation(
    project_path: str = ".",
    detail_level: str = "summary"  # NEW PARAMETER
) -> str:
    """
    Args:
        detail_level: "name_only" | "summary" | "full"
            - name_only: Just file paths (10 tokens/file)
            - summary: Paths + titles + types (50 tokens/file)
            - full: Complete metadata + preview (500 tokens/file)
    """
```

2. **Update `cde_sourceSkill`**:

```python
@mcp.tool()
def cde_sourceSkill(
    skill_query: str,
    source: str = "awesome-claude-skills",
    destination: str = "base",
    detail_level: str = "summary"  # NEW PARAMETER
) -> str:
    """
    Args:
        detail_level: "name_only" | "summary" | "full"
            - name_only: Just skill names (5 tokens/skill)
            - summary: Names + descriptions (100 tokens/skill)
            - full: Complete skill content (5000 tokens/skill)
    """
```

3. **Update `cde_getProjectInfo`**:

```python
@mcp.tool()
def cde_getProjectInfo(
    project_path: Optional[str] = None,
    project_name: Optional[str] = None,
    detail_level: str = "basic"  # NEW PARAMETER
) -> str:
    """
    Args:
        detail_level: "basic" | "detailed"
            - basic: path, exists, has_git (50 tokens)
            - detailed: + file count, last commit, dependencies (200 tokens)
    """
```

**Files Modified**:
- `src/cde_orchestrator/server.py` (+100 lines)
- `src/cde_orchestrator/adapters/filesystem_project_repository.py` (+50 lines)

**Tests**:
- `tests/unit/test_progressive_disclosure.py` (new file)

**Acceptance Criteria**:

```python
def test_scan_documentation_name_only():
    result = cde_scanDocumentation(detail_level="name_only")
    data = json.loads(result)

    # Should only contain file paths
    assert "files" in data
    assert all(isinstance(f, str) for f in data["files"])

    # Token estimate should be ~10 per file
    estimated_tokens = len(data["files"]) * 10
    assert estimated_tokens < 500  # vs 5000 with full details

def test_source_skill_summary():
    result = cde_sourceSkill("redis", detail_level="summary")
    data = json.loads(result)

    # Should contain summaries, not full content
    assert "skills_downloaded" in data
    for skill in data["skills_downloaded"]:
        assert "name" in skill
        assert "description" in skill
        assert "content" not in skill  # Full content excluded
```

**Expected Impact**: 80% token reduction for common workflows

---

### TASK-MCP-02: Implement `cde_searchTools` MCP Tool

**Effort**: 3-4 hours | **Priority**: 🔴 CRITICAL

**Description**: Add tool discovery via search instead of loading all tools upfront.

**Implementation**:

```python
# File: src/cde_orchestrator/adapters/mcp_tool_search.py

from typing import List, Dict, Literal
import inspect

DetailLevel = Literal["name_only", "name_and_description", "full_schema"]

class MCPToolSearcher:
    """Search MCP tools by keyword (Anthropic pattern)."""

    def __init__(self, server_module):
        self.tools = self._discover_tools(server_module)

    def search(
        self,
        query: str,
        detail_level: DetailLevel = "name_and_description"
    ) -> Dict:
        """
        Search tools by keyword.

        Returns:
            {
                "tools": [...],
                "total": int,
                "detail_level": str
            }
        """
        matches = [
            tool for tool in self.tools
            if query.lower() in tool["name"].lower()
            or query.lower() in tool["description"].lower()
        ]

        return {
            "tools": self._format_results(matches, detail_level),
            "total": len(matches),
            "detail_level": detail_level
        }

    def _format_results(self, tools: List[Dict], level: DetailLevel):
        if level == "name_only":
            return [t["name"] for t in tools]

        elif level == "name_and_description":
            return [
                {"name": t["name"], "description": t["description"]}
                for t in tools
            ]

        else:  # full_schema
            return tools
```

```python
# File: src/cde_orchestrator/server.py (add new tool)

@mcp.tool()
def cde_searchTools(
    query: str,
    detail_level: str = "name_and_description"
) -> str:
    """
    Search available CDE tools by keyword.

    Args:
        query: Search keywords (e.g., "skill", "workflow", "project")
        detail_level: "name_only" | "name_and_description" | "full_schema"

    Returns:
        JSON with matching tools.

    Examples:
        >>> cde_searchTools("skill", detail_level="name_only")
        {"tools": ["cde_sourceSkill", "cde_updateSkill"], "total": 2}
    """
    from cde_orchestrator.adapters.mcp_tool_search import MCPToolSearcher
    import sys

    searcher = MCPToolSearcher(sys.modules[__name__])
    results = searcher.search(query, detail_level)
    return json.dumps(results, indent=2)
```

**Files Modified**:
- `src/cde_orchestrator/adapters/mcp_tool_search.py` (NEW, +150 lines)
- `src/cde_orchestrator/server.py` (+30 lines)

**Tests**:
- `tests/unit/test_mcp_tool_search.py` (new file)

**Acceptance Criteria**:

```python
def test_search_tools_name_only():
    result = cde_searchTools("skill", detail_level="name_only")
    data = json.loads(result)

    assert data["tools"] == ["cde_sourceSkill", "cde_updateSkill"]
    assert data["total"] == 2

def test_search_tools_with_description():
    result = cde_searchTools("workflow", detail_level="name_and_description")
    data = json.loads(result)

    assert len(data["tools"]) >= 2
    assert all("name" in t and "description" in t for t in data["tools"])
```

**Expected Impact**: 85% token reduction when discovering tools

---

## Phase 2: Filesystem-Based Tool Discovery (3-5 Days) 🟡 MEDIUM PRIORITY

### TASK-MCP-03: Generate `./servers/cde/` Filesystem Structure

**Effort**: 2-3 days | **Priority**: 🟡 HIGH

**Description**: Auto-generate filesystem representation of MCP tools for progressive discovery.

**Implementation**:

```python
# File: src/cde_orchestrator/adapters/mcp_tool_filesystem.py

from pathlib import Path
from typing import Dict, List
import inspect
import ast

class MCPToolFilesystemGenerator:
    """Generate filesystem structure for MCP tools (Anthropic pattern)."""

    def generate(self, server_module, output_dir: Path):
        """
        Generate ./servers/cde/ with one file per tool.

        Structure:
            servers/
            ├── cde/
            │   ├── __init__.py
            │   ├── startFeature.py
            │   ├── submitWork.py
            │   ├── sourceSkill.py
            │   └── ...
        """
        cde_dir = output_dir / "servers" / "cde"
        cde_dir.mkdir(parents=True, exist_ok=True)

        tools = self._discover_tools(server_module)

        for tool in tools:
            self._write_tool_file(cde_dir / f"{tool['name']}.py", tool)

        self._write_index_file(cde_dir, tools)

    def _write_tool_file(self, path: Path, tool: Dict):
        """Write individual tool as importable function."""
        params = self._format_parameters(tool["parameters"])

        content = f'''"""
{tool['description']}

Parameters:
{params}

Example:
    >>> from servers.cde import {tool['name']}
    >>> result = await {tool['name']}(...)
"""

from cde_orchestrator.mcp_client import call_mcp_tool
from typing import Dict, Any

async def {tool['name']}(**kwargs) -> Dict[str, Any]:
    """
    {tool['description']}
    """
    return await call_mcp_tool("{tool['name']}", kwargs)
'''
        path.write_text(content)

    def _write_index_file(self, cde_dir: Path, tools: List[Dict]):
        """Write __init__.py with all exports."""
        exports = [f"from .{t['name']} import {t['name']}" for t in tools]
        all_list = [f'    "{t["name"]}"' for t in tools]

        content = f'''"""
CDE Orchestrator MCP Tools

Available tools:
{chr(10).join(f"    - {t['name']}: {t['description']}" for t in tools)}
"""

{chr(10).join(exports)}

__all__ = [
{chr(10).join(all_list)}
]
'''
        (cde_dir / "__init__.py").write_text(content)
```

**Files Modified**:
- `src/cde_orchestrator/adapters/mcp_tool_filesystem.py` (NEW, +250 lines)
- `src/cde_orchestrator/infrastructure/di_container.py` (+20 lines)

**Tests**:
- `tests/integration/test_filesystem_tool_discovery.py` (new file)

**Acceptance Criteria**:

```python
def test_generate_filesystem_structure():
    generator = MCPToolFilesystemGenerator()
    output_dir = Path("/tmp/test_cde")

    generator.generate(server_module, output_dir)

    # Verify structure
    assert (output_dir / "servers" / "cde" / "__init__.py").exists()
    assert (output_dir / "servers" / "cde" / "startFeature.py").exists()
    assert (output_dir / "servers" / "cde" / "sourceSkill.py").exists()

    # Verify importable
    import sys
    sys.path.insert(0, str(output_dir))
    from servers.cde import startFeature, sourceSkill

    assert callable(startFeature)
    assert callable(sourceSkill)
```

**Expected Impact**: 90%+ token reduction when agent loads only needed tools

---

### TASK-MCP-04: Update Documentation for Filesystem Pattern

**Effort**: 4-6 hours | **Priority**: 🟡 MEDIUM

**Description**: Update agent-facing documentation with filesystem discovery examples.

**Files to Update**:

1. **`AGENTS.md`** - Add section on progressive tool discovery:

```markdown
## 🔍 Tool Discovery Patterns (Anthropic Best Practice)

### Progressive Disclosure

Instead of loading all 40+ tools upfront, agents should discover tools on-demand:

**Pattern 1: Filesystem Navigation**
\`\`\`python
import os

# Discover available tool categories
servers = os.listdir('./servers/')  # ['cde']

# List tools in category
tools = os.listdir('./servers/cde/')  # ['startFeature.py', 'submitWork.py', ...]

# Read tool definition
with open('./servers/cde/sourceSkill.py') as f:
    tool_def = f.read()  # See function signature and docstring

# Import and use
from servers.cde import sourceSkill
result = await sourceSkill(skill_query="redis", destination="base")
\`\`\`

**Pattern 2: Search Tools**
\`\`\`python
# Search for relevant tools
result = cde_searchTools("skill", detail_level="name_only")
# Returns: ["cde_sourceSkill", "cde_updateSkill"]

# Get descriptions
result = cde_searchTools("skill", detail_level="name_and_description")
# Returns: [{"name": "cde_sourceSkill", "description": "..."}]
\`\`\`

**Token Impact**: 90%+ reduction (150,000 → 2,000 tokens)
```

2. **`docs/mcp-tools-manual.md`** - Add progressive detail levels section

3. **`README.md`** - Update performance metrics

**Acceptance Criteria**:
- [ ] All examples tested with real MCP tools
- [ ] Token reduction benchmarks documented
- [ ] Links to Anthropic research article included

---

## Phase 3: Advanced Optimizations (5-7 Days) 🟢 LOW PRIORITY

### TASK-MCP-05: Implement Batch Workflow Execution

**Effort**: 2-3 days | **Priority**: 🟢 MEDIUM

**Description**: Execute multiple workflow phases in server without model round-trips.

**Implementation**:

```python
@mcp.tool()
def cde_executeWorkflowBatch(
    feature_id: str,
    phases: List[str],
    auto_advance: bool = True
) -> str:
    """
    Execute multiple workflow phases in a batch (Anthropic pattern).

    Saves model round-trips and latency.

    Args:
        feature_id: Feature UUID
        phases: Phases to execute (e.g., ["define", "decompose", "design"])
        auto_advance: Continue on success, stop on error

    Returns:
        JSON with results for each phase.
    """
    use_case = container.get_execute_workflow_batch_use_case()

    results = []
    for phase_id in phases:
        result = use_case.execute(feature_id, phase_id)
        results.append({
            "phase": phase_id,
            "status": result["status"],
            "artifacts": result.get("artifacts", [])
        })

        if result["status"] == "error" and not auto_advance:
            break

    return json.dumps({"results": results}, indent=2)
```

**Expected Impact**: 3x faster for multi-phase workflows

---

### TASK-MCP-06: Add PII Tokenization Layer (Optional)

**Effort**: 2-3 days | **Priority**: 🟢 LOW

**Description**: Implement automatic PII tokenization (file paths, API keys).

**Implementation**: See `agent-docs/research/research-anthropic-mcp-code-execution-2025-11-09.md` Section "Priority 4"

**Expected Impact**: Prevents accidental PII leakage in logs

---

## Phase 4: Validation & Benchmarking (2 Days)

### TASK-MCP-07: Token Usage Benchmarks

**Effort**: 1 day | **Priority**: 🔴 CRITICAL

**Description**: Measure token reduction before/after optimizations.

**Benchmark Scenarios**:

1. **Scenario 1: Tool Discovery**
   - Before: Load all 40 tools upfront → 150,000 tokens
   - After: Progressive discovery → 2,000 tokens
   - Target: 98.7% reduction

2. **Scenario 2: Documentation Scan**
   - Before: Return all 100 files with full content → 50,000 tokens
   - After: Return names only → 1,000 tokens
   - Target: 98% reduction

3. **Scenario 3: Skill Sourcing**
   - Before: Return 3 full skills → 15,000 tokens
   - After: Return summaries → 300 tokens
   - Target: 98% reduction

**Files to Create**:
- `tests/benchmarks/token_usage_comparison.py` (new file)

**Output**: Update `README.md` with benchmark results

---

### TASK-MCP-08: Update Performance Metrics in README

**Effort**: 2-3 hours | **Priority**: 🟡 MEDIUM

**Description**: Document token reduction improvements.

**Add to README.md**:

```markdown
## ⚡ Performance

**Token Efficiency** (Following [Anthropic's MCP Best Practices](https://www.anthropic.com/engineering/code-execution-with-mcp)):

| Operation | Before Optimization | After Optimization | Reduction |
|-----------|--------------------|--------------------|-----------|
| Tool Discovery | 150,000 tokens | 2,000 tokens | 98.7% |
| Documentation Scan | 50,000 tokens | 1,000 tokens | 98% |
| Skill Sourcing | 15,000 tokens | 300 tokens | 98% |

**Patterns Implemented**:
- ✅ Progressive disclosure (filesystem-based tool discovery)
- ✅ Context-efficient data filtering (detail levels)
- ✅ Tool search with progressive detail
- ✅ State persistence and skills (DSMS)
```

---

## Summary

**Total Effort**: 10-14 days
**Expected Token Reduction**: 90-98%
**Priority Order**: Phase 1 → Phase 4 → Phase 2 → Phase 3

**Next Actions**:
1. Create GitHub issues for Phase 1 tasks
2. Assign to team members
3. Set up benchmarking infrastructure
4. Implement and test progressively

---

*End of Task Document*
