#!/usr/bin/env python3
"""
Test German Stock Support in APIs
"""
import os
import sys

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.alternative_data_sources import TwelveDataService, FinnhubService, AlphaVantageService, FallbackDataService

def test_ticker(ticker, service_name, service_method):
    """Test a single ticker with a service"""
    try:
        result = service_method(ticker)
        if result and result.get('ticker') == ticker.upper():
            print(f"  ✅ {service_name}: {ticker} → SUCCESS (Price: ${result.get('current_price', 'N/A')})")
            return True
        else:
            print(f"  ❌ {service_name}: {ticker} → FAILED (No data)")
            return False
    except Exception as e:
        print(f"  ❌ {service_name}: {ticker} → ERROR: {str(e)[:50]}")
        return False

def main():
    print("=" * 70)
    print("Testing German Stock Support in APIs")
    print("=" * 70)

    # Test different ticker formats for SAP
    test_tickers = {
        'SAP': 'SAP without suffix',
        'SAP.DE': 'SAP with .DE (XETRA)',
        'SAP.F': 'SAP with .F (Frankfurt)',
        'SAPG.DE': 'SAP alternative ticker',
        'SIE.DE': 'Siemens',
        'BMW.DE': 'BMW',
        'VOW3.DE': 'Volkswagen'
    }

    services = [
        ('Twelve Data', TwelveDataService.get_stock_quote),
        ('Finnhub', FinnhubService.get_stock_quote),
        ('Alpha Vantage', AlphaVantageService.get_stock_quote),
        ('Fallback', FallbackDataService.get_stock_quote)
    ]

    results = {}

    for ticker, description in test_tickers.items():
        print(f"\n📊 Testing: {ticker} ({description})")
        results[ticker] = {}

        for service_name, service_method in services:
            success = test_ticker(ticker, service_name, service_method)
            results[ticker][service_name] = success

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for ticker, description in test_tickers.items():
        successful_services = sum(1 for success in results[ticker].values() if success)
        total_services = len(services)
        status = "✅ WORKING" if successful_services > 0 else "❌ NOT WORKING"

        print(f"{status}: {ticker:15s} ({successful_services}/{total_services} services)")

    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    # Find which ticker format works best
    best_format = None
    max_success = 0

    for ticker in test_tickers.keys():
        success_count = sum(1 for success in results[ticker].values() if success)
        if success_count > max_success:
            max_success = success_count
            best_format = ticker

    if best_format:
        print(f"\n✅ Best ticker format: {best_format} (works with {max_success}/{len(services)} services)")
        print(f"\n💡 Recommendation: Use '{best_format}' format in screener for German stocks")
    else:
        print("\n❌ No German ticker format works reliably across services")
        print("\n💡 Recommendation: Need alternative solution for German stocks")

if __name__ == "__main__":
    main()
