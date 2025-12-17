"""
Test configuration and fixtures.

This module provides pytest fixtures and configuration
for running tests.
"""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from src.main import app
from src.core.database import Base, get_db
from src.core.config import settings


# Database URL for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db():
    """Create a test database and tables."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    yield async_session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_db):
    """Get a database session for testing."""
    async with test_db() as session:
        yield session
        await session.close()


@pytest.fixture
def test_client(test_db):
    """Create a test client for API testing with test database."""
    async def override_get_db():
        async with test_db() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    client = AsyncClient(app=app, base_url="http://test")
    yield client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing."""
    with patch('src.utils.llm.llm_service') as mock:
        mock.generate_summary.return_value = "Generated summary"
        mock.generate_review_summary.return_value = "Generated review summary"
        mock.generate_recommendations.return_value = "Generated recommendations"
        yield mock
