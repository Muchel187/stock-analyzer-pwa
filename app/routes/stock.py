from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import StockService, AIService
from app.services.news_service import NewsService
from datetime import datetime, timezone

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
            'timestamp': datetime.now(timezone.utc).isoformat()
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

@bp.route('/<ticker>/analyze-with-ai', methods=['GET'])
def analyze_with_ai_get(ticker):
    """Analyze stock with AI assistance (GET method) - Enhanced with analyst data, insider transactions, and news sentiment"""
    try:
        # Get stock data (now includes analyst_ratings, price_target, insider_transactions)
        stock_info = StockService.get_stock_info(ticker)
        if not stock_info:
            return jsonify({
                'error': f'Stock {ticker} not found',
                'message': 'Unable to fetch stock data. Please check ticker symbol and try again.'
            }), 404

        # Get additional analysis data (these might be None, handle gracefully)
        technical = StockService.calculate_technical_indicators(ticker)
        fundamental = StockService.get_fundamental_analysis(ticker)

        # Get aggregated news sentiment
        from app.services.news_service import NewsService
        news_sentiment = None
        try:
            news_sentiment = NewsService.get_aggregated_sentiment(ticker, days=7)
        except Exception as e:
            import logging
            logging.error(f"Failed to get news sentiment for {ticker}: {str(e)}")

        # Analyze short squeeze potential
        from app.services.short_squeeze_analyzer import ShortSqueezeAnalyzer
        squeeze_analysis = None
        try:
            squeeze_analysis = ShortSqueezeAnalyzer.analyze_squeeze_potential(
                stock_info,
                technical if technical else {},
                {'volume': stock_info.get('volume', 0)}
            )
        except Exception as e:
            import logging
            logging.error(f"Failed to analyze squeeze potential for {ticker}: {str(e)}")

        # Try to get actual short data from ChartExchange
        from app.services.short_data_service import ShortDataService
        short_data = None
        try:
            short_data = ShortDataService.get_short_data(ticker)
            # If we have real short data, enhance the squeeze analysis
            if short_data and squeeze_analysis:
                squeeze_analysis['real_short_data'] = short_data
                squeeze_analysis['note'] = 'Enhanced with actual short interest data from ChartExchange.com'
        except Exception as e:
            import logging
            logging.error(f"Failed to get short data for {ticker}: {str(e)}")

        # Generate AI analysis with enhanced data
        ai_service = AIService()
        ai_analysis = ai_service.analyze_stock_with_ai(
            stock_info,
            technical if technical else {},
            fundamental if fundamental else {},
            short_data,
            news_sentiment  # NEW: Pass news sentiment
        )

        if not ai_analysis or 'error' in ai_analysis:
            error_msg = ai_analysis.get('error', 'AI analysis failed') if ai_analysis else 'AI analysis failed'
            return jsonify({
                'error': error_msg,
                'ticker': ticker,
                'message': 'AI analysis could not be completed. Some data may be unavailable.'
            }), 500

        # Add squeeze analysis and news sentiment to response
        if squeeze_analysis:
            ai_analysis['squeeze_analysis'] = squeeze_analysis
        if news_sentiment:
            ai_analysis['news_sentiment'] = news_sentiment
        ai_analysis['timestamp'] = datetime.now(timezone.utc).isoformat()

        return jsonify(ai_analysis), 200

    except Exception as e:
        import logging
        import traceback
        logging.error(f"AI analysis failed for {ticker}: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': f'AI analysis failed: {str(e)}',
            'ticker': ticker
        }), 500

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

        # Analyze short squeeze potential
        from app.services.short_squeeze_analyzer import ShortSqueezeAnalyzer
        squeeze_analysis = ShortSqueezeAnalyzer.analyze_squeeze_potential(
            stock_info,
            technical,
            {'volume': stock_info.get('volume')}
        )

        # Try to get actual short data from ChartExchange
        from app.services.short_data_service import ShortDataService
        short_data = ShortDataService.get_short_data(ticker)

        # If we have real short data, enhance the squeeze analysis
        if short_data:
            squeeze_analysis['real_short_data'] = short_data
            squeeze_analysis['note'] = 'Enhanced with actual short interest data from ChartExchange.com'

        # Generate AI analysis
        ai_service = AIService()
        ai_analysis = ai_service.analyze_stock_with_ai(
            stock_info,
            technical,
            fundamental,
            short_data
        )

        if not ai_analysis:
            return jsonify({'error': 'AI analysis failed'}), 500

        # Add squeeze analysis to response
        ai_analysis['squeeze_analysis'] = squeeze_analysis
        ai_analysis['timestamp'] = datetime.now(timezone.utc).isoformat()

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
            'timestamp': datetime.now(timezone.utc).isoformat()
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
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get recommendations: {str(e)}'}), 500

@bp.route('/ai-recommendations', methods=['POST'])
@jwt_required()
def get_ai_recommendations():
    """Get AI-powered top buy/sell recommendations - FAST VERSION without AI analysis"""
    try:
        # OPTIMIZATION: Skip AI analysis for speed, use technical + fundamental scores only
        # Top US stocks to analyze (S&P 500 leaders + trending)
        us_stocks = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
            'JPM', 'V', 'MA', 'HD', 'DIS', 'NFLX'
        ]

        # Top German stocks (DAX) - reduced list
        german_stocks = [
            'SAP', 'SIE.DE', 'ALV.DE', 'BMW.DE', 'DAI.DE'
        ]

        all_stocks = us_stocks + german_stocks

        # Analyze stocks WITHOUT AI for speed (use technical + fundamental only)
        recommendations = []

        for ticker in all_stocks[:15]:  # Reduced to 15 for faster loading
            try:
                # Get stock info
                stock_info = StockService.get_stock_info(ticker)
                if not stock_info:
                    continue

                # Get fundamental analysis
                fundamental = StockService.get_fundamental_analysis(ticker)
                if not fundamental:
                    continue

                # Get technical indicators
                technical = StockService.calculate_technical_indicators(ticker)

                # FAST: Calculate recommendation based on technical + fundamental scores
                # No AI call = much faster!
                overall_score = fundamental.get('overall_score', 50)
                
                # Determine recommendation based on scores (adjusted thresholds)
                rec_type = 'HOLD'
                confidence = 70
                
                if overall_score >= 60:  # Lowered from 65
                    rec_type = 'BUY'
                    confidence = min(95, 65 + (overall_score - 60) * 2)
                elif overall_score <= 40:  # Lowered from 35
                    rec_type = 'SELL'
                    confidence = min(95, 65 + (40 - overall_score) * 2)
                else:
                    confidence = 55
                
                # Check RSI for additional signal
                if technical and technical.get('rsi'):
                    rsi = technical['rsi']
                    if rsi > 70 and rec_type != 'BUY':
                        rec_type = 'SELL'
                        confidence = min(95, confidence + 15)
                    elif rsi < 30 and rec_type != 'SELL':
                        rec_type = 'BUY'
                        confidence = min(95, confidence + 15)
                    elif rsi > 60 and overall_score < 50:
                        # Overbought but weak fundamentals
                        rec_type = 'SELL'
                    elif rsi < 40 and overall_score > 50:
                        # Oversold but strong fundamentals
                        rec_type = 'BUY'

                # Create summary based on scores
                summary = f"Score: {overall_score:.0f}/100. "
                if rec_type == 'BUY':
                    summary += "Strong fundamentals and technical indicators suggest buying opportunity."
                elif rec_type == 'SELL':
                    summary += "Weak fundamentals or overbought conditions suggest caution."
                else:
                    summary += "Mixed signals. Hold current positions."

                recommendations.append({
                    'ticker': ticker,
                    'company_name': stock_info.get('company_name', ticker),
                    'current_price': stock_info.get('current_price'),
                    'recommendation': rec_type,
                    'confidence': int(confidence),
                    'overall_score': overall_score,
                    'market': 'US' if ticker in us_stocks else 'DE',
                    'summary': summary
                })

            except Exception as e:
                print(f"Error analyzing {ticker}: {str(e)}")
                continue

        # Sort by confidence score
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)

        # Get top 10 buys and top 10 sells
        buy_recs = [r for r in recommendations if r['recommendation'] == 'BUY'][:10]
        sell_recs = [r for r in recommendations if r['recommendation'] == 'SELL'][:10]

        return jsonify({
            'top_buys': buy_recs,
            'top_sells': sell_recs,
            'analyzed_count': len(recommendations),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to generate AI recommendations: {str(e)}'}), 500

@bp.route('/compare', methods=['POST'])
def compare_stocks():
    """Compare multiple stocks (2-4 tickers)"""
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])

        if not tickers:
            return jsonify({'error': 'Tickers list is required'}), 400

        if len(tickers) < 2:
            return jsonify({'error': 'At least 2 tickers required for comparison'}), 400

        if len(tickers) > 4:
            return jsonify({'error': 'Maximum 4 tickers allowed for comparison'}), 400

        period = data.get('period', '1y')
        valid_periods = ['1mo', '3mo', '6mo', '1y', '2y', '5y', 'max']
        
        if period not in valid_periods:
            period = '1y'

        # Get data for all tickers
        comparison_data = []
        price_histories = []

        for ticker in tickers:
            try:
                # Get basic stock info
                stock_info = StockService.get_stock_info(ticker)
                if not stock_info:
                    continue

                # Get fundamental analysis
                fundamental = StockService.get_fundamental_analysis(ticker)

                # Get technical indicators
                technical = StockService.calculate_technical_indicators(ticker)

                # Get price history
                history = StockService.get_price_history(ticker, period)

                comparison_data.append({
                    'ticker': ticker.upper(),
                    'company_name': stock_info.get('company_name', ticker),
                    'current_price': stock_info.get('current_price'),
                    'market_cap': stock_info.get('market_cap'),
                    'pe_ratio': stock_info.get('pe_ratio'),
                    'dividend_yield': stock_info.get('dividend_yield'),
                    'sector': stock_info.get('sector'),
                    'industry': stock_info.get('industry'),
                    'overall_score': fundamental.get('overall_score') if fundamental else None,
                    'rsi': technical.get('rsi') if technical else None,
                    'volatility': technical.get('volatility') if technical else None,
                    'price_change_1m': technical.get('price_change_1m') if technical else None,
                    'volume': stock_info.get('volume')
                })

                if history and history.get('data'):
                    # Normalize price history for comparison (percentage change from start)
                    hist_data = history['data']
                    if len(hist_data) > 0:
                        start_price = float(hist_data[0]['close'])
                        normalized_data = []
                        
                        for point in hist_data:
                            normalized_data.append({
                                'date': point['date'],
                                'close': float(point['close']),
                                'normalized': ((float(point['close']) - start_price) / start_price * 100),
                                'volume': int(point.get('volume', 0))
                            })

                        price_histories.append({
                            'ticker': ticker.upper(),
                            'data': normalized_data
                        })

            except Exception as e:
                logger.error(f"Error comparing {ticker}: {str(e)}")
                continue

        if len(comparison_data) < 2:
            return jsonify({'error': 'Could not fetch data for at least 2 tickers'}), 404

        return jsonify({
            'comparison': comparison_data,
            'price_histories': price_histories,
            'period': period,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to compare stocks: {str(e)}'}), 500

@bp.route('/<ticker>/news', methods=['GET'])
def get_stock_news(ticker):
    """
    Get latest news for a stock with sentiment analysis
    
    Query Parameters:
    - limit: Number of articles (default: 10, max: 50)
    - days: Days to look back (default: 7, max: 30)
    
    Returns:
    - news: List of articles with headline, summary, source, url, sentiment
    - sentiment_score: Overall sentiment (-1 to 1)
    - news_count: Total articles found
    - categories: News categories breakdown
    """
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
        days = min(int(request.args.get('days', 7)), 30)
        
        news_data = NewsService.get_company_news(ticker, days=days, limit=limit)
        
        if not news_data:
            return jsonify({'error': f'No news found for {ticker}'}), 404
        
        return jsonify(news_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get news: {str(e)}'}), 500

@bp.route('/news/market', methods=['GET'])
def get_market_news():
    """
    Get general market news
    
    Query Parameters:
    - limit: Number of articles (default: 20, max: 50)
    
    Returns:
    - news: List of general market news articles
    """
    try:
        limit = min(int(request.args.get('limit', 20)), 50)
        
        news_data = NewsService.get_market_news(limit=limit)
        
        if not news_data:
            return jsonify({'error': 'No market news available'}), 404
        
        return jsonify(news_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get market news: {str(e)}'}), 500