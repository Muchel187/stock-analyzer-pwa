# Quick Start Guide - Render Deployment

## ⚡ Schnellstart für Render Deployment

### 1. Vorbereitung (lokal)
```bash
# Alle Änderungen committen
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 2. Render Account Setup
1. Gehe zu https://dashboard.render.com/
2. Melde dich mit GitHub an
3. Autorisiere Render für dein Repository

### 3. Datenbank erstellen
1. Dashboard → "New +" → "PostgreSQL"
2. Name: `aktieninspektor`
3. Database: `aktieninspektor`
4. User: `aktieninspektor_user`
5. Region: Oregon (oder nächstgelegene)
6. Plan: Free
7. Erstellen klicken

**Wichtig**: Notiere dir die Connection String!
Format: `postgresql://user:password@host/database`

### 4. Web Service erstellen
1. Dashboard → "New +" → "Web Service"
2. Wähle dein GitHub Repository: `Aktienanalyse`
3. Render erkennt automatisch die Konfiguration

**Manuelle Konfiguration** (falls nötig):
- Name: `aktieninspektor`
- Region: Oregon
- Branch: `main`
- Build Command: `./build.sh`
- Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 wsgi:app`
- Plan: Free

### 5. Environment Variables setzen

Im Render Dashboard → Dein Service → Environment:

**Pflicht-Variablen**:
```
FLASK_ENV=production
DATABASE_URL=(wird automatisch gesetzt von der Datenbank)
```

**API Keys** (mindestens einen Stock-API-Key):
```
FINNHUB_API_KEY=dein_finnhub_key
TWELVE_DATA_API_KEY=dein_twelve_data_key
ALPHA_VANTAGE_API_KEY=dein_alpha_vantage_key
GOOGLE_API_KEY=dein_google_api_key
```

**Optional**:
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=deine@email.com
MAIL_PASSWORD=dein_app_passwort
CORS_ORIGINS=*
```

### 6. Datenbank verbinden
1. Im Web Service → Settings → Environment
2. Klicke "Add Environment Variable"
3. Key: `DATABASE_URL`
4. Value: Klicke auf "From Database" dropdown
5. Wähle deine `aktieninspektor` Datenbank
6. Property: `Internal Database URL`
7. Save

### 7. Deploy starten
1. Klicke "Manual Deploy" → "Deploy latest commit"
2. Warte 3-5 Minuten
3. Beobachte die Build-Logs

**Build-Prozess**:
- ✓ Dependencies installieren
- ✓ Flask Migrations ausführen
- ✓ Gunicorn starten
- ✓ Health Check erfolgreich

### 8. Deployment testen

**Health Check**:
```bash
curl https://aktieninspektor.onrender.com/health
```

Sollte zurückgeben:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "3.0.0"
}
```

**Website öffnen**:
- Klicke auf die URL in Render Dashboard
- Format: `https://aktieninspektor.onrender.com`

### 9. Erste Schritte nach Deployment

1. **Registrieren**:
   - Öffne die Website
   - Klicke "Registrieren"
   - Erstelle deinen Account

2. **Testen**:
   - Login
   - Aktie analysieren (z.B. AAPL)
   - Watchlist hinzufügen
   - Portfolio testen

3. **Logs überwachen**:
   - Render Dashboard → Dein Service → Logs
   - Schaue auf Fehler

## 🔧 Troubleshooting

### Problem: "Application failed to start"
**Lösung**:
```
1. Logs prüfen: Dashboard → Logs
2. Oft: DATABASE_URL fehlt oder falsch
3. Überprüfe Environment Variables
```

### Problem: "Database connection failed"
**Lösung**:
```
1. Prüfe ob PostgreSQL Service läuft
2. Prüfe DATABASE_URL Format
3. Sollte mit postgresql:// (nicht postgres://) starten
```

### Problem: "Build failed"
**Lösung**:
```
1. requirements.txt prüfen
2. Python Version in runtime.txt prüfen
3. build.sh Berechtigungen: chmod +x build.sh
```

### Problem: "CORS errors"
**Lösung**:
```
1. Setze CORS_ORIGINS=* in Environment Variables
2. Oder spezifisch: CORS_ORIGINS=https://deine-domain.com
```

### Problem: "Service spins down"
**Lösung**:
```
1. Normal bei Free Plan (nach 15 Min Inaktivität)
2. Erste Request nach Spin-Down dauert 30-60 Sek
3. Upgrade zu Starter Plan ($7/mo) für 24/7
```

## 📊 Monitoring

### Render Dashboard Metriken:
- CPU Usage
- Memory Usage
- Request Rate
- Response Time

### External Monitoring (optional):
1. **UptimeRobot**: https://uptimerobot.com/
   - Kostenloser Uptime Monitoring
   - Ping alle 5 Minuten
   - Email Alerts

2. **Better Uptime**: https://betteruptime.com/
   - Umfangreiches Monitoring
   - Status Page
   - Incident Management

## 🚀 Performance Optimierungen

### 1. Redis Cache hinzufügen:
```bash
# Render Dashboard → New + → Redis
# Dann REDIS_URL in Web Service setzen
```

### 2. Gunicorn Workers anpassen:
```
# Für Starter Plan (512MB RAM):
workers = 2

# Für Professional Plan (4GB RAM):
workers = 8
```

### 3. Database Connection Pool:
```python
# Bereits konfiguriert in config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
```

## 🔐 Sicherheit

### Wichtige Punkte:
- ✅ HTTPS automatisch aktiviert (Render)
- ✅ Secure Cookies konfiguriert
- ✅ CORS geschützt
- ✅ JWT Token Authentifizierung
- ✅ Environment Variables verschlüsselt

### Nach Deployment:
1. **API Keys schützen**:
   - Nie in Code committen
   - Nur in Render Environment Variables

2. **Database Backups**:
   - Free Plan: Keine automatischen Backups
   - Paid Plan: Tägliche Backups
   - Manuell: Daten regelmäßig exportieren

3. **Access Logs**:
   - Render speichert Logs 7 Tage (Free)
   - Länger: External Logging Service

## 💰 Kosten

### Free Plan (aktuell):
- Web Service: 750h/monat (genug für 24/7)
- PostgreSQL: 1GB, 90 Tage Inaktivitätslimit
- Bandbreite: 100GB/monat
- **Kosten: $0**

### Upgrade Optionen:
- **Starter Plan**: $7/mo
  - Kein Spin-Down
  - Mehr RAM/CPU
  - Priorität Support

- **PostgreSQL Paid**: $7/mo
  - 10GB Storage
  - Automatische Backups
  - Höhere Connection Limits

## 📝 Wartung

### Regelmäßige Aufgaben:

**Wöchentlich**:
- Logs prüfen
- Performance Metriken checken
- Error Rate überwachen

**Monatlich**:
- Dependencies updaten
- Security Updates prüfen
- Database Größe prüfen

**Bei Bedarf**:
- Scale up/down
- Database Backups
- A/B Testing neuer Features

## 🔗 Nützliche Links

- **Render Docs**: https://render.com/docs
- **Flask Deployment**: https://flask.palletsprojects.com/en/latest/deploying/
- **Gunicorn Docs**: https://docs.gunicorn.org/
- **PostgreSQL on Render**: https://render.com/docs/databases

## ✅ Deployment Checklist

Vor dem Go-Live:

- [ ] Alle Environment Variables gesetzt
- [ ] Database Migrations erfolgreich
- [ ] Health Check gibt "healthy" zurück
- [ ] Login/Registration funktioniert
- [ ] Stock Analysis funktioniert
- [ ] API Keys gültig
- [ ] CORS korrekt konfiguriert
- [ ] Error Logging aktiv
- [ ] Backup Strategie definiert
- [ ] Monitoring Setup
- [ ] Custom Domain (optional)
- [ ] SSL Certificate aktiv (automatisch)

## 🎉 Fertig!

Deine App ist jetzt live auf:
**https://aktieninspektor.onrender.com**

Bei Fragen oder Problemen:
1. Render Dashboard → Support
2. GitHub Issues
3. Community Forum

Viel Erfolg! 🚀
