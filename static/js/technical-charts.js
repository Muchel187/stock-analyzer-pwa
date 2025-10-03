/**
 * Technical Analysis Charts with Advanced Indicators
 * Displays Bollinger Bands, MACD, RSI, Volume with overlays
 */

class TechnicalChartsManager {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: 'rgb(102, 126, 234)',
            secondary: 'rgb(118, 75, 162)',
            success: 'rgb(72, 187, 120)',
            danger: 'rgb(245, 101, 101)',
            warning: 'rgb(237, 137, 54)',
            info: 'rgb(66, 153, 225)',
            grid: 'rgba(255, 255, 255, 0.05)',
            text: 'rgba(255, 255, 255, 0.7)'
        };
    }

    /**
     * Main Price Chart with Bollinger Bands
     */
    createPriceChartWithBollinger(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            console.error(`Canvas ${canvasId} not found`);
            return null;
        }

        // Destroy existing chart
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const { dates, prices, bollinger } = data;

        const datasets = [
            {
                label: 'Price',
                data: prices,
                borderColor: this.colors.primary,
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 5,
                order: 1
            }
        ];

        // Add Bollinger Bands if available
        if (bollinger) {
            datasets.push(
                {
                    label: 'Upper Band',
                    data: bollinger.upper,
                    borderColor: 'rgba(237, 137, 54, 0.5)',
                    borderWidth: 1,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0,
                    order: 2
                },
                {
                    label: 'Middle Band (SMA 20)',
                    data: bollinger.middle,
                    borderColor: 'rgba(255, 255, 255, 0.3)',
                    borderWidth: 1,
                    borderDash: [2, 2],
                    fill: false,
                    pointRadius: 0,
                    order: 2
                },
                {
                    label: 'Lower Band',
                    data: bollinger.lower,
                    borderColor: 'rgba(72, 187, 120, 0.5)',
                    borderWidth: 1,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0,
                    order: 2
                }
            );
        }

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Price with Bollinger Bands',
                        color: this.colors.text,
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: this.colors.text,
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 25, 40, 0.95)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: this.colors.primary,
                        borderWidth: 1,
                        padding: 12,
                        displayColors: true,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                label += '$' + context.parsed.y.toFixed(2);
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: this.colors.grid,
                            borderColor: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: this.colors.text,
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        position: 'right',
                        grid: {
                            color: this.colors.grid,
                            borderColor: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: this.colors.text,
                            callback: function(value) {
                                return '$' + value.toFixed(2);
                            }
                        }
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    /**
     * MACD Chart with Signal Line and Histogram
     */
    createMACDChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            console.error(`Canvas ${canvasId} not found`);
            return null;
        }

        // Destroy existing chart
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const { dates, macd, signal, histogram } = data;

        // Color histogram bars based on positive/negative
        const histogramColors = histogram.map(val =>
            val >= 0 ? 'rgba(72, 187, 120, 0.5)' : 'rgba(245, 101, 101, 0.5)'
        );

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dates,
                datasets: [
                    {
                        type: 'line',
                        label: 'MACD',
                        data: macd,
                        borderColor: this.colors.primary,
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        pointRadius: 0,
                        pointHoverRadius: 5,
                        tension: 0.4,
                        order: 1
                    },
                    {
                        type: 'line',
                        label: 'Signal',
                        data: signal,
                        borderColor: this.colors.warning,
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointRadius: 0,
                        pointHoverRadius: 5,
                        tension: 0.4,
                        order: 1
                    },
                    {
                        type: 'bar',
                        label: 'Histogram',
                        data: histogram,
                        backgroundColor: histogramColors,
                        borderWidth: 0,
                        order: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'MACD (Moving Average Convergence Divergence)',
                        color: this.colors.text,
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: this.colors.text,
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 25, 40, 0.95)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: this.colors.primary,
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                label += context.parsed.y.toFixed(4);
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: this.colors.grid,
                            borderColor: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: this.colors.text,
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        position: 'right',
                        grid: {
                            color: this.colors.grid,
                            borderColor: 'rgba(255, 255, 255, 0.1)',
                            drawBorder: true
                        },
                        ticks: {
                            color: this.colors.text
                        }
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    /**
     * RSI Chart with Overbought/Oversold Zones
     */
    createRSIChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            console.error(`Canvas ${canvasId} not found`);
            return null;
        }

        // Destroy existing chart
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const { dates, rsi } = data;

        // Create overbought (70) and oversold (30) reference lines
        const overbought = new Array(dates.length).fill(70);
        const oversold = new Array(dates.length).fill(30);
        const middle = new Array(dates.length).fill(50);

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: 'RSI',
                        data: rsi,
                        borderColor: this.colors.primary,
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 5,
                        order: 1
                    },
                    {
                        label: 'Overbought (70)',
                        data: overbought,
                        borderColor: 'rgba(245, 101, 101, 0.5)',
                        borderWidth: 1,
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0,
                        order: 2
                    },
                    {
                        label: 'Oversold (30)',
                        data: oversold,
                        borderColor: 'rgba(72, 187, 120, 0.5)',
                        borderWidth: 1,
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0,
                        order: 2
                    },
                    {
                        label: 'Middle (50)',
                        data: middle,
                        borderColor: 'rgba(255, 255, 255, 0.2)',
                        borderWidth: 1,
                        borderDash: [2, 2],
                        fill: false,
                        pointRadius: 0,
                        order: 3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'RSI (Relative Strength Index)',
                        color: this.colors.text,
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: this.colors.text,
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 25, 40, 0.95)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: this.colors.primary,
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                if (context.dataset.label === 'RSI') {
                                    const value = context.parsed.y;
                                    let status = '';
                                    if (value > 70) status = ' (Overbought)';
                                    else if (value < 30) status = ' (Oversold)';
                                    return `RSI: ${value.toFixed(2)}${status}`;
                                }
                                return '';
                            }
                        }
                    },
                    annotation: {
                        annotations: {
                            overboughtZone: {
                                type: 'box',
                                yMin: 70,
                                yMax: 100,
                                backgroundColor: 'rgba(245, 101, 101, 0.1)',
                                borderWidth: 0
                            },
                            oversoldZone: {
                                type: 'box',
                                yMin: 0,
                                yMax: 30,
                                backgroundColor: 'rgba(72, 187, 120, 0.1)',
                                borderWidth: 0
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: this.colors.grid,
                            borderColor: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: this.colors.text,
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        position: 'right',
                        min: 0,
                        max: 100,
                        grid: {
                            color: this.colors.grid,
                            borderColor: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: this.colors.text,
                            stepSize: 10
                        }
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    /**
     * Volume Chart with Moving Average Overlay
     */
    createVolumeChartWithMA(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            console.error(`Canvas ${canvasId} not found`);
            return null;
        }

        // Destroy existing chart
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const { dates, volumes, volumeMA } = data;

        // Color volumes based on price direction (if available)
        const volumeColors = data.priceChanges
            ? data.priceChanges.map(change =>
                change >= 0 ? 'rgba(72, 187, 120, 0.6)' : 'rgba(245, 101, 101, 0.6)'
              )
            : new Array(volumes.length).fill('rgba(102, 126, 234, 0.6)');

        const datasets = [
            {
                type: 'bar',
                label: 'Volume',
                data: volumes,
                backgroundColor: volumeColors,
                borderWidth: 0,
                order: 2
            }
        ];

        // Add Volume MA if available
        if (volumeMA) {
            datasets.push({
                type: 'line',
                label: 'Volume MA (20)',
                data: volumeMA,
                borderColor: this.colors.warning,
                backgroundColor: 'transparent',
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 5,
                tension: 0.4,
                order: 1
            });
        }

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dates,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Trading Volume',
                        color: this.colors.text,
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: this.colors.text,
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 25, 40, 0.95)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: this.colors.primary,
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                const value = context.parsed.y;
                                if (value >= 1000000) {
                                    label += (value / 1000000).toFixed(2) + 'M';
                                } else if (value >= 1000) {
                                    label += (value / 1000).toFixed(2) + 'K';
                                } else {
                                    label += value.toLocaleString();
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: this.colors.grid,
                            borderColor: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: this.colors.text,
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        position: 'right',
                        beginAtZero: true,
                        grid: {
                            color: this.colors.grid,
                            borderColor: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: this.colors.text,
                            maxTicksLimit: 5,
                            callback: function(value) {
                                if (value >= 1000000) {
                                    return (value / 1000000).toFixed(1) + 'M';
                                } else if (value >= 1000) {
                                    return (value / 1000).toFixed(0) + 'K';
                                }
                                return value;
                            }
                        }
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    /**
     * Combined Technical Analysis Dashboard
     * Creates all charts at once with proper layout
     */
    createTechnicalDashboard(containerId, stockData) {
        console.log('[TechnicalCharts] Creating dashboard for', stockData.ticker);

        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        // Create HTML structure for charts
        container.innerHTML = `
            <div class="technical-charts-grid">
                <div class="chart-card">
                    <canvas id="priceWithBollinger"></canvas>
                </div>
                <div class="chart-card">
                    <canvas id="macdChart"></canvas>
                </div>
                <div class="chart-card">
                    <canvas id="rsiChart"></canvas>
                </div>
                <div class="chart-card">
                    <canvas id="volumeChart"></canvas>
                </div>
            </div>
        `;

        // Wait for DOM to be ready
        setTimeout(() => {
            // Create each chart
            this.createPriceChartWithBollinger('priceWithBollinger', {
                dates: stockData.dates,
                prices: stockData.prices,
                bollinger: stockData.bollinger
            });

            this.createMACDChart('macdChart', {
                dates: stockData.dates,
                macd: stockData.macd.macd,
                signal: stockData.macd.signal,
                histogram: stockData.macd.histogram
            });

            this.createRSIChart('rsiChart', {
                dates: stockData.dates,
                rsi: stockData.rsi
            });

            this.createVolumeChartWithMA('volumeChart', {
                dates: stockData.dates,
                volumes: stockData.volumes,
                volumeMA: stockData.volumeMA,
                priceChanges: stockData.priceChanges
            });

            console.log('[TechnicalCharts] Dashboard created successfully');
        }, 100);
    }

    /**
     * Destroy a specific chart
     */
    destroyChart(canvasId) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
            delete this.charts[canvasId];
        }
    }

    /**
     * Destroy all charts
     */
    destroyAll() {
        Object.keys(this.charts).forEach(canvasId => {
            this.destroyChart(canvasId);
        });
    }
}

// Export for global use
window.TechnicalChartsManager = TechnicalChartsManager;
