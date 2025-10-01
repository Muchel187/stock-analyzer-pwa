# Visuelle KI-Analyse - Stock Analyzer

## Übersicht

Die visuelle KI-Analyse bietet eine professionelle Due Diligence für Aktien mit interaktiven Visualisierungen und strukturierten Insights.

## Features

### 1. Executive Summary Dashboard
- **Investment-Empfehlung**: Klare KAUFEN/HALTEN/VERKAUFEN Empfehlung mit visuellem Icon
- **Konfidenz-Score**: Anzeige der KI-Sicherheit (0-100%)
- **Provider-Badge**: Zeigt verwendeten AI-Provider (Google Gemini / OpenAI)
- **Farbcodierte Empfehlungen**:
  - 🟢 Grün für KAUFEN
  - 🟠 Orange für HALTEN
  - 🔴 Rot für VERKAUFEN

### 2. Score Dashboard
Vier Hauptmetriken mit visuellen Fortschrittsbalken:
- **📊 Technisch** (0-100): RSI, MACD, Momentum-Indikatoren
- **💼 Fundamental** (0-100): Financial Health, Profitability
- **💰 Wert** (0-100): P/E Ratio, Value Score
- **🚀 Momentum** (0-100): Price Action, Trend Strength

### 3. Visuelle Charts

#### Fundamental Radar Chart
- 5-Achsen Darstellung:
  - Wert (Value)
  - Wachstum (Growth)
  - Qualität (Quality)
  - Momentum
  - Liquidität (Liquidity)
- Interaktive Chart.js Visualisierung
- Schnelle Erfassung der fundamentalen Stärken

#### Risiko vs. Chancen Bar Chart
- Horizontales Balkendiagramm
- Vergleicht Anzahl identifizierter Risiken vs. Chancen
- Farbcodiert (Rot für Risiken, Grün für Chancen)

### 4. Technische Indikatoren Summary
Visuell aufbereitete Key Indicators:
- **RSI (Relative Strength Index)**
  - Überkauft (>70): Rot markiert
  - Überverkauft (<30): Grün markiert
  - Neutral (30-70): Standard
- **MACD (Moving Average Convergence Divergence)**
  - Bullisch (positiv): Grün
  - Bärisch (negativ): Rot
- **Volatilität**
  - Prozentuale Darstellung
  - Status: Hoch/Normal

### 5. Risiken & Chancen Listen
Zwei nebeneinander angeordnete Karten:
- **⚠️ Hauptrisiken**: Bis zu 5 wichtigste Risikofaktoren
- **🎯 Chancen**: Bis zu 5 identifizierte Wachstumschancen
- Jeder Punkt mit Bullet-Icon und formatiertem Text
- Hover-Effekte für Interaktivität

### 6. Detaillierte Analyse (Ausklappbar)
Expandable Section für Volltext-Analysen:
- **Technische Analyse**: Detaillierte Beschreibung der technischen Indikatoren
- **Fundamentalanalyse**: Ausführliche fundamentale Bewertung
- Formatierter Text mit Absätzen
- Platzsparend durch Collapse-Funktion

## Technische Implementierung

### Dateien
- `static/js/ai-analysis.js` - Hauptlogik und Rendering
- `static/css/ai-analysis.css` - Styling und Animationen
- Integration in `static/js/app.js`

### Klasse: AIAnalysisVisualizer

#### Hauptmethoden:
```javascript
// Rendert vollständige Analyse
async renderAnalysis(ticker)

// Generiert HTML-Struktur
generateAnalysisHTML(data)

// Erstellt Score-Karten
generateScoreCards(data)

// Erzeugt technische Indikatoren
generateTechnicalSummary(data)

// Generiert Insights-Listen
generateInsightsList(text, type)

// Initialisiert Charts
initializeCharts(data)
createFundamentalRadarChart(data)
createRiskOpportunityChart(data)
```

### API-Endpunkt
```
GET /api/stock/{ticker}/analyze-with-ai
```

Rückgabe:
```json
{
  "ticker": "TSLA",
  "provider": "google",
  "confidence_score": 80.0,
  "ai_analysis": {
    "technical_analysis": "...",
    "fundamental_analysis": "...",
    "risks": "...",
    "opportunities": "...",
    "recommendation": "..."
  },
  "raw_analysis": "...",
  "timestamp": "2025-10-01T18:00:00"
}
```

## Verwendung

### 1. Aktie analysieren
```javascript
const visualizer = new AIAnalysisVisualizer();
await visualizer.renderAnalysis('AAPL');
```

### 2. Im UI
1. Gehe zur **Analyse**-Seite
2. Gib Ticker-Symbol ein (z.B. TSLA, AAPL, MSFT)
3. Klicke auf **Analysieren**
4. Wechsle zum Tab **KI-Analyse**
5. Warte auf Analyse (5-10 Sekunden)

## Visuelle Design-Prinzipien

### Farbschema
- **Primary Blue**: `#3b82f6` - Technische Metriken
- **Purple**: `#8b5cf6` - Fundamental-Scores
- **Green**: `#10b981` - Positive Werte, Chancen, Kaufen
- **Red**: `#ef4444` - Risiken, Verkaufen
- **Orange**: `#f59e0b` - Halten, Warnungen
- **Gradient Background**: Purple-to-Pink für Summary Card

### Animationen
- Fade-in für Content
- Smooth transitions auf Hover
- Progress bar fill animations (0.8s ease)
- Chart rendering mit Chart.js Animationen
- Expand/Collapse mit max-height transition

### Responsive Design
- Mobile-first Ansatz
- Grid-basiertes Layout
- Flexible Spaltenanzahl basierend auf Viewport
- Touch-optimierte Interaktionen

## Score-Extraktion Algorithmen

### Technischer Score
- Analysiert RSI, MACD, Trend-Wörter
- "strong"/"bullish" → 75
- "weak"/"bearish" → 35
- Neutral → 50

### Fundamental Score
- Extrahiert Overall Score aus Text
- Regex: `/overall.*?(\d+)/i`
- Fallback: 50

### Value Score
- Extrahiert Value Score aus Text
- Regex: `/value.*?(\d+)/i`
- P/E Ratio Berücksichtigung

### Momentum Score
- Basiert auf RSI Wert
- RSI > 70 → Überkauft
- RSI < 30 → Überverkauft
- Min(100, RSI)

## Chart.js Konfiguration

### Radar Chart
```javascript
{
  type: 'radar',
  scales: {
    r: {
      beginAtZero: true,
      max: 100,
      ticks: { stepSize: 20 }
    }
  }
}
```

### Bar Chart
```javascript
{
  type: 'bar',
  indexAxis: 'y',  // Horizontal
  backgroundColor: ['#ef4444', '#22c55e']
}
```

## Error Handling

### Loading States
```html
<div class="loading-spinner">
  KI-Analyse wird durchgeführt...
</div>
```

### Error States
```html
<div class="ai-error-container">
  <div class="error-icon">⚠️</div>
  <h3>KI-Analyse nicht verfügbar</h3>
  <p>Bitte überprüfen Sie Ihre API-Konfiguration.</p>
</div>
```

### Fallbacks
- Fehlende Daten → "Keine Daten verfügbar"
- API Timeout → Error Message
- Parsing Fehler → Default Werte (Score: 50)

## Performance-Optimierungen

1. **Lazy Loading**: Charts werden erst initialisiert wenn Tab aktiv
2. **Memoization**: Ticker wird gespeichert für Tab-Wechsel
3. **Async Rendering**: Nicht-blockierendes UI Update
4. **Chart Destruction**: Alte Charts werden zerstört vor Neuinitialisierung

## Browser-Kompatibilität

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ⚠️ IE11 nicht unterstützt (Chart.js 3.x)

## Zukünftige Erweiterungen

### Geplant
- [ ] Historischer Vergleich von Analysen
- [ ] Export als PDF
- [ ] Sentiment Analyse aus News
- [ ] Peer-Vergleich Visualisierung
- [ ] Custom Score-Gewichtung
- [ ] Real-time Updates bei Markt-Öffnung

### In Entwicklung
- [ ] Machine Learning Score-Prediction
- [ ] Social Media Sentiment Integration
- [ ] Analyst Ratings Aggregation

## Support

Bei Fragen oder Problemen:
1. Überprüfe Console für JavaScript Errors
2. Stelle sicher, dass Google Gemini API Key konfiguriert ist
3. Teste mit curl: `curl http://127.0.0.1:5000/api/stock/AAPL/analyze-with-ai`
4. Prüfe Network Tab in DevTools

## Credits

- **AI Provider**: Google Gemini 2.5 Flash
- **Charting**: Chart.js 4.x
- **Icons**: Unicode Emoji
- **Design**: Material Design inspiriert
