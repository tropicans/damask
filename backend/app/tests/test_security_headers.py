import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_security_headers():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    
    # Check that each security header is present with correct values
    assert response.headers.get("Content-Security-Policy") == "default-src 'self'; frame-ancestors 'none';"
    assert response.headers.get("Strict-Transport-Security") == "max-age=63072000; includeSubDomains; preload"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
