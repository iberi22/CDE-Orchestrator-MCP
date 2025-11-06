# 🧪 Testing MCP Status Bar Extension

## ✅ What We've Done

1. ✅ Created VS Code extension (`mcp-status-bar/`)
2. ✅ Created MCP Proxy (`mcp-monitor/proxy/mcp_proxy.py`)
3. ✅ Compiled and packaged extension (`.vsix`)
4. ✅ Installed extension in VS Code
5. ✅ Proxy is running on `ws://localhost:8766`

## 🎯 Next Steps to Test

### Step 1: Reload VS Code Window

The extension needs VS Code to restart to activate:

1. Press `Ctrl+Shift+P` (Command Palette)
2. Type "Developer: Reload Window"
3. Press Enter

**What should happen:**
- Extension activates automatically
- Connects to proxy at `ws://localhost:8766`
- You'll see a notification: "✅ MCP Status Bar connected to proxy"

### Step 2: Check Extension is Active

Open Developer Tools to see console logs:

1. Press `Ctrl+Shift+P`
2. Type "Developer: Toggle Developer Tools"
3. Look in the Console tab for:
   ```
   🚀 MCP Status Bar extension activating...
   🔌 Connecting to MCP Proxy: ws://localhost:8766
   ✅ Connected to MCP Proxy
   ```

### Step 3: Test with Test Server

We have a test MCP server running. Let's send it a tool call:

**Option A: Via command line (to test proxy directly)**

```bash
# In a new PowerShell terminal:
cd "e:\scripts-python\CDE Orchestrator MCP"

# Send a test tool call
echo '{"jsonrpc":"2.0","method":"tools/call","id":1,"params":{"name":"testTool"}}' | python mcp-monitor/proxy/test_mcp_server.py
```

**Option B: Via VS Code MCP (when configured)**

We need to update `.vscode/mcp.json` to add the test server temporarily.

### Step 4: What You Should See

**In status bar (bottom right corner):**

1. Tool starts: `$(sync~spin) testTool: 0% (0.0s)`
2. Progress: `$(sync~spin) testTool: 25% (0.5s)`
3. Progress: `$(sync~spin) testTool: 50% (1.0s)`
4. Progress: `$(sync~spin) testTool: 75% (1.5s)`
5. Complete: `$(check) testTool: 100% (2.0s)`
6. Auto-hide after 5 seconds

**Hover over status bar item for tooltip:**
```
TestServer - testTool

Progress: 50%
Elapsed: 1.0s
Status: Processing... 50%
```

## 🔍 Troubleshooting

### Extension doesn't activate

Check if it's installed:
```bash
code --list-extensions | Select-String "mcp-status-bar"
```

Should show: `cde-orchestrator.mcp-status-bar`

### Extension can't connect to proxy

1. Check proxy is running:
   ```bash
   netstat -an | findstr 8766
   ```
   Should show: `TCP    127.0.0.1:8766`

2. Check extension logs:
   - Ctrl+Shift+P → "Developer: Show Running Extensions"
   - Find "MCP Status Bar"
   - Click "Open Extension Logs"

### Status bar doesn't appear

1. Check extension settings:
   - File → Preferences → Settings
   - Search "mcpStatusBar"
   - Ensure "enabled" is checked

2. Check Developer Console for errors:
   - Ctrl+Shift+P → "Developer: Toggle Developer Tools"
   - Console tab

## 📋 Configuration Options

In VS Code settings (`settings.json`):

```json
{
  "mcpStatusBar.enabled": true,
  "mcpStatusBar.proxyUrl": "ws://localhost:8766",
  "mcpStatusBar.showPercentage": true,
  "mcpStatusBar.showElapsedTime": true
}
```

## 🎯 Testing with Real CDE Tools

Once test server works, update `.vscode/mcp.json`:

```json
{
  "servers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": [
        "mcp-monitor/proxy/mcp_proxy.py",
        "CDE",
        "python",
        "src/server.py"
      ],
      "env": {
        "PYTHONPATH": "src"
      }
    }
  }
}
```

Then use Copilot Chat:
```
@CDE_Orchestrator scan documentation in current project
```

## 📊 Success Criteria

✅ Extension activates without errors
✅ Connects to proxy WebSocket
✅ Status bar appears during tool execution
✅ Shows animated icon and percentage
✅ Updates in real-time
✅ Auto-hides after completion
✅ Tooltip shows full details

## 🐛 Known Issues

- Only shows one operation at a time
- No history yet (that's Phase 2)
- Proxy must be running before VS Code starts

## 🚀 Next Steps

1. Test with CDE's real tools (add `ctx.report_progress()` calls)
2. Add more MCP servers to test universality
3. Phase 2: Add TreeView sidebar with history
4. Phase 2: Add log panel
5. Phase 2: Add dashboard

---

**Current Status**: ✅ MVP Ready to Test
**Proxy Running**: Port 8766
**Extension Installed**: Yes
**Next Action**: Reload VS Code Window
