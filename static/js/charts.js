// Chart.js implementations for the application

class ChartManager {
    constructor() {
        this.charts = {};
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            }
        };
    }

    createPortfolioChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        // Destroy existing chart if exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#48bb78',
                        '#ed8936',
                        '#4299e1',
                        '#f56565'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }

    createPriceChart(canvasId, priceData) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        // Destroy existing chart if exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: priceData.map(d => d.date),
                datasets: [{
                    label: 'Schlusskurs',
                    data: priceData.map(d => d.close),
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                ...this.defaultOptions,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        }
                    },
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toFixed(2);
                            }
                        }
                    }
                }
            }
        });
    }

    createDiversificationChart(canvasId, diversificationData) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        // Destroy existing chart if exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        this.charts[canvasId] = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(diversificationData.by_sector),
                datasets: [{
                    data: Object.values(diversificationData.by_sector),
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#48bb78',
                        '#ed8936',
                        '#4299e1',
                        '#f56565',
                        '#38b2ac',
                        '#d69e2e'
                    ]
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed.toFixed(2) + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    destroyChart(canvasId) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
            delete this.charts[canvasId];
        }
    }

    destroyAllCharts() {
        Object.keys(this.charts).forEach(canvasId => {
            this.destroyChart(canvasId);
        });
    }
}

// Create global chart manager instance
const chartManager = new ChartManager();