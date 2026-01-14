"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import predictions, trades, indicators, models, backtest, metrics
from app.core.config import settings
from app.db.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Cleanup if needed
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="ML-powered forex market prediction and backtesting API",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "version": settings.app_version}


# Include API routers
app.include_router(
    models.router,
    prefix=f"{settings.api_prefix}/models",
    tags=["models"],
)
app.include_router(
    predictions.router,
    prefix=f"{settings.api_prefix}/predictions",
    tags=["predictions"],
)
app.include_router(
    backtest.router,
    prefix=f"{settings.api_prefix}/backtest",
    tags=["backtest"],
)
app.include_router(
    indicators.router,
    prefix=f"{settings.api_prefix}/indicators",
    tags=["indicators"],
)
app.include_router(
    trades.router,
    prefix=f"{settings.api_prefix}/trades",
    tags=["trades"],
)
app.include_router(
    metrics.router,
    prefix=f"{settings.api_prefix}/metrics",
    tags=["metrics"],
)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }
