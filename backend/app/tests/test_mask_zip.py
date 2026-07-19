import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
import json
import io
import zipfile
import pandas as pd

from app.main import app
from app.db import get_session

@pytest.fixture(name="session")
def session_fixture():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    from sqlalchemy import event
    @event.listens_for(test_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        
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

@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient, session: Session):
    from app.models.user import User
    from app.services.auth import hash_password
    user = User(
        username="zipuser",
        email="zipuser@securedata.com",
        password_hash=hash_password("password123"),
        role="admin"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    login_resp = client.post(
        "/api/auth/login",
        json={
            "email": "zipuser@securedata.com",
            "password": "password123"
        }
    )
    token = login_resp.cookies.get("secure_data_session")
    client.cookies.clear()
    return {"Authorization": f"Bearer {token}"}

def test_mask_file_with_key(client: TestClient, auth_headers: dict):
    csv_data = "nama,email,telepon\nBudi,budi@gmail.com,08123456789\nAni,ani@gmail.com,08987654321\n"
    file_bytes = csv_data.encode('utf-8')
    rules = {
        "nama": "Fake Name",
        "email": "Fake Email",
        "telepon": "No Masking"
    }
    
    response = client.post(
        "/api/mask",
        headers=auth_headers,
        files={"file": ("test.csv", file_bytes, "text/csv")},
        data={
            "rules": json.dumps(rules),
            "generate_key": "true"
        }
    )
    
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/zip"
    assert "test_masked.zip" in response.headers.get("content-disposition", "")
    
    # Read the zip archive in-memory
    zip_buf = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_buf, "r") as zf:
        namelist = zf.namelist()
        assert "test_masked.csv" in namelist
        assert "test_reversion_key.json" in namelist
        
        # Read reversion key JSON
        key_content = zf.read("test_reversion_key.json").decode('utf-8')
        mappings = json.loads(key_content)
        assert "nama" in mappings
        assert "email" in mappings
        assert "telepon" not in mappings
        
        # Read masked CSV
        masked_csv_content = zf.read("test_masked.csv").decode('utf-8')
        masked_df = pd.read_csv(io.StringIO(masked_csv_content), dtype=str)
        
        # Assert nama was masked and maps correctly
        assert masked_df["nama"].iloc[0] != "Budi"
        assert mappings["nama"]["Budi"] == masked_df["nama"].iloc[0]
        assert mappings["nama"]["Ani"] == masked_df["nama"].iloc[1]
        
        # Telepon was not masked
        assert masked_df["telepon"].iloc[0] == "08123456789"
