/**
 * Global Search Functionality
 * Provides search-from-anywhere with autocomplete and history
 */

class GlobalSearch {
    constructor(app) {
        this.app = app;
        this.input = document.getElementById('globalSearch');
        this.dropdown = document.getElementById('searchDropdown');
        this.searchHistory = JSON.parse(localStorage.getItem('searchHistory')) || [];
        
        if (this.input && this.dropdown) {
            this.init();
        }
    }
    
    init() {
        // Debounced search
        let timeout;
        this.input.addEventListener('input', (e) => {
            clearTimeout(timeout);
            const value = e.target.value.trim();
            
            if (value.length === 0) {
                this.showRecentSearches();
                return;
            }
            
            timeout = setTimeout(() => this.handleSearch(value), 300);
        });
        
        // Enter to analyze
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const ticker = this.input.value.trim().toUpperCase();
                if (ticker) {
                    this.selectTicker(ticker);
                }
            }
        });
        
        // Show recent searches on focus
        this.input.addEventListener('focus', () => {
            if (this.input.value.trim().length === 0) {
                this.showRecentSearches();
            }
        });
        
        // Close dropdown on outside click
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.dropdown.contains(e.target)) {
                this.dropdown.style.display = 'none';
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.input.focus();
                this.input.select();
            }
            
            // Escape to clear
            if (e.key === 'Escape' && document.activeElement === this.input) {
                this.input.value = '';
                this.dropdown.style.display = 'none';
                this.input.blur();
            }
        });
    }
    
    async handleSearch(query) {
        if (!query || query.length < 1) {
            this.showRecentSearches();
            return;
        }

        try {
            // Use existing search endpoint
            const response = await api.searchStocks(query);
            const results = response.results || [];
            this.showResults(results, query);
        } catch (error) {
            console.error('Search error:', error);
            this.dropdown.innerHTML = '<div class="search-no-results">Fehler beim Suchen</div>';
            this.dropdown.style.display = 'block';
        }
    }
    
    showResults(results, query) {
        if (results.length === 0) {
            this.dropdown.innerHTML = `
                <div class="search-no-results">
                    Keine Ergebnisse für "${query}"
                </div>
            `;
            this.dropdown.style.display = 'block';
            return;
        }

        this.dropdown.innerHTML = results.slice(0, 8).map(stock => `
            <div class="search-result-item" onclick="globalSearch.selectTicker('${stock.ticker}')">
                <div class="search-result-main">
                    <div class="search-result-ticker">${stock.ticker}</div>
                    <div class="search-result-name">${stock.company_name || stock.name || ''}</div>
                </div>
            </div>
        `).join('');

        this.dropdown.style.display = 'block';
    }
    
    showRecentSearches() {
        if (this.searchHistory.length === 0) {
            this.dropdown.style.display = 'none';
            return;
        }
        
        this.dropdown.innerHTML = `
            <div class="search-section-header">Zuletzt gesucht</div>
            ${this.searchHistory.map(ticker => `
                <div class="search-result-item" onclick="globalSearch.selectTicker('${ticker}')">
                    <div class="search-result-main">
                        <div class="search-result-ticker">${ticker}</div>
                        <span class="search-history-icon">🕐</span>
                    </div>
                </div>
            `).join('')}
            <div class="search-clear-history">
                <button class="btn-link" onclick="globalSearch.clearHistory()">Verlauf löschen</button>
            </div>
        `;
        
        this.dropdown.style.display = 'block';
    }
    
    selectTicker(ticker) {
        ticker = ticker.toUpperCase().trim();
        if (!ticker) return;
        
        // Add to history
        this.addToHistory(ticker);
        
        // Clear input
        this.input.value = '';
        this.dropdown.style.display = 'none';
        
        // Navigate to analysis
        this.app.navigateToAnalysis(ticker);
    }
    
    addToHistory(ticker) {
        // Remove if already exists
        this.searchHistory = this.searchHistory.filter(t => t !== ticker);
        
        // Add to beginning
        this.searchHistory.unshift(ticker);
        
        // Keep only last 10
        this.searchHistory = this.searchHistory.slice(0, 10);
        
        // Save
        localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory));
    }
    
    clearHistory() {
        this.searchHistory = [];
        localStorage.removeItem('searchHistory');
        this.dropdown.style.display = 'none';
        this.app.showNotification('Suchverlauf gelöscht', 'success');
    }
}

// Initialize on page load
let globalSearch;
document.addEventListener('DOMContentLoaded', () => {
    if (typeof app !== 'undefined') {
        globalSearch = new GlobalSearch(app);
    }
});
