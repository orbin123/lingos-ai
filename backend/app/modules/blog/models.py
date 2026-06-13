"""ORM model for blog posts (the marketing-site CMS)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.mixins import IDMixin, TimestampMixin

# The two lifecycle states. Kept as a plain string column + CheckConstraint
# (not a DB enum) for SQLite test compatibility and consistency with the
# other status columns in this codebase (see the email/billing migration).
BLOG_STATUS_DRAFT = "draft"
BLOG_STATUS_PUBLISHED = "published"
BLOG_STATUSES = (BLOG_STATUS_DRAFT, BLOG_STATUS_PUBLISHED)


class BlogPost(Base, IDMixin, TimestampMixin):
    """A single blog article. Markdown content, slug-addressed."""

    __tablename__ = "blog_posts"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'published')",
            name="ck_blog_posts_status",
        ),
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(200), nullable=False, unique=True, index=True
    )
    excerpt: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=BLOG_STATUS_DRAFT, server_default="draft"
    )
    # Set when the post first becomes published; preserved across edits.
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Author kept as a soft FK: deleting the user nulls the column rather than
    # cascading away the article. Read paths fall back to a house byline.
    author_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    author = relationship("User", lazy="selectin")

    @property
    def author_name(self) -> str:
        """Display byline. Falls back to a house name when the author row is
        gone (FK nulled) or unset. Read by Pydantic via `from_attributes`."""
        if self.author is not None and self.author.name:
            return self.author.name
        return "LingosAI Team"

    def __repr__(self) -> str:
        return f"<BlogPost(id={self.id}, slug={self.slug!r}, status={self.status!r})>"
