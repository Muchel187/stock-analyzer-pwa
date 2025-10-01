/**
 * Notification Center
 * Manages alert notifications and browser notifications
 */

class NotificationCenter {
    constructor(app) {
        this.app = app;
        this.panel = document.getElementById('notificationPanel');
        this.badge = document.getElementById('notificationBadge');
        this.button = document.getElementById('notificationBtn');
        this.checkInterval = null;
        
        if (this.panel && this.badge && this.button) {
            this.init();
        }
    }
    
    async init() {
        // Set up button click handler
        this.button.addEventListener('click', () => this.togglePanel());
        
        // Close panel on outside click
        document.addEventListener('click', (e) => {
            if (!this.button.contains(e.target) && !this.panel.contains(e.target)) {
                this.panel.style.display = 'none';
            }
        });
        
        // Request notification permission
        this.requestPermission();
        
        // Start polling for triggered alerts every 30 seconds
        this.checkInterval = setInterval(() => this.checkForNotifications(), 30000);
        
        // Initial check
        await this.checkForNotifications();
    }
    
    async checkForNotifications() {
        try {
            const response = await api.getTriggeredAlerts();
            const count = response.length;
            
            this.badge.textContent = count;
            this.badge.style.display = count > 0 ? 'flex' : 'none';
            
            // Show notification for new alerts
            if (count > 0) {
                const latestAlert = response[0];
                
                // Only show if we haven't shown this one before
                const lastShownId = localStorage.getItem('lastShownAlertId');
                if (lastShownId !== String(latestAlert.id)) {
                    this.showNotificationToast(latestAlert);
                    localStorage.setItem('lastShownAlertId', String(latestAlert.id));
                }
            }
        } catch (error) {
            console.error('Error checking notifications:', error);
        }
    }
    
    showNotificationToast(alert) {
        // Show browser notification if permission granted
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(`Alert: ${alert.ticker}`, {
                body: `Price ${alert.condition_type === 'above' ? 'über' : 'unter'} ${alert.target_price}. Aktuell: ${alert.current_price}`,
                icon: '/static/images/icon-192.png',
                tag: `alert-${alert.id}`,
                requireInteraction: true
            });
        }
        
        // Also show in-app toast
        this.app.showNotification(
            `🔔 Alert ausgelöst: ${alert.ticker} ist jetzt ${alert.current_price}`,
            'info',
            10000
        );
    }
    
    togglePanel() {
        const isVisible = this.panel.style.display === 'block';
        this.panel.style.display = isVisible ? 'none' : 'block';
        
        if (!isVisible) {
            this.loadNotifications();
        }
    }
    
    async loadNotifications() {
        const listEl = document.getElementById('notificationList');
        listEl.innerHTML = '<div class="loading-notifications">Lade...</div>';
        
        try {
            const alerts = await api.getTriggeredAlerts();
            
            if (alerts.length === 0) {
                listEl.innerHTML = '<p class="no-notifications">Keine neuen Benachrichtigungen</p>';
                return;
            }
            
            listEl.innerHTML = alerts.map(alert => this.createNotificationItem(alert)).join('');
        } catch (error) {
            console.error('Error loading notifications:', error);
            listEl.innerHTML = '<p class="error-notifications">Fehler beim Laden</p>';
        }
    }
    
    createNotificationItem(alert) {
        const timeAgo = this.formatTimeAgo(alert.triggered_at);
        const conditionText = alert.condition_type === 'above' ? 'über' : 'unter';
        
        return `
            <div class="notification-item" data-id="${alert.id}">
                <div class="notification-content">
                    <div class="notification-title">
                        <strong>${alert.ticker}</strong>
                        <span class="notification-time">${timeAgo}</span>
                    </div>
                    <div class="notification-message">
                        Preis ${conditionText} ${alert.target_price} erreicht
                    </div>
                    <div class="notification-price">
                        Aktuell: <strong>${alert.current_price}</strong>
                    </div>
                </div>
                <button class="notification-dismiss" onclick="notificationCenter.acknowledgeAlert(${alert.id}, event)">
                    ✓
                </button>
            </div>
        `;
    }
    
    async acknowledgeAlert(alertId, event) {
        if (event) {
            event.stopPropagation();
        }
        
        try {
            await api.acknowledgeAlert(alertId);
            
            // Remove from UI
            const item = document.querySelector(`.notification-item[data-id="${alertId}"]`);
            if (item) {
                item.style.opacity = '0';
                setTimeout(() => item.remove(), 300);
            }
            
            // Refresh badge count
            await this.checkForNotifications();
            
            // Reload list if still open
            if (this.panel.style.display === 'block') {
                await this.loadNotifications();
            }
        } catch (error) {
            console.error('Error acknowledging alert:', error);
            this.app.showNotification('Fehler beim Bestätigen', 'error');
        }
    }
    
    async markAllRead() {
        try {
            const alerts = await api.getTriggeredAlerts();
            
            for (const alert of alerts) {
                await api.acknowledgeAlert(alert.id);
            }
            
            await this.checkForNotifications();
            await this.loadNotifications();
            
            this.app.showNotification('Alle Benachrichtigungen gelesen', 'success');
        } catch (error) {
            console.error('Error marking all read:', error);
            this.app.showNotification('Fehler', 'error');
        }
    }
    
    formatTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'Gerade eben';
        if (diffMins < 60) return `vor ${diffMins} Min`;
        if (diffHours < 24) return `vor ${diffHours} Std`;
        if (diffDays < 7) return `vor ${diffDays} Tag${diffDays > 1 ? 'en' : ''}`;
        
        return date.toLocaleDateString('de-DE');
    }
    
    requestPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    console.log('Notification permission granted');
                }
            });
        }
    }
    
    destroy() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
        }
    }
}

// Initialize
let notificationCenter;
document.addEventListener('DOMContentLoaded', () => {
    if (typeof app !== 'undefined' && app.currentUser) {
        notificationCenter = new NotificationCenter(app);
    }
});
