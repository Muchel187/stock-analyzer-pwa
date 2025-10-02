"""
Short Data Service - Fetches short interest data from ChartExchange
"""
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timezone
from typing import Dict, Optional
import re

logger = logging.getLogger(__name__)

class ShortDataService:
    """Service for fetching short interest data from ChartExchange"""

    BASE_URL = "https://chartexchange.com/symbol"

    @classmethod
    def get_short_data(cls, ticker: str) -> Optional[Dict]:
        """
        Fetch short interest data from ChartExchange

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dict with short interest data or None if failed
        """
        try:
            # ChartExchange uses format: /nyse-AAPL or /nasdaq-AAPL
            # We'll try both exchanges
            exchanges = ['nyse', 'nasdaq']

            for exchange in exchanges:
                url = f"{cls.BASE_URL}/{exchange}-{ticker.upper()}"

                logger.info(f"Fetching short data from ChartExchange: {url}")

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    # Parse the HTML response
                    data = cls._parse_chartexchange_data(response.text, ticker)
                    if data:
                        logger.info(f"Successfully fetched short data for {ticker}")
                        return data

            logger.warning(f"Could not find short data for {ticker} on ChartExchange")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching short data for {ticker}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching short data for {ticker}: {str(e)}")
            return None

    @classmethod
    def _parse_chartexchange_data(cls, html_content: str, ticker: str) -> Optional[Dict]:
        """
        Parse ChartExchange HTML to extract short interest data

        Args:
            html_content: HTML content from ChartExchange
            ticker: Stock ticker for reference

        Returns:
            Dict with parsed data or None if parsing failed
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Initialize data dictionary
            data = {
                'ticker': ticker.upper(),
                'short_interest': None,
                'short_interest_ratio': None,
                'days_to_cover': None,
                'short_percent_of_float': None,
                'failure_to_deliver': None,
                'last_updated': None,
                'source': 'ChartExchange'
            }

            # Look for short interest data in various formats
            # ChartExchange typically displays data in tables or data cards

            # Try to find short interest percentage
            short_interest_elements = soup.find_all(text=re.compile(r'Short\s+Interest|Short\s+%', re.I))
            for element in short_interest_elements:
                parent = element.parent
                if parent:
                    # Look for percentage value nearby
                    text = parent.get_text()
                    match = re.search(r'(\d+(?:\.\d+)?)\s*%', text)
                    if match:
                        data['short_percent_of_float'] = float(match.group(1))
                        break

            # Try to find days to cover
            days_to_cover_elements = soup.find_all(text=re.compile(r'Days\s+to\s+Cover', re.I))
            for element in days_to_cover_elements:
                parent = element.parent
                if parent:
                    text = parent.get_text()
                    match = re.search(r'(\d+(?:\.\d+)?)', text)
                    if match:
                        data['days_to_cover'] = float(match.group(1))
                        break

            # Try to find short interest shares
            shares_short_elements = soup.find_all(text=re.compile(r'Shares\s+Short|Short\s+Shares', re.I))
            for element in shares_short_elements:
                parent = element.parent
                if parent:
                    text = parent.get_text()
                    # Look for numbers with M (millions) or K (thousands)
                    match = re.search(r'(\d+(?:\.\d+)?)\s*([MK])?', text)
                    if match:
                        value = float(match.group(1))
                        if match.group(2) == 'M':
                            value *= 1_000_000
                        elif match.group(2) == 'K':
                            value *= 1_000
                        data['short_interest'] = int(value)
                        break

            # Try to find failure to deliver
            ftd_elements = soup.find_all(text=re.compile(r'Failure\s+to\s+Deliver|FTD', re.I))
            for element in ftd_elements:
                parent = element.parent
                if parent:
                    text = parent.get_text()
                    match = re.search(r'(\d+(?:,\d+)*)', text)
                    if match:
                        # Remove commas and convert to int
                        ftd_value = int(match.group(1).replace(',', ''))
                        data['failure_to_deliver'] = ftd_value
                        break

            # Set last updated time
            data['last_updated'] = datetime.now(timezone.utc).isoformat()

            # Return data only if we found at least some short information
            if (data['short_percent_of_float'] is not None or
                data['days_to_cover'] is not None or
                data['short_interest'] is not None):
                return data

            return None

        except Exception as e:
            logger.error(f"Error parsing ChartExchange data: {str(e)}")
            return None

    @classmethod
    def calculate_squeeze_score(cls, short_data: Dict) -> Dict:
        """
        Calculate short squeeze potential score based on short data

        Args:
            short_data: Dictionary containing short interest data

        Returns:
            Dict with squeeze score and analysis
        """
        try:
            score = 0
            factors = []

            # Short interest percentage (0-40 points)
            if short_data.get('short_percent_of_float'):
                short_pct = short_data['short_percent_of_float']
                if short_pct >= 25:
                    score += 40
                    factors.append(f"Very high short interest: {short_pct:.1f}%")
                elif short_pct >= 20:
                    score += 35
                    factors.append(f"High short interest: {short_pct:.1f}%")
                elif short_pct >= 15:
                    score += 25
                    factors.append(f"Elevated short interest: {short_pct:.1f}%")
                elif short_pct >= 10:
                    score += 15
                    factors.append(f"Moderate short interest: {short_pct:.1f}%")
                else:
                    score += 5
                    factors.append(f"Low short interest: {short_pct:.1f}%")

            # Days to cover (0-30 points)
            if short_data.get('days_to_cover'):
                dtc = short_data['days_to_cover']
                if dtc >= 10:
                    score += 30
                    factors.append(f"Very high days to cover: {dtc:.1f} days")
                elif dtc >= 7:
                    score += 25
                    factors.append(f"High days to cover: {dtc:.1f} days")
                elif dtc >= 5:
                    score += 20
                    factors.append(f"Elevated days to cover: {dtc:.1f} days")
                elif dtc >= 3:
                    score += 10
                    factors.append(f"Moderate days to cover: {dtc:.1f} days")
                else:
                    score += 5
                    factors.append(f"Low days to cover: {dtc:.1f} days")

            # Failure to deliver (0-30 points)
            if short_data.get('failure_to_deliver'):
                ftd = short_data['failure_to_deliver']
                if ftd >= 1_000_000:
                    score += 30
                    factors.append(f"Very high FTDs: {ftd:,}")
                elif ftd >= 500_000:
                    score += 20
                    factors.append(f"High FTDs: {ftd:,}")
                elif ftd >= 100_000:
                    score += 10
                    factors.append(f"Moderate FTDs: {ftd:,}")
                else:
                    score += 5
                    factors.append(f"Low FTDs: {ftd:,}")

            # Determine squeeze level
            if score >= 80:
                level = "EXTREME"
                description = "Extremely high short squeeze potential"
            elif score >= 60:
                level = "HIGH"
                description = "High short squeeze potential"
            elif score >= 40:
                level = "MODERATE"
                description = "Moderate short squeeze potential"
            elif score >= 20:
                level = "LOW"
                description = "Low short squeeze potential"
            else:
                level = "MINIMAL"
                description = "Minimal short squeeze potential"

            return {
                'score': score,
                'level': level,
                'description': description,
                'factors': factors,
                'data': short_data
            }

        except Exception as e:
            logger.error(f"Error calculating squeeze score: {str(e)}")
            return {
                'score': 0,
                'level': "UNKNOWN",
                'description': "Unable to calculate squeeze potential",
                'factors': [],
                'data': short_data
            }