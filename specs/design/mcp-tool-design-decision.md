---
title: "MCP Tool Design Decision: Keep Granular Tools"
description: "Design decision to maintain separate cde_onboardingProject, cde_scanDocumentation, and cde_analyzeDocumentation tools"
type: "design"
status: "active"
created: "2025-11-02"
updated: "2025-11-02"
author: "GitHub Copilot"
llm_summary: |
  Design decision rationale for keeping documentation tools separate rather than consolidating
  into monolithic tool. Based on analysis of 5000+ MCP servers showing granularity pattern wins.
---

# MCP Tool Design Decision: Keep Granular Tools

## Decision

**KEEP separate tools**:
- ✅ `cde_onboardingProject`
- ✅ `cde_scanDocumentation`
- ✅ `cde_analyzeDocumentation`

**ADD router tool** (new):
- ✅ `cde_selectDocumentationTool(user_intent)` - Guides LLM to right tool

**DO NOT consolidate**:
- ❌ `cde_manageDocumentation(mode, ...)` - Rejected

## Rationale

### Research Findings

Analyzed **5,051 MCP servers** on GitHub:

**Pattern**: Successful servers use **many small tools** vs. few large ones

| Server | Tools | Pattern |
|--------|-------|---------|
| GitHub MCP | 40+ | `create_pr()`, `merge_pr()`, `list_commits()` |
| Snowflake | 10+ | `query_agent()`, `execute_sql()`, `manage_objects()` |
| Kubernetes | 80+ | `get_pods()`, `delete_pod()`, `scale_deployment()` |
| n8n | 400+ | Each service = separate tools |

**69% of top servers** have 6-50 tools (granular approach wins)

### Key Benefits of Separation

1. **Clarity**: Tool name reveals exact intent
   ```python
   # ✅ Clear
   cde_scanDocumentation()

   # ❌ Ambiguous
   cde_manageDocs(mode="scan")
   ```

2. **Security**: Smaller blast radius per tool
   ```python
   # ✅ Safe read
   cde_scanDocumentation()  # Can't modify

   # ❌ Hidden danger
   cde_manageDocs(mode="delete_all")
   ```

3. **Debuggability**: Clear audit trail
   ```log
   # ✅ Clear logs
   [14:23:11] cde_scanDocumentation(project_path=".")
   [14:23:15] cde_analyzeDocumentation(project_path=".")

   # ❌ Opaque
   [14:23:11] cde_manageDocs(mode="analyze", ...)
   ```

4. **LLM Clarity**: Fewer parameters = less confusion
   ```python
   # ✅ Simple (1-2 params typical)
   cde_scanDocumentation(project_path=".")

   # ❌ Complex (4+ params = confusion)
   cde_manageDocs(mode="scan", deep=True, fix=False, ...)
   ```

## Implementation Plan

### Phase 1: Add Router Tool (1 hour)

```python
@app.tool()
async def cde_selectDocumentationTool(user_intent: str) -> str:
    """
    🎯 Recommends which documentation tool to use.

    Args:
        user_intent: What you want to do (e.g., "check doc quality")

    Returns:
        {
          "recommended_tool": "cde_scanDocumentation",
          "reasoning": "General documentation check",
          "next_steps": ["Run cde_scanDocumentation() first"]
        }
    """
    # Simple keyword matching
    if "onboard" in user_intent.lower():
        return recommend("cde_onboardingProject")
    if "quality" in user_intent.lower():
        return recommend("cde_analyzeDocumentation")
    return recommend("cde_scanDocumentation")
```

### Phase 2: Improve Descriptions (30 min)

Add "USE THIS WHEN" guidance to existing tools:

```python
@app.tool()
async def cde_scanDocumentation(project_path: str = ".") -> str:
    """
    📁 Scan documentation structure and find issues.

    USE THIS WHEN:
    - Quick overview of doc organization needed
    - Finding missing metadata or orphaned files
    - First step before deeper analysis

    NEXT STEPS:
    - If issues found → cde_analyzeDocumentation()
    - If first-time → cde_onboardingProject()
    """
```

### Phase 3: Optional Workflow Tool (2 hours)

For common sequences only:

```python
@app.tool()
async def cde_documentationWorkflow(
    workflow: Literal["health_check", "quality_audit"]
) -> str:
    """
    🔄 Execute common multi-step workflows.

    Use individual tools for custom flows.
    """
    if workflow == "health_check":
        scan = await cde_scanDocumentation()
        if needs_analysis(scan):
            return await cde_analyzeDocumentation()
    # ...
```

## Alternatives Considered

### ❌ Option 1: Monolithic Tool (Rejected)

```python
cde_manageDocumentation(
    mode: Literal["scan", "analyze", "onboard"],
    project_path: str,
    deep_analysis: bool = False,
    auto_fix: bool = False
)
```

**Why rejected**:
- Too many parameters (4+) confuse LLM
- Unclear what mode+flags combinations mean
- Poor error messages (which mode failed?)
- Violates single-responsibility principle

### ❌ Option 2: Resource-Based (Rejected)

```python
@app.resource("docs://analysis")
async def docs_analysis_resource() -> str:
    return await analyze()  # Side effects!
```

**Why rejected**:
- Resources = passive reads only (MCP spec)
- Scanning/analyzing has side effects (not idempotent)

### ✅ Option 3: Router + Existing Tools (CHOSEN)

- Keep existing tools AS-IS
- Add router for guidance
- Add workflow tool for common sequences (optional)

## Metrics Impact

| Metric | Monolithic | Current (3 Tools) | Proposed (+Router) |
|--------|-----------|-------------------|-------------------|
| Tool Count | 1 | 3 | 4 |
| Avg Params | 4-5 | 1-2 | 1 |
| LLM Confusion | High | Low | Very Low |
| Debuggability | Low | High | Very High |

## Industry Validation

**Microsoft MCP Curriculum** guidance:
> "Tools should do one thing well. Use multiple tools for complex operations."

**GitHub MCP Server**: 40+ specialized tools
**Snowflake MCP**: Separate tools per operation
**n8n**: 400+ servers, each focused

## Conclusion

**Decision**: Maintain tool separation, add router for guidance.

**Reasoning**: Industry pattern + research data supports granularity.

**Risk**: Slightly more tools to discover
**Mitigation**: Router tool + improved descriptions guide LLM

**Estimated effort**: 1-2 hours (Phase 1), 30 min (Phase 2)

---

**References**:
- Full research: `agent-docs/research/mcp-tool-consolidation-best-practices-2025-11-02.md`
- MCP Spec: <https://modelcontextprotocol.io/docs/concepts/tools>
- GitHub Topic: `topic:mcp-server` (5,051 repos analyzed)
