from datetime import datetime, timezone, timedelta
from app import db

class StockCache(db.Model):
    __tablename__ = 'stock_cache'

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20), nullable=False, unique=True, index=True)
    data = db.Column(db.JSON, nullable=False)
    data_type = db.Column(db.String(50))  # quote, info, history, analysis
    cached_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)

    @classmethod
    def get_cached(cls, ticker, data_type='quote'):
        """Get cached data if not expired"""
        cache = cls.query.filter_by(ticker=ticker, data_type=data_type).first()
        if cache:
            # Make expires_at timezone-aware if it's naive
            expires_at = cache.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if expires_at > datetime.now(timezone.utc):
                return cache.data
        return None

    @classmethod
    def set_cache(cls, ticker, data, data_type='quote', expires_at=None):
        """Set or update cache"""
        if expires_at is None:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        cache = cls.query.filter_by(ticker=ticker, data_type=data_type).first()
        if cache:
            cache.data = data
            cache.cached_at = datetime.now(timezone.utc)
            cache.expires_at = expires_at
        else:
            cache = cls(
                ticker=ticker,
                data=data,
                data_type=data_type,
                expires_at=expires_at
            )
            db.session.add(cache)

        db.session.commit()
        return cache

    def __repr__(self):
        return f'<StockCache {self.ticker} {self.data_type}>'