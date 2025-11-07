import * as vscode from 'vscode';
import * as path from 'path';
import { ToolMetricsStore } from './store';

/**
 * DashboardWebview - Performance Dashboard Provider
 *
 * Displays MCP tool metrics in an interactive webview with Chart.js visualizations.
 * Fetches data from ToolMetricsStore.
 */
export class DashboardWebview {
    private panel: vscode.WebviewPanel | undefined;
    private store: ToolMetricsStore;
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.store = ToolMetricsStore.getInstance(context);
    }

    public show(): void {
        if (this.panel) {
            this.panel.reveal(vscode.ViewColumn.One);
            return;
        }

        this.panel = vscode.window.createWebviewPanel(
            'mcpDashboard',
            'MCP Performance Dashboard',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [
                    vscode.Uri.file(path.join(this.context.extensionPath, 'webview'))
                ],
            }
        );

        this.panel.webview.html = this.getHtmlContent();

        // Handle messages from webview
        this.panel.webview.onDidReceiveMessage(
            (message) => {
                if (message.command === 'refresh') {
                    this.updateDashboard();
                }
            },
            undefined,
            this.context.subscriptions
        );

        // Update on store changes
        this.store.onDidChange(() => {
            this.updateDashboard();
        });

        // Cleanup when closed
        this.panel.onDidDispose(() => {
            this.panel = undefined;
        });

        // Initial data load
        this.updateDashboard();
    }

    private updateDashboard(): void {
        if (!this.panel) return;

        const dashboardData = this.store.getDashboardData();

        // Transform data for Chart.js
        const chartData = {
            timeline: {
                labels: dashboardData.executionTimeline.map(e => e.tool),
                datasets: [{
                    label: 'Execution Time (s)',
                    data: dashboardData.executionTimeline.map(e => e.duration),
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                }],
            },
            ratio: {
                labels: ['Success', 'Failure'],
                datasets: [{
                    data: [
                        dashboardData.successFailureRatio.success,
                        dashboardData.successFailureRatio.failure,
                    ],
                    backgroundColor: ['rgba(75, 192, 192, 0.6)', 'rgba(255, 99, 132, 0.6)'],
                }],
            },
            latency: {
                labels: dashboardData.latencyHistogram.map((_, i) => `Exec ${i + 1}`),
                datasets: [{
                    label: 'Latency (s)',
                    data: dashboardData.latencyHistogram,
                    backgroundColor: 'rgba(153, 102, 255, 0.6)',
                }],
            },
            slowest: {
                labels: dashboardData.topSlowestTools.map(t => t.tool),
                datasets: [{
                    label: 'Avg. Duration (s)',
                    data: dashboardData.topSlowestTools.map(t => t.avgDuration),
                    backgroundColor: 'rgba(255, 159, 64, 0.6)',
                }],
            },
        };

        this.panel.webview.postMessage({
            command: 'updateData',
            data: chartData,
        });
    }

    private getHtmlContent(): string {
        const webviewPath = path.join(this.context.extensionPath, 'webview');
        const chartJsUri = this.panel!.webview.asWebviewUri(
            vscode.Uri.file(path.join(webviewPath, 'chart.min.js'))
        );
        const dashboardJsUri = this.panel!.webview.asWebviewUri(
            vscode.Uri.file(path.join(webviewPath, 'dashboard.js'))
        );

        return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Performance Dashboard</title>
    <script src="${chartJsUri}"></script>
    <style>
        body {
            font-family: var(--vscode-font-family);
            padding: 1rem;
            background-color: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
        }
        .chart-container {
            position: relative;
            height: 300px;
            width: 100%;
            margin-bottom: 2rem;
            background: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
            padding: 1rem;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }
        button {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 0.5rem 1rem;
            cursor: pointer;
            border-radius: 4px;
        }
        button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        h1 {
            margin: 0;
        }
        h2 {
            color: var(--vscode-editor-foreground);
            border-bottom: 1px solid var(--vscode-panel-border);
            padding-bottom: 0.5rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 MCP Performance Dashboard</h1>
        <button id="refresh-button">🔄 Refresh</button>
    </div>

    <h2>📊 Tool Execution Timeline</h2>
    <div class="chart-container">
        <canvas id="timeline-chart"></canvas>
    </div>

    <h2>✅ Success/Failure Ratio</h2>
    <div class="chart-container" style="height: 250px; width: 50%; margin: 0 auto 2rem;">
        <canvas id="ratio-chart"></canvas>
    </div>

    <h2>⏱️ Latency Histogram</h2>
    <div class="chart-container">
        <canvas id="latency-chart"></canvas>
    </div>

    <h2>🐌 Top 5 Slowest Tools</h2>
    <div class="chart-container">
        <canvas id="slowest-chart"></canvas>
    </div>

    <script src="${dashboardJsUri}"></script>
</body>
</html>
        `;
    }
}
