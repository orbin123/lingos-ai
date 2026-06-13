"""Domain exceptions for the blog module.

Routes translate these into HTTPException at the boundary.
"""

from __future__ import annotations


class BlogError(Exception):
    """Base class for any blog domain error."""


class BlogNotFound(BlogError):
    """Requested blog post does not exist (or is not publicly visible)."""


class BlogSlugConflict(BlogError):
    """Another post already uses the requested slug."""
