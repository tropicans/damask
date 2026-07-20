import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models.user import User, LoginAudit
from app.services.auth import hash_password

def create_user(session: Session, username: str, email: str, role: str, is_active: bool = True) -> User:
    user = User(
        username=username,
        email=email,
        password_hash=hash_password("strongpassword123"),
        role=role,
        is_active=is_active
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_auth_headers(client: TestClient, email: str) -> dict:
    login_resp = client.post(
        "/api/auth/login",
        json={"email": email, "password": "strongpassword123"}
    )
    token = login_resp.cookies.get("secure_data_session")
    client.cookies.clear()
    return {"Authorization": f"Bearer {token}"}

def test_admin_endpoints_access_control(client: TestClient, session: Session):
    # Create an admin, an auditor, and a user
    admin = create_user(session, "admin", "admin@test.com", "admin")
    auditor = create_user(session, "auditor", "auditor@test.com", "auditor")
    user = create_user(session, "user", "user@test.com", "user")

    admin_headers = get_auth_headers(client, admin.email)
    auditor_headers = get_auth_headers(client, auditor.email)
    user_headers = get_auth_headers(client, user.email)

    # Test list users access
    assert client.get("/api/admin/users", headers=admin_headers).status_code == 200
    assert client.get("/api/admin/users", headers=auditor_headers).status_code == 403
    assert client.get("/api/admin/users", headers=user_headers).status_code == 403

    # Test toggle user status access
    status_payload = {"is_active": False}
    assert client.put(f"/api/admin/users/{user.id}/status", json=status_payload, headers=admin_headers).status_code == 200
    # Reset status back to True so user is active again for subsequent assertions
    assert client.put(f"/api/admin/users/{user.id}/status", json={"is_active": True}, headers=admin_headers).status_code == 200
    assert client.put(f"/api/admin/users/{user.id}/status", json=status_payload, headers=auditor_headers).status_code == 403
    assert client.put(f"/api/admin/users/{user.id}/status", json=status_payload, headers=user_headers).status_code == 403

    # Test update user role access
    role_payload = {"role": "auditor"}
    assert client.put(f"/api/admin/users/{user.id}/role", json=role_payload, headers=admin_headers).status_code == 200
    assert client.put(f"/api/admin/users/{user.id}/role", json=role_payload, headers=auditor_headers).status_code == 403
    assert client.put(f"/api/admin/users/{user.id}/role", json=role_payload, headers=user_headers).status_code == 403

    # Test list login audits access
    assert client.get("/api/admin/login-audits", headers=admin_headers).status_code == 200
    assert client.get("/api/admin/login-audits", headers=auditor_headers).status_code == 403
    assert client.get("/api/admin/login-audits", headers=user_headers).status_code == 403

def test_deactivated_user_lockout_and_session_invalidation(client: TestClient, session: Session):
    admin = create_user(session, "admin", "admin@test.com", "admin")
    target_user = create_user(session, "user", "user@test.com", "user")

    admin_headers = get_auth_headers(client, admin.email)
    user_headers = get_auth_headers(client, target_user.email)

    # User starts active, test cookie authentication
    res = client.get("/api/auth/me", headers=user_headers)
    assert res.status_code == 200
    assert res.json()["is_active"] is True

    # Deactivate the user via Admin API
    res = client.put(f"/api/admin/users/{target_user.id}/status", json={"is_active": False}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["is_active"] is False

    # Check that subsequent requests fail with 401
    res = client.get("/api/auth/me", headers=user_headers)
    assert res.status_code == 401
    assert "dinonaktifkan" in res.json()["detail"]

    # Try to login again
    res = client.post("/api/auth/login", json={"email": target_user.email, "password": "strongpassword123"})
    assert res.status_code == 400
    assert "dinonaktifkan" in res.json()["detail"]

def test_role_changes(client: TestClient, session: Session):
    admin = create_user(session, "admin", "admin@test.com", "admin")
    target_user = create_user(session, "user", "user@test.com", "user")

    admin_headers = get_auth_headers(client, admin.email)

    # Demote/Promote role validation
    res = client.put(f"/api/admin/users/{target_user.id}/role", json={"role": "auditor"}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["role"] == "auditor"

    res = client.put(f"/api/admin/users/{target_user.id}/role", json={"role": "invalid"}, headers=admin_headers)
    assert res.status_code == 400
    assert "Peran tidak valid" in res.json()["detail"]

def test_self_lockout_prevention_single_admin(client: TestClient, session: Session):
    admin = create_user(session, "admin", "admin@test.com", "admin")
    admin_headers = get_auth_headers(client, admin.email)

    # Try deactivating itself (should fail as only active admin)
    res = client.put(f"/api/admin/users/{admin.id}/status", json={"is_active": False}, headers=admin_headers)
    assert res.status_code == 400
    assert "satu-satunya admin aktif yang tersisa" in res.json()["detail"]

    # Try demoting itself (should fail as only active admin)
    res = client.put(f"/api/admin/users/{admin.id}/role", json={"role": "user"}, headers=admin_headers)
    assert res.status_code == 400
    assert "satu-satunya admin aktif yang tersisa" in res.json()["detail"]

def test_self_lockout_allowed_multiple_admins(client: TestClient, session: Session):
    admin1 = create_user(session, "admin1", "admin1@test.com", "admin")
    admin2 = create_user(session, "admin2", "admin2@test.com", "admin")

    admin1_headers = get_auth_headers(client, admin1.email)

    # Try demoting admin1 (should pass because admin2 is another active admin)
    res = client.put(f"/api/admin/users/{admin1.id}/role", json={"role": "user"}, headers=admin1_headers)
    assert res.status_code == 200
    assert res.json()["role"] == "user"

def test_login_audit_trail_logging(client: TestClient, session: Session):
    # Log successful login
    admin = create_user(session, "admin", "admin@test.com", "admin")
    admin_headers = get_auth_headers(client, admin.email)

    # Query login audits (should contain at least 1 SUCCESS for the login above)
    res = client.get("/api/admin/login-audits", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert data["items"][0]["email"] == "admin@test.com"
    assert data["items"][0]["status"] == "SUCCESS"

    # Log failed login with bad password
    client.post("/api/auth/login", json={"email": "admin@test.com", "password": "wrongpassword"})
    
    # Query audits again for FAILED
    res = client.get("/api/admin/login-audits", params={"status": "FAILED"}, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["email"] == "admin@test.com"
    assert data["items"][0]["status"] == "FAILED"

    # Log failed login with nonexistent email
    client.post("/api/auth/login", json={"email": "nonexistent@test.com", "password": "wrongpassword"})

    # Query all failed attempts
    res = client.get("/api/admin/login-audits", params={"status": "FAILED"}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["total"] == 2
