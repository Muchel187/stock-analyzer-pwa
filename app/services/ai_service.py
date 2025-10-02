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
            # Using gemini-pro-latest which is Gemini 2.5 Pro for deepest analysis
            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-latest:generateContent?key={self.google_api_key}"
            logger.info("Using Google Gemini Pro (2.5 Pro) for stock analysis")
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
                    "temperature": 0.3,
                    "maxOutputTokens": 8192,  # Increased from 2048 for comprehensive analysis
                }
            }

            response = requests.post(self.api_url, json=payload, timeout=60)

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
        """Create a comprehensive prompt for AI analysis with enhanced data"""
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

        # NEW: Analyst Consensus
        if stock_data.get('analyst_ratings'):
            ratings = stock_data['analyst_ratings']
            total = ratings['total_analysts']
            if total > 0:
                prompt += f"""
## Analyst Consensus ({ratings['period']}):
- Total Analysts: {total}
- Strong Buy: {ratings['strong_buy']} ({ratings['strong_buy']/total*100:.1f}%)
- Buy: {ratings['buy']} ({ratings['buy']/total*100:.1f}%)
- Hold: {ratings['hold']} ({ratings['hold']/total*100:.1f}%)
- Sell: {ratings['sell']} ({ratings['sell']/total*100:.1f}%)
- Strong Sell: {ratings['strong_sell']} ({ratings['strong_sell']/total*100:.1f}%)
"""

        if stock_data.get('price_target'):
            target = stock_data['price_target']
            if target['target_mean']:
                prompt += f"""
- Average Price Target: ${target['target_mean']:.2f}
- Target Range: ${target['target_low']:.2f} - ${target['target_high']:.2f}
- Number of Estimates: {target['number_analysts']}

**ANALYST COMPARISON TASK**: Compare your analysis with the analyst consensus. If your recommendation differs significantly, explain why. Are the analysts missing something, or is there information they have that supports their view?
"""

        # NEW: Insider Activity
        if stock_data.get('insider_transactions'):
            insider = stock_data['insider_transactions']
            signal_emoji = "🟢" if insider['signal'] == 'bullish' else "🔴" if insider['signal'] == 'bearish' else "⚪"
            prompt += f"""
## Insider Transactions (Last {insider['period_days']} days):
{signal_emoji} Signal: {insider['signal'].upper()}
- Shares Bought: {insider['shares_bought']:,}
- Shares Sold: {insider['shares_sold']:,}
- Net Position: {insider['net_shares']:,} shares
- Net Value: ${insider['net_value']:,.0f}
- Total Transactions: {insider['transaction_count']}

**INSIDER ACTIVITY TASK**: Interpret this insider activity. Does management show confidence in the company by buying shares, or are they selling? This can be a strong signal about the company's near-term prospects. Consider whether insiders might have information not yet public.
"""

        # NEW: News Sentiment
        if news_sentiment and news_sentiment.get('article_count', 0) > 0:
            sent = news_sentiment
            sentiment_emoji = "🟢" if sent['overall_score'] > 0.2 else "🔴" if sent['overall_score'] < -0.2 else "⚪"
            prompt += f"""
## Recent News Sentiment (Last {sent['period_days']} days):
{sentiment_emoji} Overall Score: {sent['overall_score']:.2f} (-1 to +1 scale)
- Bullish Articles: {sent['sentiment_percentages']['bullish_pct']}% ({sent['sentiment_distribution']['bullish']} articles)
- Neutral Articles: {sent['sentiment_percentages']['neutral_pct']}% ({sent['sentiment_distribution']['neutral']} articles)
- Bearish Articles: {sent['sentiment_percentages']['bearish_pct']}% ({sent['sentiment_distribution']['bearish']} articles)
- Total Articles Analyzed: {sent['article_count']}

**NEWS SENTIMENT TASK**: Consider this news sentiment in your short-term outlook (1-3 months). A highly positive sentiment can drive near-term momentum and FOMO buying, while negative sentiment may create buying opportunities or signal emerging risks. Assess whether the sentiment is justified by fundamentals or driven by hype.
"""

        prompt += """
Please provide a comprehensive analysis covering:
1. Technical Analysis insights
2. Fundamental Analysis evaluation
3. Key Risks to consider
4. Growth Opportunities
5. Price Target - Provide a 12-month price target with justification based on valuation metrics, growth prospects, and market conditions
"""

        # Add short data section if available
        if short_data:
            prompt += f"""
## SHORT INTEREST DATA (from ChartExchange.com):
- Short Interest: {short_data.get('short_interest', 'N/A')} shares
- Short % of Float: {short_data.get('short_percent_of_float', 'N/A')}%
- Days to Cover: {short_data.get('days_to_cover', 'N/A')}
- Failure to Deliver: {short_data.get('failure_to_deliver', 'N/A')} shares
- Last Updated: {short_data.get('last_updated', 'N/A')}
"""

        prompt += """
6. Short Squeeze Potential - Analyze the likelihood of a short squeeze based on:
   - Actual short interest data from ChartExchange (if available above)
   - Short interest as percentage of float (if high >20% = potential)
   - Days to cover ratio (if high >5 days = potential)
   - Failure to deliver data indicates naked shorting pressure
   - Recent price momentum and volume spikes
   - Gamma squeeze potential from options activity
   - Social media sentiment and retail interest
   Rate the short squeeze risk from 0-100 (0=no risk, 100=extreme risk) and provide specific reasoning with concrete data points
7. Final Investment Recommendation (BUY/HOLD/SELL) with clear reasoning

Format your response with clear section headings.
"""

        return prompt

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        sections = {
            'technical_analysis': '',
            'fundamental_analysis': '',
            'risks': '',
            'opportunities': '',
            'price_target': '',
            'short_squeeze': '',
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
            elif 'risk' in line_lower and 'squeeze' not in line_lower:
                current_section = 'risks'
            elif 'opportunit' in line_lower:
                current_section = 'opportunities'
            elif 'price target' in line_lower or 'kursziel' in line_lower:
                current_section = 'price_target'
            elif 'short squeeze' in line_lower or 'squeeze potential' in line_lower:
                current_section = 'short_squeeze'
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