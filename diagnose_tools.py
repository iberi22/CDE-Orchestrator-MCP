#!/usr/bin/env python3
"""
Diagnostic Tool: Check MCP Tool Signatures
Verifies async/sync consistency across all MCP tools.
"""
import asyncio
import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


async def check_tool_signatures() -> bool:
    """Check all cde_* functions for async/sync consistency."""
    import mcp_tools
    from server import app

    # Get registered tools
    tools = await app.get_tools()
    print(f"[INFO] Total MCP tools registered: {len(tools)}\n")

    # Get all cde_* functions from mcp_tools module
    tool_functions = {
        name: getattr(mcp_tools, name)
        for name in dir(mcp_tools)
        if name.startswith("cde_") and callable(getattr(mcp_tools, name))
    }

    print("[INFO] Tool Signature Analysis:\n")
    print(f"{'Tool Name':<40} {'Type':<10} {'Registered':<12}")
    print("-" * 62)

    issues = []

    for name, func in sorted(tool_functions.items()):
        is_async = inspect.iscoroutinefunction(func)
        is_registered = name in tools
        func_type = "async" if is_async else "sync"
        reg_status = "OK" if is_registered else "X MISSING"

        print(f"{name:<40} {func_type:<10} {reg_status:<12}")

        if not is_registered:
            issues.append(f"Tool '{name}' not registered in FastMCP app")

    # Check for consistency issues
    print("\n[INFO] Summary:")
    print(f"  - Functions found: {len(tool_functions)}")
    print(f"  - Registered tools: {len(tools)}")
    print(
        f"  - Async functions: {sum(1 for f in tool_functions.values() if inspect.iscoroutinefunction(f))}"
    )
    print(
        f"  - Sync functions: {sum(1 for f in tool_functions.values() if not inspect.iscoroutinefunction(f))}"
    )

    if issues:
        print("\n[WARN] Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n[OK] No issues found")

    return len(issues) == 0


if __name__ == "__main__":
    success = asyncio.run(check_tool_signatures())
    sys.exit(0 if success else 1)
