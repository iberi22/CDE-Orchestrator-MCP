import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

interface LogEntry {
    tool: string;
    percentage: number;
    message: string;
    timestamp: number;
    elapsed: number;
    success: boolean;
}

export class OutputPanel {
    private outputChannel: vscode.OutputChannel;
    private logHistory: LogEntry[] = [];
    private totalExecutionTime = 0;
    private successfulExecutions = 0;
    private totalExecutions = 0;

    constructor() {
        this.outputChannel = vscode.window.createOutputChannel('MCP Execution Log');
        this.registerExportCommand();
    }

    public log(
        tool: string,
        percentage: number,
        message: string,
        elapsed: number
    ) {
        const timestamp = Date.now();
        const isSuccess = percentage === 100;
        const isStarted = percentage === 0;

        const entry: LogEntry = {
            tool,
            percentage,
            message,
            timestamp,
            elapsed,
            success: isSuccess,
        };

        this.logHistory.push(entry);

        const logMessage = `[${new Date(
            timestamp
        ).toLocaleTimeString()}] ${tool}: ${Math.round(
            percentage * 100
        )}% - ${message}`;
        this.outputChannel.appendLine(logMessage);

        if (isStarted) {
            this.totalExecutions++;
        }

        if (isSuccess) {
            this.totalExecutionTime += elapsed;
            this.successfulExecutions++;
            this.updateMetrics();
        }
    }

    private updateMetrics() {
        const avgExecutionTime =
            this.successfulExecutions > 0
                ? (this.totalExecutionTime / this.successfulExecutions).toFixed(2)
                : 'N/A';
        const successRate =
            this.totalExecutions > 0
                ? ((this.successfulExecutions / this.totalExecutions) * 100).toFixed(
                      2
                  )
                : 'N/A';

        this.outputChannel.appendLine(
            `---\nMetrics: Avg. Execution Time: ${avgExecutionTime}s | Success Rate: ${successRate}%\n---`
        );
    }

    private registerExportCommand() {
        vscode.commands.registerCommand('mcp.exportLogs', () => {
            this.exportLogs();
        });
    }

    private async exportLogs() {
        if (this.logHistory.length === 0) {
            vscode.window.showInformationMessage('No logs to export.');
            return;
        }

        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            vscode.window.showErrorMessage(
                'No workspace folder open to save the log file.'
            );
            return;
        }

        const filePath = path.join(
            workspaceFolders[0].uri.fsPath,
            `mcp-logs-${new Date().toISOString().replace(/:/g, '-')}.json`
        );

        try {
            fs.writeFileSync(
                filePath,
                JSON.stringify(this.logHistory, null, 2)
            );
            vscode.window.showInformationMessage(`Logs exported to ${filePath}`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to export logs: ${error}`);
        }
    }
}
