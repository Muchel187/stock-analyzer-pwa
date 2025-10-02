#!/usr/bin/env python3
"""
Comprehensive App Testing Suite
Tests all major functionality and reports bugs
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"
TEST_USER = {
    "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
    "email": f"test_{datetime.now().strftime('%H%M%S')}@test.com",
    "password": "test123456"
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}TEST: {name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def pass_test(message):
    print(f"{Colors.GREEN}✓ PASS:{Colors.END} {message}")

def fail_test(message, error=""):
    print(f"{Colors.RED}✗ FAIL:{Colors.END} {message}")
    if error:
        print(f"  {Colors.YELLOW}Error: {error}{Colors.END}")

def warn_test(message):
    print(f"{Colors.YELLOW}⚠ WARN:{Colors.END} {message}")

# Test Results
results = {
    "passed": 0,
    "failed": 0,
    "warnings": 0
}

def main():
    global TOKEN
    TOKEN = None

    print(f"\n{Colors.BLUE}{'*'*60}")
    print(f"  COMPREHENSIVE APP TESTING SUITE")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'*'*60}{Colors.END}\n")

    # Test 1: Basic Endpoints
    print_test("1. Basic Endpoints")
    try:
        r = requests.get(f"{BASE_URL}/")
        if r.status_code == 200 and "Stock Analyzer" in r.text:
            pass_test("Homepage loads")
            results["passed"] += 1
        else:
            fail_test("Homepage not loading correctly")
            results["failed"] += 1
    except Exception as e:
        fail_test("Homepage failed", str(e))
        results["failed"] += 1

    # Test 2: Stock Quote
    print_test("2. Stock Data - US Stock (AAPL)")
    try:
        r = requests.get(f"{BASE_URL}/api/stock/AAPL")
        data = r.json()
        if r.status_code == 200 and data.get('ticker') == 'AAPL':
            price = data['info'].get('current_price')
            pass_test(f"Stock quote AAPL: ${price}")
            results["passed"] += 1
        else:
            fail_test("Stock quote failed", data.get('error'))
            results["failed"] += 1
    except Exception as e:
        fail_test("Stock quote exception", str(e))
        results["failed"] += 1

    # Test 3: German Stock
    print_test("3. Stock Data - German Stock (SAP.DE)")
    try:
        r = requests.get(f"{BASE_URL}/api/stock/SAP.DE")
        data = r.json()
        if r.status_code == 200 and 'SAP' in data.get('ticker', ''):
            price = data['info'].get('current_price')
            pass_test(f"German stock SAP.DE: ${price}")
            results["passed"] += 1
        else:
            fail_test("German stock failed", data.get('error'))
            results["failed"] += 1
    except Exception as e:
        fail_test("German stock exception", str(e))
        results["failed"] += 1

    # Test 4: Stock Search
    print_test("4. Stock Search")
    try:
        r = requests.get(f"{BASE_URL}/api/stock/search?q=AAPL")
        data = r.json()
        if r.status_code == 200 and len(data.get('results', [])) > 0:
            ticker = data['results'][0].get('ticker')
            pass_test(f"Search found: {ticker}")
            results["passed"] += 1
        else:
            fail_test("Search returned no results")
            results["failed"] += 1
    except Exception as e:
        fail_test("Search exception", str(e))
        results["failed"] += 1

    # Test 5: Authentication - Register
    print_test("5. Authentication - Register")
    try:
        r = requests.post(f"{BASE_URL}/api/auth/register",
                         json=TEST_USER,
                         headers={"Content-Type": "application/json"})
        data = r.json()
        if r.status_code == 201:
            pass_test(f"User registered: {TEST_USER['username']}")
            results["passed"] += 1
        else:
            fail_test("Registration failed", data.get('error'))
            results["failed"] += 1
    except Exception as e:
        fail_test("Registration exception", str(e))
        results["failed"] += 1

    # Test 6: Authentication - Login
    print_test("6. Authentication - Login")
    try:
        r = requests.post(f"{BASE_URL}/api/auth/login",
                         json={"email": TEST_USER['email'], "password": TEST_USER['password']},
                         headers={"Content-Type": "application/json"})
        data = r.json()
        if r.status_code == 200 and 'access_token' in data:
            TOKEN = data['access_token']
            pass_test(f"Login successful, token: {TOKEN[:30]}...")
            results["passed"] += 1
        else:
            fail_test("Login failed", data.get('error'))
            results["failed"] += 1
            return  # Can't continue without token
    except Exception as e:
        fail_test("Login exception", str(e))
        results["failed"] += 1
        return

    # Test 7: Protected Route
    print_test("7. Protected Route - User Profile")
    try:
        r = requests.get(f"{BASE_URL}/api/auth/profile",
                        headers={"Authorization": f"Bearer {TOKEN}"})
        data = r.json()
        # Profile endpoint returns {'user': {...}} structure
        if r.status_code == 200 and data.get('user', {}).get('username') == TEST_USER['username']:
            pass_test(f"Profile retrieved: {data['user']['username']}")
            results["passed"] += 1
        else:
            fail_test(f"Profile retrieval failed - Status: {r.status_code}, Response: {data}")
            results["failed"] += 1
    except Exception as e:
        fail_test("Profile exception", str(e))
        results["failed"] += 1

    # Test 8: FMP Integration - Piotroski Score
    print_test("8. FMP Integration - Piotroski Score")
    try:
        r = requests.get(f"{BASE_URL}/api/financial/score/AAPL")
        data = r.json()
        if r.status_code == 200 and 'piotroskiScore' in data:
            score = data.get('piotroskiScore')
            pass_test(f"Piotroski Score AAPL: {score}/9")
            results["passed"] += 1
        elif r.status_code == 404:
            warn_test("FMP API key not configured or no data")
            results["warnings"] += 1
        else:
            fail_test("Piotroski score failed", data.get('error'))
            results["failed"] += 1
    except Exception as e:
        fail_test("Piotroski exception", str(e))
        results["failed"] += 1

    # Test 9: FMP Integration - Altman Z-Score
    print_test("9. FMP Integration - Altman Z-Score")
    try:
        r = requests.get(f"{BASE_URL}/api/financial/score/AAPL")
        data = r.json()
        if r.status_code == 200 and 'altmanZScore' in data:
            score = data.get('altmanZScore')
            pass_test(f"Altman Z-Score AAPL: {score}")
            results["passed"] += 1
        elif r.status_code == 404:
            warn_test("FMP API key not configured or no data")
            results["warnings"] += 1
        else:
            fail_test("Altman Z-Score failed", data.get('error'))
            results["failed"] += 1
    except Exception as e:
        fail_test("Altman exception", str(e))
        results["failed"] += 1

    # Test 10: Watchlist
    print_test("10. Watchlist Operations")
    try:
        # Add to watchlist
        r = requests.post(f"{BASE_URL}/api/watchlist/",
                         json={"ticker": "AAPL"},
                         headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
        if r.status_code == 201:
            pass_test("Added AAPL to watchlist")
            results["passed"] += 1
        else:
            fail_test("Add to watchlist failed", r.json().get('error'))
            results["failed"] += 1

        # Get watchlist
        r = requests.get(f"{BASE_URL}/api/watchlist/",
                        headers={"Authorization": f"Bearer {TOKEN}"})
        data = r.json()
        if r.status_code == 200 and len(data.get('items', [])) > 0:
            pass_test(f"Watchlist retrieved: {len(data['items'])} items")
            results["passed"] += 1
        else:
            fail_test("Watchlist retrieval failed")
            results["failed"] += 1
    except Exception as e:
        fail_test("Watchlist exception", str(e))
        results["failed"] += 1

    # Test 11: News Service
    print_test("11. News Service")
    try:
        r = requests.get(f"{BASE_URL}/api/stock/AAPL/news?limit=5")
        data = r.json()
        if r.status_code == 200 and 'news' in data:
            news_count = len(data['news'])
            pass_test(f"News retrieved: {news_count} articles")
            results["passed"] += 1
        else:
            fail_test("News retrieval failed", data.get('error'))
            results["failed"] += 1
    except Exception as e:
        fail_test("News exception", str(e))
        results["failed"] += 1

    # Test 12: Screener
    print_test("12. Stock Screener")
    try:
        r = requests.post(f"{BASE_URL}/api/screener/",
                         json={"market_cap_min": 1000000000, "sector": "Technology"},
                         headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
        data = r.json()
        if r.status_code == 200:
            count = len(data.get('results', []))
            pass_test(f"Screener ran: {count} results")
            results["passed"] += 1
        else:
            fail_test("Screener failed", data.get('error'))
            results["failed"] += 1
    except Exception as e:
        fail_test("Screener exception", str(e))
        results["failed"] += 1

    # Print Summary
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  TEST SUMMARY")
    print(f"{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.END}")
    print(f"{Colors.RED}Failed: {results['failed']}{Colors.END}")
    print(f"{Colors.YELLOW}Warnings: {results['warnings']}{Colors.END}")

    total = results['passed'] + results['failed']
    if total > 0:
        pass_rate = (results['passed'] / total) * 100
        print(f"\n{Colors.BLUE}Pass Rate: {pass_rate:.1f}%{Colors.END}")

    print(f"\n{Colors.BLUE}Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")

    # Return exit code
    sys.exit(0 if results['failed'] == 0 else 1)

if __name__ == "__main__":
    main()
