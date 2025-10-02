"""
Alternative data sources for stock information when Yahoo Finance is unavailable
"""
import requests
import os
import logging
from typing import Dict, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


# German Stock Ticker Mapping for Finnhub
# Finnhub uses XETRA:TICKER format for German stocks
GERMAN_TICKER_MAP = {
    # DAX 40 stocks - mapping from .DE format to XETRA format
    'SAP.DE': 'XETRA:SAP',
    'SIE.DE': 'XETRA:SIE',
    'BMW.DE': 'XETRA:BMW',
    'BAS.DE': 'XETRA:BAS',
    'DAI.DE': 'XETRA:DAI',
    'ALV.DE': 'XETRA:ALV',
    'BAYN.DE': 'XETRA:BAYN',
    'ADS.DE': 'XETRA:ADS',
    'DBK.DE': 'XETRA:DBK',
    'DTE.DE': 'XETRA:DTE',
    'ADS.DE': 'XETRA:ADS',
    'AIR.DE': 'XETRA:AIR',
    'BEI.DE': 'XETRA:BEI',
    'CON.DE': 'XETRA:CON',
    'DHL.DE': 'XETRA:DHL',
    'EOAN.DE': 'XETRA:EOAN',
    'FRE.DE': 'XETRA:FRE',
    'HEI.DE': 'XETRA:HEI',
    'HEN3.DE': 'XETRA:HEN3',
    'IFX.DE': 'XETRA:IFX',
    'LIN.DE': 'XETRA:LIN',
    'MRK.DE': 'XETRA:MRK',
    'MTX.DE': 'XETRA:MTX',
    'MUV2.DE': 'XETRA:MUV2',
    'PAH3.DE': 'XETRA:PAH3',
    'PUM.DE': 'XETRA:PUM',
    'RWE.DE': 'XETRA:RWE',
    'SY1.DE': 'XETRA:SY1',
    'VOW3.DE': 'XETRA:VOW3',
    'VNA.DE': 'XETRA:VNA',
    'ZAL.DE': 'XETRA:ZAL',
    # MDAX stocks
    'AFX.DE': 'XETRA:AFX',
    'BC8.DE': 'XETRA:BC8',
    'COP.DE': 'XETRA:COP',
    'EVD.DE': 'XETRA:EVD',
    'EVK.DE': 'XETRA:EVK',
    'FIE.DE': 'XETRA:FIE',
    'FME.DE': 'XETRA:FME',
    'FPE.DE': 'XETRA:FPE',
    'FRA.DE': 'XETRA:FRA',
    'G1A.DE': 'XETRA:G1A',
    'GXI.DE': 'XETRA:GXI',
    'HNR1.DE': 'XETRA:HNR1',
    'HOT.DE': 'XETRA:HOT',
    'JUN3.DE': 'XETRA:JUN3',
    'KGX.DE': 'XETRA:KGX',
    'LEG.DE': 'XETRA:LEG',
    'NDA.DE': 'XETRA:NDA',
    'O2D.DE': 'XETRA:O2D',
    'OSR.DE': 'XETRA:OSR',
    'PFV.DE': 'XETRA:PFV',
    'PSM.DE': 'XETRA:PSM',
    'RAA.DE': 'XETRA:RAA',
    'RHK.DE': 'XETRA:RHK',
    'SAX.DE': 'XETRA:SAX',
    'SDF.DE': 'XETRA:SDF',
    'SHL.DE': 'XETRA:SHL',
    'SIX2.DE': 'XETRA:SIX2',
    'SRT.DE': 'XETRA:SRT',
    'TKA.DE': 'XETRA:TKA',
    'TLX.DE': 'XETRA:TLX',
}


def convert_ticker_for_api(ticker: str, api_name: str) -> Tuple[str, str]:
    """
    Convert ticker to API-specific format

    Args:
        ticker: Original ticker (e.g., 'SAP.DE', 'AAPL')
        api_name: API name ('finnhub', 'twelve_data', 'alpha_vantage')

    Returns:
        Tuple of (converted_ticker, original_ticker)

    Examples:
        convert_ticker_for_api('SAP.DE', 'finnhub') -> ('XETRA:SAP', 'SAP.DE')
        convert_ticker_for_api('AAPL', 'finnhub') -> ('AAPL', 'AAPL')
    """
    original_ticker = ticker

    # Finnhub uses XETRA:TICKER format for German stocks
    if api_name == 'finnhub' and ticker.endswith('.DE'):
        converted = GERMAN_TICKER_MAP.get(ticker, ticker)
        logger.debug(f"Converting ticker {ticker} to {converted} for Finnhub")
        return converted, original_ticker

    # Twelve Data and Alpha Vantage use .DE format
    # No conversion needed
    return ticker, original_ticker


class AlphaVantageService:
    """Alpha Vantage API service (free tier: 25 requests/day)"""

    BASE_URL = "https://www.alphavantage.co/query"

    @staticmethod
    def get_time_series_daily(ticker: str, outputsize: str = "compact") -> Optional[Dict[str, Any]]:
        """Get daily time series data from Alpha Vantage"""
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if not api_key:
            logger.warning("Alpha Vantage API key not configured")
            return None

        try:
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': ticker.upper(),
                'outputsize': outputsize,  # 'compact' = 100 days, 'full' = 20+ years
                'apikey': api_key
            }

            response = requests.get(AlphaVantageService.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'Time Series (Daily)' not in data:
                logger.warning(f"No time series data from Alpha Vantage for {ticker}")
                if 'Note' in data:
                    logger.warning(f"Alpha Vantage note: {data['Note']}")
                return None

            time_series = data['Time Series (Daily)']

            # Transform to our standard format
            history_data = []
            for date_str in sorted(time_series.keys()):  # Sort to get chronological order
                day_data = time_series[date_str]
                history_data.append({
                    'date': date_str,
                    'open': float(day_data.get('1. open', 0)),
                    'high': float(day_data.get('2. high', 0)),
                    'low': float(day_data.get('3. low', 0)),
                    'close': float(day_data.get('4. close', 0)),
                    'volume': int(day_data.get('5. volume', 0))
                })

            return {
                'ticker': ticker.upper(),
                'data': history_data,
                'source': 'alpha_vantage'
            }

        except Exception as e:
            logger.error(f"Alpha Vantage time series error for {ticker}: {str(e)}")
            return None

    @staticmethod
    def get_stock_quote(ticker: str) -> Optional[Dict[str, Any]]:
        """Get real-time stock quote from Alpha Vantage"""
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if not api_key:
            logger.warning("Alpha Vantage API key not configured")
            return None

        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': ticker,
                'apikey': api_key
            }

            response = requests.get(AlphaVantageService.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'Global Quote' not in data or not data['Global Quote']:
                logger.warning(f"No data returned from Alpha Vantage for {ticker}")
                return None

            quote = data['Global Quote']

            # Transform to our standard format
            return {
                'ticker': ticker.upper(),
                'current_price': float(quote.get('05. price', 0)),
                'previous_close': float(quote.get('08. previous close', 0)),
                'open': float(quote.get('02. open', 0)),
                'day_high': float(quote.get('03. high', 0)),
                'day_low': float(quote.get('04. low', 0)),
                'volume': int(quote.get('06. volume', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': quote.get('10. change percent', '0%').replace('%', ''),
                'source': 'alpha_vantage'
            }

        except Exception as e:
            logger.error(f"Alpha Vantage error for {ticker}: {str(e)}")
            return None

    @staticmethod
    def get_company_overview(ticker: str) -> Optional[Dict[str, Any]]:
        """Get company overview/fundamental data"""
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if not api_key:
            return None

        try:
            params = {
                'function': 'OVERVIEW',
                'symbol': ticker,
                'apikey': api_key
            }

            response = requests.get(AlphaVantageService.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data or 'Symbol' not in data:
                return None

            # Transform to our standard format
            return {
                'ticker': ticker.upper(),
                'company_name': data.get('Name'),
                'sector': data.get('Sector'),
                'industry': data.get('Industry'),
                'description': data.get('Description'),
                'market_cap': float(data.get('MarketCapitalization', 0)) if data.get('MarketCapitalization') else None,
                'pe_ratio': float(data.get('PERatio', 0)) if data.get('PERatio') else None,
                'peg_ratio': float(data.get('PEGRatio', 0)) if data.get('PEGRatio') else None,
                'book_value': float(data.get('BookValue', 0)) if data.get('BookValue') else None,
                'dividend_yield': float(data.get('DividendYield', 0)) if data.get('DividendYield') else None,
                'eps': float(data.get('EPS', 0)) if data.get('EPS') else None,
                'beta': float(data.get('Beta', 0)) if data.get('Beta') else None,
                '52_week_high': float(data.get('52WeekHigh', 0)) if data.get('52WeekHigh') else None,
                '52_week_low': float(data.get('52WeekLow', 0)) if data.get('52WeekLow') else None,
                'moving_avg_50': float(data.get('50DayMovingAverage', 0)) if data.get('50DayMovingAverage') else None,
                'moving_avg_200': float(data.get('200DayMovingAverage', 0)) if data.get('200DayMovingAverage') else None,
                'source': 'alpha_vantage'
            }

        except Exception as e:
            logger.error(f"Alpha Vantage overview error for {ticker}: {str(e)}")
            return None


class FinnhubService:
    """Finnhub API service (free tier: 60 requests/minute)"""

    BASE_URL = "https://finnhub.io/api/v1"

    @staticmethod
    def get_stock_quote(ticker: str) -> Optional[Dict[str, Any]]:
        """Get real-time stock quote from Finnhub with German stock support"""
        api_key = os.getenv('FINNHUB_API_KEY')
        if not api_key:
            logger.warning("Finnhub API key not configured")
            return None

        try:
            # Convert ticker for Finnhub API (German stocks need XETRA: prefix)
            api_ticker, original_ticker = convert_ticker_for_api(ticker, 'finnhub')

            params = {
                'symbol': api_ticker.upper(),
                'token': api_key
            }

            response = requests.get(f"{FinnhubService.BASE_URL}/quote", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data or data.get('c') == 0:
                logger.warning(f"No data returned from Finnhub for {ticker} (API ticker: {api_ticker})")
                return None

            # Return with original ticker format
            return {
                'ticker': original_ticker.upper(),
                'current_price': float(data.get('c', 0)),  # Current price
                'previous_close': float(data.get('pc', 0)),  # Previous close
                'open': float(data.get('o', 0)),  # Open price
                'day_high': float(data.get('h', 0)),  # High price
                'day_low': float(data.get('l', 0)),  # Low price
                'change': float(data.get('d', 0)),  # Change
                'change_percent': float(data.get('dp', 0)),  # Change percent
                'timestamp': datetime.fromtimestamp(data.get('t', 0)).isoformat() if data.get('t') else None,
                'source': 'finnhub'
            }

        except Exception as e:
            logger.error(f"Finnhub error for {ticker}: {str(e)}")
            return None

    @staticmethod
    def get_company_profile(ticker: str) -> Optional[Dict[str, Any]]:
        """Get company profile from Finnhub"""
        api_key = os.getenv('FINNHUB_API_KEY')
        if not api_key:
            return None

        try:
            params = {
                'symbol': ticker.upper(),
                'token': api_key
            }

            response = requests.get(f"{FinnhubService.BASE_URL}/stock/profile2", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data or not data.get('name'):
                return None

            return {
                'ticker': ticker.upper(),
                'company_name': data.get('name'),
                'sector': data.get('finnhubIndustry'),
                'website': data.get('weburl'),
                'exchange': data.get('exchange'),
                'currency': data.get('currency'),
                'market_cap': data.get('marketCapitalization'),
                'shares_outstanding': data.get('shareOutstanding'),
                'logo': data.get('logo'),
                'country': data.get('country'),
                'source': 'finnhub'
            }

        except Exception as e:
            logger.error(f"Finnhub profile error for {ticker}: {str(e)}")
            return None


class TwelveDataService:
    """Twelve Data API service (free tier: 800 requests/day, 8 requests/minute)"""

    BASE_URL = "https://api.twelvedata.com"

    @staticmethod
    def get_time_series(ticker: str, interval: str = "1day", outputsize: int = 30) -> Optional[Dict[str, Any]]:
        """Get historical time series data from Twelve Data"""
        api_key = os.getenv('TWELVE_DATA_API_KEY')
        if not api_key:
            return None

        try:
            params = {
                'symbol': ticker.upper(),
                'interval': interval,
                'outputsize': outputsize,
                'apikey': api_key
            }

            response = requests.get(f"{TwelveDataService.BASE_URL}/time_series", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'values' not in data or not data['values']:
                return None

            # Transform to our standard format
            history_data = []
            for item in reversed(data['values']):  # Reverse to get chronological order
                history_data.append({
                    'date': item.get('datetime'),
                    'open': float(item.get('open', 0)),
                    'high': float(item.get('high', 0)),
                    'low': float(item.get('low', 0)),
                    'close': float(item.get('close', 0)),
                    'volume': int(item.get('volume', 0))
                })

            return {
                'ticker': ticker.upper(),
                'data': history_data,
                'source': 'twelve_data'
            }

        except Exception as e:
            logger.error(f"Twelve Data time series error for {ticker}: {str(e)}")
            return None

    @staticmethod
    def get_stock_quote(ticker: str) -> Optional[Dict[str, Any]]:
        """Get real-time stock quote from Twelve Data"""
        api_key = os.getenv('TWELVE_DATA_API_KEY')
        if not api_key:
            logger.warning("Twelve Data API key not configured")
            return None

        try:
            params = {
                'symbol': ticker.upper(),
                'apikey': api_key
            }

            response = requests.get(f"{TwelveDataService.BASE_URL}/quote", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'price' not in data or data.get('code') == 400:
                logger.warning(f"No data returned from Twelve Data for {ticker}")
                return None

            return {
                'ticker': ticker.upper(),
                'company_name': data.get('name'),
                'current_price': float(data.get('close', 0)),
                'previous_close': float(data.get('previous_close', 0)),
                'open': float(data.get('open', 0)),
                'day_high': float(data.get('high', 0)),
                'day_low': float(data.get('low', 0)),
                'volume': int(data.get('volume', 0)),
                'change': float(data.get('change', 0)),
                'change_percent': float(data.get('percent_change', 0)),
                '52_week_high': float(data.get('fifty_two_week', {}).get('high', 0)) if data.get('fifty_two_week') else None,
                '52_week_low': float(data.get('fifty_two_week', {}).get('low', 0)) if data.get('fifty_two_week') else None,
                'exchange': data.get('exchange'),
                'currency': data.get('currency'),
                'source': 'twelve_data'
            }

        except Exception as e:
            logger.error(f"Twelve Data error for {ticker}: {str(e)}")
            return None


class FallbackDataService:
    """
    Coordinated fallback service that tries multiple data sources in order,
    including AI fallback when all traditional APIs are exhausted

    Priority Order:
    1. Twelve Data (Primary) - Best for real-time data, WebSocket support, 800 req/day
    2. Finnhub (Secondary) - Good fallback, 60 req/min
    3. Alpha Vantage (Tertiary) - Last resort, 25 req/day
    4. AI Fallback (Ultimate) - When all APIs fail
    """

    # Order of preference for data sources (Twelve Data first!)
    SOURCES = [
        ('twelve_data', TwelveDataService),
        ('finnhub', FinnhubService),
        ('alpha_vantage', AlphaVantageService),
    ]

    @staticmethod
    def get_stock_quote(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Try to get stock quote from available fallback sources.
        Returns None if all API sources fail (no AI fallback to avoid rate limits).
        """
        for source_name, service_class in FallbackDataService.SOURCES:
            logger.info(f"Trying {source_name} for {ticker}...")
            try:
                data = service_class.get_stock_quote(ticker)
                if data:
                    logger.info(f"Successfully fetched {ticker} from {source_name}")
                    return data
            except Exception as e:
                logger.warning(f"{source_name} failed for {ticker}: {str(e)}")
                continue

        # No AI fallback here - it causes rate limit issues
        # AI should only be used for explicit analysis requests, not quote fetching
        logger.error(f"All API sources failed for {ticker}")
        return None

    @staticmethod
    def get_company_info(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Try to get company information from available sources with proper fallback.
        Returns None if all API sources fail (no AI fallback to avoid rate limits).
        """

        # Try Finnhub first (60 requests/minute - more reliable)
        if os.getenv('FINNHUB_API_KEY'):
            try:
                logger.info(f"Trying Finnhub for company info: {ticker}")
                data = FinnhubService.get_company_profile(ticker)
                if data:
                    logger.info(f"Successfully fetched company info for {ticker} from Finnhub")
                    return data
            except Exception as e:
                logger.warning(f"Finnhub failed for company info {ticker}: {str(e)}")

        # Try Alpha Vantage as fallback (has best company overview but limited to 25 requests/day)
        if os.getenv('ALPHA_VANTAGE_API_KEY'):
            try:
                logger.info(f"Trying Alpha Vantage for company info: {ticker}")
                data = AlphaVantageService.get_company_overview(ticker)
                if data:
                    logger.info(f"Successfully fetched company info for {ticker} from Alpha Vantage")
                    return data
            except Exception as e:
                logger.warning(f"Alpha Vantage failed for company info {ticker}: {str(e)}")

        # No AI fallback here - it causes rate limit issues
        # AI should only be used for explicit analysis requests
        logger.error(f"All API sources failed for company info {ticker}")
        return None

    @staticmethod
    def get_historical_data(ticker: str, outputsize: int = 30) -> Optional[Dict[str, Any]]:
        """
        Try to get historical price data from available sources with proper fallback.
        Uses AI as ultimate fallback when all APIs fail.
        """

        # Try Twelve Data first (800 requests/day - more reliable)
        if os.getenv('TWELVE_DATA_API_KEY'):
            logger.info(f"Trying Twelve Data for historical data: {ticker}")
            try:
                data = TwelveDataService.get_time_series(ticker, outputsize=outputsize)
                if data:
                    logger.info(f"Successfully fetched historical data for {ticker} from Twelve Data")
                    return data
            except Exception as e:
                logger.warning(f"Twelve Data failed for historical {ticker}: {str(e)}")

        # Try Alpha Vantage as fallback (25 requests/day)
        if os.getenv('ALPHA_VANTAGE_API_KEY'):
            logger.info(f"Trying Alpha Vantage for historical data: {ticker}")
            try:
                # Alpha Vantage uses 'compact' (100 days) or 'full' (20+ years)
                av_outputsize = "full" if outputsize > 100 else "compact"
                data = AlphaVantageService.get_time_series_daily(ticker, outputsize=av_outputsize)
                if data:
                    logger.info(f"Successfully fetched historical data for {ticker} from Alpha Vantage")
                    # Limit to requested outputsize
                    if len(data['data']) > outputsize:
                        data['data'] = data['data'][-outputsize:]
                    return data
            except Exception as e:
                logger.warning(f"Alpha Vantage failed for historical {ticker}: {str(e)}")

        # Try Finnhub as last resort (limited historical data)
        if os.getenv('FINNHUB_API_KEY'):
            logger.info(f"Trying Finnhub for historical data: {ticker}")
            try:
                # Finnhub doesn't have a direct time series endpoint, so we skip it
                logger.info(f"Finnhub doesn't support historical time series, skipping")
            except Exception as e:
                logger.warning(f"Finnhub failed for historical {ticker}: {str(e)}")

        # Ultimate fallback: Use AI for historical data
        logger.warning(f"All API sources failed for historical data {ticker}, attempting AI fallback...")
        try:
            from app.services.ai_service import AIService
            ai_service = AIService()

            # Map outputsize to period
            period_map = {
                30: '1mo', 90: '3mo', 180: '6mo',
                365: '1y', 730: '2y', 1825: '5y'
            }
            period = '1mo'  # default
            for days, p in period_map.items():
                if outputsize <= days:
                    period = p
                    break

            ai_data = ai_service.get_historical_data_from_ai(ticker, period)
            if ai_data and ai_data.get('data'):
                logger.info(f"Successfully retrieved historical data for {ticker} from AI fallback")
                # Convert to standard format
                return {
                    'ticker': ticker.upper(),
                    'data': ai_data['data'],
                    'source': 'AI_FALLBACK'
                }
        except Exception as e:
            logger.error(f"AI fallback failed for historical data {ticker}: {str(e)}")

        logger.warning(f"No fallback source available for historical data: {ticker}")
        return None

    @staticmethod
    def merge_data(quote_data: Dict, company_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Merge quote and company data into comprehensive stock info"""
        result = quote_data.copy()

        if company_data:
            # Merge company data, preferring existing values
            for key, value in company_data.items():
                if key not in result or result[key] is None:
                    result[key] = value

        return result
