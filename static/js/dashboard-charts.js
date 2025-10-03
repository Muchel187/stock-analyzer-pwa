/**
 * Dashboard Charts Manager
 * Handles portfolio distribution, performance, and watchlist sparkline charts
 */

class DashboardChartsManager {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: 'rgba(102, 126, 234, 1)',
            primaryLight: 'rgba(102, 126, 234, 0.5)',
            success: 'rgba(72, 187, 120, 1)',
            successLight: 'rgba(72, 187, 120, 0.5)',
            danger: 'rgba(245, 101, 101, 1)',
            dangerLight: 'rgba(245, 101, 101, 0.5)',
            warning: 'rgba(237, 137, 54, 1)',
            info: 'rgba(66, 153, 225, 1)',
            purple: 'rgba(159, 122, 234, 1)',
            pink: 'rgba(237, 100, 166, 1)',
            teal: 'rgba(56, 178, 172, 1)',
            orange: 'rgba(246, 173, 85, 1)',
            gradient1: ['rgba(102, 126, 234, 0.8)', 'rgba(118, 75, 162, 0.8)'],
            gradient2: ['rgba(72, 187, 120, 0.8)', 'rgba(56, 178, 172, 0.8)'],
            gradient3: ['rgba(245, 101, 101, 0.8)', 'rgba(237, 100, 166, 0.8)']
        };
    }

    /**
     * Create Portfolio Distribution Doughnut Chart
     * Shows allocation of holdings by ticker
     * @param {string} canvasId - Canvas element ID
     * @param {Array} portfolioData - Array of {ticker, value, percentage}
     */
    createPortfolioDistribution(canvasId, portfolioData) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return null;
        }

        // Destroy existing chart
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const ctx = canvas.getContext('2d');

        // Prepare data
        const labels = portfolioData.map(item => item.ticker);
        const data = portfolioData.map(item => item.value);
        const percentages = portfolioData.map(item => item.percentage);

        // Color palette (cycle through available colors)
        const colorPalette = [
            this.colors.primary,
            this.colors.success,
            this.colors.warning,
            this.colors.info,
            this.colors.purple,
            this.colors.pink,
            this.colors.teal,
            this.colors.orange
        ];
        const backgroundColors = portfolioData.map((_, i) => colorPalette[i % colorPalette.length]);

        const config = {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Portfolio Allocation',
                    data: data,
                    backgroundColor: backgroundColors,
                    borderColor: 'rgba(26, 32, 44, 0.8)',
                    borderWidth: 2,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'right',
                        labels: {
                            color: 'rgba(255, 255, 255, 0.8)',
                            font: {
                                size: 12,
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            padding: 15,
                            usePointStyle: true,
                            generateLabels: (chart) => {
                                const data = chart.data;
                                return data.labels.map((label, i) => ({
                                    text: `${label} (${percentages[i].toFixed(1)}%)`,
                                    fillStyle: backgroundColors[i],
                                    hidden: false,
                                    index: i
                                }));
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(26, 32, 44, 0.95)',
                        titleColor: 'rgba(255, 255, 255, 0.9)',
                        bodyColor: 'rgba(255, 255, 255, 0.8)',
                        borderColor: 'rgba(102, 126, 234, 0.5)',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: true,
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const percentage = percentages[context.dataIndex];
                                return `${label}: $${value.toLocaleString('de-DE', {minimumFractionDigits: 2, maximumFractionDigits: 2})} (${percentage.toFixed(1)}%)`;
                            }
                        }
                    }
                },
                cutout: '65%', // Doughnut hole size
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, config);
        return this.charts[canvasId];
    }

    /**
     * Create Portfolio Performance Line Chart
     * Shows portfolio value over time
     * @param {string} canvasId - Canvas element ID
     * @param {Array} performanceData - Array of {date, value, change}
     */
    createPortfolioPerformance(canvasId, performanceData) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return null;
        }

        // Destroy existing chart
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const ctx = canvas.getContext('2d');

        // Prepare data
        const dates = performanceData.map(item => item.date);
        const values = performanceData.map(item => item.value);

        // Create gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(102, 126, 234, 0.4)');
        gradient.addColorStop(1, 'rgba(102, 126, 234, 0.01)');

        // Determine if overall performance is positive or negative
        const startValue = values[0] || 0;
        const endValue = values[values.length - 1] || 0;
        const isPositive = endValue >= startValue;

        const lineColor = isPositive ? this.colors.success : this.colors.danger;
        const fillGradient = ctx.createLinearGradient(0, 0, 0, 400);
        if (isPositive) {
            fillGradient.addColorStop(0, 'rgba(72, 187, 120, 0.4)');
            fillGradient.addColorStop(1, 'rgba(72, 187, 120, 0.01)');
        } else {
            fillGradient.addColorStop(0, 'rgba(245, 101, 101, 0.4)');
            fillGradient.addColorStop(1, 'rgba(245, 101, 101, 0.01)');
        }

        const config = {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Portfolio Value',
                    data: values,
                    borderColor: lineColor,
                    backgroundColor: fillGradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: lineColor,
                    pointHoverBorderColor: 'rgba(255, 255, 255, 0.8)',
                    pointHoverBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(26, 32, 44, 0.95)',
                        titleColor: 'rgba(255, 255, 255, 0.9)',
                        bodyColor: 'rgba(255, 255, 255, 0.8)',
                        borderColor: 'rgba(102, 126, 234, 0.5)',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: false,
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed.y;
                                return `Value: $${value.toLocaleString('de-DE', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.6)',
                            font: {
                                size: 11
                            },
                            maxTicksLimit: 8
                        }
                    },
                    y: {
                        display: true,
                        position: 'right',
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.6)',
                            font: {
                                size: 11
                            },
                            callback: (value) => {
                                return '$' + value.toLocaleString('de-DE', {maximumFractionDigits: 0});
                            }
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, config);
        return this.charts[canvasId];
    }

    /**
     * Create Watchlist Sparkline
     * Tiny line chart for individual watchlist items
     * @param {string} canvasId - Canvas element ID
     * @param {Array} priceData - Array of price values
     * @param {boolean} isPositive - Whether overall change is positive
     */
    createWatchlistSparkline(canvasId, priceData, isPositive = true) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return null;
        }

        // Destroy existing chart
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const ctx = canvas.getContext('2d');

        const lineColor = isPositive ? this.colors.success : this.colors.danger;
        const fillColor = isPositive ? 'rgba(72, 187, 120, 0.2)' : 'rgba(245, 101, 101, 0.2)';

        const config = {
            type: 'line',
            data: {
                labels: priceData.map((_, i) => i), // Just indices
                datasets: [{
                    data: priceData,
                    borderColor: lineColor,
                    backgroundColor: fillColor,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                },
                scales: {
                    x: {
                        display: false
                    },
                    y: {
                        display: false
                    }
                },
                animation: {
                    duration: 500
                },
                interaction: {
                    mode: null
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, config);
        return this.charts[canvasId];
    }

    /**
     * Create Sector Allocation Chart (Horizontal Bar)
     * Shows portfolio allocation by sector
     * @param {string} canvasId - Canvas element ID
     * @param {Array} sectorData - Array of {sector, value, percentage}
     */
    createSectorAllocation(canvasId, sectorData) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return null;
        }

        // Destroy existing chart
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const ctx = canvas.getContext('2d');

        // Prepare data
        const labels = sectorData.map(item => item.sector);
        const data = sectorData.map(item => item.percentage);

        // Color gradient for bars
        const backgroundColors = sectorData.map((_, i) => {
            const colors = [
                this.colors.primary,
                this.colors.success,
                this.colors.warning,
                this.colors.info,
                this.colors.purple
            ];
            return colors[i % colors.length];
        });

        const config = {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Sector Allocation (%)',
                    data: data,
                    backgroundColor: backgroundColors,
                    borderColor: 'rgba(26, 32, 44, 0.8)',
                    borderWidth: 1,
                    borderRadius: 8,
                    barThickness: 24
                }]
            },
            options: {
                indexAxis: 'y', // Horizontal bars
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(26, 32, 44, 0.95)',
                        titleColor: 'rgba(255, 255, 255, 0.9)',
                        bodyColor: 'rgba(255, 255, 255, 0.8)',
                        borderColor: 'rgba(102, 126, 234, 0.5)',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: true,
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed.x;
                                return `${context.label}: ${value.toFixed(1)}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.6)',
                            font: {
                                size: 11
                            },
                            callback: (value) => value + '%'
                        },
                        max: 100
                    },
                    y: {
                        display: true,
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            font: {
                                size: 12
                            }
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, config);
        return this.charts[canvasId];
    }

    /**
     * Destroy a specific chart
     * @param {string} canvasId - Canvas element ID
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
    destroyAllCharts() {
        Object.keys(this.charts).forEach(canvasId => {
            this.destroyChart(canvasId);
        });
    }
}

// Export for use in app.js
if (typeof window !== 'undefined') {
    window.DashboardChartsManager = DashboardChartsManager;
}
