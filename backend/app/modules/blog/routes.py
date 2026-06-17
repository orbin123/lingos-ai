"""HTTP routes for the blog CMS.

Two routers:
  - `public_router`  (`/blog`)        — unauthenticated reads of published posts
  - `admin_router`   (`/admin/blog`)  — admin/super-admin CRUD, audit-logged
"""

from __future__ import annotations

import hashlib
import logging
import time

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.ai.storage import IBlobStorage, StorageError, build_blob_storage
from app.core.config import settings
from app.core.database import get_db
from app.modules.admin.audit_service import AdminAuditService, client_ip_from_request
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.auth.models import ROLE_ADMIN, ROLE_SUPER_ADMIN, User
from app.modules.blog.exceptions import BlogNotFound, BlogSlugConflict
from app.modules.blog.schemas import (
    BlogPostAdminRead,
    BlogPostCreate,
    BlogPostListItem,
    BlogPostRead,
    BlogPostUpdate,
)
from app.modules.blog.service import BlogService

logger = logging.getLogger(__name__)

require_admin = require_role([ROLE_ADMIN, ROLE_SUPER_ADMIN])


# ── Cover-image storage ────────────────────────────────────────────────────
# Mirrors the learner-audio pattern in app/modules/responses/routes.py: a lazy
# LocalBlobStorage singleton writing under a StaticFiles-mounted media root.
_IMAGE_EXTENSIONS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
_MAX_COVER_BYTES = 5 * 1024 * 1024
_cover_storage: IBlobStorage | None = None


def get_cover_storage() -> IBlobStorage:
    global _cover_storage
    if _cover_storage is None:
        _cover_storage = build_blob_storage(
            cache_dir=settings.BLOG_MEDIA_CACHE_DIR,
            public_url_prefix=settings.BLOG_MEDIA_PUBLIC_URL_PREFIX,
        )
    return _cover_storage


def _normalized_image_content_type(content_type: str | None) -> str:
    primary = (content_type or "").split(";", 1)[0].strip().lower()
    if primary not in _IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported image type. Use PNG, JPEG, WebP, or GIF.",
        )
    return primary


# ── Public router ──────────────────────────────────────────────────────────

public_router = APIRouter(prefix="/blog", tags=["blog"])


@public_router.get("", response_model=list[BlogPostListItem])
def list_published_posts(
    limit: int | None = Query(default=None, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[BlogPostListItem]:
    posts = BlogService(db).list_published(
        limit=limit, offset=offset, category=category
    )
    return [BlogPostListItem.model_validate(p) for p in posts]


@public_router.get("/{slug}", response_model=BlogPostRead)
def get_published_post(slug: str, db: Session = Depends(get_db)) -> BlogPostRead:
    try:
        post = BlogService(db).get_published(slug)
    except BlogNotFound as exc:
        raise HTTPException(status_code=404, detail="Post not found.") from exc
    return BlogPostRead.model_validate(post)


@public_router.get("/{slug}/related", response_model=list[BlogPostListItem])
def get_related_posts(
    slug: str,
    limit: int = Query(default=3, ge=1, le=12),
    db: Session = Depends(get_db),
) -> list[BlogPostListItem]:
    posts = BlogService(db).list_related(slug, limit=limit)
    return [BlogPostListItem.model_validate(p) for p in posts]


# ── Admin router ───────────────────────────────────────────────────────────

admin_router = APIRouter(
    prefix="/admin/blog",
    tags=["admin-blog"],
    dependencies=[Depends(require_admin)],
)


def _audit(
    db: Session,
    *,
    admin: User,
    action: str,
    post_id: int | str,
    request: Request,
    old: dict | None = None,
    new: dict | None = None,
) -> None:
    AdminAuditService(db).record(
        admin=admin,
        action=action,
        resource_type="blog_post",
        resource_id=post_id,
        old_value=old,
        new_value=new,
        ip_address=client_ip_from_request(request),
    )
    db.commit()


def _snapshot(post) -> dict:
    return {"title": post.title, "slug": post.slug, "status": post.status}


@admin_router.get("", response_model=list[BlogPostAdminRead])
def admin_list_posts(db: Session = Depends(get_db)) -> list[BlogPostAdminRead]:
    return [BlogPostAdminRead.model_validate(p) for p in BlogService(db).list_all()]


@admin_router.get("/{post_id}", response_model=BlogPostAdminRead)
def admin_get_post(post_id: int, db: Session = Depends(get_db)) -> BlogPostAdminRead:
    try:
        post = BlogService(db).get(post_id)
    except BlogNotFound as exc:
        raise HTTPException(status_code=404, detail="Post not found.") from exc
    return BlogPostAdminRead.model_validate(post)


@admin_router.post("", response_model=BlogPostAdminRead, status_code=201)
def admin_create_post(
    payload: BlogPostCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BlogPostAdminRead:
    try:
        post = BlogService(db).create(payload.model_dump(), author_id=current_user.id)
    except BlogSlugConflict as exc:
        raise HTTPException(status_code=409, detail="Slug already in use.") from exc
    _audit(
        db,
        admin=current_user,
        action="create",
        post_id=post.id,
        request=request,
        new=_snapshot(post),
    )
    return BlogPostAdminRead.model_validate(post)


@admin_router.patch("/{post_id}", response_model=BlogPostAdminRead)
def admin_update_post(
    post_id: int,
    payload: BlogPostUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BlogPostAdminRead:
    service = BlogService(db)
    try:
        before = _snapshot(service.get(post_id))
        post = service.update(post_id, payload.model_dump(exclude_unset=True))
    except BlogNotFound as exc:
        raise HTTPException(status_code=404, detail="Post not found.") from exc
    except BlogSlugConflict as exc:
        raise HTTPException(status_code=409, detail="Slug already in use.") from exc
    _audit(
        db,
        admin=current_user,
        action="update",
        post_id=post.id,
        request=request,
        old=before,
        new=_snapshot(post),
    )
    return BlogPostAdminRead.model_validate(post)


@admin_router.post("/{post_id}/publish", response_model=BlogPostAdminRead)
def admin_publish_post(
    post_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BlogPostAdminRead:
    return _set_status(db, post_id, "published", current_user, request)


@admin_router.post("/{post_id}/unpublish", response_model=BlogPostAdminRead)
def admin_unpublish_post(
    post_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BlogPostAdminRead:
    return _set_status(db, post_id, "draft", current_user, request)


def _set_status(
    db: Session, post_id: int, new_status: str, current_user: User, request: Request
) -> BlogPostAdminRead:
    try:
        post = BlogService(db).set_status(post_id, new_status)
    except BlogNotFound as exc:
        raise HTTPException(status_code=404, detail="Post not found.") from exc
    _audit(
        db,
        admin=current_user,
        action=new_status,
        post_id=post.id,
        request=request,
        new=_snapshot(post),
    )
    return BlogPostAdminRead.model_validate(post)


@admin_router.delete("/{post_id}", status_code=204)
def admin_delete_post(
    post_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    service = BlogService(db)
    try:
        before = _snapshot(service.get(post_id))
        service.delete(post_id)
    except BlogNotFound as exc:
        raise HTTPException(status_code=404, detail="Post not found.") from exc
    _audit(
        db,
        admin=current_user,
        action="delete",
        post_id=post_id,
        request=request,
        old=before,
    )


@admin_router.post("/{post_id}/cover", response_model=BlogPostAdminRead)
async def admin_upload_cover(
    post_id: int,
    request: Request,
    file: UploadFile = File(..., description="Cover image (PNG/JPEG/WebP/GIF)."),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BlogPostAdminRead:
    service = BlogService(db)
    try:
        service.get(post_id)  # 404 before reading the upload body
    except BlogNotFound as exc:
        raise HTTPException(status_code=404, detail="Post not found.") from exc

    content_type = _normalized_image_content_type(file.content_type)
    data = await file.read(_MAX_COVER_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail="Empty image upload.")
    if len(data) > _MAX_COVER_BYTES:
        raise HTTPException(status_code=413, detail="Image too large (max 5 MB).")

    ext = _IMAGE_EXTENSIONS[content_type]
    digest = hashlib.sha256(data).hexdigest()[:24]
    key = f"{digest}-blog-{post_id}-{int(time.time() * 1000)}{ext}"
    try:
        stored = await get_cover_storage().put(
            key=key, data=data, content_type=content_type
        )
    except StorageError as exc:
        logger.exception("Failed to persist blog cover key=%s", key)
        raise HTTPException(status_code=500, detail="Could not save image.") from exc

    post = service.set_cover_image(post_id, stored["public_url"])
    _audit(
        db,
        admin=current_user,
        action="cover",
        post_id=post.id,
        request=request,
        new={"cover_image_url": post.cover_image_url},
    )
    return BlogPostAdminRead.model_validate(post)
