# Historical Data Solution Plan - Google Finance Crawler

## Problem Analysis

### Current Issues
1. **Alpha Vantage**: Only 25 requests/day - quickly exhausted
2. **Twelve Data**: 800 requests/day - also limited
3. **Finnhub**: No historical data endpoint for free tier
4. **AI Fallback**: Too slow and not real-time data

### Root Cause
- We're trying to fetch historical data on-demand from rate-limited APIs
- No local storage of historical prices
- Each user request triggers external API calls

## Proposed Solution: Google Finance Crawler + Local Storage

### Core Concept
1. **Scheduled Crawling**: Fetch data from Google Finance every 2-4 hours
2. **Local Database Storage**: Store all historical prices in PostgreSQL/SQLite
3. **No Rate Limits**: Google Finance has no strict API limits for reasonable crawling
4. **Always Available**: Historical data served from local DB, instant response

## Architecture Design

### 1. Database Schema

```sql
-- New table for historical prices
CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint to prevent duplicates
    UNIQUE(ticker, date),

    -- Indexes for performance
    INDEX idx_ticker (ticker),
    INDEX idx_date (date),
    INDEX idx_ticker_date (ticker, date)
);

-- Table for tracking last update time per ticker
CREATE TABLE crawler_metadata (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) UNIQUE NOT NULL,
    last_crawled_at TIMESTAMP,
    last_successful_crawl TIMESTAMP,
    crawl_status VARCHAR(50), -- 'success', 'failed', 'pending'
    error_message TEXT,
    data_points_stored INTEGER DEFAULT 0,

    INDEX idx_ticker (ticker),
    INDEX idx_last_crawled (last_crawled_at)
);
```

### 2. Google Finance Crawler Service

```python
# app/services/google_finance_crawler.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re
import json

class GoogleFinanceCrawler:
    BASE_URL = "https://www.google.com/finance/quote/{ticker}:{exchange}"

    @staticmethod
    def get_historical_data(ticker, period='1Y'):
        """
        Crawl Google Finance for historical data

        Periods: 1D, 5D, 1M, 6M, YTD, 1Y, 5Y, MAX
        """
        # Implementation details below
        pass

    @staticmethod
    def parse_price_data(html_content):
        """Parse price data from Google Finance HTML"""
        pass

    @staticmethod
    def store_in_database(ticker, price_data):
        """Store crawled data in database"""
        pass
```

### 3. Data Collection Strategy

#### Phase 1: Initial Data Population
1. **Priority Tickers** (Most searched/used):
   - S&P 500 top 100 stocks
   - DAX 30 stocks
   - User watchlist stocks
   - User portfolio stocks

2. **Collection Schedule**:
   ```
   Every 2 hours (12 times/day):
   - Update today's prices for all tracked stocks

   Every 6 hours (4 times/day):
   - Update last 5 days for active stocks

   Once daily (at 2 AM):
   - Update last 30 days for all stocks

   Once weekly:
   - Update 1 year history for all stocks
   ```

#### Phase 2: Smart Crawling
- **Priority Queue**: More frequent updates for popular stocks
- **User-Triggered**: When user searches a new stock, add to crawl queue
- **Adaptive Scheduling**: Crawl more during market hours

### 4. Implementation Steps

#### Step 1: Validate Google Finance Access
```python
def validate_google_finance_route():
    """Test if we can access Google Finance without blocking"""
    test_tickers = ['AAPL', 'MSFT', 'GOOGL']

    for ticker in test_tickers:
        url = f"https://www.google.com/finance/quote/{ticker}:NASDAQ"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

        if response.status_code == 200:
            print(f"✅ {ticker}: Accessible")
        else:
            print(f"❌ {ticker}: Blocked or error")
```

#### Step 2: Create Crawler with Anti-Detection
```python
import time
import random

class SmartCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def crawl_with_delay(self, ticker):
        """Crawl with random delay to avoid detection"""
        delay = random.uniform(2, 5)  # 2-5 seconds
        time.sleep(delay)
        return self.crawl(ticker)

    def get_random_user_agent(self):
        """Rotate user agents"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        return random.choice(agents)
```

#### Step 3: Scheduled Tasks (Using APScheduler)
```python
# app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.google_finance_crawler import GoogleFinanceCrawler

scheduler = BackgroundScheduler()

# Every 2 hours: Update current prices
scheduler.add_job(
    func=update_current_prices,
    trigger="interval",
    hours=2,
    id='update_current_prices',
    name='Update current stock prices'
)

# Every 6 hours: Update 5-day history
scheduler.add_job(
    func=update_weekly_history,
    trigger="interval",
    hours=6,
    id='update_weekly_history',
    name='Update 5-day price history'
)

# Daily at 2 AM: Update monthly history
scheduler.add_job(
    func=update_monthly_history,
    trigger="cron",
    hour=2,
    minute=0,
    id='update_monthly_history',
    name='Update 30-day price history'
)

scheduler.start()
```

### 5. API Endpoints

```python
# app/routes/historical.py

@bp.route('/api/historical/<ticker>')
def get_historical_prices(ticker):
    """
    Get historical prices from local database

    Query params:
    - period: 1D, 5D, 1M, 3M, 6M, 1Y, 5Y
    - interval: 1d, 1h (if available)
    """
    period = request.args.get('period', '1M')

    # Query from local database
    prices = StockPrice.query.filter_by(ticker=ticker)\
        .filter(StockPrice.date >= get_start_date(period))\
        .order_by(StockPrice.date.asc())\
        .all()

    return jsonify({
        'ticker': ticker,
        'period': period,
        'data': [p.to_dict() for p in prices],
        'last_updated': get_last_update_time(ticker)
    })
```

### 6. Fallback Strategy

```python
def get_historical_data_with_fallback(ticker, period):
    """
    1. Try local database first
    2. If no data or stale (>24h), trigger crawl
    3. If crawl fails, try APIs (Alpha Vantage, etc.)
    4. If APIs fail, use AI fallback
    5. Return best available data
    """

    # Step 1: Check local database
    local_data = get_from_database(ticker, period)
    if local_data and is_fresh(local_data):
        return local_data

    # Step 2: Trigger immediate crawl
    try:
        fresh_data = GoogleFinanceCrawler.crawl_now(ticker)
        if fresh_data:
            store_in_database(fresh_data)
            return fresh_data
    except:
        pass

    # Step 3: Try traditional APIs
    api_data = try_apis(ticker, period)
    if api_data:
        return api_data

    # Step 4: AI fallback
    if local_data:  # Even if stale
        return local_data

    return ai_fallback(ticker, period)
```

## Implementation Timeline

### Day 1: Foundation
1. ✅ Create database tables
2. ✅ Basic Google Finance crawler
3. ✅ Test crawling with 5 stocks
4. ✅ Store data in database

### Day 2: Scheduling
1. ✅ Implement APScheduler
2. ✅ Create scheduled tasks
3. ✅ Add crawler metadata tracking
4. ✅ Implement priority queue

### Day 3: Integration
1. ✅ Update StockService to use local DB
2. ✅ Create API endpoints
3. ✅ Implement fallback logic
4. ✅ Update frontend to use new endpoints

### Day 4: Optimization
1. ✅ Add caching layer
2. ✅ Optimize database queries
3. ✅ Implement rate limiting
4. ✅ Add monitoring/alerting

## Benefits

1. **No API Rate Limits**: Google Finance has no strict limits
2. **Always Available**: Data served from local DB
3. **Fast Response**: No external API calls needed
4. **Cost Effective**: No paid API subscriptions required
5. **Reliable**: Not dependent on third-party API uptime
6. **Scalable**: Can add more stocks as needed
7. **Historical Preservation**: Never lose historical data

## Potential Issues & Solutions

### Issue 1: Google Blocking
- **Solution**: Rotate user agents, add delays, use proxy if needed

### Issue 2: Data Storage Size
- **Solution**: Compress old data, archive to separate table

### Issue 3: Initial Data Load
- **Solution**: Prioritize user's stocks, load others gradually

### Issue 4: Market Hours
- **Solution**: Crawl more frequently during market hours

## Alternative: yfinance Library

If Google Finance becomes problematic, we can use `yfinance` library:

```python
import yfinance as yf

def get_yahoo_historical(ticker, period='1y'):
    """Alternative using Yahoo Finance"""
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)
    return history.to_dict('records')
```

However, yfinance has rate limits, so local storage is still necessary.

## Monitoring & Maintenance

### Metrics to Track
1. Crawl success rate per ticker
2. Data freshness (time since last update)
3. Database size and growth
4. Query performance
5. API fallback usage

### Alerts
1. Crawl failures > 3 consecutive
2. Database size > 80% capacity
3. Query time > 1 second
4. No data for popular ticker > 24 hours

## Conclusion

This solution provides:
- ✅ Reliable historical data
- ✅ No dependency on rate-limited APIs
- ✅ Fast response times
- ✅ Cost-effective operation
- ✅ Scalable architecture

The system will be transparent to users - they'll simply see fast, reliable historical data without knowing the backend complexity.

## Next Steps

1. Validate Google Finance access route
2. Create database schema
3. Implement basic crawler
4. Test with 5 stocks
5. Add scheduling
6. Integrate with existing system
7. Deploy and monitor