#!/usr/bin/env python
"""
Test script to verify bug fixes:
1. Database duplicate key error fix
2. AI analysis null pointer fix
3. Better error handling for missing data
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.services.stock_service import StockService
from app.services.ai_service import AIService

def test_stock_info():
    """Test stock info retrieval"""
    print("=" * 60)
    print("TEST 1: Stock Info Retrieval")
    print("=" * 60)
    
    tickers = ['TSLA', 'GME', 'AAPL']
    
    for ticker in tickers:
        print(f"\nTesting {ticker}...")
        try:
            info = StockService.get_stock_info(ticker)
            if info:
                print(f"✓ {ticker}: Successfully fetched stock info")
                print(f"  - Current Price: ${info.get('current_price', 'N/A')}")
                print(f"  - Company: {info.get('company_name', 'N/A')}")
                print(f"  - Has analyst_ratings: {bool(info.get('analyst_ratings'))}")
                print(f"  - Has price_target: {bool(info.get('price_target'))}")
            else:
                print(f"✗ {ticker}: Failed to fetch stock info")
        except Exception as e:
            print(f"✗ {ticker}: Error - {str(e)}")

def test_technical_indicators():
    """Test technical indicators calculation"""
    print("\n" + "=" * 60)
    print("TEST 2: Technical Indicators")
    print("=" * 60)
    
    tickers = ['TSLA', 'AAPL']
    
    for ticker in tickers:
        print(f"\nTesting {ticker}...")
        try:
            tech = StockService.calculate_technical_indicators(ticker)
            if tech:
                print(f"✓ {ticker}: Successfully calculated technical indicators")
                print(f"  - RSI: {tech.get('rsi', 'N/A')}")
                print(f"  - MACD: {tech.get('macd', {}).get('macd', 'N/A')}")
            else:
                print(f"⚠ {ticker}: No technical indicators (probably no historical data)")
        except Exception as e:
            print(f"✗ {ticker}: Error - {str(e)}")

def test_ai_analysis():
    """Test AI analysis with various data scenarios"""
    print("\n" + "=" * 60)
    print("TEST 3: AI Analysis")
    print("=" * 60)
    
    ticker = 'AAPL'
    print(f"\nTesting AI analysis for {ticker}...")
    
    try:
        # Get stock data
        stock_info = StockService.get_stock_info(ticker)
        technical = StockService.calculate_technical_indicators(ticker)
        fundamental = StockService.get_fundamental_analysis(ticker)
        
        print(f"  - Stock Info: {'✓' if stock_info else '✗'}")
        print(f"  - Technical: {'✓' if technical else '⚠ (no historical data)'}")
        print(f"  - Fundamental: {'✓' if fundamental else '✗'}")
        
        # Test AI analysis
        ai_service = AIService()
        print(f"  - AI Provider: {ai_service.provider_name}")
        
        ai_result = ai_service.analyze_stock_with_ai(
            stock_info if stock_info else {'ticker': ticker},
            technical,
            fundamental,
            None,
            None
        )
        
        if ai_result:
            if 'error' in ai_result:
                print(f"⚠ AI Analysis returned with error: {ai_result.get('error')}")
            else:
                print(f"✓ AI Analysis successful")
                print(f"  - Has ai_analysis: {bool(ai_result.get('ai_analysis'))}")
                print(f"  - Has raw_analysis: {bool(ai_result.get('raw_analysis'))}")
                print(f"  - Confidence score: {ai_result.get('confidence_score', 'N/A')}")
        else:
            print(f"✗ AI Analysis failed (returned None)")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())

def test_cache_duplicate():
    """Test cache duplicate key handling"""
    print("\n" + "=" * 60)
    print("TEST 4: Cache Duplicate Key Handling")
    print("=" * 60)
    
    ticker = 'TEST'
    
    try:
        from app.models.stock_cache import StockCache
        from datetime import datetime, timedelta, timezone
        
        # Try to set cache twice
        test_data = {'price': 100, 'test': True}
        
        print(f"\nSetting cache for {ticker} first time...")
        StockCache.set_cache(ticker, test_data, 'info')
        print("✓ First cache set successful")
        
        print(f"\nSetting cache for {ticker} second time (should update)...")
        test_data['price'] = 200
        StockCache.set_cache(ticker, test_data, 'info')
        print("✓ Second cache set successful (no duplicate key error)")
        
        # Verify
        cached = StockCache.get_cached(ticker, 'info')
        if cached and cached.get('price') == 200:
            print("✓ Cache was updated correctly")
        else:
            print("✗ Cache was not updated correctly")
            
        # Clean up
        from app import db
        cache_obj = StockCache.query.filter_by(ticker=ticker, data_type='info').first()
        if cache_obj:
            db.session.delete(cache_obj)
            db.session.commit()
            print("✓ Test cache cleaned up")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 60)
        print("RUNNING BUG FIX TESTS")
        print("=" * 60)
        
        test_stock_info()
        test_technical_indicators()
        test_ai_analysis()
        test_cache_duplicate()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
