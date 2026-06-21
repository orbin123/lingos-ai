"""Idempotent seeder for the A2Z Challenge.

Usage:
    uv run python -m scripts.seed_a2z_challenge

This creates or updates the challenge catalog row plus its three levels.
It does not touch user attempts or progress.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Allow `uv run python scripts/seed_a2z_challenge.py` from anywhere.
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from sqlalchemy.orm import Session  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.modules.challenges.models import Challenge, ChallengeLevel  # noqa: E402


logger = logging.getLogger(__name__)


A2Z_RULES_MD = """# A2Z Challenge

Name as many words as you can starting with a given letter before time runs out!

**Rules:**
- Each round gives you one letter from the alphabet (Q and X excluded).
- You must say words that start with that letter.
- Duplicate words are counted only once.
- Clear all 24 letters on a level to advance to the next.
- Three levels: Warm-up → Stride → Fluency, each requiring more words in more time.
- Complete all three levels to finish the challenge. You can restart once complete.
"""


LEVELS = (
    {
        "level_number": 1,
        "name": "Warm-up",
        "time_limit_seconds": 25,
        "pass_threshold": 1.0,
        "config": {
            "game": "a2z",
            "target_words": 10,
            "round_time_seconds": 25,
            "letters": [
                "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
                "M", "N", "O", "P", "R", "S", "T", "U", "V", "W", "Y", "Z",
            ],
            "exclude_letters": ["Q", "X"],
        },
    },
    {
        "level_number": 2,
        "name": "Stride",
        "time_limit_seconds": 32,
        "pass_threshold": 1.0,
        "config": {
            "game": "a2z",
            "target_words": 15,
            "round_time_seconds": 32,
            "letters": [
                "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
                "M", "N", "O", "P", "R", "S", "T", "U", "V", "W", "Y", "Z",
            ],
            "exclude_letters": ["Q", "X"],
        },
    },
    {
        "level_number": 3,
        "name": "Fluency",
        "time_limit_seconds": 45,
        "pass_threshold": 1.0,
        "config": {
            "game": "a2z",
            "target_words": 22,
            "round_time_seconds": 45,
            "letters": [
                "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
                "M", "N", "O", "P", "R", "S", "T", "U", "V", "W", "Y", "Z",
            ],
            "exclude_letters": ["Q", "X"],
        },
    },
)


def seed_a2z_challenge(db: Session) -> dict[str, int]:
    """Upsert A2Z Challenge and its three levels."""
    inserted = updated = 0
    challenge = db.query(Challenge).filter_by(slug="a2z").one_or_none()
    challenge_payload = {
        "name": "A2Z Challenge",
        "short_description": "Name words starting with each letter of the alphabet against the clock.",
        "rules_md": A2Z_RULES_MD,
        "icon": "grid",
        "is_active": True,
        "sort_order": 20,
    }
    if challenge is None:
        challenge = Challenge(slug="a2z", **challenge_payload)
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
            report = seed_a2z_challenge(db)
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("A2Z challenge seed failed - rolled back")
            raise
    logger.info("A2Z challenge seed complete: %s", report)


if __name__ == "__main__":
    main()
