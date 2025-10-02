# Portfolio Debug - Quick Reference

## Problem
Portfolio zeigt keine Aktien an, obwohl sie in der Datenbank vorhanden sind.

## Quick Fix Checklist

### 1. Browser Check (30 Sekunden)
```
□ Öffne Browser DevTools (F12)
□ Gehe zu Console Tab
□ Hard Refresh: Ctrl+Shift+R (Windows/Linux) oder Cmd+Shift+R (Mac)
□ Suche nach "[Portfolio]" Logs
□ Prüfe auf rote Fehler
```

### 2. Bist du auf der richtigen Seite?
```
✅ Portfolio-Seite: http://127.0.0.1:5000/#portfolio
❌ NICHT Dashboard: http://127.0.0.1:5000/#dashboard
```

Dashboard zeigt nur Summary, Portfolio-Seite zeigt die volle Liste!

### 3. Server Logs prüfen
```bash
cd /home/jbk/Aktienanalyse
tail -f flask_debug.log | grep Portfolio
```

Erwartete Logs:
```
[Portfolio] Getting portfolio for user 2
[Portfolio] Found 1 items
[Portfolio] Successfully returning 1 items
```

### 4. API direkt testen
```bash
# Terminal 1: Get token
cd /home/jbk/Aktienanalyse
source venv/bin/activate
python3 -c "
from app import create_app
from flask_jwt_extended import create_access_token

app = create_app()
with app.app_context():
    token = create_access_token(identity='2')
    print(token)
"

# Terminal 2: Test API
curl -H "Authorization: Bearer <TOKEN>" http://127.0.0.1:5000/api/portfolio/
```

Erwartete Response: `{"items": [{"ticker": "GME", ...}], "summary": {...}}`

### 5. Database prüfen
```bash
cd /home/jbk/Aktienanalyse
source venv/bin/activate
python3 -c "
from app import create_app, db
from app.models import Portfolio

app = create_app()
with app.app_context():
    items = Portfolio.query.filter_by(user_id=2).all()
    for item in items:
        print(f'{item.ticker}: {item.shares} shares')
"
```

Erwartete Ausgabe: `GME: 1120.0 shares`

## Console Logs Interpretieren

### ✅ Erfolgreich
```
[Portfolio] Fetching portfolio data...
[Portfolio] Data received: {items: Array(1), summary: {...}}
[Portfolio] Displaying 1 items
[displayPortfolioDetails] Starting display with data: {...}
[displayPortfolioDetails] Rendering 1 holdings
[displayPortfolioDetails] Holdings table rendered successfully
```

### ❌ Fehler: API gibt leere Liste zurück
```
[Portfolio] Data received: {items: [], summary: {...}}
[Portfolio] Displaying 0 items
```

**Lösung:** Database prüfen (Schritt 5)

### ❌ Fehler: API Fehler
```
[Portfolio] Error loading portfolio: Failed to fetch
```

**Lösung:** 
1. Server läuft? → `ps aux | grep app.py`
2. Firewall? → `curl http://127.0.0.1:5000/api/portfolio/`
3. JWT Token abgelaufen? → Logout & Login

### ❌ Fehler: Table Body nicht gefunden
```
[displayPortfolioDetails] Table body not found!
```

**Lösung:** Falsche Seite! Gehe zu #portfolio (nicht #dashboard)

## Test Page verwenden

```bash
# 1. Server starten
cd /home/jbk/Aktienanalyse
source venv/bin/activate
python app.py

# 2. Browser öffnen
firefox test_portfolio_frontend.html

# 3. Token einfügen (von Login kopieren)
# 4. "Test Portfolio Load" klicken
# 5. Logs unten prüfen
```

## Common Errors & Solutions

| Error | Ursache | Lösung |
|-------|---------|--------|
| Items array leer | Keine Transaktionen | Transaktion hinzufügen |
| 401 Unauthorized | Token abgelaufen | Logout → Login |
| Table body not found | Falsche Seite | Zu #portfolio navigieren |
| Failed to fetch | Server offline | `python app.py` starten |
| Spinner dreht ewig | API hängt | Server logs prüfen |

## Schnelle Selbstdiagnose

```javascript
// Browser Console eingeben:
console.clear();
await app.loadPortfolio();
// Prüfe Logs oben ↑
```

Wenn Logs erscheinen → Frontend OK
Wenn keine Logs → app Objekt nicht initialisiert

## Emergency Fix

Wenn nichts funktioniert:

```bash
# 1. Server stoppen
pkill -f "python.*app.py"

# 2. Browser Cache leeren
# Ctrl+Shift+Delete → Alles löschen

# 3. Server neu starten
cd /home/jbk/Aktienanalyse
source venv/bin/activate
python app.py

# 4. Neuer Browser Tab
# http://127.0.0.1:5000

# 5. Login → Portfolio
```

## Kontakt für Support

Wenn Problem weiterhin besteht, schicke:
1. Screenshot von Browser Console (F12 → Console)
2. Screenshot von Network Tab (F12 → Network → api/portfolio/)
3. Output von: `tail -20 flask_debug.log`

---

**Quick Reference Created:** 2025-10-02
**Based on:** OPTIMIZATION_PLAN.md
