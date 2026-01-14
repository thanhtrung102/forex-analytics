"""API dependencies for dependency injection."""

from typing import Annotated

from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.schemas import VALID_PAIRS, Timeframe
from app.ml.inference import ModelManager


# Database dependency
DbSession = Annotated[AsyncSession, Depends(get_db)]

# Model manager singleton
_model_manager: ModelManager | None = None


def get_model_manager() -> ModelManager:
    """Get or create the model manager singleton."""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager


ModelManagerDep = Annotated[ModelManager, Depends(get_model_manager)]


# Validation dependencies
def validate_currency_pair(
    currency_pair: str = Query(..., description="Currency pair (e.g., EURUSD)")
) -> str:
    """Validate that the currency pair is supported."""
    pair = currency_pair.upper()
    if pair not in VALID_PAIRS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid currency pair: {currency_pair}. Valid pairs: {VALID_PAIRS}"
        )
    return pair


def validate_timeframe(
    timeframe: str = Query(..., description="Timeframe (e.g., H1)")
) -> str:
    """Validate that the timeframe is supported."""
    tf = timeframe.upper()
    valid_timeframes = [t.value for t in Timeframe]
    if tf not in valid_timeframes:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid timeframe: {timeframe}. Valid timeframes: {valid_timeframes}"
        )
    return tf


ValidPair = Annotated[str, Depends(validate_currency_pair)]
ValidTimeframe = Annotated[str, Depends(validate_timeframe)]


# Pagination dependencies
class PaginationParams:
    """Common pagination parameters."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size


Pagination = Annotated[PaginationParams, Depends()]
