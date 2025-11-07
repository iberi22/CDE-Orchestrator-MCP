import * as vscode from 'vscode';

// Defines an execution in the history
export class Execution extends vscode.TreeItem {
    constructor(
        public readonly label: string, // The command that was executed
        public readonly agent: string,
        public readonly status: 'success' | 'failure' | 'running',
        public readonly timestamp: Date,
        public readonly details?: string
    ) {
        super(label, vscode.TreeItemCollapsibleState.Collapsed);
        this.tooltip = `${this.agent} - ${this.status}`;
        this.description = new Date(this.timestamp).toLocaleTimeString();
    }

    // Sets the icon based on the status
    iconPath = new vscode.ThemeIcon(
        this.status === 'success' ? 'check' : this.status === 'failure' ? 'error' : 'sync~spin'
    );

    // Context value for view/item/context
    contextValue = 'execution';
}

// Provides the data for the tree view
export class HistoryDataProvider implements vscode.TreeDataProvider<vscode.TreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<vscode.TreeItem | undefined | null | void> = new vscode.EventEmitter<vscode.TreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<vscode.TreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private executions: Execution[] = [];
    private storage: vscode.Memento;

    constructor(context: vscode.ExtensionContext) {
        this.storage = context.globalState;
        this.loadExecutions();
    }

    // Loads executions from storage
    private loadExecutions() {
        const storedExecutions = this.storage.get<any[]>('mcp-executions', []);
        this.executions = storedExecutions.map(
            (e: any) => new Execution(e.label, e.agent, e.status, new Date(e.timestamp), e.details)
        );
    }

    // Saves executions to storage
    private saveExecutions() {
        const dataToStore = this.executions.map(e => ({
            label: e.label,
            agent: e.agent,
            status: e.status,
            timestamp: e.timestamp,
            details: e.details
        }));
        this.storage.update('mcp-executions', dataToStore);
    }

    // Gets the tree item for an element
    getTreeItem(element: vscode.TreeItem): vscode.TreeItem {
        return element;
    }

    // Gets the children of an element or the root
    getChildren(element?: vscode.TreeItem): Thenable<vscode.TreeItem[]> {
        if (element instanceof Execution) {
            if (element.details) {
                return Promise.resolve(
                    element.details.split('\n').map(
                        (line) => new vscode.TreeItem(line, vscode.TreeItemCollapsibleState.None)
                    )
                );
            }
            return Promise.resolve([]);
        } else {
            return Promise.resolve(this.executions);
        }
    }

    // Adds a new execution to the history
    addExecution(execution: Execution) {
        this.executions.unshift(execution); // Add to the beginning of the array
        if (this.executions.length > 10) {
            this.executions.pop(); // Keep only the last 10
        }
        this.saveExecutions();
        this._onDidChangeTreeData.fire();
    }
}
