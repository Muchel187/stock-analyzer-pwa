from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    # Settings
    preferred_currency = db.Column(db.String(3), default='USD')
    email_notifications = db.Column(db.Boolean, default=True)
    push_notifications = db.Column(db.Boolean, default=False)
    dashboard_layout = db.Column(db.JSON, default=lambda: {
        'widgets': ['portfolio', 'watchlist', 'recommendations'],
        'layout': 'default'
    })

    # Relationships
    portfolio = db.relationship('Portfolio', backref='user', lazy='dynamic',
                                cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic',
                                    cascade='all, delete-orphan')
    watchlist = db.relationship('Watchlist', backref='user', lazy='dynamic',
                                 cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='user', lazy='dynamic',
                              cascade='all, delete-orphan')

    def set_password(self, password):
        """Set hashed password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches"""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'preferred_currency': self.preferred_currency,
            'email_notifications': self.email_notifications,
            'push_notifications': self.push_notifications,
            'dashboard_layout': self.dashboard_layout
        }

    def __repr__(self):
        return f'<User {self.username}>'