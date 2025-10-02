// Main Application Logic
class StockAnalyzerApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.currentUser = null;
        this.aiVisualizer = new AIAnalysisVisualizer();
        this.currentAnalysisTicker = null;
        this.currentStockPrice = null;
        this.currentPeriod = '1y';
        this.priceChartInstance = null;
        this.volumeChartInstance = null;
        this.compareChartInstance = null;
        this.priceHistoryData = null;
        this.showSMA50 = false;
        this.showSMA200 = false;
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

        // Stock search form (Analysis page)
        const stockSearchForm = document.getElementById('stockSearchForm');
        stockSearchForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.analyzeStock();
        });

        // Screener form
        const screenerForm = document.getElementById('screenerForm');
        screenerForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.runScreener();
        });

        // Alert form
        const alertForm = document.getElementById('alertForm');
        alertForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleCreateAlert(e);
        });

        // Transaction form
        const transactionForm = document.getElementById('transactionForm');
        transactionForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleAddTransaction(e);
        });

        // Watchlist form
        const watchlistForm = document.getElementById('watchlistForm');
        watchlistForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleAddToWatchlist(e);
        });

        // Password confirmation checker (real-time validation)
        const passwordConfirm = document.getElementById('registerPasswordConfirm');
        const password = document.getElementById('registerPassword');
        passwordConfirm?.addEventListener('input', () => {
            const matchIndicator = document.getElementById('passwordMatch');
            if (password.value === passwordConfirm.value && password.value.length >= 6) {
                matchIndicator.textContent = '✓ Passwörter stimmen überein';
                matchIndicator.style.color = '#27ae60';
            } else if (passwordConfirm.value.length > 0) {
                matchIndicator.textContent = '❌ Passwörter stimmen nicht überein';
                matchIndicator.style.color = '#e74c3c';
            } else {
                matchIndicator.textContent = '';
            }
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
        const navNotifications = document.getElementById('navNotifications');

        if (this.currentUser) {
            userDisplay.style.display = 'flex';
            loginBtn.style.display = 'none';
            username.textContent = this.currentUser.username;

            // Show notification bell when logged in
            if (navNotifications) {
                navNotifications.style.display = 'block';
            }

            // Initialize notification center
            if (typeof NotificationCenter !== 'undefined' && !window.notificationCenter) {
                window.notificationCenter = new NotificationCenter(this);
            }

            // Add admin link to menu if user is admin
            this.updateAdminLink();
        } else {
            userDisplay.style.display = 'none';
            loginBtn.style.display = 'block';

            // Hide notification bell when logged out
            if (navNotifications) {
                navNotifications.style.display = 'none';
            }

            // Remove admin link
            this.removeAdminLink();
        }
    }

    updateAdminLink() {
        // Check if user is admin and add link to navbar
        if (this.currentUser && this.currentUser.is_admin) {
            const navbarMenu = document.querySelector('.navbar-menu');
            if (navbarMenu) {
                // Check if admin link already exists
                let adminLink = document.querySelector('.navbar-menu .admin-nav-link');

                if (!adminLink) {
                    // Create admin link
                    const li = document.createElement('li');
                    li.innerHTML = '<a href="/admin" class="admin-nav-link">🛡️ Admin</a>';
                    navbarMenu.appendChild(li);
                }
            }
        }
    }

    removeAdminLink() {
        const adminLink = document.querySelector('.navbar-menu .admin-nav-link');
        if (adminLink && adminLink.parentElement) {
            adminLink.parentElement.remove();
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
            case 'analysis':
                // Analysis page doesn't need initial data load
                // It waits for user to enter a ticker
                console.log('Analysis page ready for ticker input');
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
                this.refreshAlerts(),
                this.refreshNews()
            ]);
        } else {
            await Promise.all([
                this.refreshRecommendations(),
                this.refreshNews()
            ]);
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
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📊</div>
                    <div class="empty-state-message">Keine Aktien in der Watchlist</div>
                    <div class="empty-state-hint">Fügen Sie Aktien über die Analyse-Seite oder den Screener hinzu</div>
                </div>
            `;
            return;
        }

        container.innerHTML = items.map(item => `
            <div class="watchlist-item clickable" onclick="app.navigateToAnalysis('${item.ticker}')" title="Klicken für Analyse von ${item.ticker}">
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

    async refreshAIRecommendations() {
        if (!this.currentUser) {
            this.showNotification('Bitte melden Sie sich an', 'error');
            return;
        }

        const container = document.getElementById('aiRecommendationsContent');
        const refreshBtn = document.getElementById('aiRefreshBtn');
        const refreshIcon = document.getElementById('aiRefreshIcon');
        const refreshText = document.getElementById('aiRefreshText');

        // Show loading state
        refreshBtn.disabled = true;
        refreshIcon.classList.add('spinning');
        refreshText.textContent = 'Analysiere...';

        container.innerHTML = `
            <div class="ai-recs-loading">
                <div class="loading-spinner"></div>
                <p>KI analysiert den Markt...</p>
                <p class="loading-note">Dies kann einige Minuten dauern</p>
            </div>
        `;

        try {
            const response = await api.getAIRecommendations();
            this.displayAIRecommendations(response);
            this.showNotification('KI-Analyse abgeschlossen', 'success');
        } catch (error) {
            container.innerHTML = `
                <div class="ai-recs-error">
                    <div class="error-icon">⚠️</div>
                    <p>Fehler bei der KI-Analyse</p>
                    <p class="error-note">${error.message || 'Bitte versuchen Sie es später erneut'}</p>
                </div>
            `;
            this.showNotification('KI-Analyse fehlgeschlagen', 'error');
        } finally {
            refreshBtn.disabled = false;
            refreshIcon.classList.remove('spinning');
            refreshText.textContent = 'Aktualisieren';
        }
    }

    displayAIRecommendations(data) {
        const container = document.getElementById('aiRecommendationsContent');
        const { top_buys, top_sells, analyzed_count, timestamp } = data;

        if (!top_buys || top_buys.length === 0) {
            container.innerHTML = `
                <div class="ai-recs-empty">
                    <div class="error-icon">⚠️</div>
                    <p><strong>Keine Kaufempfehlungen verfügbar</strong></p>
                    <p class="error-note">Mögliche Gründe:</p>
                    <ul class="error-reasons">
                        <li><strong>API-Limit erreicht:</strong> Alpha Vantage erlaubt nur 25 Anfragen pro Tag im kostenlosen Plan</li>
                        <li><strong>Finnhub/Twelve Data Schlüssel fehlen:</strong> Fügen Sie FINNHUB_API_KEY und TWELVE_DATA_API_KEY zur .env Datei hinzu</li>
                        <li><strong>Keine BUY-Empfehlungen:</strong> KI hat keine Kaufempfehlungen gefunden</li>
                    </ul>
                    <p class="error-note"><strong>Analysierte Aktien:</strong> ${analyzed_count || 0}</p>
                    <p class="error-note">💡 <strong>Tipp:</strong> Warten Sie bis morgen oder fügen Sie weitere API-Schlüssel hinzu</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="ai-recs-header">
                <div class="ai-recs-info">
                    <span class="ai-recs-count">📊 ${analyzed_count} Aktien analysiert</span>
                    <span class="ai-recs-time">⏱️ ${new Date(timestamp).toLocaleString('de-DE')}</span>
                </div>
            </div>

            <div class="ai-recs-grid">
                <!-- Top Buys -->
                <div class="ai-recs-section">
                    <div class="ai-recs-section-header buy">
                        <h4>🚀 Top 10 Kaufempfehlungen</h4>
                    </div>
                    <div class="ai-recs-list">
                        ${top_buys.map((stock, index) => this.createAIRecommendationCard(stock, index + 1, 'buy')).join('')}
                    </div>
                </div>

                <!-- Top Sells -->
                ${top_sells && top_sells.length > 0 ? `
                <div class="ai-recs-section">
                    <div class="ai-recs-section-header sell">
                        <h4>⚠️ Top 10 Verkaufsempfehlungen</h4>
                    </div>
                    <div class="ai-recs-list">
                        ${top_sells.map((stock, index) => this.createAIRecommendationCard(stock, index + 1, 'sell')).join('')}
                    </div>
                </div>
                ` : ''}
            </div>
        `;
    }

    createAIRecommendationCard(stock, rank, type) {
        const badgeClass = type === 'buy' ? 'badge-success' : 'badge-danger';
        const marketBadge = stock.market === 'US' ? '🇺🇸 US' : '🇩🇪 DE';

        return `
            <div class="ai-rec-card ${type}" onclick="app.showStockDetails('${stock.ticker}')">
                <div class="ai-rec-rank">#${rank}</div>
                <div class="ai-rec-main">
                    <div class="ai-rec-header">
                        <div class="ai-rec-ticker-group">
                            <span class="ai-rec-ticker">${stock.ticker}</span>
                            <span class="ai-rec-market-badge">${marketBadge}</span>
                        </div>
                        <span class="ai-rec-price">$${stock.current_price?.toFixed(2) || '-'}</span>
                    </div>
                    <div class="ai-rec-company">${stock.company_name}</div>
                    ${stock.summary ? `<div class="ai-rec-summary">${stock.summary}</div>` : ''}
                    <div class="ai-rec-metrics">
                        <span class="ai-rec-badge ${badgeClass}">${type === 'buy' ? 'KAUFEN' : 'VERKAUFEN'}</span>
                        <span class="ai-rec-confidence">
                            <span class="confidence-bar" style="--confidence: ${stock.confidence}%">
                                <span class="confidence-fill"></span>
                            </span>
                            <span class="confidence-text">${stock.confidence}% Vertrauen</span>
                        </span>
                        <span class="ai-rec-score">Score: ${stock.overall_score?.toFixed(0) || '-'}</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Navigate to analysis page and analyze a specific ticker
     * This is the central method for all ticker navigation across the app
     */
    navigateToAnalysis(ticker) {
        if (!ticker) {
            this.showNotification('Kein Ticker angegeben', 'error');
            return;
        }

        // Navigate to analysis page
        this.showPage('analysis');

        // Set ticker in search field
        document.getElementById('stockSearch').value = ticker.toUpperCase();

        // Trigger analysis
        this.analyzeStock();
    }

    // Alias for backward compatibility
    showStockDetails(ticker) {
        this.navigateToAnalysis(ticker);
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
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🔔</div>
                    <div class="empty-state-message">Keine aktiven Alerts</div>
                    <div class="empty-state-hint">Erstellen Sie Alerts auf der Alerts-Seite</div>
                </div>
            `;
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
        resultDiv.classList.add('loading');

        try {
            const [stockInfo, aiAnalysis] = await Promise.all([
                api.getStock(ticker),
                this.currentUser ? api.analyzeWithAI(ticker) : Promise.resolve(null)
            ]);

            resultDiv.classList.remove('loading');
            this.displayStockAnalysis(stockInfo, aiAnalysis);
        } catch (error) {
            resultDiv.classList.remove('loading');
            this.showNotification('Analyse fehlgeschlagen', 'error');
            resultDiv.style.display = 'none';
        }
    }

    displayStockAnalysis(data, aiAnalysis) {
        // Store current ticker and price for AI analysis
        this.currentAnalysisTicker = data.ticker;
        this.currentStockPrice = data.info.current_price;

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
        
        // Add event listener for watchlist button
        setTimeout(() => {
            const watchlistBtn = document.getElementById('addToWatchlistBtn');
            if (watchlistBtn) {
                watchlistBtn.addEventListener('click', () => this.addToWatchlistFromAnalysis());
            }
        }, 100);

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

        // Load interactive price chart
        this.loadPriceChart(data.ticker, this.currentPeriod);

        // Restore last active tab from localStorage
        this.restoreLastAnalysisTab();
    }

    restoreLastAnalysisTab() {
        const lastTab = localStorage.getItem('lastAnalysisTab');
        
        if (lastTab) {
            // Find the tab button and click it
            const tabButton = document.querySelector(`[data-analysis-tab="${lastTab}"]`);
            if (tabButton) {
                tabButton.click();
            }
        }
    }

    createOverviewContent(info) {
        return `
            <div class="overview-header-actions">
                <button id="addToWatchlistBtn" class="btn btn-primary watchlist-add-btn">
                    <span class="btn-icon">⭐</span>
                    Zur Watchlist hinzufügen
                </button>
            </div>
            <div class="metrics-grid">
                <div class="metric-item">
                    <span class="metric-label">Market Cap</span>
                    <span class="metric-value">${info.market_cap ? '$' + (info.market_cap).toFixed(2) + 'B' : 'N/A'}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Aktueller Kurs</span>
                    <span class="metric-value">$${info.current_price?.toFixed(2) || 'N/A'}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Tages-Hoch</span>
                    <span class="metric-value">$${info.day_high?.toFixed(2) || 'N/A'}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Tages-Tief</span>
                    <span class="metric-value">$${info.day_low?.toFixed(2) || 'N/A'}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Eröffnung</span>
                    <span class="metric-value">$${info.open?.toFixed(2) || 'N/A'}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Vortagesschluss</span>
                    <span class="metric-value">$${info.previous_close?.toFixed(2) || 'N/A'}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Börse</span>
                    <span class="metric-value">${info.exchange || 'N/A'}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Sektor</span>
                    <span class="metric-value">${info.sector || 'N/A'}</span>
                </div>
            </div>
            <div class="description">
                <h4>Über das Unternehmen</h4>
                <div class="company-info">
                    <div class="info-row">
                        <span class="info-label">Name:</span>
                        <span class="info-value">${info.company_name || 'N/A'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Industrie:</span>
                        <span class="info-value">${info.industry || 'N/A'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Land:</span>
                        <span class="info-value">${info.country || 'N/A'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Währung:</span>
                        <span class="info-value">${info.currency || 'USD'}</span>
                    </div>
                    ${info.website ? `
                    <div class="info-row">
                        <span class="info-label">Website:</span>
                        <span class="info-value"><a href="${info.website}" target="_blank" rel="noopener">${info.website}</a></span>
                    </div>
                    ` : ''}
                    ${info.logo ? `
                    <div class="company-logo">
                        <img src="${info.logo}" alt="${info.company_name} Logo" onerror="this.style.display='none'">
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    createTechnicalContent(technical) {
        // Store technical data for chart rendering
        this.currentTechnicalData = technical;

        return `
            <div class="technical-analysis-container">
                <!-- Visual Indicators -->
                <div class="technical-charts-grid">
                    <div class="tech-chart-card">
                        <h4>📊 RSI (Relative Strength Index)</h4>
                        <canvas id="rsiGaugeChart"></canvas>
                        <div class="indicator-status">
                            <span class="status-label">Status:</span>
                            <span class="status-value ${this.getRSIStatus(technical.rsi).class}">
                                ${this.getRSIStatus(technical.rsi).text}
                            </span>
                        </div>
                    </div>

                    <div class="tech-chart-card">
                        <h4>📈 MACD</h4>
                        <canvas id="macdChart"></canvas>
                        <div class="indicator-status">
                            <span class="status-label">Signal:</span>
                            <span class="status-value ${technical.macd?.macd > 0 ? 'bullish' : 'bearish'}">
                                ${technical.macd?.macd > 0 ? 'Bullisch' : 'Bärisch'}
                            </span>
                        </div>
                    </div>

                    <div class="tech-chart-card">
                        <h4>📉 Bollinger Bands Position</h4>
                        <canvas id="bollingerChart"></canvas>
                        <div class="indicator-status">
                            <span class="status-label">Position:</span>
                            <span class="status-value">${(technical.bollinger_bands?.current_position * 100)?.toFixed(1) || 'N/A'}%</span>
                        </div>
                    </div>

                    <div class="tech-chart-card">
                        <h4>⚡ Volatilität</h4>
                        <canvas id="volatilityChart"></canvas>
                        <div class="indicator-status">
                            <span class="status-label">Level:</span>
                            <span class="status-value ${technical.volatility > 0.5 ? 'high' : 'normal'}">
                                ${technical.volatility > 0.5 ? 'Hoch' : 'Normal'} (${(technical.volatility * 100)?.toFixed(1)}%)
                            </span>
                        </div>
                    </div>
                </div>

                <!-- Moving Averages Comparison -->
                <div class="tech-chart-card full-width">
                    <h4>📊 Moving Averages Vergleich</h4>
                    <canvas id="movingAveragesChart"></canvas>
                </div>

                <!-- Price Changes -->
                <div class="price-changes-grid">
                    <div class="price-change-card">
                        <div class="pc-label">1 Tag</div>
                        <div class="pc-value ${technical.price_change_1d > 0 ? 'positive' : 'negative'}">
                            ${technical.price_change_1d > 0 ? '+' : ''}${technical.price_change_1d?.toFixed(2) || 'N/A'}%
                        </div>
                    </div>
                    <div class="price-change-card">
                        <div class="pc-label">1 Woche</div>
                        <div class="pc-value ${technical.price_change_1w > 0 ? 'positive' : 'negative'}">
                            ${technical.price_change_1w > 0 ? '+' : ''}${technical.price_change_1w?.toFixed(2) || 'N/A'}%
                        </div>
                    </div>
                    <div class="price-change-card">
                        <div class="pc-label">1 Monat</div>
                        <div class="pc-value ${technical.price_change_1m > 0 ? 'positive' : 'negative'}">
                            ${technical.price_change_1m > 0 ? '+' : ''}${technical.price_change_1m?.toFixed(2) || 'N/A'}%
                        </div>
                    </div>
                    <div class="price-change-card">
                        <div class="pc-label">Volumen Trend</div>
                        <div class="pc-value">${technical.volume_trend || 'Normal'}</div>
                    </div>
                </div>
            </div>
        `;
    }

    getRSIStatus(rsi) {
        if (!rsi) return { text: 'N/A', class: '' };
        if (rsi > 70) return { text: 'Überkauft', class: 'overbought' };
        if (rsi < 30) return { text: 'Überverkauft', class: 'oversold' };
        return { text: 'Neutral', class: 'neutral' };
    }

    initTechnicalCharts(technical) {
        if (!technical) return;

        // RSI Gauge Chart
        this.createRSIGaugeChart(technical.rsi);

        // MACD Bar Chart
        this.createMACDChart(technical.macd);

        // Bollinger Bands Position Chart
        this.createBollingerChart(technical.bollinger_bands);

        // Volatility Gauge
        this.createVolatilityChart(technical.volatility);

        // Moving Averages Comparison
        this.createMovingAveragesChart(technical);
    }

    createRSIGaugeChart(rsi) {
        const canvas = document.getElementById('rsiGaugeChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        if (this.rsiChart) {
            this.rsiChart.destroy();
        }

        const rsiValue = rsi || 50;

        this.rsiChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [rsiValue, 100 - rsiValue],
                    backgroundColor: [
                        rsiValue > 70 ? '#ef4444' : rsiValue < 30 ? '#10b981' : '#3b82f6',
                        '#1f2937'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                cutout: '75%',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            },
            plugins: [{
                id: 'centerText',
                afterDraw: (chart) => {
                    const width = chart.width;
                    const height = chart.height;
                    const ctx = chart.ctx;
                    ctx.restore();
                    const fontSize = (height / 114).toFixed(2);
                    ctx.font = fontSize + "em sans-serif";
                    ctx.textBaseline = "middle";
                    ctx.fillStyle = '#fff';
                    const text = rsiValue.toFixed(1);
                    const textX = Math.round((width - ctx.measureText(text).width) / 2);
                    const textY = height / 2;
                    ctx.fillText(text, textX, textY);
                    ctx.save();
                }
            }]
        });
    }

    createMACDChart(macd) {
        const canvas = document.getElementById('macdChart');
        if (!canvas || !macd) return;

        const ctx = canvas.getContext('2d');

        if (this.macdChart) {
            this.macdChart.destroy();
        }

        this.macdChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['MACD', 'Signal', 'Histogram'],
                datasets: [{
                    data: [macd.macd || 0, macd.signal || 0, macd.histogram || 0],
                    backgroundColor: [
                        macd.macd > 0 ? '#10b981' : '#ef4444',
                        '#3b82f6',
                        macd.histogram > 0 ? '#10b981' : '#ef4444'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#9ca3af' },
                        grid: { color: '#374151' }
                    },
                    x: {
                        ticks: { color: '#9ca3af' },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    createBollingerChart(bollinger) {
        const canvas = document.getElementById('bollingerChart');
        if (!canvas || !bollinger) return;

        const ctx = canvas.getContext('2d');

        if (this.bollingerChart) {
            this.bollingerChart.destroy();
        }

        const position = bollinger.current_position || 0.5;

        this.bollingerChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Position in Band'],
                datasets: [{
                    label: 'Unteres Band',
                    data: [0],
                    backgroundColor: '#ef4444'
                }, {
                    label: 'Aktuelle Position',
                    data: [position],
                    backgroundColor: '#3b82f6'
                }, {
                    label: 'Oberes Band',
                    data: [1 - position],
                    backgroundColor: '#10b981'
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    x: {
                        stacked: true,
                        max: 1,
                        ticks: {
                            color: '#9ca3af',
                            callback: (value) => (value * 100) + '%'
                        },
                        grid: { color: '#374151' }
                    },
                    y: {
                        stacked: true,
                        ticks: { color: '#9ca3af' },
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        labels: { color: '#d1d5db' }
                    }
                }
            }
        });
    }

    createVolatilityChart(volatility) {
        const canvas = document.getElementById('volatilityChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        if (this.volatilityChart) {
            this.volatilityChart.destroy();
        }

        const volValue = (volatility || 0) * 100;

        this.volatilityChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [volValue, 100 - volValue],
                    backgroundColor: [
                        volValue > 50 ? '#ef4444' : '#3b82f6',
                        '#1f2937'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                cutout: '75%',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            },
            plugins: [{
                id: 'centerText',
                afterDraw: (chart) => {
                    const width = chart.width;
                    const height = chart.height;
                    const ctx = chart.ctx;
                    ctx.restore();
                    const fontSize = (height / 114).toFixed(2);
                    ctx.font = fontSize + "em sans-serif";
                    ctx.textBaseline = "middle";
                    ctx.fillStyle = '#fff';
                    const text = volValue.toFixed(1) + '%';
                    const textX = Math.round((width - ctx.measureText(text).width) / 2);
                    const textY = height / 2;
                    ctx.fillText(text, textX, textY);
                    ctx.save();
                }
            }]
        });
    }

    createMovingAveragesChart(technical) {
        const canvas = document.getElementById('movingAveragesChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        if (this.movingAveragesChart) {
            this.movingAveragesChart.destroy();
        }

        this.movingAveragesChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['SMA 20', 'SMA 50', 'EMA 12', 'EMA 26'],
                datasets: [{
                    label: 'Moving Averages',
                    data: [
                        technical.sma_20 || 0,
                        technical.sma_50 || 0,
                        technical.ema_12 || 0,
                        technical.ema_26 || 0
                    ],
                    backgroundColor: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            color: '#9ca3af',
                            callback: (value) => '$' + value.toFixed(2)
                        },
                        grid: { color: '#374151' }
                    },
                    x: {
                        ticks: { color: '#9ca3af' },
                        grid: { display: false }
                    }
                }
            }
        });
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

        // Save tab preference to localStorage
        localStorage.setItem('lastAnalysisTab', tab);

        // Load AI analysis when AI tab is selected
        if (tab === 'ai' && this.currentAnalysisTicker) {
            this.aiVisualizer.renderAnalysis(this.currentAnalysisTicker, this.currentStockPrice);
        }

        // Initialize technical charts when technical tab is selected
        if (tab === 'technical' && this.currentTechnicalData) {
            setTimeout(() => {
                this.initTechnicalCharts(this.currentTechnicalData);
            }, 100);
        }

        // Load news when news tab is selected
        if (tab === 'news' && this.currentAnalysisTicker) {
            if (!this.newsLoaded) {
                this.loadNewsTab(this.currentAnalysisTicker);
                this.newsLoaded = true;
            }
        }

        // Pre-fill first ticker when compare tab is selected
        if (tab === 'compare' && this.currentAnalysisTicker) {
            document.getElementById('compareTicker1').value = this.currentAnalysisTicker;
        }
    }

    // News functionality
    async loadNewsTab(ticker) {
        const newsContainer = document.getElementById('stockNewsContainer');
        newsContainer.innerHTML = '<div class="loading-news">Lade Nachrichten...</div>';
        
        try {
            const newsData = await api.getStockNews(ticker, 15, 7);
            this.currentNewsData = newsData;
            this.displayStockNews(newsData.news, 'all');
            
            // Set up filter buttons
            this.setupNewsFilters(newsData.news);
        } catch (error) {
            console.error('Error loading news:', error);
            newsContainer.innerHTML = '<div class="error-news">Fehler beim Laden der Nachrichten</div>';
        }
    }
    
    setupNewsFilters(newsArticles) {
        const filterButtons = document.querySelectorAll('.news-filters .filter-btn');
        
        filterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                // Remove active class from all buttons
                filterButtons.forEach(b => b.classList.remove('active'));
                
                // Add active class to clicked button
                btn.classList.add('active');
                
                // Filter news
                const filter = btn.dataset.filter;
                this.displayStockNews(newsArticles, filter);
            });
        });
    }
    
    displayStockNews(newsArticles, filter = 'all') {
        const container = document.getElementById('stockNewsContainer');
        
        // Filter articles
        let filteredNews = newsArticles;
        if (filter !== 'all') {
            filteredNews = newsArticles.filter(article => 
                article.sentiment.toLowerCase() === filter.toLowerCase()
            );
        }
        
        if (filteredNews.length === 0) {
            container.innerHTML = '<div class="no-news">Keine Nachrichten gefunden</div>';
            return;
        }
        
        container.innerHTML = filteredNews.map(article => this.createNewsCard(article)).join('');
    }
    
    createNewsCard(article) {
        const sentimentClass = {
            'bullish': 'sentiment-bullish',
            'neutral': 'sentiment-neutral',
            'bearish': 'sentiment-bearish'
        }[article.sentiment.toLowerCase()] || 'sentiment-neutral';
        
        const sentimentIcon = {
            'bullish': '🟢',
            'neutral': '⚪',
            'bearish': '🔴'
        }[article.sentiment.toLowerCase()] || '⚪';
        
        const timeAgo = this.formatNewsDate(article.date);
        const imageHtml = article.image ? 
            `<img src="${article.image}" alt="News thumbnail" class="news-thumbnail">` : '';
        
        return `
            <div class="stock-news-card" onclick="window.open('${article.url}', '_blank')">
                ${imageHtml}
                <div class="news-card-content">
                    <div class="news-card-header">
                        <span class="sentiment-badge ${sentimentClass}">
                            ${sentimentIcon} ${article.sentiment}
                        </span>
                        <span class="news-source">${article.source}</span>
                    </div>
                    <h4 class="news-headline">${article.headline}</h4>
                    ${article.summary ? `<p class="news-summary">${article.summary}</p>` : ''}
                    <div class="news-meta">
                        <span class="news-time">${timeAgo}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    formatNewsDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffHours < 1) return 'vor kurzem';
        if (diffHours < 24) return `vor ${diffHours} Std`;
        if (diffDays < 7) return `vor ${diffDays} Tag${diffDays > 1 ? 'en' : ''}`;
        
        return date.toLocaleDateString('de-DE');
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
        const resultsContainer = document.getElementById('screenerResults');
        resultsContainer.classList.add('loading');

        try {
            const response = await api.applyPresetScreen(presetName);
            resultsContainer.classList.remove('loading');
            this.displayScreenerResults(response.results);
            document.getElementById('resultCount').textContent = `(${response.count})`;
        } catch (error) {
            resultsContainer.classList.remove('loading');
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

        const resultsContainer = document.getElementById('screenerResults');
        resultsContainer.classList.add('loading');

        try {
            const response = await api.screenStocks(criteria);
            resultsContainer.classList.remove('loading');
            this.displayScreenerResults(response.results);
            document.getElementById('resultCount').textContent = `(${response.count})`;
        } catch (error) {
            resultsContainer.classList.remove('loading');
            this.showNotification('Screening fehlgeschlagen', 'error');
        }
    }

    displayScreenerResults(results) {
        const tbody = document.getElementById('screenerTableBody');

        if (results.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8">
                        <div class="empty-state">
                            <div class="empty-state-icon">🔍</div>
                            <div class="empty-state-message">Keine Ergebnisse gefunden</div>
                            <div class="empty-state-hint">Passen Sie Ihre Filterkriterien an oder versuchen Sie ein Preset</div>
                        </div>
                    </td>
                </tr>
            `;
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

        const container = document.getElementById('portfolioDetails');
        if (!container) {
            console.error('Portfolio container not found');
            return;
        }

        container.classList.add('loading');

        try {
            const portfolio = await api.getPortfolio();
            console.log('Portfolio loaded:', portfolio); // Debug log
            container.classList.remove('loading');
            this.displayPortfolioDetails(portfolio);
        } catch (error) {
            console.error('Error loading portfolio:', error);
            container.classList.remove('loading');
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
            <div class="export-actions">
                <button class="export-btn" onclick="app.exportPortfolio()">
                    📥 Export as CSV
                </button>
            </div>
        `;

        // Display holdings
        const tbody = document.getElementById('portfolioTableBody');
        if (portfolio.items.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7">
                        <div class="empty-state">
                            <div class="empty-state-icon">💼</div>
                            <div class="empty-state-message">Keine Positionen im Portfolio</div>
                            <div class="empty-state-hint">Fügen Sie Transaktionen hinzu, um Ihr Portfolio zu beginnen</div>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = portfolio.items.map(item => `
            <tr class="clickable" onclick="app.navigateToAnalysis('${item.ticker}')" style="cursor: pointer;" title="Klicken für Analyse von ${item.ticker}">
                <td><strong>${item.ticker}</strong></td>
                <td>${item.company_name}</td>
                <td>${item.shares}</td>
                <td>$${item.current_price?.toFixed(2) || '-'}</td>
                <td>$${item.current_value?.toFixed(2) || '-'}</td>
                <td class="${item.gain_loss_percent > 0 ? 'positive' : 'negative'}">
                    ${item.gain_loss_percent > 0 ? '+' : ''}${item.gain_loss_percent?.toFixed(2) || '0'}%
                </td>
                <td onclick="event.stopPropagation()">
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
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">⭐</div>
                    <div class="empty-state-message">Keine Aktien in der Watchlist</div>
                    <div class="empty-state-hint">Analysieren Sie Aktien und fügen Sie sie zur Watchlist hinzu</div>
                </div>
            `;
            return;
        }

        container.innerHTML = items.map(item => `
            <div class="watchlist-card card clickable" onclick="app.navigateToAnalysis('${item.ticker}')" title="Klicken für Analyse von ${item.ticker}">
                <h3>${item.ticker}</h3>
                <p>${item.company_name}</p>
                <div class="price-info">
                    <span class="current-price">$${item.current_price?.toFixed(2) || '-'}</span>
                    <span class="price-change ${item.price_change_percent > 0 ? 'positive' : 'negative'}">
                        ${item.price_change_percent > 0 ? '+' : ''}${item.price_change_percent?.toFixed(2) || '0'}%
                    </span>
                </div>
                <div class="watchlist-actions" onclick="event.stopPropagation()">
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

    // Export functions
    async exportPortfolio() {
        try {
            const portfolio = await api.getPortfolio();
            window.exportManager.exportPortfolioCSV(portfolio);
            this.showNotification('Portfolio erfolgreich exportiert', 'success');
        } catch (error) {
            this.showNotification('Export fehlgeschlagen', 'error');
        }
    }

    async exportWatchlist() {
        try {
            const response = await api.getWatchlist();
            window.exportManager.exportWatchlistCSV(response.items);
            this.showNotification('Watchlist erfolgreich exportiert', 'success');
        } catch (error) {
            this.showNotification('Export fehlgeschlagen', 'error');
        }
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
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🔔</div>
                    <div class="empty-state-message">Keine Alerts vorhanden</div>
                    <div class="empty-state-hint">Erstellen Sie Alerts für Ihre Watchlist-Aktien</div>
                </div>
            `;
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

    // Alert creation and management
    showCreateAlert() {
        this.showModal('alertModal');
        // Clear form
        document.getElementById('alertForm').reset();
    }

    createAlertForStock(ticker) {
        if (!ticker) {
            this.showNotification('Kein Ticker angegeben', 'error');
            return;
        }
        
        this.showModal('alertModal');
        // Pre-fill ticker
        document.getElementById('alertTicker').value = ticker.toUpperCase();
        // Clear other fields
        document.getElementById('alertCondition').value = 'above';
        document.getElementById('alertTargetPrice').value = '';
        document.getElementById('alertNote').value = '';
    }

    async handleCreateAlert(event) {
        event.preventDefault();

        if (!this.currentUser) {
            this.showNotification('Bitte melden Sie sich an', 'error');
            return;
        }

        const ticker = document.getElementById('alertTicker').value.toUpperCase();
        const condition = document.getElementById('alertCondition').value;
        const targetPrice = parseFloat(document.getElementById('alertTargetPrice').value);
        const note = document.getElementById('alertNote').value;

        if (!ticker || !targetPrice || targetPrice <= 0) {
            this.showNotification('Bitte füllen Sie alle erforderlichen Felder aus', 'error');
            return;
        }

        try {
            const alertData = {
                ticker: ticker,
                alert_type: condition === 'above' ? 'PRICE_ABOVE' : 'PRICE_BELOW',
                target_value: targetPrice,
                note: note || null
            };

            await api.createAlert(alertData);
            this.showNotification(`Alert für ${ticker} erstellt`, 'success');
            this.closeModal('alertModal');
            
            // Reload alerts if on alerts page
            if (this.currentPage === 'alerts') {
                await this.loadAlerts();
            }
        } catch (error) {
            this.showNotification(error.message || 'Alert konnte nicht erstellt werden', 'error');
        }
    }

    async deleteAlert(alertId) {
        if (!confirm('Möchten Sie diesen Alert wirklich löschen?')) {
            return;
        }

        try {
            await api.deleteAlert(alertId);
            this.showNotification('Alert gelöscht', 'success');
            await this.loadAlerts();
        } catch (error) {
            this.showNotification('Alert konnte nicht gelöscht werden', 'error');
        }
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
        const passwordConfirm = document.getElementById('registerPasswordConfirm').value;

        // Validate password match
        if (password !== passwordConfirm) {
            this.showNotification('Passwörter stimmen nicht überein', 'error');
            document.getElementById('passwordMatch').textContent = '❌ Passwörter stimmen nicht überein';
            document.getElementById('passwordMatch').style.color = '#e74c3c';
            return;
        }

        // Validate password length
        if (password.length < 6) {
            this.showNotification('Passwort muss mindestens 6 Zeichen lang sein', 'error');
            return;
        }

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

    async addToWatchlistFromAnalysis() {
        console.log('addToWatchlistFromAnalysis called');
        console.log('currentUser:', this.currentUser);
        console.log('currentAnalysisTicker:', this.currentAnalysisTicker);
        
        if (!this.currentUser) {
            this.showNotification('Bitte melden Sie sich an', 'error');
            return;
        }

        if (!this.currentAnalysisTicker) {
            this.showNotification('Keine Aktie analysiert', 'error');
            return;
        }

        try {
            await api.addToWatchlist(this.currentAnalysisTicker);
            this.showNotification(`${this.currentAnalysisTicker} zur Watchlist hinzugefügt`, 'success');
            // Refresh watchlist
            await this.loadWatchlistItems();
        } catch (error) {
            console.error('Error adding to watchlist:', error);
            if (error.message && error.message.includes('already exists')) {
                this.showNotification(`${this.currentAnalysisTicker} ist bereits in der Watchlist`, 'info');
            } else {
                this.showNotification('Fehler beim Hinzufügen zur Watchlist', 'error');
            }
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

    // Interactive Price Chart Methods
    async changePricePeriod(period) {
        if (!this.currentAnalysisTicker) return;

        this.currentPeriod = period;

        // Update active button
        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.period === period) {
                btn.classList.add('active');
            }
        });

        // Reload chart with new period
        await this.loadPriceChart(this.currentAnalysisTicker, period);
    }

    async loadPriceChart(ticker, period = '1y') {
        try {
            const history = await api.getStockHistory(ticker, period);
            
            if (!history || !history.data || history.data.length === 0) {
                console.error('No price history data available');
                return;
            }

            this.priceHistoryData = history;

            // Prepare data for Chart.js
            const dates = history.data.map(d => d.date);
            const prices = history.data.map(d => parseFloat(d.close));
            const volumes = history.data.map(d => parseInt(d.volume));

            // Calculate moving averages if enough data
            let sma50 = null;
            let sma200 = null;

            if (prices.length >= 50) {
                sma50 = this.calculateSMA(prices, 50);
            }

            if (prices.length >= 200) {
                sma200 = this.calculateSMA(prices, 200);
            }

            this.renderPriceChart(dates, prices, sma50, sma200);
            this.renderVolumeChart(dates, volumes);

        } catch (error) {
            console.error('Error loading price chart:', error);
            this.showNotification('Fehler beim Laden des Charts', 'error');
        }
    }

    calculateSMA(data, period) {
        const sma = [];
        for (let i = 0; i < data.length; i++) {
            if (i < period - 1) {
                sma.push(null);
            } else {
                const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
                sma.push(sum / period);
            }
        }
        return sma;
    }

    renderPriceChart(dates, prices, sma50, sma200) {
        const ctx = document.getElementById('priceChart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.priceChartInstance) {
            this.priceChartInstance.destroy();
        }

        const datasets = [
            {
                label: 'Preis',
                data: prices,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 2
            }
        ];

        // Add SMA50 if toggled and available
        if (this.showSMA50 && sma50) {
            datasets.push({
                label: 'SMA 50',
                data: sma50,
                borderColor: '#10b981',
                backgroundColor: 'transparent',
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: 0
            });
        }

        // Add SMA200 if toggled and available
        if (this.showSMA200 && sma200) {
            datasets.push({
                label: 'SMA 200',
                data: sma200,
                borderColor: '#ef4444',
                backgroundColor: 'transparent',
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: 0
            });
        }

        this.priceChartInstance = new Chart(ctx, {
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
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#9ca3af',
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleColor: '#f3f4f6',
                        bodyColor: '#d1d5db',
                        borderColor: '#374151',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: true,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += '$' + context.parsed.y.toFixed(2);
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#9ca3af',
                            maxTicksLimit: 10
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#9ca3af',
                            callback: function(value) {
                                return '$' + value.toFixed(2);
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        }
                    }
                }
            }
        });
    }

    renderVolumeChart(dates, volumes) {
        const ctx = document.getElementById('volumeChart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.volumeChartInstance) {
            this.volumeChartInstance.destroy();
        }

        this.volumeChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Volumen',
                    data: volumes,
                    backgroundColor: 'rgba(102, 126, 234, 0.6)',
                    borderColor: '#667eea',
                    borderWidth: 1
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
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleColor: '#f3f4f6',
                        bodyColor: '#d1d5db',
                        borderColor: '#374151',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                return 'Volumen: ' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#9ca3af',
                            maxTicksLimit: 10
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true, // Force Y-axis to start at 0
                        ticks: {
                            color: '#9ca3af',
                            maxTicksLimit: 5, // Limit number of Y-axis ticks
                            callback: function(value) {
                                return (value / 1000000).toFixed(1) + 'M';
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        }
                    }
                }
            }
        });
    }

    toggleMovingAverage(type) {
        if (type === 'sma50') {
            this.showSMA50 = document.getElementById('toggleSMA50').checked;
        } else if (type === 'sma200') {
            this.showSMA200 = document.getElementById('toggleSMA200').checked;
        }

        // Reload chart with updated MA visibility
        if (this.priceHistoryData) {
            const dates = this.priceHistoryData.data.map(d => d.date);
            const prices = this.priceHistoryData.data.map(d => parseFloat(d.close));
            const volumes = this.priceHistoryData.data.map(d => parseInt(d.volume));

            let sma50 = null;
            let sma200 = null;

            if (prices.length >= 50) {
                sma50 = this.calculateSMA(prices, 50);
            }

            if (prices.length >= 200) {
                sma200 = this.calculateSMA(prices, 200);
            }

            this.renderPriceChart(dates, prices, sma50, sma200);
        }
    }

    // Stock Comparison Methods
    async runComparison() {
        const ticker1 = document.getElementById('compareTicker1').value.trim().toUpperCase();
        const ticker2 = document.getElementById('compareTicker2').value.trim().toUpperCase();
        const ticker3 = document.getElementById('compareTicker3').value.trim().toUpperCase();
        const ticker4 = document.getElementById('compareTicker4').value.trim().toUpperCase();
        const period = document.getElementById('comparePeriod').value;

        const tickers = [ticker1, ticker2];
        if (ticker3) tickers.push(ticker3);
        if (ticker4) tickers.push(ticker4);

        if (tickers.length < 2) {
            this.showNotification('Bitte geben Sie mindestens 2 Ticker ein', 'error');
            return;
        }

        const resultsContainer = document.getElementById('compareResults');
        resultsContainer.style.display = 'block';
        resultsContainer.classList.add('loading');

        try {
            const comparisonData = await api.compareStocks(tickers, period);
            resultsContainer.classList.remove('loading');
            
            this.displayComparisonTable(comparisonData.comparison);
            this.renderComparisonChart(comparisonData.price_histories);
            
        } catch (error) {
            resultsContainer.classList.remove('loading');
            this.showNotification('Vergleich fehlgeschlagen: ' + error.message, 'error');
        }
    }

    displayComparisonTable(comparison) {
        const tableContainer = document.getElementById('compareTable');
        
        if (!comparison || comparison.length === 0) {
            tableContainer.innerHTML = '<p class="text-secondary">Keine Vergleichsdaten verfügbar</p>';
            return;
        }

        // Create table
        let html = `
            <div class="compare-table">
                <table>
                    <thead>
                        <tr>
                            <th>Kennzahl</th>
                            ${comparison.map(stock => `<th>${stock.ticker}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="metric-name">Unternehmen</td>
                            ${comparison.map(stock => `<td>${stock.company_name || '-'}</td>`).join('')}
                        </tr>
                        <tr>
                            <td class="metric-name">Aktueller Preis</td>
                            ${comparison.map(stock => `<td>$${stock.current_price?.toFixed(2) || '-'}</td>`).join('')}
                        </tr>
                        <tr>
                            <td class="metric-name">Marktkapitalisierung</td>
                            ${comparison.map(stock => `<td>${stock.market_cap ? '$' + (stock.market_cap / 1e9).toFixed(2) + 'B' : '-'}</td>`).join('')}
                        </tr>
                        <tr>
                            <td class="metric-name">KGV (P/E)</td>
                            ${comparison.map(stock => `<td>${stock.pe_ratio?.toFixed(2) || '-'}</td>`).join('')}
                        </tr>
                        <tr>
                            <td class="metric-name">Dividendenrendite</td>
                            ${comparison.map(stock => `<td>${stock.dividend_yield ? (stock.dividend_yield * 100).toFixed(2) + '%' : '-'}</td>`).join('')}
                        </tr>
                        <tr>
                            <td class="metric-name">Sektor</td>
                            ${comparison.map(stock => `<td>${stock.sector || '-'}</td>`).join('')}
                        </tr>
                        <tr>
                            <td class="metric-name">RSI</td>
                            ${comparison.map(stock => `<td>${stock.rsi?.toFixed(2) || '-'}</td>`).join('')}
                        </tr>
                        <tr>
                            <td class="metric-name">Volatilität</td>
                            ${comparison.map(stock => `<td>${stock.volatility ? (stock.volatility * 100).toFixed(2) + '%' : '-'}</td>`).join('')}
                        </tr>
                        <tr>
                            <td class="metric-name">1M Änderung</td>
                            ${comparison.map(stock => {
                                const change = stock.price_change_1m;
                                if (change === null || change === undefined) return '<td>-</td>';
                                const cssClass = change > 0 ? 'positive' : 'negative';
                                return `<td class="${cssClass}">${change > 0 ? '+' : ''}${change.toFixed(2)}%</td>`;
                            }).join('')}
                        </tr>
                        <tr>
                            <td class="metric-name">Volumen</td>
                            ${comparison.map(stock => `<td>${stock.volume ? stock.volume.toLocaleString() : '-'}</td>`).join('')}
                        </tr>
                    </tbody>
                </table>
            </div>
        `;

        tableContainer.innerHTML = html;
    }

    renderComparisonChart(priceHistories) {
        const ctx = document.getElementById('compareChart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.compareChartInstance) {
            this.compareChartInstance.destroy();
        }

        if (!priceHistories || priceHistories.length === 0) {
            return;
        }

        // Use the dates from the first ticker
        const dates = priceHistories[0].data.map(d => d.date);

        // Color palette for different stocks
        const colors = [
            '#667eea', // Purple
            '#10b981', // Green
            '#ef4444', // Red
            '#f59e0b'  // Orange
        ];

        const datasets = priceHistories.map((history, index) => ({
            label: history.ticker,
            data: history.data.map(d => d.normalized),
            borderColor: colors[index % colors.length],
            backgroundColor: 'transparent',
            borderWidth: 2,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 4
        }));

        this.compareChartInstance = new Chart(ctx, {
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
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#9ca3af',
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleColor: '#f3f4f6',
                        bodyColor: '#d1d5db',
                        borderColor: '#374151',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    const sign = context.parsed.y >= 0 ? '+' : '';
                                    label += sign + context.parsed.y.toFixed(2) + '%';
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#9ca3af',
                            maxTicksLimit: 10
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        }
                    },
                    y: {
                        maxTicksLimit: 8, // Limit number of Y-axis ticks
                        ticks: {
                            color: '#9ca3af',
                            callback: function(value) {
                                return value.toFixed(1) + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        }
                    }
                }
            }
        });
    }

    // ========================================
    // NEWS FUNCTIONALITY
    // ========================================

    async refreshNews() {
        const container = document.getElementById('newsContainer');
        container.classList.add('loading');
        container.innerHTML = '<div class="loading-spinner">Loading news...</div>';

        try {
            const newsData = await api.getMarketNews(15);
            this.displayNews(newsData.news);
            container.classList.remove('loading');
        } catch (error) {
            console.error('Error loading news:', error);
            container.classList.remove('loading');
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📰</div>
                    <div class="empty-state-message">Keine News verfügbar</div>
                    <div class="empty-state-hint">Fehler beim Laden der Nachrichten</div>
                </div>
            `;
        }
    }

    async loadStockNews(ticker) {
        try {
            const newsData = await api.getStockNews(ticker, 10, 7);
            return newsData;
        } catch (error) {
            console.error(`Error loading news for ${ticker}:`, error);
            return null;
        }
    }

    displayNews(articles) {
        const container = document.getElementById('newsContainer');

        if (!articles || articles.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📰</div>
                    <div class="empty-state-message">Keine News verfügbar</div>
                </div>
            `;
            return;
        }

        container.innerHTML = articles.map(article => {
            const date = article.date ? new Date(article.date).toLocaleString('de-DE', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            }) : 'Unbekannt';

            const sentimentClass = this.getSentimentClass(article.sentiment);
            const sentimentIcon = this.getSentimentIcon(article.sentiment);

            return `
                <div class="news-card" onclick="window.open('${article.url}', '_blank')">
                    ${article.image ? `
                        <div class="news-thumbnail">
                            <img src="${article.image}" alt="News thumbnail" onerror="this.parentElement.style.display='none'">
                        </div>
                    ` : ''}
                    <div class="news-content">
                        <div class="news-header">
                            <span class="news-source">${article.source}</span>
                            ${article.sentiment ? `<span class="sentiment-badge ${sentimentClass}">${sentimentIcon} ${article.sentiment}</span>` : ''}
                        </div>
                        <h4 class="news-headline">${article.headline}</h4>
                        ${article.summary ? `<p class="news-summary">${article.summary}</p>` : ''}
                        <div class="news-footer">
                            <span class="news-date">${date}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    getSentimentClass(sentiment) {
        switch(sentiment) {
            case 'bullish': return 'sentiment-bullish';
            case 'bearish': return 'sentiment-bearish';
            default: return 'sentiment-neutral';
        }
    }

    getSentimentIcon(sentiment) {
        switch(sentiment) {
            case 'bullish': return '🟢';
            case 'bearish': return '🔴';
            default: return '⚪';
        }
    }

    // Portfolio & Transaction Functions
    showAddTransaction() {
        // Set today's date as default
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('transactionDate').value = today;

        // Clear form
        document.getElementById('transactionForm').reset();

        // Show modal
        this.showModal('transactionModal');
    }

    async handleAddTransaction(e) {
        const ticker = document.getElementById('transactionTicker').value.toUpperCase();
        const type = document.getElementById('transactionType').value;
        const shares = parseFloat(document.getElementById('transactionShares').value);
        const price = parseFloat(document.getElementById('transactionPrice').value);
        const fees = parseFloat(document.getElementById('transactionFees').value) || 0;
        const date = document.getElementById('transactionDate').value;

        try {
            await api.addTransaction({
                ticker,
                transaction_type: type,
                shares,
                price,
                fees,
                transaction_date: date
            });

            this.showNotification(`Transaktion für ${ticker} erfolgreich hinzugefügt`, 'success');
            this.closeModal('transactionModal');

            // Refresh portfolio on both dashboard and portfolio page
            if (this.currentPage === 'portfolio') {
                await this.loadPortfolio();
            } else if (this.currentPage === 'dashboard') {
                await this.refreshPortfolio();
            }

            // Also reload to ensure visibility
            setTimeout(async () => {
                if (this.currentPage === 'portfolio') {
                    await this.loadPortfolio();
                }
            }, 500);
        } catch (error) {
            console.error('Error adding transaction:', error);
            this.showNotification(error.message || 'Fehler beim Hinzufügen der Transaktion', 'error');
        }
    }

    // Watchlist Functions
    showAddToWatchlist() {
        // Clear form
        document.getElementById('watchlistForm').reset();

        // Show modal
        this.showModal('watchlistModal');
    }

    async handleAddToWatchlist(e) {
        const ticker = document.getElementById('watchlistTicker').value.toUpperCase();
        const notes = document.getElementById('watchlistNotes').value;
        const tagsInput = document.getElementById('watchlistTags').value;

        // Parse tags
        const tags = tagsInput ? tagsInput.split(',').map(t => t.trim()).filter(t => t) : [];

        try {
            await api.addToWatchlist(ticker, notes, tags);

            this.showNotification(`${ticker} zur Watchlist hinzugefügt`, 'success');
            this.closeModal('watchlistModal');

            // Refresh watchlist if on watchlist page
            if (this.currentPage === 'watchlist') {
                await this.loadWatchlistItems();
            }
        } catch (error) {
            console.error('Error adding to watchlist:', error);
            this.showNotification(error.message || 'Fehler beim Hinzufügen zur Watchlist', 'error');
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new StockAnalyzerApp();
});