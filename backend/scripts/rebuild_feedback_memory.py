"""Rebuild the Pinecone feedback-memory index from Postgres.

Postgres (`feedback_memory_logs`) is the source of truth: every row holds the
full `document_text` plus its stable `vector_id`. This script re-embeds each
row's text and upserts it to Pinecone under the same id, so the vector index
can be recreated from scratch (e.g. after an index reset or dimension change)
or back-filled for a user.

Idempotent — re-running overwrites the same vector ids, never duplicates.

Usage:
    cd backend
    uv run python scripts/rebuild_feedback_memory.py              # all users
    uv run python scripts/rebuild_feedback_memory.py --user-id 42 # one user
    uv run python scripts/rebuild_feedback_memory.py --dry-run    # count only
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Allow `uv run python scripts/rebuild_feedback_memory.py` from anywhere.
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from sqlalchemy import select  # noqa: E402

from app.ai.embeddings.embedding_generator import (  # noqa: E402
    OpenAIEmbeddingGenerator,
)
from app.ai.embeddings.service import EmbeddingService  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.modules.feedback_memory.models import FeedbackMemoryLog  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rebuild_feedback_memory")


async def rebuild(*, user_id: int | None, dry_run: bool) -> None:
    db = SessionLocal()
    try:
        stmt = select(FeedbackMemoryLog).order_by(FeedbackMemoryLog.id)
        if user_id is not None:
            stmt = stmt.where(FeedbackMemoryLog.user_id == user_id)
        rows = list(db.execute(stmt).scalars())
    finally:
        db.close()

    print(
        f"Found {len(rows)} feedback_memory_logs row(s)"
        + (f" for user {user_id}" if user_id is not None else "")
        + f" → namespace '{settings.PINECONE_FEEDBACK_NAMESPACE}'"
    )
    if dry_run:
        print("--dry-run: nothing written.")
        return

    embedder = OpenAIEmbeddingGenerator()
    store = EmbeddingService()
    ok = failed = 0
    for row in rows:
        try:
            vector = await embedder.embed(row.document_text)
            await store.store(
                vector_id=row.vector_id,
                values=vector,
                metadata=dict(row.metadata_json or {}),
                namespace=settings.PINECONE_FEEDBACK_NAMESPACE,
            )
            ok += 1
        except Exception:  # noqa: BLE001
            failed += 1
            logger.warning(
                "Failed to rebuild vector_id=%s", row.vector_id, exc_info=True,
            )

    print(f"Done. upserted={ok} failed={failed}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user-id", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    asyncio.run(rebuild(user_id=args.user_id, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
