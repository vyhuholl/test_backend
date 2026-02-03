"""Test fixtures for application."""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_db
from app.core.config import settings
from app.main import create_app
from app.models.activity import Activity
from app.models.base import Base
from app.models.building import Building
from app.models.organisation import Organisation

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create async engine for testing
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fixture for database session with in-memory SQLite."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """Fixture for HTTP test client."""
    app = create_app()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def authenticated_client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """Fixture for authenticated HTTP test client."""
    app = create_app()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-API-Key": settings.api_key},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def sample_activity(db_session: AsyncSession) -> Activity:
    """Create a sample activity."""
    activity = Activity(name="Sample Activity")
    db_session.add(activity)
    await db_session.commit()
    await db_session.refresh(activity)
    return activity


@pytest.fixture
async def sample_building(db_session: AsyncSession) -> Building:
    """Create a sample building."""
    building = Building(
        address="123 Test Street",
        latitude=55.7558,
        longitude=37.6173,
    )
    db_session.add(building)
    await db_session.commit()
    await db_session.refresh(building)
    return building


@pytest.fixture
async def sample_organisation(
    db_session: AsyncSession,
    sample_building: Building,
    sample_activity: Activity,
) -> Organisation:
    """Create a sample organisation."""
    organisation = Organisation(
        name="Test Organisation",
        building_id=sample_building.id,
    )
    organisation.activities.append(sample_activity)
    db_session.add(organisation)
    await db_session.commit()
    # Refresh with eager loading to avoid MissingGreenlet error
    stmt = (
        select(Organisation)
        .options(
            selectinload(Organisation.building),
            selectinload(Organisation.activities),
        )
        .where(Organisation.id == organisation.id)
    )
    result = await db_session.execute(stmt)
    organisation = result.scalar_one_or_none()
    return organisation
