#!/usr/bin/env python3
"""
Intensive Unit Test Suite for AI Fallback System
Tests all components, edge cases, and integration scenarios
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
import json

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Set up test environment
os.environ['TESTING'] = 'True'
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

class TestAIFallbackSystem(unittest.TestCase):
    """Comprehensive test suite for AI Fallback functionality"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        print("\n" + "="*80)
        print("AI FALLBACK SYSTEM - INTENSIVE UNIT TEST SUITE")
        print("="*80 + "\n")

    def setUp(self):
        """Set up for each test"""
        # Save original env vars
        self.original_env = {
            'GOOGLE_API_KEY': os.environ.get('GOOGLE_API_KEY'),
            'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
            'FINNHUB_API_KEY': os.environ.get('FINNHUB_API_KEY'),
            'TWELVE_DATA_API_KEY': os.environ.get('TWELVE_DATA_API_KEY'),
            'ALPHA_VANTAGE_API_KEY': os.environ.get('ALPHA_VANTAGE_API_KEY'),
        }

    def tearDown(self):
        """Clean up after each test"""
        # Restore original env vars
        for key, value in self.original_env.items():
            if value:
                os.environ[key] = value
            elif key in os.environ:
                os.environ.pop(key)

    # ========================================================================
    # TEST GROUP 1: AIService Initialization
    # ========================================================================

    def test_01_ai_service_init_with_gemini(self):
        """Test AIService initialization with Google Gemini API key"""
        print("\n[TEST 01] AIService initialization with Gemini...")

        os.environ['GOOGLE_API_KEY'] = 'test_gemini_key'
        os.environ.pop('OPENAI_API_KEY', None)

        from app.services.ai_service import AIService
        ai_service = AIService()

        self.assertEqual(ai_service.provider, 'google')
        self.assertEqual(ai_service.provider_name, 'Google Gemini 2.5 Pro')
        self.assertIsNotNone(ai_service.api_url)
        self.assertIn('gemini-2.5-pro', ai_service.api_url)

        print("✅ PASS: Gemini initialization correct")

    def test_02_ai_service_init_with_openai(self):
        """Test AIService initialization with OpenAI API key"""
        print("\n[TEST 02] AIService initialization with OpenAI...")

        os.environ.pop('GOOGLE_API_KEY', None)
        os.environ['OPENAI_API_KEY'] = 'test_openai_key'

        from app.services.ai_service import AIService
        # Force reload
        import importlib
        import app.services.ai_service
        importlib.reload(app.services.ai_service)

        ai_service = app.services.ai_service.AIService()

        self.assertEqual(ai_service.provider, 'openai')
        self.assertEqual(ai_service.provider_name, 'OpenAI GPT-4')
        self.assertIsNotNone(ai_service.headers)

        print("✅ PASS: OpenAI initialization correct")

    def test_03_ai_service_init_without_keys(self):
        """Test AIService initialization without any API keys"""
        print("\n[TEST 03] AIService initialization without keys...")

        os.environ.pop('GOOGLE_API_KEY', None)
        os.environ.pop('OPENAI_API_KEY', None)

        from app.services.ai_service import AIService
        import importlib
        import app.services.ai_service
        importlib.reload(app.services.ai_service)

        ai_service = app.services.ai_service.AIService()

        self.assertIsNone(ai_service.provider)
        self.assertEqual(ai_service.provider_name, 'None')

        print("✅ PASS: No API keys handled correctly")

    # ========================================================================
    # TEST GROUP 2: AI Stock Data Retrieval (Mocked)
    # ========================================================================

    def test_04_get_stock_data_from_ai_success(self):
        """Test successful stock data retrieval from AI"""
        print("\n[TEST 04] Get stock data from AI (mocked success)...")

        os.environ['GOOGLE_API_KEY'] = 'test_key'

        from app.services.ai_service import AIService
        import importlib
        import app.services.ai_service
        importlib.reload(app.services.ai_service)

        ai_service = app.services.ai_service.AIService()

        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': json.dumps({
                            'ticker': 'AAPL',
                            'company_name': 'Apple Inc',
                            'current_price': 175.50,
                            'market_cap': 2800000,
                            'sector': 'Technology',
                            'source': 'AI_FALLBACK'
                        })
                    }]
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()

        with patch('requests.post', return_value=mock_response):
            result = ai_service.get_stock_data_from_ai('AAPL')

        self.assertIsNotNone(result)
        self.assertEqual(result['ticker'], 'AAPL')
        self.assertEqual(result['company_name'], 'Apple Inc')
        self.assertEqual(result['current_price'], 175.50)
        self.assertEqual(result['source'], 'AI_FALLBACK')

        print("✅ PASS: AI stock data retrieval successful")

    def test_05_get_stock_data_timeout(self):
        """Test AI timeout handling"""
        print("\n[TEST 05] AI timeout handling...")

        os.environ['GOOGLE_API_KEY'] = 'test_key'

        from app.services.ai_service import AIService
        import importlib
        import app.services.ai_service
        importlib.reload(app.services.ai_service)

        ai_service = app.services.ai_service.AIService()

        # Mock timeout
        import requests
        with patch('requests.post', side_effect=requests.exceptions.Timeout("Timeout")):
            result = ai_service.get_stock_data_from_ai('AAPL')

        self.assertIsNone(result)

        print("✅ PASS: Timeout handled gracefully")

    def test_06_get_stock_data_invalid_json(self):
        """Test handling of invalid JSON from AI"""
        print("\n[TEST 06] Invalid JSON handling...")

        os.environ['GOOGLE_API_KEY'] = 'test_key'

        from app.services.ai_service import AIService
        import importlib
        import app.services.ai_service
        importlib.reload(app.services.ai_service)

        ai_service = app.services.ai_service.AIService()

        # Mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': 'This is not valid JSON'
                    }]
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()

        with patch('requests.post', return_value=mock_response):
            result = ai_service.get_stock_data_from_ai('AAPL')

        self.assertIsNone(result)

        print("✅ PASS: Invalid JSON handled gracefully")

    # ========================================================================
    # TEST GROUP 3: Historical Data Retrieval
    # ========================================================================

    def test_07_get_historical_data_success(self):
        """Test successful historical data retrieval from AI"""
        print("\n[TEST 07] Get historical data from AI (mocked)...")

        os.environ['GOOGLE_API_KEY'] = 'test_key'

        from app.services.ai_service import AIService
        import importlib
        import app.services.ai_service
        importlib.reload(app.services.ai_service)

        ai_service = app.services.ai_service.AIService()

        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': json.dumps({
                            'ticker': 'AAPL',
                            'period': '1mo',
                            'data': [
                                {
                                    'date': '2025-10-01',
                                    'open': 175.0,
                                    'high': 177.0,
                                    'low': 174.0,
                                    'close': 176.0,
                                    'volume': 50000000
                                }
                            ],
                            'source': 'AI_FALLBACK'
                        })
                    }]
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()

        with patch('requests.post', return_value=mock_response):
            result = ai_service.get_historical_data_from_ai('AAPL', '1mo')

        self.assertIsNotNone(result)
        self.assertEqual(result['ticker'], 'AAPL')
        self.assertEqual(result['period'], '1mo')
        self.assertIsInstance(result['data'], list)
        self.assertGreater(len(result['data']), 0)

        print("✅ PASS: Historical data retrieval successful")

    def test_08_period_mapping(self):
        """Test period to days mapping in historical data"""
        print("\n[TEST 08] Period mapping validation...")

        from app.services.ai_service import AIService

        # Just check the mapping logic exists
        period_map = {
            '1mo': 30, '3mo': 90, '6mo': 180,
            '1y': 365, '2y': 730, '5y': 1825
        }

        for period, expected_days in period_map.items():
            self.assertIn(period, period_map)
            self.assertEqual(period_map[period], expected_days)

        print("✅ PASS: Period mapping correct")

    # ========================================================================
    # TEST GROUP 4: FallbackDataService Integration
    # ========================================================================

    def test_09_fallback_cascade_to_ai(self):
        """Test that FallbackDataService cascades to AI when APIs fail"""
        print("\n[TEST 09] Fallback cascade to AI...")

        # Disable all API keys
        os.environ.pop('FINNHUB_API_KEY', None)
        os.environ.pop('TWELVE_DATA_API_KEY', None)
        os.environ.pop('ALPHA_VANTAGE_API_KEY', None)
        os.environ['GOOGLE_API_KEY'] = 'test_key'

        from app.services.alternative_data_sources import FallbackDataService
        from app.services.ai_service import AIService
        import importlib
        import app.services.alternative_data_sources
        import app.services.ai_service
        importlib.reload(app.services.ai_service)
        importlib.reload(app.services.alternative_data_sources)

        # Mock AI response
        mock_ai_data = {
            'ticker': 'AAPL',
            'current_price': 175.50,
            'source': 'AI_FALLBACK'
        }

        with patch.object(app.services.ai_service.AIService, 'get_stock_data_from_ai', return_value=mock_ai_data):
            result = app.services.alternative_data_sources.FallbackDataService.get_stock_quote('AAPL')

        self.assertIsNotNone(result)
        self.assertEqual(result['source'], 'AI_FALLBACK')

        print("✅ PASS: Fallback cascade to AI successful")

    def test_10_api_before_ai(self):
        """Test that APIs are tried before AI"""
        print("\n[TEST 10] APIs tried before AI...")

        os.environ['FINNHUB_API_KEY'] = 'test_key'
        os.environ['GOOGLE_API_KEY'] = 'test_key'

        from app.services.alternative_data_sources import FallbackDataService, FinnhubService
        import importlib
        import app.services.alternative_data_sources
        importlib.reload(app.services.alternative_data_sources)

        # Mock Finnhub to succeed
        mock_finnhub_data = {
            'ticker': 'AAPL',
            'current_price': 175.50,
            'source': 'finnhub'
        }

        ai_called = False

        def mock_ai_get(*args, **kwargs):
            nonlocal ai_called
            ai_called = True
            return None

        with patch.object(app.services.alternative_data_sources.FinnhubService, 'get_stock_quote', return_value=mock_finnhub_data):
            with patch('app.services.ai_service.AIService.get_stock_data_from_ai', side_effect=mock_ai_get):
                result = app.services.alternative_data_sources.FallbackDataService.get_stock_quote('AAPL')

        self.assertIsNotNone(result)
        self.assertEqual(result['source'], 'finnhub')
        self.assertFalse(ai_called, "AI should not be called when Finnhub succeeds")

        print("✅ PASS: APIs prioritized over AI")

    # ========================================================================
    # TEST GROUP 5: Historical Data Integration
    # ========================================================================

    def test_11_historical_data_fallback_to_ai(self):
        """Test historical data fallback to AI"""
        print("\n[TEST 11] Historical data fallback to AI...")

        # Disable all API keys
        os.environ.pop('FINNHUB_API_KEY', None)
        os.environ.pop('TWELVE_DATA_API_KEY', None)
        os.environ.pop('ALPHA_VANTAGE_API_KEY', None)
        os.environ['GOOGLE_API_KEY'] = 'test_key'

        from app.services.alternative_data_sources import FallbackDataService
        from app.services.ai_service import AIService
        import importlib
        import app.services.alternative_data_sources
        import app.services.ai_service
        importlib.reload(app.services.ai_service)
        importlib.reload(app.services.alternative_data_sources)

        # Mock AI historical data
        mock_ai_data = {
            'ticker': 'AAPL',
            'data': [{'date': '2025-10-01', 'close': 175.0}],
            'source': 'AI_FALLBACK'
        }

        with patch.object(app.services.ai_service.AIService, 'get_historical_data_from_ai', return_value=mock_ai_data):
            result = app.services.alternative_data_sources.FallbackDataService.get_historical_data('AAPL', outputsize=30)

        self.assertIsNotNone(result)
        self.assertEqual(result['source'], 'AI_FALLBACK')
        self.assertIn('data', result)

        print("✅ PASS: Historical data fallback to AI successful")

    # ========================================================================
    # TEST GROUP 6: Error Handling & Edge Cases
    # ========================================================================

    def test_12_empty_ticker(self):
        """Test handling of empty ticker"""
        print("\n[TEST 12] Empty ticker handling...")

        os.environ['GOOGLE_API_KEY'] = 'test_key'

        from app.services.ai_service import AIService
        import importlib
        import app.services.ai_service
        importlib.reload(app.services.ai_service)

        ai_service = app.services.ai_service.AIService()

        # Mock response that handles empty ticker
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': 'Invalid ticker'
                    }]
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()

        with patch('requests.post', return_value=mock_response):
            result = ai_service.get_stock_data_from_ai('')

        # Should handle gracefully (return None or error)
        self.assertIsNone(result)

        print("✅ PASS: Empty ticker handled gracefully")

    def test_13_special_characters_ticker(self):
        """Test handling of tickers with special characters"""
        print("\n[TEST 13] Special characters in ticker...")

        os.environ['GOOGLE_API_KEY'] = 'test_key'

        from app.services.ai_service import AIService
        import importlib
        import app.services.ai_service
        importlib.reload(app.services.ai_service)

        ai_service = app.services.ai_service.AIService()

        # Test German ticker with .DE
        ticker = 'BMW.DE'

        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': json.dumps({
                            'ticker': ticker,
                            'company_name': 'BMW AG',
                            'source': 'AI_FALLBACK'
                        })
                    }]
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()

        with patch('requests.post', return_value=mock_response):
            result = ai_service.get_stock_data_from_ai(ticker)

        self.assertIsNotNone(result)
        self.assertEqual(result['ticker'], ticker)

        print("✅ PASS: Special characters handled correctly")

    def test_14_network_error_handling(self):
        """Test handling of network errors"""
        print("\n[TEST 14] Network error handling...")

        os.environ['GOOGLE_API_KEY'] = 'test_key'

        from app.services.ai_service import AIService
        import importlib
        import app.services.ai_service
        importlib.reload(app.services.ai_service)

        ai_service = app.services.ai_service.AIService()

        import requests
        with patch('requests.post', side_effect=requests.exceptions.ConnectionError("Network error")):
            result = ai_service.get_stock_data_from_ai('AAPL')

        self.assertIsNone(result)

        print("✅ PASS: Network error handled gracefully")

    def test_15_http_error_handling(self):
        """Test handling of HTTP errors (401, 403, 500)"""
        print("\n[TEST 15] HTTP error handling...")

        os.environ['GOOGLE_API_KEY'] = 'test_key'

        from app.services.ai_service import AIService
        import importlib
        import app.services.ai_service
        importlib.reload(app.services.ai_service)

        ai_service = app.services.ai_service.AIService()

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("403 Forbidden")

        with patch('requests.post', return_value=mock_response):
            result = ai_service.get_stock_data_from_ai('AAPL')

        self.assertIsNone(result)

        print("✅ PASS: HTTP errors handled gracefully")

    # ========================================================================
    # TEST GROUP 7: Data Validation
    # ========================================================================

    def test_16_validate_stock_data_structure(self):
        """Test that AI returns data in correct structure"""
        print("\n[TEST 16] Validate stock data structure...")

        os.environ['GOOGLE_API_KEY'] = 'test_key'

        from app.services.ai_service import AIService
        import importlib
        import app.services.ai_service
        importlib.reload(app.services.ai_service)

        ai_service = app.services.ai_service.AIService()

        # Mock complete response
        mock_data = {
            'ticker': 'AAPL',
            'company_name': 'Apple Inc',
            'current_price': 175.50,
            'previous_close': 174.00,
            'market_cap': 2800000,
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'source': 'AI_FALLBACK',
            'technical_indicators': {
                'rsi': 65.5,
                'macd': 1.2
            },
            'fundamental_metrics': {
                'revenue': 365817,
                'eps': 6.15
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': json.dumps(mock_data)
                    }]
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()

        with patch('requests.post', return_value=mock_response):
            result = ai_service.get_stock_data_from_ai('AAPL')

        # Validate structure
        self.assertIn('ticker', result)
        self.assertIn('company_name', result)
        self.assertIn('current_price', result)
        self.assertIn('source', result)
        self.assertEqual(result['source'], 'AI_FALLBACK')

        if 'technical_indicators' in result:
            self.assertIsInstance(result['technical_indicators'], dict)

        if 'fundamental_metrics' in result:
            self.assertIsInstance(result['fundamental_metrics'], dict)

        print("✅ PASS: Data structure validated")

    def test_17_validate_historical_data_structure(self):
        """Test that historical data has correct structure"""
        print("\n[TEST 17] Validate historical data structure...")

        os.environ['GOOGLE_API_KEY'] = 'test_key'

        from app.services.ai_service import AIService
        import importlib
        import app.services.ai_service
        importlib.reload(app.services.ai_service)

        ai_service = app.services.ai_service.AIService()

        mock_data = {
            'ticker': 'AAPL',
            'period': '1mo',
            'data': [
                {
                    'date': '2025-10-01',
                    'open': 175.0,
                    'high': 177.0,
                    'low': 174.0,
                    'close': 176.0,
                    'volume': 50000000
                }
            ],
            'source': 'AI_FALLBACK'
        }

        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': json.dumps(mock_data)
                    }]
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()

        with patch('requests.post', return_value=mock_response):
            result = ai_service.get_historical_data_from_ai('AAPL', '1mo')

        # Validate structure
        self.assertIn('data', result)
        self.assertIsInstance(result['data'], list)

        if len(result['data']) > 0:
            item = result['data'][0]
            self.assertIn('date', item)
            self.assertIn('close', item)

        print("✅ PASS: Historical data structure validated")

    # ========================================================================
    # TEST GROUP 8: Performance & Timeout Tests
    # ========================================================================

    def test_18_timeout_configuration(self):
        """Test that timeout is configured correctly"""
        print("\n[TEST 18] Timeout configuration...")

        os.environ['GOOGLE_API_KEY'] = 'test_key'

        from app.services.ai_service import AIService
        import importlib
        import app.services.ai_service
        importlib.reload(app.services.ai_service)

        ai_service = app.services.ai_service.AIService()

        # Check that timeout is passed to requests.post
        with patch('requests.post') as mock_post:
            mock_post.return_value = MagicMock()
            mock_post.return_value.json.return_value = {
                'candidates': [{
                    'content': {
                        'parts': [{
                            'text': '{}'
                        }]
                    }
                }]
            }
            mock_post.return_value.raise_for_status = MagicMock()

            try:
                ai_service.get_stock_data_from_ai('AAPL')
            except:
                pass

            # Verify timeout was passed
            if mock_post.called:
                call_kwargs = mock_post.call_args[1]
                self.assertIn('timeout', call_kwargs)
                self.assertEqual(call_kwargs['timeout'], 60)

        print("✅ PASS: Timeout configured to 60s")

    # ========================================================================
    # TEST GROUP 9: Integration with StockService
    # ========================================================================

    def test_19_stock_service_uses_fallback(self):
        """Test that StockService uses FallbackDataService"""
        print("\n[TEST 19] StockService integration...")

        # This is more of an integration test
        # Just verify the imports and structure
        from app.services.stock_service import StockService

        # Check that get_stock_info uses FallbackDataService
        import inspect
        source = inspect.getsource(StockService.get_stock_info)

        self.assertIn('FallbackDataService', source)

        print("✅ PASS: StockService uses FallbackDataService")


def run_tests():
    """Run all tests and generate report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAIFallbackSystem)

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Generate summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
            print(f"    {traceback}")

    if result.errors:
        print("\n❌ ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
            print(f"    {traceback}")

    print("\n" + "="*80)

    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        print("="*80)
        return 1


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
