/**
 * Advanced Interactive Chart with Indicators and Drawing Tools
 * TradingView-inspired chart component
 */

class AdvancedChart {
    constructor(canvasId, options = {}) {
        this.canvasId = canvasId;
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return;
        }

        this.options = {
            height: options.height || 400,
            showVolume: options.showVolume !== false,
            showGrid: options.showGrid !== false,
            candlestick: options.candlestick !== false,
            ...options
        };

        this.chart = null;
        this.data = null;
        this.indicators = {
            sma20: false,
            sma50: false,
            sma200: false,
            ema12: false,
            ema26: false,
            bb: false,
            rsi: false,
            macd: false
        };
        this.trendlines = [];
        this.drawingMode = false;
        this.currentTrendline = null;

        this.init();
    }

    init() {
        // Set canvas height
        this.canvas.style.height = `${this.options.height}px`;

        // Add event listeners for drawing
        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.onMouseUp(e));
    }

    /**
     * Load and display chart data
     */
    async loadData(ticker, period = '6mo') {
        try {
            // Fetch historical data
            const response = await fetch(`/api/stock/${ticker}/history?period=${period}`);
            const result = await response.json();

            if (!result.data || result.data.length === 0) {
                throw new Error('No data available');
            }

            this.data = result.data;
            this.ticker = ticker;
            this.period = period;

            this.render();
        } catch (error) {
            console.error('Error loading chart data:', error);
            this.showError('Failed to load chart data');
        }
    }

    /**
     * Render the main chart
     */
    render() {
        if (!this.data || this.data.length === 0) return;

        // Destroy existing chart
        if (this.chart) {
            this.chart.destroy();
        }

        const ctx = this.canvas.getContext('2d');
        const dates = this.data.map(d => d.date);

        const datasets = [];

        // Main price dataset (candlestick or line)
        if (this.options.candlestick && this.data[0].high) {
            // Candlestick chart
            const candleData = this.data.map(d => ({
                x: d.date,
                o: d.open,
                h: d.high,
                l: d.low,
                c: d.close
            }));

            datasets.push({
                label: this.ticker,
                data: candleData,
                type: 'candlestick',
                color: {
                    up: 'rgba(72, 187, 120, 1)',
                    down: 'rgba(245, 101, 101, 1)',
                    unchanged: 'rgba(128, 128, 128, 1)'
                }
            });
        } else {
            // Line chart
            const prices = this.data.map(d => d.close);
            datasets.push({
                label: this.ticker,
                data: prices,
                borderColor: 'rgb(102, 126, 234)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.1,
                pointRadius: 0,
                pointHoverRadius: 4
            });
        }

        // Add indicators
        this.addIndicatorDatasets(datasets, dates);

        // Create chart
        this.chart = new Chart(ctx, {
            type: this.options.candlestick ? 'candlestick' : 'line',
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
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: 'rgba(255, 255, 255, 0.8)',
                            font: { size: 11 },
                            usePointStyle: true,
                            filter: (legendItem) => {
                                // Only show enabled indicators
                                return legendItem.text === this.ticker ||
                                       this.indicators[legendItem.text.toLowerCase().replace(/\s/g, '')];
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
                                const label = context.dataset.label || '';
                                const value = context.parsed.y;
                                return `${label}: $${value.toFixed(2)}`;
                            }
                        }
                    },
                    crosshair: {
                        line: {
                            color: 'rgba(255, 255, 255, 0.3)',
                            width: 1
                        },
                        sync: {
                            enabled: false
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: this.options.showGrid,
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.6)',
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        display: true,
                        position: 'right',
                        grid: {
                            display: this.options.showGrid,
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.6)',
                            callback: (value) => '$' + value.toFixed(2)
                        }
                    }
                },
                animation: {
                    duration: 500
                }
            }
        });

        // Draw trendlines
        this.drawTrendlines();
    }

    /**
     * Add indicator datasets to chart
     */
    addIndicatorDatasets(datasets, dates) {
        const prices = this.data.map(d => d.close);

        // SMA 20
        if (this.indicators.sma20) {
            const sma20 = this.calculateSMA(prices, 20);
            datasets.push({
                label: 'SMA 20',
                data: sma20,
                borderColor: 'rgba(255, 193, 7, 0.8)',
                borderWidth: 1.5,
                fill: false,
                tension: 0,
                pointRadius: 0
            });
        }

        // SMA 50
        if (this.indicators.sma50) {
            const sma50 = this.calculateSMA(prices, 50);
            datasets.push({
                label: 'SMA 50',
                data: sma50,
                borderColor: 'rgba(72, 187, 120, 0.8)',
                borderWidth: 1.5,
                fill: false,
                tension: 0,
                pointRadius: 0
            });
        }

        // SMA 200
        if (this.indicators.sma200) {
            const sma200 = this.calculateSMA(prices, 200);
            datasets.push({
                label: 'SMA 200',
                data: sma200,
                borderColor: 'rgba(245, 101, 101, 0.8)',
                borderWidth: 2,
                fill: false,
                tension: 0,
                pointRadius: 0
            });
        }

        // EMA 12
        if (this.indicators.ema12) {
            const ema12 = this.calculateEMA(prices, 12);
            datasets.push({
                label: 'EMA 12',
                data: ema12,
                borderColor: 'rgba(156, 39, 176, 0.8)',
                borderWidth: 1.5,
                fill: false,
                tension: 0,
                pointRadius: 0
            });
        }

        // EMA 26
        if (this.indicators.ema26) {
            const ema26 = this.calculateEMA(prices, 26);
            datasets.push({
                label: 'EMA 26',
                data: ema26,
                borderColor: 'rgba(33, 150, 243, 0.8)',
                borderWidth: 1.5,
                fill: false,
                tension: 0,
                pointRadius: 0
            });
        }

        // Bollinger Bands
        if (this.indicators.bb) {
            const bb = this.calculateBollingerBands(prices, 20, 2);
            datasets.push({
                label: 'BB Upper',
                data: bb.upper,
                borderColor: 'rgba(255, 152, 0, 0.5)',
                borderWidth: 1,
                borderDash: [5, 5],
                fill: false,
                pointRadius: 0
            });
            datasets.push({
                label: 'BB Lower',
                data: bb.lower,
                borderColor: 'rgba(255, 152, 0, 0.5)',
                borderWidth: 1,
                borderDash: [5, 5],
                fill: false,
                pointRadius: 0
            });
        }
    }

    /**
     * Toggle indicator on/off
     */
    toggleIndicator(indicator) {
        if (this.indicators.hasOwnProperty(indicator)) {
            this.indicators[indicator] = !this.indicators[indicator];
            this.render();
            return this.indicators[indicator];
        }
        return false;
    }

    /**
     * Enable drawing mode for trendlines
     */
    enableDrawing() {
        this.drawingMode = true;
        this.canvas.style.cursor = 'crosshair';
    }

    /**
     * Disable drawing mode
     */
    disableDrawing() {
        this.drawingMode = false;
        this.canvas.style.cursor = 'default';
        this.currentTrendline = null;
    }

    /**
     * Mouse down event for drawing
     */
    onMouseDown(e) {
        if (!this.drawingMode || !this.chart) return;

        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Convert pixel coordinates to data coordinates
        const xValue = this.chart.scales.x.getValueForPixel(x);
        const yValue = this.chart.scales.y.getValueForPixel(y);

        this.currentTrendline = {
            startX: xValue,
            startY: yValue,
            endX: xValue,
            endY: yValue,
            color: 'rgba(255, 193, 7, 0.8)',
            width: 2
        };
    }

    /**
     * Mouse move event for drawing
     */
    onMouseMove(e) {
        if (!this.drawingMode || !this.currentTrendline || !this.chart) return;

        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const xValue = this.chart.scales.x.getValueForPixel(x);
        const yValue = this.chart.scales.y.getValueForPixel(y);

        this.currentTrendline.endX = xValue;
        this.currentTrendline.endY = yValue;

        // Redraw chart with current trendline
        this.drawTrendlines();
    }

    /**
     * Mouse up event for drawing
     */
    onMouseUp(e) {
        if (!this.drawingMode || !this.currentTrendline) return;

        // Save trendline
        this.trendlines.push({ ...this.currentTrendline });
        this.currentTrendline = null;
        this.disableDrawing();
        this.render();
    }

    /**
     * Draw trendlines on canvas
     */
    drawTrendlines() {
        if (!this.chart) return;

        const ctx = this.chart.ctx;
        const chartArea = this.chart.chartArea;

        // Draw saved trendlines
        this.trendlines.forEach(line => {
            this.drawLine(ctx, line);
        });

        // Draw current trendline being drawn
        if (this.currentTrendline) {
            this.drawLine(ctx, this.currentTrendline);
        }
    }

    /**
     * Draw a single line
     */
    drawLine(ctx, line) {
        if (!this.chart) return;

        const xScale = this.chart.scales.x;
        const yScale = this.chart.scales.y;

        const startX = xScale.getPixelForValue(line.startX);
        const startY = yScale.getPixelForValue(line.startY);
        const endX = xScale.getPixelForValue(line.endX);
        const endY = yScale.getPixelForValue(line.endY);

        ctx.save();
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.strokeStyle = line.color;
        ctx.lineWidth = line.width;
        ctx.stroke();
        ctx.restore();
    }

    /**
     * Clear all trendlines
     */
    clearTrendlines() {
        this.trendlines = [];
        this.render();
    }

    /**
     * Calculate SMA
     */
    calculateSMA(data, period) {
        const result = [];
        for (let i = 0; i < data.length; i++) {
            if (i < period - 1) {
                result.push(null);
            } else {
                const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
                result.push(sum / period);
            }
        }
        return result;
    }

    /**
     * Calculate EMA
     */
    calculateEMA(data, period) {
        const k = 2 / (period + 1);
        const result = [];
        let ema = data[0];
        result.push(ema);

        for (let i = 1; i < data.length; i++) {
            ema = data[i] * k + ema * (1 - k);
            result.push(ema);
        }
        return result;
    }

    /**
     * Calculate Bollinger Bands
     */
    calculateBollingerBands(data, period, stdDev) {
        const sma = this.calculateSMA(data, period);
        const upper = [];
        const lower = [];

        for (let i = 0; i < data.length; i++) {
            if (i < period - 1) {
                upper.push(null);
                lower.push(null);
            } else {
                const slice = data.slice(i - period + 1, i + 1);
                const mean = sma[i];
                const variance = slice.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / period;
                const sd = Math.sqrt(variance);
                upper.push(mean + sd * stdDev);
                lower.push(mean - sd * stdDev);
            }
        }

        return { upper, middle: sma, lower };
    }

    /**
     * Show error message
     */
    showError(message) {
        const container = this.canvas.parentElement;
        container.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: ${this.options.height}px; color: rgba(255, 255, 255, 0.6);">
                <div style="text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 10px;">⚠️</div>
                    <div>${message}</div>
                </div>
            </div>
        `;
    }

    /**
     * Destroy chart
     */
    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.AdvancedChart = AdvancedChart;
}
