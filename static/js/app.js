// Main Application Logic
class StockAnalyzerApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.currentUser = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkAuthentication();
        this.loadDashboard();
        this.setupNavigation();
        this.setupForms();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                this.navigateToPage(page);
            });
        });

        // Mobile menu toggle
        const navToggle = document.getElementById('navToggle');
        const navMenu = document.getElementById('navMenu');
        navToggle?.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });

        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tabGroup = e.target.closest('.alert-tabs, .tab-buttons');
                const tabContent = e.target.dataset.tab || e.target.dataset.analysisTab;

                // Update active states
                tabGroup.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');

                // Handle content switching based on context
                if (e.target.dataset.analysisTab) {
                    this.switchAnalysisTab(e.target.dataset.analysisTab);
                }
            });
        });
    }

    setupNavigation() {
        // Handle browser back/forward
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.page) {
                this.navigateToPage(e.state.page, false);
            }
        });
    }

    setupForms() {
        // Login form
        const loginForm = document.getElementById('loginForm');
        loginForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleLogin();
        });

        // Register form
        const registerForm = document.getElementById('registerForm');
        registerForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleRegister();
        });

        // Screener form
        const screenerForm = document.getElementById('screenerForm');
        screenerForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.runScreener();
        });
    }

    async checkAuthentication() {
        if (api.token) {
            try {
                const response = await api.getProfile();
                this.currentUser = response.user;
                this.updateUserDisplay();
            } catch (error) {
                console.error('Auth check failed:', error);
                api.clearTokens();
            }
        }
    }

    updateUserDisplay() {
        const userDisplay = document.getElementById('userDisplay');
        const loginBtn = document.getElementById('loginBtn');
        const username = document.getElementById('username');

        if (this.currentUser) {
            userDisplay.style.display = 'flex';
            loginBtn.style.display = 'none';
            username.textContent = this.currentUser.username;
        } else {
            userDisplay.style.display = 'none';
            loginBtn.style.display = 'block';
        }
    }

    navigateToPage(page, updateHistory = true) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));

        // Show selected page
        const pageElement = document.getElementById(`${page}-page`);
        if (pageElement) {
            pageElement.classList.add('active');
            this.currentPage = page;

            // Update nav active state
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.toggle('active', link.dataset.page === page);
            });

            // Update browser history
            if (updateHistory) {
                history.pushState({ page }, '', `#${page}`);
            }

            // Load page-specific data
            this.loadPageData(page);
        }
    }

    async loadPageData(page) {
        switch(page) {
            case 'dashboard':
                await this.loadDashboard();
                break;
            case 'portfolio':
                await this.loadPortfolio();
                break;
            case 'watchlist':
                await this.loadWatchlist();
                break;
            case 'screener':
                await this.loadScreener();
                break;
            case 'alerts':
                await this.loadAlerts();
                break;
        }
    }

    // Dashboard functionality
    async loadDashboard() {
        if (this.currentUser) {
            await Promise.all([
                this.refreshPortfolio(),
                this.refreshWatchlist(),
                this.refreshRecommendations(),
                this.refreshAlerts()
            ]);
        } else {
            await this.refreshRecommendations();
        }
    }

    async refreshPortfolio() {
        const summaryEl = document.getElementById('portfolioSummary');
        summaryEl.classList.add('loading');

        try {
            const portfolio = await api.getPortfolio();
            this.displayPortfolioSummary(portfolio.summary);
            summaryEl.classList.remove('loading');
        } catch (error) {
            this.showNotification('Failed to load portfolio', 'error');
            summaryEl.classList.remove('loading');
        }
    }

    displayPortfolioSummary(summary) {
        document.getElementById('totalValue').textContent = `$${summary.total_value?.toLocaleString() || '0'}`;

        const dayPerf = document.getElementById('dayPerformance');
        dayPerf.textContent = `${summary.total_gain_loss_percent > 0 ? '+' : ''}${summary.total_gain_loss_percent?.toFixed(2) || '0'}%`;
        dayPerf.className = `metric-value ${summary.total_gain_loss_percent > 0 ? 'positive' : 'negative'}`;

        const totalReturn = document.getElementById('totalReturn');
        totalReturn.textContent = `$${summary.total_gain_loss?.toLocaleString() || '0'}`;
        totalReturn.className = `metric-value ${summary.total_gain_loss > 0 ? 'positive' : 'negative'}`;
    }

    async refreshWatchlist() {
        const container = document.getElementById('watchlistItems');
        container.classList.add('loading');

        try {
            const response = await api.getWatchlist();
            this.displayWatchlistItems(response.items.slice(0, 5));
            container.classList.remove('loading');
        } catch (error) {
            container.classList.remove('loading');
        }
    }

    displayWatchlistItems(items) {
        const container = document.getElementById('watchlistItems');

        if (items.length === 0) {
            container.innerHTML = '<p class="text-secondary">Keine Aktien in der Watchlist</p>';
            return;
        }

        container.innerHTML = items.map(item => `
            <div class="watchlist-item">
                <div class="watchlist-item-info">
                    <div class="watchlist-item-ticker">${item.ticker}</div>
                    <div class="watchlist-item-name">${item.company_name || ''}</div>
                </div>
                <div class="watchlist-item-price">
                    <div class="watchlist-item-current">$${item.current_price?.toFixed(2) || '-'}</div>
                    <div class="watchlist-item-change ${item.price_change_percent > 0 ? 'positive' : 'negative'}">
                        ${item.price_change_percent > 0 ? '+' : ''}${item.price_change_percent?.toFixed(2) || '0'}%
                    </div>
                </div>
            </div>
        `).join('');
    }

    async refreshRecommendations() {
        const container = document.getElementById('recommendationsList');
        container.classList.add('loading');

        try {
            const response = await api.getRecommendations();
            this.displayRecommendations(response.recommendations);
            container.classList.remove('loading');
        } catch (error) {
            container.classList.remove('loading');
        }
    }

    displayRecommendations(recommendations) {
        const container = document.getElementById('recommendationsList');

        const categories = [
            { key: 'value_picks', title: 'Value Picks' },
            { key: 'growth_picks', title: 'Growth Stocks' },
            { key: 'dividend_picks', title: 'Dividenden' }
        ];

        container.innerHTML = categories.map(cat => {
            const stocks = recommendations[cat.key] || [];
            if (stocks.length === 0) return '';

            return `
                <div class="recommendation-group">
                    <div class="recommendation-title">${cat.title}</div>
                    ${stocks.map(stock => `
                        <div class="recommendation-card">
                            <div class="recommendation-info">
                                <span class="recommendation-ticker">${stock.ticker}</span>
                                <div class="recommendation-metrics">
                                    ${stock.pe_ratio ? `<span class="recommendation-metric">P/E: ${stock.pe_ratio.toFixed(1)}</span>` : ''}
                                    ${stock.dividend_yield ? `<span class="recommendation-metric">Div: ${(stock.dividend_yield * 100).toFixed(2)}%</span>` : ''}
                                </div>
                            </div>
                            <span class="recommendation-score">${stock.score?.toFixed(0) || '-'}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }).join('');
    }

    async refreshAlerts() {
        const container = document.getElementById('activeAlerts');
        container.classList.add('loading');

        try {
            const response = await api.getAlerts(true);
            const activeAlerts = response.alerts.filter(a => a.is_active && !a.is_triggered);

            document.getElementById('alertCount').textContent = activeAlerts.length;
            this.displayActiveAlerts(activeAlerts.slice(0, 5));
            container.classList.remove('loading');
        } catch (error) {
            container.classList.remove('loading');
        }
    }

    displayActiveAlerts(alerts) {
        const container = document.getElementById('activeAlerts');

        if (alerts.length === 0) {
            container.innerHTML = '<p class="text-secondary">Keine aktiven Alerts</p>';
            return;
        }

        container.innerHTML = alerts.map(alert => `
            <div class="alert-item ${alert.is_triggered ? 'triggered' : ''}">
                <div class="alert-info">
                    <div class="alert-ticker">${alert.ticker}</div>
                    <div class="alert-condition">
                        ${alert.alert_type.replace('_', ' ')} $${alert.target_value.toFixed(2)}
                    </div>
                </div>
                <div class="alert-actions">
                    <button class="btn-icon" onclick="app.editAlert(${alert.id})">✏️</button>
                    <button class="btn-icon" onclick="app.deleteAlert(${alert.id})">🗑️</button>
                </div>
            </div>
        `).join('');
    }

    // Stock Analysis
    async analyzeStock() {
        const ticker = document.getElementById('stockSearch').value.trim();
        if (!ticker) {
            this.showNotification('Bitte geben Sie ein Symbol ein', 'error');
            return;
        }

        const resultDiv = document.getElementById('analysisResult');
        resultDiv.style.display = 'block';

        try {
            const [stockInfo, aiAnalysis] = await Promise.all([
                api.getStock(ticker),
                this.currentUser ? api.analyzeWithAI(ticker) : Promise.resolve(null)
            ]);

            this.displayStockAnalysis(stockInfo, aiAnalysis);
        } catch (error) {
            this.showNotification('Analyse fehlgeschlagen', 'error');
            resultDiv.style.display = 'none';
        }
    }

    displayStockAnalysis(data, aiAnalysis) {
        // Display header
        document.getElementById('stockName').textContent = `${data.info.ticker} - ${data.info.company_name}`;

        const priceDisplay = document.getElementById('stockPrice');
        const changePercent = ((data.info.current_price - data.info.previous_close) / data.info.previous_close * 100);

        priceDisplay.innerHTML = `
            <span class="price-current">$${data.info.current_price?.toFixed(2) || '-'}</span>
            <span class="price-change ${changePercent > 0 ? 'positive' : 'negative'}">
                ${changePercent > 0 ? '+' : ''}${changePercent.toFixed(2)}%
            </span>
        `;

        // Display overview tab
        document.getElementById('overview-tab').innerHTML = this.createOverviewContent(data.info);

        // Display technical tab
        if (data.technical_indicators) {
            document.getElementById('technical-tab').innerHTML = this.createTechnicalContent(data.technical_indicators);
        }

        // Display fundamental tab
        if (data.fundamental_analysis) {
            document.getElementById('fundamental-tab').innerHTML = this.createFundamentalContent(data.fundamental_analysis);
        }

        // Display AI tab
        if (aiAnalysis && aiAnalysis.ai_analysis) {
            document.getElementById('ai-tab').innerHTML = this.createAIContent(aiAnalysis.ai_analysis);
        }
    }

    createOverviewContent(info) {
        return `
            <div class="metrics-grid">
                <div class="metric-item">
                    <span class="metric-label">Market Cap</span>
                    <span class="metric-value">$${(info.market_cap / 1e9).toFixed(2)}B</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">P/E Ratio</span>
                    <span class="metric-value">${info.pe_ratio?.toFixed(2) || 'N/A'}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Dividend Yield</span>
                    <span class="metric-value">${info.dividend_yield ? (info.dividend_yield * 100).toFixed(2) + '%' : 'N/A'}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">52 Week Range</span>
                    <span class="metric-value">$${info['52_week_low']?.toFixed(2)} - $${info['52_week_high']?.toFixed(2)}</span>
                </div>
            </div>
            <div class="description">
                <h4>Über das Unternehmen</h4>
                <p>${info.description || 'Keine Beschreibung verfügbar'}</p>
            </div>
        `;
    }

    createTechnicalContent(technical) {
        return `
            <div class="technical-indicators">
                <div class="indicator">
                    <span class="indicator-label">RSI (14)</span>
                    <span class="indicator-value">${technical.rsi?.toFixed(2) || 'N/A'}</span>
                </div>
                <div class="indicator">
                    <span class="indicator-label">MACD</span>
                    <span class="indicator-value">${technical.macd?.macd?.toFixed(2) || 'N/A'}</span>
                </div>
                <div class="indicator">
                    <span class="indicator-label">Volatilität</span>
                    <span class="indicator-value">${(technical.volatility * 100)?.toFixed(2)}%</span>
                </div>
            </div>
        `;
    }

    createFundamentalContent(fundamental) {
        return `
            <div class="fundamental-scores">
                <div class="score-item">
                    <span class="score-label">Gesamt-Score</span>
                    <span class="score-value">${fundamental.overall_score}/100</span>
                </div>
                <div class="score-item">
                    <span class="score-label">Empfehlung</span>
                    <span class="score-value">${fundamental.recommendation}</span>
                </div>
            </div>
        `;
    }

    createAIContent(aiAnalysis) {
        return `
            <div class="ai-analysis">
                ${aiAnalysis.summary ? `<div class="ai-section"><h4>Zusammenfassung</h4><p>${aiAnalysis.summary}</p></div>` : ''}
                ${aiAnalysis.technical_analysis ? `<div class="ai-section"><h4>Technische Analyse</h4><p>${aiAnalysis.technical_analysis}</p></div>` : ''}
                ${aiAnalysis.risks ? `<div class="ai-section"><h4>Risiken</h4><p>${aiAnalysis.risks}</p></div>` : ''}
                ${aiAnalysis.opportunities ? `<div class="ai-section"><h4>Chancen</h4><p>${aiAnalysis.opportunities}</p></div>` : ''}
            </div>
        `;
    }

    switchAnalysisTab(tab) {
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        document.getElementById(`${tab}-tab`).classList.add('active');
    }

    // Screener functionality
    async loadScreener() {
        await this.loadPresetStrategies();
    }

    async loadPresetStrategies() {
        try {
            const response = await api.getScreenerPresets();
            const container = document.getElementById('presetStrategies');

            container.innerHTML = response.presets.map(preset => `
                <button class="preset-btn" onclick="app.applyPreset('${preset.name.toLowerCase().replace(' ', '_')}')">
                    ${preset.name}
                </button>
            `).join('');
        } catch (error) {
            console.error('Failed to load presets:', error);
        }
    }

    async applyPreset(presetName) {
        try {
            const response = await api.applyPresetScreen(presetName);
            this.displayScreenerResults(response.results);
            document.getElementById('resultCount').textContent = `(${response.count})`;
        } catch (error) {
            this.showNotification('Preset konnte nicht angewendet werden', 'error');
        }
    }

    async runScreener() {
        const criteria = {
            market: document.getElementById('marketFilter').value,
            min_market_cap: parseFloat(document.getElementById('minMarketCap').value) || undefined,
            min_pe_ratio: parseFloat(document.getElementById('minPE').value) || undefined,
            max_pe_ratio: parseFloat(document.getElementById('maxPE').value) || undefined,
            min_dividend_yield: parseFloat(document.getElementById('minDividend').value) / 100 || undefined,
            prefer_value: document.getElementById('preferValue').checked,
            prefer_growth: document.getElementById('preferGrowth').checked,
            prefer_dividends: document.getElementById('preferDividends').checked,
            prefer_momentum: document.getElementById('preferMomentum').checked
        };

        try {
            const response = await api.screenStocks(criteria);
            this.displayScreenerResults(response.results);
            document.getElementById('resultCount').textContent = `(${response.count})`;
        } catch (error) {
            this.showNotification('Screening fehlgeschlagen', 'error');
        }
    }

    displayScreenerResults(results) {
        const tbody = document.getElementById('screenerTableBody');

        if (results.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8">Keine Ergebnisse gefunden</td></tr>';
            return;
        }

        tbody.innerHTML = results.map(stock => `
            <tr>
                <td><strong>${stock.ticker}</strong></td>
                <td>${stock.company_name}</td>
                <td>$${stock.current_price?.toFixed(2) || '-'}</td>
                <td>$${(stock.market_cap / 1e9).toFixed(2)}B</td>
                <td>${stock.pe_ratio?.toFixed(2) || '-'}</td>
                <td>${stock.dividend_yield ? (stock.dividend_yield * 100).toFixed(2) + '%' : '-'}</td>
                <td>${stock.score?.toFixed(0) || '-'}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="app.addToWatchlistFromScreener('${stock.ticker}')">
                        + Watchlist
                    </button>
                </td>
            </tr>
        `).join('');
    }

    resetScreener() {
        document.getElementById('screenerForm').reset();
        document.getElementById('screenerTableBody').innerHTML = '';
        document.getElementById('resultCount').textContent = '';
    }

    // Portfolio functionality
    async loadPortfolio() {
        if (!this.currentUser) {
            this.showNotification('Bitte melden Sie sich an', 'error');
            return;
        }

        try {
            const portfolio = await api.getPortfolio();
            this.displayPortfolioDetails(portfolio);
        } catch (error) {
            this.showNotification('Portfolio konnte nicht geladen werden', 'error');
        }
    }

    displayPortfolioDetails(portfolio) {
        // Display summary
        const summary = portfolio.summary;
        document.getElementById('portfolioDetailSummary').innerHTML = `
            <div class="portfolio-metrics">
                <div class="portfolio-metric">
                    <div class="portfolio-metric-label">Gesamtwert</div>
                    <div class="portfolio-metric-value">$${summary.total_value?.toLocaleString() || '0'}</div>
                </div>
                <div class="portfolio-metric">
                    <div class="portfolio-metric-label">Investiert</div>
                    <div class="portfolio-metric-value">$${summary.total_invested?.toLocaleString() || '0'}</div>
                </div>
                <div class="portfolio-metric">
                    <div class="portfolio-metric-label">Gewinn/Verlust</div>
                    <div class="portfolio-metric-value ${summary.total_gain_loss > 0 ? 'positive' : 'negative'}">
                        $${summary.total_gain_loss?.toLocaleString() || '0'}
                        (${summary.total_gain_loss_percent?.toFixed(2) || '0'}%)
                    </div>
                </div>
            </div>
        `;

        // Display holdings
        const tbody = document.getElementById('portfolioTableBody');
        if (portfolio.items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7">Keine Positionen im Portfolio</td></tr>';
            return;
        }

        tbody.innerHTML = portfolio.items.map(item => `
            <tr>
                <td><strong>${item.ticker}</strong></td>
                <td>${item.company_name}</td>
                <td>${item.shares}</td>
                <td>$${item.current_price?.toFixed(2) || '-'}</td>
                <td>$${item.current_value?.toFixed(2) || '-'}</td>
                <td class="${item.gain_loss_percent > 0 ? 'positive' : 'negative'}">
                    ${item.gain_loss_percent > 0 ? '+' : ''}${item.gain_loss_percent?.toFixed(2) || '0'}%
                </td>
                <td>
                    <button class="btn-icon" onclick="app.sellPosition('${item.ticker}')">Verkaufen</button>
                </td>
            </tr>
        `).join('');
    }

    // Watchlist functionality
    async loadWatchlist() {
        if (!this.currentUser) {
            this.showNotification('Bitte melden Sie sich an', 'error');
            return;
        }

        try {
            const response = await api.getWatchlist();
            this.displayFullWatchlist(response.items);
        } catch (error) {
            this.showNotification('Watchlist konnte nicht geladen werden', 'error');
        }
    }

    displayFullWatchlist(items) {
        const container = document.getElementById('watchlistGrid');

        if (items.length === 0) {
            container.innerHTML = '<p>Keine Aktien in der Watchlist</p>';
            return;
        }

        container.innerHTML = items.map(item => `
            <div class="watchlist-card card">
                <h3>${item.ticker}</h3>
                <p>${item.company_name}</p>
                <div class="price-info">
                    <span class="current-price">$${item.current_price?.toFixed(2) || '-'}</span>
                    <span class="price-change ${item.price_change_percent > 0 ? 'positive' : 'negative'}">
                        ${item.price_change_percent > 0 ? '+' : ''}${item.price_change_percent?.toFixed(2) || '0'}%
                    </span>
                </div>
                <div class="watchlist-actions">
                    <button class="btn btn-sm btn-outline" onclick="app.createAlertForStock('${item.ticker}')">
                        Alert erstellen
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="app.removeFromWatchlist('${item.ticker}')">
                        Entfernen
                    </button>
                </div>
            </div>
        `).join('');
    }

    // Alerts functionality
    async loadAlerts() {
        if (!this.currentUser) {
            this.showNotification('Bitte melden Sie sich an', 'error');
            return;
        }

        try {
            const [alerts, stats] = await Promise.all([
                api.getAlerts(),
                api.getAlertStatistics()
            ]);

            this.displayAlertStats(stats);
            this.displayAllAlerts(alerts.alerts);
        } catch (error) {
            this.showNotification('Alerts konnten nicht geladen werden', 'error');
        }
    }

    displayAlertStats(stats) {
        document.getElementById('alertStats').innerHTML = `
            <div class="stat-item">
                <div class="stat-value">${stats.total_alerts || 0}</div>
                <div class="stat-label">Gesamt</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.active_alerts || 0}</div>
                <div class="stat-label">Aktiv</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.triggered_alerts || 0}</div>
                <div class="stat-label">Ausgelöst</div>
            </div>
        `;
    }

    displayAllAlerts(alerts) {
        const container = document.getElementById('alertsList');

        if (alerts.length === 0) {
            container.innerHTML = '<p>Keine Alerts vorhanden</p>';
            return;
        }

        container.innerHTML = alerts.map(alert => `
            <div class="alert-card card ${alert.is_triggered ? 'triggered' : ''}">
                <h4>${alert.ticker}</h4>
                <p>${alert.alert_type.replace('_', ' ')}</p>
                <p>Target: $${alert.target_value?.toFixed(2)}</p>
                <p>Current: $${alert.current_value?.toFixed(2) || '-'}</p>
                ${alert.is_triggered ? '<span class="badge">Ausgelöst</span>' : ''}
                <div class="alert-actions">
                    <button class="btn-icon" onclick="app.deleteAlert(${alert.id})">🗑️</button>
                </div>
            </div>
        `).join('');
    }

    // User actions
    async handleLogin() {
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        try {
            const response = await api.login(email, password);
            this.currentUser = response.user;
            this.updateUserDisplay();
            this.closeModal('loginModal');
            this.showNotification('Erfolgreich angemeldet', 'success');
            this.loadDashboard();
        } catch (error) {
            this.showNotification(error.message || 'Anmeldung fehlgeschlagen', 'error');
        }
    }

    async handleRegister() {
        const email = document.getElementById('registerEmail').value;
        const username = document.getElementById('registerUsername').value;
        const password = document.getElementById('registerPassword').value;

        try {
            const response = await api.register(email, username, password);
            this.currentUser = response.user;
            this.updateUserDisplay();
            this.closeModal('registerModal');
            this.showNotification('Erfolgreich registriert', 'success');
            this.loadDashboard();
        } catch (error) {
            this.showNotification(error.message || 'Registrierung fehlgeschlagen', 'error');
        }
    }

    async logout() {
        try {
            await api.logout();
            this.currentUser = null;
            this.updateUserDisplay();
            this.showNotification('Erfolgreich abgemeldet', 'success');
            this.navigateToPage('dashboard');
        } catch (error) {
            console.error('Logout failed:', error);
        }
    }

    // Modal functions
    showLogin() {
        this.showModal('loginModal');
    }

    showRegister() {
        this.closeModal('loginModal');
        this.showModal('registerModal');
    }

    showModal(modalId) {
        document.getElementById('modalOverlay').style.display = 'block';
        document.getElementById(modalId).style.display = 'block';
    }

    closeModal(modalId) {
        document.getElementById('modalOverlay').style.display = 'none';
        document.getElementById(modalId).style.display = 'none';
    }

    // Notifications
    showNotification(message, type = 'info') {
        const container = document.getElementById('notificationContainer');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        container.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // Additional helper methods
    async addToWatchlistFromScreener(ticker) {
        if (!this.currentUser) {
            this.showNotification('Bitte melden Sie sich an', 'error');
            return;
        }

        try {
            await api.addToWatchlist(ticker);
            this.showNotification(`${ticker} zur Watchlist hinzugefügt`, 'success');
        } catch (error) {
            this.showNotification('Fehler beim Hinzufügen zur Watchlist', 'error');
        }
    }

    async removeFromWatchlist(ticker) {
        try {
            await api.removeFromWatchlist(ticker);
            this.showNotification(`${ticker} aus Watchlist entfernt`, 'success');
            this.loadWatchlist();
        } catch (error) {
            this.showNotification('Fehler beim Entfernen aus Watchlist', 'error');
        }
    }

    async deleteAlert(alertId) {
        try {
            await api.deleteAlert(alertId);
            this.showNotification('Alert gelöscht', 'success');
            this.loadAlerts();
        } catch (error) {
            this.showNotification('Fehler beim Löschen des Alerts', 'error');
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new StockAnalyzerApp();
});