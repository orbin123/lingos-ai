"""Business logic for the feedback-prompt system.

Three collaborators, each constructed per-request with a DB session (mirrors
``SubscriptionService(db)``):

  FeedbackEligibilityService — has the user earned the right to be asked?
  FeedbackPromptService       — cooldowns + randomized display + recording.
  FeedbackAnalyticsService    — admin aggregates over reviews + prompt logs.

Services own their commits at logical boundaries; repositories never commit.
"""

from __future__ import annotations

import random
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.feedback import constants as C
from app.modules.feedback.repository import FeedbackPromptRepository
from app.modules.feedback.schemas import (
    FeedbackSubmit,
    ReviewStats,
    ReviewTrendPoint,
    ShouldShowResponse,
    ThemeCount,
)
from app.modules.reviews.repository import AppReviewRepository


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_aware(dt: datetime) -> datetime:
    """Treat naive timestamps (SQLite round-trips) as UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@dataclass(frozen=True)
class EligibilityResult:
    eligible: bool
    trigger_type: str | None


class FeedbackEligibilityService:
    """Decides whether a user has experienced enough value to be asked."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = FeedbackPromptRepository(db)

    def evaluate(self, user: User, *, now: datetime | None = None) -> EligibilityResult:
        """First condition met (in priority order) wins."""
        now = now or _utcnow()

        # 1. Completed learning tasks.
        if self.repo.completed_task_count(user.id) >= C.ELIGIBLE_COMPLETED_TASKS:
            return EligibilityResult(True, C.TRIGGER_TASK_MILESTONE)

        # 2. Reached Day 3 since signup.
        created = _as_aware(user.created_at)
        if now - created >= timedelta(days=C.ELIGIBLE_DAYS_SINCE_SIGNUP):
            return EligibilityResult(True, C.TRIGGER_DAY_3)

        # 3. Received N AI feedback reports.
        if self.repo.feedback_report_count(user.id) >= C.ELIGIBLE_FEEDBACK_REPORTS:
            return EligibilityResult(True, C.TRIGGER_FEEDBACK_REPORTS)

        # 4. Accumulated learning minutes.
        if self.repo.active_minutes(user.id) >= C.ELIGIBLE_ACTIVE_MINUTES:
            return EligibilityResult(True, C.TRIGGER_TIME_SPENT)

        return EligibilityResult(False, None)


class FeedbackPromptService:
    """Cooldowns, randomized display, and recording submit/dismiss."""

    def __init__(self, db: Session, *, rng: random.Random | None = None) -> None:
        self.db = db
        self.repo = FeedbackPromptRepository(db)
        self.reviews = AppReviewRepository(db)
        self.eligibility = FeedbackEligibilityService(db)
        self._rng = rng or random

    def _in_cooldown(self, user: User, now: datetime) -> bool:
        submitted_at = self.repo.last_submitted_at(user.id)
        if submitted_at is not None and now - _as_aware(submitted_at) < timedelta(
            days=C.SUBMIT_COOLDOWN_DAYS
        ):
            return True
        dismissed_at = self.repo.last_dismissed_at(user.id)
        if dismissed_at is not None and now - _as_aware(dismissed_at) < timedelta(
            days=C.DISMISS_COOLDOWN_DAYS
        ):
            return True
        return False

    def should_show(
        self, user: User, *, now: datetime | None = None
    ) -> ShouldShowResponse:
        now = now or _utcnow()

        # 1. Cooldown gate.
        if self._in_cooldown(user, now):
            return ShouldShowResponse(show=False, trigger_type=None)

        # 2. Eligibility gate.
        result = self.eligibility.evaluate(user, now=now)
        if not result.eligible:
            return ShouldShowResponse(show=False, trigger_type=None)

        # 3. Randomized display. Only log a prompt when we actually show it.
        if self._rng.random() >= C.SHOW_PROBABILITY:
            return ShouldShowResponse(show=False, trigger_type=None)

        self.repo.create_log(
            user_id=user.id,
            prompted_at=now,
            trigger_type=result.trigger_type or C.TRIGGER_TASK_MILESTONE,
        )
        self.db.commit()
        return ShouldShowResponse(show=True, trigger_type=result.trigger_type)

    def record_submit(
        self, user: User, payload: FeedbackSubmit, *, now: datetime | None = None
    ):
        now = now or _utcnow()

        title, body = _synthesize_title_body(payload)
        days_since_signup = max(0, (now - _as_aware(user.created_at)).days)
        review = self.reviews.create(
            user_id=user.id,
            rating=payload.rating,
            title=title,
            body=body,
            positive_feedback=payload.positive_feedback,
            improvement_feedback=payload.improvement_feedback,
            bug_report=payload.bug_report,
            task_count_when_submitted=self.repo.completed_task_count(user.id),
            days_since_signup=days_since_signup,
            app_version=payload.app_version,
        )

        # Close out the open prompt (or record a synthetic one so the 30-day
        # cooldown still applies for direct submissions).
        log = self.repo.latest_open_prompt(user.id)
        if log is None:
            log = self.repo.create_log(
                user_id=user.id,
                prompted_at=now,
                trigger_type=C.TRIGGER_TASK_MILESTONE,
            )
        log.submitted = True

        self.db.commit()
        self.db.refresh(review)
        return review

    def record_dismiss(self, user: User, *, now: datetime | None = None) -> None:
        now = now or _utcnow()
        log = self.repo.latest_open_prompt(user.id)
        if log is None:
            log = self.repo.create_log(
                user_id=user.id,
                prompted_at=now,
                trigger_type=C.TRIGGER_TASK_MILESTONE,
            )
        log.dismissed = True
        self.db.commit()


class FeedbackAnalyticsService:
    """Read-only aggregates for the admin User Reviews page."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.reviews = AppReviewRepository(db)
        self.prompts = FeedbackPromptRepository(db)

    def stats(self, *, now: datetime | None = None) -> ReviewStats:
        now = now or _utcnow()
        since = now - timedelta(days=C.TREND_WINDOW_DAYS)

        total = self.reviews.count()
        avg = self.reviews.average_rating()
        distribution = self.reviews.rating_distribution()

        prompts_shown, prompts_submitted = self.prompts.prompt_totals()
        submission_rate = (
            prompts_submitted / prompts_shown if prompts_shown else None
        )

        improvements: list[str] = []
        bugs: list[str] = []
        for improvement, bug in self.reviews.text_fields_since():
            if improvement:
                improvements.append(improvement)
            if bug:
                bugs.append(bug)

        return ReviewStats(
            total_reviews=total,
            average_rating=round(float(avg), 2) if avg is not None else None,
            rating_distribution=distribution,
            submission_rate=(
                round(submission_rate, 3) if submission_rate is not None else None
            ),
            prompts_shown=prompts_shown,
            prompts_submitted=prompts_submitted,
            top_improvements=_top_themes(improvements),
            top_bugs=_top_themes(bugs),
            trend=_build_trend(self.reviews.trend_rows(since)),
        )


# ── Helpers ────────────────────────────────────────────────────────


def _synthesize_title_body(payload: FeedbackSubmit) -> tuple[str | None, str]:
    """Build legacy title/body so older readers still render something useful."""
    sections: list[str] = []
    if payload.positive_feedback:
        sections.append(f"Likes: {payload.positive_feedback.strip()}")
    if payload.improvement_feedback:
        sections.append(f"Improve: {payload.improvement_feedback.strip()}")
    if payload.bug_report:
        sections.append(f"Bugs: {payload.bug_report.strip()}")
    body = "\n\n".join(sections)
    title = f"{payload.rating}★ review"
    return title, body


# Words too common to be a useful "theme".
_STOPWORDS = frozenset(
    {
        "the", "and", "for", "you", "your", "are", "but", "not", "with", "this",
        "that", "have", "has", "was", "were", "can", "could", "would", "should",
        "more", "less", "very", "really", "just", "some", "any", "all", "from",
        "they", "them", "what", "when", "which", "there", "their", "about",
        "into", "than", "then", "also", "like", "want", "need", "make", "made",
        "it's", "its", "app", "lingos", "please", "would", "thing", "things",
    }
)

_WORD_RE = re.compile(r"[a-z']{3,}")


def _top_themes(entries: list[str], *, top_n: int = 8) -> list[ThemeCount]:
    """Deterministic word-frequency tally across free-text entries."""
    counter: Counter[str] = Counter()
    for entry in entries:
        for word in _WORD_RE.findall(entry.lower()):
            if word in _STOPWORDS:
                continue
            counter[word] += 1
    # Sort by count desc, then word asc for stable output.
    ranked = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
    return [ThemeCount(text=word, count=n) for word, n in ranked[:top_n]]


def _build_trend(rows: list[tuple[datetime, int]]) -> list[ReviewTrendPoint]:
    """Bucket (created_at, rating) rows by calendar day (UTC)."""
    buckets: dict[date, list[int]] = {}
    for created_at, rating in rows:
        day = _as_aware(created_at).date()
        buckets.setdefault(day, []).append(rating)
    points = []
    for day in sorted(buckets):
        ratings = buckets[day]
        points.append(
            ReviewTrendPoint(
                date=day,
                count=len(ratings),
                average_rating=round(sum(ratings) / len(ratings), 2),
            )
        )
    return points
