// AI Analysis Visualization Module
class AIAnalysisVisualizer {
    constructor() {
        this.radarChart = null;
        this.riskChart = null;
    }

    /**
     * Render complete AI analysis with visual components
     */
    async renderAnalysis(ticker, currentPrice = null) {
        const container = document.getElementById('ai-tab');
        container.innerHTML = '<div class="loading-spinner">KI-Analyse wird durchgeführt...</div>';

        try {
            // Fetch AI analysis using GET endpoint
            const response = await fetch(`/api/stock/${ticker}/analyze-with-ai`);
            if (!response.ok) throw new Error('AI analysis failed');

            const data = await response.json();

            // Add current price to data for upside calculation
            if (currentPrice) {
                data.current_price = currentPrice;
            }

            container.innerHTML = this.generateAnalysisHTML(data);

            // Initialize charts after DOM is ready
            setTimeout(() => {
                this.initializeCharts(data);
            }, 100);

        } catch (error) {
            console.error('AI Analysis Error:', error);
            container.innerHTML = this.generateErrorHTML();
        }
    }

    /**
     * Generate complete HTML structure
     */
    generateAnalysisHTML(data) {
        const recommendation = this.extractRecommendation(data);
        const confidence = data.confidence_score || 0;
        const priceTarget = this.extractPriceTarget(data);

        return `
            <div class="ai-analysis-container">
                <!-- Executive Summary -->
                <div class="ai-summary-card">
                    <div class="ai-summary-header">
                        <h3>📊 Due Diligence Zusammenfassung</h3>
                        <div class="ai-provider-badge">
                            <span class="provider-icon">✨</span>
                            <span>${data.provider === 'google' ? 'Google Gemini 2.5 Pro' : 'OpenAI GPT-4'}</span>
                        </div>
                    </div>

                    <div class="ai-recommendation-box ${recommendation.type}">
                        <div class="rec-icon">${recommendation.icon}</div>
                        <div class="rec-content">
                            <div class="rec-label">Empfehlung</div>
                            <div class="rec-value">${recommendation.text}</div>
                        </div>
                        ${priceTarget.value ? `
                        <div class="price-target-meter">
                            <div class="pt-label">12-Monats Kursziel</div>
                            <div class="pt-value">$${priceTarget.value}</div>
                            <div class="pt-upside ${priceTarget.upside >= 0 ? 'positive' : 'negative'}">
                                ${priceTarget.upside >= 0 ? '+' : ''}${priceTarget.upside}% Potenzial
                            </div>
                        </div>
                        ` : ''}
                        <div class="confidence-meter">
                            <div class="confidence-label">Konfidenz</div>
                            <div class="confidence-value">${confidence.toFixed(0)}%</div>
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: ${confidence}%"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Score Dashboard -->
                <div class="ai-scores-grid">
                    ${this.generateScoreCards(data)}
                </div>

                <!-- Visual Analysis Section -->
                <div class="ai-visual-section">
                    <div class="ai-card">
                        <h4>📈 Fundamentale Stärken</h4>
                        <canvas id="fundamentalRadarChart"></canvas>
                    </div>

                    <div class="ai-card">
                        <h4>⚖️ Risiko vs. Chancen</h4>
                        <canvas id="riskOpportunityChart"></canvas>
                    </div>
                </div>

                <!-- Short Squeeze Indicator -->
                ${this.generateShortSqueezeIndicator(data)}

                <!-- Squeeze Price Scenarios -->
                ${this.generateSqueezeScenariosCard(data)}

                <!-- Technical Indicators Summary -->
                <div class="ai-card">
                    <h4>📉 Technische Indikatoren</h4>
                    ${this.generateTechnicalSummary(data)}
                </div>

                <!-- Risks & Opportunities -->
                <div class="ai-insights-grid">
                    <div class="ai-card insights-card risks">
                        <h4>⚠️ Hauptrisiken</h4>
                        ${this.generateInsightsList(data.ai_analysis?.risks, 'risk')}
                    </div>

                    <div class="ai-card insights-card opportunities">
                        <h4>🎯 Chancen</h4>
                        ${this.generateInsightsList(data.ai_analysis?.opportunities, 'opportunity')}
                    </div>
                </div>

                <!-- Detailed Analysis (Collapsible) -->
                <div class="ai-card">
                    <div class="expandable-section">
                        <button class="expand-btn" onclick="this.parentElement.classList.toggle('expanded')">
                            <span>📋 Detaillierte Analyse anzeigen</span>
                            <span class="expand-icon">▼</span>
                        </button>
                        <div class="expanded-content">
                            <div class="detailed-section">
                                <h5>Technische Analyse</h5>
                                <div class="analysis-text">${this.formatAnalysisText(data.ai_analysis?.technical_analysis)}</div>
                            </div>
                            <div class="detailed-section">
                                <h5>Fundamentalanalyse</h5>
                                <div class="analysis-text">${this.formatAnalysisText(data.ai_analysis?.fundamental_analysis)}</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Timestamp -->
                <div class="ai-timestamp">
                    Analyse erstellt: ${new Date(data.timestamp).toLocaleString('de-DE')}
                </div>
            </div>
        `;
    }

    /**
     * Extract recommendation from AI response
     */
    extractRecommendation(data) {
        const rawText = data.raw_analysis?.toLowerCase() || '';
        const recSection = data.ai_analysis?.recommendation?.toLowerCase() || '';
        const summary = data.ai_analysis?.summary?.toLowerCase() || '';

        const fullText = `${rawText} ${recSection} ${summary}`;

        if (fullText.includes('buy') || fullText.includes('kaufen')) {
            return { type: 'buy', text: 'KAUFEN', icon: '📈' };
        } else if (fullText.includes('sell') || fullText.includes('verkaufen')) {
            return { type: 'sell', text: 'VERKAUFEN', icon: '📉' };
        } else {
            return { type: 'hold', text: 'HALTEN', icon: '⏸️' };
        }
    }

    /**
     * Extract price target from AI response
     */
    extractPriceTarget(data) {
        console.log('[AI] Extracting price target from data');
        
        const rawText = data.raw_analysis || '';
        const priceTargetSection = data.ai_analysis?.price_target || '';
        const recommendation = data.ai_analysis?.recommendation || '';
        const fullText = `${rawText} ${priceTargetSection} ${recommendation}`;

        console.log('[AI] Searching in text length:', fullText.length);

        // Try to extract price target using various patterns
        const patterns = [
            // Pattern 1: "target of $XXX" or "target: $XXX"
            /(?:target|kursziel).*?\$(\d+(?:\.\d{1,2})?)/i,
            // Pattern 2: "price target $XXX"
            /price\s+target.*?\$(\d+(?:\.\d{1,2})?)/i,
            // Pattern 3: "fair value $XXX"
            /fair\s+value.*?\$(\d+(?:\.\d{1,2})?)/i,
            // Pattern 4: "target price of XXX"
            /target\s+price\s+of\s+(\d+(?:\.\d{1,2})?)/i,
            // Pattern 5: Just "Kursziel: XXX"
            /kursziel.*?(\d+(?:\.\d{1,2})?)/i,
            // Pattern 6: "$XXX target"
            /\$(\d+(?:\.\d{1,2})?)\s+target/i
        ];

        let targetValue = null;

        // Try each pattern
        for (const pattern of patterns) {
            const match = fullText.match(pattern);
            if (match) {
                targetValue = parseFloat(match[1]);
                console.log('[AI] Price target found with pattern:', pattern, '→', targetValue);
                break;
            }
        }

        // Fallback: look for reasonable price values in price_target section
        if (!targetValue && priceTargetSection) {
            const dollarPattern = /\$(\d+(?:\.\d{1,2})?)/g;
            const matches = [...priceTargetSection.matchAll(dollarPattern)];
            if (matches.length > 0) {
                // Take the first reasonable value (between $1 and $10000)
                for (const match of matches) {
                    const val = parseFloat(match[1]);
                    if (val >= 1 && val <= 10000) {
                        targetValue = val;
                        console.log('[AI] Price target found in section:', targetValue);
                        break;
                    }
                }
            }
        }

        // Calculate upside if we have current price
        let upside = 0;
        if (targetValue && data.current_price) {
            upside = ((targetValue - data.current_price) / data.current_price * 100).toFixed(1);
            console.log('[AI] Calculated upside:', upside, '% (current:', data.current_price, ', target:', targetValue, ')');
        }

        const result = {
            value: targetValue ? targetValue.toFixed(2) : null,
            upside: parseFloat(upside)
        };

        console.log('[AI] Price target result:', result);
        return result;
    }

    /**
     * Generate score cards for key metrics
     */
    generateScoreCards(data) {
        const scores = [
            {
                label: 'Technisch',
                value: this.extractTechnicalScore(data),
                icon: '📊',
                color: '#3b82f6'
            },
            {
                label: 'Fundamental',
                value: this.extractFundamentalScore(data),
                icon: '💼',
                color: '#8b5cf6'
            },
            {
                label: 'Wert',
                value: this.extractValueScore(data),
                icon: '💰',
                color: '#10b981'
            },
            {
                label: 'Momentum',
                value: this.extractMomentumScore(data),
                icon: '🚀',
                color: '#f59e0b'
            }
        ];

        return scores.map(score => `
            <div class="score-card" style="--card-color: ${score.color}">
                <div class="score-icon">${score.icon}</div>
                <div class="score-content">
                    <div class="score-label">${score.label}</div>
                    <div class="score-value">${score.value}/100</div>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${score.value}%; background: ${score.color}"></div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * Generate Short Squeeze Indicator with flame animation
     */
    generateShortSqueezeIndicator(data) {
        const shortSqueezeText = data.ai_analysis?.short_squeeze || '';
        const squeezeScore = this.extractSqueezeScore(shortSqueezeText);

        if (!shortSqueezeText || squeezeScore === null) {
            return ''; // Don't show if no data
        }

        const flameLevel = this.getFlameLevel(squeezeScore);
        const explanation = this.generateSqueezeExplanation(squeezeScore, shortSqueezeText);

        return `
            <div class="short-squeeze-card">
                <div class="squeeze-header">
                    <h4>🔥 Short Squeeze Potenzial</h4>
                    <div class="squeeze-score-badge ${flameLevel.class}">
                        ${squeezeScore}/100
                    </div>
                </div>

                <div class="squeeze-visual">
                    <div class="flame-container ${flameLevel.class}">
                        ${this.generateFlames(squeezeScore)}
                        <div class="squeeze-label">${flameLevel.label}</div>
                    </div>
                </div>

                <!-- Probability Explanation -->
                <div class="squeeze-explanation">
                    <div class="explanation-header">
                        <span class="explanation-icon">💡</span>
                        <strong>Wahrscheinlichkeit & Einschätzung:</strong>
                    </div>
                    <div class="explanation-text">
                        ${explanation}
                    </div>
                </div>

                <div class="squeeze-analysis">
                    <div class="squeeze-factors">
                        <h5>📊 Due Diligence Faktoren:</h5>
                        ${this.extractSqueezeFactors(shortSqueezeText)}
                    </div>
                    <div class="squeeze-details">
                        <button class="details-btn" onclick="this.parentElement.parentElement.classList.toggle('expanded')">
                            <span>Vollständige Analyse anzeigen</span>
                            <span class="expand-icon">▼</span>
                        </button>
                        <div class="squeeze-full-text">
                            ${this.formatAnalysisText(shortSqueezeText)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Extract squeeze score from text
     */
    extractSqueezeScore(text) {
        if (!text) return null;

        // Try to find score pattern like "75/100" or "score: 75" or "risk: 75"
        const patterns = [
            /(\d+)\/100/,
            /score.*?(\d+)/i,
            /risk.*?(\d+)/i,
            /potential.*?(\d+)/i,
            /rating.*?(\d+)/i
        ];

        for (const pattern of patterns) {
            const match = text.match(pattern);
            if (match) {
                const score = parseInt(match[1]);
                if (score >= 0 && score <= 100) {
                    return score;
                }
            }
        }

        return null;
    }

    /**
     * Get flame level based on score
     */
    getFlameLevel(score) {
        if (score >= 80) {
            return { class: 'extreme', label: 'EXTREM HOCH', color: '#dc2626' };
        } else if (score >= 60) {
            return { class: 'high', label: 'HOCH', color: '#f59e0b' };
        } else if (score >= 40) {
            return { class: 'moderate', label: 'MODERAT', color: '#eab308' };
        } else if (score >= 20) {
            return { class: 'low', label: 'NIEDRIG', color: '#3b82f6' };
        } else {
            return { class: 'minimal', label: 'MINIMAL', color: '#6b7280' };
        }
    }

    /**
     * Generate flame icons based on score
     */
    generateFlames(score) {
        const flameCount = Math.ceil(score / 20); // 1-5 flames
        let flames = '';

        for (let i = 0; i < 5; i++) {
            if (i < flameCount) {
                flames += `<span class="flame active" style="animation-delay: ${i * 0.1}s;">🔥</span>`;
            } else {
                flames += `<span class="flame inactive">🔥</span>`;
            }
        }

        return `<div class="flames">${flames}</div>`;
    }

    /**
     * Generate squeeze probability explanation
     */
    generateSqueezeExplanation(score, text) {
        let probability = '';
        let reasoning = '';

        if (score >= 80) {
            probability = '🔴 <strong>EXTREM WAHRSCHEINLICH</strong>';
            reasoning = 'Alle Indikatoren deuten auf ein sehr hohes Short Squeeze Potenzial hin. Die Kombination aus hohem Short Interest, begrenztem Float und starkem Kaufdruck schafft optimale Bedingungen.';
        } else if (score >= 60) {
            probability = '🟠 <strong>WAHRSCHEINLICH</strong>';
            reasoning = 'Die meisten Faktoren unterstützen ein Short Squeeze Szenario. Short Interest und Float-Situation sind günstig, jedoch sollten Katalysatoren und Volumen beobachtet werden.';
        } else if (score >= 40) {
            probability = '🟡 <strong>MÖGLICH</strong>';
            reasoning = 'Ein Short Squeeze ist möglich, aber nicht garantiert. Einige Faktoren sind positiv, andere neutral. Es bedarf zusätzlicher Katalysatoren oder erhöhtem Kaufdruck.';
        } else if (score >= 20) {
            probability = '🔵 <strong>UNWAHRSCHEINLICH</strong>';
            reasoning = 'Die Bedingungen für einen Short Squeeze sind aktuell nicht optimal. Short Interest oder Float-Verfügbarkeit sind nicht ausreichend, oder es fehlt an Momentum.';
        } else {
            probability = '⚪ <strong>SEHR UNWAHRSCHEINLICH</strong>';
            reasoning = 'Ein Short Squeeze ist unter den aktuellen Bedingungen sehr unwahrscheinlich. Die fundamentalen Voraussetzungen (Short Interest, Float, Volumen) sind nicht gegeben.';
        }

        // Extract specific reasons from text if available
        let specificReasons = '';
        if (text.toLowerCase().includes('warum') || text.toLowerCase().includes('because') || text.toLowerCase().includes('da ')) {
            const reasonMatch = text.match(/(?:warum|because|da\s+)(.*?)(?:\.|$)/i);
            if (reasonMatch && reasonMatch[1]) {
                specificReasons = `<br><br><em>Spezifische Gründe:</em> ${reasonMatch[1].trim()}`;
            }
        }

        return `
            <div class="probability-statement">${probability}</div>
            <div class="reasoning-text">${reasoning}${specificReasons}</div>
        `;
    }

    /**
     * Extract squeeze factors from text
     */
    extractSqueezeFactors(text) {
        console.log('[AI] Extracting squeeze factors from text length:', text?.length);
        const factors = [];

        // FREEFLOAT / FLOAT
        if (text.toLowerCase().includes('float') || text.toLowerCase().includes('freefloat')) {
            const floatMatch = text.match(/(?:free\s*)?float.*?(\d+(?:\.\d+)?)\s*(?:%|prozent|percent|million|m\b)/i);
            if (floatMatch) {
                const floatValue = floatMatch[1];
                const isPercentage = /(%|prozent|percent)/.test(floatMatch[0]);
                const isMillion = /(million|m\b)/i.test(floatMatch[0]);
                
                factors.push({
                    icon: '🏦',
                    label: 'Freefloat',
                    value: isPercentage ? `${floatValue}%` : isMillion ? `${floatValue}M Aktien` : floatValue,
                    status: isPercentage && parseFloat(floatValue) < 50 ? 'high' : 'normal',
                    description: 'Verfügbare handelbare Aktien'
                });
            } else if (text.toLowerCase().includes('float')) {
                factors.push({
                    icon: '🏦',
                    label: 'Freefloat',
                    value: 'Begrenzt',
                    status: 'high',
                    description: 'Niedriger Float erhöht Squeeze-Potenzial'
                });
            }
        }

        // SHORT INTEREST / SHORT QUOTE
        if (text.toLowerCase().includes('short interest') || text.toLowerCase().includes('short %') || text.toLowerCase().includes('shortquote')) {
            const shortMatch = text.match(/short\s+(?:interest|quote|%).*?(\d+(?:\.\d+)?)\s*%/i);
            if (shortMatch) {
                const shortValue = parseFloat(shortMatch[1]);
                factors.push({
                    icon: '📊',
                    label: 'Short Interest',
                    value: `${shortValue}%`,
                    status: shortValue > 20 ? 'high' : shortValue > 10 ? 'moderate' : 'normal',
                    description: shortValue > 30 ? 'Extrem hoch!' : shortValue > 20 ? 'Sehr hoch' : shortValue > 10 ? 'Erhöht' : 'Normal'
                });
            } else if (text.toLowerCase().includes('short')) {
                // Try to find any percentage near "short"
                const nearbyPercent = text.match(/short.*?(\d+(?:\.\d+)?)\s*(?:%|prozent)/i);
                if (nearbyPercent) {
                    factors.push({
                        icon: '📊',
                        label: 'Short Interest',
                        value: `${nearbyPercent[1]}%`,
                        status: parseFloat(nearbyPercent[1]) > 20 ? 'high' : 'normal',
                        description: 'Anteil leerverkaufter Aktien'
                    });
                } else {
                    factors.push({
                        icon: '📊',
                        label: 'Short Interest',
                        value: 'Erhöht',
                        status: 'high',
                        description: 'Signifikantes Short Interest vorhanden'
                    });
                }
            }
        }

        // DAYS TO COVER
        if (text.toLowerCase().includes('days to cover') || text.toLowerCase().includes('tage bis')) {
            const daysMatch = text.match(/days\s+to\s+cover.*?(\d+(?:\.\d+)?)/i);
            if (daysMatch) {
                const days = parseFloat(daysMatch[1]);
                factors.push({
                    icon: '📅',
                    label: 'Days to Cover',
                    value: `${days} Tage`,
                    status: days > 5 ? 'high' : days > 3 ? 'moderate' : 'normal',
                    description: days > 5 ? 'Hoher Deckungsbedarf!' : 'Zeit zum Schließen von Shorts'
                });
            }
        }

        // FTD (Failure to Deliver)
        if (text.toLowerCase().includes('ftd') || text.toLowerCase().includes('failure to deliver') || text.toLowerCase().includes('lieferausfall')) {
            const ftdMatch = text.match(/ftd.*?(\d+(?:,\d+)?)\s*(?:shares|aktien|million|m\b)/i);
            if (ftdMatch) {
                factors.push({
                    icon: '⚠️',
                    label: 'FTDs',
                    value: ftdMatch[1].replace(',', '.') + (ftdMatch[0].toLowerCase().includes('million') ? 'M' : ''),
                    status: 'high',
                    description: 'Nicht gelieferte Aktien - Squeeze-Katalysator!'
                });
            } else if (text.toLowerCase().includes('ftd')) {
                factors.push({
                    icon: '⚠️',
                    label: 'FTDs',
                    value: 'Erhöht',
                    status: 'high',
                    description: 'Lieferausfälle detektiert'
                });
            }
        }

        // VOLUME / HANDELSVOLUMEN
        if (text.toLowerCase().includes('volume') || text.toLowerCase().includes('spike') || text.toLowerCase().includes('handelsvolumen')) {
            const volumeMatch = text.match(/volume.*?(\d+(?:\.\d+)?)\s*(?:million|m\b|prozent|%)/i);
            if (volumeMatch) {
                factors.push({
                    icon: '📈',
                    label: 'Handelsvolumen',
                    value: volumeMatch[0].includes('%') ? `+${volumeMatch[1]}%` : `${volumeMatch[1]}M`,
                    status: 'high',
                    description: 'Erhöhte Handelsaktivität'
                });
            } else {
                factors.push({
                    icon: '📈',
                    label: 'Volumen Aktivität',
                    value: text.toLowerCase().includes('high') || text.toLowerCase().includes('spike') || text.toLowerCase().includes('erhöht') ? 'Erhöht' : 'Normal',
                    status: text.toLowerCase().includes('high') || text.toLowerCase().includes('spike') ? 'high' : 'normal',
                    description: 'Handelsaktivität'
                });
            }
        }

        // RETAIL SENTIMENT
        if (text.toLowerCase().includes('sentiment') || text.toLowerCase().includes('retail') || text.toLowerCase().includes('social media') || text.toLowerCase().includes('reddit')) {
            factors.push({
                icon: '💬',
                label: 'Retail Sentiment',
                value: text.toLowerCase().includes('strong') || text.toLowerCase().includes('bullish') || text.toLowerCase().includes('stark') ? 'Stark Bullish' : 'Moderat',
                status: text.toLowerCase().includes('strong') || text.toLowerCase().includes('bullish') ? 'high' : 'normal',
                description: 'Kleinanleger-Stimmung'
            });
        }

        // OPTIONS ACTIVITY
        if (text.toLowerCase().includes('option') || text.toLowerCase().includes('call') || text.toLowerCase().includes('put')) {
            const callPutRatio = text.match(/(?:call|put).*?ratio.*?(\d+(?:\.\d+)?)/i);
            if (callPutRatio) {
                factors.push({
                    icon: '📑',
                    label: 'Options Aktivität',
                    value: `Ratio: ${callPutRatio[1]}`,
                    status: 'high',
                    description: 'Optionshandel-Aktivität'
                });
            } else {
                factors.push({
                    icon: '📑',
                    label: 'Options Aktivität',
                    value: text.toLowerCase().includes('unusual') || text.toLowerCase().includes('erhöht') ? 'Ungewöhnlich Hoch' : 'Erhöht',
                    status: 'high',
                    description: 'Gamma Squeeze möglich'
                });
            }
        }

        // CATALYST / KATALYSATOR
        if (text.toLowerCase().includes('catalyst') || text.toLowerCase().includes('katalysator') || text.toLowerCase().includes('announcement')) {
            factors.push({
                icon: '🎯',
                label: 'Katalysatoren',
                value: 'Vorhanden',
                status: 'high',
                description: 'News/Events als Auslöser'
            });
        }

        console.log('[AI] Extracted', factors.length, 'squeeze factors');

        if (factors.length === 0) {
            // Create generic summary from text
            return `
                <div class="due-diligence-summary">
                    <p class="no-factors-msg">
                        📋 <strong>Hinweis:</strong> Keine spezifischen Squeeze-Faktoren in der Analyse gefunden. 
                        Lesen Sie die vollständige Analyse unten für Details.
                    </p>
                </div>
            `;
        }

        return `
            <div class="squeeze-factors-grid">
                ${factors.map(factor => `
                    <div class="squeeze-factor ${factor.status}">
                        <div class="factor-header">
                            <span class="factor-icon">${factor.icon}</span>
                            <div class="factor-label">${factor.label}</div>
                        </div>
                        <div class="factor-value">${factor.value}</div>
                        <div class="factor-description">${factor.description}</div>
                    </div>
                `).join('')}
            </div>
            <div class="dd-disclaimer">
                <small>⚠️ Dies ist keine Anlageberatung. Short Squeezes sind hochriskant und unvorhersehbar. Eigene Due Diligence erforderlich.</small>
            </div>
        `;
    }

    /**
     * Generate technical indicators summary
     */
    generateTechnicalSummary(data) {
        const analysis = data.ai_analysis?.technical_analysis || '';

        // Extract key metrics from text
        const rsiMatch = analysis.match(/RSI.*?(\d+\.?\d*)/i);
        const macdMatch = analysis.match(/MACD.*?(\d+\.?\d*)/i);
        const volatilityMatch = analysis.match(/[Vv]olatility.*?(\d+\.?\d*)/i);

        const rsi = rsiMatch ? parseFloat(rsiMatch[1]) : null;
        const macd = macdMatch ? parseFloat(macdMatch[1]) : null;
        const volatility = volatilityMatch ? parseFloat(volatilityMatch[1]) : null;

        return `
            <div class="technical-indicators-grid">
                ${rsi ? `
                <div class="indicator-card">
                    <div class="indicator-label">RSI</div>
                    <div class="indicator-value ${rsi > 70 ? 'overbought' : rsi < 30 ? 'oversold' : ''}">${rsi.toFixed(1)}</div>
                    <div class="indicator-status">${rsi > 70 ? 'Überkauft' : rsi < 30 ? 'Überverkauft' : 'Neutral'}</div>
                </div>
                ` : ''}

                ${macd ? `
                <div class="indicator-card">
                    <div class="indicator-label">MACD</div>
                    <div class="indicator-value ${macd > 0 ? 'positive' : 'negative'}">${macd.toFixed(2)}</div>
                    <div class="indicator-status">${macd > 0 ? 'Bullisch' : 'Bärisch'}</div>
                </div>
                ` : ''}

                ${volatility ? `
                <div class="indicator-card">
                    <div class="indicator-label">Volatilität</div>
                    <div class="indicator-value">${(volatility * 100).toFixed(1)}%</div>
                    <div class="indicator-status">${volatility > 0.5 ? 'Hoch' : 'Normal'}</div>
                </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Generate insights list (risks or opportunities)
     */
    generateInsightsList(text, type) {
        if (!text || text.trim().length === 0) {
            return `<p class="no-data">Keine ${type === 'risk' ? 'Risiken' : 'Chancen'} identifiziert</p>`;
        }

        console.log(`[AI] Generating ${type} list from text length:`, text.length);

        // Parse numbered or bulleted list
        let items = text.split(/\d+\.\s+|\*\s+|\-\s+/).filter(item => item.trim().length > 10);

        // If no items found with delimiters, try splitting by newlines
        if (items.length === 0) {
            items = text.split(/\n/).filter(item => item.trim().length > 10);
        }

        // If still no items, split by sentences
        if (items.length === 0) {
            const sentences = text.split(/\.\s+/).filter(s => s.trim().length > 20);
            items = sentences;
        }

        console.log(`[AI] Found ${items.length} ${type} items`);

        if (items.length === 0) {
            // Last fallback: show full text
            return `
                <div class="insight-item">
                    <span class="insight-bullet">${type === 'risk' ? '⚠️' : '✅'}</span>
                    <span class="insight-text">${text.trim()}</span>
                </div>
            `;
        }

        return items.slice(0, 5).map(item => `
            <div class="insight-item">
                <span class="insight-bullet">${type === 'risk' ? '⚠️' : '✅'}</span>
                <span class="insight-text">${item.trim().replace(/\.$/, '')}${item.trim().endsWith('.') ? '' : '.'}</span>
            </div>
        `).join('');
    }

    /**
     * Format analysis text with paragraphs
     */
    formatAnalysisText(text) {
        if (!text) return '<p>Keine Analyse verfügbar</p>';

        // Split into paragraphs and format
        const paragraphs = text.split(/\n\n+/).filter(p => p.trim().length > 0);
        return paragraphs.map(p => `<p>${p.trim()}</p>`).join('');
    }

    /**
     * Initialize Chart.js visualizations
     */
    initializeCharts(data) {
        this.createFundamentalRadarChart(data);
        this.createRiskOpportunityChart(data);
    }

    /**
     * Create radar chart for fundamental analysis
     */
    createFundamentalRadarChart(data) {
        const canvas = document.getElementById('fundamentalRadarChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        // Destroy existing chart
        if (this.radarChart) {
            this.radarChart.destroy();
        }

        const scores = {
            'Wert': this.extractValueScore(data),
            'Wachstum': this.extractGrowthScore(data),
            'Qualität': this.extractQualityScore(data),
            'Momentum': this.extractMomentumScore(data),
            'Liquidität': this.extractLiquidityScore(data)
        };

        this.radarChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: Object.keys(scores),
                datasets: [{
                    label: 'Fundamental-Score',
                    data: Object.values(scores),
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(59, 130, 246, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(59, 130, 246, 1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            color: '#9ca3af'
                        },
                        grid: {
                            color: '#374151'
                        },
                        pointLabels: {
                            color: '#d1d5db',
                            font: {
                                size: 12
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    /**
     * Create risk vs opportunity chart
     */
    createRiskOpportunityChart(data) {
        const canvas = document.getElementById('riskOpportunityChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        // Destroy existing chart
        if (this.riskChart) {
            this.riskChart.destroy();
        }

        const risks = this.countInsights(data.ai_analysis?.risks);
        const opportunities = this.countInsights(data.ai_analysis?.opportunities);

        this.riskChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Risiken', 'Chancen'],
                datasets: [{
                    label: 'Anzahl',
                    data: [risks, opportunities],
                    backgroundColor: [
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(34, 197, 94, 0.8)'
                    ],
                    borderColor: [
                        'rgba(239, 68, 68, 1)',
                        'rgba(34, 197, 94, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                indexAxis: 'y',
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1,
                            color: '#9ca3af'
                        },
                        grid: {
                            color: '#374151'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#d1d5db'
                        },
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    // Score extraction helpers
    extractTechnicalScore(data) {
        const text = data.ai_analysis?.technical_analysis?.toLowerCase() || '';
        if (text.includes('strong') || text.includes('bullish')) return 75;
        if (text.includes('weak') || text.includes('bearish')) return 35;
        return 50;
    }

    extractFundamentalScore(data) {
        const text = data.ai_analysis?.fundamental_analysis?.toLowerCase() || '';
        const scoreMatch = text.match(/overall.*?(\d+)/i);
        if (scoreMatch) return parseInt(scoreMatch[1]);
        return 50;
    }

    extractValueScore(data) {
        const text = data.ai_analysis?.fundamental_analysis?.toLowerCase() || '';
        const scoreMatch = text.match(/value.*?(\d+)/i);
        if (scoreMatch) return parseInt(scoreMatch[1]);
        return 50;
    }

    extractGrowthScore(data) {
        const text = data.ai_analysis?.fundamental_analysis?.toLowerCase() || '';
        if (text.includes('growth') && text.includes('strong')) return 70;
        if (text.includes('growth') && text.includes('weak')) return 30;
        return 50;
    }

    extractQualityScore(data) {
        const text = data.ai_analysis?.fundamental_analysis?.toLowerCase() || '';
        const healthMatch = text.match(/health.*?(\d+)/i);
        if (healthMatch) return parseInt(healthMatch[1]);
        return 50;
    }

    extractMomentumScore(data) {
        const text = data.ai_analysis?.technical_analysis?.toLowerCase() || '';
        const rsiMatch = text.match(/rsi.*?(\d+\.?\d*)/i);
        if (rsiMatch) {
            const rsi = parseFloat(rsiMatch[1]);
            return Math.min(100, rsi);
        }
        return 50;
    }

    extractLiquidityScore(data) {
        const text = data.ai_analysis?.fundamental_analysis?.toLowerCase() || '';
        if (text.includes('liquidity') && text.includes('strong')) return 80;
        if (text.includes('liquidity') && text.includes('weak')) return 30;
        return 60;
    }

    countInsights(text) {
        if (!text) return 0;
        const items = text.split(/\d+\.\s+|\*\s+|\-\s+/).filter(item => item.trim().length > 10);
        return items.length || text.split(/\.\s+/).filter(s => s.trim().length > 20).length;
    }

    generateErrorHTML() {
        return `
            <div class="ai-error-container">
                <div class="error-icon">⚠️</div>
                <h3>KI-Analyse nicht verfügbar</h3>
                <p>Die KI-Analyse konnte nicht durchgeführt werden. Bitte überprüfen Sie Ihre API-Konfiguration.</p>
            </div>
        `;
    }

    /**
     * Generate Squeeze Price Scenarios Card
     */
    generateSqueezeScenariosCard(data) {
        // Check for squeeze analysis data
        if (!data.squeeze_analysis || !data.squeeze_analysis.price_scenarios) {
            return '';
        }

        const squeezeData = data.squeeze_analysis;
        const scenarios = squeezeData.price_scenarios.scenarios;
        const currentPrice = squeezeData.price_scenarios.current_price;
        const warning = squeezeData.price_scenarios.warning;

        if (!scenarios || scenarios.length === 0) {
            return '';
        }

        return `
            <div class="ai-card squeeze-scenarios-card">
                <h4>🎯 Short Squeeze Kursziel-Szenarien</h4>

                <div class="squeeze-warning">
                    ${warning}
                </div>

                <div class="current-price-display">
                    <span class="label">Aktueller Kurs:</span>
                    <span class="price">$${currentPrice.toFixed(2)}</span>
                </div>

                <div class="scenarios-grid">
                    ${scenarios.map((scenario, index) => `
                        <div class="scenario-card ${index === 0 ? 'conservative' : index === 1 ? 'base' : 'aggressive'}">
                            <div class="scenario-header">
                                <span class="scenario-name">${scenario.name}</span>
                                <span class="scenario-probability">${scenario.probability}</span>
                            </div>

                            <div class="scenario-target">
                                <div class="target-price">$${scenario.target_price.toFixed(2)}</div>
                                <div class="target-upside ${scenario.upside_percent > 0 ? 'positive' : 'negative'}">
                                    ${scenario.upside_percent > 0 ? '+' : ''}${scenario.upside_percent.toFixed(1)}%
                                </div>
                            </div>

                            <div class="scenario-timeframe">
                                <i class="clock-icon">⏰</i> ${scenario.timeframe}
                            </div>

                            <div class="scenario-description">
                                ${scenario.description}
                            </div>

                            <div class="scenario-triggers">
                                <div class="triggers-label">Auslöser:</div>
                                <ul>
                                    ${scenario.triggers.map(trigger => `<li>${trigger}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    `).join('')}
                </div>

                <div class="squeeze-score-summary">
                    <div class="score-label">Squeeze Score:</div>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${squeezeData.score}%">
                            ${squeezeData.score}/100
                        </div>
                    </div>
                    <div class="score-level ${squeezeData.level.toLowerCase()}">
                        ${squeezeData.level} - ${squeezeData.description}
                    </div>
                </div>

                <div class="methodology-note">
                    <i>ℹ️ ${squeezeData.price_scenarios.methodology}</i>
                </div>
            </div>
        `;
    }
}

// Export for use in main app
window.AIAnalysisVisualizer = AIAnalysisVisualizer;
