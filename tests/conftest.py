"""Test fixtures for application."""

from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient, AsyncSession

from app.core.config import settings
from app.database import get_db
from app.main import create_app


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    """Fixture for database session."""
    async for session in get_db():
        yield session


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    """Fixture for HTTP test client."""
    async with AsyncClient(
        app=create_app(),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
async def authenticated_client(
    client: AsyncClient,
) -> AsyncGenerator[AsyncClient]:
    """Fixture for authenticated HTTP test client."""
    async with AsyncClient(
        app=create_app(),
        base_url="http://test",
        headers={"X-API-Key": settings.api_key},
    ) as ac:
        yield ac
