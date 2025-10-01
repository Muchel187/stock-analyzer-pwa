# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Stock Analyzer PWA - A Progressive Web App for stock analysis and portfolio management with multi-source data fallback. Built with Flask backend, vanilla JavaScript frontend, and supports both US stocks and DAX market analysis.

**Key Features:**
- Portfolio tracking with transaction history
- Watchlist management with price tracking
- Stock screener with preset strategies
- Price alerts system
- AI-powered stock analysis (OpenAI integration)
- Multi-source data fallback (Yahoo Finance, Finnhub, Twelve Data, Alpha Vantage)

## Development Commands

### Running the Application

```bash
# Development server
source venv/bin/activate
python app.py

# With Docker
docker-compose up -d
```

### Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py

# Run integration tests
pytest tests/test_integration.py

# Run single test
pytest tests/test_portfolio.py::test_add_transaction
```

### Database

```bash
# Initialize database (creates tables)
# Tables are auto-created on first run via create_all() in app.py

# For migrations (if flask-migrate is configured):
flask db init       # Initialize migrations (first time only)
flask db migrate    # Generate migration
flask db upgrade    # Apply migration
```

### Dependencies

```bash
# Install requirements
pip install -r requirements.txt

# Update requirements
pip freeze > requirements.txt
```

## Architecture

### Application Factory Pattern

The app uses Flask's application factory pattern in `app/__init__.py`:
- Extensions initialized globally, then bound to app instance
- Blueprints registered for modular routing
- Configuration loaded from `config.py` based on environment

**Critical: JWT Identity Type**
- JWT `identity` MUST be a string: `create_access_token(identity=str(user.id))`
- User loaders in `app/__init__.py` convert string back to int for database queries
- This was a major bug that caused 422 errors - always use `str(user.id)`

### Multi-Source Data Fallback System

**Location:** `app/services/stock_service.py` + `app/services/alternative_data_sources.py`

Yahoo Finance (via yfinance) is the primary data source but has strict rate limits (429 errors). The app implements automatic fallback:

1. **Yahoo Finance** (yfinance) - Primary source, comprehensive data
2. **Finnhub API** - First fallback (60 req/min free) - real-time quotes
3. **Twelve Data API** - Second fallback (800 req/day free) - historical data
4. **Alpha Vantage API** - Third fallback (25 req/day free) - fundamentals

**How it works:**
- `StockService.get_stock_info()` tries Yahoo Finance first
- On 429 error or failure, automatically tries `FallbackDataService.get_stock_quote()`
- `FallbackDataService` iterates through configured APIs until one succeeds
- All responses normalized to common format with `source` field indicating which API was used
- Results cached for 1 hour (configurable via `STOCKS_CACHE_TIMEOUT`)

**Setup:**
- API keys configured in `.env` file
- See `FALLBACK_DATA_SOURCES.md` for detailed setup instructions
- App works without API keys but limited to cached data when Yahoo fails

### Service Layer Architecture

Services contain business logic, routes handle HTTP:

- **`stock_service.py`** - Stock data fetching, caching, technical analysis
- **`portfolio_service.py`** - Portfolio calculations, performance metrics
- **`screener_service.py`** - Stock screening logic, preset strategies
- **`alert_service.py`** - Alert checking, notification sending
- **`ai_service.py`** - OpenAI integration for stock analysis
- **`alternative_data_sources.py`** - Multi-source API fallback implementation

### Models & Relationships

```
User (1) ─→ (N) Portfolio (1) ─→ (N) Transaction
     (1) ─→ (N) Watchlist
     (1) ─→ (N) Alert

StockCache - Shared cache table for all stock data
```

**Important Model Methods:**
- `Portfolio.calculate_performance()` - Computes gains, returns, current value
- `Watchlist.update_price()` - Updates current price and tracks changes
- `Alert.check_condition()` - Evaluates if alert should trigger
- `StockCache.get_cached()` / `set_cache()` - Database-level caching

### Authentication

**Dual System:** Flask-Login (sessions) + JWT (API)

- Flask-Login used for template-based views
- JWT used for API endpoints (`@jwt_required()`)
- Both user loaders defined in `app/__init__.py`
- **Critical:** JWT identity must be string, loaders convert to int

**Registration/Login Flow:**
1. User submits credentials to `/api/auth/register` or `/api/auth/login`
2. Password hashed with bcrypt (`User.set_password()`)
3. JWT tokens generated: `access_token` (24h), `refresh_token` (30d)
4. Frontend stores tokens in localStorage
5. Tokens sent in `Authorization: Bearer <token>` header

### Frontend Architecture (Vanilla JS SPA)

**Main files:**
- `static/js/app.js` - Main app controller, routing, page management
- `static/js/api.js` - API service layer, handles all HTTP requests
- `static/js/components.js` - Reusable UI components
- `static/js/charts.js` - Chart.js wrapper functions

**PWA Components:**
- `static/sw.js` - Service Worker for offline caching
- `static/manifest.json` - PWA manifest for installation
- Cache-first strategy for static assets, network-first for API

**State Management:**
- JWT tokens in localStorage
- User data in memory (`window.currentUser`)
- No complex state management library - direct DOM manipulation

## Configuration & Environment

### Environment Variables (`.env`)

**Required for basic functionality:**
```bash
FLASK_ENV=development
SECRET_KEY=<strong-secret>
JWT_SECRET_KEY=<strong-secret>
DATABASE_URL=sqlite:///stockanalyzer.db  # or postgresql://...
```

**Optional but recommended for full functionality:**
```bash
# Stock data fallback APIs
FINNHUB_API_KEY=<key>           # 60 req/min free
TWELVE_DATA_API_KEY=<key>       # 800 req/day free
ALPHA_VANTAGE_API_KEY=<key>     # 25 req/day free

# AI analysis
OPENAI_API_KEY=<key>

# Email alerts
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=<email>
MAIL_PASSWORD=<app-password>

# Caching
REDIS_URL=redis://localhost:6379/0  # Optional, uses simple cache if not set
STOCKS_CACHE_TIMEOUT=3600  # 1 hour
```

### Configuration Classes (`config.py`)

- `DevelopmentConfig` - Debug enabled, SQLite default
- `ProductionConfig` - Debug disabled, requires PostgreSQL
- `TestingConfig` - In-memory SQLite, CSRF disabled

**Database URL Compatibility:**
Config automatically converts `postgres://` to `postgresql://` for SQLAlchemy 2.0 compatibility.

## Common Patterns & Gotchas

### Error Handling Pattern

All routes follow this pattern:
```python
try:
    # Business logic
    return jsonify({'success': True}), 200
except Exception as e:
    db.session.rollback()  # If database operations involved
    return jsonify({'error': str(e)}), 500
```

### Caching Strategy

**Two-level caching:**
1. **Database cache** (`StockCache` model) - Persistent, survives restarts
2. **Memory cache** (Flask-Cache/Redis) - Fast, temporary

Check database cache first, then fetch from API, then save to both caches.

### Service Worker Static File Serving

**Critical Fix:** Static files (sw.js, manifest.json) must use `current_app.static_folder`:

```python
# WRONG - causes 404s
return send_from_directory('static', 'sw.js')

# CORRECT
from flask import current_app
return send_from_directory(current_app.static_folder, 'sw.js')
```

### JWT Optional Authentication

**Avoid** `@jwt_required(optional=True)` - causes 422 errors when no token present.

Instead, use separate endpoints or handle missing auth manually:
```python
from flask_jwt_extended import get_jwt_identity

@bp.route('/data')
def get_data():
    user_id = get_jwt_identity()  # Returns None if not authenticated
    if user_id:
        # Personalized data
    else:
        # Public data
```

## Background Jobs & Scheduler

**Location:** `jobs/scheduler.py`

Currently **disabled** in `app/__init__.py` (lines 93-97) to avoid startup errors.

When enabled, runs periodic tasks:
- Portfolio value updates (5 min interval)
- Alert checking (1 min interval)
- Stock cache refresh (configurable)

**To enable:**
1. Uncomment scheduler setup in `app/__init__.py`
2. Ensure database migrations are complete
3. Test that all scheduled jobs run without errors

## Testing Strategy

**Test Structure:**
- `tests/conftest.py` - Fixtures (app, client, auth tokens)
- `tests/test_auth.py` - Authentication endpoints
- `tests/test_portfolio.py` - Portfolio CRUD operations
- `tests/test_stock_service.py` - Stock data fetching
- `tests/test_integration.py` - End-to-end workflows

**Key Fixtures:**
- `app` - Flask app with testing config (in-memory DB)
- `client` - Test client for making requests
- `auth_headers` - Headers with valid JWT token
- `sample_user` - Registered test user

**Running specific tests:**
```bash
# Test a specific function
pytest tests/test_portfolio.py::test_add_transaction -v

# Test with print output
pytest tests/test_auth.py -s

# Stop on first failure
pytest tests/ -x
```

## Known Issues & Solutions

### Yahoo Finance Rate Limiting (429 Errors)

**Problem:** Yahoo Finance API limits requests aggressively
**Solution:** Multi-source fallback system automatically tries alternative APIs
**Workaround:** Get free API keys from Finnhub, Twelve Data, or Alpha Vantage (see `FALLBACK_DATA_SOURCES.md`)

### JWT "Subject must be a string" Error

**Problem:** JWT library requires string identity
**Solution:** Always use `str(user.id)` when creating tokens
**Location:** Fixed in `app/routes/auth.py` lines 38, 39, 66, 67

### Service Worker 404 Errors

**Problem:** `send_from_directory('static', ...)` doesn't work correctly
**Solution:** Use `send_from_directory(current_app.static_folder, ...)`
**Location:** Fixed in `app/routes/main.py`

## Docker Deployment

**Services in `docker-compose.yml`:**
- `web` - Flask app (gunicorn in production)
- `db` - PostgreSQL database
- `redis` - Cache layer
- `nginx` - Reverse proxy (production only)

**Development:**
```bash
docker-compose up -d
docker-compose logs -f web
```

**Production:**
- Update `.env` with production settings
- Set `FLASK_ENV=production`
- Use strong `SECRET_KEY` and `JWT_SECRET_KEY`
- Configure SSL/TLS in nginx.conf

## API Documentation

All API endpoints follow RESTful conventions. See `README.md` for complete endpoint list.

**Base URL:** `/api`

**Authentication:** Bearer token in Authorization header (except auth endpoints)

**Response Format:**
```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful"
}
```

**Error Format:**
```json
{
  "error": "Error message",
  "status": 400
}
```

## Additional Resources

- **`FALLBACK_DATA_SOURCES.md`** - Complete guide to setting up alternative stock data APIs
- **`TESTING_RESULTS.md`** - Test results and known issues documentation
- **`WICHTIG_YAHOO_FINANCE.md`** - Yahoo Finance rate limiting explanation
- **`README.md`** - User-facing documentation and setup guide
