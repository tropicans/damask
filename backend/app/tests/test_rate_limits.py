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

@pytest.fixture(autouse=True)
def enable_limiter():
    # Force enable limiter and reset its memory storage before the test runs
    app.state.limiter.enabled = True
    app.state.limiter.reset()
    yield
    # Clean up and disable limiter back to prevent interference with other tests
    app.state.limiter.enabled = False
    app.state.limiter.reset()

def test_auth_rate_limiting(client: TestClient):
    # Send 5 requests to /api/auth/login
    for i in range(5):
        response = client.post(
            "/api/auth/login",
            json={
                "email": f"test{i}@securedata.com",
                "password": "wrongpassword"
            }
        )
        # Should be Bad Request (400) because credentials are wrong, not rate limited yet
        assert response.status_code == 400
        
    # The 6th request should be rate limited (429)
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test6@securedata.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 429
