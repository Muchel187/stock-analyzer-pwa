#!/usr/bin/env python3
"""
Database initialization script for production deployment
Run this after deploying to Render to set up the database
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User, Portfolio, Transaction, Watchlist, Alert, StockCache

def init_db():
    """Initialize database with tables"""
    print("Initializing database...")
    
    # Create app with production config
    app = create_app('production')
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully")
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@aktieninspektor.com'
            )
            admin.set_password('change_this_password_immediately')
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created (username: admin, password: change_this_password_immediately)")
            print("⚠️  WICHTIG: Ändere das Admin-Passwort sofort!")
        else:
            print("✓ Admin user already exists")
        
        print("\n✅ Database initialization complete!")
        print("\nNext steps:")
        print("1. Login with admin credentials")
        print("2. Change admin password immediately")
        print("3. Create your user account")
        print("4. Test all features")

if __name__ == '__main__':
    init_db()
