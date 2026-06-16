"""Offline golden-set harness for the LLM-as-judge (Part B Phase 3).

Runs the real evaluator -> feedback pipeline over a hand-picked golden set,
scores each produced feedback with ``FeedbackJudge``, prints a per-axis mean
table, flags any case scoring below 6 on any axis, persists the run to a JSON
file (and diffs against the previous run so a prompt change shows as a
regression), and — unless ``--no-db`` — writes one ``ai_evaluations`` row per
case with ``eval_mode="offline"`` so offline runs appear on the admin
dashboard alongside online sampling.

Usage:
    uv run python -m scripts.run_evals               # real models, write DB rows
    uv run python -m scripts.run_evals --stub        # deterministic stubs, no LLM
    uv run python -m scripts.run_evals --no-db       # don't write ai_evaluations
    uv run python -m scripts.run_evals --judge-model gpt-4o

The harness is provider-agnostic: ``run_cases`` takes injected collaborators so
CI can drive it with stubs and a fake judge, while a local run uses the real
OpenAI-backed agents.
"""

from __future__ import annotations

import argparse
import asyncio
import dataclasses
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

# Allow `uv run python scripts/run_evals.py` from anywhere.
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.scoring import get_archetype  # noqa: E402

logger = logging.getLogger(__name__)

GOLDEN_SET_PATH = Path(__file__).resolve().parent / "golden_set.json"
RESULTS_DIR = Path(__file__).resolve().parent / ".eval_results"

# Axes scored for feedback. Mentor-note faithfulness is scored online; the
# golden set here is feedback-only.
AXES = ("accuracy", "relevance", "helpfulness", "correctness")
FLAG_THRESHOLD = 6.0


@dataclasses.dataclass
class CaseResult:
    case_id: str
    archetype_id: str
    target_type: str
    axes: dict[str, float]
    rationale: str
    flagged: bool


# ── pipeline ────────────────────────────────────────────────────────


def _feedback_to_payload(feedback: Any) -> dict:
    """Render a ``FeedbackResult`` as the dict the judge scores."""
    return {
        "score": feedback.score,
        "summary": feedback.summary,
        "did_well": list(feedback.did_well or ()),
        "mistakes": [dataclasses.asdict(m) for m in (feedback.mistakes or ())],
        "next_tip": feedback.next_tip,
    }


async def _run_one_case(
    case: dict,
    *,
    evaluator: Any,
    feedback_gen: Any,
    judge: Any,
) -> CaseResult:
    archetype = get_archetype(case["archetype_id"])
    task_content = {"prompt": case["task"], **case.get("task_content", {})}
    user_response = case.get("user_response") or {"text": case["sample_answer"]}

    evaluation = await evaluator.evaluate(
        archetype=archetype,
        task_content=task_content,
        user_response=user_response,
    )
    feedback = await feedback_gen.generate(
        archetype=archetype,
        evaluation=evaluation,
        user_response=user_response,
        task_content=task_content,
    )
    feedback_payload = _feedback_to_payload(feedback)

    scores = await judge.score(
        task=task_content,
        user_answer=user_response,
        feedback=feedback_payload,
    )
    axes = {axis: float(getattr(scores, axis)) for axis in AXES}
    flagged = any(v < FLAG_THRESHOLD for v in axes.values())
    return CaseResult(
        case_id=case["id"],
        archetype_id=case["archetype_id"],
        target_type="feedback",
        axes=axes,
        rationale=getattr(scores, "rationale", "") or "",
        flagged=flagged,
    )


async def run_cases(
    cases: list[dict],
    *,
    evaluator: Any,
    feedback_gen: Any,
    judge: Any,
) -> list[CaseResult]:
    """Run the full pipeline + judge over every case. One bad case never aborts
    the others — a per-case failure is logged and recorded as flagged."""
    results: list[CaseResult] = []
    for case in cases:
        try:
            results.append(
                await _run_one_case(
                    case,
                    evaluator=evaluator,
                    feedback_gen=feedback_gen,
                    judge=judge,
                )
            )
        except Exception:
            logger.warning("Eval case %s failed", case.get("id"), exc_info=True)
            results.append(
                CaseResult(
                    case_id=case.get("id", "?"),
                    archetype_id=case.get("archetype_id", "?"),
                    target_type="feedback",
                    axes={axis: 0.0 for axis in AXES},
                    rationale="pipeline error",
                    flagged=True,
                )
            )
    return results


# ── reporting ───────────────────────────────────────────────────────


def axis_means(results: list[CaseResult]) -> dict[str, float]:
    if not results:
        return {axis: 0.0 for axis in AXES}
    return {
        axis: round(mean(r.axes[axis] for r in results), 2) for axis in AXES
    }


def print_report(results: list[CaseResult], previous: dict | None) -> None:
    means = axis_means(results)
    flagged = [r for r in results if r.flagged]

    print("\n=== Offline judge results ===")
    print(f"cases: {len(results)}   flagged (<{FLAG_THRESHOLD}): {len(flagged)}\n")

    header = f"{'case':28} " + " ".join(f"{a[:4]:>5}" for a in AXES) + "  flag"
    print(header)
    print("-" * len(header))
    for r in results:
        row = f"{r.case_id:28} " + " ".join(f"{r.axes[a]:5.1f}" for a in AXES)
        print(row + ("   !!" if r.flagged else ""))

    print("\nmean per axis:")
    prev_means = (previous or {}).get("means", {})
    for axis in AXES:
        cur = means[axis]
        delta = ""
        if axis in prev_means:
            d = round(cur - prev_means[axis], 2)
            delta = f"  (Δ {d:+.2f} vs previous run)"
        print(f"  {axis:14} {cur:5.2f}{delta}")

    if flagged:
        print("\nflagged cases (any axis < 6):")
        for r in flagged:
            print(f"  - {r.case_id}: {r.rationale}")


def persist_results(results: list[CaseResult], judge_model: str) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RESULTS_DIR / f"{stamp}.json"
    payload = {
        "timestamp": stamp,
        "judge_model": judge_model,
        "means": axis_means(results),
        "cases": [dataclasses.asdict(r) for r in results],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def load_previous_results() -> dict | None:
    """The most recent prior results file, for a regression diff."""
    if not RESULTS_DIR.exists():
        return None
    files = sorted(RESULTS_DIR.glob("*.json"))
    if not files:
        return None
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def write_offline_rows(results: list[CaseResult], *, judge_model: str) -> int:
    """Write one ``ai_evaluations`` row per case (``eval_mode="offline"``)."""
    from app.core.database import SessionLocal
    from app.modules.admin.models import AIEvaluation

    written = 0
    with SessionLocal() as db:
        try:
            for r in results:
                db.add(
                    AIEvaluation(
                        trace_id=None,
                        target_type=r.target_type,
                        target_id=r.case_id,
                        judge_model=judge_model,
                        accuracy=r.axes.get("accuracy"),
                        relevance=r.axes.get("relevance"),
                        helpfulness=r.axes.get("helpfulness"),
                        correctness=r.axes.get("correctness"),
                        faithfulness=None,
                        rationale=(r.rationale or "")[:1000] or None,
                        eval_mode="offline",
                    )
                )
                written += 1
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Failed to write offline ai_evaluations rows")
            raise
    return written


# ── collaborator wiring ─────────────────────────────────────────────


class _StubJudge:
    """Deterministic judge for ``--stub`` runs (no LLM). Scores a flat pass so
    the harness exercises end-to-end without network access."""

    async def score(self, *, task, user_answer, feedback):
        from app.ai.eval.judge import JudgeScores

        return JudgeScores(
            rationale="stub judge — constant pass",
            accuracy=7.0,
            relevance=7.0,
            helpfulness=7.0,
            correctness=7.0,
        )


def build_collaborators(*, stub: bool, judge_model: str | None):
    if stub:
        from app.modules.sessions.evaluator import StubEvaluator
        from app.modules.sessions.feedback_generator import StubFeedbackGenerator

        return StubEvaluator(), StubFeedbackGenerator(), _StubJudge()

    from app.ai.sessions.factory import build_default_agents, build_judge

    evaluator, feedback_gen, _task_gen = build_default_agents()
    judge = build_judge()
    return evaluator, feedback_gen, judge


def load_golden_set(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("cases", []))


async def _amain(args: argparse.Namespace) -> int:
    from app.core.config import settings

    if args.judge_model:
        settings.AI_EVAL_JUDGE_MODEL = args.judge_model
    judge_model = "stub" if args.stub else settings.AI_EVAL_JUDGE_MODEL

    cases = load_golden_set(Path(args.golden))
    logger.info("Loaded %d golden cases from %s", len(cases), args.golden)

    evaluator, feedback_gen, judge = build_collaborators(
        stub=args.stub, judge_model=args.judge_model
    )
    results = await run_cases(
        cases, evaluator=evaluator, feedback_gen=feedback_gen, judge=judge
    )

    previous = load_previous_results()
    print_report(results, previous)
    out = persist_results(results, judge_model)
    logger.info("Wrote results to %s", out)

    if not args.no_db:
        written = write_offline_rows(results, judge_model=judge_model)
        logger.info("Wrote %d offline ai_evaluations rows", written)

    flagged = [r for r in results if r.flagged]
    return 1 if flagged else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline LLM-as-judge harness")
    parser.add_argument(
        "--stub",
        action="store_true",
        help="Use deterministic stub agents + stub judge (no LLM / no network).",
    )
    parser.add_argument(
        "--no-db",
        action="store_true",
        help="Do not write ai_evaluations rows (keeps the run hermetic).",
    )
    parser.add_argument(
        "--judge-model",
        default=None,
        help="Override AI_EVAL_JUDGE_MODEL for this run.",
    )
    parser.add_argument(
        "--golden",
        default=str(GOLDEN_SET_PATH),
        help="Path to the golden set JSON.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    exit_code = asyncio.run(_amain(args))
    # Non-zero exit when any case is flagged, so CI can gate on regressions.
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
