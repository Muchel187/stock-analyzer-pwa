# ⚠️ Wichtiger Hinweis zu Yahoo Finance API

## Problem: Rate Limiting (429 Fehler)

Die App nutzt `yfinance` für kostenlose Aktiendaten von Yahoo Finance. Yahoo hat jedoch **Rate Limits**, die zu folgenden Fehlern führen können:

```
429 Client Error: Too Many Requests
```

## Warum passiert das?

Yahoo Finance erlaubt nur eine **begrenzte Anzahl von Anfragen** pro:
- IP-Adresse
- Zeiteinheit (normalerweise ~2000 Anfragen pro Stunde)
- Zu viele schnelle aufeinanderfolgende Anfragen

## Lösungen:

### 1. **Warten** (Einfachste Lösung)
- Warte 5-10 Minuten, dann funktioniert es wieder
- Die App hat Caching implementiert, sodass bereits geladene Daten nicht neu abgefragt werden

### 2. **Caching nutzen**
Die App cached alle Aktiendaten für 1 Stunde. Beim zweiten Aufruf derselben Aktie wird der Cache verwendet.

### 3. **Weniger Anfragen stellen**
- Suche gezielt nach Aktien statt sie alle durchzugehen
- Nutze die Watchlist für häufig geprüfte Aktien
- Der Screener lädt viele Aktien gleichzeitig - nutze ihn sparsam

### 4. **Alternative Daten-Quellen (Optional)**

#### Option A: Alpha Vantage (Kostenlos)
- Registriere dich bei https://www.alphavantage.co/support/#api-key
- Trage den API-Key in die `.env` ein:
  ```
  ALPHA_VANTAGE_API_KEY=dein-key-hier
  ```

#### Option B: Finnhub (Kostenlos bis 60 calls/minute)
- https://finnhub.io/
- Besseres Rate Limit als Yahoo Finance

#### Option C: IEX Cloud (Bezahlt)
- https://iexcloud.io/
- Professionelle API, zuverlässiger

### 5. **VPN nutzen**
Wenn du einen VPN hast, kannst du die IP-Adresse wechseln, um ein neues Rate Limit zu bekommen.

## Wie erkennst du Rate Limiting?

In den Server-Logs siehst du:
```
Error fetching stock info for AAPL: 429 Client Error: Too Many Requests
```

Im Browser siehst du:
```
Failed to load resource: the server responded with a status of 404
```

## Best Practices:

1. ✅ **Nutze die Suchfunktion** statt alle Aktien zu laden
2. ✅ **Verwende Watchlist** für deine wichtigsten Aktien
3. ✅ **Screener sparsam nutzen** - er lädt 50-100 Aktien auf einmal
4. ✅ **Warte zwischen Anfragen** wenn du viele Aktien analysierst
5. ✅ **Cache nutzen** - bereits geladene Daten bleiben 1 Stunde im Cache

## Für Entwickler:

Das Caching ist in `/home/jbk/Aktienanalyse/app/services/stock_service.py` implementiert:

```python
# Check cache first
cached = StockCache.get_cached(ticker, 'info')
if cached:
    return cached
```

Du kannst den Cache-Timeout in der `.env` anpassen:
```
STOCKS_CACHE_TIMEOUT=3600  # in Sekunden (Standard: 1 Stunde)
```

## Alternative: Eigene Datenbank
Für eine produktive Anwendung solltest du:
1. Daten regelmäßig (z.B. täglich nach Börsenschluss) in eine Datenbank laden
2. Die App nutzt dann die Datenbank statt Live-API-Calls
3. Nur bei Bedarf Live-Daten abrufen

---

**Zusammenfassung:** Das 429-Problem ist **normal** bei kostenloser API-Nutzung. Die App funktioniert trotzdem - du musst nur geduldig sein oder eine der obigen Lösungen nutzen.