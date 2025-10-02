"""
Admin Routes - API endpoints for admin operations
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.admin_required import admin_required
from app.services.admin_service import AdminService
from app.models import User
from app import db
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@bp.route('/check', methods=['GET'])
@jwt_required()
def check_admin():
    """Check if current user is admin"""
    try:
        current_user = get_jwt_identity()
        user = db.session.get(User, int(current_user))

        if not user or not user.is_admin:
            return jsonify({'error': 'Not authorized'}), 403

        return jsonify({
            'is_admin': True,
            'username': user.username,
            'user_id': user.id
        }), 200

    except Exception as e:
        logger.error(f"Error checking admin status: {str(e)}")
        return jsonify({'error': 'Failed to check admin status'}), 500

@bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get paginated list of all users"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        search = request.args.get('search', None)
        is_admin = request.args.get('is_admin', None, type=lambda x: x.lower() == 'true')

        # Get users from service
        result = AdminService.get_users(
            page=page,
            per_page=per_page,
            search=search,
            is_admin=is_admin
        )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return jsonify({'error': 'Failed to get users'}), 500

@bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_details(user_id):
    """Get detailed user information"""
    try:
        user_data = AdminService.get_user_details(user_id)

        if not user_data:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(user_data), 200

    except Exception as e:
        logger.error(f"Error getting user details: {str(e)}")
        return jsonify({'error': 'Failed to get user details'}), 500

@bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user information"""
    try:
        data = request.get_json()

        # Validate input
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update user
        user_data = AdminService.update_user(user_id, data)

        if not user_data:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'user': user_data
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        return jsonify({'error': 'Failed to update user'}), 500

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user account"""
    try:
        admin_id = int(get_jwt_identity())

        # Delete user
        success = AdminService.delete_user(user_id, admin_id)

        if not success:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'success': True,
            'message': 'User deleted successfully',
            'deleted_user_id': user_id
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        return jsonify({'error': 'Failed to delete user'}), 500

@bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin_status(user_id):
    """Toggle user's admin status"""
    try:
        admin_id = int(get_jwt_identity())

        # Toggle admin status
        result = AdminService.toggle_admin_status(user_id, admin_id)

        if not result:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error toggling admin status: {str(e)}")
        return jsonify({'error': 'Failed to toggle admin status'}), 500

@bp.route('/stats', methods=['GET'])
@admin_required
def get_system_stats():
    """Get system statistics"""
    try:
        stats = AdminService.get_system_stats()
        return jsonify(stats), 200

    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        return jsonify({'error': 'Failed to get system statistics'}), 500

