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
def auth_headers_fixture(client: TestClient):
    client.post(
        "/api/auth/register",
        json={
            "username": "revertuser",
            "email": "revertuser@securedata.com",
            "password": "password123",
            "role": "admin"
        }
    )
    login_resp = client.post(
        "/api/auth/login",
        json={
            "email": "revertuser@securedata.com",
            "password": "password123"
        }
    )
    token = login_resp.cookies.get("secure_data_session")
    client.cookies.clear()
    return {"Authorization": f"Bearer {token}"}

def test_revert_endpoint_success(client: TestClient, auth_headers: dict):
    csv_data = "nama,email,telepon\nBudi,budi@gmail.com,08123456789\nAni,ani@gmail.com,08987654321\n"
    file_bytes = csv_data.encode('utf-8')
    rules = {
        "nama": "Fake Name",
        "email": "Fake Email",
        "telepon": "No Masking"
    }
    
    # 1. Mask the file and generate key
    mask_resp = client.post(
        "/api/mask",
        headers=auth_headers,
        files={"file": ("test_masked.csv", file_bytes, "text/csv")},
        data={
            "rules": json.dumps(rules),
            "generate_key": "true"
        }
    )
    assert mask_resp.status_code == 200
    
    # Extract zip contents in-memory
    zip_buf = io.BytesIO(mask_resp.content)
    with zipfile.ZipFile(zip_buf, "r") as zf:
        masked_csv = zf.read("test_masked_masked.csv")
        reversion_key = zf.read("test_masked_reversion_key.json")
        
    # 2. Revert the file using the extracted key
    revert_resp = client.post(
        "/api/mask/revert",
        headers=auth_headers,
        files={
            "file": ("test_masked_masked.csv", masked_csv, "text/csv"),
            "key": ("test_masked_reversion_key.json", reversion_key, "application/json")
        }
    )
    
    assert revert_resp.status_code == 200
    assert "test_masked_reverted.csv" in revert_resp.headers.get("content-disposition", "")
    
    reverted_df = pd.read_csv(io.StringIO(revert_resp.text), dtype=str)
    original_df = pd.read_csv(io.StringIO(csv_data), dtype=str)
    pd.testing.assert_frame_equal(reverted_df, original_df)

def test_revert_endpoint_mismatched_column(client: TestClient, auth_headers: dict):
    csv_data = "nama,email,telepon\nBudi,budi@gmail.com,08123456789\n"
    key_data = {
        "nama": {"Budi": "FakeName"},
        "missing_column": {"Val": "Masked"}
    }
    
    response = client.post(
        "/api/mask/revert",
        headers=auth_headers,
        files={
            "file": ("test.csv", csv_data.encode('utf-8'), "text/csv"),
            "key": ("key.json", json.dumps(key_data).encode('utf-8'), "application/json")
        }
    )
    
    assert response.status_code == 400
    assert "Kolom berikut tidak ditemukan di dalam berkas: missing_column" in response.json()["detail"]

def test_revert_endpoint_unmapped_value(client: TestClient, auth_headers: dict):
    # Masked value in file is "FakeName", but the key has another value
    csv_data = "nama,email\nFakeName,budi@gmail.com\n"
    key_data = {
        "nama": {"Budi": "OtherFakeName"}
    }
    
    response = client.post(
        "/api/mask/revert",
        headers=auth_headers,
        files={
            "file": ("test.csv", csv_data.encode('utf-8'), "text/csv"),
            "key": ("key.json", json.dumps(key_data).encode('utf-8'), "application/json")
        }
    )
    
    assert response.status_code == 400
    assert "Nilai tidak cocok pada kolom 'nama': FakeName" in response.json()["detail"]

def test_revert_endpoint_malformed_json_key(client: TestClient, auth_headers: dict):
    csv_data = "nama,email\nFakeName,budi@gmail.com\n"
    
    response = client.post(
        "/api/mask/revert",
        headers=auth_headers,
        files={
            "file": ("test.csv", csv_data.encode('utf-8'), "text/csv"),
            "key": ("key.json", b"{invalid-json", "application/json")
        }
    )
    
    assert response.status_code == 400
    assert "JSON tidak valid" in response.json()["detail"]
