# 🤖 AI-Integration Setup - Google Gemini & OpenAI

## Übersicht

Die Stock Analyzer App unterstützt **zwei AI-Provider** für intelligente Aktienanalyse:

1. **Google Gemini AI** (empfohlen - kostenlos)
2. **OpenAI GPT-4** (kostenpflichtig)

Die App verwendet **automatisch** den konfigurierten Provider (Google Gemini wird bevorzugt, falls beide Keys vorhanden sind).

---

## Option 1: Google Gemini AI (Empfohlen - Kostenlos)

### Vorteile
- ✅ **Komplett kostenlos** mit großzügigem Free Tier
- ✅ 60 Anfragen pro Minute
- ✅ Sehr schnelle Antwortzeiten
- ✅ Mehrsprachig (Deutsch & Englisch)
- ✅ Keine Kreditkarte erforderlich

### Setup-Schritte

1. **Google AI Studio öffnen**
   - Gehen Sie zu: https://makersuite.google.com/app/apikey
   - Oder: https://aistudio.google.com/

2. **API Key erstellen**
   - Klicken Sie auf "Create API Key"
   - Wählen Sie Ihr Google Cloud Projekt (oder erstellen Sie ein neues)
   - Kopieren Sie den API Key

3. **API Key in .env eintragen**
   ```bash
   # Öffnen Sie /home/jbk/Aktienanalyse/.env
   GOOGLE_API_KEY=IHR_GOOGLE_API_KEY_HIER
   ```

4. **Server neu starten**
   ```bash
   cd /home/jbk/Aktienanalyse
   source venv/bin/activate
   python app.py
   ```

### Testen

```bash
curl -X POST http://127.0.0.1:5000/api/stock/analyze-with-ai \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

---

## Option 2: OpenAI GPT-4 (Kostenpflichtig)

### Vorteile
- ✅ Sehr detaillierte Analysen
- ✅ Ausgereifte Technologie
- ⚠️ Kostenpflichtig (~$0.03 pro Analyse)

### Setup-Schritte

1. **OpenAI Account erstellen**
   - Gehen Sie zu: https://platform.openai.com/signup

2. **API Key erstellen**
   - Navigieren Sie zu: https://platform.openai.com/api-keys
   - Klicken Sie auf "Create new secret key"
   - Kopieren Sie den Key (beginnt mit `sk-...`)

3. **Billing einrichten**
   - Fügen Sie eine Zahlungsmethode hinzu
   - Minimum: $5 Guthaben

4. **API Key in .env eintragen**
   ```bash
   # Öffnen Sie /home/jbk/Aktienanalyse/.env
   OPENAI_API_KEY=sk-IHR_OPENAI_KEY_HIER
   ```

5. **Server neu starten**

---

## Aktuelle Konfiguration

Ihre `.env` Datei:

```bash
# AI-Integration (wählen Sie einen Provider)

# Option 1: Google Gemini (kostenlos, empfohlen)
GOOGLE_API_KEY=

# Option 2: OpenAI GPT-4 (kostenpflichtig)
# OPENAI_API_KEY=sk-...
```

---

## Features der AI-Analyse

Die AI-Integration bietet:

### 1. **Stock Analysis** (`/api/stock/analyze-with-ai`)
- ✅ Technische Analyse (RSI, MACD, Trend)
- ✅ Fundamentalanalyse (P/E, Bewertung, Finanzen)
- ✅ Risikobewertung
- ✅ Chancen & Katalysatoren
- ✅ Investmentempfehlung (Buy/Hold/Sell)
- ✅ Confidence Score

**Beispiel Request:**
```json
POST /api/stock/analyze-with-ai
{
  "ticker": "AAPL"
}
```

**Beispiel Response:**
```json
{
  "ticker": "AAPL",
  "provider": "google",
  "ai_analysis": {
    "technical_analysis": "Strong uptrend with RSI at 82...",
    "fundamental_analysis": "Fair valuation with P/E of 28...",
    "risks": "Market volatility, regulatory concerns...",
    "opportunities": "iPhone 16 launch, AI integration...",
    "recommendation": "BUY - Target price $280"
  },
  "confidence_score": 85.5
}
```

### 2. **Market Insights** (zukünftig)
- Marktüberblick
- Sektoranalyse
- Trendidentifikation

---

## Kosten-Vergleich

| Provider | Kosten | Anfragen/Tag | Empfehlung |
|----------|--------|--------------|------------|
| **Google Gemini** | Kostenlos | ~10.000+ | ✅ Für Entwicklung & Produktion |
| **OpenAI GPT-4** | ~$0.03/Analyse | Unbegrenzt | Für Enterprise mit Budget |

---

## Fehlerbehebung

### "AI service not configured"
- ✅ Prüfen Sie, ob `GOOGLE_API_KEY` oder `OPENAI_API_KEY` in `.env` gesetzt ist
- ✅ Server neu starten nach Änderungen

### "Google Gemini API error: 400"
- ✅ API Key korrekt kopiert? (keine Leerzeichen)
- ✅ API in Google Cloud Console aktiviert?
- ✅ Projekt korrekt ausgewählt?

### "OpenAI API error: 401"
- ✅ Billing eingerichtet?
- ✅ API Key gültig?
- ✅ Guthaben vorhanden?

### Server-Logs prüfen
```bash
# Im laufenden Server sehen Sie:
"Using Google Gemini AI for stock analysis"  # ✅ Google aktiv
"Using OpenAI for stock analysis"            # ✅ OpenAI aktiv
"No AI API key configured"                    # ⚠️ Kein Key
```

---

## Best Practices

### Für Entwicklung (kostenlos)
```bash
GOOGLE_API_KEY=your_key_here
```

### Für Produktion mit hohem Traffic
```bash
# Nutzen Sie beide als Fallback
GOOGLE_API_KEY=your_google_key
OPENAI_API_KEY=sk-your_openai_key

# Die App nutzt automatisch Google, falls bei OpenAI ein Error auftritt
```

---

## Beispiel: Vollständige Integration testen

```bash
# 1. Google Gemini Key setzen
echo "GOOGLE_API_KEY=AIza..." >> .env

# 2. Server neustarten
source venv/bin/activate
python app.py

# 3. Im Browser öffnen
# http://127.0.0.1:5000
# Gehen Sie zu "Analyse" → Ticker eingeben → "Analysieren"

# 4. Oder via API:
curl -X POST http://127.0.0.1:5000/api/stock/analyze-with-ai \
  -H "Content-Type: application/json" \
  -d '{"ticker": "MSFT"}' | python3 -m json.tool
```

---

## Zusammenfassung

✅ **Empfohlen:** Google Gemini (kostenlos, leistungsstark)
✅ **.env konfigurieren:** `GOOGLE_API_KEY=...`
✅ **Server neustarten**
✅ **Testen:** Analyse-Seite öffnen

**Status:** Die App ist bereit für AI-Integration - Sie müssen nur noch Ihren Google API Key eintragen! 🚀
