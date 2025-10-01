from flask import Blueprint, render_template, send_from_directory, current_app
import os

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Serve the main application"""
    return render_template('index.html')

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