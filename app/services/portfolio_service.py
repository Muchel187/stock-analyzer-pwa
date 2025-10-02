from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from sqlalchemy import func
from app import db
from app.models import Portfolio, Transaction, User
from app.services.stock_service import StockService
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
            portfolio_items = Portfolio.query.filter_by(user_id=user_id).all()

            if not portfolio_items:
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
            for item in portfolio_items:
                PortfolioService.update_portfolio_item(item)

            # Calculate portfolio summary
            total_value = sum(item.current_value or 0 for item in portfolio_items)
            total_invested = sum(item.total_invested or 0 for item in portfolio_items)
            total_gain_loss = total_value - total_invested
            total_gain_loss_percent = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0

            # Calculate diversification
            diversification = PortfolioService._calculate_diversification(portfolio_items)

            # Find top performers
            sorted_items = sorted(portfolio_items, key=lambda x: x.gain_loss_percent or 0, reverse=True)
            top_gainers = [item.to_dict() for item in sorted_items[:3] if (item.gain_loss_percent or 0) > 0]
            top_losers = [item.to_dict() for item in sorted_items[-3:] if (item.gain_loss_percent or 0) < 0]

            return {
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

        except Exception as e:
            logger.error(f"Error getting portfolio: {str(e)}")
            return {
                'items': [],
                'summary': {},
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