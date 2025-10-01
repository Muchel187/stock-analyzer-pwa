/**
 * Market Status Widget - Display real-time market open/closed status
 */
class MarketStatusWidget {
    constructor() {
        this.markets = {
            'NYSE': {
                name: 'NYSE',
                timezone: 'America/New_York',
                open: '09:30',
                close: '16:00',
                preMarketOpen: '04:00',
                afterHoursClose: '20:00'
            },
            'NASDAQ': {
                name: 'NASDAQ',
                timezone: 'America/New_York',
                open: '09:30',
                close: '16:00',
                preMarketOpen: '04:00',
                afterHoursClose: '20:00'
            },
            'XETRA': {
                name: 'Frankfurt',
                timezone: 'Europe/Berlin',
                open: '09:00',
                close: '17:30',
                preMarketOpen: '08:00',
                afterHoursClose: '22:00'
            }
        };
        
        this.updateInterval = null;
        this.init();
    }

    init() {
        this.createWidget();
        this.update();
        // Update every minute
        this.updateInterval = setInterval(() => this.update(), 60000);
    }

    createWidget() {
        const navUser = document.querySelector('.nav-user');
        if (!navUser) return;

        const container = document.createElement('div');
        container.className = 'market-status-widget';
        container.id = 'marketStatus';
        
        // Insert before theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            navUser.insertBefore(container, themeToggle);
        } else {
            navUser.insertBefore(container, navUser.firstChild);
        }
    }

    getMarketStatus(market) {
        const now = new Date();
        const marketInfo = this.markets[market];
        
        // Get market time (simplified - using local time for demo)
        const hours = now.getHours();
        const minutes = now.getMinutes();
        const currentTime = hours * 60 + minutes;
        
        // Parse market times
        const [openH, openM] = marketInfo.open.split(':').map(Number);
        const [closeH, closeM] = marketInfo.close.split(':').map(Number);
        const openTime = openH * 60 + openM;
        const closeTime = closeH * 60 + closeM;
        
        const [preH, preM] = marketInfo.preMarketOpen.split(':').map(Number);
        const [afterH, afterM] = marketInfo.afterHoursClose.split(':').map(Number);
        const preMarketTime = preH * 60 + preM;
        const afterHoursTime = afterH * 60 + afterM;
        
        // Weekend check
        const day = now.getDay();
        if (day === 0 || day === 6) {
            return { status: 'closed', label: 'Closed (Weekend)', class: 'closed' };
        }
        
        // Determine status
        if (currentTime >= openTime && currentTime < closeTime) {
            return { status: 'open', label: 'Market Open', class: 'open', countdown: this.getCountdown(closeTime - currentTime) };
        } else if (currentTime >= preMarketTime && currentTime < openTime) {
            return { status: 'pre-market', label: 'Pre-Market', class: 'pre-market', countdown: this.getCountdown(openTime - currentTime) };
        } else if (currentTime >= closeTime && currentTime < afterHoursTime) {
            return { status: 'after-hours', label: 'After Hours', class: 'after-hours', countdown: this.getCountdown(afterHoursTime - currentTime) };
        } else {
            return { status: 'closed', label: 'Market Closed', class: 'closed', countdown: this.getCountdown((24 * 60 - currentTime) + openTime) };
        }
    }

    getCountdown(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        
        if (hours > 0) {
            return `${hours}h ${mins}m`;
        } else {
            return `${mins}m`;
        }
    }

    update() {
        const container = document.getElementById('marketStatus');
        if (!container) return;

        // For now, show NYSE status (primary US market)
        const status = this.getMarketStatus('NYSE');
        
        container.innerHTML = `
            <div class="market-status-indicator ${status.class}" title="NYSE Market Status">
                <span class="status-dot"></span>
                <span class="status-text">${status.label}</span>
                ${status.countdown ? `<span class="status-countdown">(${status.countdown})</span>` : ''}
            </div>
        `;
    }

    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Initialize market status when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.marketStatus = new MarketStatusWidget();
    });
} else {
    window.marketStatus = new MarketStatusWidget();
}
