"""
Financial Modeling Prep (FMP) Service
Provides access to financial health scores, ratios, dividends, and earnings data
"""

import os
import requests
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FMPService:
    """Service for accessing Financial Modeling Prep API"""

    BASE_URL = "https://financialmodelingprep.com/api"

    @staticmethod
    def _get_api_key() -> Optional[str]:
        """Get FMP API key from environment"""
        api_key = os.getenv('FMP_API_KEY')
        if not api_key:
            logger.warning("FMP_API_KEY not configured")
        return api_key

    @staticmethod
    def _make_request(endpoint: str, params: Dict[str, Any] = None) -> Optional[Any]:
        """
        Make HTTP request to FMP API with error handling

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response data or None on error
        """
        api_key = FMPService._get_api_key()
        if not api_key:
            return None

        if params is None:
            params = {}

        params['apikey'] = api_key

        try:
            url = f"{FMPService.BASE_URL}{endpoint}"
            logger.debug(f"FMP API request: {url}")

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            logger.debug(f"FMP API response received: {len(str(data))} bytes")

            return data

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error("FMP API rate limit exceeded")
            else:
                logger.error(f"FMP API HTTP error {e.response.status_code}: {e}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"FMP API request failed: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error in FMP API request: {e}")
            return None

    @staticmethod
    def get_financial_score(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get Piotroski Score and Altman Z-Score for a stock

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dict with financial scores or None on error

        Example response:
            {
                "symbol": "AAPL",
                "piotroskiScore": 8,
                "altmanZScore": 5.2,
                "profitability": 4,
                "leverage": 2,
                "efficiency": 2
            }
        """
        endpoint = "/v4/score"
        params = {'symbol': ticker.upper()}

        data = FMPService._make_request(endpoint, params)

        if not data or not isinstance(data, list) or len(data) == 0:
            logger.warning(f"No financial score data for {ticker}")
            return None

        # FMP returns list, take first element
        score_data = data[0] if isinstance(data, list) else data

        return {
            'symbol': score_data.get('symbol', ticker.upper()),
            'piotroskiScore': score_data.get('piotroskiScore'),
            'altmanZScore': score_data.get('altmanZScore'),
            'profitability': score_data.get('profitability'),
            'leverage': score_data.get('leverage'),
            'efficiency': score_data.get('efficiency')
        }

    @staticmethod
    def get_financial_ratios(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive financial ratios (TTM - Trailing Twelve Months)

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dict with financial ratios or None on error
        """
        endpoint = f"/v3/ratios-ttm/{ticker.upper()}"

        data = FMPService._make_request(endpoint)

        if not data or not isinstance(data, list) or len(data) == 0:
            logger.warning(f"No financial ratios data for {ticker}")
            return None

        # FMP returns list, take first element
        return data[0] if isinstance(data, list) else data
