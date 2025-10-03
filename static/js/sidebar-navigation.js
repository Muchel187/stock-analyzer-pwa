/**
 * SIDEBAR NAVIGATION - TradingView Style
 * Professional collapsible sidebar with smooth animations
 */

class SidebarNavigation {
    constructor() {
        this.sidebar = null;
        this.overlay = null;
        this.isExpanded = false;
        this.isMobile = window.innerWidth <= 768;

        this.init();
    }

    init() {
        this.createSidebar();
        this.attachEventListeners();
        this.handleResize();

        // Restore sidebar state from localStorage
        const savedState = localStorage.getItem('sidebarExpanded');
        if (savedState === 'true' && !this.isMobile) {
            this.expand();
        }
    }

    createSidebar() {
        // Create sidebar HTML
        const sidebarHTML = `
            <aside class="sidebar" id="mainSidebar">
                <!-- Toggle Button -->
                <button class="sidebar-toggle" aria-label="Toggle Sidebar">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 18l6-6-6-6"/>
                    </svg>
                </button>

                <!-- Header -->
                <div class="sidebar-header">
                    <div class="sidebar-logo">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <span class="sidebar-brand">Aktieninspektor</span>
                </div>

                <!-- Navigation -->
                <nav class="sidebar-nav">
                    <!-- Main Section -->
                    <a href="/" class="nav-item" data-page="dashboard">
                        <span class="nav-icon">
                            <i class="fas fa-chart-pie"></i>
                        </span>
                        <span class="nav-text">Dashboard</span>
                        <span class="nav-tooltip">Dashboard</span>
                    </a>

                    <a href="#" class="nav-item" data-page="analysis">
                        <span class="nav-icon">
                            <i class="fas fa-search-dollar"></i>
                        </span>
                        <span class="nav-text">Analyse</span>
                        <span class="nav-tooltip">Aktienanalyse</span>
                    </a>

                    <a href="#" class="nav-item" data-page="portfolio">
                        <span class="nav-icon">
                            <i class="fas fa-briefcase"></i>
                        </span>
                        <span class="nav-text">Portfolio</span>
                        <span class="nav-tooltip">Mein Portfolio</span>
                    </a>

                    <a href="#" class="nav-item" data-page="watchlist">
                        <span class="nav-icon">
                            <i class="fas fa-star"></i>
                        </span>
                        <span class="nav-text">Watchlist</span>
                        <span class="nav-tooltip">Watchlist</span>
                    </a>

                    <a href="#" class="nav-item" data-page="alerts">
                        <span class="nav-icon">
                            <i class="fas fa-bell"></i>
                        </span>
                        <span class="nav-text">Alerts</span>
                        <span class="nav-badge" id="alertsBadge" style="display: none;">0</span>
                        <span class="nav-tooltip">Preisalarme</span>
                    </a>

                    <!-- Tools Section -->
                    <div class="nav-section">
                        <div class="nav-section-title">Tools</div>
                    </div>

                    <a href="#" class="nav-item" data-page="screener">
                        <span class="nav-icon">
                            <i class="fas fa-filter"></i>
                        </span>
                        <span class="nav-text">Screener</span>
                        <span class="nav-tooltip">Aktien-Screener</span>
                    </a>

                    <a href="#" class="nav-item" data-page="compare">
                        <span class="nav-icon">
                            <i class="fas fa-balance-scale"></i>
                        </span>
                        <span class="nav-text">Vergleich</span>
                        <span class="nav-tooltip">Aktienvergleich</span>
                    </a>

                    <a href="#" class="nav-item" data-page="news">
                        <span class="nav-icon">
                            <i class="fas fa-newspaper"></i>
                        </span>
                        <span class="nav-text">News</span>
                        <span class="nav-tooltip">Marktnachrichten</span>
                    </a>

                    <!-- AI Section -->
                    <div class="nav-section">
                        <div class="nav-section-title">KI-Analyse</div>
                    </div>

                    <a href="#" class="nav-item" data-page="ai-analysis">
                        <span class="nav-icon">
                            <i class="fas fa-brain"></i>
                        </span>
                        <span class="nav-text">KI-Analyse</span>
                        <span class="nav-tooltip">KI-gestützte Analyse</span>
                    </a>

                    <a href="#" class="nav-item" data-page="ai-recommendations">
                        <span class="nav-icon">
                            <i class="fas fa-robot"></i>
                        </span>
                        <span class="nav-text">KI-Empfehlungen</span>
                        <span class="nav-tooltip">KI-Empfehlungen</span>
                    </a>
                </nav>

                <!-- Footer / User Profile -->
                <div class="sidebar-footer">
                    <div class="user-profile" id="userProfile">
                        <div class="user-avatar" id="userAvatar">U</div>
                        <div class="user-info">
                            <div class="user-name" id="userName">Benutzer</div>
                            <div class="user-email" id="userEmail">user@email.com</div>
                        </div>
                    </div>
                </div>
            </aside>

            <!-- Mobile Overlay -->
            <div class="sidebar-overlay" id="sidebarOverlay"></div>
        `;

        // Insert sidebar at the beginning of body
        document.body.insertAdjacentHTML('afterbegin', sidebarHTML);

        this.sidebar = document.getElementById('mainSidebar');
        this.overlay = document.getElementById('sidebarOverlay');

        // Set active page
        this.setActivePage();
    }

    attachEventListeners() {
        // Toggle button
        const toggleBtn = this.sidebar.querySelector('.sidebar-toggle');
        toggleBtn.addEventListener('click', () => this.toggle());

        // Mobile overlay
        this.overlay.addEventListener('click', () => {
            if (this.isMobile) {
                this.collapse();
            }
        });

        // Nav items
        const navItems = this.sidebar.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => this.handleNavClick(e));
        });

        // User profile
        const userProfile = document.getElementById('userProfile');
        userProfile.addEventListener('click', () => this.showUserMenu());

        // Window resize
        window.addEventListener('resize', () => this.handleResize());

        // Keyboard shortcut (Ctrl/Cmd + B to toggle sidebar)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
                e.preventDefault();
                this.toggle();
            }
        });
    }

    toggle() {
        if (this.isExpanded) {
            this.collapse();
        } else {
            this.expand();
        }
    }

    expand() {
        this.sidebar.classList.add('expanded');
        this.isExpanded = true;

        if (this.isMobile) {
            this.overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        } else {
            localStorage.setItem('sidebarExpanded', 'true');
        }
    }

    collapse() {
        this.sidebar.classList.remove('expanded');
        this.isExpanded = false;

        if (this.isMobile) {
            this.overlay.classList.remove('active');
            document.body.style.overflow = '';
        } else {
            localStorage.setItem('sidebarExpanded', 'false');
        }
    }

    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= 768;

        if (wasMobile !== this.isMobile) {
            if (this.isMobile) {
                // Switch to mobile
                this.collapse();
            } else {
                // Switch to desktop
                this.overlay.classList.remove('active');
                document.body.style.overflow = '';

                // Restore desktop state
                const savedState = localStorage.getItem('sidebarExpanded');
                if (savedState === 'true') {
                    this.expand();
                }
            }
        }
    }

    handleNavClick(e) {
        const item = e.currentTarget;
        const page = item.dataset.page;

        // Don't prevent default for actual links
        if (item.getAttribute('href') === '#') {
            e.preventDefault();
        }

        // Update active state
        this.sidebar.querySelectorAll('.nav-item').forEach(navItem => {
            navItem.classList.remove('active');
        });
        item.classList.add('active');

        // Store active page
        localStorage.setItem('activePage', page);

        // Close sidebar on mobile after navigation
        if (this.isMobile) {
            this.collapse();
        }

        // Emit custom event for page navigation
        const event = new CustomEvent('sidebar-navigate', {
            detail: { page }
        });
        document.dispatchEvent(event);
    }

    setActivePage() {
        const currentPath = window.location.pathname;
        const savedPage = localStorage.getItem('activePage');

        let activePage = 'dashboard';

        if (currentPath === '/') {
            activePage = 'dashboard';
        } else if (currentPath.includes('analysis')) {
            activePage = 'analysis';
        } else if (currentPath.includes('portfolio')) {
            activePage = 'portfolio';
        } else if (savedPage) {
            activePage = savedPage;
        }

        const activeItem = this.sidebar.querySelector(`[data-page="${activePage}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }

    updateUserInfo(user) {
        if (!user) return;

        const userName = document.getElementById('userName');
        const userEmail = document.getElementById('userEmail');
        const userAvatar = document.getElementById('userAvatar');

        if (user.username) {
            userName.textContent = user.username;
        }
        if (user.email) {
            userEmail.textContent = user.email;
        }
        if (user.username) {
            userAvatar.textContent = user.username.charAt(0).toUpperCase();
        }
    }

    updateAlertsBadge(count) {
        const badge = document.getElementById('alertsBadge');
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }
    }

    showUserMenu() {
        // Create dropdown menu
        const menu = document.createElement('div');
        menu.className = 'user-dropdown-menu';
        menu.innerHTML = `
            <div class="dropdown-item" data-action="profile">
                <i class="fas fa-user"></i>
                <span>Profil</span>
            </div>
            <div class="dropdown-item" data-action="settings">
                <i class="fas fa-cog"></i>
                <span>Einstellungen</span>
            </div>
            <div class="dropdown-divider"></div>
            <div class="dropdown-item" data-action="logout">
                <i class="fas fa-sign-out-alt"></i>
                <span>Abmelden</span>
            </div>
        `;

        // Position menu
        const userProfile = document.getElementById('userProfile');
        const rect = userProfile.getBoundingClientRect();

        menu.style.position = 'fixed';
        menu.style.bottom = `${window.innerHeight - rect.top + 8}px`;
        menu.style.left = this.isExpanded ? `${rect.left}px` : `${rect.right + 8}px`;

        document.body.appendChild(menu);

        // Animate in
        setTimeout(() => menu.classList.add('active'), 10);

        // Handle clicks
        menu.addEventListener('click', (e) => {
            const item = e.target.closest('.dropdown-item');
            if (item) {
                const action = item.dataset.action;
                this.handleUserMenuAction(action);
                this.closeUserMenu(menu);
            }
        });

        // Close on outside click
        setTimeout(() => {
            document.addEventListener('click', (e) => {
                if (!menu.contains(e.target) && !userProfile.contains(e.target)) {
                    this.closeUserMenu(menu);
                }
            }, { once: true });
        }, 100);
    }

    closeUserMenu(menu) {
        menu.classList.remove('active');
        setTimeout(() => menu.remove(), 200);
    }

    handleUserMenuAction(action) {
        switch (action) {
            case 'profile':
                window.location.href = '/profile';
                break;
            case 'settings':
                window.location.href = '/settings';
                break;
            case 'logout':
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
                break;
        }
    }

    // Public method to open sidebar programmatically
    open() {
        this.expand();
    }

    // Public method to close sidebar programmatically
    close() {
        this.collapse();
    }
}

// User Dropdown Menu Styles (inject into head)
const userMenuStyles = `
<style>
.user-dropdown-menu {
    background: var(--bg-elevated);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-xl);
    padding: var(--space-2);
    min-width: 200px;
    z-index: var(--z-dropdown);
    opacity: 0;
    transform: translateY(4px);
    transition: all var(--transition-fast);
}

.user-dropdown-menu.active {
    opacity: 1;
    transform: translateY(0);
}

.dropdown-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    cursor: pointer;
    transition: all var(--transition-fast);
}

.dropdown-item:hover {
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-primary);
}

.dropdown-item i {
    width: 16px;
    text-align: center;
}

.dropdown-divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.1);
    margin: var(--space-2) 0;
}
</style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', userMenuStyles);

// Initialize sidebar when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.sidebarNav = new SidebarNavigation();
    });
} else {
    window.sidebarNav = new SidebarNavigation();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SidebarNavigation;
}
