#!/usr/bin/env python3
"""
Vollständiger App-Test - Alle Funktionen
"""

import requests
import json
import time

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
ENDC = '\033[0m'

BASE_URL = "http://localhost:5000"

def test_feature(name, func):
    """Test wrapper with error handling"""
    print(f"\n{BLUE}[TEST] {name}{ENDC}")
    try:
        result = func()
        if result:
            print(f"{GREEN}✅ {name} - ERFOLGREICH{ENDC}")
            return True
        else:
            print(f"{RED}❌ {name} - FEHLGESCHLAGEN{ENDC}")
            return False
    except Exception as e:
        print(f"{RED}❌ {name} - ERROR: {str(e)}{ENDC}")
        return False

class AppTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user = None

    def test_server(self):
        """Test if server is running"""
        response = self.session.get(f"{BASE_URL}/")
        return response.status_code == 200

    def test_registration(self):
        """Test user registration"""
        timestamp = str(int(time.time()))
        data = {
            "username": f"test_{timestamp}",
            "email": f"test_{timestamp}@test.com",
            "password": "Test123!"
        }

        response = self.session.post(f"{BASE_URL}/api/auth/register", json=data)
        if response.status_code == 201:
            result = response.json()
            self.token = result.get('access_token')
            self.user = result.get('user')
            return True
        return False

    def test_login(self):
        """Test login with existing user"""
        data = {
            "email": "testuser1903",  # Using previously created user
            "password": "Test123!"
        }

        response = self.session.post(f"{BASE_URL}/api/auth/login", json=data)
        if response.status_code == 200:
            result = response.json()
            self.token = result.get('access_token')
            self.user = result.get('user')
            return True
        return False

    def test_stock_info(self):
        """Test stock info endpoint"""
        response = self.session.get(f"{BASE_URL}/api/stock/AAPL")
        if response.status_code == 200:
            data = response.json()
            if 'info' in data and 'current_price' in data['info']:
                print(f"  AAPL Preis: ${data['info']['current_price']}")
                return True
        return False

    def test_stock_history(self):
        """Test stock history endpoint"""
        response = self.session.get(f"{BASE_URL}/api/stock/AAPL/history?period=1mo")
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                print(f"  History: {len(data['data'])} Datenpunkte")
                return True
        return False

    def test_stock_search(self):
        """Test stock search"""
        response = self.session.get(f"{BASE_URL}/api/stock/search?q=AAPL")
        if response.status_code == 200:
            data = response.json()
            if 'results' in data:
                print(f"  Suchergebnisse: {len(data['results'])} gefunden")
                return True
        return False

    def test_portfolio(self):
        """Test portfolio operations"""
        if not self.token:
            print("  Übersprungen - kein Auth Token")
            return False

        headers = {'Authorization': f'Bearer {self.token}'}

        # Get portfolio
        response = self.session.get(f"{BASE_URL}/api/portfolio/", headers=headers)
        if response.status_code != 200:
            return False

        # Add transaction
        transaction = {
            "ticker": "AAPL",
            "transaction_type": "buy",
            "quantity": 10,
            "price": 150.00
        }

        response = self.session.post(
            f"{BASE_URL}/api/portfolio/transaction",
            json=transaction,
            headers=headers
        )

        if response.status_code in [200, 201]:
            print("  Portfolio-Transaktion hinzugefügt")
            return True
        return False

    def test_watchlist(self):
        """Test watchlist operations"""
        if not self.token:
            print("  Übersprungen - kein Auth Token")
            return False

        headers = {'Authorization': f'Bearer {self.token}'}

        # Add to watchlist
        response = self.session.post(
            f"{BASE_URL}/api/watchlist/",
            json={"ticker": "MSFT"},
            headers=headers
        )

        if response.status_code in [200, 201, 409]:  # 409 = already exists
            # Get watchlist
            response = self.session.get(f"{BASE_URL}/api/watchlist/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"  Watchlist: {len(data.get('items', []))} Items")
                return True
        return False

    def test_screener(self):
        """Test stock screener"""
        if not self.token:
            print("  Übersprungen - kein Auth Token")
            return False

        headers = {'Authorization': f'Bearer {self.token}'}

        criteria = {
            "criteria": {
                "min_price": 10,
                "max_price": 1000,
                "min_volume": 1000000
            }
        }

        response = self.session.post(
            f"{BASE_URL}/api/screener/",
            json=criteria,
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            print(f"  Screener: {len(data.get('results', []))} Aktien gefunden")
            return True
        return False

    def test_alerts(self):
        """Test price alerts"""
        if not self.token:
            print("  Übersprungen - kein Auth Token")
            return False

        headers = {'Authorization': f'Bearer {self.token}'}

        alert = {
            "ticker": "AAPL",
            "condition": "above",
            "price": 200.00,
            "name": "AAPL High Alert"
        }

        response = self.session.post(
            f"{BASE_URL}/api/alerts/",
            json=alert,
            headers=headers
        )

        if response.status_code in [200, 201]:
            print("  Alert erstellt")
            return True
        return False

    def test_ai_analysis(self):
        """Test AI analysis (brief)"""
        if not self.token:
            print("  Übersprungen - kein Auth Token")
            return False

        headers = {'Authorization': f'Bearer {self.token}'}

        print("  KI-Analyse wird angefordert (kann 10-30 Sekunden dauern)...")
        response = self.session.get(
            f"{BASE_URL}/api/stock/AAPL/analyze-with-ai",
            headers=headers,
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            if 'analysis' in data:
                print("  KI-Analyse erfolgreich erhalten")
                return True
        return False

    def test_news(self):
        """Test news endpoints"""
        # Stock news
        response = self.session.get(f"{BASE_URL}/api/stock/AAPL/news?limit=5")
        if response.status_code == 200:
            data = response.json()
            if 'news' in data:
                print(f"  AAPL News: {len(data['news'])} Artikel")

                # Market news
                response = self.session.get(f"{BASE_URL}/api/stock/news/market?limit=10")
                if response.status_code == 200:
                    data = response.json()
                    if 'news' in data:
                        print(f"  Market News: {len(data['news'])} Artikel")
                        return True
        return False

def main():
    print(f"\n{BLUE}{'='*60}{ENDC}")
    print(f"{BLUE}     STOCK ANALYZER PWA - VOLLSTÄNDIGER FUNKTIONSTEST{ENDC}")
    print(f"{BLUE}{'='*60}{ENDC}")

    tester = AppTester()
    results = []

    # Run all tests
    tests = [
        ("Server Verfügbarkeit", tester.test_server),
        ("User Registration", tester.test_registration),
        ("User Login", tester.test_login),
        ("Stock Info API", tester.test_stock_info),
        ("Stock History API", tester.test_stock_history),
        ("Stock Search API", tester.test_stock_search),
        ("Portfolio Management", tester.test_portfolio),
        ("Watchlist Management", tester.test_watchlist),
        ("Stock Screener", tester.test_screener),
        ("Price Alerts", tester.test_alerts),
        ("News API", tester.test_news),
        ("KI-Analyse", tester.test_ai_analysis),
    ]

    for name, test_func in tests:
        results.append(test_feature(name, test_func))

    # Summary
    print(f"\n{BLUE}{'='*60}{ENDC}")
    print(f"{BLUE}                    ZUSAMMENFASSUNG{ENDC}")
    print(f"{BLUE}{'='*60}{ENDC}")

    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"\nGetestete Features: {total}")
    print(f"{GREEN}Erfolgreich: {passed}{ENDC}")
    print(f"{RED}Fehlgeschlagen: {total - passed}{ENDC}")
    print(f"\nErfolgsrate: {percentage:.1f}%")

    if percentage == 100:
        print(f"\n{GREEN}🎉 ALLE TESTS BESTANDEN! Die App funktioniert einwandfrei!{ENDC}")
    elif percentage >= 80:
        print(f"\n{YELLOW}⚠️ Die meisten Features funktionieren. Einige Probleme müssen behoben werden.{ENDC}")
    else:
        print(f"\n{RED}❌ Kritische Probleme gefunden. Sofortige Behebung erforderlich.{ENDC}")

if __name__ == "__main__":
    main()