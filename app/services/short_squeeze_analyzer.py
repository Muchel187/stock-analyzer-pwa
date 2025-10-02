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

            # Calculate squeeze price target scenarios
            current_price = stock_data.get('current_price', 0)
            price_scenarios = cls._calculate_squeeze_scenarios(
                current_price,
                score,
                level,
                technical_data
            )

            return {
                'score': score,
                'risk_level': risk_level,
                'level': level,
                'description': description,
                'factors': factors,
                'signals': signals,
                'recommendations': recommendations,
                'price_scenarios': price_scenarios,
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

    @classmethod
    def _calculate_squeeze_scenarios(cls, current_price: float, score: int,
                                    level: str, technical_data: Dict = None) -> Dict:
        """
        Calculate 3 hypothetical price target scenarios for a potential short squeeze

        Args:
            current_price: Current stock price
            score: Squeeze score (0-100)
            level: Squeeze level (MINIMAL to EXTREME)
            technical_data: Technical indicators for additional context

        Returns:
            Dictionary with 3 scenarios: Conservative, Base, Aggressive
        """
        if not current_price or current_price <= 0:
            return {
                'error': 'Invalid price data',
                'scenarios': []
            }

        try:
            # Base multipliers based on squeeze level
            level_multipliers = {
                'EXTREME': {'conservative': 1.5, 'base': 2.5, 'aggressive': 5.0},
                'HIGH': {'conservative': 1.3, 'base': 1.8, 'aggressive': 3.0},
                'MODERATE': {'conservative': 1.15, 'base': 1.4, 'aggressive': 2.0},
                'LOW': {'conservative': 1.08, 'base': 1.2, 'aggressive': 1.5},
                'MINIMAL': {'conservative': 1.03, 'base': 1.08, 'aggressive': 1.2}
            }

            multipliers = level_multipliers.get(level, level_multipliers['MINIMAL'])

            # Adjust based on technical indicators if available
            adjustment = 1.0
            if technical_data:
                # RSI factor
                rsi = technical_data.get('rsi')
                if rsi and rsi > 70:
                    adjustment *= 1.1  # Overbought - higher squeeze potential
                elif rsi and rsi < 30:
                    adjustment *= 1.2  # Oversold - bigger bounce potential

                # Volatility factor
                volatility = technical_data.get('volatility')
                if volatility and volatility > 0.5:
                    adjustment *= 1.15  # High volatility = bigger moves

            # Calculate the three scenarios
            scenarios = [
                {
                    'name': 'Konservativ',
                    'description': 'Moderater Squeeze mit teilweiser Short-Eindeckung',
                    'target_price': round(current_price * multipliers['conservative'] * adjustment, 2),
                    'upside_percent': round((multipliers['conservative'] * adjustment - 1) * 100, 1),
                    'probability': cls._get_probability(score, 'conservative'),
                    'timeframe': '1-2 Wochen',
                    'triggers': [
                        'Positive Nachrichten oder Earnings Beat',
                        'Leichter Anstieg des Kaufvolumens',
                        'Erste Welle von Short-Eindeckungen'
                    ]
                },
                {
                    'name': 'Basis-Szenario',
                    'description': 'Signifikanter Squeeze mit Momentum-Aufbau',
                    'target_price': round(current_price * multipliers['base'] * adjustment, 2),
                    'upside_percent': round((multipliers['base'] * adjustment - 1) * 100, 1),
                    'probability': cls._get_probability(score, 'base'),
                    'timeframe': '2-4 Wochen',
                    'triggers': [
                        'Starker Katalysator (Partnership, FDA-Zulassung, etc.)',
                        'Massiver Volumenanstieg (3-5x normal)',
                        'Kaskadierende Short-Eindeckungen',
                        'Social Media Momentum (Reddit, Twitter)'
                    ]
                },
                {
                    'name': 'Aggressiv',
                    'description': 'Extremer Squeeze mit parabolischer Bewegung',
                    'target_price': round(current_price * multipliers['aggressive'] * adjustment, 2),
                    'upside_percent': round((multipliers['aggressive'] * adjustment - 1) * 100, 1),
                    'probability': cls._get_probability(score, 'aggressive'),
                    'timeframe': '1-3 Monate',
                    'triggers': [
                        'Perfekter Sturm mehrerer Katalysatoren',
                        'Gamma Squeeze durch Optionen',
                        'Institutionelle FOMO-Käufe',
                        'Viraler Social Media Hype',
                        'Margin Calls bei Short-Positionen'
                    ]
                }
            ]

            # Add warning based on risk level
            warning = cls._get_scenario_warning(level)

            return {
                'current_price': current_price,
                'scenarios': scenarios,
                'warning': warning,
                'methodology': 'Szenarien basierend auf historischen Squeeze-Mustern und technischen Indikatoren'
            }

        except Exception as e:
            logger.error(f"Error calculating squeeze scenarios: {str(e)}")
            return {
                'error': str(e),
                'scenarios': []
            }

    @classmethod
    def _get_probability(cls, score: int, scenario_type: str) -> str:
        """Calculate probability for each scenario based on squeeze score"""
        if scenario_type == 'conservative':
            if score >= 80:
                return 'Hoch (70-80%)'
            elif score >= 60:
                return 'Mittel-Hoch (50-70%)'
            elif score >= 40:
                return 'Mittel (30-50%)'
            else:
                return 'Niedrig (<30%)'
        elif scenario_type == 'base':
            if score >= 80:
                return 'Mittel-Hoch (40-60%)'
            elif score >= 60:
                return 'Mittel (25-40%)'
            elif score >= 40:
                return 'Niedrig-Mittel (15-25%)'
            else:
                return 'Sehr Niedrig (<15%)'
        else:  # aggressive
            if score >= 80:
                return 'Mittel (20-35%)'
            elif score >= 60:
                return 'Niedrig (10-20%)'
            elif score >= 40:
                return 'Sehr Niedrig (5-10%)'
            else:
                return 'Minimal (<5%)'

    @classmethod
    def _get_scenario_warning(cls, level: str) -> str:
        """Get appropriate warning message based on squeeze level"""
        warnings = {
            'EXTREME': '⚠️ EXTREME WARNUNG: Sehr hohes Risiko! Diese Szenarien sind hochspekulativ. Short Squeezes können schnell verpuffen.',
            'HIGH': '⚠️ HOHE VOLATILITÄT: Signifikantes Risiko. Kurse können sich schnell in beide Richtungen bewegen.',
            'MODERATE': '⚠️ VORSICHT: Moderate Squeeze-Wahrscheinlichkeit. Szenarien sind hypothetisch.',
            'LOW': 'ℹ️ HINWEIS: Geringe Squeeze-Wahrscheinlichkeit. Szenarien sind optimistisch.',
            'MINIMAL': 'ℹ️ INFO: Minimale Squeeze-Anzeichen. Szenarien sind hochspekulativ.'
        }
        return warnings.get(level, 'Szenarien sind hypothetisch und keine Anlageberatung.')