from datetime import datetime
import logging
from app.services import AlertService, PortfolioService
from app.models import Portfolio, Watchlist

logger = logging.getLogger(__name__)

def check_price_alerts():
    """Job to check price alerts"""
    try:
        logger.info("Checking price alerts...")
        triggered_alerts = AlertService.check_alerts()
        logger.info(f"Alert check complete. {len(triggered_alerts)} alerts triggered.")
    except Exception as e:
        logger.error(f"Error in alert check job: {str(e)}")

def update_portfolio_prices():
    """Job to update portfolio prices"""
    try:
        logger.info("Updating portfolio prices...")

        # Get all unique portfolio items
        portfolio_items = Portfolio.query.all()

        for item in portfolio_items:
            PortfolioService.update_portfolio_item(item)

        logger.info(f"Updated {len(portfolio_items)} portfolio items")
    except Exception as e:
        logger.error(f"Error updating portfolio prices: {str(e)}")

def update_watchlist_prices():
    """Job to update watchlist prices"""
    try:
        logger.info("Updating watchlist prices...")

        from app import db
        from app.services import StockService

        # Get all unique watchlist items
        watchlist_items = Watchlist.query.all()

        for item in watchlist_items:
            stock_info = StockService.get_stock_info(item.ticker)
            if stock_info and stock_info.get('current_price'):
                item.update_price(stock_info['current_price'])

        db.session.commit()
        logger.info(f"Updated {len(watchlist_items)} watchlist items")
    except Exception as e:
        logger.error(f"Error updating watchlist prices: {str(e)}")

def cleanup_old_cache():
    """Job to clean up expired cache entries"""
    try:
        from app import db
        from app.models import StockCache

        expired = StockCache.query.filter(
            StockCache.expires_at < datetime.utcnow()
        ).all()

        for cache_entry in expired:
            db.session.delete(cache_entry)

        db.session.commit()
        logger.info(f"Cleaned up {len(expired)} expired cache entries")
    except Exception as e:
        logger.error(f"Error cleaning cache: {str(e)}")

def setup_jobs(app, scheduler):
    """Setup all background jobs"""

    # Check alerts every minute
    scheduler.add_job(
        func=check_price_alerts,
        trigger="interval",
        seconds=app.config.get('ALERT_CHECK_INTERVAL', 60),
        id='check_alerts',
        name='Check price alerts',
        replace_existing=True
    )

    # Update portfolio prices every 5 minutes
    scheduler.add_job(
        func=update_portfolio_prices,
        trigger="interval",
        seconds=app.config.get('PORTFOLIO_UPDATE_INTERVAL', 300),
        id='update_portfolio',
        name='Update portfolio prices',
        replace_existing=True
    )

    # Update watchlist prices every 5 minutes
    scheduler.add_job(
        func=update_watchlist_prices,
        trigger="interval",
        seconds=300,
        id='update_watchlist',
        name='Update watchlist prices',
        replace_existing=True
    )

    # Clean up cache every hour
    scheduler.add_job(
        func=cleanup_old_cache,
        trigger="interval",
        hours=1,
        id='cleanup_cache',
        name='Clean up expired cache',
        replace_existing=True
    )

    logger.info("Background jobs scheduled successfully")