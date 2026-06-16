"""Calibrate the LLM-as-judge against learner reactions (Part B Phase 3).

The judge is also an LLM, so it is also wrong sometimes. Before trusting its
numbers, check that it agrees with the humans who actually reacted to feedback
in ``feedback_reactions``. This script joins each stored ``ai_evaluations`` row
to its learner reaction (polymorphic: ``feedback`` → ``activity_feedback``
reacted to as ``feedback_type="ACTIVITY_FEEDBACK"``; ``mentor_note`` →
``session_scorecards`` reacted to as ``feedback_type="COACH_NOTE"``) and reports
agreement: does the judge's "any axis < 6" flag line up with a learner DISLIKE?

A learner DISLIKE is the human "flag" signal; a LIKE is a pass. It only
reports — it never auto-tunes. Disagreement means the rubric needs a human's
attention, not an automatic change.

Usage:
    uv run python -m scripts.calibrate_judge
    uv run python -m scripts.calibrate_judge --limit 100
"""

from __future__ import annotations

import argparse
import dataclasses
import logging
import sys
from pathlib import Path

# Allow `uv run python scripts/calibrate_judge.py` from anywhere.
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from sqlalchemy.orm import Session  # noqa: E402

from app.modules.admin.models import AIEvaluation  # noqa: E402
from app.modules.sessions.models import (  # noqa: E402
    FeedbackReaction,
    FeedbackType,
    ReactionValue,
)

logger = logging.getLogger(__name__)

FLAG_THRESHOLD = 6.0
_AXES = ("accuracy", "relevance", "helpfulness", "correctness", "faithfulness")
# ai_evaluations.target_type -> feedback_reactions.feedback_type
_TARGET_TO_REACTION_TYPE = {
    "feedback": FeedbackType.ACTIVITY_FEEDBACK.value,
    "mentor_note": FeedbackType.COACH_NOTE.value,
}


@dataclasses.dataclass
class CalibrationReport:
    judged_total: int          # rows scored by the judge
    matched: int               # rows with a non-pending human review
    agree: int                 # judge flag == human flag
    # confusion (positive = "flag"):
    true_pos: int              # judge flag & human flag
    false_pos: int             # judge flag & human pass
    true_neg: int              # judge pass & human pass
    false_neg: int             # judge pass & human flag (the dangerous miss)

    @property
    def agreement_rate(self) -> float:
        return round(self.agree / self.matched, 3) if self.matched else 0.0


def _judge_flags(row: AIEvaluation) -> bool:
    """The judge "flags" a row when any scored axis is below the threshold."""
    for axis in _AXES:
        val = getattr(row, axis)
        if val is not None and float(val) < FLAG_THRESHOLD:
            return True
    return False


def calibrate(db: Session, *, limit: int = 200) -> CalibrationReport:
    evals = (
        db.query(AIEvaluation)
        .order_by(AIEvaluation.created_at.desc())
        .limit(limit)
        .all()
    )

    matched = agree = tp = fp = tn = fn = 0
    for ev in evals:
        reaction_type = _TARGET_TO_REACTION_TYPE.get(ev.target_type)
        if reaction_type is None or ev.target_id is None:
            continue
        try:
            feedback_id = int(ev.target_id)
        except (TypeError, ValueError):
            continue

        reaction = (
            db.query(FeedbackReaction)
            .filter(
                FeedbackReaction.feedback_type == reaction_type,
                FeedbackReaction.feedback_id == feedback_id,
            )
            .first()
        )
        # No human verdict yet (the learner never reacted) — nothing to compare.
        if reaction is None:
            continue

        human_flag = reaction.reaction == ReactionValue.DISLIKE.value
        judge_flag = _judge_flags(ev)
        matched += 1
        if judge_flag == human_flag:
            agree += 1
        if judge_flag and human_flag:
            tp += 1
        elif judge_flag and not human_flag:
            fp += 1
        elif not judge_flag and not human_flag:
            tn += 1
        else:
            fn += 1

    return CalibrationReport(
        judged_total=len(evals),
        matched=matched,
        agree=agree,
        true_pos=tp,
        false_pos=fp,
        true_neg=tn,
        false_neg=fn,
    )


def print_report(report: CalibrationReport) -> None:
    print("\n=== Judge vs human calibration ===")
    print(f"judged rows examined : {report.judged_total}")
    print(f"with learner reaction: {report.matched}")
    if not report.matched:
        print(
            "\nNo learner reactions matched the judged rows yet. Learners need to "
            "react (👍/👎) to some feedback first, then re-run."
        )
        return
    print(f"agreement rate       : {report.agreement_rate:.1%} "
          f"({report.agree}/{report.matched})")
    print("\nconfusion (positive = disliked):")
    print(f"  judge flag & learner dislike (TP): {report.true_pos}")
    print(f"  judge flag & learner like    (FP): {report.false_pos}")
    print(f"  judge pass & learner like    (TN): {report.true_neg}")
    print(f"  judge pass & learner dislike (FN): {report.false_neg}  <- missed by judge")
    if report.false_neg:
        print(
            "\n⚠ The judge passed feedback a learner disliked. Tighten the rubric "
            "before trusting the scores."
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate judge vs human reviews")
    parser.add_argument(
        "--limit",
        type=int,
        default=200,
        help="Max ai_evaluations rows to examine (most recent first).",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    from app.core.database import SessionLocal

    with SessionLocal() as db:
        report = calibrate(db, limit=args.limit)
    print_report(report)


if __name__ == "__main__":
    main()
