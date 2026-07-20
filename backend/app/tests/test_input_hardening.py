import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

def test_invalid_mime_type(client: TestClient, session: Session):
    from app.models.user import User
    from app.services.auth import hash_password
    user = User(
        username="testuser",
        email="test@securedata.com",
        password_hash=hash_password("strongpassword123"),
        role="user"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    login_resp = client.post(
        "/api/auth/login",
        json={
            "email": "test@securedata.com",
            "password": "strongpassword123"
        }
    )
    token = login_resp.cookies.get("secure_data_session")
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

def test_file_too_large(client: TestClient, session: Session):
    # Override size constraint temporarily for the test to avoid creating a real 50MB payload
    from app.api.endpoints import preview, mask
    old_preview_max = preview.MAX_FILE_SIZE_BYTES
    old_mask_max = mask.MAX_FILE_SIZE_BYTES
    
    preview.MAX_FILE_SIZE_BYTES = 10
    mask.MAX_FILE_SIZE_BYTES = 10
    
    try:
        from app.models.user import User
        from app.services.auth import hash_password
        user = User(
            username="testuser2",
            email="test2@securedata.com",
            password_hash=hash_password("strongpassword123"),
            role="user"
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        login_resp = client.post(
            "/api/auth/login",
            json={
                "email": "test2@securedata.com",
                "password": "strongpassword123"
            }
        )
        token = login_resp.cookies.get("secure_data_session")
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
