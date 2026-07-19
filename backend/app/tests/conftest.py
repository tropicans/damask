import pytest
from app.services.auth import _failed_attempts

@pytest.fixture(autouse=True)
def clear_lockout():
    """Resets the brute-force failed attempts counter before each test to ensure isolation."""
    _failed_attempts.clear()
