"""Low-level client for Pinecone vector DB.

Wraps the SDK but does NOT know anything about business logic
(user_responses, task_ids, etc). It speaks in raw vectors + metadata.

Two operations:
  - pinecone_upsert()  — store a vector
  - pinecone_query()   — retrieve nearest neighbours by cosine similarity
"""

import logging
from functools import lru_cache

from pinecone import Pinecone

from app.ai.embeddings.exceptions import PineconeQueryFailed, PineconeUpsertFailed
from app.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _pinecone_index():
    """Create the Pinecone index lazily so imports never require network."""
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    return pc.Index(settings.PINECONE_INDEX_NAME)


def pinecone_upsert(
    *, vector_id: str, values: list[float], metadata: dict, namespace: str = ""
) -> None:
    """Upsert a single vector into the configured Pinecone index.

    Raises PineconeUpsertFailed on any SDK error.
    """
    try:
        _pinecone_index().upsert(
            vectors=[
                {"id": vector_id, "values": values, "metadata": metadata}
            ],
            namespace=namespace,
        )
    except Exception as e:  # pinecone SDK throws various subclasses
        logger.warning("Pinecone upsert error: %s", e)
        raise PineconeUpsertFailed(f"Pinecone upsert failed: {e}") from e


def pinecone_query(
    *,
    values: list[float],
    top_k: int = 10,
    filter: dict | None = None,
    namespace: str = "",
    include_metadata: bool = True,
) -> list[dict]:
    """Query Pinecone for nearest-neighbour vectors.

    Returns a list of match dicts, each containing:
      {"id": str, "score": float, "metadata": dict}

    Raises PineconeQueryFailed on any SDK error.
    """
    try:
        result = _pinecone_index().query(
            vector=values,
            top_k=top_k,
            filter=filter or {},
            namespace=namespace,
            include_metadata=include_metadata,
        )
        return [
            {
                "id": m.get("id", m.id) if hasattr(m, "id") else m["id"],
                "score": m.get("score", m.score) if hasattr(m, "score") else m["score"],
                "metadata": (
                    m.get("metadata", m.metadata)
                    if hasattr(m, "metadata")
                    else m.get("metadata", {})
                ),
            }
            for m in (result.get("matches", []) if isinstance(result, dict) else result.matches)
        ]
    except Exception as e:
        logger.warning("Pinecone query error: %s", e)
        raise PineconeQueryFailed(f"Pinecone query failed: {e}") from e
