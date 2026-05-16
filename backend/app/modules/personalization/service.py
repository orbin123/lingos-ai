"""PersonalizationService — orchestrates extraction + cache write +
DailyPlan invalidation.

Triggered from:
- profile PATCH (when personalisation fields change)
- diagnosis completion (since diagnosis writes profile fields)

The service is best-effort: any LLM or DB failure is logged and swallowed
so a transient extraction error never blocks a profile save.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.ai.agents.personalization import extract_structured_personalisation
from app.modules.auth.models import UserProfile
from app.modules.auth.repository import UserProfileRepository
from app.modules.curriculum.repository import DailyPlanRepository
from app.modules.personalization.schemas import (
    StructuredPersonalisation,
    empty_personalisation,
    fallback_personalisation,
)

logger = logging.getLogger(__name__)


def _profile_to_extraction_input(profile: UserProfile) -> dict[str, Any]:
    """Map the SQLAlchemy model into the dict shape the agent expects."""
    return {
        "personalisation_context": profile.personalisation_context or "",
        "primary_goals": profile.primary_goals or "",
        "interests": profile.interests or "",
        "goal": profile.goal.value if profile.goal is not None else "",
        "native_language": profile.native_language or "",
        "country": profile.country or "",
        "self_assessed_level": (
            profile.self_assessed_level.value
            if profile.self_assessed_level is not None
            else ""
        ),
    }


class PersonalizationService:
    """High-level entry point for personalization refresh.

    Usage:
        await PersonalizationService(db).refresh_for_user(user_id)

    Idempotent. Safe to call after every relevant profile mutation —
    overlapping calls just produce two extractions; last write wins.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self._profile_repo = UserProfileRepository(db)
        self._plan_repo = DailyPlanRepository(db)

    async def refresh_for_user(
        self, user_id: int
    ) -> StructuredPersonalisation | None:
        """Re-extract structured personalisation for one user and invalidate
        their cached daily plans.

        Returns the new payload, or None if the user has no profile.
        """
        profile = self._profile_repo.get_by_user_id(user_id)
        if profile is None:
            logger.info("personalization_refresh_skipped_no_profile user_id=%s", user_id)
            return None

        extraction_input = _profile_to_extraction_input(profile)

        try:
            structured = await extract_structured_personalisation(
                profile=extraction_input
            )
        except Exception:
            # Defence in depth — the agent already has its own fallback,
            # but if something truly catastrophic happens we still want a
            # complete row written so downstream agents don't blow up.
            logger.exception(
                "personalization_extraction_unexpected_failure user_id=%s", user_id
            )
            structured = fallback_personalisation()

        payload = structured.model_dump(mode="json")

        try:
            self._profile_repo.set_structured_personalisation(
                user_id=user_id, payload=payload
            )
        except Exception:
            logger.exception(
                "personalization_persist_failed user_id=%s", user_id
            )
            return structured

        # Cached plans were built under the old personalisation. Wipe them so
        # the next session generates fresh, personalised plans. Lazy regen
        # means we don't pay any LLM cost until the user actually opens
        # their next lesson.
        try:
            wiped = self._plan_repo.delete_for_user(user_id=user_id)
            if wiped:
                logger.info(
                    "personalization_invalidated_daily_plans user_id=%s wiped=%s",
                    user_id, wiped,
                )
        except Exception:
            logger.exception(
                "personalization_plan_invalidation_failed user_id=%s", user_id
            )

        return structured

    async def write_empty_default(self, user_id: int) -> StructuredPersonalisation | None:
        """Seed an empty default for a brand-new user without calling the LLM.

        Useful right after signup so downstream agents always read a
        complete object instead of NULL.
        """
        structured = empty_personalisation()
        try:
            self._profile_repo.set_structured_personalisation(
                user_id=user_id, payload=structured.model_dump(mode="json")
            )
        except Exception:
            logger.exception(
                "personalization_empty_default_failed user_id=%s", user_id
            )
            return None
        return structured
