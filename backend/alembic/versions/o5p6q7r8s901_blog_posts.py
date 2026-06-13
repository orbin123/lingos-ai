"""add blog_posts table (+ seed example posts)

Revision ID: o5p6q7r8s901
Revises: n4o5p6q7r890
Create Date: 2026-06-13 12:00:00.000000

Adds the blog CMS table for the marketing site:

- blog_posts: Markdown articles, slug-addressed, draft/published lifecycle.
  status stays a plain string + CheckConstraint (no DB enum) for SQLite test
  compatibility, consistent with the other status columns in this codebase.
- author_id is a soft FK (ON DELETE SET NULL) so removing a user keeps the
  article and falls back to a house byline.

Two example posts (from docs/rest_pages.md) are seeded as published so the
public /blog page renders immediately.
"""

from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "o5p6q7r8s901"
down_revision: Union[str, Sequence[str], None] = "n4o5p6q7r890"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_POST_1_CONTENT = """\
Most English learners don't fail because they lack effort. They fail because
the tools they use are built for everyone — and therefore for no one in
particular.

## The problem with generic apps

Generic language apps hand every learner the same deck of exercises. They
can't see *your* recurring mistakes, *your* level, or *your* goals. So you
drill vocabulary you already know and skip the structures you actually
struggle with.

## What personalized coaching does differently

- **Diagnoses first.** It measures your real strengths and weaknesses across
  grammar, fluency, pronunciation, and idea organization.
- **Targets the gaps.** Daily tasks are generated for *your* weak sub-skills,
  not a fixed syllabus.
- **Closes the loop.** Every answer gets specific, actionable feedback — and
  the system remembers your patterns so it can coach the same mistake until
  it's gone.

Learning a language is a feedback problem. Solve the feedback, and the
progress follows.
"""

_POST_2_CONTENT = """\
Grammar matters — but it's rarely the thing standing between you and confident
communication. These seven skills carry far more weight in real conversations.

## 1. Confidence
Hesitation reads louder than a misplaced article. Speaking up — imperfectly —
beats staying silent.

## 2. Fluency
Smooth, connected speech keeps a listener with you even when the grammar
wobbles.

## 3. Idea generation
Knowing *what* to say, quickly, is half of communication. Structure your
thoughts before you reach for perfect words.

## 4. Tone
The same sentence can be warm, neutral, or rude. Tone is what people actually
remember.

## 5. Listening
You can't respond well to what you didn't catch. Active listening shapes every
reply.

## 6. Clarity
Short, well-ordered sentences out-communicate long, "correct" ones.

## 7. Pronunciation
Not an accent — just being *understood* the first time.

Master these and your grammar has room to catch up while you're already
communicating well.
"""


def upgrade() -> None:
    op.create_table(
        "blog_posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("excerpt", sa.String(length=500), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("cover_image_url", sa.String(length=500), nullable=True),
        sa.Column("category", sa.String(length=80), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "author_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'published')", name="ck_blog_posts_status"
        ),
    )
    op.create_index(
        op.f("ix_blog_posts_slug"), "blog_posts", ["slug"], unique=True
    )
    op.create_index(op.f("ix_blog_posts_author_id"), "blog_posts", ["author_id"])

    # ── Seed the two example posts ────────────────────────────────────────
    blog_posts = sa.table(
        "blog_posts",
        sa.column("title", sa.String),
        sa.column("slug", sa.String),
        sa.column("excerpt", sa.String),
        sa.column("content", sa.Text),
        sa.column("cover_image_url", sa.String),
        sa.column("category", sa.String),
        sa.column("status", sa.String),
        sa.column("published_at", sa.DateTime(timezone=True)),
        sa.column("author_id", sa.Integer),
    )
    op.bulk_insert(
        blog_posts,
        [
            {
                "title": "Why Traditional English Learning Fails Most Learners",
                "slug": "why-traditional-english-learning-fails-most-learners",
                "excerpt": (
                    "Generic language apps give everyone the same exercises. "
                    "Here's why personalized coaching changes the outcome."
                ),
                "content": _POST_1_CONTENT,
                "cover_image_url": None,
                "category": "Learning Strategy",
                "status": "published",
                "published_at": datetime(2026, 6, 10, 9, 0, tzinfo=timezone.utc),
                "author_id": None,
            },
            {
                "title": "7 Communication Skills That Matter More Than Grammar",
                "slug": "7-communication-skills-that-matter-more-than-grammar",
                "excerpt": (
                    "Confidence, fluency, idea generation, tone, and more — the "
                    "skills that actually decide whether you're understood."
                ),
                "content": _POST_2_CONTENT,
                "cover_image_url": None,
                "category": "Communication",
                "status": "published",
                "published_at": datetime(2026, 6, 5, 9, 0, tzinfo=timezone.utc),
                "author_id": None,
            },
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_blog_posts_author_id"), table_name="blog_posts")
    op.drop_index(op.f("ix_blog_posts_slug"), table_name="blog_posts")
    op.drop_table("blog_posts")
