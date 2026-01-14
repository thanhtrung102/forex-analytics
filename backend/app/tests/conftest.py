"""Pytest configuration and fixtures."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.db.database import Base, get_db
from app.ml.inference import ModelManager
from app.api.dependencies import get_model_manager


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_forex.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
def mock_model_manager() -> ModelManager:
    """Create mock model manager for testing."""
    return ModelManager()


@pytest.fixture(scope="function")
def client(db_session, mock_model_manager) -> TestClient:
    """Create test client with dependency overrides."""

    async def override_get_db():
        yield db_session

    def override_get_model_manager():
        return mock_model_manager

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_model_manager] = override_get_model_manager

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session, mock_model_manager) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""

    async def override_get_db():
        yield db_session

    def override_get_model_manager():
        return mock_model_manager

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_model_manager] = override_get_model_manager

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
