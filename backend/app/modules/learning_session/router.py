"""HTTP + WebSocket endpoints for chat-driven learning sessions."""

from __future__ import annotations

import json
import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.learning_session.schemas import (
    LearningSessionSnapshotRead,
    StartSessionRequest,
    StartSessionResponse,
    WSIncomingMessage,
    WSOutgoingMessage,
)
from app.modules.learning_session.authoring import (
    AuthoringLearningSessionService,
    AuthoringModeDisabled,
    AuthoringSessionNotFound,
)
from app.modules.learning_session.service import (
    LearningSessionService,
    LearningSessionTaskUnavailable,
)
from app.modules.sessions.exceptions import DayNotFound

logger = logging.getLogger(__name__)

authoring_bearer_scheme = HTTPBearer(auto_error=False)


# --- REST -------------------------------------------------------------

rest_router = APIRouter(prefix="/learning", tags=["learning_session"])
dev_rest_router = APIRouter(prefix="/dev/learning", tags=["learning_session_dev"])


def _guard_authoring_auth(
    credentials: HTTPAuthorizationCredentials | None,
) -> None:
    if not settings.AUTHORING_CHAT_REQUIRE_AUTH:
        return
    if credentials is None or decode_token(credentials.credentials) is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authoring chat auth required",
        )


def _authoring_ws_authorized(token: str | None) -> bool:
    if not settings.AUTHORING_CHAT_REQUIRE_AUTH:
        return True
    return bool(token and decode_token(token) is not None)


@rest_router.post(
    "/sessions/start",
    response_model=StartSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_session(
    payload: StartSessionRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StartSessionResponse:
    service = LearningSessionService(db)
    try:
        return await service.create_session(
            user_id=current_user.id,
            daily_session_id=payload.daily_session_id if payload else None,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except LearningSessionTaskUnavailable as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover — unexpected
        logger.exception("start_session failed for user_id=%s", current_user.id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@rest_router.post(
    "/sessions/{session_id}/restart",
    response_model=StartSessionResponse,
    status_code=status.HTTP_200_OK,
)
async def restart_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StartSessionResponse:
    service = LearningSessionService(db)
    try:
        return await service.restart_session(
            session_id=session_id,
            user_id=current_user.id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover — unexpected
        logger.exception(
            "restart_session failed session_id=%s user_id=%s",
            session_id,
            current_user.id,
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@rest_router.get(
    "/sessions/by-daily-session/{daily_session_id}",
    response_model=LearningSessionSnapshotRead,
    status_code=status.HTTP_200_OK,
)
def get_session_by_daily_session(
    daily_session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LearningSessionSnapshotRead:
    """Return the chat session linked to a given V2 DailySession (by int PK).

    Used for resume / history views that have the V2 session id but want
    the chat conversation snapshot.

    Errors:
      404 — no chat session found for this daily session belonging to user
    """
    from app.modules.learning_session.models import LearningSession

    session = (
        db.query(LearningSession)
        .filter(
            LearningSession.daily_session_id == daily_session_id,
            LearningSession.user_id == current_user.id,
        )
        .order_by(LearningSession.id.desc())
        .first()
    )
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="No chat session found for this daily session",
        )

    return LearningSessionSnapshotRead(
        session_id=session.session_id,
        daily_session_id=session.daily_session_id,
        topic=session.topic,
        skill_name=session.skill_name,
        task_type=session.task_type,
        phase=session.phase,
        messages=session.messages or [],
        pre_generated_tasks=session.pre_generated_tasks,
        user_submission=session.user_submission,
        evaluation=session.evaluation,
        feedback=session.feedback,
        task_queue=session.task_queue or [],
        created_at=session.created_at,
    )


@rest_router.get(
    "/sessions/{session_id}/scorecard",
    status_code=status.HTTP_200_OK,
)
async def get_scorecard_for_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the V2 SessionScorecard for the DailySession backing this chat.

    The chat URL carries the LearningSession id, but the scorecard endpoint
    is keyed by the DailySession UUID. This bridges the two so the chat UI
    can render the day-level scorecard without leaking the V2 id.
    """
    from app.modules.learning_session.models import LearningSession
    from app.modules.sessions.models import DailySession
    from app.modules.sessions.routes import _make_session_service, _serialize_scorecard

    chat = (
        db.query(LearningSession)
        .filter(
            LearningSession.session_id == session_id,
            LearningSession.user_id == current_user.id,
        )
        .first()
    )
    if chat is None:
        raise HTTPException(status_code=404, detail="chat session not found")

    daily = db.get(DailySession, chat.daily_session_id)
    if daily is None:
        raise HTTPException(status_code=404, detail="daily session not found")

    service = _make_session_service(db)
    scorecard = service.get_scorecard(
        session_id=daily.session_id, user_id=current_user.id,
    )
    if scorecard is None:
        await LearningSessionService(db)._auto_complete_daily_if_ready(chat)
        scorecard = service.get_scorecard(
            session_id=daily.session_id, user_id=current_user.id,
        )
    if scorecard is None:
        raise HTTPException(
            status_code=404,
            detail="session has no scorecard yet",
        )
    return _serialize_scorecard(daily.session_id, scorecard, db=db)


# --- WebSocket --------------------------------------------------------

ws_router = APIRouter()
dev_ws_router = APIRouter()


@dev_rest_router.post(
    "/sessions/start",
    response_model=StartSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_authoring_session(
    week: int = 1,
    day: int = 1,
    credentials: HTTPAuthorizationCredentials | None = Depends(authoring_bearer_scheme),
) -> StartSessionResponse:
    _guard_authoring_auth(credentials)
    service = AuthoringLearningSessionService()
    try:
        return await service.start_session(week=week, day=day)
    except AuthoringModeDisabled as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DayNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@dev_rest_router.post(
    "/sessions/{session_id}/restart",
    response_model=StartSessionResponse,
    status_code=status.HTTP_200_OK,
)
async def restart_authoring_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials | None = Depends(authoring_bearer_scheme),
) -> StartSessionResponse:
    _guard_authoring_auth(credentials)
    service = AuthoringLearningSessionService()
    try:
        return await service.restart_session(session_id=session_id)
    except AuthoringModeDisabled as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AuthoringSessionNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DayNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _resolve_user_from_token(token: str | None, db: Session) -> User | None:
    if not token:
        return None
    payload = decode_token(token)
    if payload is None:
        return None
    sub = payload.get("sub")
    if sub is None:
        return None
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        return None
    return UserRepository(db).get_by_id(user_id)


async def _send(ws: WebSocket, msg: WSOutgoingMessage) -> None:
    await ws.send_text(msg.model_dump_json(exclude_none=True))


@ws_router.websocket("/ws/learning/{session_id}")
async def learning_session_ws(
    websocket: WebSocket,
    session_id: str,
    token: str | None = None,
    db: Session = Depends(get_db),
) -> None:
    user = _resolve_user_from_token(token, db)
    if user is None:
        await websocket.close(code=4401)
        return

    service = LearningSessionService(db)

    session = service.session_repo.get_by_session_id(session_id)
    if session is None or session.user_id != user.id:
        await websocket.close(code=4404)
        return

    await websocket.accept()

    try:
        if not session.messages:
            async for msg in service.initial_messages_stream(session_id):
                await _send(websocket, msg)
        else:
            async for msg in service.resume_messages_stream(session_id):
                await _send(websocket, msg)

        while True:
            raw = await websocket.receive_text()
            try:
                payload = json.loads(raw)
                incoming = WSIncomingMessage.model_validate(payload)
            except (json.JSONDecodeError, ValidationError) as exc:
                await _send(
                    websocket,
                    WSOutgoingMessage(
                        type="error", content=f"Bad message: {exc}"
                    ),
                )
                continue

            try:
                stream = service.process_message_stream(session_id, incoming)
                async for msg in stream:
                    await _send(websocket, msg)
            except Exception as exc:  # pragma: no cover — unexpected
                logger.exception(
                    "ws process_message failed session_id=%s", session_id
                )
                await _send(
                    websocket,
                    WSOutgoingMessage(type="error", content=str(exc)),
                )
                continue

    except WebSocketDisconnect:
        return


@dev_ws_router.websocket("/dev/ws/learning/{session_id}")
async def authoring_learning_session_ws(
    websocket: WebSocket,
    session_id: str,
    token: str | None = Query(default=None),
) -> None:
    if not settings.AUTHORING_CHAT_MODE:
        await websocket.close(code=4404)
        return
    if not _authoring_ws_authorized(token):
        await websocket.close(code=4401)
        return
    service = AuthoringLearningSessionService()
    session = service.store.get(session_id)
    if session is None:
        await websocket.close(code=4404)
        return

    await websocket.accept()

    try:
        if not session.messages:
            async for msg in service.initial_messages_stream(session_id):
                await _send(websocket, msg)
        else:
            async for msg in service.resume_messages_stream(session_id):
                await _send(websocket, msg)

        while True:
            raw = await websocket.receive_text()
            try:
                payload = json.loads(raw)
                incoming = WSIncomingMessage.model_validate(payload)
            except (json.JSONDecodeError, ValidationError) as exc:
                await _send(
                    websocket,
                    WSOutgoingMessage(
                        type="error", content=f"Bad message: {exc}"
                    ),
                )
                continue

            try:
                stream = service.process_message_stream(session_id, incoming)
                async for msg in stream:
                    await _send(websocket, msg)
            except Exception as exc:  # pragma: no cover - unexpected
                logger.exception(
                    "dev ws process_message failed session_id=%s", session_id
                )
                await _send(
                    websocket,
                    WSOutgoingMessage(type="error", content=str(exc)),
                )
                continue

    except WebSocketDisconnect:
        return
