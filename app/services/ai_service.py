import os
import json
import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-enhanced stock analysis using OpenAI or Google Gemini API"""

    def __init__(self):
        # Check for Google Gemini API first, then OpenAI
        self.google_api_key = os.environ.get('GOOGLE_API_KEY')
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')

        if self.google_api_key:
            self.provider = 'google'
            # Using Gemini 2.5 Pro (October 2025 - production-ready, enhanced reasoning)
            # Note: Gemini 2.5 Pro is available as of October 2025 with improved analysis capabilities
            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={self.google_api_key}"
            logger.info("Using Google Gemini 2.5 Pro for stock analysis")
        elif self.openai_api_key:
            self.provider = 'openai'
            self.api_url = "https://api.openai.com/v1/chat/completions"
            self.headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            logger.info("Using OpenAI for stock analysis")
        else:
            self.provider = None
            logger.warning("No AI API key configured")

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

        try:
            prompt = self._create_analysis_prompt(stock_data, technical_indicators, fundamental_analysis, short_data, news_sentiment)

            if self.provider == 'google':
                analysis_text = self._call_google_gemini(prompt)
            else:  # openai
                analysis_text = self._call_openai(prompt)

            if not analysis_text:
                return {
                    'error': 'AI service error',
                    'analysis': 'Unable to generate AI analysis at this time'
                }

            # Parse the AI response into structured format
            structured_analysis = self._parse_ai_response(analysis_text)

            return {
                'ticker': stock_data.get('ticker'),
                'ai_analysis': structured_analysis,
                'raw_analysis': analysis_text,
                'confidence_score': self._calculate_confidence_score(stock_data, technical_indicators, fundamental_analysis),
                'provider': self.provider,
                'timestamp': None  # Will be set by the caller
            }

        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return {
                'error': 'AI service error',
                'analysis': f'Error generating analysis: {str(e)}'
            }

    def _call_google_gemini(self, prompt: str) -> Optional[str]:
        """Call Google Gemini API"""
        try:
            system_prompt = "You are an expert financial analyst providing detailed stock analysis. Provide insights in a structured format with clear sections for Technical Analysis, Fundamental Analysis, Risks, Opportunities, and a final Investment Recommendation. Be data-driven and objective."

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
                        "content": "You are an expert financial analyst providing detailed stock analysis. Provide insights in a structured format with clear sections for Technical Analysis, Fundamental Analysis, Risks, Opportunities, and a final Investment Recommendation. Be data-driven and objective."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1500
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
        ticker = stock_data.get('ticker', 'N/A')
        company = stock_data.get('company_name', 'Unknown')
        
        # Build compact data sections
        sections = []
        
        # Market data (compact)
        market = f"Price ${stock_data.get('current_price', 'N/A')}, "
        market += f"P/E {stock_data.get('pe_ratio', 'N/A')}, "
        market += f"Beta {stock_data.get('beta', 'N/A')}"
        sections.append(f"Market: {market}")
        
        # Technical (compact)
        if technical_indicators:
            tech = f"RSI {technical_indicators.get('rsi', 'N/A')}, "
            tech += f"MACD {technical_indicators.get('macd', {}).get('macd', 'N/A')}, "
            tech += f"1M Change {technical_indicators.get('price_change_1m', 'N/A')}%"
            sections.append(f"Technical: {tech}")
        
        # Fundamental (compact)
        if fundamental_analysis:
            fund = f"Score {fundamental_analysis.get('overall_score', 'N/A')}/100, "
            fund += f"Rec: {fundamental_analysis.get('recommendation', 'N/A')}"
            sections.append(f"Fundamental: {fund}")
        
        # Analyst consensus (compact)
        if stock_data.get('analyst_ratings'):
            ratings = stock_data['analyst_ratings']
            total = ratings['total_analysts']
            if total > 0:
                buy_pct = (ratings['strong_buy'] + ratings['buy']) / total * 100
                sections.append(f"Analysts: {total} total, {buy_pct:.0f}% Buy/Strong Buy")
        
        if stock_data.get('price_target') and stock_data['price_target'].get('target_mean'):
            target = stock_data['price_target']
            sections.append(f"Analyst Target: ${target['target_mean']:.2f} (Range ${target['target_low']:.2f}-${target['target_high']:.2f})")
        
        # Insider activity (compact)
        if stock_data.get('insider_transactions'):
            insider = stock_data['insider_transactions']
            signal = insider['signal']
            sections.append(f"Insiders: {signal.upper()}, Net ${insider['net_value']:,.0f} ({insider['net_shares']:,} shares)")
        
        # News sentiment (compact)
        if news_sentiment and news_sentiment.get('article_count', 0) > 0:
            sent = news_sentiment
            sections.append(f"News: {sent['overall_score']:.2f} score, {sent['sentiment_percentages']['bullish_pct']}% bullish")
        
        # Short data (compact)
        if short_data:
            short_info = f"Short Interest: {short_data.get('short_percent_of_float', 'N/A')}% float, "
            short_info += f"DTC {short_data.get('days_to_cover', 'N/A')}"
            sections.append(f"Short Data: {short_info}")
        
        # Build final comprehensive prompt
        prompt = f"""Analyze {ticker} ({company}) - Comprehensive Due Diligence Report:

DATA:
{chr(10).join(['- ' + s for s in sections])}

PROVIDE DETAILED ANALYSIS IN THE FOLLOWING 7 SECTIONS (ALL REQUIRED):

## 1. TECHNICAL ANALYSIS
- Current trend direction (bullish/bearish/neutral)
- Key support and resistance levels
- RSI interpretation (overbought/oversold?)
- MACD signals and momentum
- Optimal entry/exit points
- Volume analysis

## 2. FUNDAMENTAL ANALYSIS
- Valuation assessment (undervalued/overvalued?)
- Growth prospects and catalysts
- Profitability and margins analysis
- Balance sheet health
- Comparison with analyst consensus (if available)
- Quality of management and strategy

## 3. KEY RISKS (HAUPTRISIKEN)
List 3-5 specific major risks with detailed explanations:
- Risk 1: [Specific risk with detailed explanation]
- Risk 2: [Specific risk with detailed explanation]
- Risk 3: [Specific risk with detailed explanation]
- Risk 4: [Optional additional risk]
- Risk 5: [Optional additional risk]
Include: market risks, company-specific risks, sector headwinds, competitive threats

## 4. OPPORTUNITIES (CHANCEN)
List 3-5 specific growth opportunities with detailed explanations:
- Opportunity 1: [Specific opportunity with detailed explanation]
- Opportunity 2: [Specific opportunity with detailed explanation]
- Opportunity 3: [Specific opportunity with detailed explanation]
- Opportunity 4: [Optional additional opportunity]
- Opportunity 5: [Optional additional opportunity]
Include: growth catalysts, upcoming events, competitive advantages, market trends

## 5. PRICE TARGET
Provide 12-month price target: $XXX.XX
Justification: [Explain valuation method (DCF, P/E multiple, etc.) and key assumptions]
Upside/Downside: [Calculate exact percentage from current price ${stock_data.get('current_price', 'N/A')}]
Target Range: [Provide low/high range: $XX - $XX]

## 6. SHORT SQUEEZE POTENTIAL
Score: XX/100 (Must provide numeric score)

**Due Diligence Factors (provide ACTUAL DATA if available):**
- Freefloat: [Provide percentage or state "Limited/Low/High"]
- Short Interest: [Provide percentage of float, e.g., "25% of float"]
- Days to Cover: [Provide number, e.g., "4.5 days"]
- FTDs (Failure to Deliver): [State "Significant", "Moderate", "Low", or actual number]
- Borrowing costs: [State "High", "Moderate", "Low" with percentage if known]
- Volume spikes: [Describe recent trading activity]
- Sentiment: [Social media/retail interest: Strong Bullish/Moderate/Bearish]
- Options activity: [Mention any unusual activity]

**Analysis Explanation:**
Explain in 3-5 sentences WHY this score is justified. What specific factors make a squeeze LIKELY or UNLIKELY?
Probability: [Choose ONE: EXTREM WAHRSCHEINLICH / WAHRSCHEINLICH / MÖGLICH / UNWAHRSCHEINLICH / SEHR UNWAHRSCHEINLICH]
Reasoning: [Explain the probability assessment]

## 7. RECOMMENDATION
Clear verdict: **BUY** / **HOLD** / **SELL**

Reasoning: [Provide 4-6 sentences explaining the verdict with specific factors]
- Key factor 1
- Key factor 2
- Key factor 3

Confidence Level: [High/Medium/Low]
Time Horizon: [Short-term (0-3 months) / Medium-term (3-12 months) / Long-term (1+ years)]

Compare your analysis with analyst consensus (if available) and explain any significant differences.
Consider insider activity and news sentiment in your outlook.

IMPORTANT: You MUST provide ALL 7 sections. Do not skip any section. Use "N/A" or "Not available" if data is missing, but provide the section structure."""

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
            'short_squeeze_details': {},  # NEW: Structured short squeeze data
            'recommendation': '',
            'summary': ''
        }

        current_section = None
        lines = response_text.split('\n')
        
        # Extract short squeeze details using regex
        short_squeeze_patterns = {
            'freefloat': r'freefloat[:\s]+([0-9.]+%?|limited|low|high)',
            'short_interest': r'short\s+interest[:\s]+([0-9.]+%)',
            'days_to_cover': r'days?\s+to\s+cover[:\s]+([0-9.]+)',
            'ftd': r'ftds?[:\s]+(significant|high|low|moderate|none|[0-9,]+)',
            'borrowing_cost': r'borrowing\s+cost[:\s]+([0-9.]+%|high|low|moderate)',
            'volume_spike': r'volume\s+spike[:\s]+(yes|no|significant|moderate)',
            'sentiment': r'sentiment[:\s]+(bullish|bearish|neutral|positive|negative)',
        }

        for line in lines:
            line_lower = line.lower().strip()
            
            # Skip empty lines
            if not line_lower:
                if current_section:
                    sections[current_section] += '\n'
                continue

            # Enhanced section detection with multiple pattern matching
            
            # Section 1: Technical Analysis
            if re.search(r'(?:##\s*)?(?:1\.?|section\s+1)[:\s]*technical|^technical\s*analysis|^\*\*technical', line_lower):
                current_section = 'technical_analysis'
                continue
            
            # Section 2: Fundamental Analysis
            elif re.search(r'(?:##\s*)?(?:2\.?|section\s+2)[:\s]*fundamental|^fundamental\s*analysis|^\*\*fundamental', line_lower):
                current_section = 'fundamental_analysis'
                continue
            
            # Section 3: Key Risks (Hauptrisiken)
            elif re.search(r'(?:##\s*)?(?:3\.?|section\s+3)[:\s]*(?:key\s*)?risks|^hauptrisiken|^\*\*(?:key\s*)?risks', line_lower):
                if 'squeeze' not in line_lower:  # Exclude "Short Squeeze" from risks
                    current_section = 'risks'
                    continue
            
            # Section 4: Opportunities (Chancen)
            elif re.search(r'(?:##\s*)?(?:4\.?|section\s+4)[:\s]*opportunit|^chancen|^growth\s+opportunit|^\*\*opportunit', line_lower):
                current_section = 'opportunities'
                continue
            
            # Section 5: Price Target (Kursziel)
            elif re.search(r'(?:##\s*)?(?:5\.?|section\s+5)[:\s]*price\s*target|^kursziel|^target\s+price|^\*\*price\s*target', line_lower):
                current_section = 'price_target'
                continue
            
            # Section 6: Short Squeeze
            elif re.search(r'(?:##\s*)?(?:6\.?|section\s+6)[:\s]*short\s*squeeze|^squeeze\s*potential|^\*\*short\s*squeeze', line_lower):
                current_section = 'short_squeeze'
                continue
            
            # Section 7: Recommendation
            elif re.search(r'(?:##\s*)?(?:7\.?|section\s+7)[:\s]*recommendation|^empfehlung|^verdict|^investment\s+recommendation|^\*\*recommendation', line_lower):
                current_section = 'recommendation'
                continue
            
            # Extract short squeeze details from any line
            for key, pattern in short_squeeze_patterns.items():
                match = re.search(pattern, line_lower)
                if match:
                    sections['short_squeeze_details'][key] = match.group(1)
            
            # Add content to current section
            if current_section:
                # Don't add markdown headers or section titles
                if not line.strip().startswith('##') and not line.strip().startswith('#') and not line.strip().startswith('**Section'):
                    sections[current_section] += line + '\n'

        # Clean up sections - remove empty lines at start/end
        for key in sections:
            if isinstance(sections[key], str):
                sections[key] = sections[key].strip()

        # Create summary if not present
        if not sections['summary']:
            # Use first 200 chars of recommendation or first paragraph
            if sections['recommendation']:
                sections['summary'] = sections['recommendation'][:200]
            elif sections['technical_analysis']:
                sections['summary'] = sections['technical_analysis'][:200]
            else:
                sections['summary'] = 'Analysis completed'

        # Debug logging - show what was found
        logger.info(f"Parsed sections with content: {[(k, len(v) if isinstance(v, str) else len(v)) for k, v in sections.items() if v]}")
        
        # Log if key sections are missing
        for key_section in ['risks', 'opportunities', 'price_target', 'recommendation']:
            if not sections[key_section]:
                logger.warning(f"Section '{key_section}' is EMPTY - AI response may be incomplete")

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