"""API routes for predictions."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, func

from app.api.dependencies import DbSession, ModelManagerDep, Pagination
from app.db.models import Prediction
from app.db.schemas import (
    PredictionInput,
    PredictionOutput,
    PredictionListResponse,
    TradeDirection,
)

router = APIRouter()


@router.post("", response_model=PredictionOutput)
async def create_prediction(
    input_data: PredictionInput,
    db: DbSession,
    model_manager: ModelManagerDep,
):
    """Generate a new price prediction using the specified model."""
    # Get prediction from ML model
    try:
        result = model_manager.predict(
            model_type=input_data.model_type.value,
            currency_pair=input_data.currency_pair.upper(),
            timeframe=input_data.timeframe.value,
            lookback_periods=input_data.lookback_periods,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    # Determine direction
    direction = TradeDirection.NEUTRAL
    if result["price_change"] > 0.0001:
        direction = TradeDirection.UP
    elif result["price_change"] < -0.0001:
        direction = TradeDirection.DOWN

    # Create database record
    prediction = Prediction(
        currency_pair=input_data.currency_pair.upper(),
        timeframe=input_data.timeframe.value,
        predicted_price=result["predicted_price"],
        predicted_direction=direction.value,
        confidence=result["confidence"],
        model_type=input_data.model_type.value,
        model_version=result["model_version"],
        input_data={"lookback_periods": input_data.lookback_periods},
    )

    db.add(prediction)
    await db.commit()
    await db.refresh(prediction)

    return PredictionOutput(
        prediction_id=prediction.id,
        currency_pair=prediction.currency_pair,
        timeframe=prediction.timeframe,
        predicted_price=prediction.predicted_price,
        predicted_direction=direction,
        confidence=prediction.confidence,
        model_type=prediction.model_type,
        model_version=prediction.model_version,
        created_at=prediction.created_at,
    )


@router.get("", response_model=PredictionListResponse)
async def list_predictions(
    db: DbSession,
    pagination: Pagination,
    currency_pair: Optional[str] = Query(None, description="Filter by currency pair"),
    model_type: Optional[str] = Query(None, description="Filter by model type"),
):
    """List all predictions with optional filtering."""
    # Build query
    query = select(Prediction).order_by(Prediction.created_at.desc())

    if currency_pair:
        query = query.where(Prediction.currency_pair == currency_pair.upper())
    if model_type:
        query = query.where(Prediction.model_type == model_type.lower())

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    predictions = result.scalars().all()

    return PredictionListResponse(
        predictions=[
            PredictionOutput(
                prediction_id=p.id,
                currency_pair=p.currency_pair,
                timeframe=p.timeframe,
                predicted_price=p.predicted_price,
                predicted_direction=TradeDirection(p.predicted_direction),
                confidence=p.confidence,
                model_type=p.model_type,
                model_version=p.model_version,
                created_at=p.created_at,
            )
            for p in predictions
        ],
        total=total or 0,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{prediction_id}", response_model=PredictionOutput)
async def get_prediction(prediction_id: str, db: DbSession):
    """Get a specific prediction by ID."""
    result = await db.execute(
        select(Prediction).where(Prediction.id == prediction_id)
    )
    prediction = result.scalar_one_or_none()

    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    return PredictionOutput(
        prediction_id=prediction.id,
        currency_pair=prediction.currency_pair,
        timeframe=prediction.timeframe,
        predicted_price=prediction.predicted_price,
        predicted_direction=TradeDirection(prediction.predicted_direction),
        confidence=prediction.confidence,
        model_type=prediction.model_type,
        model_version=prediction.model_version,
        created_at=prediction.created_at,
    )


@router.delete("/{prediction_id}")
async def delete_prediction(prediction_id: str, db: DbSession):
    """Delete a specific prediction."""
    result = await db.execute(
        select(Prediction).where(Prediction.id == prediction_id)
    )
    prediction = result.scalar_one_or_none()

    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    await db.delete(prediction)
    await db.commit()

    return {"status": "deleted", "prediction_id": prediction_id}
