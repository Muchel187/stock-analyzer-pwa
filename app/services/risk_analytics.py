"""
Advanced Portfolio Risk Analytics Service
Provides institutional-grade risk metrics for portfolio analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RiskAnalytics:
    """
    Professional risk analytics for portfolio management
    Implements industry-standard metrics used by institutional investors
    """

    # Risk-free rate (US Treasury 10-year, approximate)
    RISK_FREE_RATE = 0.042  # 4.2% annual

    # Trading days per year
    TRADING_DAYS = 252

    @staticmethod
    def calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float = None) -> float:
        """
        Calculate annualized Sharpe Ratio

        Sharpe Ratio = (Portfolio Return - Risk-Free Rate) / Portfolio StdDev

        Interpretation:
        - > 3.0: Excellent
        - 2.0-3.0: Very Good
        - 1.0-2.0: Good
        - 0.5-1.0: Acceptable
        - < 0.5: Poor

        Args:
            returns: Array of daily returns
            risk_free_rate: Annual risk-free rate (default: 4.2%)

        Returns:
            Annualized Sharpe Ratio
        """
        if len(returns) < 2:
            return 0.0

        if risk_free_rate is None:
            risk_free_rate = RiskAnalytics.RISK_FREE_RATE

        try:
            # Calculate excess returns (daily)
            daily_rf_rate = risk_free_rate / RiskAnalytics.TRADING_DAYS
            excess_returns = returns - daily_rf_rate

            # Annualize
            mean_excess_return = excess_returns.mean() * RiskAnalytics.TRADING_DAYS
            std_returns = excess_returns.std() * np.sqrt(RiskAnalytics.TRADING_DAYS)

            if std_returns == 0:
                return 0.0

            sharpe = mean_excess_return / std_returns
            return float(sharpe)

        except Exception as e:
            logger.error(f"Error calculating Sharpe Ratio: {e}")
            return 0.0

    @staticmethod
    def calculate_sortino_ratio(returns: np.ndarray, risk_free_rate: float = None, target_return: float = 0.0) -> float:
        """
        Calculate annualized Sortino Ratio

        Similar to Sharpe but only penalizes downside volatility
        More appropriate for asymmetric return distributions

        Sortino Ratio = (Portfolio Return - Target Return) / Downside Deviation

        Args:
            returns: Array of daily returns
            risk_free_rate: Annual risk-free rate
            target_return: Target return threshold (default: 0)

        Returns:
            Annualized Sortino Ratio
        """
        if len(returns) < 2:
            return 0.0

        if risk_free_rate is None:
            risk_free_rate = RiskAnalytics.RISK_FREE_RATE

        try:
            # Calculate downside deviation (only negative returns)
            downside_returns = returns[returns < target_return]

            if len(downside_returns) == 0:
                return float('inf')  # No downside = infinite Sortino

            downside_std = downside_returns.std() * np.sqrt(RiskAnalytics.TRADING_DAYS)

            if downside_std == 0:
                return 0.0

            mean_return = returns.mean() * RiskAnalytics.TRADING_DAYS
            sortino = (mean_return - risk_free_rate) / downside_std

            return float(sortino)

        except Exception as e:
            logger.error(f"Error calculating Sortino Ratio: {e}")
            return 0.0

    @staticmethod
    def calculate_beta(portfolio_returns: np.ndarray, market_returns: np.ndarray) -> float:
        """
        Calculate portfolio Beta vs. market

        Beta = Covariance(Portfolio, Market) / Variance(Market)

        Interpretation:
        - β > 1: More volatile than market
        - β = 1: Moves with market
        - β < 1: Less volatile than market
        - β < 0: Inversely correlated to market

        Args:
            portfolio_returns: Array of portfolio returns
            market_returns: Array of market (S&P 500) returns

        Returns:
            Portfolio Beta
        """
        if len(portfolio_returns) < 2 or len(market_returns) < 2:
            return 1.0  # Default to market beta

        if len(portfolio_returns) != len(market_returns):
            min_len = min(len(portfolio_returns), len(market_returns))
            portfolio_returns = portfolio_returns[-min_len:]
            market_returns = market_returns[-min_len:]

        try:
            # Calculate covariance and variance
            covariance_matrix = np.cov(portfolio_returns, market_returns)
            covariance = covariance_matrix[0, 1]
            market_variance = np.var(market_returns)

            if market_variance == 0:
                return 1.0

            beta = covariance / market_variance
            return float(beta)

        except Exception as e:
            logger.error(f"Error calculating Beta: {e}")
            return 1.0

    @staticmethod
    def calculate_alpha(portfolio_returns: np.ndarray, market_returns: np.ndarray,
                       beta: float = None, risk_free_rate: float = None) -> float:
        """
        Calculate portfolio Alpha (Jensen's Alpha)

        Alpha = Portfolio Return - [Risk-Free Rate + Beta * (Market Return - Risk-Free Rate)]

        Interpretation:
        - α > 0: Outperforming (generating excess returns)
        - α = 0: Performing as expected
        - α < 0: Underperforming

        Args:
            portfolio_returns: Array of portfolio returns
            market_returns: Array of market returns
            beta: Portfolio beta (calculated if not provided)
            risk_free_rate: Annual risk-free rate

        Returns:
            Annualized Alpha
        """
        if len(portfolio_returns) < 2 or len(market_returns) < 2:
            return 0.0

        if risk_free_rate is None:
            risk_free_rate = RiskAnalytics.RISK_FREE_RATE

        if beta is None:
            beta = RiskAnalytics.calculate_beta(portfolio_returns, market_returns)

        try:
            # Annualize returns
            portfolio_return = portfolio_returns.mean() * RiskAnalytics.TRADING_DAYS
            market_return = market_returns.mean() * RiskAnalytics.TRADING_DAYS

            # CAPM expected return
            expected_return = risk_free_rate + beta * (market_return - risk_free_rate)

            # Alpha = actual - expected
            alpha = portfolio_return - expected_return

            return float(alpha)

        except Exception as e:
            logger.error(f"Error calculating Alpha: {e}")
            return 0.0

    @staticmethod
    def calculate_var(returns: np.ndarray, confidence: float = 0.95, timeframe_days: int = 1) -> float:
        """
        Calculate Value at Risk (VaR) using historical simulation

        VaR answers: "What is the maximum loss expected over the next N days
        with X% confidence?"

        Args:
            returns: Array of daily returns
            confidence: Confidence level (e.g., 0.95 = 95%)
            timeframe_days: Timeframe in days (default: 1 day)

        Returns:
            VaR as a percentage (e.g., -0.05 = 5% potential loss)
        """
        if len(returns) < 10:
            return 0.0

        try:
            # Scale to timeframe if needed
            if timeframe_days > 1:
                scaled_returns = returns * np.sqrt(timeframe_days)
            else:
                scaled_returns = returns

            # Calculate VaR at specified confidence level
            var = np.percentile(scaled_returns, (1 - confidence) * 100)

            return float(var)

        except Exception as e:
            logger.error(f"Error calculating VaR: {e}")
            return 0.0

    @staticmethod
    def calculate_cvar(returns: np.ndarray, confidence: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR / Expected Shortfall)

        CVaR answers: "If we exceed VaR, what is the average loss?"
        More conservative than VaR.

        Args:
            returns: Array of daily returns
            confidence: Confidence level

        Returns:
            CVaR as a percentage
        """
        if len(returns) < 10:
            return 0.0

        try:
            var = RiskAnalytics.calculate_var(returns, confidence)

            # CVaR = average of returns worse than VaR
            tail_losses = returns[returns <= var]

            if len(tail_losses) == 0:
                return var

            cvar = tail_losses.mean()
            return float(cvar)

        except Exception as e:
            logger.error(f"Error calculating CVaR: {e}")
            return 0.0

    @staticmethod
    def calculate_max_drawdown(portfolio_values: np.ndarray) -> Dict[str, float]:
        """
        Calculate Maximum Drawdown and related metrics

        Maximum Drawdown = largest peak-to-trough decline
        Important metric for understanding worst-case scenarios

        Args:
            portfolio_values: Array of portfolio values over time

        Returns:
            Dict with max_drawdown, max_drawdown_duration, current_drawdown
        """
        if len(portfolio_values) < 2:
            return {
                'max_drawdown': 0.0,
                'max_drawdown_duration': 0,
                'current_drawdown': 0.0
            }

        try:
            # Calculate running maximum
            running_max = np.maximum.accumulate(portfolio_values)

            # Calculate drawdown at each point
            drawdowns = (portfolio_values - running_max) / running_max

            # Maximum drawdown
            max_drawdown = np.min(drawdowns)

            # Maximum drawdown duration (days in drawdown)
            in_drawdown = drawdowns < 0
            max_duration = 0
            current_duration = 0

            for is_down in in_drawdown:
                if is_down:
                    current_duration += 1
                    max_duration = max(max_duration, current_duration)
                else:
                    current_duration = 0

            # Current drawdown
            current_drawdown = drawdowns[-1]

            return {
                'max_drawdown': float(max_drawdown),
                'max_drawdown_duration': int(max_duration),
                'current_drawdown': float(current_drawdown)
            }

        except Exception as e:
            logger.error(f"Error calculating Max Drawdown: {e}")
            return {
                'max_drawdown': 0.0,
                'max_drawdown_duration': 0,
                'current_drawdown': 0.0
            }

    @staticmethod
    def calculate_information_ratio(portfolio_returns: np.ndarray, benchmark_returns: np.ndarray) -> float:
        """
        Calculate Information Ratio

        Information Ratio = Active Return / Tracking Error
        Measures portfolio manager skill vs. benchmark

        Args:
            portfolio_returns: Array of portfolio returns
            benchmark_returns: Array of benchmark returns

        Returns:
            Annualized Information Ratio
        """
        if len(portfolio_returns) < 2 or len(benchmark_returns) < 2:
            return 0.0

        if len(portfolio_returns) != len(benchmark_returns):
            min_len = min(len(portfolio_returns), len(benchmark_returns))
            portfolio_returns = portfolio_returns[-min_len:]
            benchmark_returns = benchmark_returns[-min_len:]

        try:
            # Active returns
            active_returns = portfolio_returns - benchmark_returns

            # Tracking error (volatility of active returns)
            tracking_error = active_returns.std() * np.sqrt(RiskAnalytics.TRADING_DAYS)

            if tracking_error == 0:
                return 0.0

            # Active return (annualized)
            active_return = active_returns.mean() * RiskAnalytics.TRADING_DAYS

            info_ratio = active_return / tracking_error
            return float(info_ratio)

        except Exception as e:
            logger.error(f"Error calculating Information Ratio: {e}")
            return 0.0

    @staticmethod
    def calculate_all_metrics(portfolio_values: np.ndarray, portfolio_returns: np.ndarray,
                             market_returns: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Calculate all risk metrics for a portfolio

        Args:
            portfolio_values: Array of portfolio values over time
            portfolio_returns: Array of daily returns
            market_returns: Optional array of market returns (for beta/alpha)

        Returns:
            Dictionary with all calculated metrics
        """
        try:
            metrics = {}

            # Basic metrics
            metrics['sharpe_ratio'] = RiskAnalytics.calculate_sharpe_ratio(portfolio_returns)
            metrics['sortino_ratio'] = RiskAnalytics.calculate_sortino_ratio(portfolio_returns)

            # Risk metrics
            metrics['var_95'] = RiskAnalytics.calculate_var(portfolio_returns, 0.95)
            metrics['var_99'] = RiskAnalytics.calculate_var(portfolio_returns, 0.99)
            metrics['cvar_95'] = RiskAnalytics.calculate_cvar(portfolio_returns, 0.95)

            # Drawdown metrics
            drawdown_metrics = RiskAnalytics.calculate_max_drawdown(portfolio_values)
            metrics.update(drawdown_metrics)

            # Volatility
            metrics['volatility'] = float(portfolio_returns.std() * np.sqrt(RiskAnalytics.TRADING_DAYS))

            # Market-relative metrics (if market data available)
            if market_returns is not None and len(market_returns) > 0:
                metrics['beta'] = RiskAnalytics.calculate_beta(portfolio_returns, market_returns)
                metrics['alpha'] = RiskAnalytics.calculate_alpha(portfolio_returns, market_returns,
                                                                 metrics['beta'])
                metrics['information_ratio'] = RiskAnalytics.calculate_information_ratio(
                    portfolio_returns, market_returns
                )
            else:
                metrics['beta'] = None
                metrics['alpha'] = None
                metrics['information_ratio'] = None

            # Returns
            metrics['total_return'] = float(portfolio_values[-1] / portfolio_values[0] - 1)
            metrics['annualized_return'] = float(
                (portfolio_values[-1] / portfolio_values[0]) ** (252 / len(portfolio_values)) - 1
            )

            # Risk-adjusted performance
            metrics['calmar_ratio'] = float(
                metrics['annualized_return'] / abs(metrics['max_drawdown'])
                if metrics['max_drawdown'] != 0 else 0.0
            )

            return metrics

        except Exception as e:
            logger.error(f"Error calculating all metrics: {e}")
            return {}

    @staticmethod
    def interpret_sharpe_ratio(sharpe: float) -> Dict[str, str]:
        """Return interpretation of Sharpe Ratio"""
        if sharpe > 3.0:
            return {'rating': 'Excellent', 'class': 'excellent', 'emoji': '🌟'}
        elif sharpe > 2.0:
            return {'rating': 'Very Good', 'class': 'very-good', 'emoji': '🎯'}
        elif sharpe > 1.0:
            return {'rating': 'Good', 'class': 'good', 'emoji': '👍'}
        elif sharpe > 0.5:
            return {'rating': 'Acceptable', 'class': 'acceptable', 'emoji': '✓'}
        else:
            return {'rating': 'Poor', 'class': 'poor', 'emoji': '⚠️'}

    @staticmethod
    def interpret_beta(beta: float) -> Dict[str, str]:
        """Return interpretation of Beta"""
        if beta > 1.5:
            return {'description': 'High Volatility', 'class': 'high-vol', 'emoji': '📈'}
        elif beta > 1.0:
            return {'description': 'Above Market', 'class': 'above-market', 'emoji': '↗️'}
        elif beta > 0.5:
            return {'description': 'Below Market', 'class': 'below-market', 'emoji': '↘️'}
        else:
            return {'description': 'Low Volatility', 'class': 'low-vol', 'emoji': '📉'}

    @staticmethod
    def interpret_alpha(alpha: float) -> Dict[str, str]:
        """Return interpretation of Alpha"""
        if alpha > 0.05:
            return {'description': 'Outperforming', 'class': 'outperform', 'emoji': '🚀'}
        elif alpha > 0:
            return {'description': 'Slight Outperformance', 'class': 'slight-outperform', 'emoji': '↗️'}
        elif alpha > -0.05:
            return {'description': 'Slight Underperformance', 'class': 'slight-underperform', 'emoji': '↘️'}
        else:
            return {'description': 'Underperforming', 'class': 'underperform', 'emoji': '⚠️'}
