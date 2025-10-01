from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import AlertService

bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_alerts():
    """Get user's alerts"""
    try:
        user_id = get_jwt_identity()
        active_only = request.args.get('active_only', 'false').lower() == 'true'

        alerts = AlertService.get_user_alerts(user_id, active_only)

        return jsonify({
            'alerts': alerts
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get alerts: {str(e)}'}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def create_alert():
    """Create a new alert"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Validate required fields
        required = ['ticker', 'alert_type', 'target_value']
        for field in required:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Validate alert type
        valid_types = ['PRICE_ABOVE', 'PRICE_BELOW', 'PERCENT_CHANGE']
        if data['alert_type'] not in valid_types:
            return jsonify({'error': f'alert_type must be one of: {valid_types}'}), 400

        # Create alert
        alert = AlertService.create_alert(user_id, data)

        if not alert:
            return jsonify({'error': 'Failed to create alert'}), 400

        return jsonify({
            'message': 'Alert created successfully',
            'alert': alert.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'error': f'Failed to create alert: {str(e)}'}), 500

@bp.route('/<int:alert_id>', methods=['PUT'])
@jwt_required()
def update_alert(alert_id):
    """Update an alert"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        alert = AlertService.update_alert(alert_id, user_id, data)

        if not alert:
            return jsonify({'error': 'Alert not found or unauthorized'}), 404

        return jsonify({
            'message': 'Alert updated successfully',
            'alert': alert.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to update alert: {str(e)}'}), 500

@bp.route('/<int:alert_id>', methods=['DELETE'])
@jwt_required()
def delete_alert(alert_id):
    """Delete an alert"""
    try:
        user_id = get_jwt_identity()

        success = AlertService.delete_alert(alert_id, user_id)

        if not success:
            return jsonify({'error': 'Alert not found or unauthorized'}), 404

        return jsonify({
            'message': 'Alert deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to delete alert: {str(e)}'}), 500

@bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_alert_statistics():
    """Get alert statistics"""
    try:
        user_id = get_jwt_identity()
        stats = AlertService.get_alert_statistics(user_id)

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get statistics: {str(e)}'}), 500

@bp.route('/check', methods=['POST'])
@jwt_required()
def check_alerts_manually():
    """Manually trigger alert checking (admin/testing)"""
    try:
        # In production, this would be admin-only
        triggered = AlertService.check_alerts()

        return jsonify({
            'message': 'Alert check completed',
            'triggered_count': len(triggered)
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to check alerts: {str(e)}'}), 500