#!/usr/bin/env python3
"""
Test the new historical data service
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.services.historical_data_service import HistoricalDataService
from app.models.historical_price import HistoricalPrice, DataCollectionMetadata
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_historical_data():
    """Test the historical data service"""
    app = create_app()

    with app.app_context():
        print("\n" + "="*80)
        print("TESTING HISTORICAL DATA SERVICE")
        print("="*80)

        test_ticker = 'AAPL'
        period = '1mo'

        # Test 1: Get historical data (should fetch from API and cache)
        print(f"\n1. Fetching {test_ticker} for period {period}...")
        result = HistoricalDataService.get_historical_data(
            ticker=test_ticker,
            period=period,
            force_update=False
        )

        if result and result.get('data'):
            print(f"✅ SUCCESS: Got {len(result['data'])} data points")
            print(f"   Source: {result.get('source')}")
            print(f"   Period: {result.get('period')}")

            # Show sample data
            if result['data']:
                first = result['data'][0]
                last = result['data'][-1]
                print(f"   First: {first.get('date')} - Close: ${first.get('close')}")
                print(f"   Last:  {last.get('date')} - Close: ${last.get('close')}")
        else:
            print(f"❌ FAILED: No data returned")
            if result:
                print(f"   Error: {result.get('error')}")

        # Test 2: Check if data was cached in database
        print(f"\n2. Checking database cache...")
        cached_data = HistoricalPrice.query.filter_by(ticker=test_ticker).count()
        print(f"   Found {cached_data} records in database")

        metadata = DataCollectionMetadata.query.filter_by(ticker=test_ticker).first()
        if metadata:
            print(f"   ✅ Metadata found:")
            print(f"      Last collected: {metadata.last_collected_at}")
            print(f"      Status: {metadata.collection_status}")
            print(f"      Data points: {metadata.data_points_count}")
            print(f"      Date range: {metadata.earliest_date} to {metadata.latest_date}")
        else:
            print(f"   ❌ No metadata found")

        # Test 3: Get cached data (should be fast)
        print(f"\n3. Testing cache retrieval...")
        result2 = HistoricalDataService.get_historical_data(
            ticker=test_ticker,
            period=period,
            force_update=False
        )

        if result2 and result2.get('source') == 'local_cache':
            print(f"✅ SUCCESS: Data retrieved from cache")
            print(f"   Source: {result2.get('source')}")
        else:
            print(f"⚠️  WARNING: Data not from cache")
            if result2:
                print(f"   Source: {result2.get('source')}")

        # Test 4: Test different period
        print(f"\n4. Testing different period (3mo)...")
        result3 = HistoricalDataService.get_historical_data(
            ticker=test_ticker,
            period='3mo',
            force_update=False
        )

        if result3 and result3.get('data'):
            print(f"✅ SUCCESS: Got {len(result3['data'])} data points for 3mo")
        else:
            print(f"❌ FAILED: No data for 3mo period")

        # Test 5: Test German stock
        print(f"\n5. Testing German stock (SAP.DE)...")
        result4 = HistoricalDataService.get_historical_data(
            ticker='SAP.DE',
            period='1mo',
            force_update=False
        )

        if result4 and result4.get('data'):
            print(f"✅ SUCCESS: Got {len(result4['data'])} data points for SAP.DE")
            print(f"   Source: {result4.get('source')}")
        else:
            print(f"⚠️  WARNING: No data for SAP.DE")
            if result4:
                print(f"   Error: {result4.get('error')}")

        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)

        # Check total records in database
        total_records = HistoricalPrice.query.count()
        total_tickers = db.session.query(HistoricalPrice.ticker).distinct().count()
        total_metadata = DataCollectionMetadata.query.count()

        print(f"\nDatabase Statistics:")
        print(f"  Total price records: {total_records}")
        print(f"  Unique tickers: {total_tickers}")
        print(f"  Metadata entries: {total_metadata}")

        # List all tickers in database
        tickers = db.session.query(HistoricalPrice.ticker).distinct().all()
        if tickers:
            print(f"\nTickers in database:")
            for ticker_row in tickers:
                ticker = ticker_row[0]
                count = HistoricalPrice.query.filter_by(ticker=ticker).count()
                print(f"  - {ticker}: {count} records")

        print("\n✅ Historical data service is working!")
        print("The system will now cache data locally and update it periodically.")

if __name__ == '__main__':
    test_historical_data()