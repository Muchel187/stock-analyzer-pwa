#!/usr/bin/env python3
"""
Test yfinance Python Module as Data Service
Tests if yfinance can be used reliably for stock data
"""

import yfinance as yf
import time
from datetime import datetime

def test_basic_stock_info():
    """Test basic stock information retrieval"""
    print("\n=== Test 1: Basic Stock Info ===")
    try:
        ticker = yf.Ticker("AAPL")
        info = ticker.info

        print(f"✅ Successfully fetched info for AAPL")
        print(f"   Company: {info.get('longName', 'N/A')}")
        print(f"   Sector: {info.get('sector', 'N/A')}")
        print(f"   Current Price: ${info.get('currentPrice', 'N/A')}")
        print(f"   Market Cap: ${info.get('marketCap', 'N/A'):,}")
        return True
    except Exception as e:
        print(f"❌ Failed to fetch stock info: {e}")
        return False

def test_historical_data():
    """Test historical data retrieval"""
    print("\n=== Test 2: Historical Data ===")
    try:
        ticker = yf.Ticker("GOOGL")
        hist = ticker.history(period="1mo")

        if len(hist) > 0:
            print(f"✅ Successfully fetched {len(hist)} days of data for GOOGL")
            print(f"   Latest Close: ${hist['Close'].iloc[-1]:.2f}")
            print(f"   Date Range: {hist.index[0].date()} to {hist.index[-1].date()}")
            return True
        else:
            print(f"❌ No historical data returned")
            return False
    except Exception as e:
        print(f"❌ Failed to fetch historical data: {e}")
        return False

def test_multiple_tickers():
    """Test fetching multiple tickers"""
    print("\n=== Test 3: Multiple Tickers ===")
    tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    results = []

    for symbol in tickers:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
            results.append((symbol, price, True))
            print(f"   {symbol}: ${price}")
        except Exception as e:
            results.append((symbol, None, False))
            print(f"   {symbol}: Failed ({str(e)[:50]})")

        # Small delay to avoid rate limiting
        time.sleep(0.5)

    successful = sum(1 for _, _, success in results if success)
    print(f"\n   Success Rate: {successful}/{len(tickers)} ({successful/len(tickers)*100:.0f}%)")
    return successful == len(tickers)

def test_rate_limiting():
    """Test rate limiting behavior"""
    print("\n=== Test 4: Rate Limiting ===")
    print("   Making 10 rapid requests...")

    errors = 0
    successes = 0

    for i in range(10):
        try:
            ticker = yf.Ticker("AAPL")
            info = ticker.info
            price = info.get('currentPrice', info.get('regularMarketPrice'))
            if price:
                successes += 1
                print(f"   Request {i+1}: ✅ Success (${price})")
            else:
                errors += 1
                print(f"   Request {i+1}: ⚠️ No price data")
        except Exception as e:
            errors += 1
            error_msg = str(e)
            if "429" in error_msg or "Too Many Requests" in error_msg:
                print(f"   Request {i+1}: ❌ Rate Limited")
            else:
                print(f"   Request {i+1}: ❌ Error: {error_msg[:50]}")

        # No delay - testing rate limit behavior

    print(f"\n   Successes: {successes}/10")
    print(f"   Errors: {errors}/10")

    if errors > 5:
        print("   ⚠️ WARNING: High error rate suggests rate limiting issues")
        return False
    else:
        print("   ✅ Rate limiting acceptable")
        return True

def test_german_stocks():
    """Test German stock data (DAX)"""
    print("\n=== Test 5: German Stocks (DAX) ===")
    german_tickers = ["SAP.DE", "SIE.DE", "VOW3.DE"]  # SAP, Siemens, VW

    results = []
    for symbol in german_tickers:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
            results.append((symbol, price, True))
            print(f"   {symbol}: €{price}")
        except Exception as e:
            results.append((symbol, None, False))
            print(f"   {symbol}: Failed ({str(e)[:50]})")

        time.sleep(0.5)

    successful = sum(1 for _, _, success in results if success)
    print(f"\n   Success Rate: {successful}/{len(german_tickers)} ({successful/len(german_tickers)*100:.0f}%)")
    return successful >= 2  # At least 2 out of 3

def test_data_freshness():
    """Test if data is fresh/recent"""
    print("\n=== Test 6: Data Freshness ===")
    try:
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="1d", interval="1m")

        if len(hist) > 0:
            latest_time = hist.index[-1]
            time_diff = datetime.now(latest_time.tzinfo) - latest_time
            minutes_old = time_diff.total_seconds() / 60

            print(f"   Latest data timestamp: {latest_time}")
            print(f"   Data age: {minutes_old:.0f} minutes")

            if minutes_old < 60:
                print(f"   ✅ Data is fresh (< 1 hour old)")
                return True
            else:
                print(f"   ⚠️ Data is stale (> 1 hour old)")
                return False
        else:
            print(f"   ❌ No intraday data available")
            return False
    except Exception as e:
        print(f"   ❌ Failed to check freshness: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("yfinance Python Service Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Basic Stock Info", test_basic_stock_info),
        ("Historical Data", test_historical_data),
        ("Multiple Tickers", test_multiple_tickers),
        ("Rate Limiting", test_rate_limiting),
        ("German Stocks", test_german_stocks),
        ("Data Freshness", test_data_freshness),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))

        time.sleep(1)  # Delay between tests

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print("\n" + "=" * 60)
    print(f"Overall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("=" * 60)

    if passed == total:
        print("\n✅ ALL TESTS PASSED - yfinance is working reliably")
        return 0
    elif passed >= total * 0.7:
        print("\n⚠️ MOST TESTS PASSED - yfinance is working but has some issues")
        return 1
    else:
        print("\n❌ MANY TESTS FAILED - yfinance has significant issues")
        return 2

if __name__ == "__main__":
    exit(main())
