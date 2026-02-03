"""Organisation model with relationships to building and activities."""

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.activity import Activity
    from app.models.building import Building


# Junction table for Organisation-Activity many-to-many relationship
organisation_activities = Table(
    "organisation_activities",
    Base.metadata,
    Column(
        "organisation_id",
        Integer,
        ForeignKey("organisations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "activity_id",
        Integer,
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Organisation(Base):
    """Organisation entity with building, phones, and activities."""

    __tablename__ = "organisations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    building_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("buildings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    building: Mapped["Building"] = relationship(
        "Building",
        back_populates="organisations",
    )
    phones: Mapped[list["OrganisationPhone"]] = relationship(
        "OrganisationPhone",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )
    activities: Mapped[list["Activity"]] = relationship(
        "Activity",
        secondary=organisation_activities,
        back_populates="organisations",
    )

    def __repr__(self) -> str:
        return f"<Organisation(id={self.id}, name='{self.name}')>"


class OrganisationPhone(Base):
    """Phone numbers for organisations."""

    __tablename__ = "organisation_phones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organisation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)

    organisation: Mapped[Organisation] = relationship(
        "Organisation",
        back_populates="phones",
    )

    def __repr__(self) -> str:
        return (
            f"<OrganisationPhone(id={self.id}, phone='{self.phone_number}')>"
        )
