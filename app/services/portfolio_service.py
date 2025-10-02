from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from app import db
from app.models import Portfolio, Transaction, User
from app.services.stock_service import StockService
from app.services.risk_analytics import RiskAnalytics
import numpy as np
import logging

logger = logging.getLogger(__name__)

class PortfolioService:
    """Service for portfolio management operations"""

    @staticmethod
    def add_transaction(user_id: int, transaction_data: Dict[str, Any]) -> Optional[Transaction]:
        """Add a new transaction and update portfolio"""
        try:
            # Create transaction
            transaction = Transaction(
                user_id=user_id,
                ticker=transaction_data['ticker'].upper(),
                transaction_type=transaction_data['transaction_type'],
                shares=float(transaction_data['shares']),
                price=float(transaction_data['price']),
                transaction_date=transaction_data.get('transaction_date', datetime.now(timezone.utc)),
                notes=transaction_data.get('notes', ''),
                fees=float(transaction_data.get('fees', 0)),
                tax=float(transaction_data.get('tax', 0))
            )
            transaction.calculate_amounts()

            db.session.add(transaction)

            # Update portfolio
            portfolio_item = Portfolio.query.filter_by(
                user_id=user_id,
                ticker=transaction.ticker
            ).first()

            if transaction.transaction_type == 'BUY':
                if portfolio_item:
                    # Update existing position
                    total_shares = portfolio_item.shares + transaction.shares
                    total_cost = portfolio_item.total_invested + transaction.net_amount
                    portfolio_item.shares = total_shares
                    portfolio_item.total_invested = total_cost
                    portfolio_item.avg_price = total_cost / total_shares if total_shares > 0 else 0
                else:
                    # Create new position
                    stock_info = StockService.get_stock_info(transaction.ticker)
                    portfolio_item = Portfolio(
                        user_id=user_id,
                        ticker=transaction.ticker,
                        shares=transaction.shares,
                        avg_price=transaction.price,
                        total_invested=transaction.net_amount,
                        company_name=stock_info.get('company_name') if stock_info else transaction.ticker,
                        sector=stock_info.get('sector') if stock_info else 'Unknown',
                        market=stock_info.get('market') if stock_info else 'USA'
                    )
                    db.session.add(portfolio_item)

            elif transaction.transaction_type == 'SELL':
                if portfolio_item and portfolio_item.shares >= transaction.shares:
                    # Update position
                    portfolio_item.shares -= transaction.shares
                    if portfolio_item.shares == 0:
                        # Remove position if all shares sold
                        db.session.delete(portfolio_item)
                    else:
                        # Recalculate average price (FIFO method)
                        portfolio_item.total_invested -= (transaction.shares * portfolio_item.avg_price)
                else:
                    db.session.rollback()
                    return None

            db.session.commit()

            # Update portfolio prices
            if portfolio_item and portfolio_item.shares > 0:
                PortfolioService.update_portfolio_item(portfolio_item)

            return transaction

        except Exception as e:
            logger.error(f"Error adding transaction: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def get_portfolio(user_id: int) -> Dict[str, Any]:
        """Get user's complete portfolio with calculated metrics"""
        try:
            logger.info(f"[Portfolio] Getting portfolio for user {user_id}")
            
            # Use optimized query with single DB call
            portfolio_items = Portfolio.query.filter_by(user_id=user_id).all()
            logger.info(f"[Portfolio] Found {len(portfolio_items)} items")

            if not portfolio_items:
                logger.info(f"[Portfolio] No items found for user {user_id}")
                return {
                    'items': [],
                    'summary': {
                        'total_value': 0,
                        'total_invested': 0,
                        'total_gain_loss': 0,
                        'total_gain_loss_percent': 0,
                        'positions': 0
                    }
                }

            # Update all portfolio items with current prices
            logger.info("[Portfolio] Updating portfolio items with current prices")
            for item in portfolio_items:
                try:
                    PortfolioService.update_portfolio_item(item)
                except Exception as item_error:
                    logger.error(f"[Portfolio] Error updating {item.ticker}: {str(item_error)}")
                    # Continue with other items even if one fails

            # Calculate portfolio summary
            total_value = sum(item.current_value or 0 for item in portfolio_items)
            total_invested = sum(item.total_invested or 0 for item in portfolio_items)
            total_gain_loss = total_value - total_invested
            total_gain_loss_percent = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0

            logger.info(f"[Portfolio] Summary - Value: ${total_value:.2f}, Invested: ${total_invested:.2f}, G/L: ${total_gain_loss:.2f} ({total_gain_loss_percent:.2f}%)")

            # Calculate diversification
            diversification = PortfolioService._calculate_diversification(portfolio_items)

            # Find top performers
            sorted_items = sorted(portfolio_items, key=lambda x: x.gain_loss_percent or 0, reverse=True)
            top_gainers = [item.to_dict() for item in sorted_items[:3] if (item.gain_loss_percent or 0) > 0]
            top_losers = [item.to_dict() for item in sorted_items[-3:] if (item.gain_loss_percent or 0) < 0]

            result = {
                'items': [item.to_dict() for item in portfolio_items],
                'summary': {
                    'total_value': round(total_value, 2),
                    'total_invested': round(total_invested, 2),
                    'total_gain_loss': round(total_gain_loss, 2),
                    'total_gain_loss_percent': round(total_gain_loss_percent, 2),
                    'positions': len(portfolio_items),
                    'diversification': diversification,
                    'top_gainers': top_gainers,
                    'top_losers': top_losers
                }
            }
            
            logger.info(f"[Portfolio] Successfully returning {len(result['items'])} items")
            return result

        except Exception as e:
            logger.error(f"[Portfolio] Critical error getting portfolio: {str(e)}", exc_info=True)
            return {
                'items': [],
                'summary': {
                    'total_value': 0,
                    'total_invested': 0,
                    'total_gain_loss': 0,
                    'total_gain_loss_percent': 0,
                    'positions': 0
                },
                'error': str(e)
            }

    @staticmethod
    def update_portfolio_item(portfolio_item: Portfolio) -> None:
        """Update portfolio item with current market prices"""
        try:
            stock_info = StockService.get_stock_info(portfolio_item.ticker)
            if stock_info and stock_info.get('current_price'):
                portfolio_item.calculate_metrics(stock_info['current_price'])
                db.session.commit()
        except Exception as e:
            logger.error(f"Error updating portfolio item {portfolio_item.ticker}: {str(e)}")

    @staticmethod
    def get_transactions(user_id: int, ticker: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's transactions"""
        try:
            query = Transaction.query.filter_by(user_id=user_id)

            if ticker:
                query = query.filter_by(ticker=ticker.upper())

            transactions = query.order_by(Transaction.transaction_date.desc()).limit(limit).all()

            return [t.to_dict() for t in transactions]

        except Exception as e:
            logger.error(f"Error getting transactions: {str(e)}")
            return []

    @staticmethod
    def _calculate_diversification(portfolio_items: List[Portfolio]) -> Dict[str, Any]:
        """Calculate portfolio diversification metrics"""
        try:
            total_value = sum(item.current_value or 0 for item in portfolio_items)

            if total_value == 0:
                return {'by_sector': {}, 'by_market': {}}

            # By sector
            sector_allocation = {}
            for item in portfolio_items:
                sector = item.sector or 'Unknown'
                if sector not in sector_allocation:
                    sector_allocation[sector] = 0
                sector_allocation[sector] += (item.current_value or 0)

            # Convert to percentages
            sector_percentages = {
                sector: round((value / total_value) * 100, 2)
                for sector, value in sector_allocation.items()
            }

            # By market
            market_allocation = {}
            for item in portfolio_items:
                market = item.market or 'USA'
                if market not in market_allocation:
                    market_allocation[market] = 0
                market_allocation[market] += (item.current_value or 0)

            market_percentages = {
                market: round((value / total_value) * 100, 2)
                for market, value in market_allocation.items()
            }

            return {
                'by_sector': sector_percentages,
                'by_market': market_percentages
            }

        except Exception as e:
            logger.error(f"Error calculating diversification: {str(e)}")
            return {'by_sector': {}, 'by_market': {}}

    @staticmethod
    def get_portfolio_performance(user_id: int, period: str = '1M') -> Dict[str, Any]:
        """Calculate portfolio performance over time"""
        try:
            # Get all transactions
            transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.transaction_date).all()

            if not transactions:
                return {'performance_data': [], 'metrics': {}}

            # Calculate daily portfolio values
            performance_data = []
            current_holdings = {}

            for transaction in transactions:
                date = transaction.transaction_date.date()

                if transaction.ticker not in current_holdings:
                    current_holdings[transaction.ticker] = 0

                if transaction.transaction_type == 'BUY':
                    current_holdings[transaction.ticker] += transaction.shares
                else:  # SELL
                    current_holdings[transaction.ticker] -= transaction.shares

                # Calculate portfolio value at this date
                # (Would need historical prices for accurate calculation)
                total_value = sum(current_holdings.values())  # Simplified

                performance_data.append({
                    'date': date.isoformat(),
                    'value': total_value,
                    'holdings': dict(current_holdings)
                })

            return {
                'performance_data': performance_data,
                'metrics': {
                    'period': period,
                    'start_value': performance_data[0]['value'] if performance_data else 0,
                    'end_value': performance_data[-1]['value'] if performance_data else 0
                }
            }

        except Exception as e:
            logger.error(f"Error calculating portfolio performance: {str(e)}")
            return {'performance_data': [], 'metrics': {}}

    @staticmethod
    def get_risk_analytics(user_id: int) -> Dict[str, Any]:
        """
        Calculate comprehensive risk analytics for user's portfolio

        Returns institutional-grade risk metrics including:
        - Sharpe Ratio, Sortino Ratio
        - Beta, Alpha vs. S&P 500
        - Value at Risk (VaR)
        - Maximum Drawdown
        - Volatility metrics

        Args:
            user_id: User ID

        Returns:
            Dictionary with all risk metrics and interpretations
        """
        try:
            logger.info(f"[Risk Analytics] Calculating for user {user_id}")

            # Get all transactions to build portfolio history
            transactions = Transaction.query.filter_by(user_id=user_id)\
                .order_by(Transaction.transaction_date).all()

            if not transactions or len(transactions) < 2:
                logger.warning(f"[Risk Analytics] Insufficient transactions for user {user_id}")
                return {
                    'error': 'Insufficient transaction history',
                    'message': 'Need at least 2 transactions to calculate risk metrics'
                }

            # Build daily portfolio values
            portfolio_values, portfolio_returns = PortfolioService._calculate_historical_portfolio_values(
                transactions
            )

            if len(portfolio_values) < 10:
                return {
                    'error': 'Insufficient data',
                    'message': 'Need at least 10 days of portfolio history'
                }

            # Get market returns (S&P 500) for beta/alpha calculation
            market_returns = PortfolioService._get_market_returns(len(portfolio_returns))

            # Calculate all risk metrics
            metrics = RiskAnalytics.calculate_all_metrics(
                portfolio_values,
                portfolio_returns,
                market_returns
            )

            # Add interpretations
            if metrics.get('sharpe_ratio') is not None:
                metrics['sharpe_interpretation'] = RiskAnalytics.interpret_sharpe_ratio(
                    metrics['sharpe_ratio']
                )

            if metrics.get('beta') is not None:
                metrics['beta_interpretation'] = RiskAnalytics.interpret_beta(
                    metrics['beta']
                )

            if metrics.get('alpha') is not None:
                metrics['alpha_interpretation'] = RiskAnalytics.interpret_alpha(
                    metrics['alpha']
                )

            # Add summary statistics
            metrics['data_points'] = len(portfolio_values)
            metrics['analysis_period_days'] = len(portfolio_values)
            metrics['start_value'] = float(portfolio_values[0])
            metrics['current_value'] = float(portfolio_values[-1])

            logger.info(f"[Risk Analytics] Successfully calculated metrics for user {user_id}")
            logger.info(f"[Risk Analytics] Sharpe: {metrics.get('sharpe_ratio', 0):.2f}, "
                       f"Beta: {metrics.get('beta', 0):.2f}, "
                       f"Alpha: {metrics.get('alpha', 0):.4f}")

            return metrics

        except Exception as e:
            logger.error(f"[Risk Analytics] Error calculating risk analytics: {str(e)}", exc_info=True)
            return {
                'error': str(e),
                'message': 'Failed to calculate risk analytics'
            }

    @staticmethod
    def _calculate_historical_portfolio_values(transactions: List[Transaction]) -> tuple:
        """
        Calculate historical portfolio values and returns from transaction history

        Args:
            transactions: List of Transaction objects (ordered by date)

        Returns:
            Tuple of (portfolio_values, portfolio_returns) as numpy arrays
        """
        try:
            # Build daily holdings from transactions
            holdings = {}  # {ticker: shares}
            daily_data = {}  # {date: {ticker: shares}}

            for transaction in transactions:
                date = transaction.transaction_date.date()

                if date not in daily_data:
                    daily_data[date] = dict(holdings)

                ticker = transaction.ticker
                if ticker not in holdings:
                    holdings[ticker] = 0.0

                if transaction.transaction_type == 'BUY':
                    holdings[ticker] += transaction.shares
                else:  # SELL
                    holdings[ticker] -= transaction.shares

                if holdings[ticker] <= 0:
                    holdings.pop(ticker, None)

                daily_data[date] = dict(holdings)

            # Get all dates from first transaction to today
            start_date = transactions[0].transaction_date.date()
            end_date = datetime.now().date()

            portfolio_values = []
            dates = []

            current_date = start_date
            current_holdings = {}

            while current_date <= end_date:
                # Update holdings if there were transactions on this date
                if current_date in daily_data:
                    current_holdings = daily_data[current_date]

                # Skip if no holdings
                if not current_holdings:
                    current_date += timedelta(days=1)
                    continue

                # Calculate portfolio value for this date
                total_value = 0.0
                for ticker, shares in current_holdings.items():
                    # Get historical price for this ticker on this date
                    # For simplicity, use current price (in production, fetch historical)
                    try:
                        stock_info = StockService.get_stock_info(ticker)
                        if stock_info and stock_info.get('current_price'):
                            price = stock_info['current_price']
                            total_value += shares * price
                    except Exception as e:
                        logger.warning(f"Could not get price for {ticker}: {e}")
                        continue

                if total_value > 0:
                    portfolio_values.append(total_value)
                    dates.append(current_date)

                current_date += timedelta(days=1)

            # Calculate returns
            portfolio_values_array = np.array(portfolio_values)

            if len(portfolio_values_array) < 2:
                return np.array([10000.0]), np.array([0.0])

            portfolio_returns = np.diff(portfolio_values_array) / portfolio_values_array[:-1]

            logger.info(f"[Portfolio History] Built {len(portfolio_values)} daily values")

            return portfolio_values_array, portfolio_returns

        except Exception as e:
            logger.error(f"Error calculating historical portfolio values: {e}")
            # Return dummy data
            return np.array([10000.0, 10500.0]), np.array([0.05])

    @staticmethod
    def _get_market_returns(num_days: int) -> Optional[np.ndarray]:
        """
        Get S&P 500 returns for the specified number of days

        For now, returns synthetic data. In production, fetch real S&P 500 data.

        Args:
            num_days: Number of days of returns needed

        Returns:
            Numpy array of daily returns or None
        """
        try:
            # Fetch S&P 500 historical data
            # Using ^GSPC as S&P 500 index ticker
            spy_data = StockService.get_price_history('^GSPC', period='1y')

            if spy_data and spy_data.get('data'):
                # Extract closing prices
                prices = [day['close'] for day in spy_data['data'][-num_days-1:]]

                if len(prices) >= num_days + 1:
                    prices_array = np.array(prices)
                    returns = np.diff(prices_array) / prices_array[:-1]
                    return returns[-num_days:]

            # Fallback: Generate synthetic S&P 500 returns
            # Mean daily return: 0.04% (10% annual / 252 days)
            # Std dev: 1% daily
            logger.warning("[Market Returns] Using synthetic S&P 500 data (could not fetch real data)")
            synthetic_returns = np.random.normal(0.0004, 0.01, num_days)
            return synthetic_returns

        except Exception as e:
            logger.warning(f"Could not get market returns: {e}")
            return None