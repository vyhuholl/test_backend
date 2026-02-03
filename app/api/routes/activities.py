"""Activity API routes."""

from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends

from app.api.dependencies import get_authenticated_db
from app.api.schemas import ActivitySchema, ActivityTreeSchema
from app.services.activity_service import ActivityService

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("", response_model=list[ActivitySchema])
async def get_activities(
    db: AsyncGenerator = Depends(get_authenticated_db),
) -> list[ActivitySchema]:
    """Get all activities."""
    service = ActivityService(db)
    activities = [
        ActivitySchema.model_validate(a) async for a in service.get_all()
    ]
    return activities


@router.get("/tree", response_model=list[ActivityTreeSchema])
async def get_activity_tree(
    db: AsyncGenerator = Depends(get_authenticated_db),
) -> list[ActivityTreeSchema]:
    """Get all activities as a hierarchical tree."""
    service = ActivityService(db)
    return await service.get_activity_tree()
