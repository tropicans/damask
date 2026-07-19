"""
Integration tests for Phase 11: Auth Policy & Invite Registration.

Tests:
- Invite creation (admin-only, returns URL)
- Invite-based registration gate (rejects without/with invalid/expired/used invite)
- Password policy enforcement (no uppercase, no digit, too short → 422)
- Account lockout — HTTP 423 after 5 failed attempts from same IP
- Successful login clears failed attempt counter
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta

from app.main import app
from app.db import get_session
from app.models.user import User, Invite
from app.services.auth import hash_password, _failed_attempts


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app, raise_server_exceptions=False)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="admin_user")
def admin_user_fixture(session: Session):
    admin = User(
        username="testadmin",
        email="admin@test.com",
        password_hash=hash_password("AdminPass1"),
        role="admin"
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin


@pytest.fixture(name="admin_headers")
def admin_headers_fixture(client: TestClient, admin_user: User):
    _failed_attempts.clear()
    response = client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "AdminPass1"
    })
    assert response.status_code == 200, f"Admin login failed: {response.json()}"
    token = response.cookies.get("secure_data_session")
    client.cookies.clear()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="valid_invite_token")
def valid_invite_token_fixture(client: TestClient, admin_headers):
    response = client.post("/api/auth/invite", headers=admin_headers)
    assert response.status_code == 201, f"Invite creation failed: {response.json()}"
    return response.json()["token"]


# ---------------------------------------------------------------------------
# Invite Creation Tests
# ---------------------------------------------------------------------------

def test_create_invite_as_admin_succeeds(client: TestClient, admin_headers):
    """Admin can create an invite link — returns 201 with token and invite_url."""
    response = client.post("/api/auth/invite", headers=admin_headers)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.json()}"
    data = response.json()
    assert "token" in data
    assert "invite_url" in data
    assert "invite=" in data["invite_url"]
    assert data["is_used"] is False


def test_create_invite_as_non_admin_fails(client: TestClient, session: Session):
    """Non-admin users cannot create invite links — returns 403."""
    # Create a regular user directly in DB
    user = User(
        username="regularuser",
        email="user@test.com",
        password_hash=hash_password("UserPass1"),
        role="user"
    )
    session.add(user)
    session.commit()

    _failed_attempts.clear()
    login_resp = client.post("/api/auth/login", json={"email": "user@test.com", "password": "UserPass1"})
    assert login_resp.status_code == 200
    token = login_resp.cookies.get("secure_data_session")
    client.cookies.clear()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/auth/invite", headers=headers)
    assert response.status_code == 403
    assert "admin" in response.json()["detail"].lower()


def test_create_invite_returns_correct_expiry(client: TestClient, admin_headers):
    """Invite expiry is approximately 48 hours from creation."""
    response = client.post("/api/auth/invite", headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", ""))
    now = datetime.utcnow()
    diff_hours = (expires_at - now).total_seconds() / 3600
    # Allow 1-minute tolerance around 48h
    assert 47.98 <= diff_hours <= 48.02, f"Expected ~48h expiry, got {diff_hours:.2f}h"


# ---------------------------------------------------------------------------
# Invite Registration Gate Tests
# ---------------------------------------------------------------------------

def test_register_without_invite_rejected(client: TestClient):
    """Registration without invite token is rejected with HTTP 400."""
    response = client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "SecurePass1"
    })
    assert response.status_code == 400
    assert "undangan" in response.json()["detail"].lower()


def test_register_with_invalid_invite_rejected(client: TestClient, admin_user: User):
    """Registration with a non-existent invite token is rejected with HTTP 400."""
    response = client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "SecurePass1",
        "invite_token": "00000000-0000-0000-0000-000000000000"
    })
    assert response.status_code == 400


def test_register_with_valid_invite_succeeds(client: TestClient, valid_invite_token: str):
    """Registration with a valid invite token succeeds — returns 201 with user profile."""
    response = client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "SecurePass1",
        "invite_token": valid_invite_token
    })
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.json()}"
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["username"] == "newuser"


def test_invite_is_single_use(client: TestClient, valid_invite_token: str):
    """Invite token cannot be reused after first successful registration."""
    # First registration succeeds
    resp1 = client.post("/api/auth/register", json={
        "username": "user1",
        "email": "user1@test.com",
        "password": "SecurePass1",
        "invite_token": valid_invite_token
    })
    assert resp1.status_code == 201

    # Second registration with same token fails
    resp2 = client.post("/api/auth/register", json={
        "username": "user2",
        "email": "user2@test.com",
        "password": "SecurePass1",
        "invite_token": valid_invite_token
    })
    assert resp2.status_code == 400
    assert "sudah digunakan" in resp2.json()["detail"]


def test_register_with_expired_invite_rejected(client: TestClient, session: Session, admin_user: User):
    """Registration with an expired invite token is rejected with HTTP 400."""
    # Create an expired invite directly in DB
    expired_invite = Invite(
        created_by=admin_user.id,
        expires_at=datetime.utcnow() - timedelta(hours=1),  # 1 hour in the past
        is_used=False
    )
    session.add(expired_invite)
    session.commit()
    session.refresh(expired_invite)

    response = client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "SecurePass1",
        "invite_token": expired_invite.token
    })
    assert response.status_code == 400
    assert "kadaluarsa" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Password Policy Tests
# ---------------------------------------------------------------------------

def test_register_with_no_uppercase_rejected(client: TestClient, valid_invite_token: str):
    """Password without an uppercase letter is rejected with HTTP 422."""
    response = client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "securepass1",  # no uppercase
        "invite_token": valid_invite_token
    })
    assert response.status_code == 422


def test_register_with_no_digit_rejected(client: TestClient, admin_headers, session: Session):
    """Password without a digit is rejected with HTTP 422."""
    invite_resp = client.post("/api/auth/invite", headers=admin_headers)
    token = invite_resp.json()["token"]
    response = client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "SecurePassword",  # no digit
        "invite_token": token
    })
    assert response.status_code == 422


def test_register_with_no_lowercase_rejected(client: TestClient, admin_headers):
    """Password without a lowercase letter is rejected with HTTP 422."""
    invite_resp = client.post("/api/auth/invite", headers=admin_headers)
    token = invite_resp.json()["token"]
    response = client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "SECUREPASS1",  # no lowercase
        "invite_token": token
    })
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Account Lockout Tests (PROD-14)
# ---------------------------------------------------------------------------

def test_account_lockout_after_5_failed_attempts(client: TestClient, admin_user: User):
    """Account/IP is locked after 5 failed login attempts — 6th returns HTTP 423."""
    _failed_attempts.clear()

    # 5 failed attempts — should return 400 (not locked yet)
    for i in range(5):
        resp = client.post("/api/auth/login", json={
            "email": "admin@test.com",
            "password": "WrongPassword"
        })
        assert resp.status_code == 400, f"Attempt {i+1}: expected 400, got {resp.status_code}"

    # 6th attempt — should be locked (423)
    resp = client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "WrongPassword"
    })
    assert resp.status_code == 423, f"Expected 423 after lockout, got {resp.status_code}: {resp.json()}"
    assert "dikunci" in resp.json()["detail"].lower()


def test_successful_login_clears_failed_attempts(client: TestClient, admin_user: User):
    """Successful login resets the failed attempt counter for the IP."""
    _failed_attempts.clear()

    # 3 failed attempts
    for _ in range(3):
        client.post("/api/auth/login", json={"email": "admin@test.com", "password": "Wrong"})

    # Successful login clears counter
    resp = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "AdminPass1"})
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.json()}"

    # Now 4 more failures should NOT trigger lockout (counter was reset, only 4 attempts now)
    for _ in range(4):
        client.post("/api/auth/login", json={"email": "admin@test.com", "password": "Wrong"})

    # 5th attempt after reset should return 400 (not 423, since we reset after successful login)
    resp = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "Wrong"})
    assert resp.status_code == 400, f"Expected 400 (not locked), got {resp.status_code}"
