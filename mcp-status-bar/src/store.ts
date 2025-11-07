import * as vscode from 'vscode';

/**
 * ToolMetricsStore - Unified Data Store for MCP Tool Metrics
 *
 * Central source of truth for all MCP tool execution data.
 * Manages history, metrics, and notifies all UI components (TreeView, OUTPUT, Dashboard).
 *
 * Architecture:
 * - TreeView reads execution history
 * - OutputPanel reads metrics (avg time, success rate)
 * - Dashboard reads all data for visualization
 * - All components subscribe to updates via EventEmitter
 */

export interface ToolExecution {
    id: string; // Unique execution ID
    tool: string; // Tool name (e.g., "cde_scanDocumentation")
    server: string; // MCP server name
    status: 'success' | 'failure' | 'running';
    startTime: Date;
    endTime?: Date;
    duration?: number; // In seconds
    message?: string;
    percentage: number; // 0.0 to 1.0
}

export interface ToolMetrics {
    totalExecutions: number;
    successCount: number;
    failureCount: number;
    runningCount: number;
    avgDuration: number; // Average execution time in seconds
    successRate: number; // Percentage 0-100
    durations: number[]; // Last N durations for histogram
}

export interface DashboardData {
    executionTimeline: Array<{ tool: string; duration: number; timestamp: Date }>;
    successFailureRatio: { success: number; failure: number };
    latencyHistogram: number[];
    topSlowestTools: Array<{ tool: string; avgDuration: number }>;
}

export class ToolMetricsStore {
    private static instance: ToolMetricsStore;

    private executions: Map<string, ToolExecution> = new Map();
    private executionHistory: ToolExecution[] = []; // Last 100 executions
    private maxHistorySize = 100;

    private _onDidChange: vscode.EventEmitter<void> = new vscode.EventEmitter<void>();
    public readonly onDidChange: vscode.Event<void> = this._onDidChange.event;

    private storage: vscode.Memento;

    private constructor(context: vscode.ExtensionContext) {
        this.storage = context.globalState;
        this.loadFromStorage();
    }

    /**
     * Get singleton instance
     */
    public static getInstance(context: vscode.ExtensionContext): ToolMetricsStore {
        if (!ToolMetricsStore.instance) {
            ToolMetricsStore.instance = new ToolMetricsStore(context);
        }
        return ToolMetricsStore.instance;
    }

    /**
     * Add or update tool execution
     */
    public addExecution(execution: ToolExecution): void {
        // Add to active executions map
        this.executions.set(execution.id, execution);

        // If complete, add to history
        if (execution.status !== 'running') {
            this.executionHistory.unshift(execution);

            // Keep only last N executions
            if (this.executionHistory.length > this.maxHistorySize) {
                this.executionHistory = this.executionHistory.slice(0, this.maxHistorySize);
            }

            // Remove from active map
            this.executions.delete(execution.id);
        }

        this.saveToStorage();
        this._onDidChange.fire();
    }

    /**
     * Update existing execution (for progress updates)
     */
    public updateExecution(id: string, updates: Partial<ToolExecution>): void {
        const existing = this.executions.get(id);
        if (existing) {
            Object.assign(existing, updates);

            // Calculate duration if endTime provided
            if (updates.endTime) {
                existing.duration = (updates.endTime.getTime() - existing.startTime.getTime()) / 1000;
            }

            this.executions.set(id, existing);
            this._onDidChange.fire();
        }
    }

    /**
     * Get last N executions (for TreeView history)
     */
    public getHistory(limit: number = 10): ToolExecution[] {
        return this.executionHistory.slice(0, limit);
    }

    /**
     * Get currently running executions
     */
    public getRunningExecutions(): ToolExecution[] {
        return Array.from(this.executions.values()).filter(e => e.status === 'running');
    }

    /**
     * Calculate aggregate metrics (for OutputPanel)
     */
    public getMetrics(): ToolMetrics {
        const completed = this.executionHistory.filter(e => e.status !== 'running');
        const successCount = completed.filter(e => e.status === 'success').length;
        const failureCount = completed.filter(e => e.status === 'failure').length;
        const runningCount = this.executions.size;

        const durations = completed
            .filter(e => e.duration !== undefined)
            .map(e => e.duration!);

        const avgDuration = durations.length > 0
            ? durations.reduce((sum, d) => sum + d, 0) / durations.length
            : 0;

        const successRate = completed.length > 0
            ? (successCount / completed.length) * 100
            : 0;

        return {
            totalExecutions: completed.length + runningCount,
            successCount,
            failureCount,
            runningCount,
            avgDuration,
            successRate,
            durations: durations.slice(-50), // Last 50 for histogram
        };
    }

    /**
     * Get dashboard visualization data
     */
    public getDashboardData(): DashboardData {
        const completed = this.executionHistory.filter(e => e.duration !== undefined);

        // Execution timeline (last 20 executions)
        const executionTimeline = completed.slice(0, 20).map(e => ({
            tool: e.tool,
            duration: e.duration!,
            timestamp: e.startTime,
        }));

        // Success/Failure ratio
        const successFailureRatio = {
            success: completed.filter(e => e.status === 'success').length,
            failure: completed.filter(e => e.status === 'failure').length,
        };

        // Latency histogram (durations)
        const latencyHistogram = completed
            .slice(0, 50)
            .map(e => e.duration!)
            .filter(d => d !== undefined);

        // Top 5 slowest tools
        const toolDurations = new Map<string, number[]>();
        completed.forEach(e => {
            if (e.duration) {
                const durations = toolDurations.get(e.tool) || [];
                durations.push(e.duration);
                toolDurations.set(e.tool, durations);
            }
        });

        const topSlowestTools = Array.from(toolDurations.entries())
            .map(([tool, durations]) => ({
                tool,
                avgDuration: durations.reduce((sum, d) => sum + d, 0) / durations.length,
            }))
            .sort((a, b) => b.avgDuration - a.avgDuration)
            .slice(0, 5);

        return {
            executionTimeline,
            successFailureRatio,
            latencyHistogram,
            topSlowestTools,
        };
    }

    /**
     * Clear all data
     */
    public clear(): void {
        this.executions.clear();
        this.executionHistory = [];
        this.saveToStorage();
        this._onDidChange.fire();
    }

    /**
     * Persist to VS Code global state
     */
    private saveToStorage(): void {
        const dataToStore = {
            history: this.executionHistory.map(e => ({
                id: e.id,
                tool: e.tool,
                server: e.server,
                status: e.status,
                startTime: e.startTime.toISOString(),
                endTime: e.endTime?.toISOString(),
                duration: e.duration,
                message: e.message,
                percentage: e.percentage,
            })),
        };
        this.storage.update('mcp-metrics-store', dataToStore);
    }

    /**
     * Load from VS Code global state
     */
    private loadFromStorage(): void {
        const stored = this.storage.get<any>('mcp-metrics-store');
        if (stored && stored.history) {
            this.executionHistory = stored.history.map((e: any) => ({
                id: e.id,
                tool: e.tool,
                server: e.server,
                status: e.status,
                startTime: new Date(e.startTime),
                endTime: e.endTime ? new Date(e.endTime) : undefined,
                duration: e.duration,
                message: e.message,
                percentage: e.percentage,
            }));
        }
    }
}
