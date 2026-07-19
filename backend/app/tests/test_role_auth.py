import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db import get_session

@pytest.fixture(name="session")
def session_fixture():
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

def test_regular_user_access_denied(client: TestClient):
    # Register user with default role 'user'
    register_resp = client.post(
        "/api/auth/register",
        json={
            "username": "reguser",
            "email": "reg@securedata.com",
            "password": "strongpassword123",
            "role": "user"
        }
    )
    assert register_resp.status_code == 201
    assert register_resp.json()["role"] == "user"
    
    token = register_resp.cookies.get("secure_data_session")
    client.cookies.clear()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try calling get jobs history
    response = client.get("/api/jobs/", headers=headers)
    assert response.status_code == 403
    assert "Akses ditolak" in response.json()["detail"]
    
    # Try calling get jobs stats
    response = client.get("/api/jobs/stats", headers=headers)
    assert response.status_code == 403
    assert "Akses ditolak" in response.json()["detail"]

def test_admin_user_access_allowed(client: TestClient):
    # Register user with 'admin' role
    register_resp = client.post(
        "/api/auth/register",
        json={
            "username": "adminuser",
            "email": "admin@securedata.com",
            "password": "strongpassword123",
            "role": "admin"
        }
    )
    assert register_resp.status_code == 201
    assert register_resp.json()["role"] == "admin"
    
    token = register_resp.cookies.get("secure_data_session")
    client.cookies.clear()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try calling get jobs history
    response = client.get("/api/jobs/", headers=headers)
    assert response.status_code == 200
    
    # Try calling get jobs stats
    response = client.get("/api/jobs/stats", headers=headers)
    assert response.status_code == 200
