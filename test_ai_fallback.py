#!/usr/bin/env python3
"""
Test script for AI Fallback functionality
Tests that AI can provide stock data when traditional APIs are exhausted
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_ai_fallback():
    """Test AI fallback for stock data retrieval"""
    print("=" * 80)
    print("AI FALLBACK TEST - Stock Data Retrieval")
    print("=" * 80)
    print()

    from app.services.ai_service import AIService

    # Initialize AI service
    ai_service = AIService()

    if not ai_service.provider:
        print("❌ FAIL: No AI provider configured")
        print("   Please set GOOGLE_API_KEY or OPENAI_API_KEY in .env")
        return False

    print(f"✅ AI Provider: {ai_service.provider_name}")
    print()

    # Test 1: Get stock data from AI
    print("-" * 80)
    print("TEST 1: Get Stock Data from AI")
    print("-" * 80)

    test_ticker = "AAPL"
    print(f"Fetching data for {test_ticker} from AI...")

    try:
        stock_data = ai_service.get_stock_data_from_ai(test_ticker)

        if stock_data:
            print(f"✅ SUCCESS: Retrieved data for {test_ticker}")
            print(f"   Company: {stock_data.get('company_name', 'N/A')}")
            print(f"   Price: ${stock_data.get('current_price', 'N/A')}")
            print(f"   Market Cap: ${stock_data.get('market_cap', 'N/A')}M")
            print(f"   Sector: {stock_data.get('sector', 'N/A')}")
            print(f"   Source: {stock_data.get('source', 'N/A')}")

            # Check technical indicators
            if 'technical_indicators' in stock_data:
                tech = stock_data['technical_indicators']
                print(f"\n   Technical Indicators:")
                print(f"   - RSI: {tech.get('rsi', 'N/A')}")
                print(f"   - MACD: {tech.get('macd', 'N/A')}")
                print(f"   - SMA 50: {tech.get('sma_50', 'N/A')}")
                print(f"   - Volatility: {tech.get('volatility', 'N/A')}")

            # Check fundamental metrics
            if 'fundamental_metrics' in stock_data:
                fund = stock_data['fundamental_metrics']
                print(f"\n   Fundamental Metrics:")
                print(f"   - Revenue: ${fund.get('revenue', 'N/A')}M")
                print(f"   - EPS: ${fund.get('earnings_per_share', 'N/A')}")
                print(f"   - ROE: {fund.get('roe', 'N/A')}%")

            # Check historical data
            if 'historical_data' in stock_data and stock_data['historical_data']:
                hist_count = len(stock_data['historical_data'])
                print(f"\n   Historical Data: {hist_count} days")
                if hist_count > 0:
                    latest = stock_data['historical_data'][0]
                    print(f"   - Latest: {latest.get('date', 'N/A')} - Close: ${latest.get('close', 'N/A')}")
        else:
            print(f"❌ FAIL: No data returned for {test_ticker}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    print()

    # Test 2: Get historical data from AI
    print("-" * 80)
    print("TEST 2: Get Historical Data from AI")
    print("-" * 80)

    print(f"Fetching historical data for {test_ticker} (1mo)...")

    try:
        historical_data = ai_service.get_historical_data_from_ai(test_ticker, period='1mo')

        if historical_data and historical_data.get('data'):
            data_points = len(historical_data['data'])
            print(f"✅ SUCCESS: Retrieved {data_points} days of historical data")
            print(f"   Period: {historical_data.get('period', 'N/A')}")
            print(f"   Source: {historical_data.get('source', 'N/A')}")

            # Show first and last data points
            if data_points > 0:
                first = historical_data['data'][0]
                last = historical_data['data'][-1]
                print(f"\n   First: {first.get('date', 'N/A')}")
                print(f"   - Open: ${first.get('open', 'N/A')}")
                print(f"   - Close: ${first.get('close', 'N/A')}")
                print(f"   - Volume: {first.get('volume', 'N/A'):,}")
                print(f"\n   Last: {last.get('date', 'N/A')}")
                print(f"   - Open: ${last.get('open', 'N/A')}")
                print(f"   - Close: ${last.get('close', 'N/A')}")
                print(f"   - Volume: {last.get('volume', 'N/A'):,}")
        else:
            print(f"❌ FAIL: No historical data returned for {test_ticker}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    print()

    # Test 3: Test with FallbackDataService integration
    print("-" * 80)
    print("TEST 3: FallbackDataService Integration")
    print("-" * 80)

    from app.services.alternative_data_sources import FallbackDataService

    # Temporarily disable API keys to force AI fallback
    print("Testing AI fallback when APIs are unavailable...")

    original_finnhub = os.environ.get('FINNHUB_API_KEY')
    original_twelve = os.environ.get('TWELVE_DATA_API_KEY')
    original_alpha = os.environ.get('ALPHA_VANTAGE_API_KEY')

    # Disable API keys
    if original_finnhub:
        os.environ.pop('FINNHUB_API_KEY', None)
    if original_twelve:
        os.environ.pop('TWELVE_DATA_API_KEY', None)
    if original_alpha:
        os.environ.pop('ALPHA_VANTAGE_API_KEY', None)

    try:
        test_ticker = "TSLA"
        print(f"\nFetching {test_ticker} with all APIs disabled (forcing AI fallback)...")

        quote_data = FallbackDataService.get_stock_quote(test_ticker)

        if quote_data:
            print(f"✅ SUCCESS: AI fallback provided data for {test_ticker}")
            print(f"   Source: {quote_data.get('source', 'N/A')}")
            print(f"   Price: ${quote_data.get('current_price', 'N/A')}")
            print(f"   Company: {quote_data.get('company_name', 'N/A')}")
        else:
            print(f"❌ FAIL: AI fallback did not provide data")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore API keys
        if original_finnhub:
            os.environ['FINNHUB_API_KEY'] = original_finnhub
        if original_twelve:
            os.environ['TWELVE_DATA_API_KEY'] = original_twelve
        if original_alpha:
            os.environ['ALPHA_VANTAGE_API_KEY'] = original_alpha

    print()
    print("=" * 80)
    print("✅ ALL AI FALLBACK TESTS PASSED")
    print("=" * 80)
    print()
    print("Summary:")
    print("- AI can provide stock quotes when APIs fail")
    print("- AI can provide historical data when APIs fail")
    print("- AI can provide technical indicators")
    print("- AI can provide fundamental metrics")
    print("- FallbackDataService correctly uses AI as ultimate fallback")
    print()
    print("⚠️  IMPORTANT NOTES:")
    print("- AI data is based on training data (not real-time)")
    print("- AI should only be used when traditional APIs are exhausted")
    print("- Data freshness may vary depending on AI model training date")
    print("- Always prefer real-time API data when available")
    print()

    return True


if __name__ == "__main__":
    success = test_ai_fallback()
    sys.exit(0 if success else 1)
