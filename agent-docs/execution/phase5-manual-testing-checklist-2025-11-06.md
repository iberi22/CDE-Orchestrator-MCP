---
title: "Phase 5 Manual Testing Checklist"
description: "Step-by-step manual validation of MCP Status Bar extension UI components"
type: "guide"
status: "active"
created: "2025-11-06"
updated: "2025-11-06"
author: "CDE Agent"
---

## Phase 5: Manual Testing Checklist

### 📋 Pre-Testing Setup

**Requirements**:

- [ ] VS Code installed (v1.85+)
- [ ] Extension built: `npm run compile` ✅
- [ ] Extension packaged: `npm run package` ✅
- [ ] VSIX file exists: `mcp-status-bar-0.1.0.vsix`

**Installation**:

```bash
cd mcp-status-bar
code --install-extension mcp-status-bar-0.1.0.vsix
```

---

### 🧪 Test Suite 1: TreeView Component

#### Test 1.1: TreeView Panel Visibility

- [ ] Open VS Code with workspace
- [ ] Look at Explorer sidebar (left panel)
- [ ] Verify "MCP History" panel appears under Explorer
- [ ] Panel shows history icon `$(history)`
- [ ] Panel is empty initially (no executions yet)

**Expected**: Panel visible in Explorer, labeled "MCP History"

#### Test 1.2: TreeView Shows Execution After Tool Run

- [ ] Run any MCP tool from CLI (e.g., `cde_scanDocumentation`)
- [ ] Status bar shows progress: `$(sync~spin) scanDocumentation: 0%`
- [ ] After completion, expand "MCP History" in Explorer
- [ ] Execution appears with:
  - [ ] Tool name (e.g., "scanDocumentation")
  - [ ] Status icon (✅ success or ❌ failure)
  - [ ] Timestamp (MM:SS format)
  - [ ] Duration (if completed)

**Expected**: Execution visible in TreeView with all metadata

#### Test 1.3: TreeView Shows Multiple Executions

- [ ] Run 5+ MCP tools (different tools if possible)
- [ ] Each execution appears in TreeView
- [ ] Most recent at top (sorted by time)
- [ ] All show correct status icons
- [ ] Clicking execution shows details in breadcrumb

**Expected**: All 5+ executions visible, properly sorted

#### Test 1.4: TreeView Persistence After Reload

- [ ] With 5+ executions showing
- [ ] Close VS Code (Ctrl+Q or Cmd+Q)
- [ ] Reopen the same workspace
- [ ] MCP History still shows all previous executions
- [ ] Data persisted across session

**Expected**: All executions restored after reload

---

### 📊 Test Suite 2: OUTPUT Panel

#### Test 2.1: OUTPUT Channel Appears

- [ ] Open OUTPUT panel (View → Output or Ctrl+Shift+U)
- [ ] Dropdown shows "MCP Execution Log" channel
- [ ] Select it (if not default)
- [ ] Panel is empty initially

**Expected**: "MCP Execution Log" channel exists and is accessible

#### Test 2.2: OUTPUT Shows Tool Execution Logs

- [ ] Run `cde_scanDocumentation` or similar tool
- [ ] Switch to OUTPUT → MCP Execution Log
- [ ] See logs with format: `[HH:MM:SS] toolName: XX% - message`
- [ ] Example: `[14:23:45] scanDocumentation: 25% - Analyzing files...`
- [ ] Progress updates appear as tool executes
- [ ] Final entry shows 100% and elapsed time

**Expected**: Timestamped progress logs appear in real-time

#### Test 2.3: OUTPUT Panel Shows Metrics Summary

- [ ] After running 5+ tools
- [ ] Scroll to end of OUTPUT panel
- [ ] See metrics summary:

```text
📊 MCP Execution Metrics
├─ Total Executions: 5
├─ Successful: 4
├─ Failed: 1
├─ Avg. Duration: 12.3s
└─ Success Rate: 80%
```

**Expected**: Aggregated metrics visible at end of OUTPUT

#### Test 2.4: Export Logs Command Works

- [ ] Command palette (Ctrl+Shift+P)
- [ ] Type "MCP: Export Logs"
- [ ] Select command
- [ ] File save dialog appears
- [ ] Save as JSON
- [ ] Open JSON file and verify it contains:
  - [ ] All execution records
  - [ ] Metrics summary
  - [ ] Timestamp

**Expected**: JSON export with complete execution history and metrics

---

### 📈 Test Suite 3: Dashboard Component

#### Test 3.1: Dashboard Opens

- [ ] Command palette (Ctrl+Shift+P)
- [ ] Type "MCP: Show Performance Dashboard"
- [ ] Select command
- [ ] Webview panel opens with title "MCP Performance Dashboard"
- [ ] No errors in Debug Console (F12)

**Expected**: Dashboard webview opens without errors

#### Test 3.2: Dashboard Shows 4 Charts

After dashboard opens, verify:

- [ ] **Chart 1 - Timeline**: Bar chart showing last 10-20 executions
  - X-axis: Tool names
  - Y-axis: Duration in seconds
  - Bars colored by status (green=success, red=failure)
- [ ] **Chart 2 - Success/Failure**: Doughnut chart
  - Shows ratio of successful to failed executions
  - Percentages labeled
- [ ] **Chart 3 - Latency Histogram**: Bar chart
  - X-axis: Duration ranges (0-5s, 5-10s, etc.)
  - Y-axis: Frequency (number of tools)
- [ ] **Chart 4 - Top 5 Slowest**: Horizontal bar chart
  - Top 5 tools by average duration
  - Tool names on Y-axis
  - Duration on X-axis

**Expected**: All 4 charts render correctly with data

#### Test 3.3: Dashboard Updates in Real-Time

- [ ] Keep dashboard open
- [ ] Run a new MCP tool (e.g., `cde_onboardingProject`)
- [ ] Watch dashboard charts update live
- [ ] New execution appears in Timeline chart
- [ ] Success/Failure ratio updates
- [ ] Metrics recalculate

**Expected**: Charts update without manual refresh

#### Test 3.4: Dashboard Styling Matches VS Code Theme

- [ ] Check dashboard colors match VS Code theme
- [ ] Light theme: Light backgrounds, dark text
- [ ] Dark theme: Dark backgrounds, light text
- [ ] All text readable (good contrast)
- [ ] Charts styled consistently

**Expected**: Professional appearance matching VS Code theme

---

### ⚡ Test Suite 4: Progress Tracking Performance

#### Test 4.1: Status Bar Shows Progress Without Blocking

- [ ] Run `cde_scanDocumentation` on large project (500+ files)
- [ ] Status bar shows: `$(sync~spin) scanDocumentation: 5% (2.1s)`
- [ ] Percentage increments smoothly (not stuck at one value)
- [ ] Elapsed time increases continuously
- [ ] VS Code UI remains responsive (can type, scroll, click)
- [ ] No freezes or hangs

**Expected**: Progress visible, UI never blocks

#### Test 4.2: Batched Progress (HTTP Reduction)

- [ ] Run `cde_scanDocumentation` on 1000+ files
- [ ] Monitor network (DevTools or proxy) if possible
- [ ] HTTP POST calls to `http://localhost:8768/progress` should be:
  - [ ] Initial: 1 call (0%)
  - [ ] Scanning: ~10-15 calls (5-95%)
  - [ ] Final: 1-2 calls (95-100%)
  - [ ] **Total: ~12-18 calls** (NOT 1000+)
- [ ] Scan completes in 20-30 seconds with visual feedback

**Expected**: ~15 HTTP calls for 1000 file scan (98% reduction)

#### Test 4.3: Progress with Errors

- [ ] Start a tool that will error (or mock error)
- [ ] Status bar shows progress initially: `$(sync~spin) tool: 25%`
- [ ] When error occurs: `$(error) tool: ❌ Error message`
- [ ] TreeView shows ❌ icon
- [ ] OUTPUT shows error details
- [ ] No HTTP errors or exceptions in console

**Expected**: Error handling smooth, user sees clear status

#### Test 4.4: Concurrent Tool Progress

- [ ] Open terminal and run 2-3 MCP tools concurrently
- [ ] Status bar cycles between tools (most recent at top)
- [ ] Each tool maintains its own history in TreeView
- [ ] OUTPUT shows logs from all tools
- [ ] Dashboard metrics combine all tools
- [ ] No tool progress overwrites another

**Expected**: Multiple tools tracked independently, metrics aggregated

---

### 🧬 Test Suite 5: Edge Cases & Reliability

#### Test 5.1: Long-Running Tool (5+ minutes)

- [ ] Run Jules delegation: `cde_delegateToJules(...)`
- [ ] Status bar shows stage progress:
  - [ ] "Init" → "Connect" → "Create" → "Execute" → "Complete"
- [ ] Progress updates every 10-30 seconds (macro stages, not micro)
- [ ] UI responsive throughout
- [ ] Can interrupt (Ctrl+C) cleanly if needed

**Expected**: Long operations show meaningful progress

#### Test 5.2: HTTP Server Down

- [ ] Stop MCP server or block port 8768
- [ ] Run a tool
- [ ] Tool still executes (HTTP failures fail silently)
- [ ] Status bar shows progress as if HTTP working
- [ ] Tool completes successfully despite HTTP errors
- [ ] No exceptions in debug console

**Expected**: Tools resilient to HTTP failures

#### Test 5.3: Multiple Sessions/Windows

- [ ] Open 2 VS Code windows, both with extension
- [ ] Run tools from both windows
- [ ] Each window's TreeView/Dashboard shows only its own tools
- [ ] OUTPUT logs tagged with window ID or tool name
- [ ] No cross-contamination of data

**Expected**: Multi-window isolation maintained

#### Test 5.4: Rapid Tool Executions

- [ ] Run 10 tools in quick succession (one after another)
- [ ] Each execution logged and tracked
- [ ] No data loss or duplicates
- [ ] TreeView shows all 10
- [ ] Metrics accurate (10 total, success count, avg duration)

**Expected**: High-throughput tracking works reliably

---

### ✅ Test Suite 6: Data Persistence & Cleanup

#### Test 6.1: History Limit (Last 100)

- [ ] Run 150 MCP tools over time
- [ ] Check `store.ts`: `private static readonly HISTORY_LIMIT = 100`
- [ ] Only last 100 in TreeView
- [ ] Dashboard shows only recent tools (last 50 for histogram)
- [ ] Oldest tools dropped automatically

**Expected**: History capped at 100, oldest removed

#### Test 6.2: Metrics Calculation Accuracy

- [ ] Run 10 tools: 7 success (durations: 5, 5, 10, 10, 15, 20, 30)
  - [ ] 3 failures (durations: 5, 10, 15)
- [ ] Check metrics:
  - [ ] Total: 10
  - [ ] Success: 7
  - [ ] Failure: 3
  - [ ] Avg Duration: (5+5+10+10+15+20+30+5+10+15) / 10 = 12.5s
  - [ ] Success Rate: 7/10 = 70%
- [ ] Verify in OUTPUT panel metrics

**Expected**: Calculations correct to 1 decimal place

#### Test 6.3: Storage Persistence

- [ ] Run 5 tools
- [ ] Check VS Code ExtensionContext.globalState
- [ ] Data saved to key: `'mcp-metrics-store'`
- [ ] Close and reopen VS Code
- [ ] All 5 tools still in TreeView
- [ ] Metrics unchanged

**Expected**: Data survives session reload

#### Test 6.4: Clear Command

- [ ] If `cde_clearMetrics()` tool exists, call it
- [ ] OR manually call `store.clear()` from console
- [ ] TreeView becomes empty
- [ ] OUTPUT metrics reset: Total=0, Avg=0
- [ ] Dashboard charts show no data

**Expected**: Complete metrics reset when cleared

---

### 📋 Compilation & Packaging Validation

#### Pre-Test Check

- [ ] TypeScript compiles: `npm run compile`
  - Result: `✅ 0 errors, 0 warnings`
- [ ] Package builds: `npm run package`
  - Result: `✅ mcp-status-bar-0.1.0.vsix (15.53 KB)`

#### Installation Test

- [ ] Extension installs without errors
- [ ] No security warnings
- [ ] Activates on `*` events (all workspaces)
- [ ] No exceptions in VS Code debug console (F12 → Debug Console)

---

### 🎯 Success Criteria

**Test Passing Threshold**:

- ✅ All Tests in Suites 1-3 pass (TreeView, OUTPUT, Dashboard)
- ✅ All Tests in Suite 4 pass (Progress tracking)
- ✅ 80%+ tests in Suites 5-6 pass (Edge cases, persistence)
- ✅ No critical errors in debug console
- ✅ Extension activates and deactivates cleanly

**Phase 5 Completion**:

- ✅ Manual testing checklist 100% complete
- ✅ Performance baseline established (batching, response times)
- ✅ Edge cases identified and resolved
- ✅ Execution report generated: `execution-phase5-testing-results-2025-11-06.md`
- ✅ Final commit: `test(phase5): End-to-end testing & validation complete`

---

### 📝 Execution Log

| Test Suite | Status | Notes | Time |
|-----------|--------|-------|------|
| 1. TreeView | ⏳ TODO | | |
| 2. OUTPUT | ⏳ TODO | | |
| 3. Dashboard | ⏳ TODO | | |
| 4. Progress | ⏳ TODO | | |
| 5. Edge Cases | ⏳ TODO | | |
| 6. Persistence | ⏳ TODO | | |

---

### 🔗 Related Documents

- `AGENTS.md` - Section "📊 MCP Tool Metrics & Monitoring (Phase 4 - NEW)"
- `execution-phase4-unified-store-optimization-2025-11-06.md` - Architecture details
- `test_progress_tracking.py` - Automated test suite (86% passing)
