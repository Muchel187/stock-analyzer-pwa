"""
Short Squeeze Analyzer - Advanced analysis for short squeeze potential
Uses multiple signals and indicators to assess squeeze likelihood
"""
import logging
from typing import Dict, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class ShortSqueezeAnalyzer:
    """Analyzes short squeeze potential based on various market indicators"""

    @classmethod
    def analyze_squeeze_potential(cls,
                                 stock_data: Dict,
                                 technical_data: Dict = None,
                                 volume_data: Dict = None) -> Dict:
        """
        Analyze short squeeze potential using available data

        Args:
            stock_data: Basic stock information
            technical_data: Technical indicators (RSI, MACD, etc.)
            volume_data: Volume and price history

        Returns:
            Dictionary with squeeze analysis
        """
        try:
            score = 0
            factors = []
            signals = []

            # 1. Technical Indicators Analysis (0-25 points)
            if technical_data:
                # RSI Analysis
                rsi = technical_data.get('rsi')
                if rsi:
                    if rsi > 70:
                        score += 10
                        factors.append(f"Overbought RSI ({rsi:.1f}) - shorts may cover")
                    elif rsi < 30:
                        score += 5
                        factors.append(f"Oversold RSI ({rsi:.1f}) - potential reversal")

                # MACD Analysis
                macd_data = technical_data.get('macd', {})
                if macd_data:
                    macd = macd_data.get('macd_line', 0)
                    signal = macd_data.get('signal_line', 0)
                    if macd > signal and macd > 0:
                        score += 10
                        signals.append("Bullish MACD crossover")

                # Bollinger Bands
                bb = technical_data.get('bollinger_bands', {})
                if bb:
                    current = stock_data.get('current_price', 0)
                    upper = bb.get('upper', 0)
                    lower = bb.get('lower', 0)
                    if current and upper and current > upper:
                        score += 5
                        signals.append("Price above upper Bollinger Band")

            # 2. Price Movement Analysis (0-25 points)
            if stock_data:
                # Check recent price momentum
                price_change_1m = stock_data.get('price_change_1m', 0)
                price_change_1w = stock_data.get('price_change_1w', 0)

                if price_change_1m and price_change_1m > 20:
                    score += 15
                    factors.append(f"Strong monthly momentum: +{price_change_1m:.1f}%")
                elif price_change_1m and price_change_1m > 10:
                    score += 10
                    factors.append(f"Positive monthly momentum: +{price_change_1m:.1f}%")

                if price_change_1w and price_change_1w > 10:
                    score += 10
                    signals.append(f"Weekly surge: +{price_change_1w:.1f}%")

            # 3. Volume Analysis (0-25 points)
            if stock_data.get('volume'):
                volume = stock_data['volume']
                avg_volume = stock_data.get('avg_volume_10d', volume)

                if avg_volume and volume > avg_volume * 2:
                    score += 15
                    factors.append(f"Volume spike: {(volume/avg_volume):.1f}x average")
                    signals.append("Unusual volume activity")
                elif avg_volume and volume > avg_volume * 1.5:
                    score += 10
                    factors.append(f"Elevated volume: {(volume/avg_volume):.1f}x average")

            # 4. Market Cap and Float Analysis (0-25 points)
            market_cap = stock_data.get('market_cap', 0)
            if market_cap:
                if market_cap < 1_000_000_000:  # Small cap < $1B
                    score += 15
                    factors.append("Small cap stock - higher squeeze potential")
                elif market_cap < 5_000_000_000:  # Mid cap < $5B
                    score += 10
                    factors.append("Mid cap stock - moderate squeeze potential")
                else:
                    score += 5
                    factors.append("Large cap stock - lower squeeze potential")

            # 5. Volatility Analysis
            volatility = technical_data.get('volatility') if technical_data else None
            if volatility:
                if volatility > 0.5:  # 50% annualized volatility
                    score += 10
                    factors.append(f"High volatility: {volatility*100:.1f}%")
                    signals.append("Volatile trading conditions")

            # Determine squeeze level based on score
            if score >= 80:
                level = "EXTREME"
                description = "Extreme short squeeze potential - Multiple strong signals present"
                risk_level = 95
            elif score >= 60:
                level = "HIGH"
                description = "High short squeeze potential - Several positive indicators"
                risk_level = 75
            elif score >= 40:
                level = "MODERATE"
                description = "Moderate short squeeze potential - Some favorable conditions"
                risk_level = 50
            elif score >= 20:
                level = "LOW"
                description = "Low short squeeze potential - Limited signals"
                risk_level = 25
            else:
                level = "MINIMAL"
                description = "Minimal short squeeze potential - No significant indicators"
                risk_level = 10

            # Add recommendations based on level
            recommendations = cls._get_squeeze_recommendations(level, factors)

            return {
                'score': score,
                'risk_level': risk_level,
                'level': level,
                'description': description,
                'factors': factors,
                'signals': signals,
                'recommendations': recommendations,
                'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                'note': 'Analysis based on technical indicators and market dynamics. Actual short interest data from ChartExchange.com would improve accuracy.'
            }

        except Exception as e:
            logger.error(f"Error analyzing squeeze potential: {str(e)}")
            return {
                'score': 0,
                'risk_level': 0,
                'level': "UNKNOWN",
                'description': "Unable to analyze squeeze potential",
                'factors': [],
                'signals': [],
                'error': str(e)
            }

    @classmethod
    def _get_squeeze_recommendations(cls, level: str, factors: list) -> list:
        """Generate recommendations based on squeeze level"""
        recommendations = []

        if level == "EXTREME":
            recommendations.append("⚠️ EXTREME CAUTION: Very high volatility expected")
            recommendations.append("Consider taking partial profits if long")
            recommendations.append("Avoid shorting - extreme risk")
            recommendations.append("Monitor closely for rapid price movements")
        elif level == "HIGH":
            recommendations.append("High squeeze risk for short sellers")
            recommendations.append("Potential for significant upward movement")
            recommendations.append("Watch for volume spikes as confirmation")
            recommendations.append("Consider protective stops if short")
        elif level == "MODERATE":
            recommendations.append("Moderate squeeze conditions developing")
            recommendations.append("Monitor short interest updates")
            recommendations.append("Watch for catalyst events")
        elif level == "LOW":
            recommendations.append("Limited squeeze potential currently")
            recommendations.append("Monitor for changing conditions")
        else:
            recommendations.append("No significant squeeze risk detected")
            recommendations.append("Normal trading conditions")

        return recommendations