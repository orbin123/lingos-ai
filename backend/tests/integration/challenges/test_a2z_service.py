"""Integration-style tests for the A2Z service layer.

Uses SQLite in-memory DB and a stub STT service. Exercises the full
round lifecycle: progress → spin/pick → ingest chunks → finish → restart.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base

# Import the central model registry so ALL tables are known to Base.metadata.
# This resolves FK references like admin_audit_logs → users.
import app.models  # noqa: F401

from app.modules.challenges.a2z_game.constants import A2Z_LETTERS, TOTAL_LETTERS
from app.modules.challenges.a2z_game.service import (
    A2ZLetterNotAvailable,
    A2ZRestartNotAllowed,
    A2ZRoundNotFound,
    A2ZRoundNotInProgress,
    A2ZService,
)
from app.modules.challenges.models import Challenge, ChallengeLevel


# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture()
def db_session():
    """Create an in-memory SQLite session with all tables."""
    engine = create_engine("sqlite:///:memory:")

    # SQLite doesn't enforce FKs by default
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=OFF")  # OFF for test flexibility
        cursor.close()

    Base.metadata.create_all(engine)
    _SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def seeded_db(db_session: Session):
    """Seed the A2Z challenge and levels into the test DB."""
    # We need a user row for FK constraints — create a minimal one.
    # Since we're using SQLite and the User model has many dependencies,
    # we'll insert raw rows instead.
    from sqlalchemy import text

    # Create a minimal users table row (just id). Columns must match the
    # real User model: password_hash (not hashed_password) and a non-null name.
    db_session.execute(
        text(
            "INSERT INTO users (id, email, password_hash, name, is_active, created_at, updated_at) "
            "VALUES (1, 'test@test.com', 'hashed', 'Test User', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        )
    )

    challenge = Challenge(
        slug="a2z",
        name="A2Z Challenge",
        short_description="Test A2Z",
        rules_md="# Test",
        icon="grid",
        is_active=True,
        sort_order=20,
    )
    db_session.add(challenge)
    db_session.flush()

    levels_config = [
        {
            "level_number": 1,
            "name": "Warm-up",
            "target_words": 10,
            "round_time_seconds": 25,
        },
        {
            "level_number": 2,
            "name": "Stride",
            "target_words": 15,
            "round_time_seconds": 32,
        },
        {
            "level_number": 3,
            "name": "Fluency",
            "target_words": 22,
            "round_time_seconds": 45,
        },
    ]
    for lc in levels_config:
        db_session.add(
            ChallengeLevel(
                challenge_id=challenge.id,
                level_number=lc["level_number"],
                name=lc["name"],
                time_limit_seconds=lc["round_time_seconds"],
                pass_threshold=1.0,
                config={
                    "game": "a2z",
                    "target_words": lc["target_words"],
                    "round_time_seconds": lc["round_time_seconds"],
                },
            )
        )
    db_session.flush()
    db_session.commit()
    return db_session


@pytest.fixture()
def stub_stt():
    """A mock STT service that returns canned transcription results."""
    mock = AsyncMock()
    mock.transcribe = AsyncMock(
        return_value={
            "text": "",
            "language": "en",
            "duration_seconds": 2.5,
            "words": None,
        }
    )
    return mock


@pytest.fixture()
def stub_blob():
    """A mock blob storage that just stores in-memory."""
    storage = {}
    mock = AsyncMock()

    async def put(*, key, data, content_type):
        storage[key] = {"data": data, "content_type": content_type}
        return {
            "public_url": f"/blob/{key}",
            "storage_key": key,
            "content_type": content_type,
            "size_bytes": len(data),
        }

    mock.put = AsyncMock(side_effect=put)
    mock.get = AsyncMock(return_value=None)
    mock.exists = AsyncMock(return_value=False)
    mock.url_for = lambda *, key: f"/blob/{key}"
    return mock


def make_service(db, stt=None, blob=None):
    return A2ZService(db, stt_service=stt, blob_storage=blob)


USER_ID = 1


# ── Progress tests ───────────────────────────────────────────────────


class TestGetProgress:
    def test_initial_progress_all_empty(self, seeded_db):
        svc = make_service(seeded_db)
        progress = svc.get_progress(USER_ID)

        assert progress.challenge_slug == "a2z"
        assert progress.letters == A2Z_LETTERS
        assert len(progress.levels) == 3
        assert progress.current_level_number == 1
        assert progress.cleared_by_level == {"1": [], "2": [], "3": []}
        assert len(progress.open_letters) == TOTAL_LETTERS
        assert progress.game_completed is False
        assert progress.can_restart is False

    def test_progress_is_idempotent(self, seeded_db):
        svc = make_service(seeded_db)
        p1 = svc.get_progress(USER_ID)
        p2 = svc.get_progress(USER_ID)
        assert p1.current_level_number == p2.current_level_number


# ── Start round tests ────────────────────────────────────────────────


class TestStartRound:
    def test_spin_returns_open_letter(self, seeded_db):
        svc = make_service(seeded_db)
        result = svc.start_round(USER_ID, mode="spin")

        assert result.letter in A2Z_LETTERS
        assert result.target_words == 10
        assert result.round_time_seconds == 25
        assert result.level_number == 1
        assert result.round_id > 0

    def test_pick_valid_letter(self, seeded_db):
        svc = make_service(seeded_db)
        result = svc.start_round(USER_ID, mode="pick", letter="M")

        assert result.letter == "M"
        assert result.level_number == 1

    def test_pick_excluded_letter_raises(self, seeded_db):
        svc = make_service(seeded_db)
        # Q is excluded from A2Z_LETTERS
        with pytest.raises(A2ZLetterNotAvailable):
            svc.start_round(USER_ID, mode="pick", letter="Q")

    def test_pick_lowercase_normalized(self, seeded_db):
        svc = make_service(seeded_db)
        result = svc.start_round(USER_ID, mode="pick", letter="m")
        assert result.letter == "M"

    def test_pick_without_letter_raises(self, seeded_db):
        svc = make_service(seeded_db)
        with pytest.raises(A2ZLetterNotAvailable):
            svc.start_round(USER_ID, mode="pick", letter=None)

    def test_spin_never_returns_cleared_letter(self, seeded_db):
        svc = make_service(seeded_db)
        # Manually clear all but one letter on level 1
        from app.modules.challenges.a2z_game.repository import A2ZProgressRepository

        repo = A2ZProgressRepository(seeded_db)
        challenge = svc._load_challenge()
        progress = repo.get_or_create(user_id=USER_ID, challenge_id=challenge.id)
        # Clear all letters except "Z"
        progress.cleared_letters = {
            "1": [letter for letter in A2Z_LETTERS if letter != "Z"],
            "2": [],
            "3": [],
        }
        from sqlalchemy.orm.attributes import flag_modified

        flag_modified(progress, "cleared_letters")
        seeded_db.flush()
        seeded_db.commit()

        # Spin should always return "Z"
        for _ in range(10):
            result = svc.start_round(USER_ID, mode="spin")
            assert result.letter == "Z"


# ── Finish round tests ───────────────────────────────────────────────


class TestFinishRound:
    def test_pass_adds_letter_to_progress(self, seeded_db, stub_stt, stub_blob):
        svc = make_service(seeded_db, stt=stub_stt, blob=stub_blob)
        round_result = svc.start_round(USER_ID, mode="pick", letter="M")

        # Simulate a transcript with enough words
        from app.modules.challenges.a2z_game.repository import A2ZRoundRepository

        round_repo = A2ZRoundRepository(seeded_db)
        attempt = round_repo.get_for_user(
            round_id=round_result.round_id, user_id=USER_ID
        )
        attempt.response_payload = {
            "running_transcript": "mountain music market mirror metal magic mango maple march mask",
            "accepted_words": [],
        }
        from sqlalchemy.orm.attributes import flag_modified

        flag_modified(attempt, "response_payload")
        seeded_db.flush()

        finish = svc.finish_round(USER_ID, round_result.round_id)
        assert finish.passed is True
        assert finish.letter == "M"
        assert finish.valid_word_count == 10
        assert "M" in finish.progress.cleared_by_level["1"]

    def test_fail_does_not_add_letter(self, seeded_db, stub_stt, stub_blob):
        svc = make_service(seeded_db, stt=stub_stt, blob=stub_blob)
        round_result = svc.start_round(USER_ID, mode="pick", letter="B")

        # Simulate a transcript with too few words
        from app.modules.challenges.a2z_game.repository import A2ZRoundRepository

        round_repo = A2ZRoundRepository(seeded_db)
        attempt = round_repo.get_for_user(
            round_id=round_result.round_id, user_id=USER_ID
        )
        attempt.response_payload = {
            "running_transcript": "ball bat",
            "accepted_words": [],
        }
        from sqlalchemy.orm.attributes import flag_modified

        flag_modified(attempt, "response_payload")
        seeded_db.flush()

        finish = svc.finish_round(USER_ID, round_result.round_id)
        assert finish.passed is False
        assert "B" not in finish.progress.cleared_by_level["1"]

    def test_finish_nonexistent_round_raises(self, seeded_db):
        svc = make_service(seeded_db)
        with pytest.raises(A2ZRoundNotFound):
            svc.finish_round(USER_ID, 99999)

    def test_finish_already_completed_round_raises(
        self, seeded_db, stub_stt, stub_blob
    ):
        svc = make_service(seeded_db, stt=stub_stt, blob=stub_blob)
        round_result = svc.start_round(USER_ID, mode="pick", letter="A")

        # Set up and finish once
        from app.modules.challenges.a2z_game.repository import A2ZRoundRepository

        round_repo = A2ZRoundRepository(seeded_db)
        attempt = round_repo.get_for_user(
            round_id=round_result.round_id, user_id=USER_ID
        )
        attempt.response_payload = {"running_transcript": "apple", "accepted_words": []}
        from sqlalchemy.orm.attributes import flag_modified

        flag_modified(attempt, "response_payload")
        seeded_db.flush()
        svc.finish_round(USER_ID, round_result.round_id)

        # Try to finish again
        with pytest.raises(A2ZRoundNotInProgress):
            svc.finish_round(USER_ID, round_result.round_id)


# ── Level advancement tests ──────────────────────────────────────────


class TestLevelAdvancement:
    def test_clear_all_level1_advances_to_level2(self, seeded_db, stub_stt, stub_blob):
        svc = make_service(seeded_db, stt=stub_stt, blob=stub_blob)

        # Clear all 24 letters on level 1
        from app.modules.challenges.a2z_game.repository import A2ZProgressRepository

        repo = A2ZProgressRepository(seeded_db)
        challenge = svc._load_challenge()
        progress = repo.get_or_create(user_id=USER_ID, challenge_id=challenge.id)
        progress.cleared_letters = {
            "1": list(A2Z_LETTERS),  # all 24 cleared
            "2": [],
            "3": [],
        }
        from sqlalchemy.orm.attributes import flag_modified

        flag_modified(progress, "cleared_letters")
        seeded_db.flush()
        seeded_db.commit()

        p = svc.get_progress(USER_ID)
        assert p.current_level_number == 2
        assert p.game_completed is False

    def test_clear_all_level3_completes_game(self, seeded_db, stub_stt, stub_blob):
        svc = make_service(seeded_db, stt=stub_stt, blob=stub_blob)

        from app.modules.challenges.a2z_game.repository import A2ZProgressRepository

        repo = A2ZProgressRepository(seeded_db)
        challenge = svc._load_challenge()
        progress = repo.get_or_create(user_id=USER_ID, challenge_id=challenge.id)
        progress.cleared_letters = {
            "1": list(A2Z_LETTERS),
            "2": list(A2Z_LETTERS),
            "3": list(A2Z_LETTERS),
        }
        progress.game_completed_at = datetime.now(timezone.utc)
        from sqlalchemy.orm.attributes import flag_modified

        flag_modified(progress, "cleared_letters")
        seeded_db.flush()
        seeded_db.commit()

        p = svc.get_progress(USER_ID)
        assert p.game_completed is True
        assert p.can_restart is True


# ── Restart tests ────────────────────────────────────────────────────


class TestRestart:
    def test_restart_mid_game_raises(self, seeded_db):
        svc = make_service(seeded_db)
        # Get initial progress (game not complete)
        svc.get_progress(USER_ID)

        with pytest.raises(A2ZRestartNotAllowed):
            svc.restart_game(USER_ID)

    def test_restart_after_completion_resets(self, seeded_db):
        svc = make_service(seeded_db)

        # Set up completed state
        from app.modules.challenges.a2z_game.repository import A2ZProgressRepository

        repo = A2ZProgressRepository(seeded_db)
        challenge = svc._load_challenge()
        progress = repo.get_or_create(user_id=USER_ID, challenge_id=challenge.id)
        progress.cleared_letters = {
            "1": list(A2Z_LETTERS),
            "2": list(A2Z_LETTERS),
            "3": list(A2Z_LETTERS),
        }
        progress.game_completed_at = datetime.now(timezone.utc)
        from sqlalchemy.orm.attributes import flag_modified

        flag_modified(progress, "cleared_letters")
        seeded_db.flush()
        seeded_db.commit()

        result = svc.restart_game(USER_ID)
        assert result.game_completed is False
        assert result.can_restart is False
        assert result.cleared_by_level == {"1": [], "2": [], "3": []}
        assert result.current_level_number == 1


# ── Audio chunk tests ────────────────────────────────────────────────


class TestAudioChunkIngest:
    def test_new_words_returned(self, seeded_db, stub_stt, stub_blob):
        svc = make_service(seeded_db, stt=stub_stt, blob=stub_blob)
        round_result = svc.start_round(USER_ID, mode="pick", letter="S")

        # Stub STT to return words
        stub_stt.transcribe.return_value = {
            "text": "snake super school",
            "language": "en",
            "duration_seconds": 2.5,
            "words": None,
        }

        result = asyncio.run(
            svc.ingest_audio_chunk(
                user_id=USER_ID,
                round_id=round_result.round_id,
                audio_bytes=b"fake_audio",
                chunk_index=0,
                content_type="audio/webm",
            )
        )

        assert set(result.new_words) == {"snake", "super", "school"}
        assert result.valid_word_count == 3

    def test_subsequent_chunk_only_new_words(self, seeded_db, stub_stt, stub_blob):
        svc = make_service(seeded_db, stt=stub_stt, blob=stub_blob)
        round_result = svc.start_round(USER_ID, mode="pick", letter="S")

        # First chunk
        stub_stt.transcribe.return_value = {
            "text": "snake super",
            "language": "en",
            "duration_seconds": 2.5,
            "words": None,
        }
        asyncio.run(
            svc.ingest_audio_chunk(
                user_id=USER_ID,
                round_id=round_result.round_id,
                audio_bytes=b"chunk1",
                chunk_index=0,
                content_type="audio/webm",
            )
        )

        # Second chunk — includes a repeat and a new word
        stub_stt.transcribe.return_value = {
            "text": "snake star",
            "language": "en",
            "duration_seconds": 2.5,
            "words": None,
        }
        result = asyncio.run(
            svc.ingest_audio_chunk(
                user_id=USER_ID,
                round_id=round_result.round_id,
                audio_bytes=b"chunk2",
                chunk_index=1,
                content_type="audio/webm",
            )
        )

        # Only "star" should be new (snake already seen)
        assert "star" in result.new_words
        assert "snake" not in result.new_words
        assert result.valid_word_count == 3  # snake, super, star

    def test_chunk_for_nonexistent_round_raises(self, seeded_db, stub_stt, stub_blob):
        svc = make_service(seeded_db, stt=stub_stt, blob=stub_blob)
        with pytest.raises(A2ZRoundNotFound):
            asyncio.run(
                svc.ingest_audio_chunk(
                    user_id=USER_ID,
                    round_id=99999,
                    audio_bytes=b"audio",
                    chunk_index=0,
                )
            )
