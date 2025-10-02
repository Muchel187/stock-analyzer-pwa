from datetime import datetime, timezone
from app import db
from sqlalchemy import func

class Portfolio(db.Model):
    __tablename__ = 'portfolios'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticker = db.Column(db.String(20), nullable=False, index=True)
    shares = db.Column(db.Float, nullable=False, default=0)
    avg_price = db.Column(db.Float, nullable=False, default=0)
    total_invested = db.Column(db.Float, nullable=False, default=0)
    current_price = db.Column(db.Float, default=0)
    current_value = db.Column(db.Float, default=0)
    gain_loss = db.Column(db.Float, default=0)
    gain_loss_percent = db.Column(db.Float, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    # Additional metadata
    company_name = db.Column(db.String(255))
    sector = db.Column(db.String(100))
    market = db.Column(db.String(20))  # USA or DAX

    __table_args__ = (
        db.UniqueConstraint('user_id', 'ticker', name='unique_user_ticker'),
    )

    def calculate_metrics(self, current_price):
        """Calculate portfolio metrics based on current price"""
        self.current_price = current_price
        self.current_value = self.shares * current_price
        self.gain_loss = self.current_value - self.total_invested
        if self.total_invested > 0:
            self.gain_loss_percent = (self.gain_loss / self.total_invested) * 100
        else:
            self.gain_loss_percent = 0
        self.last_updated = datetime.now(timezone.utc)

    def to_dict(self):
        """Convert portfolio item to dictionary"""
        return {
            'id': self.id,
            'ticker': self.ticker,
            'shares': self.shares,
            'avg_price': round(self.avg_price, 2) if self.avg_price else 0,
            'total_invested': round(self.total_invested, 2) if self.total_invested else 0,
            'current_price': round(self.current_price, 2) if self.current_price else 0,
            'current_value': round(self.current_value, 2) if self.current_value else 0,
            'gain_loss': round(self.gain_loss, 2) if self.gain_loss else 0,
            'gain_loss_percent': round(self.gain_loss_percent, 2) if self.gain_loss_percent else 0,
            'company_name': self.company_name,
            'sector': self.sector,
            'market': self.market,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticker = db.Column(db.String(20), nullable=False, index=True)
    transaction_type = db.Column(db.String(10), nullable=False)  # BUY or SELL
    shares = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # For tracking fees and taxes
    fees = db.Column(db.Float, default=0)
    tax = db.Column(db.Float, default=0)
    net_amount = db.Column(db.Float)

    def calculate_amounts(self):
        """Calculate transaction amounts"""
        self.total_amount = self.shares * self.price
        self.net_amount = self.total_amount + (self.fees or 0) + (self.tax or 0)

    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            'id': self.id,
            'ticker': self.ticker,
            'transaction_type': self.transaction_type,
            'shares': self.shares,
            'price': round(self.price, 2) if self.price else 0,
            'total_amount': round(self.total_amount, 2) if self.total_amount else 0,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'notes': self.notes,
            'fees': round(self.fees, 2) if self.fees else 0,
            'tax': round(self.tax, 2) if self.tax else 0,
            'net_amount': round(self.net_amount, 2) if self.net_amount else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Transaction {self.transaction_type} {self.shares} {self.ticker}>'