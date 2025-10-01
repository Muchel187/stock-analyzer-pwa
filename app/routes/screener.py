from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import ScreenerService

bp = Blueprint('screener', __name__, url_prefix='/api/screener')

@bp.route('/', methods=['POST'])
def screen_stocks():
    """Screen stocks based on criteria"""
    try:
        data = request.get_json()

        # Build criteria from request
        criteria = {
            'market': data.get('market', 'USA'),
            'min_market_cap': data.get('min_market_cap'),
            'max_market_cap': data.get('max_market_cap'),
            'min_pe_ratio': data.get('min_pe_ratio'),
            'max_pe_ratio': data.get('max_pe_ratio'),
            'min_dividend_yield': data.get('min_dividend_yield'),
            'max_dividend_yield': data.get('max_dividend_yield'),
            'min_price': data.get('min_price'),
            'max_price': data.get('max_price'),
            'min_volume': data.get('min_volume'),
            'min_beta': data.get('min_beta'),
            'max_beta': data.get('max_beta'),
            'sectors': data.get('sectors', []),
            'only_profitable': data.get('only_profitable', False),
            'min_revenue_growth': data.get('min_revenue_growth'),
            'prefer_value': data.get('prefer_value', False),
            'prefer_growth': data.get('prefer_growth', False),
            'prefer_dividends': data.get('prefer_dividends', False),
            'prefer_momentum': data.get('prefer_momentum', False),
            'sort_by': data.get('sort_by', 'market_cap'),
            'sort_order': data.get('sort_order', 'desc'),
            'limit': min(data.get('limit', 50), 100)
        }

        # Remove None values
        criteria = {k: v for k, v in criteria.items() if v is not None}

        # Screen stocks
        results = ScreenerService.screen_stocks(criteria)

        return jsonify({
            'results': results,
            'count': len(results),
            'criteria': criteria
        }), 200

    except Exception as e:
        return jsonify({'error': f'Screening failed: {str(e)}'}), 500

@bp.route('/presets', methods=['GET'])
def get_preset_screens():
    """Get predefined screening strategies"""
    try:
        presets = ScreenerService.get_predefined_screens()

        return jsonify({
            'presets': presets
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get presets: {str(e)}'}), 500

@bp.route('/presets/<preset_name>', methods=['POST'])
def apply_preset_screen(preset_name):
    """Apply a predefined screening strategy"""
    try:
        presets = ScreenerService.get_predefined_screens()
        preset = next((p for p in presets if p['name'].lower().replace(' ', '_') == preset_name.lower()), None)

        if not preset:
            return jsonify({'error': 'Preset not found'}), 404

        # Apply preset criteria
        results = ScreenerService.screen_stocks(preset['criteria'])

        return jsonify({
            'preset': preset['name'],
            'description': preset['description'],
            'results': results,
            'count': len(results)
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to apply preset: {str(e)}'}), 500

@bp.route('/sectors', methods=['GET'])
def get_sectors():
    """Get list of available sectors"""
    try:
        # Common sectors
        sectors = [
            'Technology',
            'Healthcare',
            'Financial Services',
            'Consumer Cyclical',
            'Consumer Defensive',
            'Energy',
            'Industrials',
            'Basic Materials',
            'Real Estate',
            'Communication Services',
            'Utilities'
        ]

        return jsonify({
            'sectors': sectors
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get sectors: {str(e)}'}), 500