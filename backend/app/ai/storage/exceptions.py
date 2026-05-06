"""Blob storage exceptions.

Mirrors the LLM exception family pattern: callers catch ONE base class
(`StorageError`) instead of N filesystem / SDK exception types.
"""


class StorageError(Exception):
    """Base class for any blob-storage failure."""


class StorageNotFound(StorageError):
    """Asked for a key that doesn't exist. Different from a real I/O
    failure — this one is often expected (cache miss)."""


class StorageWriteError(StorageError):
    """Write failed (disk full, permissions, network). Caller may retry."""


class StorageReadError(StorageError):
    """Read failed for reasons other than 'key not found'. Rare."""
