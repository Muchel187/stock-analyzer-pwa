// Reusable UI components and utilities

class UIComponents {
    static createStockCard(stock) {
        const changeClass = stock.change_percent > 0 ? 'positive' : 'negative';
        const changeSymbol = stock.change_percent > 0 ? '+' : '';

        return `
            <div class="stock-card card">
                <div class="stock-header">
                    <h3>${stock.ticker}</h3>
                    <span class="badge">${stock.sector || 'N/A'}</span>
                </div>
                <div class="stock-body">
                    <p class="company-name">${stock.company_name}</p>
                    <div class="price-section">
                        <span class="current-price">$${stock.current_price?.toFixed(2) || '-'}</span>
                        <span class="price-change ${changeClass}">
                            ${changeSymbol}${stock.change_percent?.toFixed(2)}%
                        </span>
                    </div>
                    <div class="stock-metrics">
                        <div class="metric">
                            <span class="label">P/E</span>
                            <span class="value">${stock.pe_ratio?.toFixed(2) || '-'}</span>
                        </div>
                        <div class="metric">
                            <span class="label">Div</span>
                            <span class="value">${stock.dividend_yield ? (stock.dividend_yield * 100).toFixed(2) + '%' : '-'}</span>
                        </div>
                    </div>
                </div>
                <div class="stock-actions">
                    <button class="btn btn-sm btn-outline" onclick="app.analyzeStock('${stock.ticker}')">
                        Analyse
                    </button>
                    <button class="btn btn-sm btn-primary" onclick="app.addToWatchlist('${stock.ticker}')">
                        + Watchlist
                    </button>
                </div>
            </div>
        `;
    }

    static createTransactionModal() {
        return `
            <div id="transactionModal" class="modal" style="display:none;">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>Transaktion hinzufügen</h2>
                        <button class="close-btn" onclick="app.closeModal('transactionModal')">×</button>
                    </div>
                    <div class="modal-body">
                        <form id="transactionForm">
                            <div class="form-group">
                                <label>Symbol</label>
                                <input type="text" id="transactionTicker" required placeholder="z.B. AAPL">
                            </div>
                            <div class="form-group">
                                <label>Typ</label>
                                <select id="transactionType" required>
                                    <option value="BUY">Kauf</option>
                                    <option value="SELL">Verkauf</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Anzahl Aktien</label>
                                <input type="number" id="transactionShares" required step="0.001" min="0">
                            </div>
                            <div class="form-group">
                                <label>Preis pro Aktie ($)</label>
                                <input type="number" id="transactionPrice" required step="0.01" min="0">
                            </div>
                            <div class="form-group">
                                <label>Datum</label>
                                <input type="datetime-local" id="transactionDate">
                            </div>
                            <div class="form-group">
                                <label>Gebühren ($)</label>
                                <input type="number" id="transactionFees" step="0.01" min="0" placeholder="0.00">
                            </div>
                            <div class="form-group">
                                <label>Notizen</label>
                                <textarea id="transactionNotes" rows="3"></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary btn-block">Transaktion speichern</button>
                        </form>
                    </div>
                </div>
            </div>
        `;
    }

    static createAlertModal() {
        return `
            <div id="alertModal" class="modal" style="display:none;">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>Preis-Alert erstellen</h2>
                        <button class="close-btn" onclick="app.closeModal('alertModal')">×</button>
                    </div>
                    <div class="modal-body">
                        <form id="alertForm">
                            <div class="form-group">
                                <label>Symbol</label>
                                <input type="text" id="alertTicker" required placeholder="z.B. AAPL">
                            </div>
                            <div class="form-group">
                                <label>Alert-Typ</label>
                                <select id="alertType" required>
                                    <option value="PRICE_ABOVE">Preis über</option>
                                    <option value="PRICE_BELOW">Preis unter</option>
                                    <option value="PERCENT_CHANGE">Prozentuale Änderung</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Zielwert ($)</label>
                                <input type="number" id="alertTarget" required step="0.01" min="0">
                            </div>
                            <div class="form-group">
                                <label>Benachrichtigung per</label>
                                <div class="checkbox-group">
                                    <label>
                                        <input type="checkbox" id="alertEmail" checked> E-Mail
                                    </label>
                                    <label>
                                        <input type="checkbox" id="alertPush"> Push-Benachrichtigung
                                    </label>
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Notizen</label>
                                <textarea id="alertNotes" rows="3"></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary btn-block">Alert erstellen</button>
                        </form>
                    </div>
                </div>
            </div>
        `;
    }

    static formatCurrency(value, currency = 'USD') {
        if (value === null || value === undefined) return '-';
        return new Intl.NumberFormat('de-DE', {
            style: 'currency',
            currency: currency
        }).format(value);
    }

    static formatPercent(value, decimals = 2) {
        if (value === null || value === undefined) return '-';
        const sign = value > 0 ? '+' : '';
        return `${sign}${value.toFixed(decimals)}%`;
    }

    static formatNumber(value, decimals = 0) {
        if (value === null || value === undefined) return '-';
        return new Intl.NumberFormat('de-DE', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value);
    }

    static formatMarketCap(value) {
        if (!value) return '-';

        if (value >= 1e12) {
            return `$${(value / 1e12).toFixed(2)}T`;
        } else if (value >= 1e9) {
            return `$${(value / 1e9).toFixed(2)}B`;
        } else if (value >= 1e6) {
            return `$${(value / 1e6).toFixed(2)}M`;
        }
        return `$${value.toFixed(0)}`;
    }

    static createLoadingSpinner() {
        return '<div class="loading-spinner"></div>';
    }

    static createEmptyState(message, icon = '📊') {
        return `
            <div class="empty-state">
                <div class="empty-icon">${icon}</div>
                <p class="empty-message">${message}</p>
            </div>
        `;
    }

    static createErrorState(message) {
        return `
            <div class="error-state">
                <div class="error-icon">⚠️</div>
                <p class="error-message">${message}</p>
                <button class="btn btn-sm btn-outline" onclick="location.reload()">
                    Neu laden
                </button>
            </div>
        `;
    }
}

// Date utilities
class DateUtils {
    static formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('de-DE');
    }

    static formatDateTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('de-DE');
    }

    static getRelativeTime(dateString) {
        if (!dateString) return '-';

        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;

        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'gerade eben';
        if (minutes < 60) return `vor ${minutes} Minute${minutes > 1 ? 'n' : ''}`;
        if (hours < 24) return `vor ${hours} Stunde${hours > 1 ? 'n' : ''}`;
        if (days < 30) return `vor ${days} Tag${days > 1 ? 'en' : ''}`;

        return this.formatDate(dateString);
    }
}

// Validation utilities
class ValidationUtils {
    static isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    static isValidTicker(ticker) {
        const re = /^[A-Z]{1,5}(\.DE)?$/;
        return re.test(ticker.toUpperCase());
    }

    static isPositiveNumber(value) {
        return !isNaN(value) && value > 0;
    }

    static validateTransactionForm(data) {
        const errors = [];

        if (!this.isValidTicker(data.ticker)) {
            errors.push('Ungültiges Symbol');
        }

        if (!this.isPositiveNumber(data.shares)) {
            errors.push('Anzahl muss größer als 0 sein');
        }

        if (!this.isPositiveNumber(data.price)) {
            errors.push('Preis muss größer als 0 sein');
        }

        return errors;
    }
}