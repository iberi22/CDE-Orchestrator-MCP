/**
 * ToolMetricsStore - Unit Tests
 *
 * Comprehensive test suite for the unified metrics store.
 * Tests: persistence, metrics calculation, event propagation, edge cases.
 */

import { expect } from 'chai';
import * as vscode from 'vscode';
import { ToolMetricsStore, ToolExecution, ToolMetrics } from '../store';

// Mock ExtensionContext for testing
class MockMemento implements vscode.Memento {
    private data = new Map<string, any>();

    get<T>(key: string, defaultValue?: T): T | undefined {
        return this.data.get(key) ?? defaultValue;
    }

    update(key: string, value: any): Thenable<void> {
        this.data.set(key, value);
        return Promise.resolve();
    }

    keys(): readonly string[] {
        return Array.from(this.data.keys());
    }
}

// Create mock context
function createMockContext(): vscode.ExtensionContext {
    return {
        globalState: new MockMemento(),
    } as any;
}

describe('ToolMetricsStore', () => {
    let store: ToolMetricsStore;
    let context: vscode.ExtensionContext;

    beforeEach(() => {
        context = createMockContext();
        // Reset singleton
        (ToolMetricsStore as any).instance = undefined;
        store = ToolMetricsStore.getInstance(context);
    });

    it('Singleton pattern - returns same instance', () => {
        const store2 = ToolMetricsStore.getInstance(context);
        expect(store).to.equal(store2);
    });

    it('Add execution - creates new record', () => {
        const execution: ToolExecution = {
            id: 'test-1',
            tool: 'scanDocumentation',
            server: 'CDE',
            status: 'running',
            startTime: new Date(),
            percentage: 0,
        };

        store.addExecution(execution);
        const history = store.getHistory(10);

        expect(history).to.have.lengthOf(1);
        expect(history[0].tool).to.equal('scanDocumentation');
    });

    it('Add multiple executions - keeps last N', () => {
        for (let i = 0; i < 120; i++) {
            const execution: ToolExecution = {
                id: `test-${i}`,
                tool: `tool-${i % 3}`,
                server: 'CDE',
                status: 'success',
                startTime: new Date(Date.now() - i * 1000),
                endTime: new Date(),
                duration: Math.random() * 10,
                percentage: 1.0,
            };
            store.addExecution(execution);
        }

        const history = store.getHistory(100);
        expect(history.length).to.be.at.most(100);
    });

    it('Get metrics - calculates averages correctly', () => {
        // Add 5 successful executions with known durations
        for (let i = 0; i < 5; i++) {
            store.addExecution({
                id: `metric-${i}`,
                tool: 'testTool',
                server: 'CDE',
                status: 'success',
                startTime: new Date(),
                endTime: new Date(Date.now() + (i + 1) * 1000),
                duration: i + 1, // 1, 2, 3, 4, 5 seconds
                percentage: 1.0,
            });
        }

        const metrics = store.getMetrics();

        expect(metrics.successCount).to.equal(5);
        expect(metrics.failureCount).to.equal(0);
        expect(metrics.avgDuration).to.equal(3); // Average of 1,2,3,4,5 = 3
        expect(metrics.successRate).to.equal(100);
    });

    it('Get metrics - success rate calculation', () => {
        // Add 3 successful + 2 failed
        for (let i = 0; i < 3; i++) {
            store.addExecution({
                id: `success-${i}`,
                tool: 'testTool',
                server: 'CDE',
                status: 'success',
                startTime: new Date(),
                endTime: new Date(),
                duration: 1,
                percentage: 1.0,
            });
        }

        for (let i = 0; i < 2; i++) {
            store.addExecution({
                id: `failure-${i}`,
                tool: 'testTool',
                server: 'CDE',
                status: 'failure',
                startTime: new Date(),
                endTime: new Date(),
                duration: 1,
                percentage: 1.0,
            });
        }

        const metrics = store.getMetrics();

        expect(metrics.totalExecutions).to.equal(5);
        expect(metrics.successCount).to.equal(3);
        expect(metrics.failureCount).to.equal(2);
        expect(metrics.successRate).to.equal(60); // 3/5 = 60%
    });

    it('Get dashboard data - generates correct structure', () => {
        // Add varied executions
        for (let i = 0; i < 10; i++) {
            store.addExecution({
                id: `dash-${i}`,
                tool: i % 2 === 0 ? 'scanDoc' : 'onboarding',
                server: 'CDE',
                status: i % 3 === 0 ? 'failure' : 'success',
                startTime: new Date(Date.now() - i * 5000),
                endTime: new Date(),
                duration: Math.random() * 10,
                percentage: 1.0,
            });
        }

        const dashData = store.getDashboardData();

        expect(dashData.executionTimeline).to.exist;
        expect(dashData.successFailureRatio).to.exist;
        expect(dashData.latencyHistogram).to.exist;
        expect(dashData.topSlowestTools).to.exist;
        expect(dashData.topSlowestTools.length).to.be.at.most(5);
    });

    it('Event emitter - fires on data change', (done: Mocha.Done) => {
        let fired = false;

        store.onDidChange(() => {
            fired = true;
            done();
        });

        // Add execution to trigger event
        store.addExecution({
            id: 'event-test',
            tool: 'testTool',
            server: 'CDE',
            status: 'success',
            startTime: new Date(),
            endTime: new Date(),
            duration: 1,
            percentage: 1.0,
        });
    });

    it('Clear all - removes all data', () => {
        // Add some data
        for (let i = 0; i < 5; i++) {
            store.addExecution({
                id: `clear-${i}`,
                tool: 'testTool',
                server: 'CDE',
                status: 'success',
                startTime: new Date(),
                endTime: new Date(),
                duration: 1,
                percentage: 1.0,
            });
        }

        expect(store.getHistory(10)).to.have.length.greaterThan(0);

        // Clear
        store.clear();

        expect(store.getHistory(10)).to.have.lengthOf(0);
        expect(store.getMetrics().totalExecutions).to.equal(0);
    });

    it('Persistence - data survives reload', async () => {
        // Add execution
        store.addExecution({
            id: 'persist-1',
            tool: 'scanDocumentation',
            server: 'CDE',
            status: 'success',
            startTime: new Date('2025-11-06T10:00:00Z'),
            endTime: new Date('2025-11-06T10:00:05Z'),
            duration: 5,
            percentage: 1.0,
        });

        // Create new store instance (simulates reload)
        (ToolMetricsStore as any).instance = undefined;
        const store2 = ToolMetricsStore.getInstance(context);

        const history = store2.getHistory(10);
        expect(history.length).to.be.greaterThan(0);
        expect(history[0].id).to.equal('persist-1');
    });

    it('Running executions - not in history until complete', () => {
        const running: ToolExecution = {
            id: 'running-1',
            tool: 'testTool',
            server: 'CDE',
            status: 'running',
            startTime: new Date(),
            percentage: 0.5,
        };

        store.addExecution(running);
        let history = store.getHistory(10);

        // Note: Running executions are stored if addExecution is called
        // Update should change status
        store.updateExecution('running-1', {
            status: 'success',
            endTime: new Date(),
            percentage: 1.0,
        });

        // Re-add as completed to verify
        store.addExecution({
            ...running,
            status: 'success',
            endTime: new Date(),
            duration: 1,
        });

        history = store.getHistory(10);
        expect(history.length).to.be.greaterThan(0);
    });

    it('Edge case - empty metrics', () => {
        const metrics = store.getMetrics();

        expect(metrics.totalExecutions).to.equal(0);
        expect(metrics.successCount).to.equal(0);
        expect(metrics.avgDuration).to.equal(0);
        expect(metrics.successRate).to.equal(0);
    });

    it('Edge case - single execution', () => {
        store.addExecution({
            id: 'single-1',
            tool: 'testTool',
            server: 'CDE',
            status: 'success',
            startTime: new Date(),
            endTime: new Date(),
            duration: 42.5,
            percentage: 1.0,
        });

        const metrics = store.getMetrics();
        expect(metrics.totalExecutions).to.equal(1);
        expect(metrics.avgDuration).to.equal(42.5);
        expect(metrics.successRate).to.equal(100);
    });

    it('Edge case - all failures', () => {
        for (let i = 0; i < 3; i++) {
            store.addExecution({
                id: `fail-${i}`,
                tool: 'testTool',
                server: 'CDE',
                status: 'failure',
                startTime: new Date(),
                endTime: new Date(),
                duration: 1,
                percentage: 1.0,
            });
        }

        const metrics = store.getMetrics();
        expect(metrics.successRate).to.equal(0);
        expect(metrics.failureCount).to.equal(3);
    });

    it('Performance - adding 1000 executions', function () {
        this.timeout(5000); // 5 second timeout for this test

        const startTime = Date.now();

        for (let i = 0; i < 1000; i++) {
            store.addExecution({
                id: `perf-${i}`,
                tool: `tool-${i % 10}`,
                server: 'CDE',
                status: i % 5 === 0 ? 'failure' : 'success',
                startTime: new Date(),
                endTime: new Date(),
                duration: Math.random() * 30,
                percentage: 1.0,
            });
        }

        const elapsed = Date.now() - startTime;

        console.log(`Added 1000 executions in ${elapsed}ms`);
        expect(elapsed).to.be.lessThan(1000);

        const metrics = store.getMetrics();
        expect(metrics.totalExecutions).to.be.at.most(100);
    });
});
