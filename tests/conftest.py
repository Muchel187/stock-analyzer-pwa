import pytest
from app import create_app, db
from app.models import User, Portfolio, Transaction
from datetime import datetime, timezone

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client):
    """Create authenticated user and return headers with token"""
    # Create test user
    user_data = {
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'testpass123'
    }

    # Register user
    response = client.post('/api/auth/register', json=user_data)
    data = response.get_json()

    return {
        'Authorization': f'Bearer {data["access_token"]}'
    }

@pytest.fixture
def sample_user(app):
    """Create a sample user and return user_id"""
    with app.app_context():
        user = User(
            email='sample@example.com',
            username='sampleuser'
        )
        user.set_password('samplepass123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id  # Store ID

    # Return user_id, not the user object
    # Tests should use this ID directly
    class UserFixture:
        def __init__(self, user_id):
            self._id = user_id

        @property
        def id(self):
            return self._id

    return UserFixture(user_id)

@pytest.fixture
def sample_portfolio(app, sample_user):
    """Create sample portfolio data and return user_id"""
    with app.app_context():
        # Get user_id within app context
        user_id = sample_user.id

        # Add portfolio items
        portfolio_items = [
            Portfolio(
                user_id=user_id,
                ticker='AAPL',
                shares=10,
                avg_price=150.00,
                total_invested=1500.00,
                company_name='Apple Inc.',
                sector='Technology',
                market='USA'
            ),
            Portfolio(
                user_id=user_id,
                ticker='MSFT',
                shares=5,
                avg_price=300.00,
                total_invested=1500.00,
                company_name='Microsoft Corporation',
                sector='Technology',
                market='USA'
            )
        ]

        for item in portfolio_items:
            db.session.add(item)

        # Add transactions
        transactions = [
            Transaction(
                user_id=user_id,
                ticker='AAPL',
                transaction_type='BUY',
                shares=10,
                price=150.00,
                total_amount=1500.00,
                transaction_date=datetime.now(timezone.utc)
            ),
            Transaction(
                user_id=user_id,
                ticker='MSFT',
                transaction_type='BUY',
                shares=5,
                price=300.00,
                total_amount=1500.00,
                transaction_date=datetime.now(timezone.utc)
            )
        ]

        for transaction in transactions:
            transaction.calculate_amounts()
            db.session.add(transaction)

        db.session.commit()

        # Return user_id instead of objects
        return {
            'user_id': user_id,
            'item_count': len(portfolio_items),
            'transaction_count': len(transactions)
        }