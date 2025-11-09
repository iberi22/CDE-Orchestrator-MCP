#!/usr/bin/env python3
"""
Diagnostic script to test MCP progress communication chain.

Tests:
1. Proxy HTTP server on port 8767
2. VS Code extension HTTP server on port 8768
3. End-to-end progress event flow
"""

import json
import sys
import urllib.request


def test_proxy_server() -> bool:
    """Test if proxy is listening on 8767"""
    print("🔍 Testing proxy server on port 8767...")
    try:
        event = {
            "server": "CDE",
            "tool": "test",
            "percentage": 0.5,
            "elapsed": 1.5,
            "message": "Testing communication",
        }
        data = json.dumps(event).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:8767/progress",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        response = urllib.request.urlopen(req, timeout=2)
        result = json.loads(response.read().decode("utf-8"))
        response.close()
        print(f"✅ Proxy responding on 8767: {result}")
        return True
    except Exception as e:
        print(f"❌ Proxy not responding on 8767: {e}")
        return False


def test_vscode_extension() -> bool:
    """Test if VS Code extension is listening on 8768"""
    print("\n🔍 Testing VS Code extension on port 8768...")
    try:
        event = {
            "server": "CDE",
            "tool": "test",
            "percentage": 0.75,
            "elapsed": 2.5,
            "message": "Testing VS Code communication",
        }
        data = json.dumps(event).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:8768/progress",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        response = urllib.request.urlopen(req, timeout=2)
        result = json.loads(response.read().decode("utf-8"))
        response.close()
        print(f"✅ VS Code extension responding on 8768: {result}")
        return True
    except Exception as e:
        print(f"❌ VS Code extension not responding on 8768: {e}")
        return False


def main() -> None:
    print("=" * 60)
    print("MCP PROGRESS COMMUNICATION DIAGNOSTIC")
    print("=" * 60)

    proxy_ok = test_proxy_server()
    vscode_ok = test_vscode_extension()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Proxy (8767):        {'✅ OK' if proxy_ok else '❌ FAIL'}")
    print(f"VS Code (8768):      {'✅ OK' if vscode_ok else '❌ FAIL'}")

    if proxy_ok and vscode_ok:
        print("\n🎉 COMMUNICATION WORKING! Progress should display in status bar.")
        sys.exit(0)
    elif proxy_ok and not vscode_ok:
        print("\n⚠️ Proxy OK but VS Code extension not responding.")
        print("   → Make sure extension is activated (check Output panel)")
        print("   → Try reloading VS Code window (Ctrl+Shift+P → Reload Window)")
        sys.exit(1)
    else:
        print("\n❌ Proxy not responding. Check if mcp_proxy.py is running.")
        print(
            "   → Run: python mcp-monitor/proxy/mcp_proxy.py CDE python src/server.py"
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
