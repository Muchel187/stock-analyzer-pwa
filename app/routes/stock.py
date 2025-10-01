from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import StockService, AIService
from datetime import datetime

bp = Blueprint('stock', __name__, url_prefix='/api/stock')

@bp.route('/<ticker>', methods=['GET'])
def get_stock_info(ticker):
    """Get comprehensive stock information"""
    try:
        # Get stock info
        stock_info = StockService.get_stock_info(ticker)

        if not stock_info:
            return jsonify({'error': f'Stock {ticker} not found'}), 404

        # Get technical indicators
        technical = StockService.calculate_technical_indicators(ticker)

        # Get fundamental analysis
        fundamental = StockService.get_fundamental_analysis(ticker)

        return jsonify({
            'ticker': ticker.upper(),
            'info': stock_info,
            'technical_indicators': technical,
            'fundamental_analysis': fundamental,
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get stock info: {str(e)}'}), 500

@bp.route('/<ticker>/history', methods=['GET'])
def get_price_history(ticker):
    """Get historical price data"""
    try:
        period = request.args.get('period', '1y')
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max']

        if period not in valid_periods:
            return jsonify({'error': f'Invalid period. Must be one of: {valid_periods}'}), 400

        history = StockService.get_price_history(ticker, period)

        if not history:
            return jsonify({'error': f'Unable to get history for {ticker}'}), 404

        return jsonify(history), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get price history: {str(e)}'}), 500

@bp.route('/analyze-with-ai', methods=['POST'])
def analyze_with_ai():
    """Analyze stock with AI assistance"""
    try:
        data = request.get_json()
        ticker = data.get('ticker')

        if not ticker:
            return jsonify({'error': 'Ticker is required'}), 400

        # Get stock data
        stock_info = StockService.get_stock_info(ticker)
        if not stock_info:
            return jsonify({'error': f'Stock {ticker} not found'}), 404

        # Get additional analysis data
        technical = StockService.calculate_technical_indicators(ticker)
        fundamental = StockService.get_fundamental_analysis(ticker)

        # Generate AI analysis
        ai_service = AIService()
        ai_analysis = ai_service.analyze_stock_with_ai(
            stock_info,
            technical,
            fundamental
        )

        if not ai_analysis:
            return jsonify({'error': 'AI analysis failed'}), 500

        ai_analysis['timestamp'] = datetime.utcnow().isoformat()

        return jsonify(ai_analysis), 200

    except Exception as e:
        return jsonify({'error': f'AI analysis failed: {str(e)}'}), 500

@bp.route('/batch', methods=['POST'])
def get_batch_quotes():
    """Get quotes for multiple stocks"""
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])

        if not tickers:
            return jsonify({'error': 'Tickers list is required'}), 400

        if len(tickers) > 20:
            return jsonify({'error': 'Maximum 20 tickers allowed per request'}), 400

        results = {}
        for ticker in tickers:
            stock_info = StockService.get_stock_info(ticker)
            if stock_info:
                results[ticker] = {
                    'ticker': ticker.upper(),
                    'company_name': stock_info.get('company_name'),
                    'current_price': stock_info.get('current_price'),
                    'change': stock_info.get('current_price', 0) - stock_info.get('previous_close', 0),
                    'change_percent': ((stock_info.get('current_price', 0) - stock_info.get('previous_close', 0)) /
                                      stock_info.get('previous_close', 1) * 100) if stock_info.get('previous_close') else 0,
                    'volume': stock_info.get('volume'),
                    'market_cap': stock_info.get('market_cap')
                }

        return jsonify({
            'quotes': results,
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get batch quotes: {str(e)}'}), 500

@bp.route('/search', methods=['GET'])
def search_stocks():
    """Search for stocks by name or ticker"""
    try:
        query = request.args.get('q', '').strip()

        if not query or len(query) < 2:
            return jsonify({'error': 'Search query must be at least 2 characters'}), 400

        # This is a simplified search - in production, you'd have a proper search index
        # For now, we'll check against known tickers
        from app.services.screener_service import ScreenerService

        all_tickers = ScreenerService.US_STOCKS + ScreenerService.DAX_STOCKS
        matches = []

        for ticker in all_tickers:
            if query.upper() in ticker.upper():
                stock_info = StockService.get_stock_info(ticker)
                if stock_info:
                    matches.append({
                        'ticker': ticker,
                        'company_name': stock_info.get('company_name'),
                        'exchange': stock_info.get('exchange'),
                        'sector': stock_info.get('sector')
                    })

                if len(matches) >= 10:  # Limit results
                    break

        return jsonify({
            'results': matches,
            'query': query
        }), 200

    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get stock recommendations"""
    try:
        # Get top performing stocks based on our analysis
        from app.services.screener_service import ScreenerService

        # Get different types of recommendations
        value_stocks = ScreenerService.screen_stocks({
            'max_pe_ratio': 15,
            'min_market_cap': 1000000000,
            'prefer_value': True,
            'limit': 5,
            'sort_by': 'score'
        })

        growth_stocks = ScreenerService.screen_stocks({
            'min_revenue_growth': 0.15,
            'prefer_growth': True,
            'min_market_cap': 1000000000,
            'limit': 5,
            'sort_by': 'score'
        })

        dividend_stocks = ScreenerService.screen_stocks({
            'min_dividend_yield': 0.03,
            'prefer_dividends': True,
            'limit': 5,
            'sort_by': 'dividend_yield'
        })

        return jsonify({
            'recommendations': {
                'value_picks': value_stocks[:3],
                'growth_picks': growth_stocks[:3],
                'dividend_picks': dividend_stocks[:3]
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get recommendations: {str(e)}'}), 500