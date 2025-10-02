# Kostenlose Financial API Integration Plan
## Morningstar-ähnliche Features für Stock Analyzer Pro

**Erstellt:** 2. Oktober 2025
**Autor:** Claude Code
**Ziel:** Integration kostenloser, professioneller Finanzanalyse-Instrumente

---

## 🎯 Executive Summary

Basierend auf umfassender Recherche der Marktführer (Morningstar, Yahoo Finance, Bloomberg) wurden folgende **kostenlose** APIs identifiziert, die professionelle Analyseinstrumente bereitstellen:

### Top 3 Empfohlene APIs:
1. **Financial Modeling Prep (FMP)** - Beste Gesamtlösung
2. **Alpha Vantage** - Bereits integriert, erweitern
3. **EODHD** - Globale Marktabdeckung

---

## 📊 Verfügbare Kostenlose Datenquellen

### 1. Financial Modeling Prep (FMP)
**Status:** ⭐ HÖCHSTE PRIORITÄT
**Website:** https://site.financialmodelingprep.com/

#### Kostenlose Features:
- ✅ **Financial Ratios API** - P/E, P/B, ROE, ROA, Debt/Equity, Current Ratio, etc.
- ✅ **TTM Ratios** - Trailing Twelve Month Metriken
- ✅ **Piotroski Score** - Finanzstabilität (0-9 Score)
- ✅ **Altman Z-Score** - Insolvenzrisiko
- ✅ **Stock Screener API** - Filter nach Fundamentals
- ✅ **Dividend History** - Historische Dividendenzahlungen
- ✅ **Dividend Calendar** - Kommende Dividenden
- ✅ **Financial Statements** - Bilanz, GuV, Cashflow
- ✅ **Company Profile** - Sektor, Industrie, CEO, Beschreibung
- ✅ **Key Metrics** - Revenue per Share, Book Value, etc.

#### Rate Limits (Free Tier):
- **250 Requests/Tag**
- **5 Requests/Minute**

#### Kosten:
- **FREE:** 250 calls/day
- **Starter ($14/Monat):** 300 calls/minute
- **Premium ($29/Monat):** 750 calls/minute

---

### 2. Alpha Vantage (bereits integriert)
**Status:** ✅ TEILWEISE INTEGRIERT
**Website:** https://www.alphavantage.co/

#### Bereits genutzt:
- Real-time quotes
- Historical price data
- Company overview

#### Zusätzlich verfügbar (noch nicht genutzt):
- ✅ **Company Overview** - Erweiterte Fundamentals
- ✅ **Earnings** - Quartalsberichte und Prognosen
- ✅ **Income Statement** - Gewinn- und Verlustrechnung
- ✅ **Balance Sheet** - Bilanzinformationen
- ✅ **Cash Flow** - Cashflow-Statements
- ✅ **Earnings Calendar** - Kommende Earnings

#### Rate Limits:
- **5 Requests/Minute**
- **25 Requests/Tag** (Free Tier)
- **500 Requests/Tag** ($49.99/Monat)

---

### 3. EODHD (EOD Historical Data)
**Status:** 🆕 NEU EMPFOHLEN
**Website:** https://eodhd.com/

#### Kostenlose Features:
- ✅ **Stock Screener API** - Filter nach 50+ Kriterien
- ✅ **Fundamental Data** - Bilanz, GuV, Cashflow
- ✅ **Dividend History** - 1 Jahr historische Daten (Free)
- ✅ **Splits History** - Stock Splits Daten
- ✅ **Global Coverage** - 70+ Börsen, 150,000+ Tickers
- ✅ **Calendar API** - Earnings, IPOs, Splits

#### Rate Limits:
- **20 Requests/Sekunde** (Free Trial)
- **100,000 API calls/Monat**

#### Kosten:
- **Trial:** Kostenlos für 7 Tage
- **All World ($19.99/Monat):** Unbegrenzte API calls
- **All-In-One ($79.99/Monat):** Alle Features

---

### 4. Finnhub (bereits integriert)
**Status:** ✅ BEREITS INTEGRIERT
**Website:** https://finnhub.io/

#### Bereits genutzt:
- Real-time quotes
- Company profile
- German stocks (XETRA)

#### Zusätzlich verfügbar:
- ✅ **Financial Statements** - Bilanz, GuV
- ✅ **Earnings Calendar** - Kommende Earnings
- ✅ **Recommendation Trends** - Analyst Ratings
- ✅ **Price Target** - Analyst Kursziele
- ✅ **Dividends** - Dividend data

#### Rate Limits:
- **60 Requests/Minute** (Free Tier)

---

### 5. SimFin (Spezialität: Fundamentals)
**Status:** 🆕 NEU EMPFOHLEN
**Website:** https://www.simfin.com/

#### Kostenlose Features:
- ✅ **7,000+ Calculated Ratios** - Historisch seit 2003
- ✅ **Financial Statements** - Bilanz, GuV, Cashflow
- ✅ **Daily Financial Data** - Täglich aktualisierte Kennzahlen
- ✅ **Industry Classification** - Sektor/Industrie Mapping

#### Rate Limits:
- **2,000 API Calls/Tag** (Free)

---

## 🎨 Neue Dashboard-Instrumente (Morningstar-Style)

### Phase 1: Financial Health Scores (Priorität: HOCH)

#### 1.1 Piotroski F-Score Widget
**Quelle:** FMP API
**Endpoint:** `/v4/score?symbol=AAPL`

**Beschreibung:**
9-Punkte Score zur Bewertung der Finanzstabilität (0=schwach, 9=stark)

**Visualisierung:**
```
┌─────────────────────────────────┐
│ Piotroski F-Score: 8/9          │
│ ████████░ 89%                   │
│                                 │
│ ✅ Profitabilität:    4/4       │
│ ✅ Leverage:          2/3       │
│ ✅ Betriebseffizienz: 2/2       │
│                                 │
│ Status: STARK                   │
└─────────────────────────────────┘
```

**Komponenten:**
- 9 binäre Tests (0 oder 1)
- Profitabilität: ROA, Cashflow, ROA-Wachstum, Accruals
- Leverage: Verschuldung, Current Ratio, Share Issuance
- Effizienz: Margin, Asset Turnover

**Integration:**
- Dashboard Widget
- Analyse-Seite (neuer Tab "Financial Health")

---

#### 1.2 Altman Z-Score Widget
**Quelle:** FMP API
**Endpoint:** `/v4/score?symbol=AAPL`

**Beschreibung:**
Insolvenzrisiko-Score (>3.0=sicher, <1.8=Gefahr)

**Visualisierung:**
```
┌─────────────────────────────────┐
│ Altman Z-Score: 5.2             │
│                                 │
│ Sicher │ Grau │ Gefahr          │
│   ██████████                    │
│   3.0  1.8                      │
│                                 │
│ Status: FINANZIELL SICHER       │
│ Insolvenzrisiko: SEHR GERING    │
└─────────────────────────────────┘
```

**Formel:**
```
Z = 1.2×X1 + 1.4×X2 + 3.3×X3 + 0.6×X4 + 1.0×X5
X1 = Working Capital / Total Assets
X2 = Retained Earnings / Total Assets
X3 = EBIT / Total Assets
X4 = Market Cap / Total Liabilities
X5 = Sales / Total Assets
```

**Integration:**
- Dashboard Widget
- Analyse-Seite (Financial Health Tab)

---

### Phase 2: Erweiterte Financial Ratios (Priorität: HOCH)

#### 2.1 Key Financial Ratios Dashboard
**Quelle:** FMP API
**Endpoint:** `/v3/ratios-ttm/AAPL`

**Metriken:**
1. **Profitabilität:**
   - Gross Profit Margin
   - Operating Profit Margin
   - Net Profit Margin
   - Return on Assets (ROA)
   - Return on Equity (ROE)
   - Return on Capital Employed (ROCE)

2. **Liquidität:**
   - Current Ratio
   - Quick Ratio
   - Cash Ratio
   - Operating Cash Flow Ratio

3. **Verschuldung:**
   - Debt-to-Equity Ratio
   - Debt-to-Assets Ratio
   - Interest Coverage Ratio

4. **Effizienz:**
   - Asset Turnover
   - Inventory Turnover
   - Receivables Turnover
   - Days Sales Outstanding

5. **Bewertung:**
   - P/E Ratio (TTM)
   - P/B Ratio
   - P/S Ratio
   - PEG Ratio
   - EV/EBITDA

**Visualisierung:**
```
┌──────────────────────────────────────┐
│ Financial Ratios - AAPL             │
├──────────────────────────────────────┤
│ 📈 PROFITABILITÄT                   │
│ ├─ Gross Margin:    38.5%  ████░   │
│ ├─ Operating Margin: 30.2%  ███░    │
│ ├─ Net Margin:      25.3%  ███░     │
│ ├─ ROE:             147.3% █████    │
│ └─ ROA:             28.7%  ███░     │
│                                      │
│ 💧 LIQUIDITÄT                       │
│ ├─ Current Ratio:   0.98   ⚠️       │
│ ├─ Quick Ratio:     0.84   ⚠️       │
│ └─ Cash Ratio:      0.23   ❌       │
│                                      │
│ 💳 VERSCHULDUNG                     │
│ ├─ Debt/Equity:     1.97   ⚠️       │
│ ├─ Debt/Assets:     0.32   ✅       │
│ └─ Interest Cov.:   28.5x  ✅       │
│                                      │
│ ⚡ EFFIZIENZ                        │
│ ├─ Asset Turnover:  1.14   ✅       │
│ ├─ Inventory Turn.: 38.2   ✅       │
│ └─ Receivables T.:  14.5   ✅       │
│                                      │
│ 💰 BEWERTUNG                        │
│ ├─ P/E Ratio:       28.3   ⚠️       │
│ ├─ P/B Ratio:       45.8   ⚠️       │
│ ├─ P/S Ratio:       7.2    ⚠️       │
│ └─ EV/EBITDA:       22.1   ✅       │
└──────────────────────────────────────┘
```

**Radar Chart Alternative:**
```
    Profitabilität
          │
     ╱────┴────╲
Liquidität──────Verschuldung
     ╲────┬────╱
          │
     Effizienz
```

**Integration:**
- Neuer Tab in Analyse-Seite: "Financial Ratios"
- Dashboard Widget: "Top 5 Ratios"

---

#### 2.2 Peer Comparison mit Ratios
**Quelle:** FMP API + Stock Screener
**Endpoint:** `/v3/stock-screener` + `/v3/ratios-ttm/{ticker}`

**Beschreibung:**
Vergleich mit Top 3-5 Wettbewerbern basierend auf Sektor

**Visualisierung:**
```
┌────────────────────────────────────────┐
│ Peer Comparison - Technology Sector    │
├────────────────────────────────────────┤
│        AAPL  MSFT  GOOGL  META  Sektor │
│ ROE    147%  43%   28%    36%   38%   │
│ P/E    28.3  33.5  23.2   24.8  27.1  │
│ Margin 25.3% 36.7% 27.6%  29.5% 28.2% │
│ Debt/E 1.97  0.35  0.08   0.00  0.85  │
│                                        │
│ [Bar Chart Comparison]                 │
└────────────────────────────────────────┘
```

**Integration:**
- Analyse-Seite: "Peer Comparison" Tab
- AI-Integration: KI berücksichtigt Peer-Daten

---

### Phase 3: Dividend Dashboard (Priorität: MITTEL)

#### 3.1 Dividend Tracker Widget
**Quelle:** FMP API
**Endpoint:** `/v3/historical-price-full/stock_dividend/AAPL`

**Features:**
- Dividendenhistorie (10 Jahre)
- Dividend Yield Trend
- Payout Ratio
- Dividend Growth Rate (3J, 5J, 10J)
- Nächster Ex-Dividend Date
- Kommende Auszahlung

**Visualisierung:**
```
┌──────────────────────────────────────┐
│ 💸 Dividend Dashboard - AAPL        │
├──────────────────────────────────────┤
│ Current Yield:        0.52%         │
│ Annual Dividend:      $0.96         │
│ Payout Ratio:         14.9%  ✅     │
│ 5Y Growth Rate:       7.2%          │
│                                      │
│ Next Payment:         2025-11-15    │
│ Ex-Dividend:          2025-11-08    │
│ Amount:               $0.24         │
│                                      │
│ [Line Chart: 10 Jahre Historie]     │
│                                      │
│ Zahlungen pro Jahr:   4 (Quarterly) │
│ Consecutive Years:    13 Jahre      │
│ Status: DIVIDEND ARISTOCRAT 👑      │
└──────────────────────────────────────┘
```

**Dashboard Widget Variante:**
```
┌──────────────────────────┐
│ Top Dividend Stocks      │
├──────────────────────────┤
│ 1. T      7.2%  $1.44    │
│ 2. VZ     6.8%  $2.56    │
│ 3. XOM    3.4%  $3.76    │
│ 4. PFE    5.9%  $1.68    │
│ 5. IBM    4.7%  $6.64    │
└──────────────────────────┘
```

**Integration:**
- Dashboard: "Dividend Stocks" Widget
- Portfolio: Dividend Income Tracker
- Watchlist: Dividend Yield Column

---

#### 3.2 Dividend Calendar
**Quelle:** FMP API
**Endpoint:** `/v3/stock_dividend_calendar`

**Beschreibung:**
Übersicht aller kommenden Dividendenzahlungen in Portfolio/Watchlist

**Visualisierung:**
```
┌─────────────────────────────────────────┐
│ Dividend Calendar - Nächste 30 Tage    │
├─────────────────────────────────────────┤
│ Nov 8  │ AAPL   │ Ex-Date  │ $0.24     │
│ Nov 12 │ MSFT   │ Ex-Date  │ $0.75     │
│ Nov 15 │ AAPL   │ Payment  │ $0.24     │
│ Nov 20 │ JNJ    │ Ex-Date  │ $1.19     │
│ Dec 1  │ MSFT   │ Payment  │ $0.75     │
│                                         │
│ Total Expected Income: $2.42            │
└─────────────────────────────────────────┘
```

**Integration:**
- Neuer Menüpunkt: "Dividenden"
- Dashboard Widget

---

### Phase 4: Earnings Calendar & Analysis (Priorität: MITTEL)

#### 4.1 Earnings Calendar
**Quelle:** FMP API / Alpha Vantage
**Endpoint:** `/v3/earning_calendar` (FMP)

**Features:**
- Kommende Earnings Dates
- Earnings Surprise Historie
- EPS Estimate vs. Actual
- Revenue Estimate vs. Actual
- Earnings Call Transcripts (optional)

**Visualisierung:**
```
┌──────────────────────────────────────────┐
│ 📊 Earnings Calendar                    │
├──────────────────────────────────────────┤
│ HEUTE                                    │
│ ├─ TSLA    After Market                 │
│ │  EPS Est: $0.74    Revenue: $25.2B    │
│ │  Whisper: $0.78                       │
│ └─ Countdown: 4h 23m                    │
│                                          │
│ DIESE WOCHE                              │
│ ├─ Nov 3: AAPL (After Market)           │
│ ├─ Nov 4: GOOGL (After Market)          │
│ └─ Nov 5: MSFT (Before Market)          │
│                                          │
│ [Watchlist Stocks Only]                  │
└──────────────────────────────────────────┘
```

**Dashboard Widget:**
```
┌──────────────────────────┐
│ Kommende Earnings        │
├──────────────────────────┤
│ 🔥 Heute:     TSLA       │
│ 📅 Morgen:    AAPL       │
│ 📅 Do.:       GOOGL      │
│ 📅 Fr.:       MSFT       │
└──────────────────────────┘
```

**Integration:**
- Dashboard Widget: "Kommende Earnings"
- Neuer Tab: "Earnings" in Analyse-Seite
- Notifications: Earnings-Alert (24h vorher)

---

#### 4.2 Earnings Surprise Tracker
**Quelle:** FMP API
**Endpoint:** `/v3/earnings-surprises/AAPL`

**Visualisierung:**
```
┌──────────────────────────────────────────┐
│ Earnings History - AAPL                 │
├──────────────────────────────────────────┤
│ Q3 2025 │ Est: $1.35 │ Act: $1.46 │ +8% │
│ Q2 2025 │ Est: $1.26 │ Act: $1.40 │ +11%│
│ Q1 2025 │ Est: $2.10 │ Act: $2.18 │ +4% │
│ Q4 2024 │ Est: $1.39 │ Act: $1.29 │ -7% │
│                                          │
│ Beat Rate: 75% (letzte 12 Quarters)     │
│ Avg Surprise: +5.3%                     │
│                                          │
│ [Line Chart: Estimate vs Actual]        │
└──────────────────────────────────────────┘
```

**Integration:**
- Analyse-Seite: "Earnings" Tab

---

### Phase 5: Advanced Screener (Priorität: MITTEL)

#### 5.1 Multi-Criteria Screener
**Quelle:** FMP API / EODHD
**Endpoint:** `/v3/stock-screener` (FMP)

**Filter-Kategorien:**

**1. Fundamentals:**
- Market Cap: $0 - $3T
- P/E Ratio: 0 - 100
- P/B Ratio: 0 - 50
- Dividend Yield: 0% - 15%
- ROE: -100% - 200%
- Debt/Equity: 0 - 10
- Current Ratio: 0 - 10
- EPS Growth: -100% - 500%
- Revenue Growth: -100% - 500%

**2. Technical:**
- Price: $0 - $1000
- Volume: 0 - 1B
- 52W High/Low: Percentage
- RSI: 0 - 100
- Beta: 0 - 3

**3. Sector/Industry:**
- 11 Sektoren (GICS)
- 140+ Industrien

**4. Geography:**
- US Stocks
- German Stocks (DAX, MDAX)
- International

**5. Dividends:**
- Dividend Yield: 0% - 15%
- Payout Ratio: 0% - 200%
- Dividend Growth Rate: 0% - 100%
- Years of Dividends: 0 - 100

**6. Financial Health:**
- Piotroski Score: 0 - 9
- Altman Z-Score: <0 - >10

**Preset Strategies:**
1. **Value Investing** (Graham-Style)
   - P/E < 15
   - P/B < 1.5
   - Debt/Equity < 0.5
   - Current Ratio > 1.5
   - Dividend Yield > 2%

2. **High Quality** (Buffett-Style)
   - ROE > 20%
   - Net Margin > 20%
   - Piotroski Score >= 7
   - Low Debt/Equity
   - Consistent Earnings Growth

3. **Dividend Aristocrats**
   - Dividend Yield > 3%
   - 25+ Years of Dividends
   - Payout Ratio < 60%
   - Positive EPS Growth
   - Altman Z-Score > 3.0

4. **Growth Stocks**
   - EPS Growth > 20%
   - Revenue Growth > 15%
   - High ROE
   - P/E < PEG Ratio

5. **Turnaround Plays**
   - Altman Z-Score: 1.8 - 3.0 (Gray Zone)
   - Recent Negative Earnings
   - Improving Margins
   - Low P/B

6. **Financial Strength**
   - Piotroski Score >= 8
   - Altman Z-Score > 3.0
   - Current Ratio > 2.0
   - Debt/Equity < 0.3

**Visualisierung:**
```
┌──────────────────────────────────────────┐
│ Advanced Stock Screener                 │
├──────────────────────────────────────────┤
│ Filter:                                  │
│ ├─ Market Cap: $10B - $500B             │
│ ├─ P/E Ratio:  < 20                     │
│ ├─ ROE:        > 15%                    │
│ ├─ Piotroski:  >= 7                     │
│ └─ Sector:     Technology               │
│                                          │
│ Results: 23 stocks                       │
│                                          │
│ Ticker │ P/E  │ ROE  │ P-Score │ Price │
│ AAPL   │ 28.3 │ 147% │ 8       │ $245  │
│ MSFT   │ 33.5 │ 43%  │ 7       │ $420  │
│ NVDA   │ 71.2 │ 97%  │ 8       │ $485  │
│ ...                                      │
│                                          │
│ [Export] [Save Filter] [Alert]          │
└──────────────────────────────────────────┘
```

**Integration:**
- Erweiterung des bestehenden Screeners
- Speichern von Custom Filters
- Alert bei neuen Matches

---

### Phase 6: Analyst Data & Ratings (Priorität: NIEDRIG)

#### 6.1 Analyst Recommendations
**Quelle:** Finnhub (bereits verfügbar)
**Endpoint:** `/stock/recommendation`

**Features:**
- Analyst Rating Distribution
- Rating Changes Historie
- Consensus Rating
- Price Target (High/Low/Average)

**Visualisierung:**
```
┌──────────────────────────────────────────┐
│ Analyst Consensus - AAPL                │
├──────────────────────────────────────────┤
│ Rating: BUY (Strong)                    │
│                                          │
│ Strong Buy  ████████████ 18             │
│ Buy         ████████     12             │
│ Hold        ████         6              │
│ Sell        █            1              │
│ Strong Sell              0              │
│                                          │
│ Price Target: $285 (Avg)                │
│ ├─ High:     $325                       │
│ ├─ Low:      $225                       │
│ └─ Current:  $245 ▲ Upside: +16%       │
│                                          │
│ Updated: 2025-10-01                     │
└──────────────────────────────────────────┘
```

**Integration:**
- Analyse-Seite: "Analyst Ratings" Section
- AI nutzt Consensus für Empfehlungen

---

## 🔧 Technische Implementierung

### Priorität 1: FMP Integration (Woche 1-2)

#### Backend: Neuer Service
```python
# app/services/fmp_service.py

import os
import requests
from typing import Optional, Dict, Any, List

class FMPService:
    BASE_URL = "https://financialmodelingprep.com/api"
    API_KEY = os.getenv('FMP_API_KEY')

    @staticmethod
    def get_financial_score(ticker: str) -> Optional[Dict[str, Any]]:
        """Get Piotroski and Altman Z-Score"""
        endpoint = f"{FMPService.BASE_URL}/v4/score"
        params = {'symbol': ticker, 'apikey': FMPService.API_KEY}

        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        return None

    @staticmethod
    def get_financial_ratios(ticker: str) -> Optional[Dict[str, Any]]:
        """Get TTM financial ratios"""
        endpoint = f"{FMPService.BASE_URL}/v3/ratios-ttm/{ticker}"
        params = {'apikey': FMPService.API_KEY}

        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
        return None

    @staticmethod
    def get_dividend_history(ticker: str) -> Optional[List[Dict[str, Any]]]:
        """Get historical dividend data"""
        endpoint = f"{FMPService.BASE_URL}/v3/historical-price-full/stock_dividend/{ticker}"
        params = {'apikey': FMPService.API_KEY}

        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('historical', [])
        return None

    @staticmethod
    def get_dividend_calendar(from_date: str, to_date: str) -> Optional[List[Dict[str, Any]]]:
        """Get upcoming dividend calendar"""
        endpoint = f"{FMPService.BASE_URL}/v3/stock_dividend_calendar"
        params = {
            'from': from_date,
            'to': to_date,
            'apikey': FMPService.API_KEY
        }

        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        return None

    @staticmethod
    def get_earnings_calendar(from_date: str, to_date: str) -> Optional[List[Dict[str, Any]]]:
        """Get earnings calendar"""
        endpoint = f"{FMPService.BASE_URL}/v3/earning_calendar"
        params = {
            'from': from_date,
            'to': to_date,
            'apikey': FMPService.API_KEY
        }

        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        return None

    @staticmethod
    def get_earnings_surprises(ticker: str) -> Optional[List[Dict[str, Any]]]:
        """Get earnings surprise history"""
        endpoint = f"{FMPService.BASE_URL}/v3/earnings-surprises/{ticker}"
        params = {'apikey': FMPService.API_KEY}

        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        return None

    @staticmethod
    def screen_stocks(filters: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Advanced stock screener with multiple filters"""
        endpoint = f"{FMPService.BASE_URL}/v3/stock-screener"

        # Build query parameters from filters
        params = {'apikey': FMPService.API_KEY}

        # Market Cap
        if 'marketCapMoreThan' in filters:
            params['marketCapMoreThan'] = filters['marketCapMoreThan']
        if 'marketCapLowerThan' in filters:
            params['marketCapLowerThan'] = filters['marketCapLowerThan']

        # Price
        if 'priceMoreThan' in filters:
            params['priceMoreThan'] = filters['priceMoreThan']
        if 'priceLowerThan' in filters:
            params['priceLowerThan'] = filters['priceLowerThan']

        # Volume
        if 'volumeMoreThan' in filters:
            params['volumeMoreThan'] = filters['volumeMoreThan']

        # Ratios
        if 'dividendMoreThan' in filters:
            params['dividendMoreThan'] = filters['dividendMoreThan']
        if 'betaMoreThan' in filters:
            params['betaMoreThan'] = filters['betaMoreThan']
        if 'betaLowerThan' in filters:
            params['betaLowerThan'] = filters['betaLowerThan']

        # Sector
        if 'sector' in filters:
            params['sector'] = filters['sector']

        # Country
        if 'country' in filters:
            params['country'] = filters['country']

        # Limit
        params['limit'] = filters.get('limit', 100)

        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        return None
```

#### Frontend: Neue Widgets
```javascript
// static/js/financial-health.js

class FinancialHealthWidget {
    constructor(app) {
        this.app = app;
    }

    async renderPiotroskiScore(ticker, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        try {
            const data = await api.getFinancialScore(ticker);

            if (!data || !data.piotroskiScore) {
                container.innerHTML = '<p>Keine Daten verfügbar</p>';
                return;
            }

            const score = data.piotroskiScore;
            const percentage = (score / 9) * 100;
            const status = score >= 8 ? 'STARK' : score >= 6 ? 'GUT' : score >= 4 ? 'MITTEL' : 'SCHWACH';
            const statusClass = score >= 8 ? 'success' : score >= 6 ? 'info' : score >= 4 ? 'warning' : 'danger';

            container.innerHTML = `
                <div class="financial-health-card">
                    <h3>Piotroski F-Score: ${score}/9</h3>
                    <div class="score-bar">
                        <div class="score-fill ${statusClass}" style="width: ${percentage}%"></div>
                    </div>
                    <div class="score-breakdown">
                        <div class="score-category">
                            <span>✅ Profitabilität:</span>
                            <span>${data.profitability || 0}/4</span>
                        </div>
                        <div class="score-category">
                            <span>✅ Leverage:</span>
                            <span>${data.leverage || 0}/3</span>
                        </div>
                        <div class="score-category">
                            <span>✅ Betriebseffizienz:</span>
                            <span>${data.efficiency || 0}/2</span>
                        </div>
                    </div>
                    <div class="score-status ${statusClass}">
                        Status: ${status}
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error rendering Piotroski Score:', error);
            container.innerHTML = '<p>Fehler beim Laden</p>';
        }
    }

    async renderAltmanZScore(ticker, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        try {
            const data = await api.getFinancialScore(ticker);

            if (!data || data.altmanZScore === undefined) {
                container.innerHTML = '<p>Keine Daten verfügbar</p>';
                return;
            }

            const score = data.altmanZScore;
            const status = score > 3.0 ? 'FINANZIELL SICHER' :
                          score > 1.8 ? 'GRAUZONE' :
                          'INSOLVENZRISIKO';
            const risk = score > 3.0 ? 'SEHR GERING' :
                        score > 1.8 ? 'MITTEL' :
                        'HOCH';
            const statusClass = score > 3.0 ? 'success' :
                               score > 1.8 ? 'warning' :
                               'danger';

            // Position on scale (0-6 range, clamped)
            const position = Math.min(Math.max(score, 0), 6) / 6 * 100;

            container.innerHTML = `
                <div class="financial-health-card">
                    <h3>Altman Z-Score: ${score.toFixed(2)}</h3>
                    <div class="z-score-scale">
                        <div class="z-scale-bar">
                            <div class="z-marker" style="left: ${position}%"></div>
                        </div>
                        <div class="z-scale-labels">
                            <span>Gefahr</span>
                            <span>Grau</span>
                            <span>Sicher</span>
                        </div>
                        <div class="z-scale-values">
                            <span>0</span>
                            <span>1.8</span>
                            <span>3.0</span>
                            <span>6.0</span>
                        </div>
                    </div>
                    <div class="score-status ${statusClass}">
                        <div>Status: ${status}</div>
                        <div>Insolvenzrisiko: ${risk}</div>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error rendering Altman Z-Score:', error);
            container.innerHTML = '<p>Fehler beim Laden</p>';
        }
    }
}

// Initialize
let financialHealthWidget;
document.addEventListener('DOMContentLoaded', () => {
    if (typeof app !== 'undefined') {
        financialHealthWidget = new FinancialHealthWidget(app);
    }
});
```

#### API Endpoints
```python
# app/routes/financial.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.fmp_service import FMPService
from datetime import datetime, timedelta

bp = Blueprint('financial', __name__, url_prefix='/api/financial')

@bp.route('/score/<ticker>', methods=['GET'])
def get_financial_score(ticker):
    """Get Piotroski and Altman Z-Score for a stock"""
    try:
        data = FMPService.get_financial_score(ticker)
        if not data:
            return jsonify({'error': 'No data available'}), 404

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/ratios/<ticker>', methods=['GET'])
def get_financial_ratios(ticker):
    """Get comprehensive financial ratios (TTM)"""
    try:
        data = FMPService.get_financial_ratios(ticker)
        if not data:
            return jsonify({'error': 'No data available'}), 404

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dividends/<ticker>', methods=['GET'])
@jwt_required()
def get_dividend_history(ticker):
    """Get dividend history for a stock"""
    try:
        data = FMPService.get_dividend_history(ticker)
        if not data:
            return jsonify({'error': 'No dividend data available'}), 404

        return jsonify({'ticker': ticker, 'dividends': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dividends/calendar', methods=['GET'])
@jwt_required()
def get_dividend_calendar():
    """Get upcoming dividend calendar"""
    try:
        # Default: next 30 days
        from_date = datetime.now().strftime('%Y-%m-%d')
        to_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

        data = FMPService.get_dividend_calendar(from_date, to_date)
        if not data:
            return jsonify({'error': 'No calendar data available'}), 404

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/earnings/calendar', methods=['GET'])
@jwt_required()
def get_earnings_calendar():
    """Get earnings calendar"""
    try:
        from_date = request.args.get('from', datetime.now().strftime('%Y-%m-%d'))
        to_date = request.args.get('to', (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))

        data = FMPService.get_earnings_calendar(from_date, to_date)
        if not data:
            return jsonify({'error': 'No calendar data available'}), 404

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/earnings/surprises/<ticker>', methods=['GET'])
def get_earnings_surprises(ticker):
    """Get earnings surprise history"""
    try:
        data = FMPService.get_earnings_surprises(ticker)
        if not data:
            return jsonify({'error': 'No earnings data available'}), 404

        return jsonify({'ticker': ticker, 'surprises': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/screener', methods=['POST'])
@jwt_required()
def advanced_screener():
    """Advanced stock screener with multiple filters"""
    try:
        filters = request.json

        if not filters:
            return jsonify({'error': 'No filters provided'}), 400

        results = FMPService.screen_stocks(filters)

        if not results:
            return jsonify({'error': 'No results found', 'results': []}), 200

        return jsonify({'results': results, 'count': len(results)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### Environment Variables
```bash
# .env additions
FMP_API_KEY=your_fmp_api_key_here
```

---

### Priorität 2: UI/UX Integration (Woche 3-4)

#### Dashboard Updates
1. **Neue Widgets:**
   - Piotroski Score Widget
   - Altman Z-Score Widget
   - Top Dividend Stocks Widget
   - Earnings This Week Widget

2. **Analyse-Seite:**
   - Neuer Tab: "Financial Health"
   - Neuer Tab: "Financial Ratios"
   - Neuer Tab: "Dividends"
   - Neuer Tab: "Earnings"

3. **Neue Seite:**
   - "Dividend Dashboard" (vollständige Übersicht)
   - "Earnings Calendar" (vollständige Übersicht)

#### CSS Styling
```css
/* Financial Health Cards */
.financial-health-card {
    background: var(--bg-secondary);
    border-radius: var(--radius);
    padding: 1.5rem;
    box-shadow: var(--shadow);
}

.score-bar {
    width: 100%;
    height: 30px;
    background: var(--border-color);
    border-radius: var(--radius);
    overflow: hidden;
    margin: 1rem 0;
}

.score-fill {
    height: 100%;
    transition: width 0.5s ease;
}

.score-fill.success {
    background: linear-gradient(90deg, #10b981, #059669);
}

.score-fill.info {
    background: linear-gradient(90deg, #3b82f6, #2563eb);
}

.score-fill.warning {
    background: linear-gradient(90deg, #f59e0b, #d97706);
}

.score-fill.danger {
    background: linear-gradient(90deg, #ef4444, #dc2626);
}

.score-breakdown {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin: 1rem 0;
}

.score-category {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    background: var(--bg-primary);
    border-radius: var(--radius);
}

.score-status {
    text-align: center;
    padding: 1rem;
    border-radius: var(--radius);
    font-weight: 600;
    margin-top: 1rem;
}

/* Z-Score Scale */
.z-score-scale {
    margin: 1.5rem 0;
}

.z-scale-bar {
    position: relative;
    width: 100%;
    height: 20px;
    background: linear-gradient(90deg, #ef4444 0%, #f59e0b 30%, #10b981 50%, #10b981 100%);
    border-radius: var(--radius);
}

.z-marker {
    position: absolute;
    top: -5px;
    width: 4px;
    height: 30px;
    background: var(--text-primary);
    border: 2px solid white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.z-scale-labels,
.z-scale-values {
    display: flex;
    justify-content: space-between;
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: var(--text-secondary);
}
```

---

### Priorität 3: Performance & Caching (Woche 5)

#### Caching Strategy
```python
# app/services/cache_service.py

from app.models import StockCache
from datetime import datetime, timedelta

class FinancialDataCache:

    # Cache TTLs
    FINANCIAL_SCORE_TTL = 86400  # 24 hours (daily update)
    RATIOS_TTL = 3600  # 1 hour (for TTM data)
    DIVIDEND_TTL = 43200  # 12 hours
    EARNINGS_TTL = 3600  # 1 hour

    @staticmethod
    def get_cached_score(ticker: str):
        """Get cached financial score"""
        return StockCache.get_cached(ticker, 'financial_score')

    @staticmethod
    def set_cached_score(ticker: str, data: dict):
        """Cache financial score"""
        StockCache.set_cache(
            ticker,
            data,
            'financial_score',
            ttl=FinancialDataCache.FINANCIAL_SCORE_TTL
        )

    @staticmethod
    def get_cached_ratios(ticker: str):
        """Get cached financial ratios"""
        return StockCache.get_cached(ticker, 'financial_ratios')

    @staticmethod
    def set_cached_ratios(ticker: str, data: dict):
        """Cache financial ratios"""
        StockCache.set_cache(
            ticker,
            data,
            'financial_ratios',
            ttl=FinancialDataCache.RATIOS_TTL
        )
```

#### Rate Limit Management
```python
# app/services/rate_limiter.py

from datetime import datetime, timedelta
from collections import deque
import time

class APIRateLimiter:
    """Manage API rate limits across services"""

    def __init__(self, max_requests: int, time_window: int):
        """
        max_requests: Maximum requests allowed
        time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()

    def can_make_request(self) -> bool:
        """Check if we can make a request"""
        now = time.time()

        # Remove old requests outside time window
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()

        return len(self.requests) < self.max_requests

    def record_request(self):
        """Record a new request"""
        self.requests.append(time.time())

    def wait_time(self) -> float:
        """Calculate wait time until next request is allowed"""
        if self.can_make_request():
            return 0

        oldest_request = self.requests[0]
        wait_until = oldest_request + self.time_window
        return max(0, wait_until - time.time())

# Global rate limiters
FMP_LIMITER = APIRateLimiter(max_requests=5, time_window=60)  # 5/minute
ALPHA_VANTAGE_LIMITER = APIRateLimiter(max_requests=5, time_window=60)  # 5/minute
```

---

## 📅 Implementierungs-Timeline

### Woche 1-2: FMP Integration & Financial Health
**Ziel:** Piotroski Score, Altman Z-Score, Financial Ratios

**Tasks:**
- [x] FMP API Key beantragen (kostenlos)
- [ ] `fmp_service.py` erstellen
- [ ] Financial Score Endpoints
- [ ] Financial Ratios Endpoints
- [ ] Frontend Widgets (Piotroski, Altman)
- [ ] CSS Styling
- [ ] Integration in Analyse-Seite
- [ ] Dashboard Widgets
- [ ] Testing & Bugfixes

**Deliverables:**
- ✅ Piotroski Score Widget
- ✅ Altman Z-Score Widget
- ✅ Financial Ratios Tab
- ✅ Backend API Endpoints

---

### Woche 3-4: Dividends & Earnings
**Ziel:** Dividend Tracker, Earnings Calendar

**Tasks:**
- [ ] Dividend History Endpoint
- [ ] Dividend Calendar Endpoint
- [ ] Earnings Calendar Endpoint
- [ ] Earnings Surprise Endpoint
- [ ] Dividend Dashboard Frontend
- [ ] Earnings Calendar Frontend
- [ ] Dashboard Widgets
- [ ] Notifications für Earnings
- [ ] Testing & Bugfixes

**Deliverables:**
- ✅ Dividend Dashboard (neue Seite)
- ✅ Earnings Calendar (neue Seite)
- ✅ Dashboard Widgets (Dividends, Earnings)
- ✅ Earnings Notifications

---

### Woche 5-6: Advanced Screener
**Ziel:** Multi-Criteria Screener mit Fundamentals

**Tasks:**
- [ ] Erweiterte Screener API Integration
- [ ] Filter UI Implementation
- [ ] Preset Strategies Implementation
- [ ] Save Custom Filters Feature
- [ ] Alert on New Matches Feature
- [ ] Export Results Feature
- [ ] Testing & Bugfixes

**Deliverables:**
- ✅ Advanced Screener mit 50+ Filtern
- ✅ 6 Preset Strategies
- ✅ Save/Load Custom Filters
- ✅ Export to CSV

---

### Woche 7-8: Performance & Polish
**Ziel:** Caching, Rate Limiting, UI Polish

**Tasks:**
- [ ] Implement Comprehensive Caching
- [ ] Rate Limiter Implementation
- [ ] API Error Handling Improvements
- [ ] UI/UX Polish
- [ ] Mobile Responsiveness
- [ ] Documentation Updates
- [ ] Final Testing
- [ ] Production Deployment

**Deliverables:**
- ✅ All Features Cached
- ✅ Rate Limits Managed
- ✅ Mobile-Optimized
- ✅ Documentation Complete

---

## 💰 Kosten-Übersicht

### Aktuelle APIs (bereits integriert):
| API | Free Tier | Paid Tier | Status |
|-----|-----------|-----------|--------|
| Finnhub | 60 req/min | $59/mo (300 req/min) | ✅ Aktiv |
| Twelve Data | 800 req/day | $8/mo (8k req/day) | ✅ Aktiv |
| Alpha Vantage | 25 req/day | $49.99/mo (500 req/day) | ✅ Aktiv |
| Google Gemini AI | Rate Limited | Pay-per-use | ✅ Aktiv |

### Neue APIs (empfohlen):
| API | Free Tier | Paid Tier | Empfehlung |
|-----|-----------|-----------|------------|
| **FMP** | 250 req/day | $14/mo (300 req/min) | ⭐ JETZT |
| EODHD | Trial 7 Tage | $19.99/mo (unlimited) | 📅 SPÄTER |
| SimFin | 2k req/day | $15/mo (10k req/day) | 📅 OPTIONAL |

### Budget-Strategie:
**Phase 1 (Monate 1-3):** Nur kostenlose Tiers nutzen
- FMP Free: 250 req/day
- Alpha Vantage: 25 req/day (erweitern)
- Finnhub: 60 req/min
- Twelve Data: 800 req/day

**Phase 2 (Monate 4-6):** Bei Bedarf upgraden
- FMP Starter: $14/Monat (wenn Free Tier nicht reicht)

**Phase 3 (Monate 7+):** Premium Features
- EODHD All World: $19.99/Monat (globale Daten)
- FMP Premium: $29/Monat (höhere Limits)

**Geschätzte Kosten:**
- **Jetzt:** $0/Monat (Free Tiers)
- **Nach 3 Monaten:** $14/Monat (FMP Starter)
- **Nach 6 Monaten:** $34/Monat (FMP + EODHD)

---

## 🎯 Success Metrics

### Phase 1 Success:
- [ ] Piotroski Score für alle US Stocks verfügbar
- [ ] Altman Z-Score für alle US Stocks verfügbar
- [ ] Financial Ratios Tab vollständig implementiert
- [ ] Dashboard Widgets funktional
- [ ] < 2 Sekunden Ladezeit

### Phase 2 Success:
- [ ] Dividend Dashboard zeigt alle Dividenden im Portfolio
- [ ] Earnings Calendar zeigt nächste 30 Tage
- [ ] Earnings Notifications 24h vorher
- [ ] Dividend Calendar zeigt kommende Zahlungen

### Phase 3 Success:
- [ ] Screener unterstützt 50+ Filter
- [ ] 6 Preset Strategies funktionieren
- [ ] Custom Filter speicherbar
- [ ] Screener findet mindestens 100 Stocks

### Overall Success:
- [ ] API Rate Limits nicht überschritten
- [ ] 99%+ Daten-Verfügbarkeit
- [ ] User-Feedback positiv
- [ ] Feature-Nutzung > 50% der User

---

## 🚀 Quick Start Guide

### Schritt 1: FMP API Key beantragen
1. Gehe zu https://site.financialmodelingprep.com/developer/docs/pricing
2. Wähle "Free" Plan
3. Registriere Account
4. Kopiere API Key
5. Füge zu `.env` hinzu:
```bash
FMP_API_KEY=your_api_key_here
```

### Schritt 2: Backend Installation
```bash
# Install dependencies (if needed)
pip install requests

# Test FMP API
python test_fmp_integration.py
```

### Schritt 3: Frontend Integration
```bash
# Add scripts to index.html
<script src="/static/js/financial-health.js"></script>

# Add CSS
<link rel="stylesheet" href="/static/css/financial-health.css">
```

### Schritt 4: Deploy & Test
```bash
# Commit changes
git add .
git commit -m "feat: Add FMP integration for financial health scores"

# Push to production
git push origin main

# Test on live site
# Navigate to stock analysis page
# Check new "Financial Health" tab
```

---

## 📝 Next Steps

1. **Sofort:**
   - FMP API Key beantragen
   - `fmp_service.py` erstellen
   - Piotroski Score Widget implementieren

2. **Diese Woche:**
   - Financial Health Tab in Analyse-Seite
   - Dashboard Widgets
   - Testing

3. **Nächste Woche:**
   - Altman Z-Score Widget
   - Financial Ratios Tab
   - Production Deployment

4. **Diesen Monat:**
   - Dividend Dashboard
   - Earnings Calendar
   - Advanced Screener Prototype

---

## 🔍 Alternativen zu Morningstar

### Was Morningstar bietet (nicht kostenlos):
- ❌ Proprietary Star Ratings (bezahlt)
- ❌ Fair Value Estimates (bezahlt)
- ❌ Economic Moat Ratings (bezahlt)
- ❌ Sustainability Ratings (bezahlt)

### Was wir kostenlos nachbauen können:
- ✅ Financial Health Scores (Piotroski, Altman) via FMP
- ✅ Comprehensive Ratios via FMP/Alpha Vantage
- ✅ Dividend Analysis via FMP
- ✅ Earnings Analysis via FMP
- ✅ Stock Screener via FMP/EODHD
- ✅ Analyst Ratings via Finnhub
- ✅ AI-Generated Analysis via Gemini (eigener Moat Analysis)

### Unsere Vorteile:
- 💪 **AI-Integration:** Gemini 2.5 Pro für tiefere Analyse
- 💪 **Real-time Data:** WebSocket Updates
- 💪 **German Stocks:** XETRA Support
- 💪 **Custom Dashboards:** Individuell anpassbar
- 💪 **Portfolio Tracking:** Vollständiges Portfolio Management
- 💪 **No Paywall:** Alle Features kostenlos

---

## 📚 Resources

### API Dokumentation:
- FMP: https://site.financialmodelingprep.com/developer/docs
- Alpha Vantage: https://www.alphavantage.co/documentation/
- EODHD: https://eodhd.com/financial-apis/
- Finnhub: https://finnhub.io/docs/api
- SimFin: https://simfin.com/api/v2/documentation/

### Educational:
- Piotroski Score: https://en.wikipedia.org/wiki/Piotroski_F-score
- Altman Z-Score: https://en.wikipedia.org/wiki/Altman_Z-score
- Financial Ratios: https://www.investopedia.com/financial-ratios-4689817

### Community:
- GitHub Issues: https://github.com/Muchel187/stock-analyzer-pwa/issues
- Discord: (optional)

---

**Erstellt mit Claude Code am 2. Oktober 2025**
**Nächstes Update:** Nach Phase 1 Completion
