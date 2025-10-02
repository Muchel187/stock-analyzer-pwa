"""
Historical Price Model for storing stock price history
"""

from app import db
from datetime import datetime
from sqlalchemy import Index, UniqueConstraint


class HistoricalPrice(db.Model):
    """
    Store historical stock prices in local database
    This eliminates dependency on rate-limited APIs
    """

    __tablename__ = 'historical_prices'

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)

    # OHLCV data
    open = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    close = db.Column(db.Float, nullable=False)
    adjusted_close = db.Column(db.Float)
    volume = db.Column(db.BigInteger)

    # Metadata
    source = db.Column(db.String(50))  # 'yfinance', 'alpha_vantage', 'finnhub', 'manual'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint to prevent duplicate entries
    __table_args__ = (
        UniqueConstraint('ticker', 'date', name='uq_ticker_date'),
        Index('idx_ticker', 'ticker'),
        Index('idx_date', 'date'),
        Index('idx_ticker_date', 'ticker', 'date'),
    )

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'date': self.date.isoformat() if self.date else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'adjusted_close': float(self.adjusted_close) if self.adjusted_close else None,
            'volume': int(self.volume) if self.volume else None,
            'source': self.source
        }

    def __repr__(self):
        return f'<HistoricalPrice {self.ticker} {self.date} ${self.close}>'


class DataCollectionMetadata(db.Model):
    """
    Track when we last collected data for each ticker
    Helps manage efficient data updates
    """

    __tablename__ = 'data_collection_metadata'

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20), unique=True, nullable=False)

    # Tracking
    last_collected_at = db.Column(db.DateTime)
    last_successful_collection = db.Column(db.DateTime)

    # Data range
    earliest_date = db.Column(db.Date)
    latest_date = db.Column(db.Date)
    data_points_count = db.Column(db.Integer, default=0)

    # Status
    collection_status = db.Column(db.String(50))  # 'success', 'failed', 'pending', 'rate_limited'
    error_message = db.Column(db.Text)
    consecutive_failures = db.Column(db.Integer, default=0)

    # Priority (higher = more important)
    priority = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_metadata_ticker', 'ticker'),
        Index('idx_metadata_priority', 'priority'),
        Index('idx_metadata_status', 'collection_status'),
    )

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'ticker': self.ticker,
            'last_collected_at': self.last_collected_at.isoformat() if self.last_collected_at else None,
            'last_successful_collection': self.last_successful_collection.isoformat() if self.last_successful_collection else None,
            'earliest_date': self.earliest_date.isoformat() if self.earliest_date else None,
            'latest_date': self.latest_date.isoformat() if self.latest_date else None,
            'data_points_count': self.data_points_count,
            'collection_status': self.collection_status,
            'priority': self.priority,
            'is_active': self.is_active
        }

    def __repr__(self):
        return f'<DataCollectionMetadata {self.ticker} status={self.collection_status}>'