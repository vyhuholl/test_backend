"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel, Field, field_validator


class ActivitySchema(BaseModel):
    """Schema for activity responses."""

    id: int
    name: str
    parent_id: int | None = None

    class Config:
        from_attributes = True


class ActivityTreeSchema(BaseModel):
    """Schema for activity tree responses."""

    id: int
    name: str
    children: list["ActivityTreeSchema"] = []

    class Config:
        from_attributes = True


class BuildingSchema(BaseModel):
    """Schema for building responses."""

    id: int
    address: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    class Config:
        from_attributes = True


class OrganisationPhoneSchema(BaseModel):
    """Schema for organisation phone responses."""

    id: int
    phone_number: str

    class Config:
        from_attributes = True


class OrganisationSchema(BaseModel):
    """Schema for organisation responses."""

    id: int
    name: str
    building: BuildingSchema
    phones: list[OrganisationPhoneSchema]
    activities: list[ActivitySchema]

    class Config:
        from_attributes = True


class SearchQuerySchema(BaseModel):
    """Schema for search query parameters."""

    name: str | None = None
    lat: float | None = Field(None, ge=-90, le=90)
    lon: float | None = Field(None, ge=-180, le=180)
    radius_km: float | None = Field(None, gt=0)
    min_lat: float | None = Field(None, ge=-90, le=90)
    max_lat: float | None = Field(None, ge=-90, le=90)
    min_lon: float | None = Field(None, ge=-180, le=180)
    max_lon: float | None = Field(None, ge=-180, le=180)

    @field_validator("max_lat")
    @classmethod
    def validate_lat_range(cls, v: float | None, info) -> float | None:
        """Validate that max_lat >= min_lat if both are provided."""
        if v is not None and info.data.get("min_lat") is not None:
            if v < info.data["min_lat"]:
                raise ValueError("max_lat must be >= min_lat")
        return v

    @field_validator("max_lon")
    @classmethod
    def validate_lon_range(cls, v: float | None, info) -> float | None:
        """Validate that max_lon >= min_lon if both are provided."""
        if v is not None and info.data.get("min_lon") is not None:
            if v < info.data["min_lon"]:
                raise ValueError("max_lon must be >= min_lon")
        return v


class ErrorResponseSchema(BaseModel):
    """Schema for error responses."""

    detail: str


# Update forward references
ActivityTreeSchema.model_rebuild()
