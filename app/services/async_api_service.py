"""
Async API Service for parallel stock data fetching
Uses asyncio + aiohttp for non-blocking I/O
"""

import asyncio
import aiohttp
import os
import logging
from typing import List, Dict, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class AsyncAPIService:
    """Async API service for parallel data fetching"""

    def __init__(self):
        self.finnhub_key = os.environ.get('FINNHUB_API_KEY')
        self.alpha_vantage_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
        self.twelve_data_key = os.environ.get('TWELVE_DATA_API_KEY')

    async def fetch_multiple_quotes(self, tickers: List[str]) -> Dict[str, dict]:
        """
        Fetch quotes for multiple tickers in parallel

        Args:
            tickers: List of ticker symbols

        Returns:
            Dict mapping ticker to quote data
        """
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch_single_quote(session, ticker)
                for ticker in tickers
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Build result dict, filter out exceptions
            quote_data = {}
            for ticker, result in zip(tickers, results):
                if not isinstance(result, Exception) and result:
                    quote_data[ticker] = result
                else:
                    logger.warning(f"Failed to fetch quote for {ticker}: {result}")

            return quote_data

    async def _fetch_single_quote(self, session: aiohttp.ClientSession, ticker: str) -> Optional[dict]:
        """Fetch quote from Finnhub API"""
        if not self.finnhub_key:
            return None

        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={self.finnhub_key}"

        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'current_price': data.get('c'),
                        'high': data.get('h'),
                        'low': data.get('l'),
                        'open': data.get('o'),
                        'previous_close': data.get('pc'),
                        'change': data.get('d'),
                        'change_percent': data.get('dp'),
                        'source': 'finnhub'
                    }
                else:
                    logger.warning(f"Finnhub API error for {ticker}: {response.status}")
                    return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching quote for {ticker}")
            return None
        except Exception as e:
            logger.error(f"Error fetching quote for {ticker}: {e}")
            return None

    async def fetch_batch_fundamentals(self, tickers: List[str]) -> Dict[str, dict]:
        """
        Fetch fundamental data for multiple tickers in parallel

        Args:
            tickers: List of ticker symbols

        Returns:
            Dict mapping ticker to fundamental data
        """
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch_company_profile(session, ticker)
                for ticker in tickers
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            fundamentals = {}
            for ticker, result in zip(tickers, results):
                if not isinstance(result, Exception) and result:
                    fundamentals[ticker] = result

            return fundamentals

    async def _fetch_company_profile(self, session: aiohttp.ClientSession, ticker: str) -> Optional[dict]:
        """Fetch company profile from Finnhub"""
        if not self.finnhub_key:
            return None

        url = f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker}&token={self.finnhub_key}"

        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"Error fetching profile for {ticker}: {e}")
            return None

    async def fetch_portfolio_quotes(self, portfolio_items: List[dict]) -> Dict[str, dict]:
        """
        Fetch current quotes for all portfolio items in parallel

        Args:
            portfolio_items: List of portfolio items with 'ticker' field

        Returns:
            Dict mapping ticker to current quote
        """
        tickers = [item['ticker'] for item in portfolio_items if item.get('ticker')]
        return await self.fetch_multiple_quotes(list(set(tickers)))  # Remove duplicates


# Helper decorator for Flask routes
def async_route(f):
    """
    Decorator to run async functions in Flask routes

    Usage:
        @stock_bp.route('/batch-quotes', methods=['POST'])
        @async_route
        async def batch_quotes():
            data = await AsyncAPIService().fetch_multiple_quotes(['AAPL', 'MSFT'])
            return jsonify(data)
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return wrapper


# Synchronous wrapper for compatibility
class AsyncAPIServiceSync:
    """Synchronous wrapper for AsyncAPIService"""

    def __init__(self):
        self.async_service = AsyncAPIService()

    def fetch_multiple_quotes_sync(self, tickers: List[str]) -> Dict[str, dict]:
        """Synchronous wrapper for fetch_multiple_quotes"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.async_service.fetch_multiple_quotes(tickers)
            )
        finally:
            loop.close()

    def fetch_batch_fundamentals_sync(self, tickers: List[str]) -> Dict[str, dict]:
        """Synchronous wrapper for fetch_batch_fundamentals"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.async_service.fetch_batch_fundamentals(tickers)
            )
        finally:
            loop.close()
