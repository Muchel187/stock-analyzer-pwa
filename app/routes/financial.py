"""
Financial Health API Endpoints
Provides Piotroski Score, Altman Z-Score, and Financial Ratios
"""

from flask import Blueprint, jsonify
from app.services.fmp_service import FMPService

bp = Blueprint('financial', __name__, url_prefix='/api/financial')


@bp.route('/score/<ticker>', methods=['GET'])
def get_financial_score(ticker):
    """
    Get Piotroski and Altman Z-Score for a stock

    Example: GET /api/financial/score/AAPL

    Response:
        {
            "symbol": "AAPL",
            "piotroskiScore": 8,
            "altmanZScore": 5.2,
            "profitability": 4,
            "leverage": 2,
            "efficiency": 2
        }
    """
    try:
        data = FMPService.get_financial_score(ticker)

        if not data:
            return jsonify({'error': f'No financial score data available for {ticker}'}), 404

        return jsonify(data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ratios/<ticker>', methods=['GET'])
def get_financial_ratios(ticker):
    """
    Get comprehensive financial ratios (TTM)

    Example: GET /api/financial/ratios/AAPL

    Response includes:
        - Profitability: grossProfitMargin, operatingProfitMargin, netProfitMargin, returnOnEquity, returnOnAssets
        - Liquidity: currentRatio, quickRatio, cashRatio
        - Leverage: debtToEquityRatio, debtToAssets, interestCoverage
        - Efficiency: assetTurnover, inventoryTurnover, receivablesTurnover
        - Valuation: priceToEarningsRatio, priceToBookRatio, priceToSalesRatio, pegRatio, evToEbitda
    """
    try:
        data = FMPService.get_financial_ratios(ticker)

        if not data:
            return jsonify({'error': f'No financial ratios data available for {ticker}'}), 404

        return jsonify(data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
