"""SQLAlchemy database models."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Integer, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


def generate_uuid():
    """Generate a new UUID."""
    return str(uuid.uuid4())


class Prediction(Base):
    """Model for storing forex predictions."""

    __tablename__ = "predictions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    currency_pair = Column(String(10), nullable=False, index=True)
    timeframe = Column(String(5), nullable=False)
    predicted_price = Column(Float, nullable=False)
    predicted_direction = Column(String(10))  # UP, DOWN, NEUTRAL
    confidence = Column(Float)
    model_type = Column(String(20), nullable=False)  # cnn, rnn, tcn
    model_version = Column(String(50))
    input_data = Column(JSON)  # Store input features for reference
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship to trades
    trades = relationship("Trade", back_populates="prediction")

    def __repr__(self):
        return f"<Prediction {self.id[:8]} {self.currency_pair} {self.predicted_direction}>"


class Trade(Base):
    """Model for storing simulated trades."""

    __tablename__ = "trades"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    prediction_id = Column(String(36), ForeignKey("predictions.id"), nullable=True)
    backtest_run_id = Column(String(36), ForeignKey("backtest_runs.id"), nullable=True)
    currency_pair = Column(String(10), nullable=False, index=True)
    trade_type = Column(String(10), nullable=False)  # BUY, SELL
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    lot_size = Column(Float, default=0.01)
    leverage = Column(Integer, default=100)
    take_profit = Column(Float)
    stop_loss = Column(Float)
    profit_loss = Column(Float)
    profit_pips = Column(Float)
    status = Column(String(20), default="OPEN")  # OPEN, CLOSED, CANCELLED
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    closed_at = Column(DateTime)

    # Relationships
    prediction = relationship("Prediction", back_populates="trades")
    backtest_run = relationship("BacktestRun", back_populates="trades")

    def __repr__(self):
        return f"<Trade {self.id[:8]} {self.trade_type} {self.currency_pair} {self.status}>"


class BacktestRun(Base):
    """Model for storing backtesting run results."""

    __tablename__ = "backtest_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    currency_pair = Column(String(10), nullable=False)
    timeframe = Column(String(5), nullable=False)
    model_type = Column(String(20), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_balance = Column(Float, default=10000.0)
    final_balance = Column(Float)
    leverage = Column(Integer, default=100)

    # Results
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    total_profit_loss = Column(Float, default=0.0)
    win_rate = Column(Float)
    max_drawdown = Column(Float)
    sharpe_ratio = Column(Float)

    # Full results as JSON
    parameters = Column(JSON)
    detailed_results = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship to trades
    trades = relationship("Trade", back_populates="backtest_run")

    def __repr__(self):
        return f"<BacktestRun {self.id[:8]} {self.currency_pair} {self.model_type}>"


class MarketData(Base):
    """Model for storing historical market data."""

    __tablename__ = "market_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    currency_pair = Column(String(10), nullable=False, index=True)
    timeframe = Column(String(5), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, default=0)

    def __repr__(self):
        return f"<MarketData {self.currency_pair} {self.timeframe} {self.timestamp}>"
