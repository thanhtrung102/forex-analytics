"""API routes for technical indicators."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query

from app.api.dependencies import ValidPair, ValidTimeframe
from app.db.schemas import IndicatorsResponse, IndicatorData
from app.indicators.technical import TechnicalIndicators

router = APIRouter()


@router.get("/{currency_pair}/{timeframe}", response_model=IndicatorsResponse)
async def get_indicators(
    currency_pair: str,
    timeframe: str,
    periods: int = Query(default=100, ge=1, le=500, description="Number of periods"),
    indicators: Optional[str] = Query(
        default=None,
        description="Comma-separated list of indicators to calculate (e.g., 'ema,rsi,macd')"
    ),
):
    """Calculate technical indicators for a currency pair and timeframe."""
    pair = currency_pair.upper()
    tf = timeframe.upper()

    # Parse requested indicators
    requested_indicators = None
    if indicators:
        requested_indicators = [i.strip().lower() for i in indicators.split(",")]

    # Calculate indicators
    calculator = TechnicalIndicators()
    result = calculator.calculate_all(
        currency_pair=pair,
        timeframe=tf,
        periods=periods,
        indicator_list=requested_indicators,
    )

    # Format response
    formatted_indicators = {}
    for name, values in result.items():
        formatted_indicators[name] = [
            IndicatorData(timestamp=v["timestamp"], value=v["value"])
            for v in values
        ]

    return IndicatorsResponse(
        currency_pair=pair,
        timeframe=tf,
        indicators=formatted_indicators,
        generated_at=datetime.utcnow(),
    )


@router.get("/list")
async def list_available_indicators():
    """List all available technical indicators."""
    calculator = TechnicalIndicators()
    return {
        "indicators": calculator.list_indicators(),
        "categories": {
            "moving_averages": ["sma", "ema", "wma", "hma"],
            "momentum": ["rsi", "macd", "roc", "ppo", "kst"],
            "volatility": ["bollinger_upper", "bollinger_middle", "bollinger_lower", "atr"],
            "oscillators": ["stochastic_k", "stochastic_d", "cci"],
            "trend": ["adx", "aroon_up", "aroon_down"],
        }
    }
