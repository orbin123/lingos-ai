"""Embedding pipeline errors. Caller decides whether to block or log."""


class EmbeddingError(Exception):
    """Base class for all embedding-related failures."""


class PineconeUpsertFailed(EmbeddingError):
    """Pinecone rejected the upsert."""


class PineconeQueryFailed(EmbeddingError):
    """Pinecone query failed."""


class PineconeDeleteFailed(EmbeddingError):
    """Pinecone rejected the delete."""
