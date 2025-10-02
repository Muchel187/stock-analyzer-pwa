# KI-Analyse Verbesserungsplan - Implementierung

## Phase 1: Datenanreicherung und Prompt-Optimierung ⏳ IN PROGRESS

### 1.1 Analystenbewertungen und Kursziele ⏳

**Backend:**
- [ ] `StockService.get_analyst_ratings(ticker)` - Finnhub API
- [ ] `StockService.get_price_targets(ticker)` - Analyst targets
- [ ] Integration in `get_stock_info()`

**AI Service:**
- [ ] Prompt-Erweiterung mit Analyst-Daten
- [ ] Vergleich KI vs. Analysten-Konsens

**Status:** Starting implementation...

### 1.2 Insider-Transaktionen ⏳

**Backend:**
- [ ] `StockService.get_insider_transactions(ticker)` - Last 6 months
- [ ] Aggregation: Net buying/selling

**AI Service:**
- [ ] Prompt-Erweiterung mit Insider-Daten
- [ ] Bullish/Bearish Signal Interpretation

**Status:** Queued

### 1.3 Nachrichten-Sentiment-Analyse ⏳

**Backend:**
- [ ] `NewsService` bereits vorhanden ✅
- [ ] Sentiment-Aggregation hinzufügen

**AI Service:**
- [ ] Prompt-Erweiterung mit News-Sentiment
- [ ] Kurzfristige Prognose-Integration

**Status:** Queued

---

## Phase 2: Erweiterte Visuelle Darstellungen (Geplant)

### 2.1 KI-Prognose Chart
- [ ] Frontend: Tachometer/Balken-Chart
- [ ] Aktueller Kurs vs. KI-Kursziel
- [ ] Upside/Downside Visualization

### 2.2 Peer-Group Vergleich
- [ ] Backend: Top 3-5 Competitors
- [ ] Frontend: Radar-Chart
- [ ] Vergleich: KGV, Umsatzwachstum, Marge

### 2.3 Szenario-Analyse
- [ ] Backend: Best/Base/Worst-Case Scenarios
- [ ] Frontend: Interaktive Karten
- [ ] Kursz-Szenarien mit Begründungen

---

## Phase 3: Detaillierte Spezifische Analysen (Geplant)

### 3.1 Enhanced Short Squeeze Analysis
- [ ] `ShortDataService` Integration
- [ ] Echtzeit Short-Quote + FTD Daten
- [ ] Frontend: Konkrete Daten-Anzeige

### 3.2 Burggraben (Moat) Analyse
- [ ] Prompt: Moat-Bewertung
- [ ] Frontend: Burg-Icon + Rating
- [ ] Bewertung: Breit/Schmal/Keiner

### 3.3 Management-Bewertung
- [ ] Backend: CEO + Leadership Data
- [ ] Prompt: Management Quality Assessment
- [ ] Frontend: Management Scorecard (A-F)

---

## Implementation Order

**Session 1 (Current):**
1. ✅ Setup Implementation Plan
2. ⏳ 1.1 - Analyst Ratings & Price Targets
3. ⏳ 1.2 - Insider Transactions
4. ⏳ 1.3 - News Sentiment Aggregation

**Session 2:**
5. Phase 2 - Visual Charts
6. Phase 3 - Detailed Analysis

---

## API Requirements Check

### Finnhub (Primary):
- ✅ Stock Quote
- ✅ Company Profile
- ✅ News
- ⏳ **Analyst Ratings** - `/stock/recommendation`
- ⏳ **Price Targets** - `/stock/price-target`
- ⏳ **Insider Transactions** - `/stock/insider-transactions`

### Alpha Vantage (Fallback):
- ✅ Company Overview
- ✅ News & Sentiment
- ⏳ **Analyst Estimates** - Available

### Twelve Data (Tertiary):
- ✅ Stock Quotes
- ✅ Historical Data
- ❌ No Analyst/Insider Data

---

## Files to Modify

**Phase 1 Backend:**
- `app/services/stock_service.py` - New methods
- `app/services/news_service.py` - Sentiment aggregation
- `app/services/ai_service.py` - Prompt enhancement
- `app/routes/stock.py` - Optional new endpoints

**Phase 1 Frontend:**
- None (data only in AI response)

**Phase 2 Frontend:**
- `static/js/ai-analysis.js` - New chart components
- `static/css/ai-analysis.css` - Chart styling

**Phase 3 Mixed:**
- Backend + Frontend updates

---

**Started:** 2025-10-02 10:50 CEST
**Estimated Time:** Phase 1 = 2-3 hours
