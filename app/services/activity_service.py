"""Service layer for activity operations."""

from collections.abc import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity


class ActivityService:
    """Service for managing activities."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with database session."""
        self.session = session

    async def get_all(self) -> AsyncGenerator[Activity, None]:
        """Get all activities."""
        stmt = select(Activity)
        result = await self.session.execute(stmt)
        for activity in result.scalars():
            yield activity

    async def get_by_id(self, activity_id: int) -> Activity | None:
        """Get activity by ID."""
        stmt = select(Activity).where(Activity.id == activity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_descendants(
        self,
        activity_id: int,
    ) -> list[Activity]:
        """Get all descendant activities recursively."""
        activity = await self.get_by_id(activity_id)
        if activity is None:
            return []
        return activity.get_descendants()

    async def get_activity_tree(self) -> list[dict]:
        """Get all activities as a hierarchical tree."""
        stmt = select(Activity)
        result = await self.session.execute(stmt)
        activities = result.scalars().all()

        # Build a dict of activities by ID
        activity_map = {a.id: a for a in activities}

        # Build the tree
        tree = []
        for activity in activities:
            if activity.parent_id is None:
                tree.append(self._build_tree_node(activity, activity_map))
        return tree

    def _build_tree_node(
        self,
        activity: Activity,
        activity_map: dict[int, Activity],
    ) -> dict:
        """Build a tree node for an activity."""
        node = {
            "id": activity.id,
            "name": activity.name,
            "children": [],
        }
        # Find children
        for child in activity_map.values():
            if child.parent_id == activity.id:
                node["children"].append(
                    self._build_tree_node(child, activity_map),
                )
        return node
