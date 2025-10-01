from datetime import datetime
from app import db

class Watchlist(db.Model):
    __tablename__ = 'watchlists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticker = db.Column(db.String(20), nullable=False, index=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    # Price tracking
    added_price = db.Column(db.Float)
    current_price = db.Column(db.Float)
    price_change = db.Column(db.Float)
    price_change_percent = db.Column(db.Float)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    # Stock metadata
    company_name = db.Column(db.String(255))
    sector = db.Column(db.String(100))
    market = db.Column(db.String(20))  # USA or DAX
    market_cap = db.Column(db.Float)
    pe_ratio = db.Column(db.Float)
    dividend_yield = db.Column(db.Float)

    # Custom tags
    tags = db.Column(db.JSON, default=list)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'ticker', name='unique_user_watchlist_ticker'),
    )

    def update_price(self, current_price):
        """Update current price and calculate changes"""
        self.current_price = current_price
        if self.added_price:
            self.price_change = current_price - self.added_price
            self.price_change_percent = (self.price_change / self.added_price) * 100
        self.last_updated = datetime.utcnow()

    def to_dict(self):
        """Convert watchlist item to dictionary"""
        return {
            'id': self.id,
            'ticker': self.ticker,
            'company_name': self.company_name,
            'sector': self.sector,
            'market': self.market,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'added_price': round(self.added_price, 2) if self.added_price else None,
            'current_price': round(self.current_price, 2) if self.current_price else None,
            'price_change': round(self.price_change, 2) if self.price_change else None,
            'price_change_percent': round(self.price_change_percent, 2) if self.price_change_percent else None,
            'market_cap': self.market_cap,
            'pe_ratio': round(self.pe_ratio, 2) if self.pe_ratio else None,
            'dividend_yield': round(self.dividend_yield, 2) if self.dividend_yield else None,
            'tags': self.tags if self.tags else [],
            'notes': self.notes,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

    def __repr__(self):
        return f'<Watchlist {self.ticker} for User {self.user_id}>'