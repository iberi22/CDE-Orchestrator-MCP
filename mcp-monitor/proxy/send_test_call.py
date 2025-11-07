#!/usr/bin/env python3
"""Quick test to send a tool call to the test server through the proxy."""

import json
import sys
import time

# Send initialize
init_msg = {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {}}
print(json.dumps(init_msg))
sys.stdout.flush()
time.sleep(0.5)

# Send tool call
tool_msg = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {"name": "scanDocumentation"},
}
print(json.dumps(tool_msg))
sys.stdout.flush()

# Wait for response
time.sleep(3)
