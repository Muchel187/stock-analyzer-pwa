# PHASE 3 & 4 QUICK REFERENCE

## 📋 Feature Priority Matrix

### Phase 3: High Impact, Low-Medium Effort (11 hours)

| Feature | Impact | Effort | Priority | Duration |
|---------|--------|--------|----------|----------|
| News Integration | ⭐⭐⭐⭐⭐ | 3h | 🔥 HIGH | 3.5h |
| Market Status | ⭐⭐⭐⭐ | 1h | 🔥 HIGH | 1h |
| Theme Toggle | ⭐⭐⭐⭐⭐ | 1.5h | 🔥 HIGH | 1.5h |
| Export Functionality | ⭐⭐⭐⭐ | 2h | 🟡 MEDIUM | 2h |
| Dashboard Customization | ⭐⭐⭐ | 3h | 🟡 MEDIUM | 3h |

### Phase 4: High Impact, Medium Effort (17 hours)

| Feature | Impact | Effort | Priority | Duration |
|---------|--------|--------|----------|----------|
| Portfolio Timeline | ⭐⭐⭐⭐⭐ | 4h | 🔥 HIGH | 4h |
| Risk Metrics | ⭐⭐⭐⭐⭐ | 2h | 🔥 HIGH | 2h |
| Advanced Indicators | ⭐⭐⭐⭐ | 3h | 🔥 HIGH | 3h |
| Earnings Calendar | ⭐⭐⭐⭐ | 2h | 🟡 MEDIUM | 2h |
| Correlation Matrix | ⭐⭐⭐ | 2h | 🟡 MEDIUM | 2h |
| Dividend Tracking | ⭐⭐⭐⭐ | 2h | 🟡 MEDIUM | 2h |
| UI/UX Enhancements | ⭐⭐⭐⭐ | 2h | 🟡 MEDIUM | 2h |

---

## 🎯 Implementation Checklist

### Phase 3 Tasks

#### 1. News Integration (3.5h)
- [ ] Create `app/services/news_service.py`
- [ ] Add endpoint `GET /api/stock/<ticker>/news`
- [ ] Integrate Finnhub News API
- [ ] Add sentiment analysis calculation
- [ ] Create news widget component
- [ ] Add news cards with styling
- [ ] Implement click handlers
- [ ] Add category filtering
- [ ] Test with multiple tickers

#### 2. Market Status Indicator (1h)
- [ ] Create `static/js/market-status.js`
- [ ] Implement market hours calculation
- [ ] Add timezone support
- [ ] Create status widget in navbar
- [ ] Add countdown timer
- [ ] Style with colors (green/red/yellow)
- [ ] Test with different timezones

#### 3. Theme Toggle (1.5h)
- [ ] Create `static/js/theme-manager.js`
- [ ] Add theme toggle button to navbar
- [ ] Implement localStorage persistence
- [ ] Create dark theme CSS variables
- [ ] Add smooth transitions
- [ ] Support system preference detection
- [ ] Test theme switching

#### 4. Export Functionality (2h)
- [ ] Install jsPDF and html2canvas
- [ ] Create `static/js/export-manager.js`
- [ ] Implement PDF export for analysis
- [ ] Implement CSV export for portfolio
- [ ] Implement CSV export for watchlist
- [ ] Add export buttons to UI
- [ ] Test downloads in different browsers

#### 5. Dashboard Customization (3h)
- [ ] Create `static/js/dashboard-customizer.js`
- [ ] Implement drag & drop with HTML5 API
- [ ] Add widget visibility toggles
- [ ] Create settings modal
- [ ] Save layout to localStorage
- [ ] Add dashboard templates
- [ ] Test layout persistence

---

### Phase 4 Tasks

#### 1. Portfolio Performance Timeline (4h)
- [ ] Create migration for `portfolio_history` table
- [ ] Add cron job for daily snapshots
- [ ] Create endpoint `GET /api/portfolio/history`
- [ ] Implement timeline chart rendering
- [ ] Add benchmark comparison (S&P 500)
- [ ] Add transaction markers
- [ ] Create sector allocation pie chart
- [ ] Implement performance attribution
- [ ] Test with sample data

#### 2. Risk Metrics (2h)
- [ ] Create `app/services/portfolio_analytics.py`
- [ ] Implement Sharpe ratio calculation
- [ ] Implement Beta calculation
- [ ] Implement Alpha calculation
- [ ] Implement max drawdown calculation
- [ ] Implement VaR calculation
- [ ] Create risk metrics dashboard card
- [ ] Test calculations with known values

#### 3. Advanced Technical Indicators (3h)
- [ ] Create `static/js/advanced-indicators.js`
- [ ] Implement MACD on chart
- [ ] Implement RSI overlay panel
- [ ] Implement Bollinger Bands on chart
- [ ] Implement Fibonacci levels
- [ ] Implement S&R detection
- [ ] Create indicator selection panel
- [ ] Test all indicators

#### 4. Earnings Calendar (2h)
- [ ] Add endpoint `GET /api/stock/<ticker>/earnings`
- [ ] Integrate Finnhub Earnings API
- [ ] Create earnings calendar widget
- [ ] Display next earnings date
- [ ] Show analyst estimates
- [ ] Create dashboard "This Week" widget
- [ ] Test with various tickers

#### 5. Correlation Matrix (2h)
- [ ] Implement correlation calculation
- [ ] Create heatmap visualization
- [ ] Calculate diversification score
- [ ] Add insights/suggestions
- [ ] Create correlation matrix card
- [ ] Test with portfolio data

#### 6. Dividend Tracking (2h)
- [ ] Create migration for `dividends` table
- [ ] Add endpoint `GET /api/portfolio/dividends`
- [ ] Create dividend calendar widget
- [ ] Implement dividend history
- [ ] Create dividend charts
- [ ] Add DRIP tracking
- [ ] Test dividend calculations

#### 7. UI/UX Enhancements (2h)
- [ ] Create `static/js/keyboard-shortcuts.js`
- [ ] Implement keyboard shortcuts
- [ ] Create command palette (Ctrl+K)
- [ ] Add onboarding tutorial
- [ ] Replace spinners with skeletons
- [ ] Test keyboard navigation

---

## 📊 API Endpoints to Create

### Phase 3
```
GET  /api/stock/<ticker>/news
     - Query params: limit, days
     - Returns: news articles with sentiment

GET  /api/market/status
     - Returns: market status for all exchanges
     
POST /api/export/analysis
     - Body: { ticker, format: 'pdf' }
     - Returns: PDF download
     
POST /api/export/portfolio
     - Body: { format: 'csv' }
     - Returns: CSV download
```

### Phase 4
```
GET  /api/portfolio/history
     - Query params: period, resolution
     - Returns: portfolio value over time
     
GET  /api/portfolio/risk-metrics
     - Returns: Sharpe, Beta, Alpha, MaxDD, VaR
     
GET  /api/stock/<ticker>/earnings
     - Returns: earnings calendar and history
     
GET  /api/portfolio/dividends
     - Returns: dividend calendar and history
     
GET  /api/portfolio/correlation
     - Returns: correlation matrix
```

---

## 🗄️ Database Migrations

### Phase 3 (No new tables)
- Uses existing tables + localStorage

### Phase 4 (4 new tables)

```sql
-- 1. Portfolio History
CREATE TABLE portfolio_history (
    id INTEGER PRIMARY KEY,
    portfolio_id INTEGER,
    date DATE,
    total_value DECIMAL(12,2),
    cash DECIMAL(12,2),
    invested DECIMAL(12,2),
    gain_loss DECIMAL(12,2),
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);

-- 2. Dividends
CREATE TABLE dividends (
    id INTEGER PRIMARY KEY,
    portfolio_id INTEGER,
    ticker VARCHAR(10),
    ex_date DATE,
    payment_date DATE,
    amount DECIMAL(10,2),
    shares DECIMAL(10,2),
    total DECIMAL(10,2),
    reinvested BOOLEAN,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);

-- 3. User Preferences
CREATE TABLE user_preferences (
    user_id INTEGER PRIMARY KEY,
    theme VARCHAR(20),
    dashboard_layout TEXT,
    default_currency VARCHAR(3),
    notifications_enabled BOOLEAN,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 4. News Bookmarks
CREATE TABLE news_bookmarks (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    ticker VARCHAR(10),
    headline TEXT,
    url TEXT,
    bookmarked_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 📦 New Dependencies

### Phase 3
```bash
# Frontend (CDN links)
- jsPDF (PDF generation)
- html2canvas (Chart capture)
- Papa Parse (CSV generation)

# Backend (requirements.txt)
# No new dependencies needed
```

### Phase 4
```bash
# Frontend
# No new dependencies (uses Chart.js)

# Backend
pip install numpy  # For portfolio analytics
pip install scipy  # For advanced calculations
```

---

## 🎨 CSS Classes to Add

### Phase 3
```css
/* Theme Toggle */
.theme-toggle-btn
.dark-theme (body class)
.high-contrast (body class)

/* News Widget */
.news-widget
.news-card
.news-thumbnail
.sentiment-badge
.sentiment-bullish
.sentiment-neutral
.sentiment-bearish

/* Market Status */
.market-status-indicator
.market-open
.market-closed
.market-pre-market
.market-after-hours
.countdown-timer

/* Dashboard Customization */
.dashboard-customizer
.widget-handle (drag handle)
.widget-settings
.layout-template

/* Export */
.export-menu
.export-btn
```

### Phase 4
```css
/* Portfolio Timeline */
.portfolio-timeline-card
.timeline-chart-container
.benchmark-legend

/* Risk Metrics */
.risk-metrics-grid
.metric-card
.metric-icon
.metric-value
.metric-description

/* Advanced Indicators */
.indicator-panel
.indicator-btn
.indicator-overlay

/* Earnings Calendar */
.earnings-card
.earnings-date
.earnings-estimates
.earnings-history

/* Correlation Matrix */
.correlation-matrix
.correlation-heatmap
.diversification-score

/* Dividends */
.dividend-calendar
.dividend-card
.dividend-chart
```

---

## 🧪 Test Files to Create

### Phase 3
```
tests/test_news_service.py
tests/test_export_functionality.py
tests/e2e/test_theme_toggle.spec.js
tests/e2e/test_dashboard_customization.spec.js
```

### Phase 4
```
tests/test_portfolio_analytics.py
tests/test_risk_metrics.py
tests/test_earnings_integration.py
tests/test_dividend_tracking.py
tests/e2e/test_portfolio_timeline.spec.js
tests/e2e/test_indicators.spec.js
```

---

## ⏱️ Daily Implementation Schedule

### Week 1 - Phase 3 Part 1
- **Monday**: News Service Backend (2h)
- **Tuesday**: News Widget Frontend (1.5h)
- **Wednesday**: Market Status Indicator (1h)

### Week 2 - Phase 3 Part 2
- **Monday**: Theme Toggle (1.5h)
- **Tuesday**: Export Functionality (2h)
- **Wednesday**: Dashboard Customization Part 1 (1.5h)
- **Thursday**: Dashboard Customization Part 2 (1.5h)
- **Friday**: Testing & Bug Fixes (1h)

### Week 3 - Phase 4 Part 1
- **Monday**: Database Migration + Portfolio History (2h)
- **Tuesday**: Portfolio Timeline Chart (2h)
- **Wednesday**: Risk Metrics (2h)

### Week 4 - Phase 4 Part 2
- **Monday**: Advanced Indicators Part 1 (1.5h)
- **Tuesday**: Advanced Indicators Part 2 (1.5h)
- **Wednesday**: Earnings Calendar (2h)
- **Thursday**: Correlation Matrix (2h)

### Week 5 - Phase 4 Part 3
- **Monday**: Dividend Tracking Backend (1h)
- **Tuesday**: Dividend Tracking Frontend (1h)
- **Wednesday**: UI/UX Enhancements (2h)
- **Thursday**: Testing & Documentation (1h)
- **Friday**: Final Review & Deploy (1h)

---

## 📈 Progress Tracking

### Phase 3 Progress (11h total)
- [ ] News Integration (3.5h)
- [ ] Market Status (1h)
- [ ] Theme Toggle (1.5h)
- [ ] Export Functionality (2h)
- [ ] Dashboard Customization (3h)

**Progress: 0/5 features (0%)**

### Phase 4 Progress (17h total)
- [ ] Portfolio Timeline (4h)
- [ ] Risk Metrics (2h)
- [ ] Advanced Indicators (3h)
- [ ] Earnings Calendar (2h)
- [ ] Correlation Matrix (2h)
- [ ] Dividend Tracking (2h)
- [ ] UI/UX Enhancements (2h)

**Progress: 0/7 features (0%)**

---

## 🚀 Quick Start Commands

### Start Implementation
```bash
# Create new feature branch
git checkout -b phase-3-implementation

# Install new dependencies (if needed)
pip install -r requirements.txt

# Create new service files
touch app/services/news_service.py
touch static/js/theme-manager.js
touch static/js/market-status.js

# Start development server
python app.py
```

### Run Tests
```bash
# Unit tests
pytest tests/test_news_service.py -v

# Integration tests
pytest tests/test_api.py::test_news_endpoint -v

# E2E tests
npx playwright test tests/e2e/test_theme_toggle.spec.js
```

### Commit & Push
```bash
# Commit feature
git add .
git commit -m "feat(phase3): Add news integration with sentiment analysis"

# Push to GitHub
git push origin phase-3-implementation
```

---

## 📚 Useful Resources

### APIs
- **Finnhub**: https://finnhub.io/docs/api
- **Alpha Vantage**: https://www.alphavantage.co/documentation/

### Libraries
- **Chart.js**: https://www.chartjs.org/docs/
- **jsPDF**: https://github.com/parallax/jsPDF
- **html2canvas**: https://html2canvas.hertzen.com/
- **Papa Parse**: https://www.papaparse.com/

### Design Inspiration
- **TradingView**: https://www.tradingview.com/
- **Yahoo Finance**: https://finance.yahoo.com/
- **Seeking Alpha**: https://seekingalpha.com/

---

## 🎯 Success Criteria

### Phase 3 Complete When:
- ✅ News feed loads and displays correctly
- ✅ Sentiment analysis shows accurate badges
- ✅ Market status indicator updates in real-time
- ✅ Theme toggle works across all pages
- ✅ Export generates valid PDF/CSV files
- ✅ Dashboard layout persists after reload
- ✅ All tests passing

### Phase 4 Complete When:
- ✅ Portfolio timeline chart renders correctly
- ✅ Risk metrics calculate accurately
- ✅ All advanced indicators display properly
- ✅ Earnings calendar shows upcoming dates
- ✅ Correlation matrix visualizes relationships
- ✅ Dividend tracking records payments
- ✅ Keyboard shortcuts work
- ✅ All tests passing
- ✅ Documentation updated

---

**READY TO START? LET'S BUILD THE BEST STOCK ANALYZER! 🚀**
