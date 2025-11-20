"""
Test script to send progress events directly to VS Code extension HTTP server.
This bypasses the proxy to isolate the issue.
"""

import json
import time
import urllib.error
import urllib.request


def send_progress(percentage: float, message: str) -> bool:
    event = {
        "server": "CDE",
        "tool": "direct_test",
        "percentage": percentage,
        "elapsed": percentage * 5,
        "message": message,
    }

    data = json.dumps(event).encode("utf-8")
    req = urllib.request.Request(
        "http://localhost:8768/progress",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    try:
        response = urllib.request.urlopen(req, timeout=10)
        result = response.read().decode("utf-8")
        print(f"✅ {int(percentage * 100)}% → {result}")
        response.close()
        return True
    except urllib.error.URLError as e:
        print(f"❌ {int(percentage * 100)}% → Error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing direct connection to VS Code extension (port 8768)...\n")

    # Test with 5 progress steps
    for i in range(6):
        percentage = i / 5
        message = f"Step {i}/5"

        print(f"Sending: {message} ({int(percentage * 100)}%)")
        success = send_progress(percentage, message)

        if not success and i == 0:
            print("\n⚠️ Extension HTTP server not responding!")
            print("Make sure:")
            print("  1. VS Code is running")
            print("  2. MCP Status Bar extension is installed and activated")
            print(
                "  3. Extension activated successfully (check Developer Tools console)"
            )
            break

        time.sleep(1)

    print("\n✅ Test completed!")
