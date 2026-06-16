"""Part B Phase 2 — online LLM-as-judge for feedback.

Covers the new isolated units:
  * ``is_llm_backed_evaluation`` — the archetype gate (only LLM-graded
    archetypes are worth a judge call).
  * ``FeedbackJudge.score`` — returns validated 0–10 ``JudgeScores`` and runs
    the judge deterministically (temperature 0.0).
  * ``_run_ai_eval_worker`` — writes exactly one ``ai_evaluations`` row on its
    own session; a judge failure writes nothing and never raises.
  * ``AdminService.ai_quality`` — rolling means per target_type + the worst-N
    (any axis < 6) read path.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (populate the mapper registry)
from app.ai.eval.judge import (
    FeedbackJudge,
    JudgeScores,
    MentorNoteJudge,
    MentorNoteScores,
)
from app.ai.sessions.llm_evaluator import is_llm_backed_evaluation
from app.core.database import Base
from app.modules.admin.models import AIEvaluation
from app.modules.admin.service import AdminService
from app.modules.auth.models import User

NOW = datetime.now(timezone.utc)


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine, tables=[User.__table__, AIEvaluation.__table__]
    )
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = Session()
    yield session, Session
    session.close()
    engine.dispose()


# ── archetype gate ──────────────────────────────────────────────────


@pytest.mark.parametrize(
    "archetype_id,expected",
    [
        ("LISTEN_MCQ", False),
        ("READ_COMP_MCQ", False),
        ("READ_CLOZE", False),
        ("LISTEN_CLOZE", False),
        ("READ_ERROR_SPOT", False),
        ("WRITE_OPEN", True),
        ("SPEAK_READ_ALOUD", True),
        ("SPEAK_FREE", True),
    ],
)
def test_is_llm_backed_evaluation_gate(archetype_id, expected):
    archetype = SimpleNamespace(archetype_id=archetype_id)
    assert is_llm_backed_evaluation(archetype) is expected


# ── the judge ───────────────────────────────────────────────────────


class _FakeJudgeLLM:
    """Captures the temperature and returns a fixed JudgeScores instance."""

    def __init__(self, out: JudgeScores) -> None:
        self.out = out
        self.calls: list[float | None] = []

    async def generate_structured(
        self, *, system_prompt, user_prompt, output_model, temperature=None
    ):
        self.calls.append(temperature)
        assert output_model is JudgeScores
        return self.out


@pytest.mark.asyncio
async def test_feedback_judge_scores_and_is_deterministic():
    out = JudgeScores(
        rationale="grounded and specific",
        accuracy=8.0,
        relevance=7.5,
        helpfulness=6.0,
        correctness=9.0,
    )
    llm = _FakeJudgeLLM(out)
    judge = FeedbackJudge(llm)

    scores = await judge.score(
        task={"prompt": "Describe your weekend."},
        user_answer={"text": "I go to park yesterday."},
        feedback={"summary": "Watch your past tense."},
    )

    assert isinstance(scores, JudgeScores)
    assert scores.accuracy == 8.0
    assert scores.correctness == 9.0
    # Judges must be deterministic.
    assert llm.calls == [0.0]


def test_judge_scores_reject_out_of_range():
    with pytest.raises(Exception):
        JudgeScores(accuracy=11.0, relevance=5, helpfulness=5, correctness=5)


# ── worker ──────────────────────────────────────────────────────────


class _StubJudge:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail

    async def score(self, *, task, user_answer, feedback) -> JudgeScores:
        if self.fail:
            raise RuntimeError("judge boom")
        return JudgeScores(
            rationale="ok", accuracy=7.0, relevance=8.0, helpfulness=6.5, correctness=7.0
        )


@pytest.mark.asyncio
async def test_run_ai_eval_worker_writes_one_row(db, monkeypatch):
    session, Session = db
    import app.ai.sessions.factory as factory
    import app.core.database as database

    monkeypatch.setattr(factory, "build_judge", lambda: _StubJudge())
    monkeypatch.setattr(database, "SessionLocal", Session)

    from app.modules.sessions.service import _run_ai_eval_worker

    await _run_ai_eval_worker(
        trace_id="trace-xyz",
        user_id=1,
        target_id="42",
        task_content={"prompt": "p"},
        user_response={"text": "a"},
        feedback={"summary": "s"},
    )

    rows = session.query(AIEvaluation).all()
    assert len(rows) == 1
    row = rows[0]
    assert row.trace_id == "trace-xyz"
    assert row.target_type == "feedback"
    assert row.target_id == "42"
    assert row.eval_mode == "online"
    assert float(row.accuracy) == 7.0
    assert row.faithfulness is None
    assert row.rationale == "ok"


@pytest.mark.asyncio
async def test_run_ai_eval_worker_swallows_judge_failure(db, monkeypatch):
    session, Session = db
    import app.ai.sessions.factory as factory
    import app.core.database as database

    monkeypatch.setattr(factory, "build_judge", lambda: _StubJudge(fail=True))
    monkeypatch.setattr(database, "SessionLocal", Session)

    from app.modules.sessions.service import _run_ai_eval_worker

    # Must not raise — observability is best-effort.
    await _run_ai_eval_worker(
        trace_id="t",
        user_id=1,
        target_id="9",
        task_content={},
        user_response={},
        feedback={},
    )

    assert session.query(AIEvaluation).count() == 0


# ── admin read path ─────────────────────────────────────────────────


def _eval_row(db, **kw) -> AIEvaluation:
    defaults = dict(
        trace_id="t",
        target_type="feedback",
        target_id="1",
        judge_model="gpt-4.1",
        eval_mode="online",
        created_at=NOW,
    )
    defaults.update(kw)
    row = AIEvaluation(**defaults)
    db.add(row)
    db.flush()
    return row


def test_ai_quality_means_and_worst(db):
    session, _ = db
    # Two good feedback rows + one bad one (correctness 3 < 6).
    _eval_row(session, accuracy=8, relevance=8, helpfulness=8, correctness=8)
    _eval_row(session, accuracy=6, relevance=6, helpfulness=6, correctness=6)
    bad = _eval_row(
        session, accuracy=7, relevance=7, helpfulness=7, correctness=3,
        rationale="invented a mistake", trace_id="bad-trace", target_id="99",
    )
    # A stale row outside the window must be excluded.
    _eval_row(
        session, accuracy=1, relevance=1, helpfulness=1, correctness=1,
        created_at=NOW - timedelta(days=30),
    )
    session.commit()

    report = AdminService(session).ai_quality(days=7)

    assert report.days == 7
    assert report.judged_count == 3  # stale row excluded
    feedback = next(r for r in report.means if r.target_type == "feedback")
    assert feedback.judged_count == 3
    # mean accuracy = (8 + 6 + 7) / 3 = 7.0
    assert feedback.mean_accuracy == 7.0
    # Only the correctness-3 row trips the < 6 worst filter.
    assert len(report.worst) == 1
    assert report.worst[0].id == bad.id
    assert report.worst[0].trace_id == "bad-trace"
    assert report.worst[0].rationale == "invented a mistake"

    # Time-series: the three in-window rows share one UTC day + target_type.
    assert len(report.series) == 1
    point = report.series[0]
    assert point.target_type == "feedback"
    assert point.judged_count == 3
    assert point.mean_accuracy == 7.0


# ── Phase 3: RAG mentor-note judge ──────────────────────────────────


class _FakeMentorLLM:
    """Returns faithfulness keyed on whether the retrieved context is present.

    Mimics a real judge: a note has nothing to ground a "recurring pattern"
    claim against when the RETRIEVED CONTEXT is empty, so faithfulness is low;
    when the context carries the pattern, faithfulness is high. Also records
    the temperature so determinism can be asserted.
    """

    def __init__(self) -> None:
        self.calls: list[float | None] = []

    async def generate_structured(
        self, *, system_prompt, user_prompt, output_model, temperature=None
    ):
        self.calls.append(temperature)
        assert output_model is MentorNoteScores
        # The note's "article" claim is grounded only if the RETRIEVED CONTEXT
        # section itself mentions articles.
        context_section = user_prompt.split("RETRIEVED CONTEXT")[1].split(
            "MENTOR NOTE"
        )[0]
        grounded = "article" in context_section
        faithfulness = 9.0 if grounded else 2.0
        return MentorNoteScores(
            rationale="grounded" if grounded else "invented a pattern",
            accuracy=8.0,
            relevance=8.0,
            helpfulness=7.0,
            correctness=8.0,
            faithfulness=faithfulness,
        )


@pytest.mark.asyncio
async def test_mentor_judge_is_deterministic_and_returns_scores():
    llm = _FakeMentorLLM()
    judge = MentorNoteJudge(llm)

    scores = await judge.score(
        note="You keep making article errors — watch 'a'/'the'.",
        rag_context={"recurring_patterns": [{"issue": "article", "count": 3}]},
        today_activities=[{"archetype_id": "WRITE_OPEN"}],
    )

    assert isinstance(scores, MentorNoteScores)
    assert scores.faithfulness == 9.0  # context supports the article claim
    assert llm.calls == [0.0]  # judges must be deterministic


@pytest.mark.asyncio
async def test_mentor_judge_penalises_ungrounded_pattern():
    llm = _FakeMentorLLM()
    judge = MentorNoteJudge(llm)

    # The note asserts a recurring article pattern, but retrieval returned nothing.
    scores = await judge.score(
        note="You keep making article errors — watch 'a'/'the'.",
        rag_context={},
        today_activities=[{"archetype_id": "WRITE_OPEN"}],
    )

    assert scores.faithfulness == 2.0


def test_mentor_note_scores_reject_out_of_range():
    with pytest.raises(Exception):
        MentorNoteScores(
            accuracy=5, relevance=5, helpfulness=5, correctness=5, faithfulness=11.0
        )


class _StubMentorJudge:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail

    async def score(self, *, note, rag_context, today_activities=None):
        if self.fail:
            raise RuntimeError("mentor judge boom")
        return MentorNoteScores(
            rationale="grounded",
            accuracy=7.0,
            relevance=8.0,
            helpfulness=6.5,
            correctness=7.0,
            faithfulness=9.0,
        )


@pytest.mark.asyncio
async def test_run_mentor_note_eval_worker_writes_one_row(db, monkeypatch):
    session, Session = db
    import app.ai.sessions.factory as factory
    import app.core.database as database

    monkeypatch.setattr(factory, "build_mentor_judge", lambda: _StubMentorJudge())
    monkeypatch.setattr(database, "SessionLocal", Session)

    from app.modules.sessions.service import _run_mentor_note_eval_worker

    await _run_mentor_note_eval_worker(
        trace_id="trace-mn",
        user_id=1,
        target_id="7",
        note="Nice progress on past tense today.",
        rag_context={"recurring_patterns": []},
        today_activities=[{"archetype_id": "WRITE_OPEN"}],
    )

    rows = session.query(AIEvaluation).all()
    assert len(rows) == 1
    row = rows[0]
    assert row.trace_id == "trace-mn"
    assert row.target_type == "mentor_note"
    assert row.target_id == "7"
    assert row.eval_mode == "online"
    assert float(row.faithfulness) == 9.0
    assert row.rationale == "grounded"


@pytest.mark.asyncio
async def test_run_mentor_note_eval_worker_swallows_judge_failure(db, monkeypatch):
    session, Session = db
    import app.ai.sessions.factory as factory
    import app.core.database as database

    monkeypatch.setattr(
        factory, "build_mentor_judge", lambda: _StubMentorJudge(fail=True)
    )
    monkeypatch.setattr(database, "SessionLocal", Session)

    from app.modules.sessions.service import _run_mentor_note_eval_worker

    # Must not raise — observability is best-effort.
    await _run_mentor_note_eval_worker(
        trace_id="t",
        user_id=1,
        target_id="9",
        note="note",
        rag_context={},
        today_activities=[],
    )

    assert session.query(AIEvaluation).count() == 0


class _StubRag:
    async def retrieve_context_for_feedback(self, **_kw):
        return {"recurring_patterns": []}


class _StubMentorGen:
    async def generate(self, **_kw):
        return "Nice work on past tense today."


@pytest.mark.parametrize("rate,expected_scheduled", [(0.0, False), (1.0, True)])
@pytest.mark.asyncio
async def test_mentor_note_eval_sampling_gate(db, monkeypatch, rate, expected_scheduled):
    session, _ = db
    from app.core.config import settings
    from app.modules.sessions import service as service_mod
    from app.modules.sessions.service import SessionService

    scheduled: list[dict] = []

    async def _fake_worker(**kwargs):
        scheduled.append(kwargs)

    monkeypatch.setattr(service_mod, "_run_mentor_note_eval_worker", _fake_worker)
    monkeypatch.setattr(settings, "AI_EVAL_ENABLED", True)
    monkeypatch.setattr(settings, "AI_EVAL_MENTOR_SAMPLE_RATE", rate)

    svc = SessionService(session)
    svc._rag_service = _StubRag()
    svc._mentor_generator = _StubMentorGen()
    # `_generate_mentor_note_safe` reads attempts to collect today's mistakes.
    svc.attempts_repo = SimpleNamespace(list_for_session=lambda _id: [])

    sess = SimpleNamespace(id=1, user_id=1, day_id="day_24_01_00", session_id="s-1")
    note = await svc._generate_mentor_note_safe(
        session=sess,
        activities_breakdown=[{"archetype_id": "WRITE_OPEN", "weighted_points": {}}],
        scorecard_id=55,
    )

    # Let any scheduled task run.
    import asyncio as _asyncio

    await _asyncio.sleep(0)

    assert note == "Nice work on past tense today."
    if expected_scheduled:
        assert len(scheduled) == 1
        assert scheduled[0]["target_id"] == "55"
        assert scheduled[0]["note"] == note
    else:
        assert scheduled == []
