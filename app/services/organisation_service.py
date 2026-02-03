"""Service layer for organisation operations with geospatial search."""

from collections.abc import AsyncGenerator
from math import asin, cos, radians, sin, sqrt

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.activity import Activity
from app.models.building import Building
from app.models.organisation import Organisation


class OrganisationService:
    """Service for managing organisations with search capabilities."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with database session."""
        self.session = session

    async def get_by_id(self, org_id: int) -> Organisation | None:
        """Get organisation by ID with all relations."""
        stmt = (
            select(Organisation)
            .options(
                joinedload(Organisation.building),
                selectinload(Organisation.phones),
                selectinload(Organisation.activities),
            )
            .where(Organisation.id == org_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_building(
        self,
        building_id: int,
    ) -> AsyncGenerator[Organisation, None]:
        """Get all organisations in a building."""
        stmt = (
            select(Organisation)
            .options(
                joinedload(Organisation.building),
                selectinload(Organisation.phones),
                selectinload(Organisation.activities),
            )
            .where(Organisation.building_id == building_id)
        )
        result = await self.session.execute(stmt)
        for org in result.scalars():
            yield org

    async def get_by_activity(
        self,
        activity_id: int,
    ) -> AsyncGenerator[Organisation, None]:
        """Get organisations by activity (including descendants)."""
        # Get activity and all its descendants
        activity = await self.session.get(Activity, activity_id)
        if activity is None:
            return

        activity_ids = [activity_id]
        activity_ids.extend([a.id for a in activity.get_descendants()])

        stmt = (
            select(Organisation)
            .options(
                joinedload(Organisation.building),
                selectinload(Organisation.phones),
                selectinload(Organisation.activities),
            )
            .where(Organisation.activities.any(Activity.id.in_(activity_ids)))
        )
        result = await self.session.execute(stmt)
        for org in result.scalars():
            yield org

    async def search_by_name(
        self,
        name_query: str,
    ) -> AsyncGenerator[Organisation, None]:
        """Search organisations by name (case-insensitive partial match)."""
        stmt = (
            select(Organisation)
            .options(
                joinedload(Organisation.building),
                selectinload(Organisation.phones),
                selectinload(Organisation.activities),
            )
            .where(Organisation.name.ilike(f"%{name_query}%"))
        )
        result = await self.session.execute(stmt)
        for org in result.scalars():
            yield org

    async def search_by_radius(
        self,
        lat: float,
        lon: float,
        radius_km: float,
    ) -> AsyncGenerator[Organisation, None]:
        """Search organisations within a radius of a point."""
        stmt = (
            select(Organisation)
            .options(
                joinedload(Organisation.building),
                selectinload(Organisation.phones),
                selectinload(Organisation.activities),
            )
            .join(Building)
        )
        result = await self.session.execute(stmt)
        for org in result.scalars():
            distance = self._haversine_distance(
                lat,
                lon,
                org.building.latitude,
                org.building.longitude,
            )
            if distance <= radius_km:
                yield org

    async def search_by_area(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
    ) -> AsyncGenerator[Organisation, None]:
        """Search organisations within a rectangular area."""
        stmt = (
            select(Organisation)
            .options(
                joinedload(Organisation.building),
                selectinload(Organisation.phones),
                selectinload(Organisation.activities),
            )
            .join(Building)
            .where(
                and_(
                    Building.latitude >= min_lat,
                    Building.latitude <= max_lat,
                    Building.longitude >= min_lon,
                    Building.longitude <= max_lon,
                ),
            )
        )
        result = await self.session.execute(stmt)
        for org in result.scalars():
            yield org

    async def search(
        self,
        name: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        radius_km: float | None = None,
        min_lat: float | None = None,
        max_lat: float | None = None,
        min_lon: float | None = None,
        max_lon: float | None = None,
    ) -> AsyncGenerator[Organisation, None]:
        """Search organisations with multiple filters."""
        stmt = (
            select(Organisation)
            .options(
                joinedload(Organisation.building),
                selectinload(Organisation.phones),
                selectinload(Organisation.activities),
            )
            .join(Building)
        )

        conditions = []
        if name:
            conditions.append(Organisation.name.ilike(f"%{name}%"))

        if radius_km and lat is not None and lon is not None:
            # For radius search, we need to filter in Python
            # since SQLite doesn't have spatial functions
            pass  # We'll filter after loading

        if all(v is not None for v in [min_lat, max_lat, min_lon, max_lon]):
            conditions.append(
                and_(
                    Building.latitude >= min_lat,
                    Building.latitude <= max_lat,
                    Building.longitude >= min_lon,
                    Building.longitude <= max_lon,
                ),
            )

        if conditions:
            stmt = stmt.where(or_(*conditions))

        result = await self.session.execute(stmt)
        for org in result.scalars():
            # Apply radius filter if specified
            if radius_km and lat is not None and lon is not None:
                distance = self._haversine_distance(
                    lat,
                    lon,
                    org.building.latitude,
                    org.building.longitude,
                )
                if distance <= radius_km:
                    yield org
            else:
                yield org

    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """Calculate distance between two points using Haversine formula.

        Returns distance in kilometers.
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))

        # Radius of Earth in kilometers
        r = 6371
        return c * r
