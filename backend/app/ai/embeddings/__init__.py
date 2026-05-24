"""Embeddings + vector storage for user responses (and future entities)."""

from app.ai.embeddings.embedding_generator import OpenAIEmbeddingGenerator
from app.ai.embeddings.exceptions import (
    EmbeddingError,
    PineconeQueryFailed,
    PineconeUpsertFailed,
)
from app.ai.embeddings.service import EmbeddingService

__all__ = [
    "EmbeddingError",
    "EmbeddingService",
    "OpenAIEmbeddingGenerator",
    "PineconeQueryFailed",
    "PineconeUpsertFailed",
]
