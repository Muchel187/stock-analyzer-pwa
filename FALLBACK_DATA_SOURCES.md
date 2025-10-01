# 📊 Fallback Data Sources - Stock API Configuration

## Problem: Yahoo Finance Rate Limiting

Yahoo Finance (via `yfinance`) is the primary data source but has strict rate limits that cause **429 Too Many Requests** errors. This app now includes **automatic fallback to alternative free APIs**.

## How It Works

The app automatically tries data sources in this order:

1. **Yahoo Finance** (via yfinance) - Primary source
2. **Finnhub API** - First fallback (60 requests/minute free)
3. **Twelve Data API** - Second fallback (800 requests/day free)
4. **Alpha Vantage API** - Third fallback (25 requests/day free)

If Yahoo Finance fails, the app **automatically switches** to the next available source without user intervention.

## Setup Instructions

### 1. Get Free API Keys

All these services offer free tiers suitable for development:

#### Finnhub (Recommended - Best Free Tier)
- Sign up: https://finnhub.io/
- Free tier: **60 requests per minute**
- Best for: Real-time quotes, company profiles
- Setup:
  1. Create account
  2. Get API key from dashboard
  3. Add to `.env`: `FINNHUB_API_KEY=your_key_here`

#### Twelve Data (Best for Daily Use)
- Sign up: https://twelvedata.com/
- Free tier: **800 requests per day, 8 per minute**
- Best for: Historical data, extended quotes
- Setup:
  1. Create account
  2. Get API key from dashboard
  3. Add to `.env`: `TWELVE_DATA_API_KEY=your_key_here`

#### Alpha Vantage (Best for Fundamentals)
- Sign up: https://www.alphavantage.co/support/#api-key
- Free tier: **25 requests per day** (limited!)
- Best for: Company fundamentals, financial statements
- Setup:
  1. Create account
  2. Get API key
  3. Add to `.env`: `ALPHA_VANTAGE_API_KEY=your_key_here`

### 2. Configure .env File

Edit `/home/jbk/Aktienanalyse/.env` and add your API keys:

```bash
# Stock Data API Keys (fallback sources)
FINNHUB_API_KEY=your_finnhub_key_here
TWELVE_DATA_API_KEY=your_twelve_data_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
```

**Note:** The app works without API keys, but will be limited to cached data when Yahoo Finance is rate-limited.

### 3. Restart the Server

```bash
# Stop the current server (Ctrl+C)
# Restart
source venv/bin/activate
python app.py
```

## Features

### Automatic Fallback
- No code changes needed
- Seamless transition between sources
- Logs show which source was used

### Smart Caching
- Data cached for 1 hour by default
- Reduces API calls across all sources
- Configure in `.env`: `STOCKS_CACHE_TIMEOUT=3600`

### Data Source Indicator
- Stock info includes `"source"` field showing which API was used
- Example: `"source": "finnhub"` or `"source": "yahoo_finance"`

## Rate Limit Comparison

| Service | Free Tier Limit | Best For |
|---------|----------------|----------|
| Yahoo Finance | ~2000/hour | Historical data, comprehensive info |
| Finnhub | 60/minute | Real-time quotes, high frequency |
| Twelve Data | 800/day, 8/min | Daily analysis, moderate use |
| Alpha Vantage | 25/day | Fundamentals only |

## Recommended Setup

### For Development (Testing)
```bash
FINNHUB_API_KEY=your_key    # Main fallback
TWELVE_DATA_API_KEY=your_key # Backup
```

### For Production (Heavy Use)
Consider upgrading to paid tiers:
- **Finnhub Pro**: $59/month (Unlimited)
- **Twelve Data Grow**: $19/month (8000 requests/day)
- **Alpha Vantage Premium**: $49/month (1200 requests/minute)

## Troubleshooting

### Still Getting 404 Errors?

1. **Check API keys are set:**
   ```bash
   cat .env | grep API_KEY
   ```

2. **Verify keys work:**
   ```bash
   # Test Finnhub
   curl "https://finnhub.io/api/v1/quote?symbol=AAPL&token=YOUR_KEY"

   # Test Twelve Data
   curl "https://api.twelvedata.com/quote?symbol=AAPL&apikey=YOUR_KEY"
   ```

3. **Check server logs:**
   - Look for: `"Trying finnhub for AAPL..."`
   - Success: `"Successfully fetched AAPL from finnhub"`
   - Failure: `"All fallback sources failed for AAPL"`

### Rate Limit Still Exceeded?

If all sources are rate-limited:

1. **Wait 5-10 minutes** - Limits reset automatically
2. **Use cache** - Already-loaded stocks use cached data
3. **Be strategic:**
   - Search for specific stocks (don't load everything)
   - Use watchlist (caches your favorites)
   - Avoid screener during rate limits (loads 50+ stocks)

## Code Example

The fallback is automatic, but you can see the source in the response:

```python
from app.services import StockService

# This will try Yahoo Finance, then fallbacks automatically
stock_info = StockService.get_stock_info('AAPL')

if stock_info:
    print(f"Price: ${stock_info['current_price']}")
    print(f"Source: {stock_info['source']}")  # Shows which API was used
```

## Files Modified

- `app/services/stock_service.py` - Enhanced with fallback logic
- `app/services/alternative_data_sources.py` - New fallback service classes
- `.env` - API key configuration

## Benefits

✅ **No more 404 errors** when Yahoo Finance is rate-limited
✅ **Automatic switching** between data sources
✅ **No code changes** required in routes/frontend
✅ **Free tier friendly** - combines limits from multiple sources
✅ **Production ready** - can upgrade individual services as needed

## Alternative: Local Database

For production apps with heavy traffic, consider:

1. **Daily data import** - Load stocks into database after market close
2. **Serve from database** - No API calls during normal use
3. **Live updates only** - Use APIs only for real-time updates

This approach eliminates rate limit issues entirely.

---

**Summary:** The app now has intelligent fallback to multiple free stock data APIs. Get at least one API key (Finnhub recommended) to avoid rate limiting issues!
