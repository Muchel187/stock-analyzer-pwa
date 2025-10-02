"""
Historical Data Scheduler Service
Manages scheduled updates of historical price data
"""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from threading import Thread
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app import create_app, db
from app.models import Portfolio, Watchlist
from app.models.historical_price import DataCollectionMetadata
from app.services.historical_data_service import HistoricalDataService

logger = logging.getLogger(__name__)


class DataSchedulerService:
    """
    Manages scheduled data collection for historical prices
    Updates priority tickers every few hours
    """

    def __init__(self, app=None):
        self.app = app
        self.scheduler = BackgroundScheduler(
            timezone='UTC',
            job_defaults={'coalesce': True, 'max_instances': 1}
        )
        self.is_running = False

    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app

        # Start scheduler on app startup
        if not self.scheduler.running:
            self.scheduler.start()
            self.is_running = True

            # Schedule jobs
            self._schedule_jobs()

            # Shut down scheduler on app exit
            atexit.register(self._shutdown)

            logger.info("DataSchedulerService initialized and started")

    def _schedule_jobs(self):
        """Schedule all data collection jobs"""

        # Update high-priority tickers every 2 hours during market hours
        self.scheduler.add_job(
            func=self.update_priority_tickers,
            trigger=IntervalTrigger(hours=2),
            id='update_priority_tickers',
            name='Update priority tickers',
            replace_existing=True
        )

        # Update all active tickers once a day at 2 AM UTC
        self.scheduler.add_job(
            func=self.update_all_active_tickers,
            trigger='cron',
            hour=2,
            id='update_all_active',
            name='Update all active tickers',
            replace_existing=True
        )

        # Clean old data weekly
        self.scheduler.add_job(
            func=self.cleanup_old_data,
            trigger='cron',
            day_of_week='sun',
            hour=3,
            id='cleanup_old_data',
            name='Clean up old data',
            replace_existing=True
        )

        logger.info("Scheduled jobs configured")

    def update_priority_tickers(self):
        """Update high-priority tickers (portfolio, watchlist, popular)"""
        with self.app.app_context():
            try:
                logger.info("Starting priority ticker update...")

                # Identify priority tickers
                priority_tickers = self._get_priority_tickers()

                logger.info(f"Updating {len(priority_tickers)} priority tickers")

                success_count = 0
                failed_count = 0

                for ticker in priority_tickers:
                    try:
                        # Update historical data for 1 month
                        result = HistoricalDataService.get_historical_data(
                            ticker=ticker,
                            period='1mo',
                            force_update=True
                        )

                        if result and result.get('data'):
                            success_count += 1
                            logger.info(f"✅ Updated {ticker}: {len(result['data'])} data points")
                        else:
                            failed_count += 1
                            logger.warning(f"❌ Failed to update {ticker}")

                        # Rate limiting - avoid hammering APIs
                        time.sleep(2)

                    except Exception as e:
                        failed_count += 1
                        logger.error(f"Error updating {ticker}: {e}")

                logger.info(f"Priority update complete: {success_count} success, {failed_count} failed")

            except Exception as e:
                logger.error(f"Error in priority ticker update: {e}")

    def update_all_active_tickers(self):
        """Update all active tickers in the database"""
        with self.app.app_context():
            try:
                logger.info("Starting full ticker update...")

                # Get all active tickers
                active_metadata = DataCollectionMetadata.query.filter_by(
                    is_active=True
                ).order_by(DataCollectionMetadata.priority.desc()).all()

                logger.info(f"Found {len(active_metadata)} active tickers")

                success_count = 0
                failed_count = 0

                for metadata in active_metadata:
                    ticker = metadata.ticker

                    try:
                        # Check if update is needed
                        if metadata.last_successful_collection:
                            age = datetime.now() - metadata.last_successful_collection
                            if age.total_seconds() < 86400:  # Updated within 24 hours
                                logger.info(f"Skipping {ticker} - recently updated")
                                continue

                        # Update historical data
                        period = '3mo' if metadata.priority >= 50 else '1mo'

                        result = HistoricalDataService.get_historical_data(
                            ticker=ticker,
                            period=period,
                            force_update=True
                        )

                        if result and result.get('data'):
                            success_count += 1
                            logger.info(f"✅ Updated {ticker}: {len(result['data'])} data points")
                        else:
                            failed_count += 1
                            logger.warning(f"❌ Failed to update {ticker}")

                        # Rate limiting
                        time.sleep(3)

                    except Exception as e:
                        failed_count += 1
                        logger.error(f"Error updating {ticker}: {e}")

                        # Mark as failed if too many consecutive failures
                        if metadata.consecutive_failures > 5:
                            metadata.is_active = False
                            db.session.commit()
                            logger.warning(f"Deactivating {ticker} after 5 consecutive failures")

                logger.info(f"Full update complete: {success_count} success, {failed_count} failed")

            except Exception as e:
                logger.error(f"Error in full ticker update: {e}")

    def cleanup_old_data(self):
        """Clean up old historical data to save space"""
        with self.app.app_context():
            try:
                logger.info("Starting data cleanup...")

                # Keep only last 2 years of data for low-priority tickers
                cutoff_date = datetime.now().date() - timedelta(days=730)

                from app.models.historical_price import HistoricalPrice

                # Get low-priority tickers
                low_priority = DataCollectionMetadata.query.filter(
                    DataCollectionMetadata.priority < 10
                ).all()

                deleted_count = 0

                for metadata in low_priority:
                    # Delete old data
                    deleted = HistoricalPrice.query.filter(
                        HistoricalPrice.ticker == metadata.ticker,
                        HistoricalPrice.date < cutoff_date
                    ).delete()

                    deleted_count += deleted

                db.session.commit()

                logger.info(f"Cleanup complete: deleted {deleted_count} old records")

            except Exception as e:
                logger.error(f"Error in data cleanup: {e}")
                db.session.rollback()

    def _get_priority_tickers(self) -> List[str]:
        """Get list of priority tickers to update"""
        priority_tickers = set()

        try:
            # Add portfolio tickers
            from app.models import Portfolio
            portfolio_items = db.session.query(Portfolio.ticker).distinct().all()
            for item in portfolio_items:
                priority_tickers.add(item[0])

            # Add watchlist tickers
            from app.models import WatchlistItem
            watchlist_items = db.session.query(WatchlistItem.ticker).distinct().all()
            for item in watchlist_items:
                priority_tickers.add(item[0])

            # Add popular US tickers
            popular_us = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA',
                         'SPY', 'QQQ', 'DIA', 'IWM', 'VTI', 'JPM', 'V', 'JNJ']
            for ticker in popular_us:
                priority_tickers.add(ticker)

            # Add popular German tickers
            popular_de = ['SAP.DE', 'SIE.DE', 'ALV.DE', 'BMW.DE', 'BAS.DE',
                         'BAYN.DE', 'DAI.DE', 'DBK.DE', 'VOW3.DE', 'MRK.DE']
            for ticker in popular_de:
                priority_tickers.add(ticker)

        except Exception as e:
            logger.error(f"Error getting priority tickers: {e}")

        return list(priority_tickers)

    def trigger_update(self, ticker: str, period: str = '1mo'):
        """Manually trigger update for a specific ticker"""
        with self.app.app_context():
            try:
                logger.info(f"Manually triggering update for {ticker}")

                result = HistoricalDataService.get_historical_data(
                    ticker=ticker,
                    period=period,
                    force_update=True
                )

                if result and result.get('data'):
                    logger.info(f"✅ Manual update successful: {len(result['data'])} data points")
                    return True
                else:
                    logger.warning(f"❌ Manual update failed for {ticker}")
                    return False

            except Exception as e:
                logger.error(f"Error in manual update: {e}")
                return False

    def get_scheduler_info(self) -> Dict[str, Any]:
        """Get information about scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })

        return {
            'is_running': self.is_running,
            'jobs': jobs,
            'scheduler_state': self.scheduler.state
        }

    def _shutdown(self):
        """Shutdown the scheduler gracefully"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("DataSchedulerService shut down")


# Global instance
data_scheduler = DataSchedulerService()