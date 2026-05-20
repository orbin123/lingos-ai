"""Skill module models — master table of the 7 tracked sub-skills."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import CreatedAtMixin, IDMixin


class Skill(Base, IDMixin, CreatedAtMixin):
    """
    Master table for the 7 sub-skills tracked by the system.

    Pre-seeded once. Rarely changes. Only created_at, no updated_at.
    """

    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    display_label: Mapped[str] = mapped_column(
        String(60), nullable=False, default=""
    )

    def __repr__(self) -> str:
        return f"<Skill(id={self.id}, name={self.name!r})>"