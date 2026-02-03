"""Organisation API routes."""

from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_authenticated_db
from app.api.schemas import (
    ErrorResponseSchema,
    OrganisationSchema,
)
from app.services.organisation_service import OrganisationService

router = APIRouter(prefix="/organisations", tags=["organisations"])


@router.get(
    "/{org_id}",
    response_model=OrganisationSchema,
    responses={
        404: {"model": ErrorResponseSchema, "description": "Not found"},
    },
)
async def get_organisation(
    org_id: int,
    db: AsyncGenerator = Depends(get_authenticated_db),
) -> OrganisationSchema:
    """Get organisation by ID."""
    service = OrganisationService(db)
    org = await service.get_by_id(org_id)
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organisation with id {org_id} not found",
        )
    return OrganisationSchema.model_validate(org)


@router.get(
    "/by-building/{building_id}",
    response_model=list[OrganisationSchema],
)
async def get_organisations_by_building(
    building_id: int,
    db: AsyncGenerator = Depends(get_authenticated_db),
) -> list[OrganisationSchema]:
    """Get all organisations in a building."""
    service = OrganisationService(db)
    organisations = [
        OrganisationSchema.model_validate(org)
        async for org in service.get_by_building(building_id)
    ]
    return organisations


@router.get(
    "/by-activity/{activity_id}",
    response_model=list[OrganisationSchema],
)
async def get_organisations_by_activity(
    activity_id: int,
    db: AsyncGenerator = Depends(get_authenticated_db),
) -> list[OrganisationSchema]:
    """Get organisations by activity (including descendants)."""
    service = OrganisationService(db)
    organisations = [
        OrganisationSchema.model_validate(org)
        async for org in service.get_by_activity(activity_id)
    ]
    return organisations


@router.get(
    "/search",
    response_model=list[OrganisationSchema],
)
async def search_organisations(
    name: str | None = Query(None, description="Search by name"),
    lat: float | None = Query(None, ge=-90, le=90),
    lon: float | None = Query(None, ge=-180, le=180),
    radius_km: float | None = Query(None, gt=0, alias="radius"),
    min_lat: float | None = Query(None, ge=-90, le=90),
    max_lat: float | None = Query(None, ge=-90, le=90),
    min_lon: float | None = Query(None, ge=-180, le=180),
    max_lon: float | None = Query(None, ge=-180, le=180),
    db: AsyncGenerator = Depends(get_authenticated_db),
) -> list[OrganisationSchema]:
    """Search organisations by name and/or geospatial criteria."""
    # Validate search parameters
    if radius_km and (lat is None or lon is None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="lat and lon are required when using radius",
        )

    if any(v is not None for v in [min_lat, max_lat, min_lon, max_lon]):
        if not all(
            v is not None for v in [min_lat, max_lat, min_lon, max_lon]
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All area parameters (min_lat, max_lat, min_lon, max_lon) "
                "are required when using area search",
            )
        if max_lat < min_lat or max_lon < min_lon:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="max_lat must be >= min_lat and max_lon must be >= min_lon",
            )

    service = OrganisationService(db)
    organisations = [
        OrganisationSchema.model_validate(org)
        async for org in service.search(
            name=name,
            lat=lat,
            lon=lon,
            radius_km=radius_km,
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon,
        )
    ]
    return organisations
