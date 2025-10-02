"""
Admin Service - Handles all admin-related business logic
"""
from typing import Dict, List, Any, Optional
from app import db
from app.models import User, Portfolio, Transaction, Watchlist, Alert
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

class AdminService:
    """Service for admin operations"""

    @staticmethod
    def get_users(page: int = 1, per_page: int = 50, search: str = None,
                  is_admin: bool = None) -> Dict[str, Any]:
        """Get paginated list of users with optional filters"""
        try:
            query = User.query

            # Apply search filter
            if search:
                query = query.filter(
                    db.or_(
                        User.username.ilike(f'%{search}%'),
                        User.email.ilike(f'%{search}%')
                    )
                )

            # Apply admin filter
            if is_admin is not None:
                query = query.filter(User.is_admin == is_admin)

            # Order by creation date (newest first)
            query = query.order_by(User.created_at.desc())

            # Paginate
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            # Build user data with stats
            users_data = []
            for user in pagination.items:
                # Get portfolio value
                portfolio_value = db.session.query(
                    func.sum(Portfolio.total_invested)
                ).filter_by(user_id=user.id).scalar() or 0

                # Get counts
                portfolio_count = Portfolio.query.filter_by(user_id=user.id).count()
                watchlist_count = Watchlist.query.filter_by(user_id=user.id).count()
                alerts_count = Alert.query.filter_by(user_id=user.id).count()

                user_dict = user.to_dict()
                user_dict.update({
                    'portfolio_count': portfolio_count,
                    'total_portfolio_value': float(portfolio_value),
                    'watchlist_count': watchlist_count,
                    'alerts_count': alerts_count
                })
                users_data.append(user_dict)

            return {
                'users': users_data,
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total_pages': pagination.pages
            }

        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            raise

    @staticmethod
    def get_user_details(user_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed user information"""
        try:
            user = db.session.get(User, user_id)
            if not user:
                return None

            # Get portfolio stats
            portfolio_positions = Portfolio.query.filter_by(user_id=user_id).all()
            total_value = sum(p.total_invested for p in portfolio_positions)
            total_invested = sum(p.total_invested for p in portfolio_positions)

            # Calculate total return (simplified)
            total_return = 0  # Would need current prices to calculate actual return

            # Get counts
            transactions_count = Transaction.query.filter_by(user_id=user_id).count()
            watchlist_count = Watchlist.query.filter_by(user_id=user_id).count()
            alerts_count = Alert.query.filter_by(user_id=user_id).count()

            user_data = user.to_dict()
            user_data.update({
                'portfolio': {
                    'positions': len(portfolio_positions),
                    'total_value': float(total_value),
                    'total_invested': float(total_invested),
                    'total_return': float(total_return)
                },
                'watchlist_count': watchlist_count,
                'alerts_count': alerts_count,
                'transactions_count': transactions_count
            })

            return user_data

        except Exception as e:
            logger.error(f"Error getting user details for {user_id}: {str(e)}")
            raise

    @staticmethod
    def update_user(user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user information"""
        try:
            user = db.session.get(User, user_id)
            if not user:
                return None

            # Update allowed fields
            if 'username' in data:
                # Check if username is already taken
                existing = User.query.filter(
                    User.username == data['username'],
                    User.id != user_id
                ).first()
                if existing:
                    raise ValueError("Username already taken")
                user.username = data['username']

            if 'email' in data:
                # Check if email is already taken
                existing = User.query.filter(
                    User.email == data['email'],
                    User.id != user_id
                ).first()
                if existing:
                    raise ValueError("Email already taken")
                user.email = data['email']

            db.session.commit()
            return user.to_dict()

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise

    @staticmethod
    def delete_user(user_id: int, admin_id: int) -> bool:
        """Delete user account (with safety checks)"""
        try:
            # Prevent self-deletion
            if user_id == admin_id:
                raise ValueError("Cannot delete your own account")

            # Check if user exists
            user = db.session.get(User, user_id)
            if not user:
                return False

            # Check if this is the last admin
            if user.is_admin:
                admin_count = User.query.filter_by(is_admin=True).count()
                if admin_count <= 1:
                    raise ValueError("Cannot delete the last admin account")

            # Delete user (cascade will handle related records)
            db.session.delete(user)
            db.session.commit()

            logger.info(f"User {user_id} deleted by admin {admin_id}")
            return True

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise

    @staticmethod
    def toggle_admin_status(user_id: int, admin_id: int) -> Optional[Dict[str, Any]]:
        """Toggle user's admin status"""
        try:
            # Prevent self-demotion
            if user_id == admin_id:
                raise ValueError("Cannot change your own admin status")

            user = db.session.get(User, user_id)
            if not user:
                return None

            # Check if demoting the last admin
            if user.is_admin:
                admin_count = User.query.filter_by(is_admin=True).count()
                if admin_count <= 1:
                    raise ValueError("Cannot remove the last admin")

            # Toggle admin status
            user.is_admin = not user.is_admin
            db.session.commit()

            action = "promoted to" if user.is_admin else "demoted from"
            logger.info(f"User {user_id} {action} admin by admin {admin_id}")

            return {
                'success': True,
                'message': f"User {action} admin",
                'user': user.to_dict()
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error toggling admin status for {user_id}: {str(e)}")
            raise

    @staticmethod
    def get_system_stats() -> Dict[str, Any]:
        """Get system-wide statistics"""
        try:
            # User stats
            total_users = User.query.count()
            admin_count = User.query.filter_by(is_admin=True).count()

            # Activity stats (last 24 hours)
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            active_today = User.query.filter(User.last_login >= yesterday).count()

            # Activity stats (last 7 days)
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            active_week = User.query.filter(User.last_login >= week_ago).count()
            new_users_week = User.query.filter(User.created_at >= week_ago).count()

            # Content stats
            total_portfolios = Portfolio.query.count()
            total_transactions = Transaction.query.count()
            total_watchlist = Watchlist.query.count()
            total_alerts = Alert.query.count()

            return {
                'total_users': total_users,
                'active_users_today': active_today,
                'active_users_week': active_week,
                'admin_count': admin_count,
                'new_users_week': new_users_week,
                'total_portfolios': total_portfolios,
                'total_transactions': total_transactions,
                'total_watchlist_items': total_watchlist,
                'total_alerts': total_alerts,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting system stats: {str(e)}")
            raise