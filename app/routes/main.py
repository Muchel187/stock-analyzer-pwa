from flask import Blueprint, render_template, send_from_directory, current_app, jsonify
import os

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Serve the main application"""
    return render_template('index.html')

@bp.route('/admin')
def admin():
    """Serve the admin dashboard"""
    return render_template('admin.html')

@bp.route('/health')
@bp.route('/api/health')
def health_check():
    """Health check endpoint for monitoring"""
    from app import db
    from sqlalchemy import text
    
    status = {
        'status': 'healthy',
        'database': 'disconnected',
        'version': '3.0.0'
    }
    
    # Check database connection
    try:
        db.session.execute(text('SELECT 1'))
        status['database'] = 'connected'
        return jsonify(status), 200
    except Exception as e:
        status['status'] = 'unhealthy'
        status['error'] = str(e)
        return jsonify(status), 503

@bp.route('/manifest.json')
def manifest():
    """Serve PWA manifest"""
    return send_from_directory(current_app.static_folder, 'manifest.json')

@bp.route('/sw.js')
def service_worker():
    """Serve service worker"""
    return send_from_directory(current_app.static_folder, 'sw.js')

@bp.route('/offline')
def offline():
    """Offline page"""
    return render_template('offline.html')