#!/usr/bin/env python3
"""
Database Integrity Check Script
Verifies database structure and data consistency
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Portfolio, Transaction, Watchlist, Alert, StockCache
from sqlalchemy import inspect

def check_database():
    app = create_app()
    with app.app_context():
        print("🗄️  Checking Database Integrity...\n")
        
        # Check tables exist
        inspector = inspect(db.engine)
        expected_tables = ['users', 'portfolios', 'transactions', 'watchlists', 'alerts', 'stock_cache']
        existing_tables = inspector.get_table_names()
        
        print("📋 Table Check:")
        all_tables_exist = True
        for table in expected_tables:
            exists = table in existing_tables
            print(f"  {'✅' if exists else '❌'} {table}")
            if not exists:
                all_tables_exist = False
        
        if not all_tables_exist:
            print("\n⚠️  Some tables are missing! Run migrations:")
            print("   flask db upgrade")
            return False
        
        # Check data counts
        print("\n📊 Data Counts:")
        user_count = User.query.count()
        portfolio_count = Portfolio.query.count()
        transaction_count = Transaction.query.count()
        watchlist_count = Watchlist.query.count()
        alert_count = Alert.query.count()
        cache_count = StockCache.query.count()
        
        print(f"  Users: {user_count}")
        print(f"  Portfolios: {portfolio_count}")
        print(f"  Transactions: {transaction_count}")
        print(f"  Watchlist Items: {watchlist_count}")
        print(f"  Alerts: {alert_count}")
        print(f"  Cached Stocks: {cache_count}")
        
        # Sample user data
        if user_count > 0:
            print("\n👤 Sample Users:")
            for user in User.query.limit(3).all():
                print(f"  - {user.username} ({user.email}) - ID: {user.id}")
        
        # Check for orphaned records
        print("\n🔍 Checking for Orphaned Records:")
        
        issues_found = False
        
        # Portfolios without users
        orphaned_portfolios = db.session.query(Portfolio).filter(
            ~Portfolio.user_id.in_(db.session.query(User.id))
        ).count()
        status = '❌' if orphaned_portfolios > 0 else '✅'
        print(f"  {status} Orphaned Portfolios: {orphaned_portfolios}")
        if orphaned_portfolios > 0:
            issues_found = True
        
        # Transactions without users
        orphaned_transactions = db.session.query(Transaction).filter(
            ~Transaction.user_id.in_(db.session.query(User.id))
        ).count()
        status = '❌' if orphaned_transactions > 0 else '✅'
        print(f"  {status} Orphaned Transactions: {orphaned_transactions}")
        if orphaned_transactions > 0:
            issues_found = True
        
        # Watchlist items without users
        orphaned_watchlist = db.session.query(Watchlist).filter(
            ~Watchlist.user_id.in_(db.session.query(User.id))
        ).count()
        status = '❌' if orphaned_watchlist > 0 else '✅'
        print(f"  {status} Orphaned Watchlist Items: {orphaned_watchlist}")
        if orphaned_watchlist > 0:
            issues_found = True
        
        # Check for null values in critical fields
        print("\n🚨 Checking for NULL values in critical fields:")
        
        null_checks = [
            ("Portfolios with NULL user_id", Portfolio.query.filter(Portfolio.user_id == None).count()),
            ("Transactions with NULL user_id", Transaction.query.filter(Transaction.user_id == None).count()),
            ("Transactions with NULL ticker", Transaction.query.filter(Transaction.ticker == None).count()),
            ("Transactions with NULL shares", Transaction.query.filter(Transaction.shares == None).count()),
            ("Transactions with NULL price", Transaction.query.filter(Transaction.price == None).count()),
            ("Watchlist with NULL user_id", Watchlist.query.filter(Watchlist.user_id == None).count()),
            ("Watchlist with NULL ticker", Watchlist.query.filter(Watchlist.ticker == None).count()),
        ]
        
        for check_name, count in null_checks:
            status = '❌' if count > 0 else '✅'
            print(f"  {status} {check_name}: {count}")
            if count > 0:
                issues_found = True
        
        # Check portfolio-transaction consistency
        print("\n🔗 Checking Data Consistency:")
        
        # Count portfolios with each user
        if portfolio_count > 0:
            print(f"  Portfolios: {portfolio_count}")
            print(f"  Transactions: {transaction_count}")
        
        # Sample some transactions
        if transaction_count > 0:
            print("\n📝 Sample Transactions:")
            for trans in Transaction.query.limit(5).all():
                print(f"  - {trans.ticker}: {trans.transaction_type} {trans.shares} @ ${trans.price} (User: {trans.user_id})")
        
        print("\n" + "="*80)
        
        if issues_found:
            print("⚠️  Database integrity issues found - review above")
            return False
        else:
            print("✅ Database integrity check passed - no issues found")
            return True

if __name__ == "__main__":
    try:
        success = check_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error during database check: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
