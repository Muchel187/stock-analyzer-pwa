import os
import json
import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-enhanced stock analysis using OpenAI or Google Gemini API"""

    def __init__(self):
        # Check for OpenAI API first (more reliable), then Google Gemini as fallback
        self.google_api_key = os.environ.get('GOOGLE_API_KEY')
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')

        if self.openai_api_key:
            self.provider = 'openai'
            self.provider_name = 'OpenAI GPT-4'
            self.api_url = "https://api.openai.com/v1/chat/completions"
            self.headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            logger.info("Using OpenAI GPT-4 for stock analysis (PRIMARY)")
        elif self.google_api_key:
            self.provider = 'google'
            self.provider_name = 'Google Gemini 2.5 Flash'
            # Using Gemini 2.5 Flash (fast and reliable)
            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.google_api_key}"
            logger.info("Using Google Gemini 2.5 Flash for stock analysis (FALLBACK)")
        else:
            self.provider = None
            self.provider_name = 'None'
            logger.warning("No AI API key configured")

    def get_stock_data_from_ai(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        AI Fallback: Get stock data from AI when all API providers are exhausted.
        The AI provides current estimates based on its training data.

        Note: This is a fallback mechanism. Data may not be real-time and should be
        used only when traditional APIs are unavailable.
        """
        if not self.provider:
            logger.warning("No AI API configured for fallback data retrieval")
            return None

        try:
            prompt = f"""You are a financial data provider. Provide the most recent available data for stock ticker {ticker.upper()}.

Return the data in the following JSON format (no additional text, just valid JSON):

{{
  "ticker": "{ticker.upper()}",
  "company_name": "Full company name",
  "current_price": <current price estimate>,
  "previous_close": <previous close>,
  "open": <today's open>,
  "day_high": <today's high>,
  "day_low": <today's low>,
  "volume": <average volume>,
  "market_cap": <market cap in millions>,
  "pe_ratio": <P/E ratio or null>,
  "dividend_yield": <dividend yield % or null>,
  "week_52_high": <52 week high>,
  "week_52_low": <52 week low>,
  "sector": "Sector name",
  "industry": "Industry name",
  "description": "Brief company description",
  "source": "AI_FALLBACK",
  "data_freshness": "Based on training data - may not be real-time",
  "historical_data": [
    {{
      "date": "YYYY-MM-DD (last 30 trading days, most recent first)",
      "open": <price>,
      "high": <price>,
      "low": <price>,
      "close": <price>,
      "volume": <volume>
    }}
  ],
  "technical_indicators": {{
    "rsi": <RSI value 0-100>,
    "macd": <MACD value>,
    "macd_signal": <MACD signal>,
    "sma_20": <20-day SMA>,
    "sma_50": <50-day SMA>,
    "sma_200": <200-day SMA>,
    "ema_12": <12-day EMA>,
    "ema_26": <26-day EMA>,
    "bollinger_upper": <upper band>,
    "bollinger_middle": <middle band>,
    "bollinger_lower": <lower band>,
    "volatility": <annualized volatility>
  }},
  "fundamental_metrics": {{
    "revenue": <annual revenue in millions>,
    "net_income": <net income in millions>,
    "earnings_per_share": <EPS>,
    "book_value": <book value per share>,
    "debt_to_equity": <D/E ratio>,
    "roe": <ROE %>,
    "profit_margin": <profit margin %>,
    "operating_margin": <operating margin %>
  }}
}}

Provide realistic estimates based on your knowledge. If you don't have data, use reasonable industry averages."""

            logger.info(f"Fetching AI fallback data for {ticker}")

            if self.provider == 'google':
                response = requests.post(
                    self.api_url,
                    json={
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "temperature": 0.1,  # Low temperature for factual data
                            "maxOutputTokens": 4096
                        }
                    },
                    timeout=60
                )
            else:  # OpenAI
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "model": "gpt-4",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                        "max_tokens": 4096
                    },
                    timeout=60
                )

            response.raise_for_status()
            data = response.json()

            # Extract response text
            if self.provider == 'google':
                response_text = data['candidates'][0]['content']['parts'][0]['text']
            else:
                response_text = data['choices'][0]['message']['content']

            # Parse JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                stock_data = json.loads(json_match.group(0))
                logger.info(f"Successfully retrieved AI fallback data for {ticker}")
                return stock_data
            else:
                logger.error(f"Could not parse JSON from AI response for {ticker}")
                return None

        except Exception as e:
            logger.error(f"Error getting AI fallback data for {ticker}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def get_historical_data_from_ai(self, ticker: str, period: str = '1mo') -> Optional[Dict[str, Any]]:
        """
        AI Fallback: Get historical price data from AI.
        Returns realistic historical data based on known patterns.
        """
        if not self.provider:
            logger.warning("No AI API configured for fallback historical data")
            return None

        try:
            # Map period to days
            period_days = {
                '1mo': 30, '3mo': 90, '6mo': 180,
                '1y': 365, '2y': 730, '5y': 1825
            }
            days = period_days.get(period, 30)

            prompt = f"""Provide historical stock price data for {ticker.upper()} for the last {days} trading days.

Return ONLY valid JSON (no markdown, no extra text):

{{
  "ticker": "{ticker.upper()}",
  "period": "{period}",
  "data": [
    {{
      "date": "YYYY-MM-DD (most recent first)",
      "open": <price>,
      "high": <price>,
      "low": <price>,
      "close": <price>,
      "volume": <volume>
    }}
    // ... {days} entries total
  ],
  "source": "AI_FALLBACK"
}}

Base the data on realistic price movements for this stock. Use your knowledge of this company's typical price range and volatility."""

            logger.info(f"Fetching AI fallback historical data for {ticker} ({period})")

            if self.provider == 'google':
                response = requests.post(
                    self.api_url,
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.1,
                            "maxOutputTokens": 8192
                        }
                    },
                    timeout=60
                )
            else:
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "model": "gpt-4",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                        "max_tokens": 8192
                    },
                    timeout=60
                )

            response.raise_for_status()
            data = response.json()

            if self.provider == 'google':
                response_text = data['candidates'][0]['content']['parts'][0]['text']
            else:
                response_text = data['choices'][0]['message']['content']

            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                historical_data = json.loads(json_match.group(0))
                logger.info(f"Successfully retrieved AI fallback historical data for {ticker}")
                return historical_data
            else:
                logger.error(f"Could not parse JSON from AI historical response for {ticker}")
                return None

        except Exception as e:
            logger.error(f"Error getting AI fallback historical data for {ticker}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def analyze_stock_with_ai(self, stock_data: Dict[str, Any],
                               technical_indicators: Dict[str, Any] = None,
                               fundamental_analysis: Dict[str, Any] = None,
                               short_data: Dict[str, Any] = None,
                               news_sentiment: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Generate AI-powered analysis for a stock with enhanced data"""
        if not self.provider:
            logger.warning("No AI API key configured")
            return {
                'error': 'AI service not configured',
                'analysis': 'Please configure Google Gemini (GOOGLE_API_KEY) or OpenAI API key (OPENAI_API_KEY) for AI-powered analysis'
            }

        # Ensure stock_data is not None and has ticker
        if not stock_data:
            logger.error("Stock data is None in AI analysis")
            return {
                'error': 'Invalid stock data',
                'analysis': 'Stock data is missing or invalid'
            }

        # Ensure we have at least a ticker
        ticker = stock_data.get('ticker', 'UNKNOWN')
        
        try:
            prompt = self._create_analysis_prompt(stock_data, technical_indicators, fundamental_analysis, short_data, news_sentiment)

            # Try primary provider (Gemini or OpenAI based on configured keys)
            if self.provider == 'google':
                analysis_text = self._call_google_gemini(prompt)

                # If Gemini fails and OpenAI is available, try OpenAI as fallback
                if not analysis_text and self.openai_api_key:
                    logger.warning(f"Gemini failed for {ticker}, trying OpenAI fallback")
                    analysis_text = self._call_openai(prompt)
                    if analysis_text:
                        # Temporarily switch provider info for this response
                        self.provider = 'openai'
                        self.provider_name = 'OpenAI GPT-4 (Fallback)'

            else:  # openai
                analysis_text = self._call_openai(prompt)

            # If all AI calls fail, use mock data
            if not analysis_text:
                logger.warning(f"All AI services failed for {ticker}, using mock analysis")
                from app.services.mock_data_service import MockDataService
                mock_result = MockDataService.get_mock_ai_analysis(ticker, stock_data)
                return mock_result

            if not analysis_text:
                return {
                    'error': 'AI service error',
                    'analysis': 'Unable to generate AI analysis at this time',
                    'ticker': ticker
                }

            # Parse the AI response into structured format
            structured_analysis = self._parse_ai_response(analysis_text)

            return {
                'ticker': ticker,
                'ai_analysis': structured_analysis,
                'raw_analysis': analysis_text,
                'confidence_score': self._calculate_confidence_score(stock_data, technical_indicators, fundamental_analysis),
                'provider': self.provider,
                'provider_name': self.provider_name,  # NEW: Human-readable name
                'timestamp': None  # Will be set by the caller
            }

        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'error': 'AI service error',
                'analysis': f'Error generating analysis: {str(e)}',
                'ticker': ticker
            }

    def _call_google_gemini(self, prompt: str) -> Optional[str]:
        """Call Google Gemini API"""
        try:
            system_prompt = """You are the world's leading financial analyst with 30+ years of experience in equity research, technical analysis, and portfolio management. You have:

- An impeccable track record of identifying market opportunities and risks
- Deep expertise in analyzing stocks across all sectors and market caps
- Mastery of both fundamental and technical analysis methodologies
- The ability to synthesize complex financial data into actionable insights
- A reputation for accuracy, objectivity, and data-driven recommendations

Your analysis is sought after by institutional investors, hedge funds, and individual investors worldwide. You provide comprehensive, structured analysis with clear sections for Technical Analysis, Fundamental Analysis, Risks, Opportunities, Price Targets, Short Squeeze Potential, and a final Investment Recommendation. You are precise, thorough, and always support your conclusions with solid evidence."""

            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"{system_prompt}\n\n{prompt}"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.4,  # Slightly higher for more creative analysis
                    "maxOutputTokens": 8192,  # Gemini 2.5 Pro supports up to 8192 tokens
                    "topP": 0.95,
                    "topK": 40
                }
            }

            response = requests.post(self.api_url, json=payload, timeout=90)

            if response.status_code == 200:
                result = response.json()

                # Enhanced error handling for different response formats
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]

                    if 'content' in candidate:
                        content = candidate['content']

                        # Check for parts
                        if 'parts' in content and len(content['parts']) > 0:
                            if 'text' in content['parts'][0]:
                                return content['parts'][0]['text']
                            else:
                                logger.error(f"No 'text' in parts: {content['parts'][0]}")
                        else:
                            logger.error(f"No 'parts' in content. Content keys: {content.keys()}")
                            logger.error(f"Full content: {content}")
                    else:
                        logger.error(f"No 'content' in candidate. Candidate keys: {candidate.keys()}")
                else:
                    logger.error(f"No candidates in result. Result keys: {result.keys()}")

                return None
            elif response.status_code == 429:
                # Rate limit hit - return None to trigger mock data fallback
                logger.warning(f"Google Gemini rate limit exceeded (429). Falling back to mock data.")
                return None
            else:
                logger.error(f"Google Gemini API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error calling Google Gemini: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    def _call_openai(self, prompt: str) -> Optional[str]:
        """Call OpenAI API"""
        try:
            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are the world's leading financial analyst with 30+ years of experience in equity research, technical analysis, and portfolio management. You have:

- An impeccable track record of identifying market opportunities and risks
- Deep expertise in analyzing stocks across all sectors and market caps
- Mastery of both fundamental and technical analysis methodologies
- The ability to synthesize complex financial data into actionable insights
- A reputation for accuracy, objectivity, and data-driven recommendations

Your analysis is sought after by institutional investors, hedge funds, and individual investors worldwide. You provide comprehensive, structured analysis with clear sections for Technical Analysis, Fundamental Analysis, Risks, Opportunities, Price Targets, Short Squeeze Potential, and a final Investment Recommendation. You are precise, thorough, and always support your conclusions with solid evidence."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.4,
                "max_tokens": 4000
            }

            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error calling OpenAI: {str(e)}")
            return None

    def _create_analysis_prompt(self, stock_data: Dict[str, Any],
                                technical_indicators: Dict[str, Any] = None,
                                fundamental_analysis: Dict[str, Any] = None,
                                short_data: Dict[str, Any] = None,
                                news_sentiment: Dict[str, Any] = None) -> str:
        """Create an optimized, compact prompt for AI analysis"""
        # Safely get ticker and company name
        ticker = stock_data.get('ticker', 'UNKNOWN') if stock_data else 'UNKNOWN'
        company = stock_data.get('company_name', 'Unknown Company') if stock_data else 'Unknown Company'
        
        # Build compact data sections
        sections = []
        
        # Market data (compact) - safely handle None values
        if stock_data:
            market = f"Price ${stock_data.get('current_price', 'N/A')}, "
            market += f"P/E {stock_data.get('pe_ratio', 'N/A')}, "
            market += f"Beta {stock_data.get('beta', 'N/A')}"
            sections.append(f"Market: {market}")
        
        # Technical (compact) - only if available
        if technical_indicators and isinstance(technical_indicators, dict):
            tech = f"RSI {technical_indicators.get('rsi', 'N/A')}, "
            macd_data = technical_indicators.get('macd', {})
            if isinstance(macd_data, dict):
                tech += f"MACD {macd_data.get('macd', 'N/A')}, "
            else:
                tech += f"MACD N/A, "
            tech += f"1M Change {technical_indicators.get('price_change_1m', 'N/A')}%"
            sections.append(f"Technical: {tech}")
        else:
            sections.append("Technical: Data unavailable")
        
        # Fundamental (compact) - only if available
        if fundamental_analysis and isinstance(fundamental_analysis, dict):
            fund = f"Score {fundamental_analysis.get('overall_score', 'N/A')}/100, "
            fund += f"Rec: {fundamental_analysis.get('recommendation', 'N/A')}"
            sections.append(f"Fundamental: {fund}")
        else:
            sections.append("Fundamental: Data unavailable")
        
        # Analyst consensus (compact) - only if available
        if stock_data and stock_data.get('analyst_ratings'):
            ratings = stock_data['analyst_ratings']
            total = ratings.get('total_analysts', 0)
            if total > 0:
                buy_pct = (ratings.get('strong_buy', 0) + ratings.get('buy', 0)) / total * 100
                sections.append(f"Analysts: {total} total, {buy_pct:.0f}% Buy/Strong Buy")
        
        if stock_data and stock_data.get('price_target'):
            target = stock_data['price_target']
            if target.get('target_mean'):
                sections.append(f"Analyst Target: ${target['target_mean']:.2f} (Range ${target.get('target_low', 'N/A')}-${target.get('target_high', 'N/A')})")
        
        # Insider activity (compact) - only if available
        if stock_data and stock_data.get('insider_transactions'):
            insider = stock_data['insider_transactions']
            signal = insider.get('signal', 'unknown')
            sections.append(f"Insiders: {signal.upper()}, Net ${insider.get('net_value', 0):,.0f} ({insider.get('net_shares', 0):,} shares)")
        
        # News sentiment (compact) - only if available
        if news_sentiment and isinstance(news_sentiment, dict) and news_sentiment.get('article_count', 0) > 0:
            sent = news_sentiment
            sections.append(f"News: {sent.get('overall_score', 0):.2f} score, {sent.get('sentiment_percentages', {}).get('bullish_pct', 0)}% bullish")
        
        # Short data (compact) - only if available
        if short_data and isinstance(short_data, dict):
            short_info = f"Short Interest: {short_data.get('short_percent_of_float', 'N/A')}% float, "
            short_info += f"DTC {short_data.get('days_to_cover', 'N/A')}"
            sections.append(f"Short Data: {short_info}")
        
        # Build final comprehensive prompt with strict formatting instructions
        prompt = f"""Analyze {ticker} ({company}) - Comprehensive Due Diligence Report:

DATA:
{chr(10).join(['- ' + s for s in sections])}

⚠️ CRITICAL INSTRUCTIONS:
- You MUST provide ALL 7 sections below
- Each section MUST contain substantial analysis (minimum 3-5 sentences)
- Use section headers EXACTLY as shown: "## 1. TECHNICAL ANALYSIS", "## 2. FUNDAMENTAL ANALYSIS", etc.
- If data is missing, provide analysis based on available information and mention data limitations
- Do NOT skip any section

PROVIDE DETAILED ANALYSIS IN THE FOLLOWING 7 SECTIONS (ALL MANDATORY):

## 1. TECHNICAL ANALYSIS
- Current trend direction (bullish/bearish/neutral) with specific evidence
- Key support and resistance levels (provide actual price levels if possible)
- RSI interpretation (currently {technical_indicators.get('rsi', 'N/A') if technical_indicators and isinstance(technical_indicators, dict) else 'N/A'} - overbought/oversold?)
- MACD signals and momentum direction
- Optimal entry/exit points based on current technicals
- Volume analysis and recent trading patterns
- Summary: Overall technical outlook (Bullish/Neutral/Bearish)
- NOTE: If technical data is limited, focus on price action and provide qualitative analysis

## 2. FUNDAMENTAL ANALYSIS
- Valuation assessment (undervalued/fairly valued/overvalued?) - explain why
- Revenue and earnings growth prospects
- Profitability metrics (margins, ROE, ROA if available)
- Balance sheet strength (debt levels, cash position)
- Competitive position in industry
- Management quality and strategic direction
- Compare with analyst consensus if available: {stock_data.get('analyst_ratings', {}).get('total_analysts', 0) if stock_data and isinstance(stock_data, dict) else 0} analysts
- Summary: Overall fundamental health (Strong/Average/Weak)

## 3. KEY RISKS (HAUPTRISIKEN) ⚠️
**You MUST list at least 3-5 specific risks with detailed explanations**

**Risk 1:** [Name of risk]
- Detailed explanation of this risk (2-3 sentences minimum)
- Potential impact on stock price
- Likelihood: High/Medium/Low

**Risk 2:** [Name of risk]
- Detailed explanation (2-3 sentences minimum)
- Potential impact
- Likelihood: High/Medium/Low

**Risk 3:** [Name of risk]
- Detailed explanation (2-3 sentences minimum)
- Potential impact
- Likelihood: High/Medium/Low

**Risk 4:** [Optional additional risk - add if relevant]
**Risk 5:** [Optional additional risk - add if relevant]

Categories to consider: market risks, company-specific risks, sector headwinds, regulatory risks, competitive threats, financial risks

## 4. OPPORTUNITIES (CHANCEN) 🚀
**You MUST list at least 3-5 specific opportunities with detailed explanations**

**Opportunity 1:** [Name of opportunity]
- Detailed explanation of this growth catalyst (2-3 sentences minimum)
- Potential positive impact on stock
- Timeframe: Near-term/Medium-term/Long-term

**Opportunity 2:** [Name of opportunity]
- Detailed explanation (2-3 sentences minimum)
- Potential impact
- Timeframe: Near-term/Medium-term/Long-term

**Opportunity 3:** [Name of opportunity]
- Detailed explanation (2-3 sentences minimum)
- Potential impact
- Timeframe: Near-term/Medium-term/Long-term

**Opportunity 4:** [Optional - add if relevant]
**Opportunity 5:** [Optional - add if relevant]

Categories to consider: growth catalysts, upcoming product launches, market expansion, M&A potential, regulatory changes, technological advantages, market trends

## 5. PRICE TARGET 🎯
**12-Month Price Target:** $XXX.XX (You MUST provide a specific number)

**Current Price:** ${stock_data.get('current_price', 'N/A') if stock_data and isinstance(stock_data, dict) else 'N/A'}

**Valuation Method:** [Explain which method you used: DCF, P/E multiple comparison, Sum-of-Parts, or combination]

**Key Assumptions:**
1. [List major assumption 1]
2. [List major assumption 2]
3. [List major assumption 3]

**Upside/Downside:** Calculate and state: "+XX%" or "-XX%" from current price

**Target Range:**
- Bear Case: $XX.XX (pessimistic scenario)
- Base Case: $XX.XX (most likely scenario)
- Bull Case: $XX.XX (optimistic scenario)

{f"**Analyst Consensus Target:** ${stock_data.get('price_target', {}).get('target_mean', 'N/A')} (Range: ${stock_data.get('price_target', {}).get('target_low', 'N/A')} - ${stock_data.get('price_target', {}).get('target_high', 'N/A')})" if stock_data and isinstance(stock_data, dict) and stock_data.get('price_target') else ""}

## 6. SHORT SQUEEZE POTENTIAL 🔥
**Squeeze Score:** XX/100 (You MUST provide a specific number from 0-100)

**Due Diligence Factors Analysis:**

**Short Interest Data:**
- **Freefloat:** {short_data.get('free_float', 'Estimated: Medium (40-60%)') if short_data and isinstance(short_data, dict) else 'Estimated: Medium (40-60%)'}
- **Short Interest:** {short_data.get('short_percent_of_float', 'Estimated: 5-15%') if short_data and isinstance(short_data, dict) else 'Estimated: 5-15%'} of float
- **Days to Cover (DTC):** {short_data.get('days_to_cover', 'Estimated: 2-4 days') if short_data and isinstance(short_data, dict) else 'Estimated: 2-4 days'}
- **Shares Shorted:** {short_data.get('short_volume', 'Not available') if short_data and isinstance(short_data, dict) else 'Not available'}

**Trading Dynamics:**
- **FTDs (Failure to Deliver):** {short_data.get('ftd_level', 'Assessment: Moderate - requires monitoring') if short_data and isinstance(short_data, dict) else 'Assessment: Moderate - requires monitoring'}
- **Borrowing Costs:** {short_data.get('borrow_fee', 'Estimated: 2-5% annually (Moderate)') if short_data and isinstance(short_data, dict) else 'Estimated: 2-5% annually (Moderate)'}
- **Recent Volume Spikes:** {short_data.get('volume_trend', 'Analyze recent 20-day volume vs. 90-day average') if short_data and isinstance(short_data, dict) else 'Analyze recent 20-day volume vs. 90-day average'}
- **Options Activity:** {short_data.get('options_flow', 'Monitor for unusual call buying or put/call ratio changes') if short_data and isinstance(short_data, dict) else 'Monitor for unusual call buying or put/call ratio changes'}

**Sentiment & Catalysts:**
- **Social Media Sentiment:** {news_sentiment.get('social_sentiment', 'Assess: Bullish/Neutral/Bearish based on Reddit, Twitter activity') if news_sentiment and isinstance(news_sentiment, dict) else 'Assess: Bullish/Neutral/Bearish based on Reddit, Twitter activity'}
- **Retail Interest Level:** {news_sentiment.get('retail_interest', 'Gauge: High/Medium/Low') if news_sentiment and isinstance(news_sentiment, dict) else 'Gauge: High/Medium/Low'}
- **Upcoming Catalysts:** List any earnings, product launches, or events that could trigger squeeze

**Squeeze Analysis Explanation:**
[Provide 4-6 sentences explaining WHY you assigned this score. What specific factors make a squeeze LIKELY or UNLIKELY? Consider: short interest level, freefloat size, recent price action, sentiment, and any ongoing short campaigns.]

**Squeeze Probability Assessment:** 
- **Verdict:** [Choose ONE and explain: EXTREM WAHRSCHEINLICH (80-100) / WAHRSCHEINLICH (60-79) / MÖGLICH (40-59) / UNWAHRSCHEINLICH (20-39) / SEHR UNWAHRSCHEINLICH (0-19)]

**Reasoning for Probability:**
[Explain in 2-3 sentences why you chose this probability level. What are the key deciding factors?]

**Trigger Events to Watch:**
1. [Event that could trigger squeeze]
2. [Event that could trigger squeeze]
3. [Event that could trigger squeeze]

## 7. INVESTMENT RECOMMENDATION 📊
**Verdict:** **[BUY / HOLD / SELL]** (You MUST choose one)

**Reasoning:**
[Provide 5-7 sentences explaining your verdict with specific factors. Reference key points from previous sections.]

**Key Decision Factors:**
1. **[Factor 1 name]:** [Explanation - why this supports your verdict]
2. **[Factor 2 name]:** [Explanation - why this supports your verdict]
3. **[Factor 3 name]:** [Explanation - why this supports your verdict]
4. **[Factor 4 name]:** [Explanation - optional]

**Confidence Level:** [High (80-100%) / Medium (50-79%) / Low (<50%)] - Explain why

**Investment Time Horizon:** 
- **Short-term (0-3 months):** [BUY/HOLD/SELL]
- **Medium-term (3-12 months):** [BUY/HOLD/SELL]
- **Long-term (1+ years):** [BUY/HOLD/SELL]

{f"**Comparison with Analyst Consensus:** {stock_data.get('analyst_ratings', {}).get('total_analysts', 'N/A')} analysts - Your view vs. Wall Street" if stock_data.get('analyst_ratings') else ""}

{f"**Insider Activity Signal:** {stock_data.get('insider_transactions', {}).get('signal', 'NEUTRAL').upper()} - Insiders have {'bought' if stock_data.get('insider_transactions', {}).get('net_shares', 0) > 0 else 'sold'} {abs(stock_data.get('insider_transactions', {}).get('net_shares', 0)):,} shares in last 6 months" if stock_data.get('insider_transactions') else ""}

{f"**News Sentiment:** {news_sentiment.get('sentiment_percentages', {}).get('bullish_pct', 'N/A')}% bullish, {news_sentiment.get('sentiment_percentages', {}).get('bearish_pct', 'N/A')}% bearish - Consider in outlook" if news_sentiment and news_sentiment.get('article_count', 0) > 0 else ""}

**Final Note:** [Summarize in 2-3 sentences your overall conviction and any important caveats]

---
⚠️ REMEMBER: ALL 7 SECTIONS MUST BE COMPLETED. This is a comprehensive analysis that investors rely on for decision-making."""

        return prompt

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured format with improved section detection"""
        import re
        
        sections = {
            'technical_analysis': '',
            'fundamental_analysis': '',
            'risks': '',
            'opportunities': '',
            'price_target': '',
            'short_squeeze': '',
            'short_squeeze_details': {},  # Structured short squeeze data
            'recommendation': '',
            'summary': ''
        }

        current_section = None
        lines = response_text.split('\n')
        
        # Extract short squeeze details using regex (case-insensitive)
        short_squeeze_patterns = {
            'freefloat': r'freefloat[:\s]+([0-9.]+%?|limited|low|medium|high|[\w\s]+%?)',
            'short_interest': r'short\s+interest[:\s]+([0-9.]+%?[\w\s]*)',
            'days_to_cover': r'days?\s+to\s+cover[:\s]+([0-9.]+[\w\s]*)',
            'ftd': r'ftds?\s*\(failure to deliver\)[:\s]+([\w\s,]+)',
            'borrowing_cost': r'borrowing\s+costs?[:\s]+([\w\s%\-.]+)',
            'volume_spike': r'(?:volume\s+spikes?|recent\s+volume)[:\s]+([\w\s,\-.]+)',
            'sentiment': r'(?:sentiment|social\s+media\s+sentiment)[:\s]+([\w\s\-/,]+)',
            'squeeze_score': r'(?:squeeze\s+score|score)[:\s]+([0-9]{1,3})/100',
            'squeeze_probability': r'probability[:\s]+([\w\s]+)',
        }

        # First pass: Extract short squeeze details from entire text (case-insensitive)
        text_lower = response_text.lower()
        for key, pattern in short_squeeze_patterns.items():
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                sections['short_squeeze_details'][key] = match.group(1).strip()
                logger.info(f"Extracted {key}: {match.group(1).strip()}")

        # Second pass: Parse sections line by line
        for line in lines:
            line_lower = line.lower().strip()
            
            # Skip empty lines
            if not line_lower:
                if current_section:
                    sections[current_section] += '\n'
                continue

            # Enhanced section detection with multiple pattern matching
            
            # Section 1: Technical Analysis
            if re.search(r'(?:##\s*)?(?:1\.?\s*|section\s+1)[:\s]*technical|^technical\s*analysis|^\*\*technical|^1\.\s*technical', line_lower):
                current_section = 'technical_analysis'
                logger.debug(f"Detected technical_analysis section at: {line[:50]}")
                continue
            
            # Section 2: Fundamental Analysis
            elif re.search(r'(?:##\s*)?(?:2\.?\s*|section\s+2)[:\s]*fundamental|^fundamental\s*analysis|^\*\*fundamental|^2\.\s*fundamental', line_lower):
                current_section = 'fundamental_analysis'
                logger.debug(f"Detected fundamental_analysis section at: {line[:50]}")
                continue
            
            # Section 3: Key Risks (Hauptrisiken) - More specific pattern
            elif re.search(r'(?:##\s*)?(?:3\.?\s*|section\s+3)[:\s]*(?:key\s*)?risks|^hauptrisiken|^\*\*(?:key\s*)?risks|^3\.\s*(?:key\s*)?risks|^key\s+risks\s*\(hauptrisiken\)', line_lower):
                # Exclude "Short Squeeze" from risks section
                if 'squeeze' not in line_lower:
                    current_section = 'risks'
                    logger.debug(f"Detected risks section at: {line[:50]}")
                    continue
            
            # Section 4: Opportunities (Chancen)
            elif re.search(r'(?:##\s*)?(?:4\.?\s*|section\s+4)[:\s]*opportunit|^chancen|^growth\s+opportunit|^\*\*opportunit|^4\.\s*opportunit|^opportunities\s*\(chancen\)', line_lower):
                current_section = 'opportunities'
                logger.debug(f"Detected opportunities section at: {line[:50]}")
                continue
            
            # Section 5: Price Target (Kursziel)
            elif re.search(r'(?:##\s*)?(?:5\.?\s*|section\s+5)[:\s]*price\s*target|^kursziel|^target\s+price|^\*\*price\s*target|^5\.\s*price\s*target', line_lower):
                current_section = 'price_target'
                logger.debug(f"Detected price_target section at: {line[:50]}")
                continue
            
            # Section 6: Short Squeeze
            elif re.search(r'(?:##\s*)?(?:6\.?\s*|section\s+6)[:\s]*short\s*squeeze|^squeeze\s*potential|^\*\*short\s*squeeze|^6\.\s*short\s*squeeze', line_lower):
                current_section = 'short_squeeze'
                logger.debug(f"Detected short_squeeze section at: {line[:50]}")
                continue
            
            # Section 7: Recommendation
            elif re.search(r'(?:##\s*)?(?:7\.?\s*|section\s+7)[:\s]*(?:investment\s+)?recommendation|^empfehlung|^verdict|^\*\*recommendation|^7\.\s*(?:investment\s+)?recommendation', line_lower):
                current_section = 'recommendation'
                logger.debug(f"Detected recommendation section at: {line[:50]}")
                continue
            
            # Add content to current section
            if current_section:
                # Don't add markdown headers or section titles to content
                if not re.match(r'^##\s*\d+\.?\s*', line.strip()) and not line.strip().startswith('#') and not line.strip().startswith('**Section'):
                    sections[current_section] += line + '\n'

        # Clean up sections - remove empty lines at start/end
        for key in sections:
            if isinstance(sections[key], str):
                sections[key] = sections[key].strip()

        # Create summary if not present
        if not sections['summary']:
            # Use first 200 chars of recommendation or first paragraph
            if sections['recommendation']:
                sections['summary'] = sections['recommendation'][:200] + '...'
            elif sections['technical_analysis']:
                sections['summary'] = sections['technical_analysis'][:200] + '...'
            else:
                sections['summary'] = 'Analysis completed. Review all sections for detailed insights.'

        # Debug logging - show what was parsed
        for section_name, content in sections.items():
            if isinstance(content, str):
                content_length = len(content)
                logger.info(f"Section '{section_name}': {content_length} chars")
                if content_length < 50 and content:
                    logger.warning(f"Section '{section_name}' is very short: {content[:100]}")
            elif isinstance(content, dict):
                logger.info(f"Section '{section_name}' details: {len(content)} items")
        
        # Log if key sections are missing or empty
        critical_sections = ['technical_analysis', 'fundamental_analysis', 'risks', 'opportunities', 'price_target', 'recommendation']
        for key_section in critical_sections:
            if not sections[key_section] or len(sections[key_section]) < 50:
                logger.error(f"⚠️ CRITICAL: Section '{key_section}' is EMPTY or TOO SHORT - AI response incomplete!")

        return sections

    def _calculate_confidence_score(self, stock_data: Dict[str, Any],
                                   technical_indicators: Dict[str, Any] = None,
                                   fundamental_analysis: Dict[str, Any] = None) -> float:
        """Calculate confidence score based on available data"""
        score = 0
        max_score = 0

        # Check data completeness
        if stock_data:
            important_fields = ['current_price', 'pe_ratio', 'market_cap', 'volume']
            for field in important_fields:
                max_score += 10
                if stock_data.get(field) is not None:
                    score += 10

        if technical_indicators:
            max_score += 30
            if technical_indicators.get('rsi') is not None:
                score += 10
            if technical_indicators.get('macd') is not None:
                score += 10
            if technical_indicators.get('volatility') is not None:
                score += 10

        if fundamental_analysis:
            max_score += 30
            if fundamental_analysis.get('overall_score') is not None:
                score += 30

        return round((score / max_score) * 100 if max_score > 0 else 0, 2)

    def generate_market_insights(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate market-wide insights using AI"""
        if not self.api_key:
            return None

        try:
            prompt = f"""
Based on the following market data, provide insights on current market conditions and trends:

Top Gainers: {market_data.get('top_gainers', [])}
Top Losers: {market_data.get('top_losers', [])}
Most Active: {market_data.get('most_active', [])}
Market Sentiment Indicators: {market_data.get('sentiment', {})}

Provide:
1. Overall market sentiment
2. Sector rotation insights
3. Key trends to watch
4. Risk factors
5. Investment opportunities
"""

            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a market analyst providing daily market insights. Be concise and actionable."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.5,
                "max_tokens": 800
            }

            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return {
                    'insights': result['choices'][0]['message']['content'],
                    'generated_at': None  # Will be set by caller
                }

        except Exception as e:
            logger.error(f"Error generating market insights: {str(e)}")

        return None