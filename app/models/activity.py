"""Activity model with hierarchical structure."""

from typing import TYPE_CHECKING, Self

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.organisation import Organisation


class Activity(Base):
    """Activity entity with hierarchical structure (max 3 levels)."""

    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    parent: Mapped[Self | None] = relationship(
        "Activity",
        back_populates="children",
        remote_side=[id],
    )
    children: Mapped[list[Self]] = relationship(
        "Activity",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    organisations: Mapped[list["Organisation"]] = relationship(
        "Organisation",
        secondary="organisation_activities",
        back_populates="activities",
    )

    def get_descendants(self) -> list[Self]:
        """Get all descendant activities recursively."""
        descendants: list[Self] = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

    def get_level(self) -> int:
        """Get the nesting level of this activity (0 = top level)."""
        level = 0
        current = self
        while current.parent is not None:
            level += 1
            current = current.parent
            if level >= 3:
                break
        return level

    def __repr__(self) -> str:
        return f"<Activity(id={self.id}, name='{self.name}')>"
