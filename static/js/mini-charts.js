/**
 * Mini Charts for Dashboard Widgets
 * Provides small sparkline charts with expand functionality
 */

class MiniChartManager {
    constructor(app) {
        this.app = app;
        this.charts = {};
        this.modalChart = null;
    }

    /**
     * Create a mini sparkline chart for a ticker
     * @param {string} containerId - ID of the container element
     * @param {string} ticker - Stock ticker symbol
     * @param {number} currentPrice - Current stock price
     */
    async createMiniChart(containerId, ticker, currentPrice) {
        try {
            // Fetch 30-day history for sparkline
            const history = await api.getStockHistory(ticker, '1mo');

            if (!history || !history.data || history.data.length === 0) {
                console.log(`No history data for mini chart: ${ticker}`);
                return null;
            }

            const container = document.getElementById(containerId);
            if (!container) {
                console.error(`Container not found: ${containerId}`);
                return null;
            }

            // Create canvas for sparkline
            const canvas = document.createElement('canvas');
            canvas.id = `mini-chart-${ticker}`;
            canvas.width = 100;
            canvas.height = 40;
            canvas.style.cursor = 'pointer';
            canvas.onclick = () => this.expandChart(ticker, currentPrice);

            container.innerHTML = '';
            container.appendChild(canvas);

            // Prepare data
            const prices = history.data.map(d => parseFloat(d.close));
            const dates = history.data.map(d => d.date);

            // Calculate price change for color
            const priceChange = currentPrice - prices[0];
            const lineColor = priceChange >= 0 ? '#10b981' : '#ef4444';

            // Destroy existing chart if any
            if (this.charts[ticker]) {
                this.charts[ticker].destroy();
            }

            // Create sparkline chart
            this.charts[ticker] = new Chart(canvas, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        data: prices,
                        borderColor: lineColor,
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 0,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: false,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: { enabled: false }
                    },
                    scales: {
                        x: { display: false },
                        y: { display: false }
                    }
                }
            });

            return this.charts[ticker];
        } catch (error) {
            console.error(`Error creating mini chart for ${ticker}:`, error);
            return null;
        }
    }

    /**
     * Expand chart in modal
     * @param {string} ticker - Stock ticker symbol
     * @param {number} currentPrice - Current stock price
     */
    async expandChart(ticker, currentPrice) {
        try {
            // Create modal if it doesn't exist
            let modal = document.getElementById('chartExpandModal');
            if (!modal) {
                this.createChartModal();
                modal = document.getElementById('chartExpandModal');
            }

            // Show loading state
            const modalContent = modal.querySelector('.modal-content');
            modalContent.innerHTML = `
                <div class="modal-header">
                    <h3>${ticker} - Kursverlauf</h3>
                    <button class="close-btn" onclick="miniChartManager.closeExpandedChart()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="loading-spinner">Lade Chart...</div>
                </div>
            `;

            // Show modal
            modal.style.display = 'flex';

            // Fetch full history
            const history = await api.getStockHistory(ticker, '3mo');

            if (!history || !history.data || history.data.length === 0) {
                modalContent.querySelector('.modal-body').innerHTML =
                    '<p>Keine Daten verfügbar</p>';
                return;
            }

            // Prepare data
            const dates = history.data.map(d => d.date);
            const prices = history.data.map(d => parseFloat(d.close));
            const volumes = history.data.map(d => parseInt(d.volume));

            // Calculate statistics
            const priceChange = currentPrice - prices[0];
            const priceChangePercent = ((priceChange / prices[0]) * 100).toFixed(2);
            const minPrice = Math.min(...prices);
            const maxPrice = Math.max(...prices);
            const avgVolume = (volumes.reduce((a, b) => a + b, 0) / volumes.length / 1000000).toFixed(2);

            // Update modal content
            modalContent.innerHTML = `
                <div class="modal-header">
                    <div>
                        <h3>${ticker} - Kursverlauf (3 Monate)</h3>
                        <div class="chart-stats">
                            <span>Aktuell: $${currentPrice.toFixed(2)}</span>
                            <span class="${priceChange >= 0 ? 'positive' : 'negative'}">
                                ${priceChange >= 0 ? '▲' : '▼'} ${Math.abs(priceChangePercent)}%
                            </span>
                            <span>Min: $${minPrice.toFixed(2)}</span>
                            <span>Max: $${maxPrice.toFixed(2)}</span>
                            <span>Ø Volumen: ${avgVolume}M</span>
                        </div>
                    </div>
                    <button class="close-btn" onclick="miniChartManager.closeExpandedChart()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="chart-container-modal">
                        <canvas id="expandedPriceChart"></canvas>
                    </div>
                    <div class="chart-container-modal">
                        <h4>Volumen</h4>
                        <canvas id="expandedVolumeChart"></canvas>
                    </div>
                    <div class="modal-actions">
                        <button class="btn btn-primary" onclick="app.navigateToAnalysis('${ticker}')">
                            Vollständige Analyse
                        </button>
                    </div>
                </div>
            `;

            // Render charts
            this.renderExpandedPriceChart(dates, prices, currentPrice);
            this.renderExpandedVolumeChart(dates, volumes);

        } catch (error) {
            console.error(`Error expanding chart for ${ticker}:`, error);
            this.app.showNotification('Fehler beim Laden des Charts', 'error');
        }
    }

    /**
     * Create chart modal element
     */
    createChartModal() {
        const modal = document.createElement('div');
        modal.id = 'chartExpandModal';
        modal.className = 'chart-modal';
        modal.innerHTML = '<div class="modal-content"></div>';

        // Close on background click
        modal.onclick = (e) => {
            if (e.target === modal) {
                this.closeExpandedChart();
            }
        };

        document.body.appendChild(modal);
    }

    /**
     * Close expanded chart modal
     */
    closeExpandedChart() {
        const modal = document.getElementById('chartExpandModal');
        if (modal) {
            modal.style.display = 'none';

            // Destroy modal chart
            if (this.modalChart) {
                this.modalChart.destroy();
                this.modalChart = null;
            }
            if (this.modalVolumeChart) {
                this.modalVolumeChart.destroy();
                this.modalVolumeChart = null;
            }
        }
    }

    /**
     * Render expanded price chart
     */
    renderExpandedPriceChart(dates, prices, currentPrice) {
        const ctx = document.getElementById('expandedPriceChart');
        if (!ctx) return;

        // Destroy existing
        if (this.modalChart) {
            this.modalChart.destroy();
        }

        const priceChange = currentPrice - prices[0];
        const lineColor = priceChange >= 0 ? '#10b981' : '#ef4444';

        this.modalChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Preis',
                    data: prices,
                    borderColor: lineColor,
                    backgroundColor: `${lineColor}20`,
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: (context) => `Preis: $${context.parsed.y.toFixed(2)}`
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        ticks: { maxTicksLimit: 8 }
                    },
                    y: {
                        display: true,
                        ticks: {
                            callback: (value) => '$' + value.toFixed(2)
                        }
                    }
                }
            }
        });
    }

    /**
     * Render expanded volume chart
     */
    renderExpandedVolumeChart(dates, volumes) {
        const ctx = document.getElementById('expandedVolumeChart');
        if (!ctx) return;

        // Destroy existing
        if (this.modalVolumeChart) {
            this.modalVolumeChart.destroy();
        }

        this.modalVolumeChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Volumen',
                    data: volumes,
                    backgroundColor: '#667eea',
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const volume = context.parsed.y;
                                return `Volumen: ${(volume / 1000000).toFixed(2)}M`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        ticks: { maxTicksLimit: 8 }
                    },
                    y: {
                        display: true,
                        ticks: {
                            callback: (value) => (value / 1000000).toFixed(1) + 'M'
                        }
                    }
                }
            }
        });
    }

    /**
     * Destroy all charts
     */
    destroyAll() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};

        if (this.modalChart) {
            this.modalChart.destroy();
            this.modalChart = null;
        }
        if (this.modalVolumeChart) {
            this.modalVolumeChart.destroy();
            this.modalVolumeChart = null;
        }
    }
}

// Initialize on page load
let miniChartManager;
document.addEventListener('DOMContentLoaded', () => {
    if (typeof app !== 'undefined') {
        miniChartManager = new MiniChartManager(app);
    }
});
