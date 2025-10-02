import pytest
from unittest.mock import patch, MagicMock
from app.services import StockService

@patch('app.services.alternative_data_sources.FallbackDataService.get_stock_quote')
@patch('app.services.stock_service.StockCache')
def test_get_stock_info(mock_cache, mock_quote, app):
    """Test getting stock information"""
    with app.app_context():
        # Mock cache miss
        mock_cache.get_cached.return_value = None

        # Mock FallbackDataService response
        mock_quote.return_value = {
            'ticker': 'AAPL',
            'company_name': 'Apple Inc.',
            'sector': 'Technology',
            'current_price': 150.00,
            'previous_close': 148.00,
            'market_cap': 2500000000000,
            'pe_ratio': 25.5,
            'dividend_yield': 0.005,
            'fifty_two_week_low': 120.00,
            'fifty_two_week_high': 180.00,
            'source': 'finnhub'
        }

        result = StockService.get_stock_info('AAPL')

        assert result is not None
        assert result['ticker'] == 'AAPL'
        assert result['company_name'] == 'Apple Inc.'
        assert result['current_price'] == 150.00
        assert result['pe_ratio'] == 25.5

@patch('app.services.alternative_data_sources.FallbackDataService.get_historical_data')
@patch('app.services.stock_service.StockCache')
def test_calculate_technical_indicators(mock_cache, mock_history, app):
    """Test technical indicators calculation"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    with app.app_context():
        # Mock cache miss
        mock_cache.get_cached.return_value = None

        # Create mock historical data in the expected format (dict, not DataFrame)
        dates = pd.date_range(end=datetime.now(), periods=100)
        history_data = []
        for i, date in enumerate(dates):
            history_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': float(np.random.uniform(145, 155)),
                'high': float(np.random.uniform(150, 160)),
                'low': float(np.random.uniform(140, 150)),
                'close': float(np.random.uniform(145, 155)),
                'volume': int(np.random.uniform(1000000, 5000000))
            })

        mock_history.return_value = {
            'ticker': 'AAPL',
            'data': history_data,
            'period': '6mo'
        }

        result = StockService.calculate_technical_indicators('AAPL')

        assert result is not None
        assert 'rsi' in result
        assert 'macd' in result
        assert 'bollinger_bands' in result
        assert 0 <= result['rsi'] <= 100

def test_fundamental_analysis_scoring():
    """Test fundamental analysis scoring"""
    # Test value score calculation
    value_score = StockService._calculate_value_score(
        pe_ratio=12.0,
        peg_ratio=0.8,
        price_to_book=0.9
    )
    assert 70 <= value_score <= 100  # Should be high for good values

    # Test financial health score
    health_score = StockService._calculate_financial_health_score(
        debt_to_equity=0.3,
        current_ratio=2.5
    )
    assert 80 <= health_score <= 100  # Should be high for good health

    # Test profitability score
    profit_score = StockService._calculate_profitability_score(
        profit_margin=0.25,
        roe=0.20
    )
    assert 80 <= profit_score <= 100  # Should be high for good profitability

def test_get_recommendation():
    """Test investment recommendation based on score"""
    assert StockService._get_recommendation(80) == "Strong Buy"
    assert StockService._get_recommendation(65) == "Buy"
    assert StockService._get_recommendation(45) == "Hold"
    assert StockService._get_recommendation(30) == "Sell"
    assert StockService._get_recommendation(20) == "Strong Sell"

@patch('app.services.alternative_data_sources.FallbackDataService.get_historical_data')
@patch('app.services.stock_service.StockCache')
def test_get_price_history(mock_cache, mock_history, app):
    """Test getting price history"""
    import pandas as pd
    from datetime import datetime, timedelta

    with app.app_context():
        # Mock cache miss
        mock_cache.get_cached.return_value = None

        # Create mock historical data in the expected format (dict, not DataFrame)
        dates = pd.date_range(end=datetime.now(), periods=30)
        history_data = []
        for date in dates:
            history_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': 145.0,
                'high': 150.0,
                'low': 144.0,
                'close': 149.0,
                'volume': 1000000
            })

        mock_history.return_value = {
            'ticker': 'AAPL',
            'data': history_data,
            'period': '1mo'
        }

        result = StockService.get_price_history('AAPL', '1mo')

        assert result is not None
        assert result['ticker'] == 'AAPL'
        assert result['period'] == '1mo'
        assert len(result['data']) == 30
        assert result['data'][0]['close'] == 149.0

@patch('app.services.stock_service.StockCache')
def test_caching(mock_cache, app):
    """Test that caching is used"""
    with app.app_context():
        # Mock cache hit
        mock_cache.get_cached.return_value = {
            'ticker': 'AAPL',
            'current_price': 150.00
        }

        with patch('app.services.alternative_data_sources.FallbackDataService.get_stock_quote') as mock_quote:
            result = StockService.get_stock_info('AAPL')

            # FallbackDataService should not be called if cache hit
            mock_quote.assert_not_called()
            assert result['current_price'] == 150.00