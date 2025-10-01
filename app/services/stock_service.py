import pandas as pd
import numpy as np
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

            # Cache the result
            StockCache.set_cache(ticker, processed_info, 'info')

            return processed_info

        except Exception as e:
            logger.error(f"Error fetching stock info for {ticker}: {str(e)}")
            return None

    @staticmethod
    def get_price_history(ticker: str, period: str = "1y") -> Optional[Dict[str, Any]]:
        """Get historical price data using Alpha Vantage"""
        try:
            # Map period to outputsize (approximate)
            period_map = {
                '1mo': 30,
                '3mo': 90,
                '6mo': 180,
                '1y': 365,
                '2y': 730,
                '5y': 1825
            }
            outputsize = period_map.get(period, 365)

            # Use fallback service for historical data
            fallback_data = FallbackDataService.get_historical_data(ticker, outputsize=outputsize)
            if fallback_data:
                fallback_data['period'] = period
                return fallback_data

            logger.error(f"Failed to get history for {ticker}")
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