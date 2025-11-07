---
updated: '2025-11-06'
author: GitHub Copilot
status: archived
created: '2025-11-06'
type: execution
title: Phase 2C Enhanced UI - Jules Task Package
description: Parallel tasks for TreeView history + OUTPUT panel + performance dashboard
---
## Phase 2C Enhanced UI - Jules Execution Tasks

**Objective**: Extend VS Code extension with enhanced UI features (TreeView history, OUTPUT panel, performance dashboard)

**Status**: 🟢 READY FOR JULES EXECUTION

**Architecture**: 3 parallel task streams to complete in shortest time

---

## Task Stream 1: TreeView History Display (Jules Task 1)

**Complexity**: Medium | **Duration**: 45-60 min | **Parallel**: YES

### Objective
Display tool execution history in a TreeView sidebar, showing:
- Recent tool runs (last 10)
- Tool name + execution time
- Status (success/failed/in-progress)
- Expandable details (input/output)

### Implementation Details

**File to Create**: `mcp-status-bar/src/treeView.ts`

```typescript
// TreeView item structure
interface ToolExecution {
  id: string;
  tool: string;
  status: "success" | "failed" | "pending";
  percentage: number;
  elapsed: number;
  message: string;
  timestamp: Date;
  input?: string;
  output?: string;
}

// TreeView provider
class ToolHistoryProvider implements vscode.TreeDataProvider<TreeItem> {
  getChildren(element?: TreeItem): TreeItem[] {
    // Load from localStorage, limit to 10 recent
  }
  getTreeItem(element: TreeItem): TreeItem {
    // Return tree item with collapsible details
  }
}
```

### Files to Modify
1. `mcp-status-bar/src/extension.ts` - Register TreeView provider
2. `mcp-status-bar/src/store.ts` - Add localStorage for history (NEW)
3. `mcp-status-bar/package.json` - Add TreeView contribution

### Subtasks
- [ ] 1.1 Create TreeView provider class
- [ ] 1.2 Implement item rendering with icons/colors
- [ ] 1.3 Add localStorage persistence
- [ ] 1.4 Register in activation events
- [ ] 1.5 Test TreeView rendering

### Success Criteria
- ✅ TreeView shows last 10 tool executions
- ✅ Items collapsible to show details
- ✅ Data persists between VS Code restarts
- ✅ Icons indicate status (checkmark/error/spinner)

---

## Task Stream 2: OUTPUT Panel with Metrics (Jules Task 2)

**Complexity**: Medium | **Duration**: 45-60 min | **Parallel**: YES

### Objective
Create dedicated OUTPUT channel showing:
- Tool execution log (timestamp, tool name, status)
- Real-time metrics (percentage, elapsed time)
- Performance summary (avg execution time, success rate)
- JSON export button for debugging

### Implementation Details

**File to Create**: `mcp-status-bar/src/outputPanel.ts`

```typescript
// Output channel management
class ToolOutputPanel {
  private channel: vscode.OutputChannel;

  constructor() {
    this.channel = vscode.window.createOutputChannel("MCP Tools");
  }

  logExecution(tool: string, percentage: number, message: string) {
    const timestamp = new Date().toISOString();
    const line = `[${timestamp}] ${tool}: ${Math.round(percentage * 100)}% - ${message}`;
    this.channel.appendLine(line);
  }

  showMetrics(metrics: ToolMetrics) {
    this.channel.appendLine("=== PERFORMANCE SUMMARY ===");
    this.channel.appendLine(`Avg Execution: ${metrics.avgDuration}s`);
    this.channel.appendLine(`Success Rate: ${metrics.successRate}%`);
  }
}
```

### Files to Modify
1. `mcp-status-bar/src/extension.ts` - Create output channel
2. `mcp-status-bar/src/messaging.ts` - Add logging hooks (NEW)
3. `mcp-status-bar/src/store.ts` - Add metrics calculation

### Subtasks
- [ ] 2.1 Create OUTPUT channel class
- [ ] 2.2 Implement real-time logging
- [ ] 2.3 Add metrics calculation (avg time, success rate)
- [ ] 2.4 Add JSON export button
- [ ] 2.5 Test output formatting

### Success Criteria
- ✅ OUTPUT channel appears in VS Code
- ✅ Real-time log entries as tools execute
- ✅ Metrics show accurate averages
- ✅ Can export logs as JSON
- ✅ Channel persists until VS Code closes

---

## Task Stream 3: Performance Dashboard (Jules Task 3)

**Complexity**: High | **Duration**: 60-75 min | **Parallel**: YES

### Objective
Create web-based dashboard (local file served via VS Code webview):
- Tool execution timeline (x=time, y=tool names)
- Success/failure ratio chart
- Latency distribution histogram
- Top slowest tools ranking

### Implementation Details

**File to Create**: `mcp-status-bar/src/dashboard.ts` + `mcp-status-bar/webview/dashboard.html`

```typescript
// Dashboard webview provider
class DashboardProvider implements vscode.WebviewViewProvider {
  resolveWebviewView(webviewView: vscode.WebviewView) {
    webviewView.webview.html = this.getHtmlContent();
    webviewView.webview.onDidReceiveMessage((msg) => {
      if (msg.command === "getMetrics") {
        const metrics = this.loadMetrics();
        webviewView.webview.postMessage({
          command: "displayMetrics",
          data: metrics
        });
      }
    });
  }

  private getHtmlContent(): string {
    // Return HTML with Chart.js for visualization
  }
}
```

### Files to Create/Modify
1. `mcp-status-bar/webview/dashboard.html` - HTML template (NEW)
2. `mcp-status-bar/webview/dashboard.css` - Styling (NEW)
3. `mcp-status-bar/src/dashboard.ts` - Webview provider (NEW)
4. `mcp-status-bar/src/extension.ts` - Register webview
5. `mcp-status-bar/package.json` - Add webview contribution

### Dependencies
- Chart.js (for visualizations) - add to package.json

### Subtasks
- [ ] 3.1 Create webview provider class
- [ ] 3.2 Design dashboard HTML layout
- [ ] 3.3 Implement Chart.js integration
- [ ] 3.4 Add metrics aggregation logic
- [ ] 3.5 Implement refresh button
- [ ] 3.6 Test chart rendering

### Success Criteria
- ✅ Dashboard webview accessible from sidebar
- ✅ Charts render correctly with sample data
- ✅ Data refreshes in real-time
- ✅ Responsive design (mobile-friendly)
- ✅ No external API calls (local only)

---

## Integration & Wiring (Jules Task 4 - Sequential)

**Complexity**: Medium | **Duration**: 30-45 min | **After**: Tasks 1-3 complete

### Objective
Wire all three features together with shared data infrastructure

### Implementation Details

**File to Modify**: `mcp-status-bar/src/store.ts` (Central store)

```typescript
// Unified data store
class ToolMetricsStore {
  private history: ToolExecution[] = [];
  private metrics: ToolMetrics = {
    totalExecutions: 0,
    successCount: 0,
    avgDuration: 0,
    durations: []
  };

  addExecution(execution: ToolExecution) {
    this.history.push(execution);
    this.updateMetrics();
    this.notifyListeners(); // Trigger UI updates
  }

  private updateMetrics() {
    // Recalculate success rate, avg duration, etc.
  }
}
```

### Files to Modify
1. `mcp-status-bar/src/store.ts` - Central data store (NEW/ENHANCED)
2. `mcp-status-bar/src/extension.ts` - Wire all components
3. `mcp-status-bar/src/proxy-listener.ts` - Route HTTP events to store

### Subtasks
- [ ] 4.1 Create unified ToolMetricsStore class
- [ ] 4.2 Connect TreeView to store
- [ ] 4.3 Connect OUTPUT panel to store
- [ ] 4.4 Connect Dashboard to store
- [ ] 4.5 Test data flow end-to-end

### Success Criteria
- ✅ Single source of truth (store)
- ✅ All UI components receive updates
- ✅ No data duplication
- ✅ End-to-end test passing

---

## Testing & Validation (Jules Task 5 - Sequential)

**Complexity**: Low | **Duration**: 20-30 min | **After**: Task 4 complete

### Objective
Comprehensive testing of all Phase 2C features

### Test Scenarios

1. **TreeView Tests**
   - [ ] History persists across restart
   - [ ] Limit to 10 items enforced
   - [ ] Icons show correct status

2. **OUTPUT Panel Tests**
   - [ ] Real-time logging working
   - [ ] JSON export valid format
   - [ ] Metrics calculations correct

3. **Dashboard Tests**
   - [ ] Charts render without errors
   - [ ] Data updates in real-time
   - [ ] Export functionality works

4. **Integration Tests**
   - [ ] Run 5 test tools in sequence
   - [ ] All UIs update correctly
   - [ ] Data consistency maintained

### Test Tool
Use existing `cde_testProgressReporting` to simulate tool execution with progress events

### Subtasks
- [ ] 5.1 Create test suite (Jest/Mocha)
- [ ] 5.2 Run manual tests with test tool
- [ ] 5.3 Fix any UI glitches
- [ ] 5.4 Validate data integrity
- [ ] 5.5 Performance check (no memory leaks)

### Success Criteria
- ✅ All manual tests pass
- ✅ No console errors
- ✅ Memory stable after 100+ simulated executions
- ✅ UI responsive (<500ms update time)

---

## Compilation & Packaging (Jules Task 6 - Final)

**Complexity**: Low | **Duration**: 15-20 min | **After**: Task 5 complete

### Objective
Package extension and create PR to main

### Subtasks
- [ ] 6.1 Run `npm run compile`
- [ ] 6.2 Run `npm run package` (create .vsix)
- [ ] 6.3 Update CHANGELOG.md
- [ ] 6.4 Create commit with all changes
- [ ] 6.5 Push to feature branch
- [ ] 6.6 Create PR to main with detailed description

### PR Description Template
```
## Phase 2C Enhanced UI - TreeView, OUTPUT Panel, Performance Dashboard

### Changes
- TreeView sidebar showing last 10 tool executions
- OUTPUT panel with real-time metrics
- Web-based performance dashboard with charts

### Key Files
- mcp-status-bar/src/treeView.ts (NEW)
- mcp-status-bar/src/outputPanel.ts (NEW)
- mcp-status-bar/src/dashboard.ts (NEW)
- mcp-status-bar/webview/dashboard.html (NEW)
- mcp-status-bar/src/store.ts (ENHANCED)

### Tests
- Manual testing of all features: ✅
- Data persistence: ✅
- Performance validated: ✅

### Ready for Review
All changes tested locally. Ready for MCP GitHub review and integration testing.
```

### Success Criteria
- ✅ Branch pushed to GitHub
- ✅ PR created to main
- ✅ All changed files included
- ✅ Description clear and complete

---

## Execution Strategy

### Parallel Execution (Tasks 1-3)
- All three can run simultaneously
- No shared file conflicts
- Estimated total time: **60-75 minutes**

### Sequential (Tasks 4-6)
- Task 4: Wire components (30-45 min)
- Task 5: Validate (20-30 min)
- Task 6: Package & PR (15-20 min)
- Estimated total: **65-95 minutes**

### Total Execution Time
**Minimum**: 125-170 minutes (~2-3 hours)

### File Conflict Avoidance
- Task 1: Only creates treeView.ts, modifies extension.ts (lines 1-50)
- Task 2: Only creates outputPanel.ts, modifies extension.ts (lines 51-100)
- Task 3: Only creates dashboard.ts, modifies extension.ts (lines 101-150)
- Task 4: Coordinates all in store.ts + extension.ts wiring
- **Result**: Minimal conflicts, mostly sequential integration in extension.ts

---

## Jules Execution Command

```bash
# Create parallel sessions for Tasks 1-3, then sequential 4-6
jules new --parallel 3 "Phase 2C Task 1: Implement TreeView history display for MCP Status Bar extension with localStorage persistence. File: mcp-status-bar/src/treeView.ts. Register in extension.ts. Add package.json contribution. See specs in agent-docs/execution/phase2c-tasks.md"

julius new "Phase 2C Task 2: Create OUTPUT panel showing real-time tool execution log with metrics (avg time, success rate). File: mcp-status-bar/src/outputPanel.ts. Add JSON export. See specs in agent-docs/execution/phase2c-tasks.md"

jules new "Phase 2C Task 3: Build web-based performance dashboard (webview) with Chart.js showing tool timeline, success ratio, latency histogram. Files: mcp-status-bar/webview/dashboard.html, src/dashboard.ts. See specs in agent-docs/execution/phase2c-tasks.md"

# After all 3 complete:
jules new "Phase 2C Task 4: Wire TreeView, OUTPUT panel, Dashboard to unified ToolMetricsStore. Central data flow. mcp-status-bar/src/store.ts. Test end-to-end. See specs in agent-docs/execution/phase2c-tasks.md"

jules new "Phase 2C Task 5: Test all Phase 2C features - TreeView persistence, OUTPUT logging, Dashboard charts. Use cde_testProgressReporting for simulation. Validate data consistency. Performance check. See specs in agent-docs/execution/phase2c-tasks.md"

jules new "Phase 2C Task 6: Compile with 'npm run compile', package with 'npm run package', create PR to main with all changes. Update CHANGELOG. Include detailed PR description. Push feature branch. See specs in agent-docs/execution/phase2c-tasks.md"
```

---

## Success Definition

✅ **Phase 2C Complete when:**
1. TreeView shows 10 recent tool executions with status icons
2. OUTPUT panel logs real-time tool execution with metrics
3. Dashboard renders with Chart.js visualizations
4. All three features share unified data store
5. PR created to main with all changes
6. Local validation passes (no errors, responsive UI)

---

## Notes for Jules

- **Architecture**: TypeScript + Vue.js lightweight (already in extension)
- **Data**: Use localStorage for persistence (no backend needed)
- **Testing**: Simulate with `cde_testProgressReporting` tool
- **Styling**: Follow existing VS Code extension theme
- **Performance**: No external API calls, all local
- **Documentation**: Update README in mcp-status-bar/ with new features
