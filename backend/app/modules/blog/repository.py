"""Read/write helpers for `BlogPost`. No business logic, flush (not commit)."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.blog.models import BLOG_STATUS_PUBLISHED, BlogPost


class BlogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ── reads ─────────────────────────────────────────────────────────────

    def get_by_id(self, post_id: int) -> BlogPost | None:
        return self.db.get(BlogPost, post_id)

    def get_by_slug(self, slug: str) -> BlogPost | None:
        return self.db.execute(
            select(BlogPost).where(BlogPost.slug == slug)
        ).scalar_one_or_none()

    def get_published_by_slug(self, slug: str) -> BlogPost | None:
        return self.db.execute(
            select(BlogPost).where(
                BlogPost.slug == slug,
                BlogPost.status == BLOG_STATUS_PUBLISHED,
            )
        ).scalar_one_or_none()

    def list_published(
        self,
        *,
        limit: int | None = None,
        offset: int = 0,
        category: str | None = None,
    ) -> list[BlogPost]:
        stmt = (
            select(BlogPost)
            .where(BlogPost.status == BLOG_STATUS_PUBLISHED)
            # Newest first; fall back to created_at when published_at is null.
            .order_by(
                func.coalesce(BlogPost.published_at, BlogPost.created_at).desc(),
                BlogPost.id.desc(),
            )
            .offset(offset)
        )
        if category:
            stmt = stmt.where(BlogPost.category == category)
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def list_related(self, *, exclude_slug: str, limit: int = 3) -> list[BlogPost]:
        stmt = (
            select(BlogPost)
            .where(
                BlogPost.status == BLOG_STATUS_PUBLISHED,
                BlogPost.slug != exclude_slug,
            )
            .order_by(
                func.coalesce(BlogPost.published_at, BlogPost.created_at).desc(),
                BlogPost.id.desc(),
            )
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_all(self) -> list[BlogPost]:
        """Admin view — every post regardless of status, newest first."""
        return list(
            self.db.execute(
                select(BlogPost).order_by(BlogPost.created_at.desc(), BlogPost.id.desc())
            )
            .scalars()
            .all()
        )

    def slug_exists(self, slug: str, *, exclude_id: int | None = None) -> bool:
        stmt = select(BlogPost.id).where(BlogPost.slug == slug)
        if exclude_id is not None:
            stmt = stmt.where(BlogPost.id != exclude_id)
        return self.db.execute(stmt.limit(1)).first() is not None

    # ── writes (flush only — service owns commit) ─────────────────────────

    def add(self, post: BlogPost) -> BlogPost:
        self.db.add(post)
        self.db.flush()
        return post

    def delete(self, post: BlogPost) -> None:
        self.db.delete(post)
        self.db.flush()
