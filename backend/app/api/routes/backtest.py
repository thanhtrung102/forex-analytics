"""API routes for backtesting."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, func

from app.api.dependencies import DbSession, ModelManagerDep, Pagination
from app.db.models import BacktestRun, Trade
from app.db.schemas import (
    BacktestInput,
    BacktestResult,
    BacktestListResponse,
    TradeOutput,
    TradeType,
    TradeStatus,
)
from app.trading.simulator import TradingSimulator

router = APIRouter()


@router.post("", response_model=BacktestResult)
async def run_backtest(
    input_data: BacktestInput,
    db: DbSession,
    model_manager: ModelManagerDep,
):
    """Run a backtesting simulation on historical data."""
    # Initialize simulator
    simulator = TradingSimulator(
        model_manager=model_manager,
        initial_balance=input_data.initial_balance,
        leverage=input_data.leverage,
        risk_factor=input_data.risk_factor,
    )

    # Run simulation
    try:
        results = await simulator.run_backtest(
            currency_pair=input_data.currency_pair.upper(),
            timeframe=input_data.timeframe.value,
            model_type=input_data.model_type.value,
            start_date=input_data.start_date,
            end_date=input_data.end_date,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")

    # Create backtest run record
    backtest_run = BacktestRun(
        currency_pair=input_data.currency_pair.upper(),
        timeframe=input_data.timeframe.value,
        model_type=input_data.model_type.value,
        start_date=datetime.combine(input_data.start_date, datetime.min.time()),
        end_date=datetime.combine(input_data.end_date, datetime.min.time()),
        initial_balance=input_data.initial_balance,
        final_balance=results["final_balance"],
        leverage=input_data.leverage,
        total_trades=results["total_trades"],
        winning_trades=results["winning_trades"],
        losing_trades=results["losing_trades"],
        total_profit_loss=results["total_profit_loss"],
        win_rate=results["win_rate"],
        max_drawdown=results["max_drawdown"],
        sharpe_ratio=results.get("sharpe_ratio"),
        parameters={
            "risk_factor": input_data.risk_factor,
        },
        detailed_results=results.get("detailed_results", {}),
    )

    db.add(backtest_run)
    await db.commit()
    await db.refresh(backtest_run)

    # Store trades from backtest
    for trade_data in results.get("trades", []):
        trade = Trade(
            backtest_run_id=backtest_run.id,
            currency_pair=input_data.currency_pair.upper(),
            trade_type=trade_data["type"],
            entry_price=trade_data["entry_price"],
            exit_price=trade_data.get("exit_price"),
            lot_size=trade_data.get("lot_size", 0.01),
            leverage=input_data.leverage,
            take_profit=trade_data.get("take_profit"),
            stop_loss=trade_data.get("stop_loss"),
            profit_loss=trade_data.get("profit_loss"),
            profit_pips=trade_data.get("profit_pips"),
            status="CLOSED",
            created_at=trade_data.get("entry_time", datetime.utcnow()),
            closed_at=trade_data.get("exit_time"),
        )
        db.add(trade)

    await db.commit()

    return BacktestResult(
        backtest_id=backtest_run.id,
        currency_pair=backtest_run.currency_pair,
        timeframe=backtest_run.timeframe,
        model_type=backtest_run.model_type,
        start_date=backtest_run.start_date,
        end_date=backtest_run.end_date,
        initial_balance=backtest_run.initial_balance,
        final_balance=backtest_run.final_balance,
        total_trades=backtest_run.total_trades,
        winning_trades=backtest_run.winning_trades,
        losing_trades=backtest_run.losing_trades,
        total_profit_loss=backtest_run.total_profit_loss,
        win_rate=backtest_run.win_rate,
        max_drawdown=backtest_run.max_drawdown,
        sharpe_ratio=backtest_run.sharpe_ratio,
        created_at=backtest_run.created_at,
    )


@router.get("", response_model=BacktestListResponse)
async def list_backtests(
    db: DbSession,
    currency_pair: Optional[str] = Query(None, description="Filter by currency pair"),
    model_type: Optional[str] = Query(None, description="Filter by model type"),
):
    """List all backtest runs with optional filtering."""
    query = select(BacktestRun).order_by(BacktestRun.created_at.desc())

    if currency_pair:
        query = query.where(BacktestRun.currency_pair == currency_pair.upper())
    if model_type:
        query = query.where(BacktestRun.model_type == model_type.lower())

    result = await db.execute(query)
    backtests = result.scalars().all()

    return BacktestListResponse(
        backtests=[
            BacktestResult(
                backtest_id=b.id,
                currency_pair=b.currency_pair,
                timeframe=b.timeframe,
                model_type=b.model_type,
                start_date=b.start_date,
                end_date=b.end_date,
                initial_balance=b.initial_balance,
                final_balance=b.final_balance or 0,
                total_trades=b.total_trades,
                winning_trades=b.winning_trades,
                losing_trades=b.losing_trades,
                total_profit_loss=b.total_profit_loss,
                win_rate=b.win_rate or 0,
                max_drawdown=b.max_drawdown or 0,
                sharpe_ratio=b.sharpe_ratio,
                created_at=b.created_at,
            )
            for b in backtests
        ],
        total=len(backtests),
    )


@router.get("/{backtest_id}", response_model=BacktestResult)
async def get_backtest(backtest_id: str, db: DbSession):
    """Get a specific backtest by ID."""
    result = await db.execute(
        select(BacktestRun).where(BacktestRun.id == backtest_id)
    )
    backtest = result.scalar_one_or_none()

    if backtest is None:
        raise HTTPException(status_code=404, detail="Backtest not found")

    return BacktestResult(
        backtest_id=backtest.id,
        currency_pair=backtest.currency_pair,
        timeframe=backtest.timeframe,
        model_type=backtest.model_type,
        start_date=backtest.start_date,
        end_date=backtest.end_date,
        initial_balance=backtest.initial_balance,
        final_balance=backtest.final_balance or 0,
        total_trades=backtest.total_trades,
        winning_trades=backtest.winning_trades,
        losing_trades=backtest.losing_trades,
        total_profit_loss=backtest.total_profit_loss,
        win_rate=backtest.win_rate or 0,
        max_drawdown=backtest.max_drawdown or 0,
        sharpe_ratio=backtest.sharpe_ratio,
        created_at=backtest.created_at,
    )


@router.get("/{backtest_id}/trades", response_model=list[TradeOutput])
async def get_backtest_trades(backtest_id: str, db: DbSession):
    """Get all trades for a specific backtest."""
    # Verify backtest exists
    result = await db.execute(
        select(BacktestRun).where(BacktestRun.id == backtest_id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Backtest not found")

    # Get trades
    result = await db.execute(
        select(Trade)
        .where(Trade.backtest_run_id == backtest_id)
        .order_by(Trade.created_at)
    )
    trades = result.scalars().all()

    return [
        TradeOutput(
            trade_id=t.id,
            prediction_id=t.prediction_id,
            backtest_run_id=t.backtest_run_id,
            currency_pair=t.currency_pair,
            trade_type=TradeType(t.trade_type),
            entry_price=t.entry_price,
            exit_price=t.exit_price,
            lot_size=t.lot_size,
            leverage=t.leverage,
            take_profit=t.take_profit,
            stop_loss=t.stop_loss,
            profit_loss=t.profit_loss,
            profit_pips=t.profit_pips,
            status=TradeStatus(t.status),
            created_at=t.created_at,
            closed_at=t.closed_at,
        )
        for t in trades
    ]
