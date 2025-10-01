/**
 * Export Manager - Handle PDF and CSV exports
 */
class ExportManager {
    constructor() {
        this.jsPdfLoaded = false;
        this.html2canvasLoaded = false;
    }

    /**
     * Export stock analysis as PDF
     */
    async exportAnalysisPDF(ticker, stockData) {
        try {
            // Load libraries if needed
            await this.loadLibraries();

            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            
            // Add header
            doc.setFontSize(20);
            doc.text(`Stock Analysis: ${ticker}`, 20, 20);
            
            // Add timestamp
            doc.setFontSize(10);
            doc.text(`Generated: ${new Date().toLocaleString()}`, 20, 30);
            
            // Add stock info
            doc.setFontSize(14);
            doc.text('Stock Information', 20, 45);
            doc.setFontSize(10);
            
            let y = 55;
            if (stockData.info) {
                const info = stockData.info;
                doc.text(`Company: ${info.company_name || ticker}`, 20, y);
                y += 7;
                doc.text(`Price: $${info.current_price?.toFixed(2) || 'N/A'}`, 20, y);
                y += 7;
                doc.text(`Market Cap: ${this.formatMarketCap(info.market_cap)}`, 20, y);
                y += 7;
                doc.text(`Sector: ${info.sector || 'N/A'}`, 20, y);
                y += 7;
            }
            
            // Add technical indicators
            if (stockData.technical) {
                y += 10;
                doc.setFontSize(14);
                doc.text('Technical Indicators', 20, y);
                y += 10;
                doc.setFontSize(10);
                
                const tech = stockData.technical;
                if (tech.rsi) doc.text(`RSI: ${tech.rsi.toFixed(2)}`, 20, y), y += 7;
                if (tech.sma_20) doc.text(`SMA 20: $${tech.sma_20.toFixed(2)}`, 20, y), y += 7;
                if (tech.sma_50) doc.text(`SMA 50: $${tech.sma_50.toFixed(2)}`, 20, y), y += 7;
            }
            
            // Add AI summary if available
            if (stockData.aiAnalysis) {
                y += 10;
                doc.setFontSize(14);
                doc.text('AI Analysis Summary', 20, y);
                y += 10;
                doc.setFontSize(10);
                
                const summary = stockData.aiAnalysis.recommendation || 'No summary available';
                const lines = doc.splitTextToSize(summary, 170);
                lines.forEach(line => {
                    if (y > 270) {
                        doc.addPage();
                        y = 20;
                    }
                    doc.text(line, 20, y);
                    y += 7;
                });
            }
            
            // Save PDF
            doc.save(`${ticker}_analysis_${new Date().toISOString().split('T')[0]}.pdf`);
            
            return true;
        } catch (error) {
            console.error('PDF export error:', error);
            throw new Error('Failed to export PDF');
        }
    }

    /**
     * Export portfolio as CSV
     */
    exportPortfolioCSV(portfolio) {
        try {
            const headers = ['Ticker', 'Company', 'Shares', 'Avg Cost', 'Current Price', 'Current Value', 'Gain/Loss', 'Gain/Loss %'];
            const rows = [];
            
            // Add header row
            rows.push(headers.join(','));
            
            // Add data rows
            if (portfolio.items) {
                portfolio.items.forEach(item => {
                    const row = [
                        item.ticker,
                        this.escapeCsv(item.company_name || ''),
                        item.shares || 0,
                        item.average_cost?.toFixed(2) || '0.00',
                        item.current_price?.toFixed(2) || '0.00',
                        item.current_value?.toFixed(2) || '0.00',
                        item.gain_loss?.toFixed(2) || '0.00',
                        item.gain_loss_percent?.toFixed(2) || '0.00'
                    ];
                    rows.push(row.join(','));
                });
            }
            
            // Add summary row
            rows.push('');
            rows.push(`Total Value,${portfolio.total_value?.toFixed(2) || '0.00'}`);
            rows.push(`Total Gain/Loss,${portfolio.total_gain_loss?.toFixed(2) || '0.00'}`);
            rows.push(`Total Return %,${portfolio.total_return?.toFixed(2) || '0.00'}`);
            
            const csv = rows.join('\n');
            const filename = `portfolio_${new Date().toISOString().split('T')[0]}.csv`;
            
            this.downloadFile(csv, filename, 'text/csv');
            
            return true;
        } catch (error) {
            console.error('CSV export error:', error);
            throw new Error('Failed to export CSV');
        }
    }

    /**
     * Export watchlist as CSV
     */
    exportWatchlistCSV(watchlist) {
        try {
            const headers = ['Ticker', 'Company', 'Current Price', 'Change %', 'Added Date'];
            const rows = [];
            
            rows.push(headers.join(','));
            
            if (watchlist) {
                watchlist.forEach(item => {
                    const row = [
                        item.ticker,
                        this.escapeCsv(item.company_name || ''),
                        item.current_price?.toFixed(2) || '0.00',
                        item.price_change_percent?.toFixed(2) || '0.00',
                        item.added_date || new Date().toISOString().split('T')[0]
                    ];
                    rows.push(row.join(','));
                });
            }
            
            const csv = rows.join('\n');
            const filename = `watchlist_${new Date().toISOString().split('T')[0]}.csv`;
            
            this.downloadFile(csv, filename, 'text/csv');
            
            return true;
        } catch (error) {
            console.error('CSV export error:', error);
            throw new Error('Failed to export CSV');
        }
    }

    /**
     * Helper: Escape CSV values
     */
    escapeCsv(value) {
        if (value === null || value === undefined) return '';
        const str = String(value);
        if (str.includes(',') || str.includes('"') || str.includes('\n')) {
            return `"${str.replace(/"/g, '""')}"`;
        }
        return str;
    }

    /**
     * Helper: Format market cap
     */
    formatMarketCap(value) {
        if (!value) return 'N/A';
        if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
        if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
        if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
        return `$${value.toFixed(2)}`;
    }

    /**
     * Helper: Download file
     */
    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    /**
     * Load required libraries
     */
    async loadLibraries() {
        // Load jsPDF if not already loaded
        if (!window.jspdf && !this.jsPdfLoaded) {
            return new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
                script.onload = () => {
                    this.jsPdfLoaded = true;
                    resolve();
                };
                script.onerror = reject;
                document.head.appendChild(script);
            });
        }
    }
}

// Create global instance
window.exportManager = new ExportManager();
