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
            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.google_api_key}"
            logger.info("Using Google Gemini AI for stock analysis")
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
                               fundamental_analysis: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Generate AI-powered analysis for a stock"""
        if not self.provider:
            logger.warning("No AI API key configured")
            return {
                'error': 'AI service not configured',
                'analysis': 'Please configure Google Gemini (GOOGLE_API_KEY) or OpenAI API key (OPENAI_API_KEY) for AI-powered analysis'
            }

        try:
            prompt = self._create_analysis_prompt(stock_data, technical_indicators, fundamental_analysis)

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
                    "temperature": 0.3,
                    "maxOutputTokens": 2048,
                }
            }

            response = requests.post(self.api_url, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                logger.error(f"Google Gemini API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error calling Google Gemini: {str(e)}")
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
                                fundamental_analysis: Dict[str, Any] = None) -> str:
        """Create a comprehensive prompt for AI analysis"""
        prompt = f"""
Analyze the following stock data for {stock_data.get('ticker', 'Unknown')} ({stock_data.get('company_name', 'Unknown Company')}):

## Current Market Data:
- Current Price: ${stock_data.get('current_price', 'N/A')}
- Market Cap: ${stock_data.get('market_cap', 'N/A'):,} if stock_data.get('market_cap') else 'N/A'
- P/E Ratio: {stock_data.get('pe_ratio', 'N/A')}
- Dividend Yield: {stock_data.get('dividend_yield', 'N/A')}
- 52-Week Range: ${stock_data.get('52_week_low', 'N/A')} - ${stock_data.get('52_week_high', 'N/A')}
- Beta: {stock_data.get('beta', 'N/A')}
"""

        if technical_indicators:
            prompt += f"""
## Technical Indicators:
- RSI: {technical_indicators.get('rsi', 'N/A')}
- MACD: {technical_indicators.get('macd', {}).get('macd', 'N/A')}
- Price Change (1 Month): {technical_indicators.get('price_change_1m', 'N/A')}%
- Volatility: {technical_indicators.get('volatility', 'N/A')}
- Volume Trend: {technical_indicators.get('volume_trend', 'N/A')}
"""

        if fundamental_analysis:
            prompt += f"""
## Fundamental Scores:
- Overall Score: {fundamental_analysis.get('overall_score', 'N/A')}/100
- Value Score: {fundamental_analysis.get('scores', {}).get('value_score', 'N/A')}/100
- Financial Health: {fundamental_analysis.get('scores', {}).get('financial_health_score', 'N/A')}/100
- Profitability: {fundamental_analysis.get('scores', {}).get('profitability_score', 'N/A')}/100
- Current Recommendation: {fundamental_analysis.get('recommendation', 'N/A')}
"""

        prompt += """
Please provide a comprehensive analysis covering:
1. Technical Analysis insights
2. Fundamental Analysis evaluation
3. Key Risks to consider
4. Growth Opportunities
5. Final Investment Recommendation with reasoning
"""

        return prompt

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        sections = {
            'technical_analysis': '',
            'fundamental_analysis': '',
            'risks': '',
            'opportunities': '',
            'recommendation': '',
            'summary': ''
        }

        current_section = None
        lines = response_text.split('\n')

        for line in lines:
            line_lower = line.lower().strip()

            if 'technical analysis' in line_lower:
                current_section = 'technical_analysis'
            elif 'fundamental analysis' in line_lower:
                current_section = 'fundamental_analysis'
            elif 'risk' in line_lower:
                current_section = 'risks'
            elif 'opportunit' in line_lower:
                current_section = 'opportunities'
            elif 'recommendation' in line_lower:
                current_section = 'recommendation'
            elif current_section:
                sections[current_section] += line + '\n'

        # Create summary if not present
        if not sections['summary']:
            sections['summary'] = sections['recommendation'][:200] if sections['recommendation'] else 'Analysis completed'

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