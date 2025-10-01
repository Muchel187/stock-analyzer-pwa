import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.stock_service import StockService

logger = logging.getLogger(__name__)

class ScreenerService:
    """Service for stock screening and filtering"""

    # Popular US stocks
    US_STOCKS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK-B', 'V', 'JNJ',
        'WMT', 'JPM', 'MA', 'PG', 'UNH', 'HD', 'DIS', 'PYPL', 'BAC', 'NFLX',
        'ADBE', 'CRM', 'PFE', 'TMO', 'ABBV', 'CSCO', 'PEP', 'AVGO', 'NKE', 'CMCSA',
        'COST', 'CVX', 'WFC', 'INTC', 'AMD', 'QCOM', 'TXN', 'HON', 'UPS', 'IBM',
        'GS', 'AMGN', 'SBUX', 'CAT', 'BA', 'GE', 'MMM', 'MCD', 'F', 'GM'
    ]

    # DAX 40 stocks
    DAX_STOCKS = [
        'ADS.DE', 'AIR.DE', 'ALV.DE', 'BAS.DE', 'BAYN.DE', 'BEI.DE', 'BMW.DE', 'CON.DE',
        'DAI.DE', 'DBK.DE', 'DHL.DE', 'DTE.DE', 'EOAN.DE', 'FRE.DE', 'HEI.DE', 'HEN3.DE',
        'IFX.DE', 'LIN.DE', 'MRK.DE', 'MTX.DE', 'MUV2.DE', 'PAH3.DE', 'PUM.DE', 'RWE.DE',
        'SAP.DE', 'SIE.DE', 'SY1.DE', 'VOW3.DE', 'VNA.DE', 'ZAL.DE'
    ]

    @classmethod
    def screen_stocks(cls, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Screen stocks based on criteria"""
        try:
            # Get list of stocks to screen
            stocks_to_screen = cls._get_stocks_to_screen(criteria.get('market', 'USA'))

            # Apply screening in parallel
            screened_stocks = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {
                    executor.submit(cls._screen_single_stock, ticker, criteria): ticker
                    for ticker in stocks_to_screen
                }

                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        screened_stocks.append(result)

            # Sort by the specified sort criterion
            sort_by = criteria.get('sort_by', 'market_cap')
            reverse = criteria.get('sort_order', 'desc') == 'desc'
            screened_stocks.sort(key=lambda x: x.get(sort_by, 0) or 0, reverse=reverse)

            # Apply limit
            limit = min(criteria.get('limit', 100), 100)
            return screened_stocks[:limit]

        except Exception as e:
            logger.error(f"Error in stock screening: {str(e)}")
            return []

    @classmethod
    def _get_stocks_to_screen(cls, market: str) -> List[str]:
        """Get list of stocks based on market"""
        if market == 'DAX':
            return cls.DAX_STOCKS
        elif market == 'ALL':
            return cls.US_STOCKS + cls.DAX_STOCKS
        else:  # Default to USA
            return cls.US_STOCKS

    @classmethod
    def _screen_single_stock(cls, ticker: str, criteria: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Screen a single stock against criteria"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            if not info:
                return None

            # Extract metrics
            metrics = {
                'ticker': ticker,
                'company_name': info.get('longName', info.get('shortName', ticker)),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'dividend_yield': info.get('dividendYield'),
                'price_to_book': info.get('priceToBook'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'profit_margin': info.get('profitMargins'),
                'return_on_equity': info.get('returnOnEquity'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'beta': info.get('beta'),
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'volume': info.get('volume'),
                'avg_volume': info.get('averageVolume'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                '52_week_high': info.get('fiftyTwoWeekHigh')
            }

            # Apply filters
            if not cls._passes_filters(metrics, criteria):
                return None

            # Calculate additional metrics
            if metrics['current_price'] and metrics['52_week_low'] and metrics['52_week_high']:
                metrics['52_week_position'] = (
                    (metrics['current_price'] - metrics['52_week_low']) /
                    (metrics['52_week_high'] - metrics['52_week_low'])
                ) * 100 if metrics['52_week_high'] > metrics['52_week_low'] else 50

            # Add score based on criteria
            metrics['score'] = cls._calculate_stock_score(metrics, criteria)

            return metrics

        except Exception as e:
            logger.debug(f"Error screening {ticker}: {str(e)}")
            return None

    @classmethod
    def _passes_filters(cls, metrics: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if stock passes all filter criteria"""
        try:
            # Market cap filter
            if 'min_market_cap' in criteria and metrics.get('market_cap', 0) < criteria['min_market_cap']:
                return False
            if 'max_market_cap' in criteria and metrics.get('market_cap', float('inf')) > criteria['max_market_cap']:
                return False

            # P/E ratio filter
            pe = metrics.get('pe_ratio')
            if pe is not None:
                if 'min_pe_ratio' in criteria and pe < criteria['min_pe_ratio']:
                    return False
                if 'max_pe_ratio' in criteria and pe > criteria['max_pe_ratio']:
                    return False

            # Dividend yield filter
            div_yield = metrics.get('dividend_yield')
            if div_yield is not None:
                if 'min_dividend_yield' in criteria and div_yield < criteria['min_dividend_yield']:
                    return False
                if 'max_dividend_yield' in criteria and div_yield > criteria['max_dividend_yield']:
                    return False

            # Sector filter
            if 'sectors' in criteria and criteria['sectors']:
                if metrics.get('sector') not in criteria['sectors']:
                    return False

            # Price filter
            price = metrics.get('current_price')
            if price is not None:
                if 'min_price' in criteria and price < criteria['min_price']:
                    return False
                if 'max_price' in criteria and price > criteria['max_price']:
                    return False

            # Volume filter
            volume = metrics.get('avg_volume')
            if volume is not None:
                if 'min_volume' in criteria and volume < criteria['min_volume']:
                    return False

            # Beta filter (volatility)
            beta = metrics.get('beta')
            if beta is not None:
                if 'min_beta' in criteria and beta < criteria['min_beta']:
                    return False
                if 'max_beta' in criteria and beta > criteria['max_beta']:
                    return False

            # Profitability filters
            if 'only_profitable' in criteria and criteria['only_profitable']:
                if metrics.get('profit_margin', 0) <= 0:
                    return False

            # Growth filters
            if 'min_revenue_growth' in criteria:
                if metrics.get('revenue_growth', -1) < criteria['min_revenue_growth']:
                    return False

            return True

        except Exception as e:
            logger.debug(f"Error in filter check: {str(e)}")
            return False

    @classmethod
    def _calculate_stock_score(cls, metrics: Dict[str, Any], criteria: Dict[str, Any]) -> float:
        """Calculate a score for the stock based on criteria preferences"""
        score = 50.0  # Base score

        # Value scoring
        if criteria.get('prefer_value'):
            pe = metrics.get('pe_ratio')
            if pe and pe > 0:
                if pe < 15:
                    score += 10
                elif pe < 25:
                    score += 5
                elif pe > 35:
                    score -= 5

            pb = metrics.get('price_to_book')
            if pb and pb > 0:
                if pb < 1:
                    score += 5
                elif pb > 3:
                    score -= 3

        # Growth scoring
        if criteria.get('prefer_growth'):
            revenue_growth = metrics.get('revenue_growth')
            if revenue_growth:
                if revenue_growth > 0.2:
                    score += 10
                elif revenue_growth > 0.1:
                    score += 5
                elif revenue_growth < 0:
                    score -= 5

        # Dividend scoring
        if criteria.get('prefer_dividends'):
            div_yield = metrics.get('dividend_yield')
            if div_yield:
                if div_yield > 0.04:
                    score += 10
                elif div_yield > 0.02:
                    score += 5

        # Quality scoring
        roe = metrics.get('return_on_equity')
        if roe and roe > 0:
            if roe > 0.2:
                score += 5
            elif roe > 0.15:
                score += 3

        # Momentum scoring
        if criteria.get('prefer_momentum'):
            week_52_pos = metrics.get('52_week_position')
            if week_52_pos:
                if week_52_pos > 70:
                    score += 5
                elif week_52_pos < 30:
                    score -= 5

        return min(100, max(0, score))

    @classmethod
    def get_predefined_screens(cls) -> List[Dict[str, Any]]:
        """Get list of predefined screening strategies"""
        return [
            {
                'name': 'Value Stocks',
                'description': 'Undervalued stocks with low P/E ratios',
                'criteria': {
                    'max_pe_ratio': 15,
                    'min_market_cap': 1000000000,
                    'prefer_value': True
                }
            },
            {
                'name': 'Growth Stocks',
                'description': 'High growth companies',
                'criteria': {
                    'min_revenue_growth': 0.15,
                    'prefer_growth': True,
                    'min_market_cap': 1000000000
                }
            },
            {
                'name': 'Dividend Aristocrats',
                'description': 'High dividend yield stocks',
                'criteria': {
                    'min_dividend_yield': 0.03,
                    'prefer_dividends': True,
                    'min_market_cap': 5000000000
                }
            },
            {
                'name': 'Blue Chips',
                'description': 'Large, stable companies',
                'criteria': {
                    'min_market_cap': 50000000000,
                    'max_beta': 1.2,
                    'only_profitable': True
                }
            },
            {
                'name': 'Momentum Stocks',
                'description': 'Stocks near 52-week highs',
                'criteria': {
                    'prefer_momentum': True,
                    'min_volume': 1000000
                }
            },
            {
                'name': 'Small Cap Growth',
                'description': 'Small cap stocks with growth potential',
                'criteria': {
                    'min_market_cap': 300000000,
                    'max_market_cap': 2000000000,
                    'min_revenue_growth': 0.1,
                    'prefer_growth': True
                }
            }
        ]