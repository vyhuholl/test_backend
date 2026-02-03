"""Building model with geospatial data."""

from typing import TYPE_CHECKING

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.organisation import Organisation


class Building(Base):
    """Building entity with address and geospatial coordinates."""

    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    organisations: Mapped[list["Organisation"]] = relationship(
        "Organisation",
        back_populates="building",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Building(id={self.id}, address='{self.address}', "
            f"lat={self.latitude}, lon={self.longitude})>"
        )
