const vscode = acquireVsCodeApi();

const charts = {};

function createChart(id, type, data, options = {}) {
    const ctx = document.getElementById(id).getContext('2d');
    if (charts[id]) {
        charts[id].destroy();
    }
    charts[id] = new Chart(ctx, { type, data, options });
}

window.addEventListener('message', event => {
    const message = event.data;
    if (message.command === 'updateData') {
        const data = message.data;
        createChart('timeline-chart', 'bar', data.timeline, { indexAxis: 'y' });
        createChart('ratio-chart', 'doughnut', data.ratio);
        createChart('latency-chart', 'bar', data.latency);
        createChart('slowest-chart', 'bar', data.slowest, { indexAxis: 'y' });
    }
});

document.getElementById('refresh-button').addEventListener('click', () => {
    vscode.postMessage({ command: 'refresh' });
});
