"""BlogService — orchestrates blog reads and admin mutations.

The service owns commit boundaries; the repository only flushes. Slug
generation/uniqueness and the draft→published transition live here.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.modules.blog.exceptions import BlogNotFound, BlogSlugConflict
from app.modules.blog.models import BLOG_STATUS_PUBLISHED, BlogPost
from app.modules.blog.repository import BlogRepository

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    """Lowercase, hyphenate, trim. Mirrors common CMS slug rules."""
    slug = _SLUG_STRIP.sub("-", value.strip().lower()).strip("-")
    return slug or "post"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class BlogService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = BlogRepository(db)

    # ── public reads ──────────────────────────────────────────────────────

    def list_published(
        self,
        *,
        limit: int | None = None,
        offset: int = 0,
        category: str | None = None,
    ) -> list[BlogPost]:
        return self.repo.list_published(limit=limit, offset=offset, category=category)

    def get_published(self, slug: str) -> BlogPost:
        post = self.repo.get_published_by_slug(slug)
        if post is None:
            raise BlogNotFound(slug)
        return post

    def list_related(self, slug: str, *, limit: int = 3) -> list[BlogPost]:
        return self.repo.list_related(exclude_slug=slug, limit=limit)

    # ── admin reads ───────────────────────────────────────────────────────

    def list_all(self) -> list[BlogPost]:
        return self.repo.list_all()

    def get(self, post_id: int) -> BlogPost:
        post = self.repo.get_by_id(post_id)
        if post is None:
            raise BlogNotFound(post_id)
        return post

    # ── admin writes ──────────────────────────────────────────────────────

    def create(self, data: dict, *, author_id: int | None) -> BlogPost:
        slug = self._resolve_slug(
            requested=data.get("slug"), title=data["title"], exclude_id=None
        )
        status = data.get("status") or "draft"
        post = BlogPost(
            title=data["title"],
            slug=slug,
            excerpt=data.get("excerpt"),
            content=data["content"],
            cover_image_url=data.get("cover_image_url"),
            category=data.get("category"),
            status=status,
            author_id=author_id,
            published_at=_utcnow() if status == BLOG_STATUS_PUBLISHED else None,
        )
        self.repo.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def update(self, post_id: int, fields: dict) -> BlogPost:
        post = self.get(post_id)

        if "slug" in fields or "title" in fields:
            requested = fields.get("slug")
            if requested or "title" in fields:
                post.slug = self._resolve_slug(
                    requested=requested,
                    title=fields.get("title", post.title),
                    exclude_id=post.id,
                    fallback_slug=post.slug,
                )

        for key in ("title", "excerpt", "content", "cover_image_url", "category"):
            if key in fields:
                setattr(post, key, fields[key])

        if "status" in fields and fields["status"] is not None:
            self._apply_status(post, fields["status"])

        self.db.commit()
        self.db.refresh(post)
        return post

    def set_status(self, post_id: int, status: str) -> BlogPost:
        post = self.get(post_id)
        self._apply_status(post, status)
        self.db.commit()
        self.db.refresh(post)
        return post

    def set_cover_image(self, post_id: int, url: str) -> BlogPost:
        post = self.get(post_id)
        post.cover_image_url = url
        self.db.commit()
        self.db.refresh(post)
        return post

    def delete(self, post_id: int) -> None:
        post = self.get(post_id)
        self.repo.delete(post)
        self.db.commit()

    # ── internals ─────────────────────────────────────────────────────────

    def _apply_status(self, post: BlogPost, status: str) -> None:
        post.status = status
        # Stamp the first publish; keep the original date on re-publish.
        if status == BLOG_STATUS_PUBLISHED and post.published_at is None:
            post.published_at = _utcnow()

    def _resolve_slug(
        self,
        *,
        requested: str | None,
        title: str,
        exclude_id: int | None,
        fallback_slug: str | None = None,
    ) -> str:
        base = slugify(requested) if requested else slugify(title)
        # Don't churn the slug if it already resolves to the current value.
        if fallback_slug is not None and base == fallback_slug:
            return fallback_slug
        if not self.repo.slug_exists(base, exclude_id=exclude_id):
            return base
        # An explicitly requested slug that collides is a hard error; an
        # auto-derived one quietly disambiguates with a numeric suffix.
        if requested:
            raise BlogSlugConflict(base)
        for n in range(2, 1000):
            candidate = f"{base}-{n}"
            if not self.repo.slug_exists(candidate, exclude_id=exclude_id):
                return candidate
        raise BlogSlugConflict(base)
