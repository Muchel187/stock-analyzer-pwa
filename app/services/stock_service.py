import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from app.models import StockCache
from app import cache
import logging
from app.services.alternative_data_sources import FallbackDataService, AlphaVantageService

logger = logging.getLogger(__name__)

class StockService:
    """Service for fetching and analyzing stock data"""

    @staticmethod
    def get_stock_info(ticker: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive stock information using Finnhub and Alpha Vantage"""
        try:
            # Check cache first
            cached = StockCache.get_cached(ticker, 'info')
            if cached:
                return cached

            # Get quote data from fallback sources (Finnhub primary)
            quote_data = FallbackDataService.get_stock_quote(ticker)
            if not quote_data:
                logger.error(f"Failed to get quote data for {ticker}")
                return None

            # Try to get additional company information
            company_data = FallbackDataService.get_company_info(ticker)

            # Merge the data
            processed_info = FallbackDataService.merge_data(quote_data, company_data)

            # Add default values for missing fields
            processed_info.setdefault('market', 'DAX' if '.DE' in ticker.upper() else 'USA')
            processed_info.setdefault('sector', 'Unknown')
            processed_info.setdefault('industry', 'Unknown')
            processed_info.setdefault('ticker', ticker.upper())

            # Get enhanced data: Analyst ratings, price targets, insider transactions
            analyst_ratings = StockService.get_analyst_ratings(ticker)
            if analyst_ratings:
                processed_info['analyst_ratings'] = analyst_ratings
                logger.info(f"Added analyst ratings for {ticker}")

            price_target = StockService.get_price_target(ticker)
            if price_target:
                processed_info['price_target'] = price_target
                logger.info(f"Added price target for {ticker}")

            insider_data = StockService.get_insider_transactions(ticker)
            if insider_data:
                processed_info['insider_transactions'] = insider_data
                logger.info(f"Added insider transactions for {ticker}")

            # Cache the result
            StockCache.set_cache(ticker, processed_info, 'info')

            return processed_info

        except Exception as e:
            logger.error(f"Error fetching stock info for {ticker}: {str(e)}")
            return None

    @staticmethod
    def get_price_history(ticker: str, period: str = "1y") -> Optional[Dict[str, Any]]:
        """Get historical price data using the new HistoricalDataService"""
        try:
            # Import here to avoid circular import
            from app.services.historical_data_service import HistoricalDataService

            logger.info(f"Getting price history for {ticker}, period={period}")

            # Use the new historical data service with smart caching
            historical_data = HistoricalDataService.get_historical_data(
                ticker=ticker,
                period=period,
                force_update=False
            )

            if historical_data and historical_data.get('data'):
                logger.info(f"Got {len(historical_data.get('data', []))} data points from {historical_data.get('source', 'unknown')}")
                return historical_data

            # If historical service fails, try the old fallback as last resort
            logger.warning(f"HistoricalDataService failed for {ticker}, trying old fallback")
            period_map = {
                '1mo': 30,
                '3mo': 90,
                '6mo': 180,
                '1y': 365,
                '2y': 730,
                '5y': 1825
            }
            outputsize = period_map.get(period, 365)

            fallback_data = FallbackDataService.get_historical_data(ticker, outputsize=outputsize)
            if fallback_data:
                fallback_data['period'] = period
                return fallback_data

            logger.error(f"Failed to get history for {ticker} from all sources")
            return None

        except Exception as e:
            logger.error(f"Error fetching price history for {ticker}: {str(e)}")
            return None

    @staticmethod
    def calculate_technical_indicators(ticker: str) -> Optional[Dict[str, Any]]:
        """Calculate technical indicators for a stock using historical data"""
        try:
            # Get historical data
            hist_data = StockService.get_price_history(ticker, period="6mo")
            if not hist_data or not hist_data.get('data'):
                logger.warning(f"No historical data available for technical indicators: {ticker}")
                return None

            # Convert to pandas DataFrame
            df = pd.DataFrame(hist_data['data'])
            if df.empty or len(df) < 50:
                logger.warning(f"Insufficient historical data for {ticker}: {len(df)} days")
                return None

            close_prices = pd.Series([float(x) for x in df['close']])
            volumes = pd.Series([int(x) for x in df['volume']])

            # Calculate technical indicators
            indicators = {
                'ticker': ticker.upper(),
                'rsi': StockService._calculate_rsi(close_prices),
                'macd': StockService._calculate_macd(close_prices),
                'bollinger_bands': StockService._calculate_bollinger_bands(close_prices),
                'sma_20': float(close_prices.rolling(window=20).mean().iloc[-1]) if len(close_prices) >= 20 else None,
                'sma_50': float(close_prices.rolling(window=50).mean().iloc[-1]) if len(close_prices) >= 50 else None,
                'ema_12': float(close_prices.ewm(span=12).mean().iloc[-1]),
                'ema_26': float(close_prices.ewm(span=26).mean().iloc[-1]),
                'volume_trend': StockService._calculate_volume_trend_series(volumes),
                'price_change_1d': float((close_prices.iloc[-1] - close_prices.iloc[-2]) / close_prices.iloc[-2] * 100) if len(close_prices) > 1 else 0,
                'price_change_1w': float((close_prices.iloc[-1] - close_prices.iloc[-5]) / close_prices.iloc[-5] * 100) if len(close_prices) > 5 else 0,
                'price_change_1m': float((close_prices.iloc[-1] - close_prices.iloc[-20]) / close_prices.iloc[-20] * 100) if len(close_prices) > 20 else 0,
                'volatility': float(close_prices.pct_change().std() * np.sqrt(252))  # Annualized volatility
            }

            return indicators

        except Exception as e:
            logger.error(f"Error calculating technical indicators for {ticker}: {str(e)}")
            return None

    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])

    @staticmethod
    def _calculate_macd(prices: pd.Series) -> Dict[str, float]:
        """Calculate MACD indicator"""
        ema_12 = prices.ewm(span=12).mean()
        ema_26 = prices.ewm(span=26).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9).mean()
        histogram = macd_line - signal_line

        return {
            'macd': float(macd_line.iloc[-1]),
            'signal': float(signal_line.iloc[-1]),
            'histogram': float(histogram.iloc[-1])
        }

    @staticmethod
    def _calculate_bollinger_bands(prices: pd.Series, period: int = 20) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)

        return {
            'upper': float(upper_band.iloc[-1]),
            'middle': float(sma.iloc[-1]),
            'lower': float(lower_band.iloc[-1]),
            'current_position': float((prices.iloc[-1] - lower_band.iloc[-1]) / (upper_band.iloc[-1] - lower_band.iloc[-1]))
        }

    @staticmethod
    def _calculate_volume_trend(history: pd.DataFrame) -> str:
        """Determine volume trend"""
        recent_volume = history['Volume'].tail(5).mean()
        avg_volume = history['Volume'].mean()

        if recent_volume > avg_volume * 1.5:
            return 'high'
        elif recent_volume < avg_volume * 0.5:
            return 'low'
        return 'normal'

    @staticmethod
    def _calculate_volume_trend_series(volumes: pd.Series) -> str:
        """Determine volume trend from pandas Series"""
        if len(volumes) < 5:
            return 'normal'

        recent_volume = volumes.tail(5).mean()
        avg_volume = volumes.mean()

        if recent_volume > avg_volume * 1.5:
            return 'high'
        elif recent_volume < avg_volume * 0.5:
            return 'low'
        return 'normal'

    @staticmethod
    def get_fundamental_analysis(ticker: str) -> Optional[Dict[str, Any]]:
        """Perform fundamental analysis"""
        try:
            info = StockService.get_stock_info(ticker)
            if not info:
                return None

            # Calculate fundamental scores
            pe_ratio = info.get('pe_ratio', 0)
            peg_ratio = info.get('peg_ratio', 0)
            price_to_book = info.get('price_to_book', 0)
            debt_to_equity = info.get('debt_to_equity', 0)
            current_ratio = info.get('current_ratio', 0)
            profit_margin = info.get('profit_margin', 0)
            roe = info.get('return_on_equity', 0)

            # Score calculation (0-100)
            scores = {
                'value_score': StockService._calculate_value_score(pe_ratio, peg_ratio, price_to_book),
                'financial_health_score': StockService._calculate_financial_health_score(debt_to_equity, current_ratio),
                'profitability_score': StockService._calculate_profitability_score(profit_margin, roe),
                'growth_score': StockService._calculate_growth_score(peg_ratio, info)
            }

            overall_score = sum(scores.values()) / len(scores)

            return {
                'ticker': ticker.upper(),
                'scores': scores,
                'overall_score': round(overall_score, 2),
                'recommendation': StockService._get_recommendation(overall_score),
                'metrics': {
                    'pe_ratio': pe_ratio,
                    'peg_ratio': peg_ratio,
                    'price_to_book': price_to_book,
                    'debt_to_equity': debt_to_equity,
                    'current_ratio': current_ratio,
                    'profit_margin': profit_margin,
                    'return_on_equity': roe
                }
            }

        except Exception as e:
            logger.error(f"Error performing fundamental analysis for {ticker}: {str(e)}")
            return None

    @staticmethod
    def _calculate_value_score(pe_ratio: float, peg_ratio: float, price_to_book: float) -> float:
        """Calculate value score based on valuation metrics"""
        score = 50  # Base score

        # PE Ratio scoring
        if pe_ratio > 0:
            if pe_ratio < 15:
                score += 20
            elif pe_ratio < 25:
                score += 10
            elif pe_ratio > 35:
                score -= 10

        # PEG Ratio scoring
        if peg_ratio > 0:
            if peg_ratio < 1:
                score += 20
            elif peg_ratio < 1.5:
                score += 10
            elif peg_ratio > 2:
                score -= 10

        # Price to Book scoring
        if price_to_book > 0:
            if price_to_book < 1:
                score += 10
            elif price_to_book > 3:
                score -= 5

        return max(0, min(100, score))

    @staticmethod
    def _calculate_financial_health_score(debt_to_equity: float, current_ratio: float) -> float:
        """Calculate financial health score"""
        score = 50

        if debt_to_equity >= 0:
            if debt_to_equity < 0.5:
                score += 25
            elif debt_to_equity < 1:
                score += 10
            elif debt_to_equity > 2:
                score -= 20

        if current_ratio > 0:
            if current_ratio > 2:
                score += 25
            elif current_ratio > 1:
                score += 10
            elif current_ratio < 1:
                score -= 20

        return max(0, min(100, score))

    @staticmethod
    def _calculate_profitability_score(profit_margin: float, roe: float) -> float:
        """Calculate profitability score"""
        score = 50

        if profit_margin > 0:
            if profit_margin > 0.2:
                score += 25
            elif profit_margin > 0.1:
                score += 10
            elif profit_margin < 0:
                score -= 30

        if roe > 0:
            if roe > 0.15:
                score += 25
            elif roe > 0.1:
                score += 10
            elif roe < 0:
                score -= 20

        return max(0, min(100, score))

    @staticmethod
    def _calculate_growth_score(peg_ratio: float, info: Dict) -> float:
        """Calculate growth score"""
        score = 50

        if peg_ratio > 0 and peg_ratio < 1:
            score += 30
        elif peg_ratio > 0 and peg_ratio < 1.5:
            score += 15

        # Additional growth metrics could be added here

        return max(0, min(100, score))

    @staticmethod
    def _get_recommendation(score: float) -> str:
        """Get investment recommendation based on score"""
        if score >= 75:
            return "Strong Buy"
        elif score >= 60:
            return "Buy"
        elif score >= 40:
            return "Hold"
        elif score >= 25:
            return "Sell"
        else:
            return "Strong Sell"

    @staticmethod
    def get_analyst_ratings(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get analyst ratings from Finnhub
        Endpoint: https://finnhub.io/api/v1/stock/recommendation
        Returns last quarter's ratings aggregated
        """
        api_key = os.getenv('FINNHUB_API_KEY')
        if not api_key:
            logger.warning("Finnhub API key not configured")
            return None
        
        try:
            url = "https://finnhub.io/api/v1/stock/recommendation"
            params = {'symbol': ticker.upper(), 'token': api_key}
            response = requests.get(url, params=params, timeout=10)
            
            # Handle rate limit or forbidden
            if response.status_code == 403:
                logger.warning(f"Finnhub API access forbidden for analyst ratings (rate limit or invalid API key): {ticker}")
                return None
            elif response.status_code == 429:
                logger.warning(f"Finnhub API rate limit exceeded for analyst ratings: {ticker}")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            if not data or len(data) == 0:
                logger.info(f"No analyst ratings available for {ticker}")
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
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error getting analyst ratings for {ticker}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting analyst ratings for {ticker}: {str(e)}")
            return None

    @staticmethod
    def get_price_target(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get analyst price targets from Finnhub
        Endpoint: https://finnhub.io/api/v1/stock/price-target
        """
        api_key = os.getenv('FINNHUB_API_KEY')
        if not api_key:
            logger.warning("Finnhub API key not configured")
            return None
        
        try:
            url = "https://finnhub.io/api/v1/stock/price-target"
            params = {'symbol': ticker.upper(), 'token': api_key}
            response = requests.get(url, params=params, timeout=10)
            
            # Handle rate limit or forbidden
            if response.status_code == 403:
                logger.warning(f"Finnhub API access forbidden for price target (rate limit or invalid API key): {ticker}")
                return None
            elif response.status_code == 429:
                logger.warning(f"Finnhub API rate limit exceeded for price target: {ticker}")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            if not data or 'targetMean' not in data:
                logger.info(f"No price target available for {ticker}")
                return None
            
            return {
                'target_high': data.get('targetHigh'),
                'target_low': data.get('targetLow'),
                'target_mean': data.get('targetMean'),
                'target_median': data.get('targetMedian'),
                'last_updated': data.get('lastUpdated'),
                'number_analysts': data.get('numberOfAnalysts', 0)
            }
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error getting price target for {ticker}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting price target for {ticker}: {str(e)}")
            return None

    @staticmethod
    def get_insider_transactions(ticker: str, days_back: int = 180) -> Optional[Dict[str, Any]]:
        """
        Get insider transactions from Finnhub (last 6 months)
        Endpoint: https://finnhub.io/api/v1/stock/insider-transactions
        """
        api_key = os.getenv('FINNHUB_API_KEY')
        if not api_key:
            logger.warning("Finnhub API key not configured")
            return None
        
        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            url = "https://finnhub.io/api/v1/stock/insider-transactions"
            params = {
                'symbol': ticker.upper(),
                'from': from_date,
                'token': api_key
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data or 'data' not in data:
                logger.info(f"No insider transactions available for {ticker}")
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
                    if 'transactionPrice' in tx and tx['transactionPrice']:
                        total_value_bought += shares * tx['transactionPrice']
                elif change < 0:  # Sell
                    total_shares_sold += abs(shares)
                    if 'transactionPrice' in tx and tx['transactionPrice']:
                        total_value_sold += abs(shares) * tx['transactionPrice']
                
                transaction_count += 1
            
            net_shares = total_shares_bought - total_shares_sold
            net_value = total_value_bought - total_value_sold
            
            # Determine signal
            if net_value > 50000:  # Net buying > $50k
                signal = 'bullish'
            elif net_value < -50000:  # Net selling > $50k
                signal = 'bearish'
            else:
                signal = 'neutral'
            
            return {
                'shares_bought': total_shares_bought,
                'shares_sold': total_shares_sold,
                'net_shares': net_shares,
                'value_bought': total_value_bought,
                'value_sold': total_value_sold,
                'net_value': net_value,
                'transaction_count': transaction_count,
                'period_days': days_back,
                'signal': signal
            }
        except Exception as e:
            logger.error(f"Error getting insider transactions for {ticker}: {str(e)}")
            return None