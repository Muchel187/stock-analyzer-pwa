#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Script
Tests all critical endpoints and reports failures
"""

import requests
import json
import sys
from datetime import datetime

class APITester:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {token}'} if token else {}
        self.results = []
    
    def test_endpoint(self, name, method, path, data=None, expected_status=200, auth_required=False):
        """Test a single endpoint"""
        url = f"{self.base_url}{path}"
        headers = self.headers if auth_required else {}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == 'PUT':
                headers['Content-Type'] = 'application/json'
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            
            success = response.status_code == expected_status
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except:
                response_data = response.text[:200] if response.text else "Empty response"
            
            self.results.append({
                'name': name,
                'success': success,
                'status': response.status_code,
                'expected': expected_status,
                'response': response_data
            })
            
            return success, response
        except Exception as e:
            self.results.append({
                'name': name,
                'success': False,
                'error': str(e)
            })
            return False, None
    
    def run_all_tests(self):
        """Run all endpoint tests"""
        print("🧪 Starting Comprehensive API Tests...\n")
        
        # Stock endpoints (no auth required)
        print("📊 Testing Stock Endpoints (No Auth)...")
        self.test_endpoint("Stock Info - AAPL", "GET", "/api/stock/AAPL")
        self.test_endpoint("Stock History - AAPL", "GET", "/api/stock/AAPL/history?period=1mo")
        self.test_endpoint("Stock Search", "GET", "/api/stock/search?q=AAPL")
        self.test_endpoint("Stock News - AAPL", "GET", "/api/stock/AAPL/news?limit=5")
        self.test_endpoint("Market News", "GET", "/api/stock/news/market?limit=10")
        
        # Stock comparison (no auth)
        print("\n🔄 Testing Stock Comparison...")
        self.test_endpoint("Stock Comparison - 2 Stocks", "POST", "/api/stock/compare", {
            "tickers": ["AAPL", "MSFT"],
            "period": "1y"
        })
        
        # AI Analysis (no auth)
        print("\n🤖 Testing AI Analysis...")
        self.test_endpoint("AI Analysis - AAPL", "GET", "/api/stock/AAPL/analyze-with-ai")
        
        # Auth endpoints
        print("\n🔐 Testing Auth Endpoints...")
        # Try to register a test user
        test_email = f"test_{datetime.now().timestamp()}@test.com"
        success, response = self.test_endpoint("User Registration", "POST", "/api/auth/register", {
            "username": f"testuser_{int(datetime.now().timestamp())}",
            "email": test_email,
            "password": "TestPassword123!"
        }, expected_status=201)
        
        # If registration successful, get token and test authenticated endpoints
        if success and response:
            try:
                token = response.json().get('access_token')
                if token:
                    self.headers['Authorization'] = f'Bearer {token}'
                    print("\n✅ Got auth token, testing authenticated endpoints...\n")
                    
                    # Portfolio endpoints
                    print("💼 Testing Portfolio Endpoints (Auth Required)...")
                    self.test_endpoint("Get Portfolio", "GET", "/api/portfolio/", auth_required=True)
                    self.test_endpoint("Create Transaction", "POST", "/api/portfolio/transaction", {
                        "ticker": "AAPL",
                        "quantity": 10,
                        "price": 150.0,
                        "transaction_type": "BUY",
                        "date": datetime.now().isoformat()
                    }, auth_required=True)
                    self.test_endpoint("Portfolio Performance", "GET", "/api/portfolio/performance", auth_required=True)
                    
                    # Watchlist endpoints
                    print("\n⭐ Testing Watchlist Endpoints (Auth Required)...")
                    self.test_endpoint("Get Watchlist", "GET", "/api/watchlist/", auth_required=True)
                    self.test_endpoint("Add to Watchlist", "POST", "/api/watchlist/", {
                        "ticker": "MSFT"
                    }, expected_status=201, auth_required=True)
                    
                    # Alert endpoints
                    print("\n🔔 Testing Alert Endpoints (Auth Required)...")
                    self.test_endpoint("Get Alerts", "GET", "/api/alerts/", auth_required=True)
                    self.test_endpoint("Create Alert", "POST", "/api/alerts/", {
                        "ticker": "AAPL",
                        "condition": "ABOVE",
                        "target_price": 200.0,
                        "notification_type": "PLATFORM"
                    }, expected_status=201, auth_required=True)
                    
                    # Screener endpoints
                    print("\n🔍 Testing Screener Endpoints (Auth Required)...")
                    self.test_endpoint("Get Presets", "GET", "/api/screener/presets", auth_required=True)
            except Exception as e:
                print(f"❌ Error testing authenticated endpoints: {e}")
        
        # Print results
        print("\n" + "="*80)
        print("📊 TEST RESULTS SUMMARY")
        print("="*80)
        
        passed = sum(1 for r in self.results if r['success'])
        failed = len(self.results) - passed
        
        print(f"✅ Passed: {passed}/{len(self.results)}")
        print(f"❌ Failed: {failed}/{len(self.results)}")
        print()
        
        if failed > 0:
            print("❌ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"\n  🔴 {result['name']}")
                    if 'error' in result:
                        print(f"     Error: {result['error']}")
                    else:
                        print(f"     Expected: {result['expected']}, Got: {result['status']}")
                        if isinstance(result['response'], dict):
                            print(f"     Response: {json.dumps(result['response'], indent=6)}")
                        else:
                            print(f"     Response: {result['response']}")
        
        print("\n" + "="*80)
        return failed == 0

if __name__ == "__main__":
    base_url = "http://localhost:5000"
    
    print("🚀 Stock Analyzer API Testing Suite")
    print(f"📍 Testing server: {base_url}\n")
    
    tester = APITester(base_url)
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All API tests passed!")
    else:
        print("\n⚠️  Some API tests failed - review above for details")
    
    sys.exit(0 if success else 1)
