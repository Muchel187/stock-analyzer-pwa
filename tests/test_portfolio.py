import pytest
from app import db
from app.models import Portfolio, Transaction

def test_add_transaction_buy(client, auth_headers):
    """Test adding a buy transaction"""
    transaction_data = {
        'ticker': 'AAPL',
        'transaction_type': 'BUY',
        'shares': 10,
        'price': 150.00,
        'fees': 5.00
    }

    response = client.post('/api/portfolio/transaction',
                          headers=auth_headers,
                          json=transaction_data)

    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Transaction added successfully'
    assert data['transaction']['ticker'] == 'AAPL'
    assert data['transaction']['shares'] == 10

def test_add_transaction_sell(client, auth_headers):
    """Test adding a sell transaction"""
    # First add a buy transaction
    client.post('/api/portfolio/transaction', headers=auth_headers, json={
        'ticker': 'AAPL',
        'transaction_type': 'BUY',
        'shares': 20,
        'price': 150.00
    })

    # Then sell some shares
    response = client.post('/api/portfolio/transaction',
                          headers=auth_headers,
                          json={
                              'ticker': 'AAPL',
                              'transaction_type': 'SELL',
                              'shares': 10,
                              'price': 160.00
                          })

    assert response.status_code == 201
    data = response.get_json()
    assert data['transaction']['transaction_type'] == 'SELL'

def test_sell_more_than_owned(client, auth_headers):
    """Test selling more shares than owned"""
    # Buy 10 shares
    client.post('/api/portfolio/transaction', headers=auth_headers, json={
        'ticker': 'AAPL',
        'transaction_type': 'BUY',
        'shares': 10,
        'price': 150.00
    })

    # Try to sell 20 shares
    response = client.post('/api/portfolio/transaction',
                          headers=auth_headers,
                          json={
                              'ticker': 'AAPL',
                              'transaction_type': 'SELL',
                              'shares': 20,
                              'price': 160.00
                          })

    assert response.status_code == 400

def test_get_portfolio(client, auth_headers):
    """Test getting portfolio"""
    # Add some transactions first
    transactions = [
        {'ticker': 'AAPL', 'transaction_type': 'BUY', 'shares': 10, 'price': 150.00},
        {'ticker': 'MSFT', 'transaction_type': 'BUY', 'shares': 5, 'price': 300.00}
    ]

    for trans in transactions:
        client.post('/api/portfolio/transaction', headers=auth_headers, json=trans)

    response = client.get('/api/portfolio/', headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert 'summary' in data
    assert len(data['items']) == 2
    assert data['summary']['positions'] == 2

def test_portfolio_performance_calculation(client, auth_headers):
    """Test portfolio performance calculation"""
    # Add buy transaction
    client.post('/api/portfolio/transaction', headers=auth_headers, json={
        'ticker': 'AAPL',
        'transaction_type': 'BUY',
        'shares': 10,
        'price': 100.00
    })

    response = client.get('/api/portfolio/', headers=auth_headers)
    data = response.get_json()

    assert data['summary']['total_invested'] == 1000.00
    # Current value would depend on real-time price

def test_get_transactions(client, auth_headers):
    """Test getting transaction history"""
    # Add multiple transactions
    transactions = [
        {'ticker': 'AAPL', 'transaction_type': 'BUY', 'shares': 10, 'price': 150.00},
        {'ticker': 'AAPL', 'transaction_type': 'SELL', 'shares': 5, 'price': 160.00},
        {'ticker': 'MSFT', 'transaction_type': 'BUY', 'shares': 5, 'price': 300.00}
    ]

    for trans in transactions:
        client.post('/api/portfolio/transaction', headers=auth_headers, json=trans)

    # Get all transactions
    response = client.get('/api/portfolio/transactions', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['transactions']) == 3

    # Get transactions for specific ticker
    response = client.get('/api/portfolio/transactions?ticker=AAPL',
                         headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['transactions']) == 2
    assert all(t['ticker'] == 'AAPL' for t in data['transactions'])

def test_portfolio_diversification(app, sample_portfolio):
    """Test portfolio diversification calculation"""
    from app.services import PortfolioService

    with app.app_context():
        user_id = sample_portfolio['items'][0].user_id
        portfolio = PortfolioService.get_portfolio(user_id)

        assert 'diversification' in portfolio['summary']
        assert 'by_sector' in portfolio['summary']['diversification']
        assert 'Technology' in portfolio['summary']['diversification']['by_sector']

def test_transaction_validation(client, auth_headers):
    """Test transaction validation"""
    # Missing required fields
    response = client.post('/api/portfolio/transaction',
                          headers=auth_headers,
                          json={'ticker': 'AAPL'})
    assert response.status_code == 400

    # Invalid transaction type
    response = client.post('/api/portfolio/transaction',
                          headers=auth_headers,
                          json={
                              'ticker': 'AAPL',
                              'transaction_type': 'INVALID',
                              'shares': 10,
                              'price': 150.00
                          })
    assert response.status_code == 400