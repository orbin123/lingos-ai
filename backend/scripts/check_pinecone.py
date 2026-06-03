"""Pinecone connectivity + dimension smoke test.

Run this FIRST, before expecting any feedback-memory data to appear.
It proves four things end-to-end against your real `.env` credentials:

  1. The OpenAI embedding call works and returns a vector.
  2. The Pinecone index exists and its dimension matches
     OPENAI_EMBEDDING_DIMENSIONS (default 1024). A mismatch is the #1
     reason upserts silently fail and nothing shows up in Pinecone.
  3. Upsert + query round-trips a vector in a throwaway `__smoke__`
     namespace (kept separate from real feedback_memory vectors).
  4. Delete works (cleans up the test vector).

Usage:
    cd backend && uv run python scripts/check_pinecone.py

Exit code 0 = all good, data will flow. Non-zero = read the printed hint.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Allow `uv run python scripts/check_pinecone.py` from anywhere.
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.ai.embeddings.client import pinecone_index_stats  # noqa: E402
from app.ai.embeddings.embedding_generator import (  # noqa: E402
    OpenAIEmbeddingGenerator,
)
from app.ai.embeddings.service import EmbeddingService  # noqa: E402
from app.core.config import settings  # noqa: E402

_SMOKE_NAMESPACE = "__smoke__"
_SMOKE_VECTOR_ID = "smoke_test_vector"


def _fail(msg: str) -> None:
    print(f"\n❌ {msg}")
    sys.exit(1)


async def main() -> None:
    print("=== Pinecone smoke test ===")
    print(f"Index name : {settings.PINECONE_INDEX_NAME}")
    print(f"Namespace  : {settings.PINECONE_FEEDBACK_NAMESPACE} (real data)")
    print(f"Embed model: {settings.OPENAI_EMBEDDING_MODEL}")
    print(f"Expected dimension: {settings.OPENAI_EMBEDDING_DIMENSIONS}")

    # 1. Index stats + dimension check ─────────────────────────────
    try:
        stats = pinecone_index_stats()
    except Exception as exc:  # noqa: BLE001
        _fail(
            f"Could not reach the index '{settings.PINECONE_INDEX_NAME}': {exc}\n"
            "   → Create it in the Pinecone console with dimension "
            f"{settings.OPENAI_EMBEDDING_DIMENSIONS}, metric cosine, and a "
            "name matching PINECONE_INDEX_NAME."
        )

    index_dim = stats.get("dimension")
    print(f"\nIndex reports dimension: {index_dim}")
    print(f"Namespaces present: {list((stats.get('namespaces') or {}).keys())}")
    if index_dim is not None and index_dim != settings.OPENAI_EMBEDDING_DIMENSIONS:
        _fail(
            f"DIMENSION MISMATCH: index is {index_dim}, but embeddings are "
            f"{settings.OPENAI_EMBEDDING_DIMENSIONS}. Every upsert will fail.\n"
            "   → Recreate the index with the matching dimension (or set "
            "OPENAI_EMBEDDING_DIMENSIONS to the index's dimension)."
        )

    # 2. Embed ─────────────────────────────────────────────────────
    embedder = OpenAIEmbeddingGenerator()
    try:
        vector = await embedder.embed("smoke test: the cat sat on the mat")
    except Exception as exc:  # noqa: BLE001
        _fail(f"OpenAI embedding call failed: {exc}\n   → Check OPENAI_API_KEY.")
    print(f"\nEmbedding OK — vector length {len(vector)}")
    if len(vector) != settings.OPENAI_EMBEDDING_DIMENSIONS:
        _fail(
            f"Embedding length {len(vector)} != configured "
            f"{settings.OPENAI_EMBEDDING_DIMENSIONS}."
        )

    # 3. Upsert + query round-trip ─────────────────────────────────
    store = EmbeddingService()
    try:
        await store.store(
            vector_id=_SMOKE_VECTOR_ID,
            values=vector,
            metadata={"smoke": True},
            namespace=_SMOKE_NAMESPACE,
        )
        print("Upsert OK")
    except Exception as exc:  # noqa: BLE001
        _fail(f"Upsert failed: {exc}")

    try:
        matches = await store.query(
            values=vector, top_k=1, namespace=_SMOKE_NAMESPACE,
        )
    except Exception as exc:  # noqa: BLE001
        _fail(f"Query failed: {exc}")
    ids = [m.get("id") for m in matches]
    print(f"Query OK — returned ids: {ids}")
    if _SMOKE_VECTOR_ID not in ids:
        print(
            "⚠️  Query did not return the just-upserted id yet. Pinecone is "
            "eventually consistent; this can be a brief delay, not an error."
        )

    # 4. Delete cleanup ────────────────────────────────────────────
    try:
        await store.delete(vector_ids=[_SMOKE_VECTOR_ID], namespace=_SMOKE_NAMESPACE)
        print("Delete OK (cleaned up test vector)")
    except Exception as exc:  # noqa: BLE001
        _fail(f"Delete failed: {exc}")

    print(
        "\n✅ All checks passed. Pinecone is connected and the dimension "
        "matches — real feedback-memory data will now flow."
    )


if __name__ == "__main__":
    asyncio.run(main())
