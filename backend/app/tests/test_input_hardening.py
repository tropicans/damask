import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db import get_session

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

def test_invalid_mime_type(client: TestClient):
    register_resp = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@securedata.com",
            "password": "strongpassword123"
        }
    )
    assert register_resp.status_code == 201
    token = register_resp.cookies.get("secure_data_session")
    client.cookies.clear()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try uploading file with csv extension but invalid image/png MIME-type
    response = client.post(
        "/api/preview",
        files={"file": ("test.csv", b"fake data", "image/png")},
        headers=headers
    )
    assert response.status_code == 400
    assert "Tipe MIME file tidak valid" in response.json()["detail"]

def test_file_too_large(client: TestClient):
    # Override size constraint temporarily for the test to avoid creating a real 50MB payload
    from app.api.endpoints import preview, mask
    old_preview_max = preview.MAX_FILE_SIZE_BYTES
    old_mask_max = mask.MAX_FILE_SIZE_BYTES
    
    preview.MAX_FILE_SIZE_BYTES = 10
    mask.MAX_FILE_SIZE_BYTES = 10
    
    try:
        register_resp = client.post(
            "/api/auth/register",
            json={
                "username": "testuser2",
                "email": "test2@securedata.com",
                "password": "strongpassword123"
            }
        )
        assert register_resp.status_code == 201
        token = register_resp.cookies.get("secure_data_session")
        client.cookies.clear()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Upload 25 bytes file (exceeds 10 bytes limit)
        response = client.post(
            "/api/preview",
            files={"file": ("test.csv", b"col1,col2,col3\nval1,val2,val3\n", "text/csv")},
            headers=headers
        )
        assert response.status_code == 413
        assert "File terlalu besar" in response.json()["detail"]
    finally:
        # Restore limits
        preview.MAX_FILE_SIZE_BYTES = old_preview_max
        mask.MAX_FILE_SIZE_BYTES = old_mask_max
