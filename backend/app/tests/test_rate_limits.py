import pytest
from fastapi.testclient import TestClient
from app.main import app

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
    from app.services.auth import _failed_attempts
    from unittest.mock import patch
    _failed_attempts.clear()

    with patch("app.api.endpoints.auth.is_ip_locked", return_value=False):
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
