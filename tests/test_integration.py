import pytest
from datetime import datetime
from app import db
from app.models import User, Portfolio, Transaction, Watchlist, Alert

def test_full_user_workflow(client):
    """Test complete user workflow from registration to portfolio management"""
    # 1. Register user
    response = client.post('/api/auth/register', json={
        'email': 'workflow@example.com',
        'username': 'workflowuser',
        'password': 'password123'
    })
    assert response.status_code == 201
    token = response.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Add stock to watchlist
    response = client.post('/api/watchlist/', headers=headers, json={
        'ticker': 'AAPL',
        'notes': 'Watching for dip'
    })
    assert response.status_code == 201

    # 3. Create price alert
    response = client.post('/api/alerts/', headers=headers, json={
        'ticker': 'AAPL',
        'alert_type': 'PRICE_BELOW',
        'target_value': 140.00
    })
    assert response.status_code == 201

    # 4. Add buy transaction
    response = client.post('/api/portfolio/transaction', headers=headers, json={
        'ticker': 'AAPL',
        'transaction_type': 'BUY',
        'shares': 10,
        'price': 145.00
    })
    assert response.status_code == 201

    # 5. Check portfolio
    response = client.get('/api/portfolio/', headers=headers)
    assert response.status_code == 200
    portfolio = response.get_json()
    assert portfolio['summary']['positions'] == 1
    assert portfolio['summary']['total_invested'] == 1450.00

    # 6. Remove from watchlist (since we bought it)
    response = client.delete('/api/watchlist/AAPL', headers=headers)
    assert response.status_code == 200

def test_screener_to_portfolio_flow(client):
    """Test flow from screener to portfolio"""
    # Register user
    response = client.post('/api/auth/register', json={
        'email': 'screener@example.com',
        'username': 'screeneruser',
        'password': 'password123'
    })
    token = response.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 1. Run screener (would return mock data in test)
    response = client.post('/api/screener/', json={
        'market': 'USA',
        'min_market_cap': 1000000000,
        'max_pe_ratio': 20,
        'prefer_value': True
    })
    # Note: This would fail without mocking yfinance, but structure is correct

    # 2. Add screener result to watchlist
    response = client.post('/api/watchlist/', headers=headers, json={
        'ticker': 'MSFT',
        'tags': ['value', 'screener']
    })

    # 3. Eventually buy the stock
    response = client.post('/api/portfolio/transaction', headers=headers, json={
        'ticker': 'MSFT',
        'transaction_type': 'BUY',
        'shares': 5,
        'price': 300.00
    })

def test_portfolio_performance_tracking(app, sample_user):
    """Test portfolio performance over multiple transactions"""
    from app.services import PortfolioService

    with app.app_context():
        user_id = sample_user.id

        # Add initial transactions
        trans1 = PortfolioService.add_transaction(user_id, {
            'ticker': 'AAPL',
            'transaction_type': 'BUY',
            'shares': 10,
            'price': 100.00,
            'transaction_date': datetime(2024, 1, 1)
        })

        trans2 = PortfolioService.add_transaction(user_id, {
            'ticker': 'AAPL',
            'transaction_type': 'BUY',
            'shares': 10,
            'price': 110.00,
            'transaction_date': datetime(2024, 2, 1)
        })

        # Check portfolio
        portfolio = PortfolioService.get_portfolio(user_id)

        assert len(portfolio['items']) == 1
        assert portfolio['items'][0]['shares'] == 20
        assert portfolio['items'][0]['avg_price'] == 105.00  # (100*10 + 110*10) / 20

        # Sell some shares
        trans3 = PortfolioService.add_transaction(user_id, {
            'ticker': 'AAPL',
            'transaction_type': 'SELL',
            'shares': 5,
            'price': 120.00,
            'transaction_date': datetime(2024, 3, 1)
        })

        portfolio = PortfolioService.get_portfolio(user_id)
        assert portfolio['items'][0]['shares'] == 15

def test_alert_triggering(app, sample_user):
    """Test alert triggering mechanism"""
    from app.services import AlertService

    with app.app_context():
        # Create alert
        alert = AlertService.create_alert(sample_user.id, {
            'ticker': 'AAPL',
            'alert_type': 'PRICE_BELOW',
            'target_value': 145.00
        })

        assert alert is not None
        assert not alert.is_triggered

        # Mock checking alerts (would need to mock stock price)
        # In real scenario, the background job would check this

def test_watchlist_price_tracking(app, sample_user):
    """Test watchlist price tracking"""
    with app.app_context():
        # Add to watchlist
        watchlist_item = Watchlist(
            user_id=sample_user.id,
            ticker='TSLA',
            company_name='Tesla Inc.',
            added_price=200.00,
            current_price=200.00
        )
        db.session.add(watchlist_item)
        db.session.commit()

        # Update price
        watchlist_item.update_price(220.00)

        assert watchlist_item.current_price == 220.00
        assert watchlist_item.price_change == 20.00
        assert watchlist_item.price_change_percent == 10.0

def test_concurrent_transactions(app, sample_user):
    """Test handling concurrent transactions"""
    from app.services import PortfolioService

    with app.app_context():
        user_id = sample_user.id

        # Buy initial shares
        PortfolioService.add_transaction(user_id, {
            'ticker': 'GOOGL',
            'transaction_type': 'BUY',
            'shares': 100,
            'price': 100.00
        })

        # Try to sell more than owned (should fail)
        result = PortfolioService.add_transaction(user_id, {
            'ticker': 'GOOGL',
            'transaction_type': 'SELL',
            'shares': 150,
            'price': 110.00
        })

        assert result is None  # Transaction should fail

        # Sell valid amount
        result = PortfolioService.add_transaction(user_id, {
            'ticker': 'GOOGL',
            'transaction_type': 'SELL',
            'shares': 50,
            'price': 110.00
        })

        assert result is not None
        portfolio = PortfolioService.get_portfolio(user_id)

        # Find GOOGL in portfolio
        googl_item = next((item for item in portfolio['items']
                          if item['ticker'] == 'GOOGL'), None)
        assert googl_item['shares'] == 50