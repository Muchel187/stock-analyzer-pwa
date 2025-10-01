# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application

```bash
# Development server
source venv/bin/activate
python app.py
# Server runs on http://127.0.0.1:5000

# Kill existing server on port 5000
lsof -ti:5000 | xargs kill -9 2>/dev/null || true

# With Docker
docker-compose up -d
docker-compose logs -f web
```

### Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_stock_service.py

# Run single test
pytest tests/test_portfolio.py::test_add_transaction -v
```

### Database

```bash
# Initialize database
flask db upgrade

# Create new migration
flask db migrate -m "description"

# Downgrade migration
flask db downgrade
```

## Architecture Overview

### Application Factory Pattern

The app uses Flask's application factory pattern in `app/__init__.py`:
- Extensions initialized globally, then bound to app instance in `create_app()`
- Blueprints registered for modular routing (auth, stock, portfolio, watchlist, screener, alerts, main)
- Configuration loaded from `config.py` based on environment

**Critical: JWT Identity Type**
- JWT `identity` MUST be a string: `create_access_token(identity=str(user.id))`
- User loaders in `app/__init__.py` convert string back to int for database queries
- Using `int` directly causes "unhashable type" errors

### Multi-Source Stock Data Fallback System

**CRITICAL CHANGE**: Yahoo Finance (yfinance) has been **completely removed** from the codebase due to severe rate limiting issues.

**Data Source Priority** (`app/services/alternative_data_sources.py`):
1. **Finnhub API** (Primary) - 60 requests/minute, real-time quotes
2. **Twelve Data API** (Secondary) - 800 requests/day, historical data
3. **Alpha Vantage API** (Tertiary) - 25 requests/day, fundamentals

**Implementation:**
- `FallbackDataService` class in `alternative_data_sources.py` provides three service classes
- `StockService.get_stock_info()` calls `FallbackDataService.get_stock_quote()` directly
- No more yfinance imports anywhere in the codebase
- All responses include `"source"` field indicating which API provided the data
- `StockCache` model provides database-level caching with configurable TTL

**Important**: NEVER import or use `yfinance`, `yf`, or `yf.Ticker()`. All stock data must go through `FallbackDataService`.

**Setup:**
- API keys configured in `.env`: `FINNHUB_API_KEY`, `TWELVE_DATA_API_KEY`, `ALPHA_VANTAGE_API_KEY`
- App works with any combination of API keys; tries each in order until one succeeds
- See `AI_SETUP.md` for detailed API setup instructions

### AI Analysis System

**Dual Provider Support** (`app/services/ai_service.py`):
- **Google Gemini 2.5 Flash** (preferred) - Configured via `GOOGLE_API_KEY`
- **OpenAI GPT-4** (fallback) - Configured via `OPENAI_API_KEY`

**Provider Selection:**
- Checks for `GOOGLE_API_KEY` first, uses Gemini if available
- Falls back to OpenAI if only `OPENAI_API_KEY` is set
- Logs which provider is being used on initialization

**AI Response Structure:**
- Prompts explicitly request: Technical Analysis, Fundamental Analysis, Risks, Opportunities, **Price Target**, **Short Squeeze Potential**, and Recommendation
- Responses parsed into structured sections in `_parse_ai_response()`
- Price targets extracted with regex patterns for display
- Short squeeze scores (0-100) extracted and visualized with flame animation

### Visual AI Analysis System

**Location:** `static/js/ai-analysis.js` + `static/css/ai-analysis.css`

**Key Components:**
- `AIAnalysisVisualizer` class handles all rendering
- Chart.js 4.x for radar charts, bar charts, gauge charts (doughnut with center text)
- Executive summary with recommendation, price target, and confidence score
- Score cards for Technical, Fundamental, Value, and Momentum metrics
- Radar chart for 5-dimensional fundamental analysis
- Risk vs. Opportunities bar chart
- **Technical Analysis Visualization** (`app.js`):
  - RSI Gauge Chart (doughnut with center text plugin)
  - MACD Bar Chart (histogram visualization)
  - Bollinger Bands Position (stacked horizontal bar)
  - Volatility Gauge Chart
  - Moving Averages Comparison Bar Chart
  - Price Changes Grid (1d, 1w, 1m, volume)
- **Short Squeeze Indicator** (`ai-analysis.js`):
  - Flame animation visualization (1-5 flames based on 0-100 score)
  - Color-coded severity levels (Minimal/Low/Moderate/High/Extreme)
  - Due diligence factors extraction (short interest %, days to cover, volume, sentiment)
  - Pulsing animation for extreme scores (80+)
- Expandable detailed analysis sections

**Integration:**
- Instantiated in `app.js` constructor: `this.aiVisualizer = new AIAnalysisVisualizer()`
- Called when AI tab is selected: `aiVisualizer.renderAnalysis(ticker, currentStockPrice)`
- Current price passed for upside calculation on price targets
- Fetches from `GET /api/stock/{ticker}/analyze-with-ai`

**Price Target Feature:**
- Extracted from AI response using multiple regex patterns
- Calculates upside/downside vs current price
- Displayed prominently in recommendation box
- Color-coded (green for positive, red for negative)

### Service Layer Architecture

All business logic resides in service classes (`app/services/`):

- **`stock_service.py`** - Stock data retrieval, technical indicators, fundamental analysis
- **`alternative_data_sources.py`** - Multi-source API fallback (Finnhub, Twelve Data, Alpha Vantage)
- **`portfolio_service.py`** - Portfolio calculations, performance tracking
- **`screener_service.py`** - Stock screening with preset strategies
- **`ai_service.py`** - AI-powered analysis with dual provider support
- **`alert_service.py`** - Price alert management

**Critical Pattern**: Services use class methods and are stateless. They interact with models and external APIs but don't handle HTTP concerns.

**Screener Threading Fix:**
- `ScreenerService` uses **sequential execution** instead of `ThreadPoolExecutor`
- Parallel execution caused "Working outside of application context" errors
- Sequential is slower but prevents Flask context issues

### Frontend Architecture

**Pure Vanilla JavaScript** with modular design:

- **`static/js/app.js`** - Main application controller (`StockAnalyzerApp` class)
- **`static/js/api.js`** - Centralized API client with fetch wrapper
- **`static/js/charts.js`** - Chart.js visualization utilities
- **`static/js/ai-analysis.js`** - AI visualization module (`AIAnalysisVisualizer` class)
- **`static/js/components.js`** - Reusable UI components

**State Management:**
- App instance stores `currentAnalysisTicker` and `currentStockPrice` for tab-based loading
- JWT tokens in localStorage
- No complex state management framework

**Tab System:**
- Analysis page has 4 tabs: Übersicht, Technisch, Fundamental, KI-Analyse
- AI tab lazily loads content when switched to
- Technical tab initializes charts when switched to (using `setTimeout` for DOM readiness)
- Prevents unnecessary API calls

**Watchlist Integration:**
- "Zur Watchlist hinzufügen" button in Overview tab of stock analysis
- `addToWatchlistFromAnalysis()` method uses stored `currentAnalysisTicker`
- Styled with gradient button and star icon (⭐)
- Detects if stock already in watchlist and shows appropriate notification

### PWA Implementation

- **Service Worker** (`static/sw.js`) - Caches static assets and API responses
- **Manifest** (`static/manifest.json`) - App metadata for installation
- **Offline Support** - Fallback offline page and cached content
- **Cache-first** strategy for static assets, **network-first** for API calls

## Configuration & Environment

### Environment Variables (`.env`)

**Required for basic functionality:**
```bash
FLASK_ENV=development
SECRET_KEY=<strong-secret>
JWT_SECRET_KEY=<strong-secret>
DATABASE_URL=sqlite:///stockanalyzer.db  # or postgresql://...
```

**Required for stock data (at least one API key needed):**
```bash
FINNHUB_API_KEY=<key>           # Primary: 60 req/min free
TWELVE_DATA_API_KEY=<key>       # Secondary: 800 req/day free
ALPHA_VANTAGE_API_KEY=<key>     # Tertiary: 25 req/day free
```

**Required for AI analysis (choose one):**
```bash
GOOGLE_API_KEY=<key>            # Preferred: Gemini 2.5 Flash
OPENAI_API_KEY=<key>            # Fallback: GPT-4
```

**Optional:**
```bash
# Email alerts
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=<email>
MAIL_PASSWORD=<app-password>

# Caching
REDIS_URL=redis://localhost:6379/0  # Uses simple cache if not set
STOCKS_CACHE_TIMEOUT=3600            # 1 hour
```

## Critical Gotchas & Common Issues

### Flask Application Context in Threading

**Problem:** Using `ThreadPoolExecutor` in services causes "Working outside of application context" errors.

**Solution:** Use sequential execution in `ScreenerService`:
```python
# WRONG - causes context errors:
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(cls._screen_single_stock, ticker, criteria): ticker
               for ticker in stocks_to_screen}

# CORRECT - sequential execution:
for ticker in stocks_to_screen:
    result = cls._screen_single_stock(ticker, criteria)
    if result:
        screened_stocks.append(result)
```

**Location:** Fixed in `app/services/screener_service.py`

### JWT Identity Type

**Critical:** JWT identity must be a string, not integer.

```python
# CORRECT:
access_token = create_access_token(identity=str(user.id))

# WRONG - causes errors:
access_token = create_access_token(identity=user.id)
```

**Why:** JWT library requires string identities. User loaders convert back to int for DB queries.

### Never Import yfinance

**Critical:** yfinance has been completely removed from the codebase.

```python
# WRONG - DO NOT DO THIS:
import yfinance as yf
stock = yf.Ticker('AAPL')

# CORRECT:
from app.services.alternative_data_sources import FallbackDataService
data = FallbackDataService.get_stock_quote('AAPL')
```

**Why:** Yahoo Finance rate limits are too restrictive. Multi-source fallback is more reliable.

### Stock Data Caching

`StockCache` model requires `cache_type` to differentiate data:
- `'info'` - Stock quotes and basic info
- `'history'` - Historical price data
- `'analysis'` - Technical/fundamental analysis

Always specify cache type when getting/setting:
```python
StockCache.get_cached(ticker, 'info')
StockCache.set_cache(ticker, data, 'info')
```

### Chart.js Instance Management

Always destroy previous chart instances before creating new ones:
```javascript
if (this.radarChart) {
    this.radarChart.destroy();
}
this.radarChart = new Chart(ctx, config);
```

**Why:** Chart.js doesn't automatically clean up, causing memory leaks and render issues.

### Static File Serving in Flask

**Problem:** Service worker and manifest files get 404 errors.

**Solution:** Use `current_app.static_folder`:
```python
# WRONG:
return send_from_directory('static', 'sw.js')

# CORRECT:
from flask import current_app
return send_from_directory(current_app.static_folder, 'sw.js')
```

## Models & Relationships

```
User (1) ─→ (N) Portfolio (1) ─→ (N) Transaction
     (1) ─→ (N) WatchlistItem
     (1) ─→ (N) Alert

StockCache - Global cache table (not user-specific)
```

**Important Model Methods:**
- `Portfolio.calculate_performance()` - Computes gains, returns, current value
- `WatchlistItem.update_price()` - Updates current price and tracks changes
- `Alert.check_condition()` - Evaluates if alert should trigger
- `StockCache.get_cached()` / `set_cache()` - Database-level caching with TTL

## Testing Strategy

**Test Structure:**
- `tests/conftest.py` - Fixtures (app, client, auth tokens)
- `tests/test_auth.py` - Authentication endpoints
- `tests/test_portfolio.py` - Portfolio CRUD
- `tests/test_stock_service.py` - Stock data fetching
- `tests/test_integration.py` - End-to-end workflows

**Key Fixtures:**
- `app` - Flask app with testing config (in-memory DB)
- `client` - Test client for requests
- `auth_headers` - Headers with valid JWT token
- `sample_user` - Registered test user

## API Endpoints

### Stock Data
- `GET /api/stock/<ticker>` - Get stock info, technical, fundamental data
- `GET /api/stock/<ticker>/history?period=1mo` - Historical prices
- `GET /api/stock/<ticker>/analyze-with-ai` - AI-powered analysis (NEW)
- `POST /api/stock/analyze-with-ai` - AI analysis via POST (legacy)
- `POST /api/stock/ai-recommendations` - AI-powered top buy/sell recommendations (US + German markets) **[NEW]**
- `GET /api/stock/recommendations` - Recommended stocks (screener-based)
- `POST /api/stock/batch` - Batch quote fetching
- `GET /api/stock/search?q=AAPL` - Search stocks

### Portfolio
- `GET /api/portfolio/` - Get user portfolio
- `POST /api/portfolio/transaction` - Add transaction
- `GET /api/portfolio/transactions` - Transaction history
- `GET /api/portfolio/performance` - Performance metrics

### Watchlist
- `GET /api/watchlist/` - Get watchlist
- `POST /api/watchlist/` - Add stock to watchlist
- `DELETE /api/watchlist/<ticker>` - Remove from watchlist

### Screener
- `POST /api/screener/` - Custom screening
- `GET /api/screener/presets` - List preset strategies
- `POST /api/screener/presets/<name>` - Apply preset strategy

### Alerts
- `GET /api/alerts/` - Get user alerts
- `POST /api/alerts/` - Create alert
- `PUT /api/alerts/<id>` - Update alert
- `DELETE /api/alerts/<id>` - Delete alert

### Auth
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh JWT token
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update profile

## Known Issues & Solutions

### Yahoo Finance Rate Limiting
**Status:** RESOLVED - Yahoo Finance completely removed from codebase
**Solution:** Multi-source fallback system using Finnhub, Twelve Data, and Alpha Vantage

### Screener Flask Context Errors
**Status:** RESOLVED - Sequential execution implemented
**Details:** ThreadPoolExecutor caused "Working outside of application context" errors
**Solution:** Changed to sequential processing in `screener_service.py`

### AI Response Parsing
**Status:** WORKING - Price target extraction may fail if AI uses non-standard format
**Details:** Uses regex patterns to extract price targets from text
**Workaround:** Extraction is optional; analysis still works without price target

### PWA Offline Mode
**Status:** KNOWN LIMITATION - Authentication tokens not handled securely offline
**Details:** Service worker caches API responses but doesn't manage JWT tokens properly
**Impact:** Users may see stale data or auth errors when offline

## Docker Deployment

**Services:**
- `web` - Flask app (gunicorn in production)
- `db` - PostgreSQL database
- `redis` - Cache layer
- `nginx` - Reverse proxy (production)

**Commands:**
```bash
# Development
docker-compose up -d
docker-compose logs -f web

# Production
docker-compose -f docker-compose.prod.yml up -d

# Rebuild after code changes
docker-compose build web
docker-compose restart web
```

## Additional Documentation

Project-specific documentation files:
- **`AI_VISUAL_ANALYSIS.md`** - Complete visual AI system documentation
- **`AI_SETUP.md`** - Step-by-step AI provider setup (Google Gemini & OpenAI)
- **`README.md`** - User-facing documentation and deployment guide
- **`FALLBACK_DATA_SOURCES.md`** - Multi-source stock API setup (if exists)

## New Features in This Session

### KI-Marktanalyse Dashboard Widget

**Location:** Dashboard page (`templates/index.html`), full-width widget

**Purpose:** AI-powered analysis of top US and German market stocks with buy/sell recommendations

**Backend Endpoint:** `POST /api/stock/ai-recommendations` (JWT-protected)
- Analyzes 20 top stocks from US (S&P 500) and German (DAX) markets
- Returns top 10 buy recommendations and top 10 sell recommendations
- Each recommendation includes: ticker, company name, price, confidence score, overall score, market flag (US/DE), summary

**Frontend Implementation:**
- `refreshAIRecommendations()` in `app.js` - Triggers analysis with loading state
- `displayAIRecommendations()` - Renders results in two-column grid
- `createAIRecommendationCard()` - Creates individual stock cards with ranking, confidence bar, badges
- `showStockDetails()` - Navigates to analysis page when card is clicked

**Styling:** `static/css/components.css` - AI recommendations section with gradient headers, confidence bars, responsive grid

**Performance:** Analysis can take 2-5 minutes depending on API response times. Limited to 20 stocks for performance.

### Watchlist Quick-Add from Analysis

**Feature:** "Zur Watchlist hinzufügen" button added to Overview tab in stock analysis page

**Implementation:**
- Button appears at top of overview tab with star icon and gradient styling
- `addToWatchlistFromAnalysis()` method in `app.js`
- Uses `currentAnalysisTicker` from app state
- Shows notification if stock already in watchlist
- Styled in `static/css/components.css` with hover effects and responsive design

### Visual Technical Analysis Charts

**Location:** Technical tab in stock analysis page (`app.js`)

**Charts Added:**
1. **RSI Gauge** - Doughnut chart with center text plugin showing RSI value (0-100)
2. **MACD Chart** - Bar chart showing MACD histogram
3. **Bollinger Bands** - Stacked horizontal bar showing position relative to bands
4. **Volatility Gauge** - Doughnut chart with volatility level
5. **Moving Averages** - Bar chart comparing SMA20, SMA50, SMA200, EMA12, EMA26
6. **Price Changes Grid** - Stats table showing 1d, 1w, 1m changes and volume

**Implementation Details:**
- Charts initialized lazily when Technical tab is selected
- `setTimeout` used to ensure DOM is ready before chart initialization
- All charts destroyed before recreation to prevent memory leaks
- Color-coded status indicators (overbought/oversold for RSI, bullish/bearish for MACD)

### Short Squeeze Indicator

**Location:** AI Analysis tab, displayed as prominent card with flame visualization

**Features:**
- AI analyzes short squeeze potential and assigns 0-100 score
- Score determines flame count (1-5 flames) and severity level
- Animated flames with flickering effect using CSS keyframes
- Pulsing effect for extreme scores (80+)
- Extracts due diligence factors: short interest %, days to cover, volume spikes, sentiment
- Color-coded levels: Minimal (<20), Low (20-39), Moderate (40-59), High (60-79), Extreme (80+)

**Implementation:**
- Backend: AI prompt in `ai_service.py` requests short squeeze analysis
- Frontend: `generateShortSqueezeIndicator()` in `ai-analysis.js`
- Helper methods: `extractSqueezeScore()`, `getFlameLevel()`, `generateFlames()`, `extractSqueezeFactors()`
- Styling: `static/css/ai-analysis.css` with flame animations

### Price Target with Upside Calculation

**Feature:** 12-month price target displayed in AI analysis with upside/downside percentage

**Implementation:**
- AI prompt explicitly requests price target with justification
- `extractPriceTarget()` method uses regex patterns to find target price in text
- Calculates upside: `((target - current) / current * 100)`
- Displays in prominent meter with color coding (green positive, red negative)
- Shown in recommendation section of AI analysis

## Phase 2: Interactive Charts & Stock Comparison (NEW - October 2025)

**Location:** Analysis page, integrated into existing tabs plus new Vergleich tab

### Interactive Price Chart Features

**Period Selector Buttons:** 1M, 3M, 6M, 1J, 2J, 5J, Max
- Clicking a period button reloads chart with new data
- Active button highlighted with primary color
- Period state stored in `this.currentPeriod`

**Moving Average Overlays:** Toggleable SMA 50 (green) and SMA 200 (red)
- Checkbox toggles above chart
- MAs calculated client-side using `calculateSMA()` method
- Only shown when sufficient historical data available (50+ or 200+ days)
- State persists when changing periods

**Volume Chart:** Bar chart below price chart
- Purple/blue bars showing daily trading volume
- Y-axis formatted in millions (M)
- Synchronized dates with price chart
- Separate Chart.js instance

**Chart.js Implementation:**
- Responsive line chart with gradient fill for price
- Dark theme compatible tooltips
- Grid lines with transparency
- Smooth line tension (0.4)
- Hover interactions show date and values

**Dynamic Updates:**
- Charts reload when period changes
- MAs recalculated when toggled
- Old chart instances properly destroyed before recreation

### Stock Comparison Feature

**Compare 2-4 Stocks:** New "Vergleich" tab in analysis page
- Input fields for 4 tickers (2 required, 2 optional)
- Period dropdown (1mo, 3mo, 6mo, 1y, 2y, 5y)
- First ticker pre-filled with current analysis stock
- "Vergleichen" button triggers comparison

**Comparison Metrics Table:**
- Displays key metrics in table format
- Rows include:
  - Company name
  - Current price
  - Market capitalization (in billions)
  - P/E ratio
  - Dividend yield (%)
  - Sector
  - RSI (technical indicator)
  - Volatility (annualized %)
  - 1-month price change (color-coded)
  - Trading volume
- Responsive table with horizontal scroll on mobile
- Missing values displayed as "-"

**Normalized Price Chart:**
- Line chart showing % change from start for all stocks
- Each ticker has unique color (purple, green, red, orange)
- All lines start at 0% for easy comparison
- Legend shows ticker names with colors
- Tooltip displays ticker and percentage change
- Y-axis formatted as percentage
- Chart height: 450px

### Backend Implementation

**Endpoint:** `POST /api/stock/compare`

**Parameters:**
- `tickers` (array, required): 2-4 stock tickers
- `period` (string, optional): Historical period (default: '1y')

**Response Structure:**
```json
{
  "comparison": [
    {
      "ticker": "AAPL",
      "company_name": "Apple Inc",
      "current_price": 255.52,
      "market_cap": 3778808.49,
      "pe_ratio": null,
      "dividend_yield": null,
      "sector": "Technology",
      "industry": "Consumer Electronics",
      "overall_score": 56.25,
      "rsi": 81.68,
      "volatility": 0.367,
      "price_change_1m": 6.49,
      "volume": 42263900
    }
  ],
  "price_histories": [
    {
      "ticker": "AAPL",
      "data": [
        {
          "date": "2025-08-20",
          "close": 226.01,
          "normalized": 0.0,
          "volume": 42263900
        }
      ]
    }
  ],
  "period": "1y",
  "timestamp": "2025-10-01T..."
}
```

**Validation:**
- Minimum 2 tickers required (returns 400 error)
- Maximum 4 tickers allowed (returns 400 error)
- Invalid tickers skipped (continues with valid ones)
- At least 2 valid tickers needed for response

**Data Processing:**
- Fetches stock info, fundamentals, and technical data for each ticker
- Retrieves historical price data for specified period
- Normalizes price data: `((price - start_price) / start_price * 100)`
- Returns both absolute and normalized data

### Frontend Implementation

**Key Methods in `app.js`:**

- `loadPriceChart(ticker, period)` - Main method to load and render price/volume charts
- `changePricePeriod(period)` - Handles period button clicks, updates active state
- `toggleMovingAverage(type)` - Shows/hides SMA50 or SMA200 overlays
- `calculateSMA(data, period)` - Computes simple moving average client-side
- `renderPriceChart(dates, prices, sma50, sma200)` - Creates Chart.js price chart
- `renderVolumeChart(dates, volumes)` - Creates Chart.js volume bar chart
- `runComparison()` - Triggers stock comparison API call
- `displayComparisonTable(comparison)` - Renders metrics table HTML
- `renderComparisonChart(priceHistories)` - Creates normalized line chart

**Chart Instance Management:**
- `this.priceChartInstance` - Main price chart
- `this.volumeChartInstance` - Volume bar chart
- `this.compareChartInstance` - Comparison line chart
- All instances destroyed before recreation to prevent memory leaks

**State Management:**
- `this.currentPeriod` - Currently selected period (default: '1y')
- `this.priceHistoryData` - Cached historical data for MA recalculation
- `this.showSMA50` - Boolean for SMA50 visibility
- `this.showSMA200` - Boolean for SMA200 visibility

**API Integration (`api.js`):**
- `async compareStocks(tickers, period)` - Calls `/api/stock/compare`
- Returns comparison data and price histories

### CSS Styling (`static/css/components.css`)

**New Styles Added:**
- `.chart-container` - Main chart wrapper with padding
- `.chart-header` - Flexbox header with title and controls
- `.chart-controls` - Container for period buttons and toggles
- `.period-buttons` - Button group with background and rounded corners
- `.period-btn` - Individual period button with hover and active states
- `.chart-toggles` - Checkbox labels for MA toggles
- `.toggle-label` - Styled checkbox labels with hover effects
- `.volume-chart-container` - Volume chart section with border-top
- `.compare-container` - Main comparison section wrapper
- `.compare-input-section` - Input area with background and padding
- `.compare-ticker-inputs` - Grid layout for ticker inputs
- `.compare-ticker-input` - Styled input fields (uppercase transform)
- `.compare-metrics-table` - Table container with responsive scroll
- `.compare-chart-card` - Chart card with padding and title

**Responsive Design:**
- Mobile breakpoints for smaller chart heights
- Grid layout adapts to single column on mobile
- Period buttons compress on small screens
- Table scrolls horizontally when needed

### Integration Points

**Analysis Page Flow:**
1. User analyzes stock (e.g., "AAPL")
2. Stock data loaded and displayed in tabs
3. Price chart automatically loads with 1Y period
4. User can change period or toggle MAs
5. User switches to "Vergleich" tab
6. First ticker pre-filled with "AAPL"
7. User enters additional tickers
8. Comparison runs and displays results

**Tab Persistence:**
- If user previously viewed "Vergleich" tab, it remains active
- localStorage key: `'lastAnalysisTab'`
- Restored in `restoreLastAnalysisTab()` method

**Loading States:**
- Price chart shows loading spinner during API call
- Comparison results show loading spinner during fetch
- Errors display notification toast

### Performance Considerations

- **Client-side MA Calculation:** Reduces server load, instant toggle response
- **Chart.js 4.x:** Efficient canvas rendering, handles large datasets well
- **Data Caching:** Historical data cached at StockService level
- **Chart Destruction:** Prevents memory leaks by destroying old instances
- **Normalized Data Server-side:** Reduces client-side computation
- **Lazy Loading:** Charts only render when tab is visible

### Known Limitations

**API Rate Limits:**
- Alpha Vantage: 25 requests/day for historical data
- Finnhub: 60 requests/minute for quotes
- After limits reached, cached data used or errors returned

**Data Availability:**
- Some stocks may not have 200 days of history for SMA200
- German stocks (.DE suffix) may have limited Finnhub support
- Missing fundamental data shows "-" in comparison table

**Browser Compatibility:**
- Requires Chart.js 4.x
- Canvas support required (all modern browsers)
- localStorage required for tab persistence

