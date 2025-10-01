# Phase 2: Interactive Charts & Stock Comparison - Test Plan

## Test Coverage

### ✅ Backend Tests

#### 1. Stock History Endpoint
**Test:** `GET /api/stock/<ticker>/history?period=<period>`

```bash
# Test 1M period
curl http://localhost:5000/api/stock/AAPL/history?period=1mo

# Test 6M period
curl http://localhost:5000/api/stock/AAPL/history?period=6mo

# Test 1Y period
curl http://localhost:5000/api/stock/AAPL/history?period=1y
```

**Expected:**
- Returns JSON with `data` array containing date, close, volume
- Different periods return different amounts of data
- ✅ PASSED - Returns historical data correctly

#### 2. Stock Compare Endpoint
**Test:** `POST /api/stock/compare`

```bash
# Test with 2 tickers
curl -X POST http://localhost:5000/api/stock/compare \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "MSFT"], "period": "1mo"}'

# Test with 4 tickers
curl -X POST http://localhost:5000/api/stock/compare \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"], "period": "6mo"}'

# Test with invalid ticker count (should fail)
curl -X POST http://localhost:5000/api/stock/compare \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL"], "period": "1mo"}'
```

**Expected:**
- Returns `comparison` array with stock metrics
- Returns `price_histories` array with normalized prices
- Handles 2-4 tickers
- Returns error for < 2 or > 4 tickers
- ✅ PASSED - Returns comparison data correctly

### ✅ Frontend Tests

#### 3. Interactive Price Chart
**Location:** Analysis page, below tabs

**Features to Test:**
- [ ] Period buttons (1M, 3M, 6M, 1J, 2J, 5J, Max) change chart period
- [ ] Chart loads automatically when analyzing a stock
- [ ] Active period button is highlighted
- [ ] Chart updates when clicking different periods
- [ ] Chart shows price line with gradient fill
- [ ] Tooltip shows date and price on hover
- [ ] Responsive on mobile devices

**Manual Test Steps:**
1. Navigate to Analysis page
2. Enter ticker "AAPL" and click Analysieren
3. Scroll to price chart section
4. Verify chart loads with 1J period (default)
5. Click on "1M" button
6. Verify chart updates and button becomes active
7. Repeat for each period button

#### 4. Moving Average Toggles
**Location:** Chart controls, next to period buttons

**Features to Test:**
- [ ] SMA 50 checkbox adds green dashed line to chart
- [ ] SMA 200 checkbox adds red dashed line to chart
- [ ] Both can be toggled on/off independently
- [ ] Chart updates immediately when toggled
- [ ] MAs only show when enough historical data available
- [ ] Checkboxes persist state during period changes

**Manual Test Steps:**
1. Analyze a stock with sufficient history (e.g., AAPL)
2. Check "SMA 50" checkbox
3. Verify green dashed line appears on chart
4. Check "SMA 200" checkbox
5. Verify red dashed line appears on chart
6. Uncheck SMA 50
7. Verify green line disappears
8. Change period to 1M
9. Verify MAs update correctly

#### 5. Volume Chart
**Location:** Below price chart

**Features to Test:**
- [ ] Volume bar chart displays below price chart
- [ ] Bars match dates from price chart
- [ ] Hover shows volume value
- [ ] Y-axis shows volume in millions (M)
- [ ] Bar color is consistent (purple/blue)
- [ ] Responsive height on mobile

**Manual Test Steps:**
1. Analyze a stock
2. Scroll to volume chart
3. Verify bars are visible
4. Hover over bars to see tooltip
5. Verify volume values make sense
6. Change period and verify volume updates

#### 6. Stock Comparison Tab
**Location:** Analysis page, "Vergleich" tab

**Features to Test:**
- [ ] Comparison tab appears in tab list
- [ ] Clicking tab shows comparison interface
- [ ] 4 ticker input fields are visible
- [ ] Period dropdown has all options
- [ ] First ticker pre-filled with current analysis ticker
- [ ] "Vergleichen" button triggers comparison
- [ ] Loading state shows while fetching
- [ ] Error notification for < 2 tickers
- [ ] Error notification for > 4 tickers

**Manual Test Steps:**
1. Analyze stock "AAPL"
2. Click "Vergleich" tab
3. Verify ticker 1 is pre-filled with "AAPL"
4. Enter "MSFT" in ticker 2
5. Select "6mo" period
6. Click "Vergleichen"
7. Verify loading spinner appears
8. Wait for results

#### 7. Comparison Metrics Table
**Location:** Compare results section

**Features to Test:**
- [ ] Table shows after comparison completes
- [ ] Columns: Kennzahl, Ticker1, Ticker2, etc.
- [ ] Rows include: Company, Price, Market Cap, P/E, Dividend, Sector, RSI, Volatility, 1M Change, Volume
- [ ] 1M Change has color coding (green positive, red negative)
- [ ] All values formatted correctly ($, %, B for billions)
- [ ] Missing values show "-"
- [ ] Table is responsive/scrollable on mobile

**Manual Test Steps:**
1. Complete a comparison
2. Verify metrics table displays
3. Check all metrics are present
4. Verify formatting is correct
5. Verify color coding on 1M Change
6. Resize browser to test responsiveness

#### 8. Normalized Comparison Chart
**Location:** Below comparison table

**Features to Test:**
- [ ] Line chart shows normalized price changes (%)
- [ ] Each ticker has different color
- [ ] All lines start at 0%
- [ ] Legend shows ticker names with colors
- [ ] Tooltip shows ticker and % change
- [ ] Y-axis formatted as percentage
- [ ] X-axis shows date range
- [ ] Lines are smooth (tension: 0.4)
- [ ] Chart height is adequate (450px)

**Manual Test Steps:**
1. Complete a comparison with 3-4 stocks
2. Verify normalized chart displays
3. Verify each stock has unique color
4. Verify all lines start at 0%
5. Hover to see tooltip
6. Verify percentage formatting

### ✅ Integration Tests

#### 9. Tab Persistence
**Test:** Comparison tab remembered in localStorage

**Manual Test Steps:**
1. Analyze stock "AAPL"
2. Switch to "Vergleich" tab
3. Analyze another stock "MSFT"
4. Verify "Vergleich" tab is still active
5. Refresh page
6. Analyze stock again
7. Verify last tab (Vergleich) is restored

#### 10. Error Handling
**Test:** Graceful error handling

**Manual Test Steps:**
1. Try comparison with 1 ticker only
   - Expected: Error notification "Bitte geben Sie mindestens 2 Ticker ein"
2. Try comparison with 5 tickers
   - Backend should return 400 error
3. Try comparison with invalid ticker "INVALID"
   - Expected: Comparison runs but shows no data for invalid ticker
4. Test with network offline
   - Expected: Error notification "Vergleich fehlgeschlagen"

### ✅ Performance Tests

#### 11. Chart Rendering Performance
**Test:** Charts render smoothly

**Manual Test Steps:**
1. Analyze stock with max period
2. Measure time to load chart (should be < 3 seconds)
3. Toggle MAs multiple times
4. Verify no lag or freezing
5. Switch between periods rapidly
6. Verify chart updates smoothly

#### 12. Multiple Chart Instances
**Test:** Charts are properly destroyed and recreated

**Manual Test Steps:**
1. Analyze stock "AAPL"
2. Wait for charts to load
3. Analyze different stock "MSFT"
4. Verify old charts are destroyed
5. Verify new charts render correctly
6. Check browser console for errors
7. Check browser memory (no leaks)

## Test Results

### Automated Tests
- ✅ Backend: Stock history endpoint
- ✅ Backend: Stock compare endpoint  
- ✅ Backend: Error handling for invalid inputs
- ✅ JavaScript: Syntax validation

### Manual Tests (To be performed)
- [ ] Interactive price chart with period buttons
- [ ] Moving average toggles (SMA 50, SMA 200)
- [ ] Volume chart rendering
- [ ] Comparison tab interface
- [ ] Comparison metrics table
- [ ] Normalized comparison chart
- [ ] Tab persistence with localStorage
- [ ] Error handling for edge cases
- [ ] Chart rendering performance
- [ ] Memory leak prevention

## Known Issues

### 1. Alpha Vantage Rate Limiting
**Issue:** Alpha Vantage API has 25 requests/day limit
**Impact:** Historical data may fail after rate limit reached
**Workaround:** Use cached data or wait for rate limit reset
**Status:** Expected limitation, not a bug

### 2. German Stock Symbols
**Issue:** Some German stock symbols (.DE) return 403 from Finnhub
**Impact:** Comparison with German stocks may fail
**Workaround:** Use US stocks for testing
**Status:** API limitation, not application bug

### 3. Missing Logger Import
**Issue:** `logger` not imported in stock.py compare endpoint
**Impact:** No error logging in compare function
**Fix:** Added import statement
**Status:** ✅ FIXED

## Browser Compatibility

Tested on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Chrome (Android)
- [ ] Mobile Safari (iOS)

## Accessibility

- [ ] Charts have proper aria labels
- [ ] Keyboard navigation works for buttons
- [ ] Color contrast meets WCAG AA standards
- [ ] Screen reader compatible

## Documentation Updates Needed

- [x] API endpoint documentation (stock.py docstrings)
- [x] Frontend method documentation (JSDoc comments)
- [ ] User guide for comparison feature
- [ ] Update CLAUDE.md with Phase 2 features
