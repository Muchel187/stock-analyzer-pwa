// API Service for all backend communications
class APIService {
    constructor() {
        this.baseURL = '/api';
        this.token = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
    }

    setTokens(accessToken, refreshToken) {
        this.token = accessToken;
        this.refreshToken = refreshToken;
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
    }

    clearTokens() {
        this.token = null;
        this.refreshToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        if (this.token) {
            config.headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, config);

            if (response.status === 401 && this.refreshToken) {
                // Try to refresh token
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    // Retry original request
                    config.headers['Authorization'] = `Bearer ${this.token}`;
                    const retryResponse = await fetch(url, config);
                    return await this.handleResponse(retryResponse);
                }
            }

            return await this.handleResponse(response);
        } catch (error) {
            throw error;
        }
    }

    async handleResponse(response) {
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }

        return data;
    }

    async refreshAccessToken() {
        try {
            const response = await fetch(`${this.baseURL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.refreshToken}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.token = data.access_token;
                localStorage.setItem('access_token', this.token);
                return true;
            }
        } catch (error) {
            console.error('Failed to refresh token:', error);
        }

        this.clearTokens();
        return false;
    }

    // Auth endpoints
    async login(email, password) {
        const response = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        this.setTokens(response.access_token, response.refresh_token);
        return response;
    }

    async register(email, username, password) {
        const response = await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, username, password })
        });
        this.setTokens(response.access_token, response.refresh_token);
        return response;
    }

    async logout() {
        await this.request('/auth/logout', { method: 'POST' });
        this.clearTokens();
    }

    async getProfile() {
        return await this.request('/auth/profile');
    }

    async updateProfile(data) {
        return await this.request('/auth/profile', {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // Stock endpoints
    async getStock(ticker) {
        return await this.request(`/stock/${ticker}`);
    }

    async getStockHistory(ticker, period = '1y') {
        return await this.request(`/stock/${ticker}/history?period=${period}`);
    }

    async analyzeWithAI(ticker) {
        return await this.request('/stock/analyze-with-ai', {
            method: 'POST',
            body: JSON.stringify({ ticker })
        });
    }

    async getBatchQuotes(tickers) {
        return await this.request('/stock/batch', {
            method: 'POST',
            body: JSON.stringify({ tickers })
        });
    }

    async searchStocks(query) {
        return await this.request(`/stock/search?q=${encodeURIComponent(query)}`);
    }

    async getRecommendations() {
        return await this.request('/stock/recommendations');
    }

    // Portfolio endpoints
    async getPortfolio() {
        return await this.request('/portfolio/');
    }

    async addTransaction(data) {
        return await this.request('/portfolio/transaction', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async getTransactions(ticker = null, limit = 50) {
        let url = `/portfolio/transactions?limit=${limit}`;
        if (ticker) url += `&ticker=${ticker}`;
        return await this.request(url);
    }

    async getPortfolioPerformance(period = '1M') {
        return await this.request(`/portfolio/performance?period=${period}`);
    }

    // Watchlist endpoints
    async getWatchlist() {
        return await this.request('/watchlist/');
    }

    async addToWatchlist(ticker, notes = '', tags = []) {
        return await this.request('/watchlist/', {
            method: 'POST',
            body: JSON.stringify({ ticker, notes, tags })
        });
    }

    async removeFromWatchlist(ticker) {
        return await this.request(`/watchlist/${ticker}`, {
            method: 'DELETE'
        });
    }

    async updateWatchlistItem(ticker, data) {
        return await this.request(`/watchlist/${ticker}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // Screener endpoints
    async screenStocks(criteria) {
        return await this.request('/screener/', {
            method: 'POST',
            body: JSON.stringify(criteria)
        });
    }

    async getScreenerPresets() {
        return await this.request('/screener/presets');
    }

    async applyPresetScreen(presetName) {
        return await this.request(`/screener/presets/${presetName}`, {
            method: 'POST'
        });
    }

    async getSectors() {
        return await this.request('/screener/sectors');
    }

    // Alerts endpoints
    async getAlerts(activeOnly = false) {
        return await this.request(`/alerts/?active_only=${activeOnly}`);
    }

    async createAlert(data) {
        return await this.request('/alerts/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async updateAlert(alertId, data) {
        return await this.request(`/alerts/${alertId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async deleteAlert(alertId) {
        return await this.request(`/alerts/${alertId}`, {
            method: 'DELETE'
        });
    }

    async getAlertStatistics() {
        return await this.request('/alerts/statistics');
    }

    // AI Recommendations endpoint
    async getAIRecommendations() {
        return await this.request('/stock/ai-recommendations', {
            method: 'POST'
        });
    }

    // Stock Comparison endpoint
    async compareStocks(tickers, period = '1y') {
        return await this.request('/stock/compare', {
            method: 'POST',
            body: JSON.stringify({ tickers, period })
        });
    }

    // News endpoints
    async getStockNews(ticker, limit = 10, days = 7) {
        return await this.request(`/stock/${ticker}/news?limit=${limit}&days=${days}`);
    }

    async getMarketNews(limit = 20) {
        return await this.request(`/stock/news/market?limit=${limit}`);
    }
}

// Create global API instance
const api = new APIService();