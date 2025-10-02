#!/usr/bin/env python3
"""
Populate historical data for priority stocks
Run this script to pre-populate the database with historical data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.services.historical_data_service import HistoricalDataService
from app.models.historical_price import HistoricalPrice, DataCollectionMetadata
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_historical_data():
    """Populate historical data for important stocks"""
    app = create_app()

    with app.app_context():
        print("\n" + "="*80)
        print("POPULATING HISTORICAL DATA")
        print("="*80)

        # Priority stocks to populate
        priority_stocks = [
            # US Tech
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA',
            # US Index ETFs
            'SPY', 'QQQ', 'DIA',
            # German stocks
            'SAP.DE', 'SIE.DE', 'BMW.DE',
        ]

        success_count = 0
        failed_count = 0
        skipped_count = 0

        for ticker in priority_stocks:
            print(f"\nProcessing {ticker}...")

            # Check if already has recent data
            metadata = DataCollectionMetadata.query.filter_by(ticker=ticker).first()
            if metadata and metadata.last_successful_collection:
                age = (datetime.now() - metadata.last_successful_collection).total_seconds()
                if age < 3600:  # Less than 1 hour old
                    print(f"  ⏭️  SKIPPED: Recently updated")
                    skipped_count += 1
                    continue

            try:
                # Try to get 3 months of data
                result = HistoricalDataService.get_historical_data(
                    ticker=ticker,
                    period='3mo',
                    force_update=True
                )

                if result and result.get('data'):
                    success_count += 1
                    print(f"  ✅ SUCCESS: {len(result['data'])} data points from {result.get('source')}")

                    # Show date range
                    data = result['data']
                    if data:
                        dates = [d.get('date') for d in data if d.get('date')]
                        if dates:
                            print(f"     Date range: {min(dates)} to {max(dates)}")
                else:
                    failed_count += 1
                    print(f"  ❌ FAILED: {result.get('error', 'Unknown error')}")

            except Exception as e:
                failed_count += 1
                print(f"  ❌ ERROR: {str(e)}")

            # Rate limiting - be nice to APIs
            time.sleep(3)

        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)

        print(f"\nResults:")
        print(f"  ✅ Success: {success_count}")
        print(f"  ❌ Failed: {failed_count}")
        print(f"  ⏭️  Skipped: {skipped_count}")

        # Database statistics
        total_records = HistoricalPrice.query.count()
        total_tickers = db.session.query(HistoricalPrice.ticker).distinct().count()

        print(f"\nDatabase Statistics:")
        print(f"  Total price records: {total_records}")
        print(f"  Unique tickers: {total_tickers}")

        # Show all tickers with data
        tickers_with_data = db.session.query(
            HistoricalPrice.ticker,
            db.func.count(HistoricalPrice.id),
            db.func.min(HistoricalPrice.date),
            db.func.max(HistoricalPrice.date)
        ).group_by(HistoricalPrice.ticker).all()

        if tickers_with_data:
            print(f"\nTickers in database:")
            for ticker, count, min_date, max_date in tickers_with_data:
                print(f"  {ticker}: {count} records ({min_date} to {max_date})")

        print("\n✅ Data population complete!")
        print("The historical data service will continue updating data periodically.")

from datetime import datetime

if __name__ == '__main__':
    populate_historical_data()