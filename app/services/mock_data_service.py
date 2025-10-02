"""
Mock Data Service for Development and API Failure Fallback
Provides realistic mock data when APIs are unavailable or rate-limited
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MockDataService:
    """
    Provides realistic mock data for all stock-related endpoints
    Used when APIs are rate-limited or during development
    """

    # Popular stocks with realistic data
    MOCK_STOCKS = {
        'AAPL': {
            'name': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'exchange': 'NASDAQ',
            'currency': 'USD',
            'base_price': 255.50,
            'volatility': 0.02,
            'market_cap': 3900000000000,
            'pe_ratio': 33.5,
            'dividend_yield': 0.0044
        },
        'MSFT': {
            'name': 'Microsoft Corporation',
            'sector': 'Technology',
            'industry': 'Software',
            'exchange': 'NASDAQ',
            'currency': 'USD',
            'base_price': 430.25,
            'volatility': 0.018,
            'market_cap': 3200000000000,
            'pe_ratio': 36.8,
            'dividend_yield': 0.0066
        },
        'GOOGL': {
            'name': 'Alphabet Inc.',
            'sector': 'Technology',
            'industry': 'Internet Services',
            'exchange': 'NASDAQ',
            'currency': 'USD',
            'base_price': 178.90,
            'volatility': 0.022,
            'market_cap': 2200000000000,
            'pe_ratio': 28.9,
            'dividend_yield': 0
        },
        'TSLA': {
            'name': 'Tesla, Inc.',
            'sector': 'Consumer Cyclical',
            'industry': 'Auto Manufacturers',
            'exchange': 'NASDAQ',
            'currency': 'USD',
            'base_price': 248.50,
            'volatility': 0.035,
            'market_cap': 790000000000,
            'pe_ratio': 79.2,
            'dividend_yield': 0
        },
        'AMZN': {
            'name': 'Amazon.com, Inc.',
            'sector': 'Consumer Cyclical',
            'industry': 'Internet Retail',
            'exchange': 'NASDAQ',
            'currency': 'USD',
            'base_price': 185.45,
            'volatility': 0.025,
            'market_cap': 1900000000000,
            'pe_ratio': 45.3,
            'dividend_yield': 0
        },
        'SAP.DE': {
            'name': 'SAP SE',
            'sector': 'Technology',
            'industry': 'Software',
            'exchange': 'XETRA',
            'currency': 'EUR',
            'base_price': 195.80,
            'volatility': 0.02,
            'market_cap': 228000000000,
            'pe_ratio': 42.1,
            'dividend_yield': 0.013
        },
        'BMW.DE': {
            'name': 'Bayerische Motoren Werke AG',
            'sector': 'Consumer Cyclical',
            'industry': 'Auto Manufacturers',
            'exchange': 'XETRA',
            'currency': 'EUR',
            'base_price': 78.50,
            'volatility': 0.025,
            'market_cap': 50000000000,
            'pe_ratio': 5.8,
            'dividend_yield': 0.087
        }
    }

    @staticmethod
    def get_mock_stock_info(ticker: str) -> Dict[str, Any]:
        """Generate realistic mock stock info"""
        ticker = ticker.upper()

        # Get base data or generate for unknown tickers
        if ticker in MockDataService.MOCK_STOCKS:
            base = MockDataService.MOCK_STOCKS[ticker]
        else:
            base = MockDataService._generate_random_stock_data(ticker)

        # Generate current price with some randomness
        price_change = random.uniform(-base['volatility'], base['volatility'])
        current_price = round(base['base_price'] * (1 + price_change), 2)
        change = round(current_price - base['base_price'], 2)
        change_percent = round(price_change * 100, 2)

        # Generate day range
        day_low = round(current_price * (1 - base['volatility'] * 0.5), 2)
        day_high = round(current_price * (1 + base['volatility'] * 0.5), 2)

        return {
            'ticker': ticker,
            'company_name': base['name'],
            'current_price': current_price,
            'change': change,
            'change_percent': change_percent,
            'day_low': day_low,
            'day_high': day_high,
            'volume': random.randint(10000000, 100000000),
            'market_cap': base['market_cap'],
            'pe_ratio': base['pe_ratio'],
            'dividend_yield': base['dividend_yield'],
            'sector': base['sector'],
            'industry': base['industry'],
            'exchange': base['exchange'],
            'currency': base['currency'],
            'source': 'mock_data',
            'warning': 'Using mock data due to API limitations'
        }

    @staticmethod
    def get_mock_historical_data(ticker: str, period: str = '1mo') -> Dict[str, Any]:
        """Generate realistic historical price data"""
        ticker = ticker.upper()

        # Get base data
        if ticker in MockDataService.MOCK_STOCKS:
            base = MockDataService.MOCK_STOCKS[ticker]
        else:
            base = MockDataService._generate_random_stock_data(ticker)

        # Calculate number of data points based on period
        period_days = {
            '1d': 1, '5d': 5, '1mo': 30, '3mo': 90,
            '6mo': 180, '1y': 365, '2y': 730, '5y': 1825
        }
        days = period_days.get(period, 30)

        # Generate historical data
        data = []
        end_date = datetime.now().date()
        current_price = base['base_price']

        for i in range(days):
            date = end_date - timedelta(days=days - i - 1)

            # Skip weekends
            if date.weekday() >= 5:
                continue

            # Generate OHLCV data with realistic patterns
            daily_volatility = base['volatility'] * random.uniform(0.5, 1.5)
            open_price = current_price * (1 + random.uniform(-daily_volatility * 0.5, daily_volatility * 0.5))

            # Intraday movement
            high = open_price * (1 + random.uniform(0, daily_volatility))
            low = open_price * (1 - random.uniform(0, daily_volatility))

            # Close price tends to be between open and high/low
            close = random.uniform(low, high)

            # Volume with some randomness
            volume = random.randint(20000000, 150000000)

            data.append({
                'date': date.isoformat(),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })

            # Update current price for next day
            current_price = close

        return {
            'ticker': ticker,
            'period': period,
            'data': data,
            'source': 'mock_data',
            'warning': 'Using mock historical data due to API limitations'
        }

    @staticmethod
    def get_mock_technical_indicators(ticker: str) -> Dict[str, Any]:
        """Generate realistic technical indicators"""
        ticker = ticker.upper()

        return {
            'ticker': ticker,
            'rsi': round(random.uniform(30, 70), 2),
            'macd': {
                'macd': round(random.uniform(-2, 2), 3),
                'signal': round(random.uniform(-2, 2), 3),
                'histogram': round(random.uniform(-1, 1), 3)
            },
            'bollinger_bands': {
                'upper': round(random.uniform(260, 270), 2),
                'middle': round(random.uniform(250, 260), 2),
                'lower': round(random.uniform(240, 250), 2),
                'current_position': round(random.uniform(0.3, 0.7), 2)
            },
            'sma_20': round(random.uniform(245, 255), 2),
            'sma_50': round(random.uniform(240, 250), 2),
            'sma_200': round(random.uniform(230, 245), 2),
            'ema_12': round(random.uniform(248, 258), 2),
            'ema_26': round(random.uniform(245, 255), 2),
            'volume_trend': random.choice(['high', 'normal', 'low']),
            'volatility': round(random.uniform(0.15, 0.35), 3),
            'source': 'mock_data',
            'warning': 'Using mock technical indicators'
        }

    @staticmethod
    def get_mock_fundamental_analysis(ticker: str) -> Dict[str, Any]:
        """Generate mock fundamental analysis"""
        ticker = ticker.upper()

        return {
            'ticker': ticker,
            'scores': {
                'value_score': round(random.uniform(40, 80), 1),
                'financial_health_score': round(random.uniform(50, 90), 1),
                'profitability_score': round(random.uniform(45, 85), 1),
                'growth_score': round(random.uniform(40, 75), 1)
            },
            'overall_score': round(random.uniform(50, 75), 1),
            'recommendation': random.choice(['Buy', 'Hold', 'Hold', 'Sell']),
            'metrics': {
                'pe_ratio': round(random.uniform(15, 45), 1),
                'peg_ratio': round(random.uniform(0.8, 2.5), 2),
                'price_to_book': round(random.uniform(2, 8), 1),
                'debt_to_equity': round(random.uniform(0.3, 1.5), 2),
                'current_ratio': round(random.uniform(1.0, 2.5), 2),
                'profit_margin': round(random.uniform(0.05, 0.25), 3),
                'return_on_equity': round(random.uniform(0.10, 0.30), 3)
            },
            'source': 'mock_data',
            'warning': 'Using mock fundamental data'
        }

    @staticmethod
    def get_mock_ai_analysis(ticker: str, stock_data: Dict = None) -> Dict[str, Any]:
        """Generate comprehensive mock AI analysis matching real Gemini format"""
        ticker = ticker.upper()

        recommendations = ['KAUFEN', 'HALTEN', 'VERKAUFEN']
        recommendation = random.choice(recommendations)

        base_price = stock_data.get('current_price', 250) if stock_data else 250
        price_target = round(base_price * random.uniform(0.90, 1.12), 2)

        # Generate realistic technical data
        rsi = round(random.uniform(35, 70), 1)
        macd_signal = random.choice(['bullish', 'bearish', 'neutral'])

        # Generate realistic fundamental strengths
        fundamentals = random.choice([
            ('starke', 'wachsende'),
            ('solide', 'stabile'),
            ('moderate', 'gemischte'),
            ('schwache', 'rückläufige')
        ])

        # Generate risks and opportunities
        risks_pool = [
            ('Marktvolatilität', 'Erhöhte Schwankungen könnten kurzfristige Verluste verursachen.'),
            ('Zinsrisiko', 'Steigende Zinsen könnten die Bewertung belasten.'),
            ('Wettbewerbsdruck', 'Neue Konkurrenten könnten Marktanteile erobern.'),
            ('Regulatorische Änderungen', 'Neue Vorschriften könnten Kosten erhöhen.'),
            ('Makroökonomische Unsicherheit', 'Rezessionsrisiken belasten die Aussichten.'),
            ('Technologische Disruption', 'Neue Technologien könnten Geschäftsmodell gefährden.')
        ]

        opportunities_pool = [
            ('Marktexpansion', 'Wachstumspotenzial in neuen Märkten, besonders in Asien.'),
            ('Produktinnovation', 'Neue Produktlinien könnten Umsatzwachstum treiben.'),
            ('Kostenoptimierung', 'Effizienzsteigerungen verbessern Margen.'),
            ('Strategische Partnerschaften', 'Kooperationen erweitern Kundenbasis.'),
            ('Digitale Transformation', 'Cloud-Migration erhöht Wettbewerbsfähigkeit.'),
            ('M&A-Potenzial', 'Akquisitionen könnten Marktposition stärken.')
        ]

        # Select 3-4 risks and opportunities
        selected_risks = random.sample(risks_pool, k=random.randint(3, 4))
        selected_opportunities = random.sample(opportunities_pool, k=random.randint(3, 4))

        return {
            'ticker': ticker,
            'analysis': f"""
## 1. TECHNISCHE ANALYSE 📈

**Überblick:** Die technische Analyse von {ticker} zeigt ein {random.choice(['vielversprechendes', 'neutrales', 'gemischtes'])} Bild mit mehreren wichtigen Indikatoren.

**RSI (Relative Strength Index):** {rsi}
- Der RSI liegt bei {rsi}, was auf {('überkaufte' if rsi > 70 else 'überverkaufte' if rsi < 30 else 'neutrale')} Bedingungen hindeutet.
- Empfehlung: {('Vorsicht bei Neueinsteigen' if rsi > 70 else 'Potenzielle Kaufgelegenheit' if rsi < 30 else 'Normales Handelsniveau')}

**MACD (Moving Average Convergence Divergence):**
- Signal: {macd_signal.capitalize()}
- Der MACD zeigt ein {macd_signal}es Signal, was {('steigende Kurse' if macd_signal == 'bullish' else 'fallende Kurse' if macd_signal == 'bearish' else 'Seitwärtsbewegung')} nahelegt.

**Gleitende Durchschnitte:**
- SMA 20: ${round(base_price * random.uniform(0.98, 1.02), 2)}
- SMA 50: ${round(base_price * random.uniform(0.95, 1.05), 2)}
- SMA 200: ${round(base_price * random.uniform(0.90, 1.10), 2)}

Der Kurs liegt {random.choice(['über', 'unter', 'nahe'])} dem 200-Tage-Durchschnitt, was auf einen {random.choice(['Aufwärts', 'Abwärts', 'Seitwärts'])}-Trend hindeutet.

**Bollinger Bänder:**
- Die Aktie bewegt sich {random.choice(['im mittleren Bereich', 'am oberen Band', 'am unteren Band'])} der Bollinger Bänder.
- Volatilität: {random.choice(['Erhöht', 'Normal', 'Niedrig'])}

## 2. FUNDAMENTALANALYSE 💼

**Unternehmensstärke:** {ticker} zeigt {fundamentals[0]} Fundamentaldaten mit {fundamentals[1]} Geschäftsentwicklung.

**Bewertungskennzahlen:**
- P/E Ratio: {round(random.uniform(15, 40), 1)}x
- P/B Ratio: {round(random.uniform(2, 8), 1)}x
- PEG Ratio: {round(random.uniform(0.8, 2.5), 2)}

**Profitabilität:**
- Gewinnmarge: {round(random.uniform(8, 25), 1)}%
- ROE (Return on Equity): {round(random.uniform(10, 30), 1)}%
- Verschuldungsgrad: {round(random.uniform(0.3, 1.5), 2)}

**Wachstum:**
- Umsatzwachstum (YoY): {round(random.uniform(-5, 15), 1)}%
- Gewinnwachstum (YoY): {round(random.uniform(-10, 20), 1)}%

Die Fundamentaldaten deuten auf ein {random.choice(['stabiles', 'wachsendes', 'herausforderndes'])} Geschäftsmodell hin.

## 3. HAUPTRISIKEN ⚠️

{''.join([f"**Risiko {i+1}: {risk[0]}**\n{risk[1]}\n\n" for i, risk in enumerate(selected_risks)])}

## 4. CHANCEN 🎯

{''.join([f"**Chance {i+1}: {opp[0]}**\n{opp[1]}\n\n" for i, opp in enumerate(selected_opportunities)])}

## 5. KURSZIEL 🎯

**12-Monats-Kursziel:** ${price_target}
**Aktueller Kurs:** ${base_price}
**Potenzial:** {round(((price_target / base_price) - 1) * 100, 1)}%

**Bewertungsmethode:** Kombinierte DCF-Analyse und Peer-Vergleich

**Kurszielspanne:**
- Bear Case: ${round(base_price * 0.85, 2)}
- Base Case: ${price_target}
- Bull Case: ${round(base_price * 1.20, 2)}

## 6. SHORT SQUEEZE POTENZIAL 🔥

**Squeeze Score:** {random.randint(10, 40)}/100

**Due Diligence Faktoren:**
- Short Interest: ~{round(random.uniform(3, 15), 1)}% des Float
- Days to Cover: ~{round(random.uniform(1.5, 5), 1)} Tage
- Borrowing Costs: {random.choice(['Niedrig', 'Moderat', 'Erhöht'])}

**Analyse:** Das Short-Squeeze-Potenzial ist aktuell als {random.choice(['gering', 'moderat', 'erhöht'])} einzustufen. Die Short-Quote liegt im {random.choice(['unteren', 'mittleren'])} Bereich.

## 7. INVESTMENTEMPFEHLUNG 📊

**Urteil:** **{recommendation}**

**Begründung:**
Basierend auf der umfassenden Analyse empfehlen wir {recommendation.upper()}. Die {fundamentals[0]}n Fundamentaldaten und die {random.choice(['positive', 'neutrale', 'gemischte'])} technische Lage rechtfertigen diese Einschätzung.

**Hauptfaktoren:**
1. **Bewertung:** {random.choice(['Fair bewertet', 'Leicht überbewertet', 'Attraktiv bewertet'])}
2. **Wachstumsperspektiven:** {random.choice(['Vielversprechend', 'Moderat', 'Begrenzt'])}
3. **Risiko-Ertrags-Verhältnis:** {random.choice(['Ausgewogen', 'Konservativ', 'Risikoreich'])}

**Zeithorizont:**
- Kurzfristig (0-3 Monate): {random.choice(['HALTEN', 'KAUFEN', 'VERKAUFEN'])}
- Mittelfristig (3-12 Monate): {recommendation}
- Langfristig (1+ Jahre): {random.choice(['KAUFEN', 'HALTEN'])}

---
*Hinweis: Dies sind Mock-Daten für Demonstrationszwecke während API-Ausfällen. Echte Gemini AI-Analysen sind bei verfügbarem API-Kontingent deutlich detaillierter.*
            """,
            'recommendation': recommendation,
            'confidence_score': round(random.uniform(65, 90), 1),
            'price_target': price_target,
            'risk_level': random.choice(['Niedrig', 'Mittel', 'Hoch']),
            'source': 'mock_ai',
            'warning': 'Mock-Analyse während API-Quota-Überschreitung - Wartet auf Gemini API Reset'
        }

    @staticmethod
    def _generate_random_stock_data(ticker: str) -> Dict[str, Any]:
        """Generate random stock data for unknown tickers"""
        return {
            'name': f'{ticker} Corporation',
            'sector': random.choice(['Technology', 'Healthcare', 'Finance', 'Consumer', 'Industrial']),
            'industry': 'Unknown',
            'exchange': 'NASDAQ',
            'currency': 'USD',
            'base_price': round(random.uniform(20, 500), 2),
            'volatility': round(random.uniform(0.015, 0.04), 3),
            'market_cap': random.randint(1000000000, 100000000000),
            'pe_ratio': round(random.uniform(10, 50), 1),
            'dividend_yield': round(random.uniform(0, 0.05), 3)
        }

    @staticmethod
    def is_mock_mode_enabled() -> bool:
        """Check if mock mode should be used"""
        import os
        # Enable mock mode via environment variable or when APIs are failing
        return os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'