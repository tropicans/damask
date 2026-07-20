import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

def test_regular_user_access_denied(client: TestClient, session: Session):
    from app.models.user import User
    from app.services.auth import hash_password
    user = User(
        username="reguser",
        email="reg@securedata.com",
        password_hash=hash_password("strongpassword123"),
        role="user"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    login_resp = client.post(
        "/api/auth/login",
        json={
            "email": "reg@securedata.com",
            "password": "strongpassword123"
        }
    )
    token = login_resp.cookies.get("secure_data_session")
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

def test_admin_user_access_allowed(client: TestClient, session: Session):
    from app.models.user import User
    from app.services.auth import hash_password
    user = User(
        username="adminuser",
        email="admin@securedata.com",
        password_hash=hash_password("strongpassword123"),
        role="admin"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    login_resp = client.post(
        "/api/auth/login",
        json={
            "email": "admin@securedata.com",
            "password": "strongpassword123"
        }
    )
    token = login_resp.cookies.get("secure_data_session")
    client.cookies.clear()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try calling get jobs history
    response = client.get("/api/jobs/", headers=headers)
    assert response.status_code == 200
    
    # Try calling get jobs stats
    response = client.get("/api/jobs/stats", headers=headers)
    assert response.status_code == 200
