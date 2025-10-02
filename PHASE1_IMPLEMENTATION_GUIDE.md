# KI-Analyse Enhancement - Detaillierter Implementierungsplan

**Status:** ✅ Alle Änderungen gepusht an GitHub  
**Next:** Phase 1 Implementierung

---

## Phase 1: Datenanreicherung (PRIORITY)

### 1.1 Analystenbewertungen & Kursziele

#### Backend: `app/services/stock_service.py`

**Neue Methode hinzufügen:**
```python
@staticmethod
def get_analyst_ratings(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Get analyst ratings and price targets from Finnhub
    Endpoint: https://finnhub.io/api/v1/stock/recommendation?symbol={ticker}
    Returns last 4 quarters of ratings
    """
    api_key = os.getenv('FINNHUB_API_KEY')
    if not api_key:
        return None
    
    try:
        url = f"https://finnhub.io/api/v1/stock/recommendation"
        params = {'symbol': ticker.upper(), 'token': api_key}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data or len(data) == 0:
            return None
        
        # Get most recent rating
        latest = data[0]
        
        return {
            'buy': latest.get('buy', 0),
            'hold': latest.get('hold', 0),
            'sell': latest.get('sell', 0),
            'strong_buy': latest.get('strongBuy', 0),
            'strong_sell': latest.get('strongSell', 0),
            'period': latest.get('period', ''),
            'total_analysts': sum([
                latest.get('buy', 0),
                latest.get('hold', 0),
                latest.get('sell', 0),
                latest.get('strongBuy', 0),
                latest.get('strongSell', 0)
            ])
        }
    except Exception as e:
        logger.error(f"Error getting analyst ratings for {ticker}: {e}")
        return None

@staticmethod
def get_price_target(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Get analyst price targets from Finnhub
    Endpoint: https://finnhub.io/api/v1/stock/price-target?symbol={ticker}
    """
    api_key = os.getenv('FINNHUB_API_KEY')
    if not api_key:
        return None
    
    try:
        url = f"https://finnhub.io/api/v1/stock/price-target"
        params = {'symbol': ticker.upper(), 'token': api_key}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return None
        
        return {
            'target_high': data.get('targetHigh'),
            'target_low': data.get('targetLow'),
            'target_mean': data.get('targetMean'),
            'target_median': data.get('targetMedian'),
            'last_updated': data.get('lastUpdated'),
            'number_analysts': data.get('numberOfAnalysts', 0)
        }
    except Exception as e:
        logger.error(f"Error getting price target for {ticker}: {e}")
        return None
```

**Integration in `get_stock_info()`:**
```python
# Nach Zeile 34 hinzufügen:
# Get analyst data
analyst_ratings = StockService.get_analyst_ratings(ticker)
if analyst_ratings:
    processed_info['analyst_ratings'] = analyst_ratings

price_target = StockService.get_price_target(ticker)
if price_target:
    processed_info['price_target'] = price_target
```

---

### 1.2 Insider-Transaktionen

**Neue Methode in `stock_service.py`:**
```python
@staticmethod
def get_insider_transactions(ticker: str, days_back: int = 180) -> Optional[Dict[str, Any]]:
    """
    Get insider transactions from Finnhub
    Endpoint: https://finnhub.io/api/v1/stock/insider-transactions?symbol={ticker}
    Returns last 6 months by default
    """
    api_key = os.getenv('FINNHUB_API_KEY')
    if not api_key:
        return None
    
    try:
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        url = f"https://finnhub.io/api/v1/stock/insider-transactions"
        params = {
            'symbol': ticker.upper(),
            'from': from_date,
            'token': api_key
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data or 'data' not in data:
            return None
        
        transactions = data['data']
        
        # Aggregate buy vs sell
        total_shares_bought = 0
        total_shares_sold = 0
        total_value_bought = 0
        total_value_sold = 0
        transaction_count = 0
        
        for tx in transactions:
            shares = tx.get('share', 0)
            change = tx.get('change', 0)
            
            if change > 0:  # Buy
                total_shares_bought += shares
                if 'price' in tx:
                    total_value_bought += shares * tx['price']
            elif change < 0:  # Sell
                total_shares_sold += abs(shares)
                if 'price' in tx:
                    total_value_sold += abs(shares) * tx['price']
            
            transaction_count += 1
        
        net_shares = total_shares_bought - total_shares_sold
        net_value = total_value_bought - total_value_sold
        
        return {
            'shares_bought': total_shares_bought,
            'shares_sold': total_shares_sold,
            'net_shares': net_shares,
            'value_bought': total_value_bought,
            'value_sold': total_value_sold,
            'net_value': net_value,
            'transaction_count': transaction_count,
            'period_days': days_back,
            'signal': 'bullish' if net_value > 0 else 'bearish' if net_value < 0 else 'neutral'
        }
    except Exception as e:
        logger.error(f"Error getting insider transactions for {ticker}: {e}")
        return None
```

**Integration:**
```python
# In get_stock_info() hinzufügen:
insider_data = StockService.get_insider_transactions(ticker)
if insider_data:
    processed_info['insider_transactions'] = insider_data
```

---

### 1.3 News-Sentiment Aggregation

**Erweiterung in `app/services/news_service.py`:**
```python
@staticmethod
def get_aggregated_sentiment(ticker: str, days: int = 7) -> Dict[str, Any]:
    """
    Get news and aggregate sentiment scores
    Returns overall sentiment analysis
    """
    news = NewsService.get_company_news(ticker, days=days, limit=20)
    
    if not news or 'news' not in news:
        return {
            'overall_score': 0,
            'sentiment_distribution': {'bullish': 0, 'neutral': 0, 'bearish': 0},
            'article_count': 0
        }
    
    articles = news['news']
    bullish_count = 0
    neutral_count = 0
    bearish_count = 0
    
    for article in articles:
        sentiment = article.get('sentiment', 'neutral')
        if sentiment == 'bullish':
            bullish_count += 1
        elif sentiment == 'bearish':
            bearish_count += 1
        else:
            neutral_count += 1
    
    total = len(articles)
    
    # Calculate overall score (-1 to +1)
    if total > 0:
        bullish_pct = bullish_count / total
        bearish_pct = bearish_count / total
        overall_score = bullish_pct - bearish_pct
    else:
        overall_score = 0
    
    return {
        'overall_score': round(overall_score, 2),
        'sentiment_distribution': {
            'bullish': bullish_count,
            'neutral': neutral_count,
            'bearish': bearish_count
        },
        'sentiment_percentages': {
            'bullish_pct': round(bullish_count / total * 100, 1) if total > 0 else 0,
            'neutral_pct': round(neutral_count / total * 100, 1) if total > 0 else 0,
            'bearish_pct': round(bearish_count / total * 100, 1) if total > 0 else 0
        },
        'article_count': total,
        'period_days': days
    }
```

**Integration in `stock.py` Route:**
```python
# In GET /api/stock/<ticker>/analyze-with-ai:
from app.services.news_service import NewsService

# Nach dem get_stock_info():
news_sentiment = NewsService.get_aggregated_sentiment(ticker, days=7)
```

---

### 1.4 AI Service Prompt Enhancement

**In `app/services/ai_service.py` - Methode `_create_analysis_prompt()`:**

**Nach der fundamentals section hinzufügen:**
```python
# Analyst Consensus (if available)
if stock_data.get('analyst_ratings'):
    ratings = stock_data['analyst_ratings']
    total = ratings['total_analysts']
    prompt += f"""

## Analyst Consensus:
- Total Analysts: {total}
- Strong Buy: {ratings['strong_buy']}
- Buy: {ratings['buy']}
- Hold: {ratings['hold']}
- Sell: {ratings['sell']}
- Strong Sell: {ratings['strong_sell']}
"""

if stock_data.get('price_target'):
    target = stock_data['price_target']
    prompt += f"""
- Average Price Target: ${target['target_mean']:.2f}
- Target Range: ${target['target_low']:.2f} - ${target['target_high']:.2f}
- Number of Estimates: {target['number_analysts']}

**TASK**: Compare your analysis with the analyst consensus. If your recommendation differs significantly, explain why. Are the analysts missing something, or is there information they have that supports their view?
"""

# Insider Activity (if available)
if stock_data.get('insider_transactions'):
    insider = stock_data['insider_transactions']
    signal_emoji = "🟢" if insider['signal'] == 'bullish' else "🔴" if insider['signal'] == 'bearish' else "⚪"
    prompt += f"""

## Insider Transactions (Last {insider['period_days']} days):
{signal_emoji} Signal: {insider['signal'].upper()}
- Shares Bought: {insider['shares_bought']:,}
- Shares Sold: {insider['shares_sold']:,}
- Net Position: {insider['net_shares']:,} shares
- Net Value: ${insider['net_value']:,.0f}
- Total Transactions: {insider['transaction_count']}

**TASK**: Interpret this insider activity. Does management show confidence in the company by buying shares, or are they selling? This can be a strong signal about the company's near-term prospects.
"""

# News Sentiment (if available)
if 'news_sentiment' in locals() and news_sentiment:  # Passed separately
    sent = news_sentiment
    sentiment_emoji = "🟢" if sent['overall_score'] > 0.2 else "🔴" if sent['overall_score'] < -0.2 else "⚪"
    prompt += f"""

## Recent News Sentiment (Last {sent['period_days']} days):
{sentiment_emoji} Overall Score: {sent['overall_score']:.2f} (-1 to +1 scale)
- Bullish Articles: {sent['sentiment_percentages']['bullish_pct']}%
- Neutral Articles: {sent['sentiment_percentages']['neutral_pct']}%
- Bearish Articles: {sent['sentiment_percentages']['bearish_pct']}%
- Total Articles Analyzed: {sent['article_count']}

**TASK**: Consider this news sentiment in your short-term outlook. A highly positive sentiment can drive near-term momentum, while negative sentiment may create buying opportunities or signal risks.
"""
```

**Aktualisiere `analyze_stock_with_ai()` Signatur:**
```python
@staticmethod
def analyze_stock_with_ai(stock_data: Dict[str, Any], news_sentiment: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Analyze stock using AI with enhanced data
    
    Args:
        stock_data: Stock information including technicals, fundamentals
        news_sentiment: Aggregated news sentiment data (optional)
    """
    # Pass news_sentiment to _create_analysis_prompt
    prompt = AIService._create_analysis_prompt(stock_data, news_sentiment=news_sentiment)
    # ... rest of method
```

**Update `_create_analysis_prompt()` Signatur:**
```python
@staticmethod
def _create_analysis_prompt(stock_data: Dict[str, Any], news_sentiment: Optional[Dict[str, Any]] = None) -> str:
    # ... existing code ...
```

---

## Testing Checklist

### Phase 1.1 - Analyst Data:
- [ ] Test `get_analyst_ratings('AAPL')`
- [ ] Test `get_price_target('AAPL')`
- [ ] Verify data appears in `get_stock_info()` response
- [ ] Check AI prompt includes analyst consensus
- [ ] Verify AI mentions analysts in response

### Phase 1.2 - Insider Data:
- [ ] Test `get_insider_transactions('AAPL')`
- [ ] Verify bullish/bearish/neutral signal calculation
- [ ] Check data in `get_stock_info()` response
- [ ] Verify AI interprets insider activity

### Phase 1.3 - News Sentiment:
- [ ] Test `get_aggregated_sentiment('AAPL')`
- [ ] Verify percentages sum to 100%
- [ ] Check overall score calculation (-1 to +1)
- [ ] Verify AI considers sentiment in analysis

### Complete Integration:
- [ ] Analyze stock with all new data
- [ ] Check console logs for errors
- [ ] Verify AI response quality improved
- [ ] Test with multiple tickers (AAPL, GME, TSLA)

---

## API Rate Limits to Watch

**Finnhub Free Tier:**
- 60 requests/minute
- With new endpoints: 5 calls per ticker analysis
  1. Quote
  2. Company Info
  3. Analyst Ratings
  4. Price Target
  5. Insider Transactions

**Solution:** Cache aggressively (use existing StockCache model)

---

## Next Steps After Phase 1

1. Test all new endpoints
2. Verify AI responses improved
3. Document changes in CLAUDE.md
4. Commit and push
5. Begin Phase 2 (Visual Charts)

---

**Implementation Time Estimate:** 2-3 hours  
**Testing Time:** 30 minutes  
**Documentation:** 15 minutes

**Total:** ~3 hours for complete Phase 1
