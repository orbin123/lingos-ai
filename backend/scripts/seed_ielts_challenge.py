"""Idempotent seeder for the IELTS Sprint challenge.

Usage:
    uv run python -m scripts.seed_ielts_challenge

This creates or updates the challenge catalog row plus its first three levels.
It does not touch user attempts.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Allow `uv run python scripts/seed_ielts_challenge.py` from anywhere.
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from sqlalchemy.orm import Session  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.modules.challenges.models import Challenge, ChallengeLevel  # noqa: E402


logger = logging.getLogger(__name__)


IELTS_RULES_MD = """# IELTS Sprint

IELTS Sprint is IELTS-flavored practice, not a full official mock test.

**No pause allowed. Closing the tab will lose your attempt. Timer is strict.**

Each level includes Listening, Reading, Writing, and Speaking. You can retry
levels as many times as you want; your best-ever band is kept. Level unlocks
are sequential and based on a best-ever band of 6.0 or higher.
"""


LEVELS = (
    {
        "level_number": 1,
        "name": "Level 1 - Quick Sprint",
        "time_limit_seconds": 20 * 60,
        "pass_threshold": 6.0,
        "config": {
            "sections": {
                "listening": {"num_clips": 1, "num_questions": 3},
                "reading": {"passage_word_count": 150, "num_questions": 4},
                "writing": {"prompt_count": 1, "target_word_count": 80},
                "speaking": {"num_prompts": 1, "response_seconds": 30},
            }
        },
    },
    {
        "level_number": 2,
        "name": "Level 2 - Focus Sprint",
        "time_limit_seconds": 30 * 60,
        "pass_threshold": 6.0,
        "config": {
            "sections": {
                "listening": {"num_clips": 1, "num_questions": 5},
                "reading": {"passage_word_count": 250, "num_questions": 6},
                "writing": {"prompt_count": 1, "target_word_count": 120},
                "speaking": {"num_prompts": 2, "response_seconds": 45},
            }
        },
    },
    {
        "level_number": 3,
        "name": "Level 3 - Deep Sprint",
        "time_limit_seconds": 40 * 60,
        "pass_threshold": 6.0,
        "config": {
            "sections": {
                "listening": {"num_clips": 2, "num_questions": 8},
                "reading": {"passage_word_count": 400, "num_questions": 8},
                "writing": {"prompt_count": 2, "target_word_count": 160},
                "speaking": {"num_prompts": 2, "response_seconds": 60},
            }
        },
    },
)


def seed_ielts_challenge(db: Session) -> dict[str, int]:
    """Upsert IELTS Sprint and its first three levels."""
    inserted = updated = 0
    challenge = db.query(Challenge).filter_by(slug="ielts").one_or_none()
    challenge_payload = {
        "name": "IELTS Sprint",
        "short_description": "Timed IELTS-flavored practice across all four sections.",
        "rules_md": IELTS_RULES_MD,
        "icon": "award",
        "is_active": True,
        "sort_order": 10,
    }
    if challenge is None:
        challenge = Challenge(slug="ielts", **challenge_payload)
        db.add(challenge)
        db.flush()
        inserted += 1
    else:
        for field, value in challenge_payload.items():
            setattr(challenge, field, value)
        updated += 1
        db.flush()

    for level_payload in LEVELS:
        level = (
            db.query(ChallengeLevel)
            .filter_by(
                challenge_id=challenge.id,
                level_number=level_payload["level_number"],
            )
            .one_or_none()
        )
        if level is None:
            db.add(ChallengeLevel(challenge_id=challenge.id, **level_payload))
            inserted += 1
        else:
            for field, value in level_payload.items():
                setattr(level, field, value)
            updated += 1

    db.flush()
    return {"inserted": inserted, "updated": updated}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    with SessionLocal() as db:
        try:
            report = seed_ielts_challenge(db)
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("IELTS challenge seed failed - rolled back")
            raise
    logger.info("IELTS challenge seed complete: %s", report)


if __name__ == "__main__":
    main()
