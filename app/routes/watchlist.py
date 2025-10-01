from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Watchlist
from app.services import StockService
from datetime import datetime

bp = Blueprint('watchlist', __name__, url_prefix='/api/watchlist')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_watchlist():
    """Get user's watchlist"""
    try:
        user_id = get_jwt_identity()
        watchlist_items = Watchlist.query.filter_by(user_id=user_id).all()

        # Update current prices
        for item in watchlist_items:
            stock_info = StockService.get_stock_info(item.ticker)
            if stock_info and stock_info.get('current_price'):
                item.update_price(stock_info['current_price'])
                db.session.commit()

        return jsonify({
            'items': [item.to_dict() for item in watchlist_items]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get watchlist: {str(e)}'}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def add_to_watchlist():
    """Add stock to watchlist"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data.get('ticker'):
            return jsonify({'error': 'Ticker is required'}), 400

        ticker = data['ticker'].upper()

        # Check if already in watchlist
        existing = Watchlist.query.filter_by(user_id=user_id, ticker=ticker).first()
        if existing:
            return jsonify({'error': 'Stock already in watchlist'}), 400

        # Get stock info
        stock_info = StockService.get_stock_info(ticker)
        if not stock_info:
            return jsonify({'error': f'Stock {ticker} not found'}), 404

        # Create watchlist item
        watchlist_item = Watchlist(
            user_id=user_id,
            ticker=ticker,
            company_name=stock_info.get('company_name'),
            sector=stock_info.get('sector'),
            market=stock_info.get('market'),
            added_price=stock_info.get('current_price'),
            current_price=stock_info.get('current_price'),
            market_cap=stock_info.get('market_cap'),
            pe_ratio=stock_info.get('pe_ratio'),
            dividend_yield=stock_info.get('dividend_yield'),
            notes=data.get('notes', ''),
            tags=data.get('tags', [])
        )

        db.session.add(watchlist_item)
        db.session.commit()

        return jsonify({
            'message': 'Stock added to watchlist',
            'item': watchlist_item.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add to watchlist: {str(e)}'}), 500

@bp.route('/<ticker>', methods=['DELETE'])
@jwt_required()
def remove_from_watchlist(ticker):
    """Remove stock from watchlist"""
    try:
        user_id = get_jwt_identity()
        watchlist_item = Watchlist.query.filter_by(
            user_id=user_id,
            ticker=ticker.upper()
        ).first()

        if not watchlist_item:
            return jsonify({'error': 'Stock not in watchlist'}), 404

        db.session.delete(watchlist_item)
        db.session.commit()

        return jsonify({
            'message': 'Stock removed from watchlist'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to remove from watchlist: {str(e)}'}), 500

@bp.route('/<ticker>', methods=['PUT'])
@jwt_required()
def update_watchlist_item(ticker):
    """Update watchlist item (notes, tags)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        watchlist_item = Watchlist.query.filter_by(
            user_id=user_id,
            ticker=ticker.upper()
        ).first()

        if not watchlist_item:
            return jsonify({'error': 'Stock not in watchlist'}), 404

        # Update fields
        if 'notes' in data:
            watchlist_item.notes = data['notes']
        if 'tags' in data:
            watchlist_item.tags = data['tags']

        db.session.commit()

        return jsonify({
            'message': 'Watchlist item updated',
            'item': watchlist_item.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update watchlist item: {str(e)}'}), 500