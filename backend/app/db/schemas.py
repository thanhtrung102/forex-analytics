"""Pydantic schemas for API request/response validation."""

from datetime import datetime, date
from typing import Optional, List, Any
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


# Enums
class ModelType(str, Enum):
    CNN = "cnn"
    RNN = "rnn"
    TCN = "tcn"


class TradeDirection(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    NEUTRAL = "NEUTRAL"


class TradeType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class TradeStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class Timeframe(str, Enum):
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"


# Currency pairs
VALID_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCHF",
    "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY", "AUDJPY"
]


# Model Schemas
class ModelInfo(BaseModel):
    """Information about an available ML model."""
    model_id: str = Field(..., description="Unique model identifier")
    model_type: ModelType = Field(..., description="Type of model (cnn, rnn, tcn)")
    version: str = Field(..., description="Model version")
    description: str = Field(..., description="Model description")
    input_shape: List[int] = Field(..., description="Expected input shape")
    supported_pairs: List[str] = Field(..., description="Supported currency pairs")
    supported_timeframes: List[str] = Field(..., description="Supported timeframes")
    metrics: dict = Field(default={}, description="Model performance metrics")

    model_config = ConfigDict(from_attributes=True)


class ModelListResponse(BaseModel):
    """Response containing list of available models."""
    models: List[ModelInfo]
    total: int


# Prediction Schemas
class PredictionInput(BaseModel):
    """Input data for creating a prediction."""
    currency_pair: str = Field(
        ...,
        description="Forex pair (e.g., EURUSD)",
        examples=["EURUSD", "GBPUSD"]
    )
    timeframe: Timeframe = Field(
        ...,
        description="Prediction timeframe",
        examples=["H1", "D1"]
    )
    model_type: ModelType = Field(
        default=ModelType.CNN,
        description="ML model type to use"
    )
    lookback_periods: int = Field(
        default=28,
        ge=1,
        le=100,
        description="Number of historical periods to consider"
    )


class PredictionOutput(BaseModel):
    """Output from a prediction request."""
    prediction_id: str = Field(..., description="Unique prediction ID")
    currency_pair: str = Field(..., description="Currency pair predicted")
    timeframe: str = Field(..., description="Timeframe of prediction")
    predicted_price: float = Field(..., description="Predicted price value")
    predicted_direction: TradeDirection = Field(..., description="Predicted direction")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")
    model_type: str = Field(..., description="Model used for prediction")
    model_version: str = Field(..., description="Model version")
    created_at: datetime = Field(..., description="Timestamp of prediction")

    model_config = ConfigDict(from_attributes=True)


class PredictionListResponse(BaseModel):
    """Response containing list of predictions."""
    predictions: List[PredictionOutput]
    total: int
    page: int
    page_size: int


# Backtest Schemas
class BacktestInput(BaseModel):
    """Input parameters for backtesting."""
    currency_pair: str = Field(
        ...,
        description="Currency pair to backtest",
        examples=["EURUSD"]
    )
    timeframe: Timeframe = Field(
        ...,
        description="Timeframe for backtesting"
    )
    model_type: ModelType = Field(
        default=ModelType.CNN,
        description="Model type to use"
    )
    start_date: date = Field(
        ...,
        description="Start date for backtesting"
    )
    end_date: date = Field(
        ...,
        description="End date for backtesting"
    )
    initial_balance: float = Field(
        default=10000.0,
        gt=0,
        description="Initial account balance"
    )
    leverage: int = Field(
        default=100,
        ge=1,
        le=500,
        description="Trading leverage"
    )
    risk_factor: float = Field(
        default=1.0,
        gt=0,
        le=10,
        description="Risk factor for position sizing"
    )


class BacktestResult(BaseModel):
    """Results from a backtesting run."""
    backtest_id: str = Field(..., description="Unique backtest ID")
    currency_pair: str = Field(..., description="Currency pair tested")
    timeframe: str = Field(..., description="Timeframe tested")
    model_type: str = Field(..., description="Model type used")
    start_date: datetime = Field(..., description="Backtest start date")
    end_date: datetime = Field(..., description="Backtest end date")
    initial_balance: float = Field(..., description="Starting balance")
    final_balance: float = Field(..., description="Ending balance")
    total_trades: int = Field(..., description="Total number of trades")
    winning_trades: int = Field(..., description="Number of winning trades")
    losing_trades: int = Field(..., description="Number of losing trades")
    total_profit_loss: float = Field(..., description="Total profit/loss")
    win_rate: float = Field(..., ge=0, le=1, description="Win rate percentage")
    max_drawdown: float = Field(..., description="Maximum drawdown")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio")
    created_at: datetime = Field(..., description="Timestamp of backtest")

    model_config = ConfigDict(from_attributes=True)


class BacktestListResponse(BaseModel):
    """Response containing list of backtest results."""
    backtests: List[BacktestResult]
    total: int


# Trade Schemas
class TradeOutput(BaseModel):
    """Output representing a trade."""
    trade_id: str = Field(..., description="Unique trade ID")
    prediction_id: Optional[str] = Field(None, description="Associated prediction ID")
    backtest_run_id: Optional[str] = Field(None, description="Associated backtest ID")
    currency_pair: str = Field(..., description="Currency pair traded")
    trade_type: TradeType = Field(..., description="Trade type (BUY/SELL)")
    entry_price: float = Field(..., description="Entry price")
    exit_price: Optional[float] = Field(None, description="Exit price")
    lot_size: float = Field(..., description="Position size in lots")
    leverage: int = Field(..., description="Leverage used")
    take_profit: Optional[float] = Field(None, description="Take profit level")
    stop_loss: Optional[float] = Field(None, description="Stop loss level")
    profit_loss: Optional[float] = Field(None, description="Profit/loss amount")
    profit_pips: Optional[float] = Field(None, description="Profit/loss in pips")
    status: TradeStatus = Field(..., description="Trade status")
    created_at: datetime = Field(..., description="Trade open time")
    closed_at: Optional[datetime] = Field(None, description="Trade close time")

    model_config = ConfigDict(from_attributes=True)


class TradeListResponse(BaseModel):
    """Response containing list of trades."""
    trades: List[TradeOutput]
    total: int
    page: int
    page_size: int


# Indicator Schemas
class IndicatorData(BaseModel):
    """Technical indicator data point."""
    timestamp: datetime
    value: float


class IndicatorsResponse(BaseModel):
    """Response containing technical indicators."""
    currency_pair: str
    timeframe: str
    indicators: dict[str, List[IndicatorData]]
    generated_at: datetime


# Metrics Schemas
class PerformanceMetrics(BaseModel):
    """Overall performance metrics."""
    total_predictions: int = Field(..., description="Total predictions made")
    total_trades: int = Field(..., description="Total trades executed")
    total_backtests: int = Field(..., description="Total backtests run")
    overall_win_rate: float = Field(..., description="Overall win rate")
    total_profit_loss: float = Field(..., description="Total profit/loss")
    best_performing_pair: Optional[str] = Field(None, description="Best performing pair")
    best_performing_model: Optional[str] = Field(None, description="Best performing model")
    metrics_by_pair: dict = Field(default={}, description="Metrics broken down by pair")
    metrics_by_model: dict = Field(default={}, description="Metrics broken down by model")
    generated_at: datetime = Field(..., description="Timestamp of metrics")


# OHLC Data Schema
class OHLCData(BaseModel):
    """OHLC candlestick data."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int = 0


class OHLCResponse(BaseModel):
    """Response containing OHLC data."""
    currency_pair: str
    timeframe: str
    data: List[OHLCData]
    count: int
