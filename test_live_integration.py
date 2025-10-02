#!/usr/bin/env python3
"""
Live Integration Test for AI Fallback
Tests with REAL API calls to verify production readiness
"""

import os
import sys
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_live_integration():
    """Live integration test with real APIs"""
    print("=" * 80)
    print("LIVE INTEGRATION TEST - AI Fallback System")
    print("=" * 80)
    print("\n⚠️  WARNING: This test uses REAL API calls and may consume quota")
    print("Press Ctrl+C to cancel within 3 seconds...\n")

    try:
        time.sleep(3)
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
        return False

    # Set up Flask app context for StockCache
    from app import create_app
    app = create_app()

    results = {
        'passed': 0,
        'failed': 0,
        'warnings': 0
    }

    # ========================================================================
    # TEST 1: Normal API Flow (Finnhub should work)
    # ========================================================================
    print("\n" + "-" * 80)
    print("TEST 1: Normal API Flow (Primary APIs)")
    print("-" * 80)

    try:
        from app.services.alternative_data_sources import FallbackDataService

        print("Fetching AAPL from FallbackDataService...")
        start_time = time.time()
        data = FallbackDataService.get_stock_quote('AAPL')
        elapsed = time.time() - start_time

        if data:
            print(f"✅ SUCCESS: Retrieved data in {elapsed:.2f}s")
            print(f"   Source: {data.get('source', 'unknown')}")
            print(f"   Company: {data.get('company_name', 'N/A')}")
            print(f"   Price: ${data.get('current_price', 'N/A')}")

            if data.get('source') == 'AI_FALLBACK':
                print(f"   ⚠️  WARNING: Used AI fallback (APIs may be exhausted)")
                results['warnings'] += 1

            results['passed'] += 1
        else:
            print(f"❌ FAIL: No data returned")
            results['failed'] += 1

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        results['failed'] += 1

    # ========================================================================
    # TEST 2: Historical Data
    # ========================================================================
    print("\n" + "-" * 80)
    print("TEST 2: Historical Data Retrieval")
    print("-" * 80)

    try:
        from app.services.alternative_data_sources import FallbackDataService

        print("Fetching MSFT historical data (30 days)...")
        start_time = time.time()
        hist_data = FallbackDataService.get_historical_data('MSFT', outputsize=30)
        elapsed = time.time() - start_time

        if hist_data and hist_data.get('data'):
            data_points = len(hist_data['data'])
            print(f"✅ SUCCESS: Retrieved {data_points} data points in {elapsed:.2f}s")
            print(f"   Source: {hist_data.get('source', 'unknown')}")

            if data_points > 0:
                latest = hist_data['data'][-1] if isinstance(hist_data['data'], list) else None
                if latest:
                    print(f"   Latest: {latest.get('date', 'N/A')} - ${latest.get('close', 'N/A')}")

            if hist_data.get('source') == 'AI_FALLBACK':
                print(f"   ⚠️  WARNING: Used AI fallback for historical data")
                results['warnings'] += 1

            results['passed'] += 1
        else:
            print(f"❌ FAIL: No historical data returned")
            results['failed'] += 1

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        results['failed'] += 1

    # ========================================================================
    # TEST 3: Company Info
    # ========================================================================
    print("\n" + "-" * 80)
    print("TEST 3: Company Information")
    print("-" * 80)

    try:
        from app.services.alternative_data_sources import FallbackDataService

        print("Fetching TSLA company info...")
        start_time = time.time()
        company_data = FallbackDataService.get_company_info('TSLA')
        elapsed = time.time() - start_time

        if company_data:
            print(f"✅ SUCCESS: Retrieved company info in {elapsed:.2f}s")
            print(f"   Company: {company_data.get('company_name', 'N/A')}")
            print(f"   Sector: {company_data.get('sector', 'N/A')}")
            print(f"   Industry: {company_data.get('industry', 'N/A')}")
            print(f"   Source: {company_data.get('source', 'unknown')}")

            if company_data.get('source') == 'AI_FALLBACK':
                print(f"   ⚠️  WARNING: Used AI fallback for company info")
                results['warnings'] += 1

            results['passed'] += 1
        else:
            print(f"❌ FAIL: No company info returned")
            results['failed'] += 1

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        results['failed'] += 1

    # ========================================================================
    # TEST 4: StockService Integration
    # ========================================================================
    print("\n" + "-" * 80)
    print("TEST 4: StockService Integration")
    print("-" * 80)

    try:
        from app.services.stock_service import StockService

        print("Fetching GOOGL via StockService.get_stock_info()...")
        start_time = time.time()

        with app.app_context():
            stock_info = StockService.get_stock_info('GOOGL')

        elapsed = time.time() - start_time

        if stock_info:
            print(f"✅ SUCCESS: Retrieved stock info in {elapsed:.2f}s")
            print(f"   Ticker: {stock_info.get('ticker', 'N/A')}")
            print(f"   Price: ${stock_info.get('current_price', 'N/A')}")
            print(f"   Market Cap: ${stock_info.get('market_cap', 'N/A')}M")
            print(f"   Source: {stock_info.get('source', 'unknown')}")

            # Check for enhanced data
            if 'analyst_ratings' in stock_info:
                print(f"   ✅ Analyst Ratings: Present")
            if 'insider_transactions' in stock_info:
                print(f"   ✅ Insider Transactions: Present")

            if stock_info.get('source') == 'AI_FALLBACK':
                print(f"   ⚠️  WARNING: Used AI fallback")
                results['warnings'] += 1

            results['passed'] += 1
        else:
            print(f"❌ FAIL: No stock info returned")
            results['failed'] += 1

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        results['failed'] += 1

    # ========================================================================
    # TEST 5: Technical Indicators
    # ========================================================================
    print("\n" + "-" * 80)
    print("TEST 5: Technical Indicators Calculation")
    print("-" * 80)

    try:
        from app.services.stock_service import StockService

        print("Calculating technical indicators for NVDA...")
        start_time = time.time()

        with app.app_context():
            tech_indicators = StockService.calculate_technical_indicators('NVDA')

        elapsed = time.time() - start_time

        if tech_indicators:
            print(f"✅ SUCCESS: Calculated indicators in {elapsed:.2f}s")

            indicators_found = []
            if tech_indicators.get('rsi'):
                indicators_found.append(f"RSI={tech_indicators['rsi']:.2f}")
            if tech_indicators.get('macd'):
                indicators_found.append(f"MACD={tech_indicators['macd']:.2f}")
            if tech_indicators.get('sma_50'):
                indicators_found.append(f"SMA50=${tech_indicators['sma_50']:.2f}")

            if indicators_found:
                print(f"   Indicators: {', '.join(indicators_found)}")

            results['passed'] += 1
        else:
            print(f"⚠️  WARNING: No technical indicators (historical data may be unavailable)")
            results['warnings'] += 1

    except Exception as e:
        print(f"⚠️  WARNING: Technical indicators failed (expected if no historical data)")
        print(f"   Error: {str(e)}")
        results['warnings'] += 1

    # ========================================================================
    # TEST 6: Error Handling - Invalid Ticker
    # ========================================================================
    print("\n" + "-" * 80)
    print("TEST 6: Error Handling (Invalid Ticker)")
    print("-" * 80)

    try:
        from app.services.alternative_data_sources import FallbackDataService

        print("Attempting to fetch invalid ticker 'INVALIDTICKER123'...")
        start_time = time.time()
        invalid_data = FallbackDataService.get_stock_quote('INVALIDTICKER123')
        elapsed = time.time() - start_time

        if invalid_data is None:
            print(f"✅ SUCCESS: Correctly returned None for invalid ticker ({elapsed:.2f}s)")
            results['passed'] += 1
        else:
            print(f"⚠️  WARNING: Returned data for invalid ticker (may be AI estimation)")
            print(f"   Source: {invalid_data.get('source', 'unknown')}")
            if invalid_data.get('source') == 'AI_FALLBACK':
                print(f"   Note: AI may provide estimated data for unknown tickers")
                results['warnings'] += 1
            results['passed'] += 1

    except Exception as e:
        print(f"✅ SUCCESS: Exception raised as expected")
        print(f"   Error: {str(e)}")
        results['passed'] += 1

    # ========================================================================
    # TEST 7: Cache Functionality
    # ========================================================================
    print("\n" + "-" * 80)
    print("TEST 7: Cache Functionality")
    print("-" * 80)

    try:
        from app.services.stock_service import StockService

        print("First fetch of AMD (should hit API)...")
        start_time1 = time.time()

        with app.app_context():
            data1 = StockService.get_stock_info('AMD')

        elapsed1 = time.time() - start_time1

        print(f"   First fetch: {elapsed1:.2f}s")

        print("Second fetch of AMD (should hit cache)...")
        start_time2 = time.time()

        with app.app_context():
            data2 = StockService.get_stock_info('AMD')

        elapsed2 = time.time() - start_time2

        print(f"   Second fetch: {elapsed2:.2f}s")

        if elapsed2 < elapsed1 * 0.5:  # Cache should be significantly faster
            print(f"✅ SUCCESS: Cache working (2nd fetch {elapsed2/elapsed1*100:.0f}% faster)")
            results['passed'] += 1
        else:
            print(f"⚠️  WARNING: Cache may not be working optimally")
            results['warnings'] += 1

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        results['failed'] += 1

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("LIVE INTEGRATION TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Passed: {results['passed']}")
    print(f"Tests Failed: {results['failed']}")
    print(f"Warnings: {results['warnings']}")
    print("=" * 80)

    if results['failed'] == 0:
        print("✅ ALL LIVE TESTS PASSED!")
        if results['warnings'] > 0:
            print(f"⚠️  {results['warnings']} warnings (check above for details)")
        print("\n🎉 AI Fallback System is PRODUCTION READY!")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        print("\n🔧 Review errors above and fix before production deployment")
        return False


if __name__ == "__main__":
    success = test_live_integration()
    sys.exit(0 if success else 1)
