from datetime import datetime
from app import db

class Alert(db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticker = db.Column(db.String(20), nullable=False, index=True)
    alert_type = db.Column(db.String(20), nullable=False)  # PRICE_ABOVE, PRICE_BELOW, PERCENT_CHANGE
    target_value = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    is_triggered = db.Column(db.Boolean, default=False)
    triggered_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_checked = db.Column(db.DateTime)

    # Notification settings
    notify_email = db.Column(db.Boolean, default=True)
    notify_push = db.Column(db.Boolean, default=False)
    notification_sent = db.Column(db.Boolean, default=False)

    # Additional context
    notes = db.Column(db.Text)
    company_name = db.Column(db.String(255))

    def check_trigger(self, current_price):
        """Check if alert should be triggered based on current price"""
        if not self.is_active or self.is_triggered:
            return False

        self.current_value = current_price
        self.last_checked = datetime.utcnow()

        triggered = False
        if self.alert_type == 'PRICE_ABOVE':
            triggered = current_price >= self.target_value
        elif self.alert_type == 'PRICE_BELOW':
            triggered = current_price <= self.target_value
        elif self.alert_type == 'PERCENT_CHANGE':
            # Requires baseline price stored in notes or separate field
            pass

        if triggered:
            self.is_triggered = True
            self.triggered_at = datetime.utcnow()
            return True

        return False

    def reset(self):
        """Reset a triggered alert"""
        self.is_triggered = False
        self.triggered_at = None
        self.notification_sent = False

    def to_dict(self):
        """Convert alert to dictionary"""
        return {
            'id': self.id,
            'ticker': self.ticker,
            'company_name': self.company_name,
            'alert_type': self.alert_type,
            'target_value': round(self.target_value, 2) if self.target_value else 0,
            'current_value': round(self.current_value, 2) if self.current_value else None,
            'is_active': self.is_active,
            'is_triggered': self.is_triggered,
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'notify_email': self.notify_email,
            'notify_push': self.notify_push,
            'notes': self.notes
        }

    def __repr__(self):
        return f'<Alert {self.ticker} {self.alert_type} {self.target_value}>'