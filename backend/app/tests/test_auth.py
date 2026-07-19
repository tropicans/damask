import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import get_session
from app.models.user import User, Invite
from app.services.auth import hash_password, _failed_attempts

import os
from datetime import datetime, timedelta


@pytest.fixture(name="session")
def session_fixture():
    # Use an in-memory SQLite database with StaticPool to keep database alive in-memory
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


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
    """Creates an admin user directly in the DB for invite-based tests."""
    admin = User(
        username="admin",
        email="admin@securedata.com",
        password_hash=hash_password("AdminPass1"),
        role="admin"
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin


@pytest.fixture(name="admin_cookies")
def admin_cookies_fixture(client: TestClient, admin_user: User):
    """Logs in as admin and returns cookies for authenticated admin requests."""
    response = client.post("/api/auth/login", json={
        "email": "admin@securedata.com",
        "password": "AdminPass1"
    })
    return response.cookies


@pytest.fixture(name="valid_invite_token")
def valid_invite_token_fixture(client: TestClient, admin_cookies):
    """Creates an invite token via admin API and returns the token string."""
    response = client.post("/api/auth/invite", cookies=admin_cookies)
    assert response.status_code == 201, f"Failed to create invite: {response.json()}"
    return response.json()["token"]


def test_register_user(client: TestClient, valid_invite_token: str):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@securedata.com",
            "password": "StrongPass1",
            "invite_token": valid_invite_token
        }
    )
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.json()}"
    assert "secure_data_session" in response.cookies
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@securedata.com"
    assert "id" in data
    assert "password_hash" not in data


def test_register_duplicate_email(client: TestClient, admin_cookies, session: Session):
    # Create first invite and register first user
    invite1_resp = client.post("/api/auth/invite", cookies=admin_cookies)
    token1 = invite1_resp.json()["token"]
    client.post(
        "/api/auth/register",
        json={
            "username": "user1",
            "email": "user@securedata.com",
            "password": "StrongPass1",
            "invite_token": token1
        }
    )

    # Create second invite and try to register with same email
    invite2_resp = client.post("/api/auth/invite", cookies=admin_cookies)
    token2 = invite2_resp.json()["token"]
    response = client.post(
        "/api/auth/register",
        json={
            "username": "user2",
            "email": "user@securedata.com",
            "password": "StrongPass1",
            "invite_token": token2
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email sudah terdaftar."


def test_register_password_too_short(client: TestClient, valid_invite_token: str):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@securedata.com",
            "password": "short",
            "invite_token": valid_invite_token
        }
    )
    assert response.status_code == 422  # Pydantic min_length validation error


def test_login_user(client: TestClient, valid_invite_token: str):
    # Register first
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@securedata.com",
            "password": "StrongPass1",
            "invite_token": valid_invite_token
        }
    )

    # Login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@securedata.com",
            "password": "StrongPass1"
        }
    )
    assert response.status_code == 200
    assert "secure_data_session" in response.cookies
    data = response.json()
    assert "access_token" not in data
    assert data["email"] == "test@securedata.com"


def test_login_wrong_credentials(client: TestClient):
    # Login with non-existent user
    response = client.post(
        "/api/auth/login",
        json={
            "email": "wrong@securedata.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email atau kata sandi salah."


def test_get_me(client: TestClient, valid_invite_token: str):
    # Register
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@securedata.com",
            "password": "StrongPass1",
            "invite_token": valid_invite_token
        }
    )

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test@securedata.com",
            "password": "StrongPass1"
        }
    )
    token = login_response.cookies.get("secure_data_session")

    # Get /me with valid token in cookie
    with client:
        client.cookies.set("secure_data_session", token)
        response = client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

    # Get /me with invalid token in cookie
    with client:
        client.cookies.set("secure_data_session", "invalidtoken")
        response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_secure_endpoints_protection(client: TestClient):
    # Trying preview without auth (triggers CSRF block or auth check)
    response = client.post("/api/preview")
    # CSRF blocks unauthenticated mutating requests since session cookie is not set
    assert response.status_code in [401, 403]

    # Trying mask without auth
    response = client.post("/api/mask")
    assert response.status_code in [401, 403]
