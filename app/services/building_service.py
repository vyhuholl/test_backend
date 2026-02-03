"""Service layer for building operations."""

from collections.abc import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.building import Building


class BuildingService:
    """Service for managing buildings."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with database session."""
        self.session = session

    async def get_all(self) -> AsyncGenerator[Building, None]:
        """Get all buildings."""
        stmt = select(Building)
        result = await self.session.execute(stmt)
        for building in result.scalars():
            yield building

    async def get_by_id(self, building_id: int) -> Building | None:
        """Get building by ID."""
        stmt = select(Building).where(Building.id == building_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
