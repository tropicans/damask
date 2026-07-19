import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session, select
import json
import os
from datetime import datetime, timedelta

from app.main import app
from app.db import get_session
from app.models.user import User
from app.models.job import MaskingJob, JobDetail



TEST_DB_FILE = "test_jobs.db"
test_engine = create_engine(f"sqlite:///{TEST_DB_FILE}", connect_args={"check_same_thread": False})

@pytest.fixture(name="session")
def session_fixture():
    # Make sure SQLite foreign keys are enabled on connect event for the test engine as well
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    @event.listens_for(test_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)
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

@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient):
    client.post(
        "/api/auth/register",
        json={
            "username": "jobuser",
            "email": "jobuser@securedata.com",
            "password": "password123"
        }
    )
    login_resp = client.post(
        "/api/auth/login",
        json={
            "email": "jobuser@securedata.com",
            "password": "password123"
        }
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_masking_logging_success(client: TestClient, auth_headers: dict, session: Session):
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
        data={"rules": json.dumps(rules)}
    )
    assert response.status_code == 200
    
    # Check that job is logged in database
    db_jobs = session.exec(select(MaskingJob)).all()
    assert len(db_jobs) == 1
    job = db_jobs[0]
    assert job.file_name == "test.csv"
    assert job.file_size_bytes == len(file_bytes)
    assert job.row_count == 2
    assert job.status == "SUCCESS"
    assert job.error_message is None
    
    # Check that job details are logged in database
    db_details = session.exec(select(JobDetail).where(JobDetail.job_id == job.id)).all()
    assert len(db_details) == 2
    cols = [d.column_name for d in db_details]
    rules_applied = [d.rule_name for d in db_details]
    assert "nama" in cols
    assert "email" in cols
    assert "Fake Name" in rules_applied
    assert "Fake Email" in rules_applied

def test_masking_logging_failure(client: TestClient, auth_headers: dict, session: Session):
    response = client.post(
        "/api/mask",
        headers=auth_headers,
        files={"file": ("test.csv", b"invalid data", "text/csv")},
        data={"rules": "invalid-json{"}
    )
    assert response.status_code == 400
    
    db_jobs = session.exec(select(MaskingJob)).all()
    assert len(db_jobs) == 1
    job = db_jobs[0]
    assert job.file_name == "test.csv"
    assert job.status == "FAILED"
    assert "JSON tidak valid" in job.error_message

def test_get_jobs_history(client: TestClient, auth_headers: dict, session: Session):
    user = session.exec(select(User).where(User.email == "jobuser@securedata.com")).one()
    
    now = datetime.utcnow()
    job1 = MaskingJob(user_id=user.id, file_name="file1.csv", file_size_bytes=100, row_count=5, status="SUCCESS", created_at=now - timedelta(minutes=5))
    job2 = MaskingJob(user_id=user.id, file_name="file2.xlsx", file_size_bytes=200, row_count=10, status="FAILED", error_message="Error", created_at=now)
    session.add(job1)
    session.add(job2)
    session.commit()
    
    response = client.get("/api/jobs/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["file_name"] == "file2.xlsx"
    assert data[1]["file_name"] == "file1.csv"

def test_get_jobs_stats(client: TestClient, auth_headers: dict, session: Session):
    user = session.exec(select(User).where(User.email == "jobuser@securedata.com")).one()
    
    job1 = MaskingJob(user_id=user.id, file_name="file1.csv", file_size_bytes=100, row_count=5, status="SUCCESS")
    job2 = MaskingJob(user_id=user.id, file_name="file2.xlsx", file_size_bytes=200, row_count=10, status="SUCCESS")
    job3 = MaskingJob(user_id=user.id, file_name="file3.csv", file_size_bytes=300, row_count=None, status="FAILED", error_message="Error")
    
    session.add(job1)
    session.add(job2)
    session.add(job3)
    session.commit()
    
    response = client.get("/api/jobs/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_files"] == 2
    assert data["total_rows"] == 15
    assert data["success_rate"] == 66.67

def test_get_job_details(client: TestClient, auth_headers: dict, session: Session):
    user = session.exec(select(User).where(User.email == "jobuser@securedata.com")).one()
    
    job = MaskingJob(user_id=user.id, file_name="file1.csv", file_size_bytes=100, row_count=5, status="SUCCESS")
    session.add(job)
    session.commit()
    
    detail = JobDetail(job_id=job.id, column_name="nama", rule_name="Fake Name")
    session.add(detail)
    session.commit()
    
    # Fetch details
    response = client.get(f"/api/jobs/{job.id}/details", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["column_name"] == "nama"
    assert data[0]["rule_name"] == "Fake Name"

def test_get_job_details_unauthorized(client: TestClient, auth_headers: dict, session: Session):
    # Register and login another user
    client.post(
        "/api/auth/register",
        json={
            "username": "otheruser",
            "email": "other@securedata.com",
            "password": "password123"
        }
    )
    other_login = client.post(
        "/api/auth/login",
        json={
            "email": "other@securedata.com",
            "password": "password123"
        }
    )
    other_token = other_login.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    # Create job for first user
    user = session.exec(select(User).where(User.email == "jobuser@securedata.com")).one()
    job = MaskingJob(user_id=user.id, file_name="file1.csv", file_size_bytes=100, row_count=5, status="SUCCESS")
    session.add(job)
    session.commit()
    
    # Other user tries to access details
    response = client.get(f"/api/jobs/{job.id}/details", headers=other_headers)
    assert response.status_code == 403
    assert "tidak memiliki akses" in response.json()["detail"]

def test_cascade_delete_user_jobs(client: TestClient, auth_headers: dict, session: Session):
    user = session.exec(select(User).where(User.email == "jobuser@securedata.com")).one()
    
    job = MaskingJob(user_id=user.id, file_name="file1.csv", file_size_bytes=100, row_count=5, status="SUCCESS")
    session.add(job)
    session.commit()
    
    detail = JobDetail(job_id=job.id, column_name="nama", rule_name="Fake Name")
    session.add(detail)
    session.commit()
    
    # Assert they exist
    assert len(session.exec(select(MaskingJob)).all()) == 1
    assert len(session.exec(select(JobDetail)).all()) == 1
    
    # Delete user
    session.delete(user)
    session.commit()
    
    # Verify cascade delete cleared everything
    assert len(session.exec(select(MaskingJob)).all()) == 0
    assert len(session.exec(select(JobDetail)).all()) == 0
