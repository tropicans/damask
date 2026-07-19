import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import get_session
from app.models.user import User

import os

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
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_register_user(client: TestClient):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@securedata.com",
            "password": "strongpassword123"
        }
    )
    assert response.status_code == 201
    assert "secure_data_session" in response.cookies
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@securedata.com"
    assert "id" in data
    assert "password_hash" not in data

def test_register_duplicate_email(client: TestClient):
    # Register first user
    client.post(
        "/api/auth/register",
        json={
            "username": "user1",
            "email": "user@securedata.com",
            "password": "password123"
        }
    )
    
    # Register second user with same email
    response = client.post(
        "/api/auth/register",
        json={
            "username": "user2",
            "email": "user@securedata.com",
            "password": "differentpass"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email sudah terdaftar."

def test_register_password_too_short(client: TestClient):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@securedata.com",
            "password": "short"
        }
    )
    assert response.status_code == 422 # Pydantic validation error

def test_login_user(client: TestClient):
    # Register first
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@securedata.com",
            "password": "strongpassword123"
        }
    )

    # Login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@securedata.com",
            "password": "strongpassword123"
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

def test_get_me(client: TestClient):
    # Register
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@securedata.com",
            "password": "strongpassword123"
        }
    )

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test@securedata.com",
            "password": "strongpassword123"
        }
    )
    token = login_response.cookies.get("secure_data_session")

    # Get /me with valid token in cookie
    response = client.get(
        "/api/auth/me",
        cookies={"secure_data_session": token}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

    # Get /me with invalid token in cookie
    response = client.get(
        "/api/auth/me",
        cookies={"secure_data_session": "invalidtoken"}
    )
    assert response.status_code == 401

def test_secure_endpoints_protection(client: TestClient):
    # Trying preview without auth (triggers CSRF block or auth check)
    response = client.post("/api/preview")
    # CSRF blocks unauthenticated mutating requests since session cookie is not set
    assert response.status_code in [401, 403]

    # Trying mask without auth
    response = client.post("/api/mask")
    assert response.status_code in [401, 403]
