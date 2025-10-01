/**
 * Theme Manager - Handle dark/light/auto theme switching
 */
class ThemeManager {
    constructor() {
        this.themes = ['auto', 'light', 'dark'];
        this.currentTheme = localStorage.getItem('theme') || 'auto';
        this.init();
    }

    init() {
        this.applyTheme();
        this.watchSystemTheme();
        this.createThemeToggle();
    }

    applyTheme() {
        const body = document.body;
        
        if (this.currentTheme === 'auto') {
            // Use system preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            body.classList.toggle('dark-theme', prefersDark);
            body.classList.remove('light-theme');
        } else if (this.currentTheme === 'dark') {
            body.classList.add('dark-theme');
            body.classList.remove('light-theme');
        } else {
            body.classList.add('light-theme');
            body.classList.remove('dark-theme');
        }
        
        // Update toggle button icon
        this.updateToggleIcon();
    }

    watchSystemTheme() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', () => {
            if (this.currentTheme === 'auto') {
                this.applyTheme();
            }
        });
    }

    toggleTheme() {
        const currentIndex = this.themes.indexOf(this.currentTheme);
        this.currentTheme = this.themes[(currentIndex + 1) % this.themes.length];
        localStorage.setItem('theme', this.currentTheme);
        this.applyTheme();
    }

    createThemeToggle() {
        // Add theme toggle button to nav-user section
        const navUser = document.querySelector('.nav-user');
        if (!navUser) return;

        const themeBtn = document.createElement('button');
        themeBtn.className = 'theme-toggle-btn btn-icon';
        themeBtn.id = 'themeToggle';
        themeBtn.title = 'Toggle Theme (Auto/Light/Dark)';
        themeBtn.onclick = () => this.toggleTheme();
        
        // Insert before login button
        navUser.insertBefore(themeBtn, navUser.firstChild);
        
        this.updateToggleIcon();
    }

    updateToggleIcon() {
        const btn = document.getElementById('themeToggle');
        if (!btn) return;

        const icons = {
            'auto': '🌓',
            'light': '☀️',
            'dark': '🌙'
        };

        btn.textContent = icons[this.currentTheme] || '🌓';
        btn.title = `Theme: ${this.currentTheme.charAt(0).toUpperCase() + this.currentTheme.slice(1)}`;
    }

    getCurrentTheme() {
        return this.currentTheme;
    }

    setTheme(theme) {
        if (this.themes.includes(theme)) {
            this.currentTheme = theme;
            localStorage.setItem('theme', theme);
            this.applyTheme();
        }
    }
}

// Initialize theme manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.themeManager = new ThemeManager();
    });
} else {
    window.themeManager = new ThemeManager();
}
