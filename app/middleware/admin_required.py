from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app import db
from app.models import User

def admin_required(f):
    """
    Decorator to check if the current user is an admin.
    Use this on routes that should only be accessible by admins.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verify JWT token exists
        try:
            verify_jwt_in_request()
        except Exception as e:
            return jsonify({'error': 'Invalid or missing token'}), 401

        # Get current user
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Authentication required'}), 401

        # Check if user exists and is admin
        user = db.session.get(User, int(current_user_id))
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403

        # User is admin, proceed with the request
        return f(*args, **kwargs)

    return decorated_function

def get_admin_user():
    """
    Helper function to get the current admin user object.
    Returns None if user is not authenticated or not an admin.
    """
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = db.session.get(User, int(current_user_id))

        if user and user.is_admin:
            return user
        return None
    except:
        return None