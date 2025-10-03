/**
 * Market Indices Live Charts
 * Displays live charts for major indices (DAX, S&P500, NASDAQ)
 */

class MarketIndicesWidget {
    constructor() {
        this.charts = {};
        this.updateInterval = null;
        // Use ETFs as proxies since index symbols (^GDAXI, ^GSPC, ^IXIC) aren't supported by APIs
        this.indices = [
            { symbol: 'SPY', name: 'S&P 500 ETF', color: 'rgb(72, 187, 120)' },
            { symbol: 'QQQ', name: 'NASDAQ-100 ETF', color: 'rgb(245, 101, 101)' },
            { symbol: 'SAP', name: 'DAX (SAP)', color: 'rgb(102, 126, 234)' }
        ];
    }

    /**
     * Initialize all index charts
     */
    async init(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        // Create grid layout for charts
        container.innerHTML = `
            <div class="market-indices-grid">
                ${this.indices.map(index => `
                    <div class="index-chart-card" id="${this.getChartId(index.symbol)}-card">
                        <div class="index-chart-header">
                            <div class="index-name">${index.name}</div>
                            <div class="index-value" id="${this.getChartId(index.symbol)}-value">Loading...</div>
                            <div class="index-change" id="${this.getChartId(index.symbol)}-change">-</div>
                        </div>
                        <div class="index-chart-container">
                            <canvas id="${this.getChartId(index.symbol)}"></canvas>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        // Load charts for all indices
        await Promise.all(this.indices.map(index => this.loadIndexChart(index)));

        // Start auto-update (every 5 minutes)
        this.startAutoUpdate();
    }

    /**
     * Get chart ID from symbol
     */
    getChartId(symbol) {
        return 'chart-' + symbol.replace('^', '');
    }

    /**
     * Load single index chart
     */
    async loadIndexChart(index) {
        try {
            // Fetch historical data (5 days for smooth chart with enough data points)
            const response = await fetch(`/api/stock/${index.symbol}/history?period=5d`);
            const result = await response.json();

            if (!result.data || result.data.length === 0) {
                throw new Error('No data available');
            }

            const data = result.data;
            const chartId = this.getChartId(index.symbol);

            // Update current value and change
            const currentPrice = data[data.length - 1].close;
            const openPrice = data[0].open;
            const change = currentPrice - openPrice;
            const changePercent = (change / openPrice) * 100;

            document.getElementById(`${chartId}-value`).textContent =
                currentPrice.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

            const changeEl = document.getElementById(`${chartId}-change`);
            changeEl.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)} (${changePercent.toFixed(2)}%)`;
            changeEl.className = `index-change ${change >= 0 ? 'positive' : 'negative'}`;

            // Create sparkline chart
            this.createSparklineChart(chartId, data, index.color, change >= 0);

        } catch (error) {
            console.error(`Error loading ${index.name} chart:`, error);
            const chartId = this.getChartId(index.symbol);
            document.getElementById(`${chartId}-value`).textContent = 'Error';
            document.getElementById(`${chartId}-change`).textContent = 'Failed to load';
        }
    }

    /**
     * Create sparkline chart
     */
    createSparklineChart(chartId, data, color, isPositive) {
        const canvas = document.getElementById(chartId);
        if (!canvas) {
            console.error(`Canvas ${chartId} not found`);
            return;
        }

        // Destroy existing chart
        if (this.charts[chartId]) {
            this.charts[chartId].destroy();
        }

        const ctx = canvas.getContext('2d');
        const prices = data.map(d => d.close);
        const times = data.map(d => {
            const date = new Date(d.date);
            // Format as "DD.MM" for multi-day charts
            return date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' });
        });

        // Create gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        if (isPositive) {
            gradient.addColorStop(0, 'rgba(72, 187, 120, 0.3)');
            gradient.addColorStop(1, 'rgba(72, 187, 120, 0.01)');
        } else {
            gradient.addColorStop(0, 'rgba(245, 101, 101, 0.3)');
            gradient.addColorStop(1, 'rgba(245, 101, 101, 0.01)');
        }

        this.charts[chartId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: times,
                datasets: [{
                    data: prices,
                    borderColor: color,
                    backgroundColor: gradient,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    pointHoverBackgroundColor: color,
                    pointHoverBorderColor: '#fff',
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
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(26, 32, 44, 0.95)',
                        titleColor: 'rgba(255, 255, 255, 0.9)',
                        bodyColor: 'rgba(255, 255, 255, 0.8)',
                        borderColor: color,
                        borderWidth: 1,
                        padding: 10,
                        displayColors: false,
                        callbacks: {
                            title: (items) => items[0].label,
                            label: (context) => {
                                const value = context.parsed.y;
                                return value.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                            }
                        }
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
                }
            }
        });
    }

    /**
     * Start auto-update
     */
    startAutoUpdate() {
        // Update every 5 minutes
        this.updateInterval = setInterval(() => {
            this.indices.forEach(index => this.loadIndexChart(index));
        }, 5 * 60 * 1000);
    }

    /**
     * Stop auto-update
     */
    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    /**
     * Destroy all charts
     */
    destroy() {
        this.stopAutoUpdate();
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }
}

// Export for use in app.js
if (typeof window !== 'undefined') {
    window.MarketIndicesWidget = MarketIndicesWidget;
}
