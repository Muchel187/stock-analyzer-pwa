/**
 * Admin Initialization - Separates admin logic from main app
 * This ensures admin page doesn't redirect to dashboard
 */

// Only initialize admin app if we're on the admin page
if (window.location.pathname === '/admin') {
    document.addEventListener('DOMContentLoaded', () => {
        // Don't initialize the main app on admin page
        if (typeof AdminApp !== 'undefined') {
            window.adminApp = new AdminApp();
            window.adminApp.init();
        }
    });
}