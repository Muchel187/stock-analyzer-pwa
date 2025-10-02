/**
 * Admin Dashboard Application
 * Handles all admin functionality for user management
 */

class AdminApp {
    constructor() {
        this.currentPage = 1;
        this.perPage = 10;
        this.searchTerm = '';
        this.filterType = '';
        this.currentUser = null;
        this.userToDelete = null;
        this.userToEdit = null;
    }

    /**
     * Initialize the admin application
     */
    async init() {
        // Check if user is admin
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/';
            return;
        }

        // Verify admin status
        try {
            await api.checkAdmin();
        } catch (error) {
            console.error('Admin check failed:', error);
            this.showNotification('Keine Admin-Berechtigung', 'error');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
            return;
        }

        // Set user display
        const username = localStorage.getItem('username');
        if (username) {
            document.getElementById('userDisplay').textContent = `Admin: ${username}`;
        }

        // Load initial data
        await this.loadSystemStats();
        await this.loadUsers();

        // Setup event listeners
        this.setupEventListeners();

        // Start periodic refresh
        setInterval(() => this.loadSystemStats(), 60000); // Refresh stats every minute
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById('userSearch');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => {
                this.searchTerm = searchInput.value;
                this.currentPage = 1;
                this.loadUsers();
            }, 500));
        }

        // Filter select
        const filterSelect = document.getElementById('userFilter');
        if (filterSelect) {
            filterSelect.addEventListener('change', () => {
                this.filterType = filterSelect.value;
                this.currentPage = 1;
                this.loadUsers();
            });
        }

        // Close modals on outside click
        window.addEventListener('click', (event) => {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
            }
        });
    }

    /**
     * Load system statistics
     */
    async loadSystemStats() {
        try {
            const stats = await api.getAdminStats();

            // Update stat cards
            this.updateStatCard('totalUsers', stats.total_users);
            this.updateStatCard('activeToday', stats.active_users_today);
            this.updateStatCard('totalPortfolios', stats.total_portfolios);
            this.updateStatCard('totalAlerts', stats.total_alerts);
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    /**
     * Update a stat card
     */
    updateStatCard(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value !== undefined ? value.toLocaleString('de-DE') : '-';
        }
    }

    /**
     * Load users list
     */
    async loadUsers() {
        this.showLoading(true);

        try {
            const params = {
                page: this.currentPage,
                per_page: this.perPage
            };

            if (this.searchTerm) {
                params.search = this.searchTerm;
            }

            if (this.filterType === 'admin') {
                params.is_admin = true;
            } else if (this.filterType === 'regular') {
                params.is_admin = false;
            }

            const result = await api.getAdminUsers(params);
            this.renderUsersTable(result.users);
            this.renderPagination(result);
        } catch (error) {
            console.error('Error loading users:', error);
            this.showNotification('Fehler beim Laden der Benutzer', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Render users table
     */
    renderUsersTable(users) {
        const tbody = document.getElementById('usersTableBody');
        if (!tbody) return;

        if (users.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center">Keine Benutzer gefunden</td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = users.map(user => `
            <tr>
                <td>${user.id}</td>
                <td>${this.escapeHtml(user.username)}</td>
                <td>${this.escapeHtml(user.email)}</td>
                <td>
                    <span class="badge ${user.is_admin ? 'badge-admin' : 'badge-user'}">
                        ${user.is_admin ? 'Admin' : 'Benutzer'}
                    </span>
                </td>
                <td>${this.formatDate(user.created_at)}</td>
                <td>${user.last_login ? this.formatDate(user.last_login) : 'Nie'}</td>
                <td>${user.portfolio_count || 0}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-icon" onclick="adminApp.viewUserDetails(${user.id})" title="Details">
                            👁️
                        </button>
                        <button class="btn-icon" onclick="adminApp.editUser(${user.id})" title="Bearbeiten">
                            ✏️
                        </button>
                        <button class="btn-icon" onclick="adminApp.toggleAdminStatus(${user.id}, ${user.is_admin})" title="Admin-Status">
                            ${user.is_admin ? '🔓' : '🔒'}
                        </button>
                        <button class="btn-icon btn-danger" onclick="adminApp.deleteUser(${user.id}, '${this.escapeHtml(user.username)}')" title="Löschen">
                            🗑️
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    /**
     * Render pagination controls
     */
    renderPagination(data) {
        const container = document.getElementById('usersPagination');
        if (!container) return;

        const totalPages = data.total_pages || 1;
        const currentPage = data.page || 1;

        let html = '<div class="pagination-controls">';

        // Previous button
        if (currentPage > 1) {
            html += `<button class="btn-page" onclick="adminApp.goToPage(${currentPage - 1})">‹</button>`;
        }

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
                html += `<button class="btn-page ${i === currentPage ? 'active' : ''}"
                         onclick="adminApp.goToPage(${i})">${i}</button>`;
            } else if (i === currentPage - 3 || i === currentPage + 3) {
                html += '<span class="page-dots">...</span>';
            }
        }

        // Next button
        if (currentPage < totalPages) {
            html += `<button class="btn-page" onclick="adminApp.goToPage(${currentPage + 1})">›</button>`;
        }

        html += '</div>';
        html += `<div class="pagination-info">Zeige ${data.users.length} von ${data.total} Benutzern</div>`;

        container.innerHTML = html;
    }

    /**
     * Go to specific page
     */
    goToPage(page) {
        this.currentPage = page;
        this.loadUsers();
    }

    /**
     * View user details
     */
    async viewUserDetails(userId) {
        this.showLoading(true);

        try {
            const user = await api.getAdminUserDetails(userId);

            const content = document.getElementById('userDetailsContent');
            if (content) {
                content.innerHTML = `
                    <div class="user-details">
                        <h3>${this.escapeHtml(user.username)}</h3>
                        <p class="user-email">${this.escapeHtml(user.email)}</p>

                        <div class="details-grid">
                            <div class="detail-item">
                                <label>Benutzer ID:</label>
                                <span>${user.id}</span>
                            </div>
                            <div class="detail-item">
                                <label>Rolle:</label>
                                <span class="badge ${user.is_admin ? 'badge-admin' : 'badge-user'}">
                                    ${user.is_admin ? 'Admin' : 'Benutzer'}
                                </span>
                            </div>
                            <div class="detail-item">
                                <label>Registriert:</label>
                                <span>${this.formatDate(user.created_at)}</span>
                            </div>
                            <div class="detail-item">
                                <label>Letzter Login:</label>
                                <span>${user.last_login ? this.formatDate(user.last_login) : 'Nie'}</span>
                            </div>
                        </div>

                        <h4>Portfolio Statistiken</h4>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <label>Positionen:</label>
                                <span>${user.portfolio?.positions || 0}</span>
                            </div>
                            <div class="stat-item">
                                <label>Gesamtwert:</label>
                                <span>€ ${this.formatNumber(user.portfolio?.total_value || 0)}</span>
                            </div>
                            <div class="stat-item">
                                <label>Investiert:</label>
                                <span>€ ${this.formatNumber(user.portfolio?.total_invested || 0)}</span>
                            </div>
                        </div>

                        <div class="activity-stats">
                            <div class="stat-row">
                                <label>Watchlist Items:</label>
                                <span>${user.watchlist_count || 0}</span>
                            </div>
                            <div class="stat-row">
                                <label>Aktive Alerts:</label>
                                <span>${user.alerts_count || 0}</span>
                            </div>
                            <div class="stat-row">
                                <label>Transaktionen:</label>
                                <span>${user.transactions_count || 0}</span>
                            </div>
                        </div>
                    </div>
                `;
            }

            this.showModal('userDetailsModal');
        } catch (error) {
            console.error('Error loading user details:', error);
            this.showNotification('Fehler beim Laden der Benutzerdetails', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Edit user
     */
    async editUser(userId) {
        this.showLoading(true);

        try {
            const user = await api.getAdminUserDetails(userId);
            this.userToEdit = user;

            // Fill form
            document.getElementById('editUserId').value = user.id;
            document.getElementById('editUsername').value = user.username;
            document.getElementById('editEmail').value = user.email;

            this.showModal('editUserModal');
        } catch (error) {
            console.error('Error loading user for edit:', error);
            this.showNotification('Fehler beim Laden des Benutzers', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Save user edit
     */
    async saveUserEdit() {
        const userId = document.getElementById('editUserId').value;
        const username = document.getElementById('editUsername').value;
        const email = document.getElementById('editEmail').value;

        if (!username || !email) {
            this.showNotification('Bitte alle Felder ausfüllen', 'error');
            return;
        }

        this.showLoading(true);

        try {
            await api.updateAdminUser(userId, { username, email });
            this.showNotification('Benutzer erfolgreich aktualisiert', 'success');
            this.closeModal('editUserModal');
            await this.loadUsers();
        } catch (error) {
            console.error('Error updating user:', error);
            this.showNotification(error.error || 'Fehler beim Aktualisieren des Benutzers', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Toggle admin status
     */
    async toggleAdminStatus(userId, isCurrentlyAdmin) {
        const action = isCurrentlyAdmin ? 'entfernen' : 'erteilen';

        if (!confirm(`Möchten Sie diesem Benutzer Admin-Rechte ${action}?`)) {
            return;
        }

        this.showLoading(true);

        try {
            await api.toggleAdminStatus(userId);
            this.showNotification(`Admin-Status erfolgreich geändert`, 'success');
            await this.loadUsers();
            await this.loadSystemStats();
        } catch (error) {
            console.error('Error toggling admin status:', error);
            this.showNotification(error.error || 'Fehler beim Ändern des Admin-Status', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Delete user
     */
    deleteUser(userId, username) {
        this.userToDelete = { id: userId, username: username };
        document.getElementById('deleteUserInfo').innerHTML =
            `<strong>Benutzer:</strong> ${this.escapeHtml(username)} (ID: ${userId})`;
        this.showModal('deleteConfirmModal');
    }

    /**
     * Confirm delete
     */
    async confirmDelete() {
        if (!this.userToDelete) return;

        this.showLoading(true);

        try {
            await api.deleteAdminUser(this.userToDelete.id);
            this.showNotification('Benutzer erfolgreich gelöscht', 'success');
            this.closeModal('deleteConfirmModal');
            this.userToDelete = null;
            await this.loadUsers();
            await this.loadSystemStats();
        } catch (error) {
            console.error('Error deleting user:', error);
            this.showNotification(error.error || 'Fehler beim Löschen des Benutzers', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Logout
     */
    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        window.location.href = '/';
    }

    /**
     * Show modal
     */
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';
        }
    }

    /**
     * Close modal
     */
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    }

    /**
     * Show loading spinner
     */
    showLoading(show) {
        const spinner = document.getElementById('loadingSpinner');
        if (spinner) {
            spinner.style.display = show ? 'flex' : 'none';
        }
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        if (!notification) return;

        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.display = 'block';

        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }

    /**
     * Format date
     */
    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('de-DE', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Format number
     */
    formatNumber(number) {
        return number.toLocaleString('de-DE', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    /**
     * Escape HTML
     */
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.adminApp = new AdminApp();
    window.adminApp.init();
});