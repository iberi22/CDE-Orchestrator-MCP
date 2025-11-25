---
title: "Performance Issues Found During Dogfooding"
type: "feedback"
date: "2025-11-24"
status: "active"
priority: "high"
---

# Performance Issues Found During Dogfooding

## Issue 1: `cde_scanDocumentation` Extremely Slow ⚠️

**Severity**: HIGH
**Impact**: 3+ minutes for scanning 100 files (should be <5 seconds)

### Root Cause
```python
# src/cde_orchestrator/application/documentation/scan_documentation_use_case.py:259-267
for idx, md_file in enumerate(md_files):
    # ... process file ...

    # ❌ PROBLEM: Reports progress after EVERY file
    progress = (idx + 1) / len(md_files)
    report_progress_http(
        "scanDocumentation",
        progress,
        f"Scanned {idx + 1}/{len(md_files)} files",
    )
```

### Why This is Slow
- Each `report_progress_http()` makes an HTTP request
- For 100 files = 100 HTTP requests
- HTTP overhead >> actual file scanning time
- Blocks on each progress report

### Solution
**Batch progress reporting** - only report every N files:

```python
# Report progress every 10 files or at completion
if (idx + 1) % 10 == 0 or (idx + 1) == len(md_files):
    progress = (idx + 1) / len(md_files)
    report_progress_http(
        "scanDocumentation",
        progress,
        f"Scanned {idx + 1}/{len(md_files)} files",
    )
```

**Expected Improvement**: 3 minutes → 5 seconds (36x faster)

---

## Issue 2: `cde_executeWithBestAgent` Checks All Agents Every Time ⚠️

**Severity**: MEDIUM
**Impact**: 2-5 seconds overhead per execution

### Root Cause
```python
# src/mcp_tools/agents.py:822-872
# Every time this tool is called:
jules_api_key = os.getenv("JULES_API_KEY")
if jules_api_key:
    if importlib.util.find_spec("jules_agent_sdk"):  # ❌ Slow import check
        # ...

# Then checks 6 CLI tools with shutil.which():
copilot_available = shutil.which("gh")  # ❌ Subprocess call
gemini_available = shutil.which("gemini")  # ❌ Subprocess call
qwen_available = shutil.which("qwen")  # ❌ Subprocess call
# ... 3 more ...
```

### Why This is Slow
- `importlib.util.find_spec()` scans Python path
- `shutil.which()` searches PATH directories
- Done for EVERY agent on EVERY execution
- No caching between calls

### Solution
**Agent availability cache** - check once, cache results:

```python
# .cde/agents.json (created during onboarding)
{
  "last_checked": "2025-11-24T16:00:00Z",
  "available_agents": ["jules", "copilot"],
  "unavailable_agents": ["gemini", "qwen", "deepagents", "codex", "rovodev"],
  "jules": {
    "api_key_configured": true,
    "sdk_installed": true,
    "cli_available": true
  },
  "copilot": {
    "cli_available": true,
    "gh_version": "2.40.0"
  }
}
```

**Expected Improvement**: 2-5 seconds → <100ms (20-50x faster)

---

## Issue 3: No Agent Memory System 💡

**Severity**: MEDIUM (Feature Request)
**Impact**: Workflow inefficiency

### Problem
- Every tool call re-discovers agents
- No persistent knowledge of what's available
- User has to manually specify agents
- Workflows can't auto-select based on availability

### Proposed Solution: Agent Onboarding System

#### 1. New Tool: `cde_detectAgents()`
```python
@tool_handler
async def cde_detectAgents(
    project_path: str = ".",
    force_refresh: bool = False
) -> str:
    """
    🔍 Detect and cache available AI agents.

    Checks for all supported agents and saves results to .cde/agents.json
    for fast lookup in workflows.

    Returns:
        JSON with detected agents and their capabilities
    """
```

#### 2. Cache File: `.cde/agents.json`
```json
{
  "version": "1.0",
  "last_checked": "2025-11-24T16:00:00Z",
  "project_path": "/path/to/project",
  "available_agents": [
    {
      "name": "jules",
      "type": "async_api",
      "status": "available",
      "capabilities": ["full_context", "plan_approval", "async"],
      "config": {
        "api_key_configured": true,
        "sdk_version": "1.2.3"
      }
    },
    {
      "name": "copilot",
      "type": "sync_cli",
      "status": "available",
      "capabilities": ["quick_suggestions", "code_generation"],
      "config": {
        "cli_version": "2.40.0",
        "extension_installed": true
      }
    }
  ],
  "unavailable_agents": [
    {
      "name": "gemini",
      "status": "not_installed",
      "install_command": "pip install gemini-cli"
    }
  ]
}
```

#### 3. Integration with Workflows
```python
# In cde_executeWithBestAgent:
def _load_agent_cache(project_path: str) -> Dict:
    cache_file = Path(project_path) / ".cde" / "agents.json"
    if cache_file.exists():
        # Check if cache is fresh (< 24 hours old)
        cache_age = time.time() - cache_file.stat().st_mtime
        if cache_age < 86400:  # 24 hours
            return json.loads(cache_file.read_text())

    # Cache miss or stale - run detection
    return _detect_and_cache_agents(project_path)
```

#### 4. Onboarding Integration
Add to `cde_setupProject()`:
```python
# After creating .gitignore, AGENTS.md, etc.
print("Detecting available AI agents...")
agent_result = await cde_detectAgents(project_path)
print(f"✅ Found {len(available_agents)} agents")
```

### Benefits
1. **Performance**: 20-50x faster agent selection
2. **User Experience**: One-time setup, persistent knowledge
3. **Workflow Intelligence**: Auto-select best agent
4. **Debugging**: Clear visibility of what's available
5. **Offline Support**: Works without re-checking CLIs

---

## Implementation Priority

1. **HIGH**: Fix `cde_scanDocumentation` progress reporting (5 min fix)
2. **HIGH**: Implement agent caching in `cde_executeWithBestAgent` (30 min)
3. **MEDIUM**: Create `cde_detectAgents()` tool (1 hour)
4. **MEDIUM**: Integrate with `cde_setupProject()` (30 min)

---

## Testing Plan

### Test 1: Scan Performance
```bash
# Before fix
time python scripts/run_dogfooding_suite.py T014
# Expected: 180+ seconds

# After fix
time python scripts/run_dogfooding_suite.py T014
# Expected: <5 seconds
```

### Test 2: Agent Selection Performance
```bash
# Before fix
time python scripts/run_dogfooding_suite.py T037
# Expected: 5+ seconds

# After fix (with cache)
time python scripts/run_dogfooding_suite.py T037
# Expected: <0.5 seconds
```

### Test 3: Agent Detection
```bash
# New tool
python -c "from mcp_tools.agents import cde_detectAgents; import asyncio; print(asyncio.run(cde_detectAgents()))"
# Should create .cde/agents.json
```

---

## Related Tasks

- [ ] T014: Test `cde_scanDocumentation` (blocked by performance fix)
- [ ] T037: Test `cde_executeWithBestAgent` (blocked by performance fix)
- [ ] NEW: Create `cde_detectAgents()` tool
- [ ] NEW: Update `cde_setupProject()` to run agent detection
- [ ] NEW: Add agent cache validation to `cde_healthCheck()`

---

## Notes

- Performance issues discovered during T014 execution (3+ minutes)
- User reported similar issues in another project (AdminCore)
- Agent detection is a common pattern needed across all projects
- Cache invalidation strategy: 24 hours or manual refresh
