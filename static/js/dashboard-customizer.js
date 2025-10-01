/**
 * Dashboard Customizer
 * Allows users to show/hide dashboard widgets
 */

class DashboardCustomizer {
    constructor() {
        this.widgets = {
            'portfolio': true,
            'watchlist': true,
            'news': true,
            'ai-recommendations': true
        };
        this.customizationPanel = document.getElementById('customizationPanel');
        this.loadSettings();
    }
    
    loadSettings() {
        const saved = localStorage.getItem('dashboardWidgets');
        if (saved) {
            try {
                this.widgets = JSON.parse(saved);
            } catch (e) {
                console.error('Error loading dashboard settings:', e);
            }
        }
        this.applySettings();
    }
    
    applySettings() {
        Object.keys(this.widgets).forEach(widgetId => {
            const widget = document.getElementById(`${widgetId}-widget`);
            const toggle = document.getElementById(`toggle-${widgetId}`);
            
            if (widget) {
                widget.style.display = this.widgets[widgetId] ? 'block' : 'none';
            }
            if (toggle) {
                toggle.checked = this.widgets[widgetId];
            }
        });
    }
    
    toggleCustomization() {
        if (!this.customizationPanel) return;
        
        const isVisible = this.customizationPanel.style.display === 'block';
        this.customizationPanel.style.display = isVisible ? 'none' : 'block';
    }
    
    saveCustomization() {
        Object.keys(this.widgets).forEach(widgetId => {
            const toggle = document.getElementById(`toggle-${widgetId}`);
            if (toggle) {
                this.widgets[widgetId] = toggle.checked;
            }
        });
        
        localStorage.setItem('dashboardWidgets', JSON.stringify(this.widgets));
        this.applySettings();
        this.toggleCustomization();
        
        if (typeof app !== 'undefined') {
            app.showNotification('Dashboard-Einstellungen gespeichert', 'success');
        }
    }
    
    resetToDefault() {
        this.widgets = {
            'portfolio': true,
            'watchlist': true,
            'news': true,
            'ai-recommendations': true
        };
        
        localStorage.setItem('dashboardWidgets', JSON.stringify(this.widgets));
        this.applySettings();
        
        if (typeof app !== 'undefined') {
            app.showNotification('Dashboard-Einstellungen zurückgesetzt', 'success');
        }
    }
}

// Initialize
const dashboard = new DashboardCustomizer();
