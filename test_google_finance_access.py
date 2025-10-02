#!/usr/bin/env python3
"""
Test script to validate Google Finance access
Checks if we can crawl Google Finance without being blocked
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import re
from datetime import datetime

def test_google_finance_access():
    """Test if we can access Google Finance for different stocks"""

    print("=" * 80)
    print("GOOGLE FINANCE ACCESS VALIDATION")
    print("=" * 80)
    print()

    # Test stocks from different exchanges
    test_cases = [
        ('AAPL', 'NASDAQ'),
        ('MSFT', 'NASDAQ'),
        ('GOOGL', 'NASDAQ'),
        ('TSLA', 'NASDAQ'),
        ('BMW', 'ETR'),  # German stock
        ('SAP', 'ETR'),  # German stock
        ('SPY', 'NYSEARCA'),  # ETF
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }

    results = []

    for ticker, exchange in test_cases:
        print(f"\nTesting {ticker}:{exchange}...")

        url = f"https://www.google.com/finance/quote/{ticker}:{exchange}"

        try:
            # Add delay to avoid rate limiting
            time.sleep(2)

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                # Parse HTML to verify we got real data
                soup = BeautifulSoup(response.text, 'html.parser')

                # Try to find price element (Google Finance structure)
                # Look for various possible price containers
                price_found = False

                # Method 1: Look for price in specific div classes
                price_divs = soup.find_all('div', class_=re.compile('YMlKec|fxKbKc'))
                if price_divs:
                    for div in price_divs:
                        text = div.get_text(strip=True)
                        if text and '$' in text or '€' in text or any(c.isdigit() for c in text):
                            price_found = True
                            print(f"  ✅ SUCCESS: Found price data: {text[:50]}...")
                            break

                # Method 2: Look for data in script tags
                if not price_found:
                    scripts = soup.find_all('script')
                    for script in scripts:
                        if script.string and 'ticker' in script.string.lower():
                            price_found = True
                            print(f"  ✅ SUCCESS: Found data in script tags")
                            break

                # Method 3: Check for specific stock name
                if not price_found:
                    page_text = soup.get_text().lower()
                    if ticker.lower() in page_text:
                        price_found = True
                        print(f"  ✅ SUCCESS: Found ticker reference in page")

                if price_found:
                    results.append({
                        'ticker': ticker,
                        'exchange': exchange,
                        'status': 'success',
                        'status_code': response.status_code,
                        'data_found': True
                    })
                else:
                    print(f"  ⚠️  WARNING: Page loaded but no price data found")
                    results.append({
                        'ticker': ticker,
                        'exchange': exchange,
                        'status': 'partial',
                        'status_code': response.status_code,
                        'data_found': False
                    })

            elif response.status_code == 403:
                print(f"  ❌ BLOCKED: Access forbidden (403)")
                results.append({
                    'ticker': ticker,
                    'exchange': exchange,
                    'status': 'blocked',
                    'status_code': response.status_code
                })

            elif response.status_code == 429:
                print(f"  ❌ RATE LIMITED: Too many requests (429)")
                results.append({
                    'ticker': ticker,
                    'exchange': exchange,
                    'status': 'rate_limited',
                    'status_code': response.status_code
                })

            else:
                print(f"  ❌ ERROR: Status code {response.status_code}")
                results.append({
                    'ticker': ticker,
                    'exchange': exchange,
                    'status': 'error',
                    'status_code': response.status_code
                })

        except requests.exceptions.Timeout:
            print(f"  ❌ TIMEOUT: Request timed out")
            results.append({
                'ticker': ticker,
                'exchange': exchange,
                'status': 'timeout',
                'error': 'Timeout'
            })

        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            results.append({
                'ticker': ticker,
                'exchange': exchange,
                'status': 'error',
                'error': str(e)
            })

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    successful = sum(1 for r in results if r['status'] == 'success')
    partial = sum(1 for r in results if r['status'] == 'partial')
    failed = sum(1 for r in results if r['status'] in ['blocked', 'rate_limited', 'error', 'timeout'])

    print(f"\nTotal tests: {len(results)}")
    print(f"✅ Successful: {successful}")
    print(f"⚠️  Partial: {partial}")
    print(f"❌ Failed: {failed}")

    if successful > 0:
        print(f"\n✅ Google Finance is ACCESSIBLE for crawling")
        print("We can proceed with the crawler implementation")
    elif partial > 0:
        print(f"\n⚠️  Google Finance is PARTIALLY accessible")
        print("May need to adjust parsing strategy")
    else:
        print(f"\n❌ Google Finance is NOT accessible")
        print("Need to find alternative solution")

    # Save results for analysis
    with open('google_finance_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'summary': {
                'total': len(results),
                'successful': successful,
                'partial': partial,
                'failed': failed
            }
        }, f, indent=2)

    print(f"\nDetailed results saved to: google_finance_test_results.json")

    return successful > 0 or partial > 0


def test_alternative_yfinance():
    """Test yfinance as alternative"""
    print("\n" + "=" * 80)
    print("TESTING ALTERNATIVE: yfinance")
    print("=" * 80)

    try:
        import yfinance as yf

        test_ticker = "AAPL"
        print(f"\nFetching {test_ticker} with yfinance...")

        stock = yf.Ticker(test_ticker)

        # Test current info
        info = stock.info
        if info and 'currentPrice' in info:
            print(f"✅ Current price: ${info['currentPrice']}")

        # Test historical data
        history = stock.history(period="1mo")
        if not history.empty:
            print(f"✅ Historical data: {len(history)} days")
            print(f"   Latest close: ${history['Close'].iloc[-1]:.2f}")

        print("\n✅ yfinance is working as alternative!")
        return True

    except ImportError:
        print("❌ yfinance not installed")
        print("Install with: pip install yfinance")
        return False

    except Exception as e:
        print(f"❌ yfinance error: {e}")
        return False


if __name__ == "__main__":
    # Test Google Finance
    google_works = test_google_finance_access()

    # Test yfinance as backup
    yfinance_works = test_alternative_yfinance()

    print("\n" + "=" * 80)
    print("FINAL RECOMMENDATION")
    print("=" * 80)

    if google_works:
        print("\n✅ Proceed with Google Finance crawler implementation")
        print("   - Implement BeautifulSoup parser")
        print("   - Add rate limiting (2-5 second delays)")
        print("   - Rotate user agents")
        print("   - Store in local database")
    elif yfinance_works:
        print("\n✅ Use yfinance library as primary source")
        print("   - Simpler implementation")
        print("   - More reliable data structure")
        print("   - Still needs local storage for caching")
    else:
        print("\n⚠️  Both methods have issues")
        print("   - Consider using a paid API service")
        print("   - Or implement more sophisticated crawling")