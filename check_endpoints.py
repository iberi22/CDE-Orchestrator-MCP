#!/usr/bin/env python3
"""Check if HTTP and WebSocket endpoints are listening."""

import json
import socket


def is_port_open(port):
    """Check if port is listening."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("localhost", port))
    sock.close()
    return result == 0


def test_http_endpoint():
    """Test HTTP endpoint with a progress event."""
    try:
        import urllib.request

        event = {
            "server": "CDE",
            "tool": "test",
            "percentage": 0.5,
            "elapsed": 0,
            "message": "Test",
        }

        data = json.dumps(event).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:8767/progress",
            data=data,
            headers={"Content-Type": "application/json"},
        )

        response = urllib.request.urlopen(req, timeout=1)
        status = response.status
        response.close()
        return status == 200
    except Exception:
        return False


print("🔍 Checking endpoints...\n")

# WebSocket
print("📡 WebSocket (8766):", end=" ")
if is_port_open(8766):
    print("✅ LISTENING")
else:
    print("❌ NOT LISTENING")

# HTTP
print("🌐 HTTP (8767):     ", end=" ")
if is_port_open(8767):
    print("✅ LISTENING")
else:
    print("❌ NOT LISTENING")

# Test HTTP
print("\n🧪 Testing HTTP endpoint...", end=" ")
if test_http_endpoint():
    print("✅ Responding")
else:
    print("❌ Not responding")

print("\n✅ Check complete")
