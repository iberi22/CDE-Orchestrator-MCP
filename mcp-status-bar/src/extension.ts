import * as vscode from 'vscode';
import * as http from 'http';

let statusBarItem: vscode.StatusBarItem;
let hideTimer: NodeJS.Timeout | null = null;
let httpServer: http.Server | null = null;

interface ProgressEvent {
    server: string;
    tool: string;
    percentage: number;
    elapsed: number;
    message: string;
}

export function activate(context: vscode.ExtensionContext) {
    console.log('🚀 MCP Status Bar extension activating...');

    const config = vscode.workspace.getConfiguration('mcpStatusBar');

    if (!config.get('enabled', true)) {
        console.log('⏸️ MCP Status Bar is disabled in settings');
        return;
    }

    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBarItem.name = 'MCP Progress';
    statusBarItem.text = '$(radio-tower) MCP: Ready';
    statusBarItem.tooltip = 'MCP Status Bar - Waiting for tool executions...';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Start HTTP server to receive progress events
    startHttpServer();

    // Watch for config changes
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('mcpStatusBar.enabled')) {
                const enabled = vscode.workspace.getConfiguration('mcpStatusBar').get('enabled', true);
                if (!enabled) {
                    cleanup();
                }
            }
        })
    );

    console.log('✅ MCP Status Bar extension activated');
}

function startHttpServer() {
    httpServer = http.createServer((req, res) => {
        if (req.method === 'POST' && req.url === '/progress') {
            let body = '';

            req.on('data', (chunk) => {
                body += chunk.toString();
            });

            req.on('end', () => {
                try {
                    const event: ProgressEvent = JSON.parse(body);
                    console.log('📊 Progress received:', event.tool, `${Math.round(event.percentage * 100)}%`);
                    updateStatusBar(event);

                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ status: 'ok' }));
                } catch (e) {
                    console.error('Error parsing progress event:', e);
                    res.writeHead(400);
                    res.end();
                }
            });
        } else {
            res.writeHead(404);
            res.end();
        }
    });

    httpServer.on('error', (err) => {
        console.error('HTTP server error:', err);
    });

    httpServer.listen(8768, 'localhost', () => {
        console.log('✅ MCP Status Bar HTTP server listening on http://localhost:8768/progress');
        vscode.window.showInformationMessage('✅ MCP Status Bar ready on port 8768');
    });
}

function updateStatusBar(event: ProgressEvent) {
    const config = vscode.workspace.getConfiguration('mcpStatusBar');
    const showPercentage = config.get('showPercentage', true);
    const showElapsedTime = config.get('showElapsedTime', true);

    const percentage = Math.round(event.percentage * 100);
    const elapsed = event.elapsed.toFixed(1);

    // Clear any existing hide timer
    if (hideTimer) {
        clearTimeout(hideTimer);
        hideTimer = null;
    }

    // Icon with animation
    const icon = percentage === 100 ? '$(check)' : '$(sync~spin)';

    // Build text
    let text = `${icon} ${event.tool}`;

    if (showPercentage) {
        text += `: ${percentage}%`;
    }

    if (showElapsedTime) {
        text += ` (${elapsed}s)`;
    }

    statusBarItem.text = text;

    // Tooltip with full details
    statusBarItem.tooltip = new vscode.MarkdownString(
        `**${event.server}** - ${event.tool}\n\n` +
        `Progress: ${percentage}%\n\n` +
        `Elapsed: ${elapsed}s\n\n` +
        `Status: ${event.message}`,
        true
    );

    // Set color based on status
    if (percentage === 100) {
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    } else {
        statusBarItem.backgroundColor = undefined;
    }

    statusBarItem.show();

    // Return to idle state after 5 seconds if complete
    if (percentage === 100) {
        hideTimer = setTimeout(() => {
            console.log('⏰ Returning to idle state');
            statusBarItem.text = '$(radio-tower) MCP: Ready';
            statusBarItem.tooltip = 'MCP Status Bar - Ready for tool executions';
            statusBarItem.backgroundColor = undefined;
        }, 5000);
    }
}

function cleanup() {
    if (hideTimer) {
        clearTimeout(hideTimer);
        hideTimer = null;
    }
    if (httpServer) {
        httpServer.close();
        httpServer = null;
    }
}

export function deactivate() {
    cleanup();
}
