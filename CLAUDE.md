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

