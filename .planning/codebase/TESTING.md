# Testing Patterns

**Analysis Date:** 2026-07-20

## Test Framework

**Runner:**
- **Backend:** Pytest 9.x (`pytest` in python virtualenv)
- **Frontend:** None configured (no testing dependencies or test runner in `frontend/package.json`)

**Assertion Library:**
- **Backend:** Python's native `assert` statement.

**Run Commands:**
```bash
# Run all backend tests
uv run pytest app/tests

# Run a single backend test module
uv run pytest app/tests/test_auth.py

# Run a specific backend test function
uv run pytest app/tests/test_auth.py::test_login_user
```

## Test File Organization

**Location:**
- All backend tests are located in a flat structure under `backend/app/tests/`.

**Naming:**
- Backend test files use the pattern `test_*.py` (e.g., `test_auth.py`, `test_masker.py`).

**Structure:**
```
backend/
└── app/
    ├── services/
    │   ├── auth.py
    │   └── masker.py
    └── tests/
        ├── conftest.py
        ├── test_auth.py
        └── test_masker.py
```

## Test Structure

**Suite Organization:**
Tests are structured as flat module-level functions (no nested class wrappers). Fixtures are passed directly as parameters to the test functions.

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

# Fixture injection and standard assert patterns
def test_register_user(client: TestClient, valid_invite_token: str):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@securedata.com",
            "password": "StrongPass1",
            "invite_token": valid_invite_token
        }
    )
    assert response.status_code == 201
    assert "secure_data_session" in response.cookies
    
    data = response.json()
    assert data["username"] == "testuser"
```

**Patterns:**
- Use `pytest` fixtures for setup, resource generation, and teardown.
- Avoid using global database state; utilize dependency injection overrides to keep databases isolated.

## Mocking & Database Isolation

**Database Isolation:**
Instead of using the primary developer database, tests use an ephemeral, isolated in-memory SQLite database per test.

```python
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool

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
```

**FastAPI Dependency Injection Overrides:**
To mock the database session inside the application, the `session` fixture is injected into a test client by overriding FastAPI's global session dependency.

```python
from app.main import app
from app.db import get_session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app, raise_server_exceptions=False)
    yield client
    app.dependency_overrides.clear()
```

## Fixtures and Factories

**Test Data/Fixtures:**
Common fixtures defined in test modules:
- `session`: Re-creates an empty SQLite in-memory database.
- `client`: Injects the test session and returns a FastAPI TestClient.
- `admin_user`: Directly registers a user with the `admin` role in the test DB.
- `admin_cookies`: Authenticates as admin and returns session cookies.
- `valid_invite_token`: Creates a temporary registration invite link using the admin API.

**Shared Setup:**
The global `backend/app/tests/conftest.py` contains automated autouse fixtures like `clear_lockout()` to reset global limits or lockout states before every test execution.

---

*Testing analysis: 2026-07-20*
*Update when test patterns change*
