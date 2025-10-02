from typing import List, Dict, Any, Optional
from datetime import datetime
from app import db, mail
from app.models import Alert, User
from app.services.stock_service import StockService
from flask_mail import Message
import logging

logger = logging.getLogger(__name__)

class AlertService:
    """Service for managing price alerts"""

    @staticmethod
    def create_alert(user_id: int, alert_data: Dict[str, Any]) -> Optional[Alert]:
        """Create a new price alert"""
        try:
            # Validate ticker
            stock_info = StockService.get_stock_info(alert_data['ticker'])
            if not stock_info:
                return None

            alert = Alert(
                user_id=user_id,
                ticker=alert_data['ticker'].upper(),
                alert_type=alert_data['alert_type'],
                target_value=float(alert_data['target_value']),
                current_value=stock_info.get('current_price'),
                company_name=stock_info.get('company_name'),
                notes=alert_data.get('notes', ''),
                notify_email=alert_data.get('notify_email', True),
                notify_push=alert_data.get('notify_push', False)
            )

            db.session.add(alert)
            db.session.commit()

            return alert

        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def check_alerts() -> List[Alert]:
        """Check all active alerts and trigger if conditions are met"""
        triggered_alerts = []

        try:
            active_alerts = Alert.query.filter_by(is_active=True, is_triggered=False).all()

            # Group alerts by ticker for efficiency
            alerts_by_ticker = {}
            for alert in active_alerts:
                if alert.ticker not in alerts_by_ticker:
                    alerts_by_ticker[alert.ticker] = []
                alerts_by_ticker[alert.ticker].append(alert)

            # Check each ticker
            for ticker, alerts in alerts_by_ticker.items():
                stock_info = StockService.get_stock_info(ticker)
                if stock_info and stock_info.get('current_price'):
                    current_price = stock_info['current_price']

                    for alert in alerts:
                        if alert.check_trigger(current_price):
                            triggered_alerts.append(alert)
                            AlertService._send_alert_notification(alert)

            db.session.commit()

        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
            db.session.rollback()

        return triggered_alerts

    @staticmethod
    def _send_alert_notification(alert: Alert) -> None:
        """Send notification for triggered alert"""
        try:
            user = db.session.get(User, alert.user_id)
            if not user:
                return

            if alert.notify_email and user.email_notifications:
                AlertService._send_email_notification(user, alert)

            if alert.notify_push and user.push_notifications:
                AlertService._send_push_notification(user, alert)

            alert.notification_sent = True
            db.session.commit()

        except Exception as e:
            logger.error(f"Error sending notification for alert {alert.id}: {str(e)}")

    @staticmethod
    def _send_email_notification(user: User, alert: Alert) -> None:
        """Send email notification"""
        try:
            subject = f"Price Alert Triggered: {alert.ticker}"

            body = f"""
Hello {user.username},

Your price alert for {alert.company_name} ({alert.ticker}) has been triggered!

Alert Details:
- Type: {alert.alert_type}
- Target: ${alert.target_value:.2f}
- Current Price: ${alert.current_value:.2f}
- Notes: {alert.notes or 'N/A'}

Visit your dashboard to view more details and manage your alerts.

Best regards,
Stock Analyzer Team
            """

            msg = Message(
                subject=subject,
                recipients=[user.email],
                body=body
            )

            mail.send(msg)
            logger.info(f"Email notification sent to {user.email} for alert {alert.id}")

        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")

    @staticmethod
    def _send_push_notification(user: User, alert: Alert) -> None:
        """Send push notification (placeholder for web push implementation)"""
        # This would integrate with web push notifications
        # For now, just log the attempt
        logger.info(f"Push notification would be sent to user {user.id} for alert {alert.id}")

    @staticmethod
    def get_user_alerts(user_id: int, active_only: bool = False) -> List[Dict[str, Any]]:
        """Get all alerts for a user"""
        try:
            query = Alert.query.filter_by(user_id=user_id)

            if active_only:
                query = query.filter_by(is_active=True)

            alerts = query.order_by(Alert.created_at.desc()).all()

            return [alert.to_dict() for alert in alerts]

        except Exception as e:
            logger.error(f"Error getting user alerts: {str(e)}")
            return []

    @staticmethod
    def update_alert(alert_id: int, user_id: int, updates: Dict[str, Any]) -> Optional[Alert]:
        """Update an existing alert"""
        try:
            alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()

            if not alert:
                return None

            # Update allowed fields
            if 'target_value' in updates:
                alert.target_value = float(updates['target_value'])
            if 'alert_type' in updates:
                alert.alert_type = updates['alert_type']
            if 'is_active' in updates:
                alert.is_active = updates['is_active']
            if 'notify_email' in updates:
                alert.notify_email = updates['notify_email']
            if 'notify_push' in updates:
                alert.notify_push = updates['notify_push']
            if 'notes' in updates:
                alert.notes = updates['notes']

            # Reset if reactivating
            if updates.get('is_active') and alert.is_triggered:
                alert.reset()

            db.session.commit()
            return alert

        except Exception as e:
            logger.error(f"Error updating alert: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def delete_alert(alert_id: int, user_id: int) -> bool:
        """Delete an alert"""
        try:
            alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()

            if not alert:
                return False

            db.session.delete(alert)
            db.session.commit()
            return True

        except Exception as e:
            logger.error(f"Error deleting alert: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def get_alert_statistics(user_id: int) -> Dict[str, Any]:
        """Get statistics about user's alerts"""
        try:
            alerts = Alert.query.filter_by(user_id=user_id).all()

            return {
                'total_alerts': len(alerts),
                'active_alerts': len([a for a in alerts if a.is_active]),
                'triggered_alerts': len([a for a in alerts if a.is_triggered]),
                'alerts_by_type': {
                    'PRICE_ABOVE': len([a for a in alerts if a.alert_type == 'PRICE_ABOVE']),
                    'PRICE_BELOW': len([a for a in alerts if a.alert_type == 'PRICE_BELOW']),
                    'PERCENT_CHANGE': len([a for a in alerts if a.alert_type == 'PERCENT_CHANGE'])
                }
            }

        except Exception as e:
            logger.error(f"Error getting alert statistics: {str(e)}")
            return {}