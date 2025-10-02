"""
Historical Data Service with Smart Caching and Multiple Sources
Collects and stores historical price data locally to avoid API rate limits
"""

import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any
import time
import random
from sqlalchemy import and_, desc
from sqlalchemy.exc import IntegrityError

from app import db
from app.models.historical_price import HistoricalPrice, DataCollectionMetadata

logger = logging.getLogger(__name__)


class HistoricalDataService:
    """
    Manages historical price data collection and retrieval
    Uses multiple sources with intelligent fallback and local caching
    """

    # Update frequencies (in hours)
    UPDATE_FREQUENCIES = {
        'realtime': 0.5,      # 30 minutes for current day
        'daily': 24,          # Once per day for recent data
        'weekly': 168,        # Once per week for older data
        'monthly': 720,       # Once per month for very old data
    }

    @staticmethod
    def get_historical_data(ticker: str, period: str = '1mo', force_update: bool = False) -> Dict[str, Any]:
        """
        Get historical data from local database or fetch if needed

        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
            force_update: Force fetching new data even if cached

        Returns:
            Dictionary with historical price data
        """
        try:
            ticker = ticker.upper()
            logger.info(f"[Historical] Getting data for {ticker}, period={period}")

            # Calculate date range
            end_date = datetime.now().date()
            start_date = HistoricalDataService._calculate_start_date(period, end_date)

            # Check local database first
            if not force_update:
                local_data = HistoricalDataService._get_from_database(ticker, start_date, end_date)

                # Check if we have sufficient data (at least 70% of expected range)
                days_expected = (end_date - start_date).days
                if local_data:
                    # Check data freshness
                    is_fresh = HistoricalDataService._is_data_fresh(ticker, start_date, end_date)
                    data_coverage = len(local_data) / max(days_expected * 0.7, 1)  # Assume ~70% trading days

                    if is_fresh and data_coverage > 0.5:  # At least 50% coverage
                        logger.info(f"[Historical] Using cached data for {ticker}: {len(local_data)} points")
                        return {
                            'ticker': ticker,
                            'period': period,
                            'data': [price.to_dict() for price in local_data],
                            'source': 'local_cache',
                            'last_updated': local_data[0].updated_at.isoformat() if local_data else None
                        }
                    else:
                        logger.info(f"[Historical] Cache insufficient or stale for {ticker}: {len(local_data)} points, coverage={data_coverage:.1%}")

            # Data is stale or missing, fetch new data
            logger.info(f"[Historical] Fetching fresh data for {ticker}")
            success = HistoricalDataService._collect_and_store(ticker, period)

            if success:
                # Get the newly stored data
                local_data = HistoricalDataService._get_from_database(ticker, start_date, end_date)

                if local_data:
                    return {
                        'ticker': ticker,
                        'period': period,
                        'data': [price.to_dict() for price in local_data],
                        'source': 'freshly_fetched',
                        'last_updated': datetime.now().isoformat()
                    }

            # If all else fails, return whatever we have (even if stale)
            local_data = HistoricalDataService._get_from_database(ticker, start_date, end_date)

            if local_data:
                logger.warning(f"[Historical] Returning stale data for {ticker}")
                return {
                    'ticker': ticker,
                    'period': period,
                    'data': [price.to_dict() for price in local_data],
                    'source': 'stale_cache',
                    'last_updated': local_data[0].updated_at.isoformat() if local_data else None
                }

            # Try to get ANY available data for this ticker (regardless of date)
            any_data = HistoricalDataService._get_any_available_data(ticker)
            if any_data:
                logger.warning(f"[Historical] Returning ANY available cached data for {ticker} ({len(any_data)} points)")
                return {
                    'ticker': ticker,
                    'period': period,
                    'data': [price.to_dict() for price in any_data],
                    'source': 'any_cache',
                    'last_updated': any_data[0].updated_at.isoformat() if any_data else None,
                    'warning': 'Data is from a different time period due to API limitations'
                }

            # No data available at all
            logger.error(f"[Historical] No data available for {ticker}")
            return {
                'ticker': ticker,
                'period': period,
                'data': [],
                'source': 'none',
                'error': 'No historical data available'
            }

        except Exception as e:
            logger.error(f"[Historical] Error getting data for {ticker}: {e}")
            return {
                'ticker': ticker,
                'period': period,
                'data': [],
                'source': 'error',
                'error': str(e)
            }

    @staticmethod
    def _get_from_database(ticker: str, start_date: date, end_date: date) -> List[HistoricalPrice]:
        """Get historical prices from local database"""
        return HistoricalPrice.query.filter(
            and_(
                HistoricalPrice.ticker == ticker,
                HistoricalPrice.date >= start_date,
                HistoricalPrice.date <= end_date
            )
        ).order_by(HistoricalPrice.date.desc()).all()

    @staticmethod
    def _get_any_available_data(ticker: str, limit: int = 365) -> List[HistoricalPrice]:
        """Get ANY available historical data for ticker, regardless of date range"""
        return HistoricalPrice.query.filter_by(
            ticker=ticker
        ).order_by(HistoricalPrice.date.desc()).limit(limit).all()

    @staticmethod
    def _is_data_fresh(ticker: str, start_date: date, end_date: date) -> bool:
        """
        Check if cached data is fresh enough

        Returns True if data doesn't need updating
        """
        metadata = DataCollectionMetadata.query.filter_by(ticker=ticker).first()

        if not metadata or not metadata.last_successful_collection:
            return False

        # Calculate age of data
        data_age = datetime.now() - metadata.last_successful_collection

        # Different freshness requirements based on date range
        days_range = (end_date - start_date).days

        if days_range <= 5:  # Recent data
            # Update every 30 minutes during market hours
            if HistoricalDataService._is_market_hours():
                return data_age.total_seconds() < 1800  # 30 minutes
            else:
                return data_age.total_seconds() < 3600  # 1 hour

        elif days_range <= 30:  # Monthly data
            return data_age.total_seconds() < 86400  # 24 hours

        else:  # Older data
            return data_age.total_seconds() < 604800  # 7 days

    @staticmethod
    def _collect_and_store(ticker: str, period: str) -> bool:
        """
        Collect historical data from available sources and store in database

        Priority Order (yfinance REMOVED due to severe rate limiting):
        1. Twelve Data (PRIMARY) - 800 req/day, best for historical data
        2. Alpha Vantage (SECONDARY) - 25 req/day, reliable
        3. Fallback Service (TERTIARY) - Uses Finnhub or other sources

        Returns True if successful
        """
        try:
            # Try different sources in order of preference
            data = None
            source = None

            # 1. Try Twelve Data (PRIMARY - best rate limits)
            if not data:
                data, source = HistoricalDataService._fetch_from_twelve_data(ticker, period)

            # 2. Try Alpha Vantage (SECONDARY)
            if not data:
                data, source = HistoricalDataService._fetch_from_alpha_vantage(ticker, period)

            # 3. Try existing alternative sources (TERTIARY)
            if not data:
                data, source = HistoricalDataService._fetch_from_fallback(ticker, period)

            if data:
                # Store in database
                stored = HistoricalDataService._store_data(ticker, data, source)

                # Update metadata
                HistoricalDataService._update_metadata(ticker, success=stored)

                return stored

            # No data from any source
            HistoricalDataService._update_metadata(ticker, success=False, error="No data from any source")
            return False

        except Exception as e:
            logger.error(f"[Historical] Error collecting data for {ticker}: {e}")
            HistoricalDataService._update_metadata(ticker, success=False, error=str(e))
            return False

    @staticmethod
    def _fetch_from_alpha_vantage(ticker: str, period: str) -> tuple:
        """Fetch data from Alpha Vantage"""
        try:
            from app.services.alternative_data_sources import AlphaVantageService

            # ALWAYS use 'compact' to avoid getting 20+ years of data (6500+ points)
            # 'compact' returns last 100 data points, which is sufficient for 6mo period
            outputsize = 'compact'

            data_response = AlphaVantageService.get_time_series_daily(ticker, outputsize)

            if data_response and data_response.get('data'):
                # Limit to max 500 points to prevent database overload
                data = data_response['data'][:500]
                logger.info(f"[Historical] Got {len(data)} points from Alpha Vantage (limited from {len(data_response['data'])})")
                return data, 'alpha_vantage'

            return None, None

        except Exception as e:
            logger.error(f"[Historical] Alpha Vantage error for {ticker}: {e}")
            return None, None

    @staticmethod
    def _fetch_from_twelve_data(ticker: str, period: str) -> tuple:
        """Fetch data from Twelve Data"""
        try:
            from app.services.alternative_data_sources import TwelveDataService

            # Map period to outputsize
            outputsize_map = {
                '1d': 1, '5d': 5, '1mo': 30, '3mo': 90,
                '6mo': 180, '1y': 365, '2y': 730, '5y': 1825
            }
            outputsize = outputsize_map.get(period, 30)

            data_response = TwelveDataService.get_time_series(ticker, outputsize=outputsize)

            if data_response and data_response.get('data'):
                logger.info(f"[Historical] Got {len(data_response['data'])} points from Twelve Data")
                return data_response['data'], 'twelve_data'

            return None, None

        except Exception as e:
            logger.error(f"[Historical] Twelve Data error for {ticker}: {e}")
            return None, None

    @staticmethod
    def _fetch_from_fallback(ticker: str, period: str) -> tuple:
        """Try existing fallback service"""
        try:
            from app.services.alternative_data_sources import FallbackDataService

            # Map period to outputsize
            outputsize_map = {
                '1d': 1, '5d': 5, '1mo': 30, '3mo': 90,
                '6mo': 180, '1y': 365, '2y': 730, '5y': 1825
            }
            outputsize = outputsize_map.get(period, 30)

            data_response = FallbackDataService.get_historical_data(ticker, outputsize=outputsize)

            if data_response and data_response.get('data'):
                logger.info(f"[Historical] Got {len(data_response['data'])} points from Fallback Service")
                return data_response['data'], 'fallback'

            return None, None

        except Exception as e:
            logger.error(f"[Historical] Fallback error for {ticker}: {e}")
            return None, None

    @staticmethod
    def _store_data(ticker: str, data: List[Dict], source: str) -> bool:
        """Store historical data in database using optimized batch insert"""
        try:
            if not data or len(data) == 0:
                logger.warning(f"[Historical] No data to store for {ticker}")
                return False

            # Limit data to prevent database overload (max 500 points)
            if len(data) > 500:
                logger.warning(f"[Historical] Limiting data from {len(data)} to 500 points for {ticker}")
                data = data[:500]

            # Get all existing dates for this ticker in one query
            existing_dates = {
                row.date: row for row in
                HistoricalPrice.query.filter_by(ticker=ticker).all()
            }

            new_records = []
            updated_count = 0

            for point in data:
                point_date = point['date']

                if point_date in existing_dates:
                    # Update existing record
                    existing = existing_dates[point_date]
                    existing.open = point.get('open', existing.open)
                    existing.high = point.get('high', existing.high)
                    existing.low = point.get('low', existing.low)
                    existing.close = point.get('close', existing.close)
                    existing.volume = point.get('volume', existing.volume)
                    existing.source = source
                    existing.updated_at = datetime.now()
                    updated_count += 1
                else:
                    # Prepare new record for batch insert
                    new_records.append(HistoricalPrice(
                        ticker=ticker,
                        date=point_date,
                        open=point.get('open'),
                        high=point.get('high'),
                        low=point.get('low'),
                        close=point.get('close'),
                        volume=point.get('volume'),
                        source=source
                    ))

            # Batch insert all new records at once
            if new_records:
                db.session.bulk_save_objects(new_records)

            db.session.commit()

            total_stored = len(new_records) + updated_count
            logger.info(f"[Historical] Stored {total_stored} points for {ticker} ({len(new_records)} new, {updated_count} updated)")
            return total_stored > 0

        except Exception as e:
            logger.error(f"[Historical] Error storing data for {ticker}: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def _update_metadata(ticker: str, success: bool, error: str = None):
        """Update collection metadata"""
        try:
            metadata = DataCollectionMetadata.query.filter_by(ticker=ticker).first()

            if not metadata:
                metadata = DataCollectionMetadata(ticker=ticker)
                db.session.add(metadata)

            metadata.last_collected_at = datetime.now()

            if success:
                metadata.last_successful_collection = datetime.now()
                metadata.collection_status = 'success'
                metadata.consecutive_failures = 0
                metadata.error_message = None

                # Update data range
                prices = HistoricalPrice.query.filter_by(ticker=ticker).all()
                if prices:
                    metadata.data_points_count = len(prices)
                    dates = [p.date for p in prices]
                    metadata.earliest_date = min(dates)
                    metadata.latest_date = max(dates)
            else:
                metadata.collection_status = 'failed'
                metadata.consecutive_failures = (metadata.consecutive_failures or 0) + 1
                metadata.error_message = error

            db.session.commit()

        except Exception as e:
            logger.error(f"[Historical] Error updating metadata for {ticker}: {e}")
            db.session.rollback()

    @staticmethod
    def _calculate_start_date(period: str, end_date: date) -> date:
        """Calculate start date based on period"""
        period_days = {
            '1d': 1, '5d': 5, '1mo': 30, '3mo': 90,
            '6mo': 180, '1y': 365, '2y': 730, '5y': 1825,
            'max': 7300  # 20 years
        }

        days = period_days.get(period, 30)
        return end_date - timedelta(days=days)

    @staticmethod
    def _is_market_hours() -> bool:
        """Check if currently in market hours (simplified)"""
        now = datetime.now()

        # Weekday check (Mon=0, Sun=6)
        if now.weekday() > 4:  # Weekend
            return False

        # Time check (9:30 AM - 4:00 PM EST)
        # Simplified: 14:30 - 21:00 UTC
        hour = now.hour
        return 14 <= hour <= 21

    @staticmethod
    def update_priority_tickers():
        """
        Update priority tickers (portfolio, watchlist, popular)
        Should be called periodically
        """
        try:
            from app.models import Portfolio, WatchlistItem

            priority_tickers = set()

            # Get all portfolio tickers
            portfolio_items = Portfolio.query.all()
            for item in portfolio_items:
                priority_tickers.add(item.ticker)

            # Get all watchlist tickers
            watchlist_items = WatchlistItem.query.all()
            for item in watchlist_items:
                priority_tickers.add(item.ticker)

            # Add popular tickers
            popular = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'SPY', 'QQQ']
            for ticker in popular:
                priority_tickers.add(ticker)

            # Update priorities
            for ticker in priority_tickers:
                metadata = DataCollectionMetadata.query.filter_by(ticker=ticker).first()
                if not metadata:
                    metadata = DataCollectionMetadata(ticker=ticker)
                    db.session.add(metadata)

                metadata.priority = 100  # High priority
                metadata.is_active = True

            db.session.commit()
            logger.info(f"[Historical] Updated {len(priority_tickers)} priority tickers")

        except Exception as e:
            logger.error(f"[Historical] Error updating priority tickers: {e}")
            db.session.rollback()