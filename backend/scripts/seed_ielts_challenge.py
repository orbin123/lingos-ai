"""Seed the IELTS Sprint challenge catalog and levels."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.challenges.models import Challenge, ChallengeLevel


IELTS_SLUG = "ielts"

_LEVELS = (
    {
        "level_number": 1,
        "name": "Level 1 - Quick Sprint",
        "time_limit_seconds": 1200,
        "pass_threshold": 6.0,
        "config": {
            "sections": {
                "reading": {"num_questions": 4},
                "listening": {"num_questions": 3, "num_clips": 1},
                "writing": {"prompt_count": 1, "target_word_count": 80},
                "speaking": {"num_prompts": 1, "response_seconds": 30},
            }
        },
    },
    {
        "level_number": 2,
        "name": "Level 2 - Standard Sprint",
        "time_limit_seconds": 1800,
        "pass_threshold": 6.5,
        "config": {
            "sections": {
                "reading": {"num_questions": 6},
                "listening": {"num_questions": 4, "num_clips": 1},
                "writing": {"prompt_count": 1, "target_word_count": 120},
                "speaking": {"num_prompts": 2, "response_seconds": 45},
            }
        },
    },
    {
        "level_number": 3,
        "name": "Level 3 - Full Sprint",
        "time_limit_seconds": 2400,
        "pass_threshold": 7.0,
        "config": {
            "sections": {
                "reading": {"num_questions": 8},
                "listening": {"num_questions": 5, "num_clips": 1},
                "writing": {"prompt_count": 2, "target_word_count": 150},
                "speaking": {"num_prompts": 2, "response_seconds": 60},
            }
        },
    },
)

_CHALLENGE = {
    "slug": IELTS_SLUG,
    "name": "IELTS Sprint",
    "short_description": (
        "Timed IELTS-flavoured practice across Listening, Reading, Writing, and Speaking."
    ),
    "rules_md": (
        "## IELTS Sprint rules\n\n"
        "- Complete all four sections before the timer expires.\n"
        "- The timer starts only after you click **Begin Sprint** on the attempt page.\n"
        "- Reading and Listening are scored from answer keys.\n"
        "- Writing and Speaking use AI evaluation (Speaking from transcripts only).\n"
        "- Pass the level threshold to unlock the next level.\n"
        "- You can resume an in-progress attempt from the landing page.\n"
    ),
    "icon": "award",
    "is_active": True,
    "sort_order": 10,
}


def seed_ielts_challenge(db: Session) -> dict[str, int]:
    """Insert or update the IELTS Sprint catalog entry and its levels."""
    inserted = 0
    updated = 0

    challenge = db.query(Challenge).filter_by(slug=IELTS_SLUG).one_or_none()
    if challenge is None:
        challenge = Challenge(**_CHALLENGE)
        db.add(challenge)
        db.flush()
        inserted += 1
    else:
        for key, value in _CHALLENGE.items():
            if getattr(challenge, key) != value:
                setattr(challenge, key, value)
                updated += 1

    existing_levels = {
        level.level_number: level
        for level in db.query(ChallengeLevel).filter_by(challenge_id=challenge.id).all()
    }
    for level_data in _LEVELS:
        existing = existing_levels.get(level_data["level_number"])
        if existing is None:
            db.add(ChallengeLevel(challenge_id=challenge.id, **level_data))
            inserted += 1
            continue
        changed = False
        for key, value in level_data.items():
            if getattr(existing, key) != value:
                setattr(existing, key, value)
                changed = True
        if changed:
            updated += 1

    db.flush()
    return {"inserted": inserted, "updated": updated}
