from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.ai import AIRequestLoggingService
from app.main import app
from app.modules.admin.models import AIRequestLog, AdminAuditLog
from app.modules.auth.models import (
    Permission,
    ROLE_ADMIN,
    ROLE_LEARNER,
    ROLE_SUPER_ADMIN,
    Role,
    RolePermission,
    User,
    UserProfile,
    UserRole,
)
from app.modules.auth.repository import RoleRepository
from app.modules.curriculum.models import Course, CourseLevel, CourseStatus, UserEnrollment
from app.modules.progress.models import SkillPoints
from app.modules.responses.models import Evaluation, Feedback, UserResponse
from app.modules.skills.models import Skill, UserSkillScore
from app.modules.subscriptions.models import Payment, Purchase, Subscription
from app.modules.tasks.models import Task, TaskStatus, TaskType, UserTask, UserTaskStatus


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            Role.__table__,
            Permission.__table__,
            RolePermission.__table__,
            User.__table__,
            UserRole.__table__,
            UserProfile.__table__,
            AdminAuditLog.__table__,
            AIRequestLog.__table__,
            Purchase.__table__,
            Subscription.__table__,
            Payment.__table__,
            Course.__table__,
            UserEnrollment.__table__,
            Task.__table__,
            UserTask.__table__,
            UserResponse.__table__,
            Evaluation.__table__,
            Feedback.__table__,
            Skill.__table__,
            UserSkillScore.__table__,
            SkillPoints.__table__,
        ],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session: Session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _seed_roles(db: Session) -> dict[str, Role]:
    roles = RoleRepository(db).ensure_defaults()
    db.commit()
    return roles


def _make_user(
    db: Session,
    roles: dict[str, Role],
    *,
    email: str,
    role_names: list[str],
) -> User:
    user = User(
        email=email,
        password_hash="x",
        name=email.split("@")[0].title(),
        is_superuser=ROLE_SUPER_ADMIN in role_names,
    )
    db.add(user)
    db.flush()
    for role_name in role_names:
        db.add(UserRole(user_id=user.id, role_id=roles[role_name].id))
    db.commit()
    db.refresh(user)
    return user


def _auth_header(user: User, role_names: list[str]) -> dict[str, str]:
    token = create_access_token(
        {
            "sub": str(user.id),
            "roles": role_names,
            "is_superuser": ROLE_SUPER_ADMIN in role_names,
        }
    )
    return {"Authorization": f"Bearer {token}"}


def _seed_feedback_review_chain(
    db: Session,
    *,
    learner: User,
) -> Feedback:
    task = Task(
        title="Reviewable task",
        task_type=TaskType.READING,
        difficulty=2,
        status=TaskStatus.ACTIVE,
        content={"instruction": "Answer briefly."},
    )
    db.add(task)
    db.flush()
    user_task = UserTask(
        user_id=learner.id,
        task_id=task.id,
        status=UserTaskStatus.COMPLETED,
    )
    db.add(user_task)
    db.flush()
    response = UserResponse(
        user_task_id=user_task.id,
        content={"answer": "I goes to school"},
        raw_text="I goes to school",
    )
    db.add(response)
    db.flush()
    evaluation = Evaluation(
        response_id=response.id,
        overall_score=6.5,
        percentage=65,
        report={"percentage": 65, "questions": {}},
    )
    db.add(evaluation)
    db.flush()
    feedback = Feedback(
        evaluation_id=evaluation.id,
        body={"overall_message": "Use 'go' with I.", "score": 65},
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def _seed_billing_records(db: Session, *, learner: User) -> Subscription:
    now = datetime.now(timezone.utc)
    subscription = Subscription(
        user_id=learner.id,
        provider="stripe",
        provider_customer_id="cus_phase3_customer_123456",
        provider_subscription_id="sub_phase3_subscription_123456",
        plan_name="Pro Monthly",
        status="trialing",
        trial_ends_at=now + timedelta(days=7),
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )
    payment = Payment(
        user_id=learner.id,
        provider="stripe",
        provider_payment_id="pi_phase3_payment_123456",
        amount=999.0,
        currency="INR",
        status="paid",
        paid_at=now,
    )
    db.add_all([subscription, payment])
    db.commit()
    db.refresh(subscription)
    return subscription


def test_unauthenticated_user_cannot_access_admin_apis(client: TestClient) -> None:
    response = client.get("/admin/summary")

    assert response.status_code == 401


def test_learner_cannot_access_admin_apis(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    learner = _make_user(
        db_session,
        roles,
        email="learner@example.com",
        role_names=[ROLE_LEARNER],
    )

    response = client.get("/admin/summary", headers=_auth_header(learner, [ROLE_LEARNER]))

    assert response.status_code == 403


def test_admin_can_access_admin_apis(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    admin = _make_user(
        db_session,
        roles,
        email="admin@example.com",
        role_names=[ROLE_ADMIN],
    )

    response = client.get("/admin/summary", headers=_auth_header(admin, [ROLE_ADMIN]))

    assert response.status_code == 200
    assert response.json()["total_users"] == 1


def test_super_admin_can_access_admin_apis(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    super_admin = _make_user(
        db_session,
        roles,
        email="super@example.com",
        role_names=[ROLE_SUPER_ADMIN],
    )

    response = client.get(
        "/admin/summary",
        headers=_auth_header(super_admin, [ROLE_SUPER_ADMIN]),
    )

    assert response.status_code == 200
    assert response.json()["recent_users"][0]["role"] == ROLE_SUPER_ADMIN


def test_user_status_update_uses_soft_inactive_flag(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    admin = _make_user(
        db_session,
        roles,
        email="admin@example.com",
        role_names=[ROLE_ADMIN],
    )
    learner = _make_user(
        db_session,
        roles,
        email="learner@example.com",
        role_names=[ROLE_LEARNER],
    )

    response = client.patch(
        f"/admin/users/{learner.id}/status",
        headers=_auth_header(admin, [ROLE_ADMIN]),
        json={"is_active": False},
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    assert db_session.get(User, learner.id) is not None


def test_audit_log_created_after_admin_action(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    admin = _make_user(
        db_session,
        roles,
        email="admin@example.com",
        role_names=[ROLE_ADMIN],
    )
    learner = _make_user(
        db_session,
        roles,
        email="learner@example.com",
        role_names=[ROLE_LEARNER],
    )

    response = client.patch(
        f"/admin/users/{learner.id}/status",
        headers=_auth_header(admin, [ROLE_ADMIN]),
        json={"is_active": False},
    )

    assert response.status_code == 200
    log = db_session.query(AdminAuditLog).one()
    assert log.admin_user_id == admin.id
    assert log.action == "user.status_change"
    assert log.resource_type == "user"
    assert log.resource_id == str(learner.id)
    assert log.old_value["is_active"] is True
    assert log.new_value["is_active"] is False


def test_learner_cannot_access_audit_logs(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    learner = _make_user(
        db_session,
        roles,
        email="learner@example.com",
        role_names=[ROLE_LEARNER],
    )

    response = client.get(
        "/admin/audit-logs",
        headers=_auth_header(learner, [ROLE_LEARNER]),
    )

    assert response.status_code == 403


def test_admin_can_access_audit_logs(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    admin = _make_user(
        db_session,
        roles,
        email="admin@example.com",
        role_names=[ROLE_ADMIN],
    )
    db_session.add(
        AdminAuditLog(
            admin_user_id=admin.id,
            action="task_template.create",
            resource_type="task_template",
            resource_id="42",
        )
    )
    db_session.commit()

    response = client.get(
        "/admin/audit-logs",
        headers=_auth_header(admin, [ROLE_ADMIN]),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["action"] == "task_template.create"
    assert payload[0]["admin"]["email"] == "admin@example.com"


def test_ai_log_creation_works(db_session: Session) -> None:
    log = AIRequestLoggingService(db_session).record_success(
        agent_name="task_generator",
        model="gpt-4o-mini",
        input_tokens=120,
        output_tokens=40,
        latency_ms=250,
        prompt_version="template_v1",
    )
    db_session.commit()
    db_session.refresh(log)

    saved = db_session.get(AIRequestLog, log.id)
    assert saved is not None
    assert saved.agent_name == "task_generator"
    assert saved.status == "success"
    assert saved.input_tokens == 120


def test_feedback_review_status_update_works(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    admin = _make_user(
        db_session,
        roles,
        email="admin@example.com",
        role_names=[ROLE_ADMIN],
    )
    learner = _make_user(
        db_session,
        roles,
        email="learner@example.com",
        role_names=[ROLE_LEARNER],
    )
    feedback = _seed_feedback_review_chain(db_session, learner=learner)

    response = client.patch(
        f"/admin/feedback-review/{feedback.id}",
        headers=_auth_header(admin, [ROLE_ADMIN]),
        json={"review_status": "flagged", "admin_note": "Needs a clearer rule."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["review_status"] == "flagged"
    assert payload["admin_note"] == "Needs a clearer rule."

    db_session.refresh(feedback)
    assert feedback.review_status == "flagged"
    assert feedback.reviewed_by == admin.id
    assert db_session.query(AdminAuditLog).filter_by(action="feedback.review").count() == 1


def test_sensitive_fields_are_not_exposed_to_normal_admin(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    admin = _make_user(
        db_session,
        roles,
        email="admin@example.com",
        role_names=[ROLE_ADMIN],
    )
    log = AIRequestLog(
        agent_name="teacher_agent",
        model="gpt-4o-mini",
        status="error",
        error_message="OpenAI failed with api_key=sk-secret123 password=hunter2",
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)

    response = client.get(
        f"/admin/ai-logs/{log.id}",
        headers=_auth_header(admin, [ROLE_ADMIN]),
    )

    assert response.status_code == 200
    error_message = response.json()["error_message"]
    assert "sk-secret123" not in error_message
    assert "hunter2" not in error_message
    assert error_message == "Sensitive technical details hidden."


def test_super_admin_gets_sanitized_ai_error_detail(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    super_admin = _make_user(
        db_session,
        roles,
        email="super@example.com",
        role_names=[ROLE_SUPER_ADMIN],
    )
    log = AIRequestLog(
        agent_name="teacher_agent",
        model="gpt-4o-mini",
        status="error",
        error_message="OpenAI failed with api_key=sk-secret123 password=hunter2",
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)

    response = client.get(
        f"/admin/ai-logs/{log.id}",
        headers=_auth_header(super_admin, [ROLE_SUPER_ADMIN]),
    )

    assert response.status_code == 200
    error_message = response.json()["error_message"]
    assert error_message == "OpenAI failed with api_key=[REDACTED] password=[REDACTED]"


def test_permission_checks_block_missing_permission(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    admin = _make_user(
        db_session,
        roles,
        email="admin@example.com",
        role_names=[ROLE_ADMIN],
    )
    RoleRepository(db_session).replace_role_permissions(
        role=roles[ROLE_ADMIN],
        permission_keys={"users.read"},
    )
    db_session.commit()

    response = client.get(
        "/admin/payments",
        headers=_auth_header(admin, [ROLE_ADMIN]),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Missing permission: payments.read"


def test_admin_cannot_access_super_admin_pages(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    admin = _make_user(
        db_session,
        roles,
        email="admin@example.com",
        role_names=[ROLE_ADMIN],
    )

    response = client.get(
        "/admin/roles",
        headers=_auth_header(admin, [ROLE_ADMIN]),
    )

    assert response.status_code == 403


def test_super_admin_can_manage_user_roles_and_audit_is_created(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    super_admin = _make_user(
        db_session,
        roles,
        email="super@example.com",
        role_names=[ROLE_SUPER_ADMIN],
    )
    learner = _make_user(
        db_session,
        roles,
        email="learner@example.com",
        role_names=[ROLE_LEARNER],
    )

    response = client.patch(
        f"/admin/users/{learner.id}/roles",
        headers=_auth_header(super_admin, [ROLE_SUPER_ADMIN]),
        json={"roles": [ROLE_LEARNER, ROLE_ADMIN]},
    )

    assert response.status_code == 200
    assert set(response.json()["roles"]) == {ROLE_LEARNER, ROLE_ADMIN}
    db_session.refresh(learner)
    assert set(learner.role_names()) == {ROLE_LEARNER, ROLE_ADMIN}
    assert (
        db_session.query(AdminAuditLog).filter_by(action="user.roles_update").count()
        == 1
    )


def test_super_admin_can_update_role_permissions(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    super_admin = _make_user(
        db_session,
        roles,
        email="super@example.com",
        role_names=[ROLE_SUPER_ADMIN],
    )

    response = client.patch(
        f"/admin/roles/{roles[ROLE_ADMIN].id}/permissions",
        headers=_auth_header(super_admin, [ROLE_SUPER_ADMIN]),
        json={"permission_keys": ["users.read", "payments.read"]},
    )

    assert response.status_code == 200
    assert response.json()["permissions"] == ["payments.read", "users.read"]
    assert (
        db_session.query(AdminAuditLog)
        .filter_by(action="role.permissions_update")
        .count()
        == 1
    )


def test_learner_cannot_access_billing_admin_apis(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    learner = _make_user(
        db_session,
        roles,
        email="learner@example.com",
        role_names=[ROLE_LEARNER],
    )
    _seed_billing_records(db_session, learner=learner)

    response = client.get(
        "/admin/payments",
        headers=_auth_header(learner, [ROLE_LEARNER]),
    )

    assert response.status_code == 403


def test_admin_can_read_limited_billing_info(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    admin = _make_user(
        db_session,
        roles,
        email="admin@example.com",
        role_names=[ROLE_ADMIN],
    )
    learner = _make_user(
        db_session,
        roles,
        email="learner@example.com",
        role_names=[ROLE_LEARNER],
    )
    _seed_billing_records(db_session, learner=learner)

    response = client.get(
        f"/admin/users/{learner.id}/billing",
        headers=_auth_header(admin, [ROLE_ADMIN]),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["subscription"]["plan_name"] == "Pro Monthly"
    assert payload["subscription"]["provider_subscription_id"] == "sub_...3456"
    assert payload["payments"][0]["provider_payment_id"] == "pi_p...3456"
    assert "phase3" not in payload["payments"][0]["provider_payment_id"]


def test_mock_payment_change_creates_audit_log(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    learner = _make_user(
        db_session,
        roles,
        email="learner@example.com",
        role_names=[ROLE_LEARNER],
    )
    db_session.add(
        Course(
            slug="beginner-24w",
            title="24-Week Foundation",
            description="Foundation plan",
            duration_weeks=24,
            target_level=CourseLevel.BEGINNER,
            status=CourseStatus.ACTIVE,
        )
    )
    db_session.commit()

    response = client.post(
        "/api/subscriptions/purchase",
        headers=_auth_header(learner, [ROLE_LEARNER]),
        json={"plan_id": "beginner-24w"},
    )

    assert response.status_code == 200
    payment = db_session.query(Payment).one()
    assert payment.status == "paid"
    audit_log = db_session.query(AdminAuditLog).filter_by(action="payment.recorded").one()
    assert audit_log.resource_type == "payment"
    assert audit_log.resource_id == str(payment.id)
    assert audit_log.new_value["provider_payment_id"] == "[REDACTED]"


def test_super_admin_can_update_subscription_status_and_audit_is_created(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    super_admin = _make_user(
        db_session,
        roles,
        email="super@example.com",
        role_names=[ROLE_SUPER_ADMIN],
    )
    learner = _make_user(
        db_session,
        roles,
        email="learner@example.com",
        role_names=[ROLE_LEARNER],
    )
    subscription = _seed_billing_records(db_session, learner=learner)

    response = client.patch(
        f"/admin/subscriptions/{subscription.id}",
        headers=_auth_header(super_admin, [ROLE_SUPER_ADMIN]),
        json={"status": "active"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "active"
    db_session.refresh(subscription)
    assert subscription.status == "active"
    audit_log = (
        db_session.query(AdminAuditLog)
        .filter_by(action="subscription.update")
        .one()
    )
    assert audit_log.old_value["status"] == "trialing"
    assert audit_log.new_value["status"] == "active"


def test_admin_cannot_update_subscription_status(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    admin = _make_user(
        db_session,
        roles,
        email="admin@example.com",
        role_names=[ROLE_ADMIN],
    )
    learner = _make_user(
        db_session,
        roles,
        email="learner@example.com",
        role_names=[ROLE_LEARNER],
    )
    subscription = _seed_billing_records(db_session, learner=learner)

    response = client.patch(
        f"/admin/subscriptions/{subscription.id}",
        headers=_auth_header(admin, [ROLE_ADMIN]),
        json={"status": "active"},
    )

    assert response.status_code == 403


def test_task_template_crud_works(
    client: TestClient,
    db_session: Session,
) -> None:
    roles = _seed_roles(db_session)
    admin = _make_user(
        db_session,
        roles,
        email="admin@example.com",
        role_names=[ROLE_ADMIN],
    )
    headers = _auth_header(admin, [ROLE_ADMIN])

    create_response = client.post(
        "/admin/task-templates",
        headers=headers,
        json={
            "title": "Admin-created reading template",
            "task_type": "reading",
            "difficulty": 3,
            "status": "draft",
            "content": {"instruction": "Read the passage.", "activities": []},
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "Admin-created reading template"
    assert created["status"] == "draft"

    list_response = client.get("/admin/task-templates", headers=headers)
    assert list_response.status_code == 200
    assert [template["id"] for template in list_response.json()] == [created["id"]]

    patch_response = client.patch(
        f"/admin/task-templates/{created['id']}",
        headers=headers,
        json={"title": "Updated template", "status": "active", "difficulty": 4},
    )

    assert patch_response.status_code == 200
    patched = patch_response.json()
    assert patched["title"] == "Updated template"
    assert patched["status"] == "active"
    assert patched["difficulty"] == 4

    archive_response = client.delete(
        f"/admin/task-templates/{created['id']}",
        headers=headers,
    )

    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "archived"
    assert db_session.get(Task, created["id"]) is not None
