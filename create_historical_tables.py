#!/usr/bin/env python3
"""
Create historical price tables in the database
Run this script to set up the new tables for historical price caching
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.historical_price import HistoricalPrice, DataCollectionMetadata
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create historical price tables"""
    app = create_app()

    with app.app_context():
        try:
            # Create all tables defined in models
            logger.info("Creating historical price tables...")
            db.create_all()

            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            if 'historical_prices' in tables:
                logger.info("✅ Table 'historical_prices' created successfully")
            else:
                logger.error("❌ Table 'historical_prices' was not created")

            if 'data_collection_metadata' in tables:
                logger.info("✅ Table 'data_collection_metadata' created successfully")
            else:
                logger.error("❌ Table 'data_collection_metadata' was not created")

            # Test inserting a sample record
            test_metadata = DataCollectionMetadata(
                ticker='TEST',
                priority=0,
                is_active=False
            )
            db.session.add(test_metadata)
            db.session.commit()

            # Remove test record
            db.session.delete(test_metadata)
            db.session.commit()

            logger.info("✅ Tables are working correctly")

            return True

        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            return False

if __name__ == '__main__':
    success = create_tables()
    if success:
        print("\n✅ Historical price tables created successfully!")
        print("The app can now cache historical data locally.")
    else:
        print("\n❌ Failed to create historical price tables")
        print("Please check the error messages above.")
        sys.exit(1)