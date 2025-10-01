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
                            <span>${data.provider === 'google' ? 'Google Gemini' : 'OpenAI GPT'}</span>
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
        const rawText = data.raw_analysis || '';
        const priceTargetSection = data.ai_analysis?.price_target || '';
        const fullText = `${rawText} ${priceTargetSection}`;

        // Try to extract price target using various patterns
        // Pattern 1: $XXX or $XX.XX
        const dollarPattern = /\$(\d+(?:\.\d{2})?)/g;
        const matches = [...fullText.matchAll(dollarPattern)];

        // Pattern 2: "target of XXX" or "target: XXX"
        const targetPattern = /(?:target|kursziel).*?(\d+(?:\.\d{2})?)/i;
        const targetMatch = fullText.match(targetPattern);

        let targetValue = null;

        if (targetMatch) {
            targetValue = parseFloat(targetMatch[1]);
        } else if (matches.length > 0) {
            // Find the most reasonable target (usually mentioned in price target section)
            const priceTargetLower = priceTargetSection.toLowerCase();
            if (priceTargetLower) {
                const targetInSection = [...priceTargetLower.matchAll(dollarPattern)];
                if (targetInSection.length > 0) {
                    targetValue = parseFloat(targetInSection[0][1]);
                }
            }
        }

        // Calculate upside if we have current price
        let upside = 0;
        if (targetValue && data.current_price) {
            upside = ((targetValue - data.current_price) / data.current_price * 100).toFixed(1);
        }

        return {
            value: targetValue ? targetValue.toFixed(2) : null,
            upside: parseFloat(upside)
        };
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

                <div class="squeeze-analysis">
                    <div class="squeeze-factors">
                        <h5>Due Diligence Faktoren:</h5>
                        ${this.extractSqueezeFactors(shortSqueezeText)}
                    </div>
                    <div class="squeeze-details">
                        <button class="details-btn" onclick="this.parentElement.parentElement.classList.toggle('expanded')">
                            <span>Details anzeigen</span>
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
     * Extract squeeze factors from text
     */
    extractSqueezeFactors(text) {
        const factors = [];

        // Check for specific factors mentioned
        if (text.toLowerCase().includes('short interest') || text.toLowerCase().includes('short %')) {
            const match = text.match(/short\s+interest.*?(\d+\.?\d*)%/i);
            if (match) {
                factors.push({
                    icon: '📊',
                    label: 'Short Interest',
                    value: match[1] + '%',
                    status: parseFloat(match[1]) > 20 ? 'high' : 'normal'
                });
            }
        }

        if (text.toLowerCase().includes('days to cover')) {
            const match = text.match(/days\s+to\s+cover.*?(\d+\.?\d*)/i);
            if (match) {
                factors.push({
                    icon: '📅',
                    label: 'Days to Cover',
                    value: match[1] + ' days',
                    status: parseFloat(match[1]) > 5 ? 'high' : 'normal'
                });
            }
        }

        if (text.toLowerCase().includes('volume') || text.toLowerCase().includes('spike')) {
            factors.push({
                icon: '📈',
                label: 'Volumen Aktivität',
                value: text.toLowerCase().includes('high') || text.toLowerCase().includes('spike') ? 'Erhöht' : 'Normal',
                status: text.toLowerCase().includes('high') || text.toLowerCase().includes('spike') ? 'high' : 'normal'
            });
        }

        if (text.toLowerCase().includes('sentiment') || text.toLowerCase().includes('retail')) {
            factors.push({
                icon: '💬',
                label: 'Retail Sentiment',
                value: text.toLowerCase().includes('strong') || text.toLowerCase().includes('high') ? 'Stark' : 'Moderat',
                status: text.toLowerCase().includes('strong') || text.toLowerCase().includes('high') ? 'high' : 'normal'
            });
        }

        if (factors.length === 0) {
            return '<p class="no-factors">Faktoren werden in der detaillierten Analyse besprochen.</p>';
        }

        return factors.map(factor => `
            <div class="squeeze-factor ${factor.status}">
                <span class="factor-icon">${factor.icon}</span>
                <div class="factor-content">
                    <div class="factor-label">${factor.label}</div>
                    <div class="factor-value">${factor.value}</div>
                </div>
            </div>
        `).join('');
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
        if (!text) return '<p class="no-data">Keine Daten verfügbar</p>';

        // Parse numbered or bulleted list
        const items = text.split(/\d+\.\s+|\*\s+|\-\s+/).filter(item => item.trim().length > 10);

        if (items.length === 0) {
            // Fallback: split by sentences
            const sentences = text.split(/\.\s+/).filter(s => s.trim().length > 20);
            return sentences.slice(0, 5).map(item => `
                <div class="insight-item">
                    <span class="insight-bullet">${type === 'risk' ? '⚠️' : '✅'}</span>
                    <span class="insight-text">${item.trim()}.</span>
                </div>
            `).join('');
        }

        return items.slice(0, 5).map(item => `
            <div class="insight-item">
                <span class="insight-bullet">${type === 'risk' ? '⚠️' : '✅'}</span>
                <span class="insight-text">${item.trim()}</span>
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
}

// Export for use in main app
window.AIAnalysisVisualizer = AIAnalysisVisualizer;
