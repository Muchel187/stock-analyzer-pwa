import pytest
from unittest.mock import patch, MagicMock
from app.services import StockService

@patch('app.services.stock_service.yf.Ticker')
def test_get_stock_info(mock_ticker):
    """Test getting stock information"""
    # Mock yfinance response
    mock_stock = MagicMock()
    mock_stock.info = {
        'longName': 'Apple Inc.',
        'sector': 'Technology',
        'currentPrice': 150.00,
        'previousClose': 148.00,
        'marketCap': 2500000000000,
        'trailingPE': 25.5,
        'dividendYield': 0.005,
        'fiftyTwoWeekLow': 120.00,
        'fiftyTwoWeekHigh': 180.00
    }
    mock_ticker.return_value = mock_stock

    result = StockService.get_stock_info('AAPL')

    assert result is not None
    assert result['ticker'] == 'AAPL'
    assert result['company_name'] == 'Apple Inc.'
    assert result['current_price'] == 150.00
    assert result['pe_ratio'] == 25.5

@patch('app.services.stock_service.yf.Ticker')
def test_calculate_technical_indicators(mock_ticker):
    """Test technical indicators calculation"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    # Create mock historical data
    dates = pd.date_range(end=datetime.now(), periods=100)
    mock_history = pd.DataFrame({
        'Open': np.random.uniform(145, 155, 100),
        'High': np.random.uniform(150, 160, 100),
        'Low': np.random.uniform(140, 150, 100),
        'Close': np.random.uniform(145, 155, 100),
        'Volume': np.random.uniform(1000000, 5000000, 100)
    }, index=dates)

    mock_stock = MagicMock()
    mock_stock.history.return_value = mock_history
    mock_ticker.return_value = mock_stock

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

@patch('app.services.stock_service.yf.Ticker')
def test_get_price_history(mock_ticker):
    """Test getting price history"""
    import pandas as pd
    from datetime import datetime, timedelta

    # Create mock historical data
    dates = pd.date_range(end=datetime.now(), periods=30)
    mock_history = pd.DataFrame({
        'Open': [145.0] * 30,
        'High': [150.0] * 30,
        'Low': [144.0] * 30,
        'Close': [149.0] * 30,
        'Volume': [1000000] * 30
    }, index=dates)

    mock_stock = MagicMock()
    mock_stock.history.return_value = mock_history
    mock_ticker.return_value = mock_stock

    result = StockService.get_price_history('AAPL', '1mo')

    assert result is not None
    assert result['ticker'] == 'AAPL'
    assert result['period'] == '1mo'
    assert len(result['data']) == 30
    assert result['data'][0]['close'] == 149.0

@patch('app.services.stock_service.StockCache')
def test_caching(mock_cache):
    """Test that caching is used"""
    # Mock cache hit
    mock_cache.get_cached.return_value = {
        'ticker': 'AAPL',
        'current_price': 150.00
    }

    with patch('app.services.stock_service.yf.Ticker') as mock_ticker:
        result = StockService.get_stock_info('AAPL')

        # yfinance should not be called if cache hit
        mock_ticker.assert_not_called()
        assert result['current_price'] == 150.00