"""
Unit tests for News Service
"""
import pytest
from datetime import datetime
from app.services.news_service import NewsService


class TestNewsService:
    """Test NewsService functionality"""
    
    def test_calculate_sentiment_score_all_bullish(self):
        """Test sentiment score calculation with all bullish articles"""
        articles = [
            {'sentiment': 'bullish'},
            {'sentiment': 'bullish'},
            {'sentiment': 'bullish'}
        ]
        score = NewsService.calculate_sentiment_score(articles)
        assert score == 1.0
    
    def test_calculate_sentiment_score_all_bearish(self):
        """Test sentiment score calculation with all bearish articles"""
        articles = [
            {'sentiment': 'bearish'},
            {'sentiment': 'bearish'},
            {'sentiment': 'bearish'}
        ]
        score = NewsService.calculate_sentiment_score(articles)
        assert score == -1.0
    
    def test_calculate_sentiment_score_mixed(self):
        """Test sentiment score calculation with mixed articles"""
        articles = [
            {'sentiment': 'bullish'},
            {'sentiment': 'neutral'},
            {'sentiment': 'bearish'}
        ]
        score = NewsService.calculate_sentiment_score(articles)
        assert score == 0.0
    
    def test_calculate_sentiment_score_empty(self):
        """Test sentiment score with empty articles"""
        articles = []
        score = NewsService.calculate_sentiment_score(articles)
        assert score == 0.0
    
    def test_categorize_news_earnings(self):
        """Test news categorization for earnings"""
        articles = [
            {
                'headline': 'Company reports earnings beat',
                'summary': 'Quarterly revenue exceeds expectations'
            }
        ]
        categories = NewsService.categorize_news(articles)
        assert categories['earnings'] == 1
        assert categories['general'] == 0
    
    def test_categorize_news_merger(self):
        """Test news categorization for mergers"""
        articles = [
            {
                'headline': 'Company announces acquisition',
                'summary': 'Major merger deal completed'
            }
        ]
        categories = NewsService.categorize_news(articles)
        assert categories['merger_acquisition'] == 1
        assert categories['general'] == 0
    
    def test_categorize_news_product(self):
        """Test news categorization for product news"""
        articles = [
            {
                'headline': 'Company unveils new product',
                'summary': 'New product launch announced'
            }
        ]
        categories = NewsService.categorize_news(articles)
        assert categories['product'] == 1
        assert categories['general'] == 0
    
    def test_categorize_news_regulatory(self):
        """Test news categorization for regulatory news"""
        articles = [
            {
                'headline': 'Company faces sec lawsuit',
                'summary': 'Investigation leads to regulatory fine'
            }
        ]
        categories = NewsService.categorize_news(articles)
        # Test that it's correctly categorized (regulatory or general)
        assert categories['regulatory'] + categories['general'] >= 1
        assert categories['general'] == 0
    
    def test_categorize_news_general(self):
        """Test news categorization for general news"""
        articles = [
            {
                'headline': 'Company news update',
                'summary': 'General business update'
            }
        ]
        categories = NewsService.categorize_news(articles)
        assert categories['general'] == 1
    
    def test_extract_sentiment_finnhub_bullish(self):
        """Test sentiment extraction with bullish keywords"""
        article = {
            'headline': 'Stock surge on strong earnings beat',
            'summary': 'Company reports profit growth and rise in revenue'
        }
        sentiment = NewsService._extract_sentiment_finnhub(article)
        assert sentiment == 'bullish'
    
    def test_extract_sentiment_finnhub_bearish(self):
        """Test sentiment extraction with bearish keywords"""
        article = {
            'headline': 'Stock falls on weak earnings miss',
            'summary': 'Company reports loss and decline in revenue'
        }
        sentiment = NewsService._extract_sentiment_finnhub(article)
        assert sentiment == 'bearish'
    
    def test_extract_sentiment_finnhub_neutral(self):
        """Test sentiment extraction with neutral keywords"""
        article = {
            'headline': 'Company announces quarterly report',
            'summary': 'Regular business update provided'
        }
        sentiment = NewsService._extract_sentiment_finnhub(article)
        assert sentiment == 'neutral'
    
    def test_map_av_sentiment_bullish(self):
        """Test Alpha Vantage sentiment mapping for bullish"""
        sentiment = NewsService._map_av_sentiment(0.5)
        assert sentiment == 'bullish'
    
    def test_map_av_sentiment_bearish(self):
        """Test Alpha Vantage sentiment mapping for bearish"""
        sentiment = NewsService._map_av_sentiment(-0.5)
        assert sentiment == 'bearish'
    
    def test_map_av_sentiment_neutral(self):
        """Test Alpha Vantage sentiment mapping for neutral"""
        sentiment = NewsService._map_av_sentiment(0.1)
        assert sentiment == 'neutral'
    
    def test_map_av_sentiment_none(self):
        """Test Alpha Vantage sentiment mapping with None"""
        sentiment = NewsService._map_av_sentiment(None)
        assert sentiment == 'neutral'


class TestNewsServiceIntegration:
    """Integration tests for NewsService (requires API keys)"""
    
    @pytest.mark.skipif(
        not NewsService.FINNHUB_API_KEY and not NewsService.ALPHA_VANTAGE_API_KEY,
        reason="No API keys configured"
    )
    def test_get_company_news_structure(self):
        """Test that company news returns correct structure"""
        news = NewsService.get_company_news('AAPL', days=1, limit=5)
        
        if news:  # Only if API call succeeds
            assert 'news' in news
            assert 'sentiment_score' in news
            assert 'news_count' in news
            assert 'categories' in news
            assert 'ticker' in news
            assert 'timestamp' in news
            
            assert isinstance(news['news'], list)
            assert isinstance(news['sentiment_score'], (int, float))
            assert isinstance(news['news_count'], int)
            assert isinstance(news['categories'], dict)
            
            if len(news['news']) > 0:
                article = news['news'][0]
                assert 'headline' in article
                assert 'sentiment' in article
                assert article['sentiment'] in ['bullish', 'neutral', 'bearish']
    
    @pytest.mark.skipif(
        not NewsService.FINNHUB_API_KEY,
        reason="Finnhub API key not configured"
    )
    def test_get_market_news_structure(self):
        """Test that market news returns correct structure"""
        news = NewsService.get_market_news(limit=5)
        
        if news:  # Only if API call succeeds
            assert 'news' in news
            assert 'news_count' in news
            assert 'timestamp' in news
            
            assert isinstance(news['news'], list)
            assert isinstance(news['news_count'], int)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
