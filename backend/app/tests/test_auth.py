import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session

from app.main import app
from app.db import get_session
from app.models.user import User

import os

TEST_DB_FILE = "test.db"
# Use an isolated, file-based SQLite database for unit tests to ensure sharing across connections
test_engine = create_engine(f"sqlite:///{TEST_DB_FILE}", connect_args={"check_same_thread": False})

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)
    # Remove the test database file
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

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
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@securedata.com"

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
    token = login_response.json()["access_token"]

    # Get /me with valid token
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

    # Get /me with invalid token
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401

def test_secure_endpoints_protection(client: TestClient):
    # Trying preview without auth
    response = client.post("/api/preview")
    assert response.status_code == 401

    # Trying mask without auth
    response = client.post("/api/mask")
    assert response.status_code == 401
