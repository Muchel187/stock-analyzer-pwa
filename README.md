# Stock Analyzer - Progressive Web App

Eine fortschrittliche PWA für Aktienanalyse und Portfolio-Management mit KI-gestützten Insights.

## Features

### 📊 Kern-Features
- **Echtzeit-Aktienanalyse** für US-Börsen und DAX
- **Portfolio-Management** mit Performance-Tracking
- **Personalisierte Watchlists** mit Preis-Tracking
- **Intelligenter Stock-Screener** mit vordefinierten Strategien
- **Preis-Alerts** mit E-Mail-Benachrichtigungen
- **KI-gestützte Analysen** über OpenAI Integration

### 🚀 PWA-Funktionalität
- **Offline-Fähigkeit** durch Service Worker
- **App-Installation** auf Desktop und Mobile
- **Push-Benachrichtigungen** (vorbereitet)
- **Responsive Design** für alle Geräte

### 📈 Analyse-Features
- Technische Indikatoren (RSI, MACD, Bollinger Bands)
- Fundamentalanalyse mit Scoring-System
- KI-generierte Investment-Empfehlungen
- Historische Kursdaten und Charts
- Diversifikationsanalyse

## Tech Stack

### Backend
- **Python 3.11** mit Flask
- **PostgreSQL** für Datenpersistenz
- **Redis** für Caching
- **yfinance** für Finanzdaten
- **APScheduler** für Hintergrund-Jobs
- **JWT** für Authentifizierung

### Frontend
- **Vanilla JavaScript** (ES6+)
- **Chart.js** für Visualisierungen
- **PWA** mit Service Worker
- **Responsive CSS** mit CSS Variables

### DevOps
- **Docker & Docker Compose**
- **Nginx** als Reverse Proxy
- **GitHub Actions** ready
- **Pytest** für Testing

## Installation

### Voraussetzungen
- Docker & Docker Compose
- OpenAI API Key (optional, für KI-Features)

### Quick Start

1. **Repository klonen**
```bash
git clone <repository-url>
cd Aktienanalyse
```

2. **Environment-Variablen konfigurieren**
```bash
cp .env.example .env
# .env bearbeiten und API-Keys eintragen
```

3. **Mit Docker Compose starten**
```bash
docker-compose up -d
```

4. **App öffnen**
```
http://localhost:5000
```

### Lokale Entwicklung (ohne Docker)

1. **Virtual Environment erstellen**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows
```

2. **Dependencies installieren**
```bash
pip install -r requirements.txt
```

3. **Datenbank initialisieren**
```bash
flask db upgrade
```

4. **Entwicklungsserver starten**
```bash
python app.py
```

## API Dokumentation

### Authentifizierung
Alle geschützten Endpoints benötigen einen JWT-Token im Header:
```
Authorization: Bearer <token>
```

### Haupt-Endpoints

#### Auth
- `POST /api/auth/register` - Neuen Benutzer registrieren
- `POST /api/auth/login` - Anmelden
- `POST /api/auth/refresh` - Token erneuern
- `GET /api/auth/profile` - Profil abrufen
- `PUT /api/auth/profile` - Profil aktualisieren

#### Stocks
- `GET /api/stock/<ticker>` - Aktiendetails abrufen
- `GET /api/stock/<ticker>/history` - Historische Daten
- `POST /api/stock/analyze-with-ai` - KI-Analyse
- `GET /api/stock/recommendations` - Empfehlungen

#### Portfolio
- `GET /api/portfolio/` - Portfolio abrufen
- `POST /api/portfolio/transaction` - Transaktion hinzufügen
- `GET /api/portfolio/transactions` - Transaktionshistorie
- `GET /api/portfolio/performance` - Performance-Daten

#### Watchlist
- `GET /api/watchlist/` - Watchlist abrufen
- `POST /api/watchlist/` - Aktie hinzufügen
- `DELETE /api/watchlist/<ticker>` - Aktie entfernen

#### Screener
- `POST /api/screener/` - Aktien screenen
- `GET /api/screener/presets` - Vordefinierte Strategien

#### Alerts
- `GET /api/alerts/` - Alerts abrufen
- `POST /api/alerts/` - Alert erstellen
- `PUT /api/alerts/<id>` - Alert aktualisieren
- `DELETE /api/alerts/<id>` - Alert löschen

## Testing

### Unit Tests ausführen
```bash
pytest tests/
```

### Mit Coverage
```bash
pytest --cov=app tests/
```

### Integration Tests
```bash
pytest tests/test_integration.py
```

## Manuelle Test-Checkliste

### ✅ Basis-Funktionalität
- [ ] Registrierung und Login funktioniert
- [ ] JWT-Token wird korrekt gespeichert
- [ ] Navigation zwischen Seiten funktioniert

### ✅ Portfolio-Management
- [ ] Transaktionen können hinzugefügt werden
- [ ] Portfolio-Übersicht zeigt korrekte Werte
- [ ] Performance-Berechnung ist korrekt
- [ ] Diversifikation wird angezeigt

### ✅ Watchlist
- [ ] Aktien können hinzugefügt/entfernt werden
- [ ] Preise werden aktualisiert
- [ ] Tags und Notizen funktionieren

### ✅ Screener
- [ ] Filter funktionieren korrekt
- [ ] Preset-Strategien laden
- [ ] Ergebnisse werden angezeigt
- [ ] Aktien können zur Watchlist hinzugefügt werden

### ✅ Alerts
- [ ] Alerts können erstellt werden
- [ ] Alert-Bedingungen werden geprüft
- [ ] Benachrichtigungen funktionieren

### ✅ PWA-Features
- [ ] App kann installiert werden
- [ ] Offline-Modus funktioniert
- [ ] Service Worker cached Assets

## Deployment

### Production mit Docker

1. **Production .env konfigurieren**
```bash
FLASK_ENV=production
SECRET_KEY=<strong-secret-key>
DATABASE_URL=postgresql://...
```

2. **Docker Images bauen**
```bash
docker-compose build
```

3. **Services starten**
```bash
docker-compose up -d
```

4. **SSL/TLS konfigurieren** (empfohlen)
- Certbot für Let's Encrypt
- Nginx SSL-Konfiguration anpassen

### Monitoring

- Logs: `docker-compose logs -f web`
- Metriken: Integration mit Prometheus/Grafana möglich
- Health-Check: `http://localhost:5000/health`

## Sicherheit

### Best Practices implementiert
- JWT-basierte Authentifizierung
- Passwort-Hashing mit bcrypt
- CORS-Konfiguration
- SQL-Injection-Schutz durch SQLAlchemy
- XSS-Schutz durch Template-Escaping
- Rate-Limiting vorbereitet

### Empfohlene Produktions-Einstellungen
- Starke SECRET_KEY verwenden
- HTTPS aktivieren
- Content Security Policy setzen
- Regular Security Updates

## Mitwirken

Contributions sind willkommen! Bitte erstellen Sie einen Pull Request mit:
- Klarer Beschreibung der Änderungen
- Tests für neue Features
- Dokumentation-Updates

## Lizenz

MIT License - siehe LICENSE Datei

## Support

Bei Fragen oder Problemen bitte ein Issue erstellen.

---

**Entwickelt mit ❤️ für datengetriebene Investoren**