# Langfristiger Optimierungsplan für Stock Analyzer PWA

## Executive Summary
Dieses Dokument beschreibt einen umfassenden Plan zur langfristigen Optimierung der Stock Analyzer PWA mit Fokus auf API-Key Rotation, intelligentes Caching und API-Call-Optimierung.

---

## 1. API-Key Rotation System

### 1.1 Architektur

```python
class APIKeyManager:
    """
    Zentrales Management für alle API-Keys mit automatischer Rotation
    """
    def __init__(self):
        self.api_pools = {
            'finnhub': [],
            'alpha_vantage': [],
            'twelve_data': [],
            'google_gemini': [],
            'openai': []
        }
        self.usage_tracking = {}
        self.rate_limits = {}
        self.last_rotation = {}
```

### 1.2 Implementation Plan

#### Phase 1: Multi-Key Storage (Woche 1)
```python
# .env Datei Struktur
FINNHUB_API_KEYS=key1,key2,key3
ALPHA_VANTAGE_API_KEYS=key1,key2
TWELVE_DATA_API_KEYS=key1,key2
GOOGLE_API_KEYS=key1,key2,key3
OPENAI_API_KEYS=key1,key2

# Datenbank Schema
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY,
    service VARCHAR(50),
    key_hash VARCHAR(64),  -- SHA256 hash für Sicherheit
    daily_limit INTEGER,
    hourly_limit INTEGER,
    requests_today INTEGER DEFAULT 0,
    requests_this_hour INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    error_count INTEGER DEFAULT 0,
    last_error TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api_usage_log (
    id INTEGER PRIMARY KEY,
    api_key_id INTEGER,
    endpoint VARCHAR(200),
    response_code INTEGER,
    response_time_ms INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (api_key_id) REFERENCES api_keys(id)
);
```

#### Phase 2: Rotation Logic (Woche 2)

```python
class APIKeyRotator:
    def __init__(self):
        self.load_keys_from_env()
        self.current_indices = defaultdict(int)

    def get_next_key(self, service: str) -> str:
        """
        Intelligente Key-Auswahl basierend auf:
        1. Verfügbare Requests
        2. Fehlerrate
        3. Response Zeit
        """
        keys = self.get_available_keys(service)

        if not keys:
            # Fallback auf Mock-Daten
            return None

        # Wähle Key mit besten Metriken
        best_key = self.select_best_key(keys)
        self.track_usage(best_key)

        return best_key

    def select_best_key(self, keys):
        scores = []
        for key in keys:
            score = self.calculate_key_score(key)
            scores.append((key, score))

        # Sortiere nach Score
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0][0]

    def calculate_key_score(self, key):
        """
        Score basierend auf:
        - Verbleibende Requests: 40%
        - Fehlerrate: 30%
        - Durchschnittliche Response-Zeit: 30%
        """
        remaining = key.get_remaining_requests()
        error_rate = key.get_error_rate()
        avg_response = key.get_avg_response_time()

        score = (remaining * 0.4) + ((1 - error_rate) * 0.3) + ((1000 - avg_response) / 1000 * 0.3)
        return score
```

#### Phase 3: Health Monitoring (Woche 3)

```python
class APIHealthMonitor:
    def __init__(self):
        self.health_checks = {}
        self.blacklist = set()

    async def continuous_health_check(self):
        """Läuft alle 5 Minuten"""
        while True:
            for service, keys in self.api_pools.items():
                for key in keys:
                    health = await self.check_key_health(key)

                    if health['status'] == 'failed':
                        self.handle_failed_key(key)
                    elif health['status'] == 'rate_limited':
                        self.temporarily_disable_key(key, health['retry_after'])

            await asyncio.sleep(300)  # 5 Minuten

    async def check_key_health(self, key):
        """Test-Request an API"""
        try:
            response = await self.make_test_request(key)
            return {
                'status': 'healthy' if response.status == 200 else 'failed',
                'response_time': response.elapsed,
                'retry_after': response.headers.get('Retry-After')
            }
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
```

### 1.3 Implementierungs-Roadmap

| Woche | Aufgabe | Priorität |
|-------|---------|-----------|
| 1 | Multi-Key Storage & DB Schema | Hoch |
| 2 | Basic Rotation Logic | Hoch |
| 3 | Health Monitoring | Mittel |
| 4 | Admin Dashboard | Niedrig |
| 5 | Testing & Optimization | Hoch |

---

## 2. Enhanced Caching Architecture

### 2.1 Multi-Layer Caching

```
┌─────────────────────────────────────┐
│         Browser Cache               │
│     (Service Worker - 5 Min)        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Memory Cache                 │
│    (Python Dict - 1 Min)            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Redis Cache                  │
│    (Distributed - 15 Min)           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Database Cache                  │
│    (SQLite/PostgreSQL - 1 Hour)     │
└─────────────────────────────────────┘
```

### 2.2 Intelligent Cache Strategy

```python
class SmartCacheManager:
    def __init__(self):
        self.memory_cache = TTLCache(maxsize=1000, ttl=60)
        self.redis_client = redis.Redis()

    def get(self, key: str, cache_level: str = 'auto'):
        """
        Intelligente Cache-Abfrage basierend auf:
        - Datentyp (Kurse vs. Historisch)
        - Tageszeit (Marktzeiten vs. Nachts)
        - Daten-Alter
        """
        # 1. Memory Cache (schnellste)
        if key in self.memory_cache:
            return self.memory_cache[key]

        # 2. Redis Cache
        redis_data = self.redis_client.get(key)
        if redis_data:
            self.memory_cache[key] = redis_data
            return redis_data

        # 3. Database Cache
        db_data = self.get_from_database(key)
        if db_data and self.is_fresh_enough(db_data):
            self.populate_upper_caches(key, db_data)
            return db_data

        return None

    def is_fresh_enough(self, data):
        """Dynamische Freshness-Berechnung"""
        if self.is_market_hours():
            # Während Marktzeiten: striktere Freshness
            return data['age'] < 300  # 5 Minuten
        else:
            # Außerhalb Marktzeiten: lockerer
            return data['age'] < 3600  # 1 Stunde
```

### 2.3 Cache Warming Strategy

```python
class CacheWarmer:
    """Proaktives Cache-Aufwärmen für populäre Aktien"""

    def __init__(self):
        self.popular_stocks = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
        self.user_watchlists = []
        self.portfolio_stocks = []

    async def warm_cache_schedule(self):
        """Läuft vor Marktöffnung"""
        # 30 Minuten vor US-Marktöffnung (9:00 AM EST)
        schedule.every().day.at("08:30").do(self.warm_us_stocks)

        # 30 Minuten vor EU-Marktöffnung (9:00 AM CET)
        schedule.every().day.at("08:30").do(self.warm_eu_stocks)

        while True:
            schedule.run_pending()
            await asyncio.sleep(60)

    async def warm_us_stocks(self):
        stocks_to_warm = self.popular_stocks + self.get_user_stocks('US')

        for ticker in stocks_to_warm:
            # Parallel fetching
            tasks = [
                self.fetch_stock_info(ticker),
                self.fetch_historical_data(ticker, '1mo'),
                self.fetch_technical_indicators(ticker)
            ]
            await asyncio.gather(*tasks)

            # Rate limiting
            await asyncio.sleep(0.5)
```

### 2.4 Cache Invalidation

```python
class CacheInvalidator:
    """Intelligente Cache-Invalidierung"""

    def __init__(self):
        self.invalidation_rules = {
            'stock_info': timedelta(minutes=5),
            'historical_1d': timedelta(minutes=1),
            'historical_1mo': timedelta(hours=1),
            'technical': timedelta(minutes=15),
            'fundamental': timedelta(days=1),
            'news': timedelta(minutes=30)
        }

    def should_invalidate(self, cache_type: str, cached_at: datetime) -> bool:
        """Entscheidet ob Cache invalidiert werden soll"""
        max_age = self.invalidation_rules.get(cache_type, timedelta(hours=1))
        age = datetime.now() - cached_at

        # Während Marktzeiten striktere Invalidierung
        if self.is_market_hours() and cache_type in ['stock_info', 'historical_1d']:
            max_age = max_age / 2

        return age > max_age
```

---

## 3. API Call Optimization

### 3.1 Request Batching

```python
class RequestBatcher:
    """Bündelt mehrere Requests zu einem"""

    def __init__(self):
        self.batch_queue = defaultdict(list)
        self.batch_size = 10
        self.batch_timeout = 100  # ms

    async def add_request(self, ticker: str, request_type: str):
        """Fügt Request zur Warteschlange hinzu"""
        self.batch_queue[request_type].append(ticker)

        if len(self.batch_queue[request_type]) >= self.batch_size:
            return await self.execute_batch(request_type)

        # Warte auf mehr Requests oder Timeout
        await asyncio.sleep(self.batch_timeout / 1000)
        return await self.execute_batch(request_type)

    async def execute_batch(self, request_type: str):
        """Führt gebündelte Requests aus"""
        tickers = self.batch_queue[request_type]
        self.batch_queue[request_type] = []

        # Batch API call
        if request_type == 'quote':
            # Finnhub unterstützt keine Batch-Quotes, aber wir können parallel fetchen
            tasks = [self.fetch_quote(t) for t in tickers]
            results = await asyncio.gather(*tasks)
            return dict(zip(tickers, results))
```

### 3.2 Smart Request Deduplication

```python
class RequestDeduplicator:
    """Verhindert doppelte Requests"""

    def __init__(self):
        self.pending_requests = {}
        self.request_lock = asyncio.Lock()

    async def fetch_with_dedup(self, key: str, fetch_func):
        """Dedupliziert parallele Requests"""
        async with self.request_lock:
            # Check if request is already pending
            if key in self.pending_requests:
                # Wait for existing request
                return await self.pending_requests[key]

            # Create new request
            future = asyncio.create_task(fetch_func())
            self.pending_requests[key] = future

        try:
            result = await future
            return result
        finally:
            async with self.request_lock:
                del self.pending_requests[key]
```

### 3.3 Predictive Prefetching

```python
class PredictivePrefetcher:
    """Lädt Daten basierend auf Nutzerverhalten voraus"""

    def __init__(self):
        self.user_patterns = defaultdict(list)
        self.ml_model = self.load_prediction_model()

    def track_user_action(self, user_id: str, action: dict):
        """Trackt Nutzeraktionen für Vorhersagen"""
        self.user_patterns[user_id].append({
            'timestamp': datetime.now(),
            'action': action['type'],
            'ticker': action.get('ticker'),
            'context': action.get('context')
        })

    def predict_next_action(self, user_id: str):
        """Sagt nächste Nutzeraktion voraus"""
        patterns = self.user_patterns[user_id][-100:]  # Letzte 100 Aktionen

        # Simple Heuristik (kann durch ML-Modell ersetzt werden)
        if patterns:
            # Häufigste Aktionen
            common_tickers = Counter([p['ticker'] for p in patterns if p['ticker']])

            # Zeitbasierte Muster (z.B. immer morgens AAPL checken)
            time_patterns = self.analyze_time_patterns(patterns)

            return {
                'likely_tickers': common_tickers.most_common(5),
                'likely_actions': time_patterns
            }

    async def prefetch_predicted(self, user_id: str):
        """Lädt vorhergesagte Daten voraus"""
        predictions = self.predict_next_action(user_id)

        for ticker, _ in predictions['likely_tickers']:
            # Prefetch im Hintergrund
            asyncio.create_task(self.prefetch_stock_data(ticker))
```

### 3.4 GraphQL Implementation

```python
# GraphQL Schema für effizientere Abfragen
schema = """
type Query {
    stock(ticker: String!): Stock
    stocks(tickers: [String!]!): [Stock]
    portfolio(userId: ID!): Portfolio
}

type Stock {
    ticker: String!
    info: StockInfo
    history(period: String): [PricePoint]
    technical: TechnicalIndicators
    fundamental: FundamentalAnalysis
    news(limit: Int): [NewsItem]
    # Client kann genau spezifizieren was benötigt wird
}
"""

class GraphQLResolver:
    """Löst nur angeforderte Felder auf"""

    async def resolve_stock(self, info, ticker):
        # Nur angeforderte Felder laden
        requested_fields = info.field_nodes[0].selection_set.selections

        result = {'ticker': ticker}

        for field in requested_fields:
            field_name = field.name.value

            if field_name == 'info':
                result['info'] = await self.get_stock_info(ticker)
            elif field_name == 'history':
                period = field.arguments.get('period', '1mo')
                result['history'] = await self.get_history(ticker, period)
            # ... etc

        return result
```

---

## 4. Implementierungs-Zeitplan

### Monat 1: Foundation
- **Woche 1-2**: API Key Rotation Basis
- **Woche 3-4**: Enhanced Caching Layer 1 (Memory + Redis)

### Monat 2: Optimization
- **Woche 5-6**: Request Batching & Deduplication
- **Woche 7-8**: Cache Warming & Invalidation

### Monat 3: Advanced Features
- **Woche 9-10**: Predictive Prefetching
- **Woche 11-12**: GraphQL Integration & Testing

---

## 5. Performance-Ziele

### Aktuelle Metriken
- API Calls pro Tag: ~5000 (führt zu Rate Limits)
- Cache Hit Rate: 30%
- Durchschnittliche Response Zeit: 2-5 Sekunden
- Fehlerrate bei API Limits: 40%

### Ziel-Metriken (nach 3 Monaten)
- API Calls pro Tag: < 1000 (80% Reduktion)
- Cache Hit Rate: > 85%
- Durchschnittliche Response Zeit: < 500ms
- Fehlerrate bei API Limits: < 5%

---

## 6. Kostenanalyse

### Aktuelle Kosten (Kostenlos)
- Einschränkungen durch API-Limits
- Schlechte User Experience
- Keine Skalierbarkeit

### Geschätzte Kosten nach Optimierung

#### Minimal Setup (€50/Monat)
- 3x Google Cloud Konten: €0 (Free Tier)
- Redis Cloud: €10/Monat (30MB)
- Alpha Vantage Premium: €30/Monat
- Twelve Data Basic: €10/Monat

#### Professional Setup (€200/Monat)
- Google Gemini API: €20/Monat (2M tokens)
- Redis Cloud: €30/Monat (250MB)
- Alpha Vantage Premium: €50/Monat
- Twelve Data Pro: €79/Monat
- Finnhub Plus: €20/Monat

#### Enterprise Setup (€500+/Monat)
- Alle APIs in höchsten Tiers
- Dedizierte Redis Cluster
- Real-time WebSocket feeds
- Backup APIs

---

## 7. Monitoring & Alerting

```python
class APIMonitoringSystem:
    def __init__(self):
        self.metrics = {
            'api_calls_total': Counter(),
            'api_calls_failed': Counter(),
            'cache_hits': Counter(),
            'cache_misses': Counter(),
            'response_times': []
        }

    def track_api_call(self, service: str, success: bool, response_time: float):
        self.metrics['api_calls_total'][service] += 1

        if not success:
            self.metrics['api_calls_failed'][service] += 1

        self.metrics['response_times'].append(response_time)

        # Alert wenn Fehlerrate > 10%
        error_rate = self.metrics['api_calls_failed'][service] / self.metrics['api_calls_total'][service]
        if error_rate > 0.1:
            self.send_alert(f"High error rate for {service}: {error_rate:.2%}")

    def generate_daily_report(self):
        """Täglicher Report über API-Nutzung"""
        return {
            'total_calls': sum(self.metrics['api_calls_total'].values()),
            'failed_calls': sum(self.metrics['api_calls_failed'].values()),
            'cache_hit_rate': self.calculate_cache_hit_rate(),
            'avg_response_time': statistics.mean(self.metrics['response_times']),
            'api_breakdown': dict(self.metrics['api_calls_total'])
        }
```

---

## 8. Testing Strategy

### Unit Tests
```python
def test_api_rotation():
    rotator = APIKeyRotator()
    rotator.add_keys(['key1', 'key2', 'key3'])

    # Test rotation
    keys_used = set()
    for _ in range(10):
        key = rotator.get_next_key('finnhub')
        keys_used.add(key)

    assert len(keys_used) >= 2  # Should rotate between keys

def test_cache_layers():
    cache = SmartCacheManager()

    # Test cache hierarchy
    cache.set('test_key', 'value', level='database')
    assert cache.get('test_key') == 'value'

    # Should now be in memory cache
    assert 'test_key' in cache.memory_cache
```

### Integration Tests
```python
async def test_batch_requests():
    batcher = RequestBatcher()

    # Add multiple requests
    tasks = []
    for ticker in ['AAPL', 'MSFT', 'GOOGL']:
        tasks.append(batcher.add_request(ticker, 'quote'))

    results = await asyncio.gather(*tasks)

    # Should batch and return all results
    assert len(results) == 3
```

### Load Tests
```python
def test_high_load():
    """Simuliert hohe Last"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = []

        for _ in range(1000):
            future = executor.submit(make_api_request)
            futures.append(future)

        results = [f.result() for f in futures]

    # Sollte ohne Rate Limits durchlaufen
    success_rate = sum(1 for r in results if r.success) / len(results)
    assert success_rate > 0.95  # 95% Success Rate
```

---

## 9. Migration Plan

### Phase 1: Vorbereitung (1 Woche)
1. Backup aller Daten
2. Test-Environment aufsetzen
3. Neue Dependencies installieren

### Phase 2: Schrittweise Migration (2 Wochen)
1. Mock Data Service aktivieren (✅ bereits erledigt)
2. API Key Rotation implementieren
3. Memory Cache Layer hinzufügen
4. Redis Integration

### Phase 3: Testing (1 Woche)
1. Alle Features testen
2. Performance-Tests
3. User Acceptance Testing

### Phase 4: Rollout (3 Tage)
1. Staged Rollout (10% → 50% → 100%)
2. Monitoring aktivieren
3. Hotfix-Bereitschaft

---

## 10. Fazit & Nächste Schritte

### Sofortige Aktionen (diese Woche)
1. ✅ Mock Data Service implementiert
2. ⏳ Mehrere API-Keys in .env hinzufügen
3. ⏳ Basis-Rotation implementieren

### Kurzfristig (nächster Monat)
1. Redis Cloud Account erstellen
2. Cache Warming implementieren
3. Request Batching testen

### Langfristig (3 Monate)
1. Vollständige Implementation aller Features
2. Performance-Optimierung
3. Skalierung auf mehr Nutzer

---

**Dokument erstellt:** 2. Oktober 2025
**Autor:** Claude AI Assistant
**Version:** 1.0
**Status:** Aktionsbereit