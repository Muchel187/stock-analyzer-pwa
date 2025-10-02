"""
News Service for fetching and analyzing stock news
"""
import os
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class NewsService:
    """Service for fetching company news and sentiment analysis"""
    
    FINNHUB_API_KEY = os.environ.get('FINNHUB_API_KEY')
    ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
    
    @staticmethod
    def get_company_news(ticker: str, days: int = 7, limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        Get company-specific news with sentiment
        
        Args:
            ticker: Stock symbol
            days: Days to look back (default: 7)
            limit: Number of articles to return (max: 50)
            
        Returns:
            dict with news articles and sentiment score
        """
        try:
            # Try Finnhub first
            news = NewsService._fetch_finnhub_news(ticker, days)
            
            if not news:
                # Fallback to Alpha Vantage
                news = NewsService._fetch_alphavantage_news(ticker, limit)
            
            if not news:
                return None
            
            # Limit results
            news = news[:limit]
            
            # Calculate overall sentiment
            sentiment_score = NewsService.calculate_sentiment_score(news)
            
            # Categorize news
            categorized = NewsService.categorize_news(news)
            
            return {
                'news': news,
                'sentiment_score': sentiment_score,
                'news_count': len(news),
                'categories': categorized,
                'ticker': ticker.upper(),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {str(e)}")
            return None
    
    @staticmethod
    def _fetch_finnhub_news(ticker: str, days: int) -> Optional[List[Dict]]:
        """Fetch news from Finnhub API"""
        if not NewsService.FINNHUB_API_KEY:
            return None
        
        try:
            # Calculate date range
            to_date = datetime.now().date()
            from_date = to_date - timedelta(days=days)
            
            url = 'https://finnhub.io/api/v1/company-news'
            params = {
                'symbol': ticker.upper(),
                'from': from_date.isoformat(),
                'to': to_date.isoformat(),
                'token': NewsService.FINNHUB_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                articles = response.json()
                
                # Transform to standard format
                formatted = []
                for article in articles:
                    formatted.append({
                        'headline': article.get('headline', ''),
                        'summary': article.get('summary', '')[:200],  # Limit summary
                        'source': article.get('source', 'Unknown'),
                        'url': article.get('url', ''),
                        'image': article.get('image', ''),
                        'datetime': article.get('datetime', 0),
                        'date': datetime.fromtimestamp(article.get('datetime', 0)).isoformat() if article.get('datetime') else '',
                        'sentiment': NewsService._extract_sentiment_finnhub(article)
                    })
                
                return formatted
            
            return None
            
        except Exception as e:
            logger.error(f"Finnhub news error for {ticker}: {str(e)}")
            return None
    
    @staticmethod
    def _fetch_alphavantage_news(ticker: str, limit: int) -> Optional[List[Dict]]:
        """Fetch news from Alpha Vantage News Sentiment API"""
        if not NewsService.ALPHA_VANTAGE_API_KEY:
            return None
        
        try:
            url = 'https://www.alphavantage.co/query'
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': ticker.upper(),
                'limit': limit,
                'apikey': NewsService.ALPHA_VANTAGE_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'feed' not in data:
                    return None
                
                articles = data['feed']
                
                # Transform to standard format
                formatted = []
                for article in articles:
                    # Get ticker-specific sentiment
                    ticker_sentiment = None
                    if 'ticker_sentiment' in article:
                        for ts in article['ticker_sentiment']:
                            if ts.get('ticker', '').upper() == ticker.upper():
                                ticker_sentiment = float(ts.get('ticker_sentiment_score', 0))
                                break
                    
                    formatted.append({
                        'headline': article.get('title', ''),
                        'summary': article.get('summary', '')[:200],
                        'source': article.get('source', 'Unknown'),
                        'url': article.get('url', ''),
                        'image': article.get('banner_image', ''),
                        'datetime': article.get('time_published', ''),
                        'date': article.get('time_published', ''),
                        'sentiment': NewsService._map_av_sentiment(ticker_sentiment)
                    })
                
                return formatted
            
            return None
            
        except Exception as e:
            logger.error(f"Alpha Vantage news error for {ticker}: {str(e)}")
            return None
    
    @staticmethod
    def _extract_sentiment_finnhub(article: Dict) -> str:
        """Extract sentiment from Finnhub article (basic heuristic)"""
        # Finnhub doesn't provide sentiment directly, use simple keyword analysis
        headline = article.get('headline', '').lower()
        summary = article.get('summary', '').lower()
        text = headline + ' ' + summary
        
        positive_words = ['surge', 'jump', 'gain', 'rise', 'beat', 'growth', 'profit', 'success', 'win', 'positive', 'strong', 'bullish']
        negative_words = ['fall', 'drop', 'loss', 'decline', 'miss', 'weak', 'down', 'negative', 'concern', 'risk', 'bearish', 'crash']
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        if pos_count > neg_count:
            return 'bullish'
        elif neg_count > pos_count:
            return 'bearish'
        else:
            return 'neutral'
    
    @staticmethod
    def _map_av_sentiment(score: Optional[float]) -> str:
        """Map Alpha Vantage sentiment score to category"""
        if score is None:
            return 'neutral'
        
        if score > 0.15:
            return 'bullish'
        elif score < -0.15:
            return 'bearish'
        else:
            return 'neutral'
    
    @staticmethod
    def calculate_sentiment_score(articles: List[Dict]) -> float:
        """
        Calculate overall sentiment score from articles
        
        Returns:
            float: -1 (very bearish) to 1 (very bullish)
        """
        if not articles:
            return 0.0
        
        sentiment_values = {
            'bullish': 1.0,
            'neutral': 0.0,
            'bearish': -1.0
        }
        
        total = sum(sentiment_values.get(article.get('sentiment', 'neutral'), 0) for article in articles)
        
        return round(total / len(articles), 2)
    
    @staticmethod
    def categorize_news(articles: List[Dict]) -> Dict[str, int]:
        """
        Categorize news articles by type
        
        Returns:
            dict with category counts
        """
        categories = {
            'earnings': 0,
            'merger_acquisition': 0,
            'product': 0,
            'regulatory': 0,
            'general': 0
        }
        
        for article in articles:
            headline = article.get('headline', '').lower()
            summary = article.get('summary', '').lower()
            text = headline + ' ' + summary
            
            if any(word in text for word in ['earnings', 'revenue', 'profit', 'eps', 'quarterly']):
                categories['earnings'] += 1
            elif any(word in text for word in ['merger', 'acquisition', 'acquire', 'buyout', 'takeover']):
                categories['merger_acquisition'] += 1
            elif any(word in text for word in ['product', 'launch', 'release', 'unveil', 'announce']):
                categories['product'] += 1
            elif any(word in text for word in ['regulatory', 'sec', 'lawsuit', 'investigation', 'fine']):
                categories['regulatory'] += 1
            else:
                categories['general'] += 1
        
        return categories
    
    @staticmethod
    def get_market_news(limit: int = 20) -> Optional[Dict[str, Any]]:
        """
        Get general market news
        
        Args:
            limit: Number of articles
            
        Returns:
            dict with news articles
        """
        if not NewsService.FINNHUB_API_KEY:
            return None
        
        try:
            url = 'https://finnhub.io/api/v1/news'
            params = {
                'category': 'general',
                'token': NewsService.FINNHUB_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                articles = response.json()[:limit]
                
                formatted = []
                for article in articles:
                    formatted.append({
                        'headline': article.get('headline', ''),
                        'summary': article.get('summary', '')[:200],
                        'source': article.get('source', 'Unknown'),
                        'url': article.get('url', ''),
                        'image': article.get('image', ''),
                        'datetime': article.get('datetime', 0),
                        'date': datetime.fromtimestamp(article.get('datetime', 0)).isoformat() if article.get('datetime') else ''
                    })
                
                return {
                    'news': formatted,
                    'news_count': len(formatted),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching market news: {str(e)}")
            return None
