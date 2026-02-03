"""Building API routes."""

from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends

from app.api.dependencies import get_authenticated_db
from app.api.schemas import BuildingSchema
from app.services.building_service import BuildingService

router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.get("", response_model=list[BuildingSchema])
async def get_buildings(
    db: AsyncGenerator = Depends(get_authenticated_db),
) -> list[BuildingSchema]:
    """Get all buildings."""
    service = BuildingService(db)
    buildings = [
        BuildingSchema.model_validate(b) async for b in service.get_all()
    ]
    return buildings
