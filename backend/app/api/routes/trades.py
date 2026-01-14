"""API routes for trade management."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, func

from app.api.dependencies import DbSession, Pagination
from app.db.models import Trade
from app.db.schemas import TradeOutput, TradeListResponse, TradeType, TradeStatus

router = APIRouter()


@router.get("", response_model=TradeListResponse)
async def list_trades(
    db: DbSession,
    pagination: Pagination,
    currency_pair: Optional[str] = Query(None, description="Filter by currency pair"),
    status: Optional[str] = Query(None, description="Filter by status"),
    trade_type: Optional[str] = Query(None, description="Filter by trade type"),
):
    """List all trades with optional filtering."""
    query = select(Trade).order_by(Trade.created_at.desc())

    if currency_pair:
        query = query.where(Trade.currency_pair == currency_pair.upper())
    if status:
        query = query.where(Trade.status == status.upper())
    if trade_type:
        query = query.where(Trade.trade_type == trade_type.upper())

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    trades = result.scalars().all()

    return TradeListResponse(
        trades=[
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
        ],
        total=total or 0,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{trade_id}", response_model=TradeOutput)
async def get_trade(trade_id: str, db: DbSession):
    """Get a specific trade by ID."""
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    trade = result.scalar_one_or_none()

    if trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")

    return TradeOutput(
        trade_id=trade.id,
        prediction_id=trade.prediction_id,
        backtest_run_id=trade.backtest_run_id,
        currency_pair=trade.currency_pair,
        trade_type=TradeType(trade.trade_type),
        entry_price=trade.entry_price,
        exit_price=trade.exit_price,
        lot_size=trade.lot_size,
        leverage=trade.leverage,
        take_profit=trade.take_profit,
        stop_loss=trade.stop_loss,
        profit_loss=trade.profit_loss,
        profit_pips=trade.profit_pips,
        status=TradeStatus(trade.status),
        created_at=trade.created_at,
        closed_at=trade.closed_at,
    )


@router.get("/summary/by-pair")
async def get_trades_summary_by_pair(db: DbSession):
    """Get trade summary statistics grouped by currency pair."""
    result = await db.execute(
        select(
            Trade.currency_pair,
            func.count(Trade.id).label("total_trades"),
            func.sum(Trade.profit_loss).label("total_pnl"),
            func.avg(Trade.profit_loss).label("avg_pnl"),
        )
        .where(Trade.status == "CLOSED")
        .group_by(Trade.currency_pair)
    )
    rows = result.all()

    return {
        "summary": [
            {
                "currency_pair": row.currency_pair,
                "total_trades": row.total_trades,
                "total_pnl": float(row.total_pnl or 0),
                "avg_pnl": float(row.avg_pnl or 0),
            }
            for row in rows
        ]
    }
