"""Pydantic shapes for the blog REST API.

Three read shapes by audience:
  - `BlogPostListItem`  — public card (list/grid/featured/related)
  - `BlogPostRead`      — public detail (adds content + author byline)
  - `BlogPostAdminRead` — admin console (adds status/timestamps/author_id)
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

BlogStatusLiteral = Literal["draft", "published"]


# ── Read shapes ───────────────────────────────────────────────────────────


class BlogPostListItem(BaseModel):
    """Compact card shown on the public list, featured, and related rails."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    excerpt: str | None
    cover_image_url: str | None
    category: str | None
    published_at: datetime | None


class BlogPostRead(BlogPostListItem):
    """Full public detail payload."""

    content: str
    author_name: str


class BlogPostAdminRead(BaseModel):
    """Everything the admin console needs, drafts included."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    excerpt: str | None
    content: str
    cover_image_url: str | None
    category: str | None
    status: BlogStatusLiteral
    published_at: datetime | None
    author_id: int | None
    author_name: str
    created_at: datetime
    updated_at: datetime


# ── Write shapes ──────────────────────────────────────────────────────────


class BlogPostCreate(BaseModel):
    """Body for `POST /admin/blog`. Slug auto-derived from title when omitted."""

    title: str = Field(..., min_length=1, max_length=200)
    slug: str | None = Field(default=None, max_length=200)
    excerpt: str | None = Field(default=None, max_length=500)
    content: str = Field(..., min_length=1)
    cover_image_url: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=80)
    status: BlogStatusLiteral = "draft"


class BlogPostUpdate(BaseModel):
    """Body for `PATCH /admin/blog/{id}` — every field optional."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, max_length=200)
    excerpt: str | None = Field(default=None, max_length=500)
    content: str | None = Field(default=None, min_length=1)
    cover_image_url: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=80)
    status: BlogStatusLiteral | None = None
