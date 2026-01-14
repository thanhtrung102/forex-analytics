"""API routes for performance metrics."""

from datetime import datetime

from fastapi import APIRouter
from sqlalchemy import select, func

from app.api.dependencies import DbSession
from app.db.models import Prediction, Trade, BacktestRun
from app.db.schemas import PerformanceMetrics

router = APIRouter()


@router.get("", response_model=PerformanceMetrics)
async def get_metrics(db: DbSession):
    """Get overall performance metrics."""
    # Count predictions
    pred_count = await db.scalar(select(func.count(Prediction.id)))

    # Count trades and calculate stats
    trade_stats = await db.execute(
        select(
            func.count(Trade.id).label("total"),
            func.sum(Trade.profit_loss).label("total_pnl"),
            func.count(Trade.id).filter(Trade.profit_loss > 0).label("winning"),
        ).where(Trade.status == "CLOSED")
    )
    trade_row = trade_stats.one()

    total_trades = trade_row.total or 0
    total_pnl = float(trade_row.total_pnl or 0)
    winning_trades = trade_row.winning or 0
    win_rate = winning_trades / total_trades if total_trades > 0 else 0

    # Count backtests
    backtest_count = await db.scalar(select(func.count(BacktestRun.id)))

    # Get metrics by currency pair
    pair_stats = await db.execute(
        select(
            Trade.currency_pair,
            func.count(Trade.id).label("trades"),
            func.sum(Trade.profit_loss).label("pnl"),
        )
        .where(Trade.status == "CLOSED")
        .group_by(Trade.currency_pair)
    )
    metrics_by_pair = {
        row.currency_pair: {
            "trades": row.trades,
            "pnl": float(row.pnl or 0),
        }
        for row in pair_stats.all()
    }

    # Find best performing pair
    best_pair = None
    best_pair_pnl = float("-inf")
    for pair, stats in metrics_by_pair.items():
        if stats["pnl"] > best_pair_pnl:
            best_pair_pnl = stats["pnl"]
            best_pair = pair

    # Get metrics by model
    model_stats = await db.execute(
        select(
            Prediction.model_type,
            func.count(Prediction.id).label("predictions"),
        )
        .group_by(Prediction.model_type)
    )
    metrics_by_model = {
        row.model_type: {"predictions": row.predictions}
        for row in model_stats.all()
    }

    # Find best performing model (by prediction count for now)
    best_model = None
    best_model_count = 0
    for model, stats in metrics_by_model.items():
        if stats["predictions"] > best_model_count:
            best_model_count = stats["predictions"]
            best_model = model

    return PerformanceMetrics(
        total_predictions=pred_count or 0,
        total_trades=total_trades,
        total_backtests=backtest_count or 0,
        overall_win_rate=win_rate,
        total_profit_loss=total_pnl,
        best_performing_pair=best_pair,
        best_performing_model=best_model,
        metrics_by_pair=metrics_by_pair,
        metrics_by_model=metrics_by_model,
        generated_at=datetime.utcnow(),
    )


@router.get("/summary")
async def get_summary(db: DbSession):
    """Get a quick summary of system activity."""
    pred_count = await db.scalar(select(func.count(Prediction.id)))
    trade_count = await db.scalar(select(func.count(Trade.id)))
    backtest_count = await db.scalar(select(func.count(BacktestRun.id)))

    # Get recent activity
    recent_predictions = await db.execute(
        select(Prediction)
        .order_by(Prediction.created_at.desc())
        .limit(5)
    )
    recent_preds = recent_predictions.scalars().all()

    recent_backtests = await db.execute(
        select(BacktestRun)
        .order_by(BacktestRun.created_at.desc())
        .limit(5)
    )
    recent_bts = recent_backtests.scalars().all()

    return {
        "counts": {
            "predictions": pred_count or 0,
            "trades": trade_count or 0,
            "backtests": backtest_count or 0,
        },
        "recent_predictions": [
            {
                "id": p.id,
                "pair": p.currency_pair,
                "direction": p.predicted_direction,
                "confidence": p.confidence,
                "created_at": p.created_at.isoformat(),
            }
            for p in recent_preds
        ],
        "recent_backtests": [
            {
                "id": b.id,
                "pair": b.currency_pair,
                "model": b.model_type,
                "win_rate": b.win_rate,
                "pnl": b.total_profit_loss,
                "created_at": b.created_at.isoformat(),
            }
            for b in recent_bts
        ],
    }
