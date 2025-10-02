from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import PortfolioService
from datetime import datetime

bp = Blueprint('portfolio', __name__, url_prefix='/api/portfolio')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_portfolio():
    """Get user's portfolio"""
    try:
        user_id = get_jwt_identity()
        
        # Validate user_id
        if not user_id:
            return jsonify({'error': 'Invalid user ID'}), 401
        
        # Convert user_id to int if it's a string (JWT stores as string)
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID format'}), 401
        
        portfolio = PortfolioService.get_portfolio(user_id)

        # Ensure proper structure even if error occurred
        if not isinstance(portfolio, dict):
            return jsonify({
                'items': [],
                'summary': {
                    'total_value': 0,
                    'total_invested': 0,
                    'total_gain_loss': 0,
                    'total_gain_loss_percent': 0,
                    'positions': 0
                },
                'error': 'Invalid portfolio data'
            }), 500

        return jsonify(portfolio), 200

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[Portfolio API] Error: {error_details}")
        
        return jsonify({
            'error': f'Failed to get portfolio: {str(e)}',
            'items': [],
            'summary': {
                'total_value': 0,
                'total_invested': 0,
                'total_gain_loss': 0,
                'total_gain_loss_percent': 0,
                'positions': 0
            }
        }), 500

@bp.route('/transaction', methods=['POST'])
@jwt_required()
def add_transaction():
    """Add a new transaction"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Validate required fields
        required = ['ticker', 'transaction_type', 'shares', 'price']
        for field in required:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Validate transaction type
        if data['transaction_type'] not in ['BUY', 'SELL']:
            return jsonify({'error': 'transaction_type must be BUY or SELL'}), 400

        # Add transaction
        transaction = PortfolioService.add_transaction(user_id, data)

        if not transaction:
            return jsonify({'error': 'Failed to add transaction. Check if you have sufficient shares for SELL orders.'}), 400

        return jsonify({
            'message': 'Transaction added successfully',
            'transaction': transaction.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'error': f'Failed to add transaction: {str(e)}'}), 500

@bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """Get user's transactions"""
    try:
        user_id = get_jwt_identity()
        ticker = request.args.get('ticker')
        limit = int(request.args.get('limit', 50))

        transactions = PortfolioService.get_transactions(user_id, ticker, limit)

        return jsonify({
            'transactions': transactions
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get transactions: {str(e)}'}), 500

@bp.route('/performance', methods=['GET'])
@jwt_required()
def get_performance():
    """Get portfolio performance over time"""
    try:
        user_id = get_jwt_identity()
        period = request.args.get('period', '1M')

        performance = PortfolioService.get_portfolio_performance(user_id, period)

        return jsonify(performance), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get performance: {str(e)}'}), 500