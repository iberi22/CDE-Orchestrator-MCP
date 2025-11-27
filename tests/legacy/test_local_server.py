#!/usr/bin/env python3
"""
Test Local MCP Server - Sin Docker
Verifica que el servidor funciona localmente con todas sus dependencias.
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


async def test_server() -> bool:
    """Test MCP server locally."""
    print("[TEST] Testing Nexus AI MCP Server (Local)...\n")

    # 1. Import server
    try:
        from server import app

        print("[OK] Server module imported")
    except Exception as e:
        print(f"[FAIL] Failed to import server: {e}")
        return False

    # 2. Get tools
    try:
        tools = await app.get_tools()
        print(f"[OK] Registered {len(tools)} MCP tools")
    except Exception as e:
        print(f"[FAIL] Failed to get tools: {e}")
        return False

    # 3. List some tools
    print("\n[INFO] Sample Tools:")
    for i, tool_name in enumerate(list(tools.keys())[:10], 1):
        print(f"   {i}. {tool_name}")

    # 4. Test Rust module
    try:
        import cde_rust_core

        print("\n[OK] Rust module imported successfully")
        print(
            f"   Available functions: {len([x for x in dir(cde_rust_core) if not x.startswith('_')])}"
        )
    except Exception as e:
        print(f"\n[FAIL] Rust module import failed: {e}")
        return False

    # 5. Test a simple tool
    print("\n[TEST] Testing cde_checkRecipes tool...")
    try:
        import inspect

        from mcp_tools import cde_checkRecipes

        # Check if async
        if inspect.iscoroutinefunction(cde_checkRecipes):
            result = await cde_checkRecipes()
        else:
            result = cde_checkRecipes()

        import json

        check_data = json.loads(result)
        print("[OK] Tool execution passed")
        print(f"   Exists: {check_data.get('exists')}")
        print(f"   Path: {check_data.get('path')}")
    except Exception as e:
        print(f"[FAIL] Tool execution failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    print("\n[OK] All tests passed! Server is functional locally.")
    return True


if __name__ == "__main__":
    result = asyncio.run(test_server())
    sys.exit(0 if result else 1)
