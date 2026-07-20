import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db import get_session
from app.services.auth import _failed_attempts


# ---------------------------------------------------------------------------
# Lockout reset (autouse — applies to every test in all modules)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_lockout():
    """Resets the brute-force failed attempts counter before each test."""
    _failed_attempts.clear()


# ---------------------------------------------------------------------------
# Shared DB fixtures (switchable via TEST_DATABASE_URL env var)
# ---------------------------------------------------------------------------

def _make_test_engine():
    """
    Build the test SQLAlchemy engine.
    - Default: SQLite in-memory with StaticPool (zero-config).
    - Override: set TEST_DATABASE_URL for PostgreSQL CI runs.
    """
    test_db_url = os.environ.get("TEST_DATABASE_URL", "")
    if test_db_url:
        return create_engine(test_db_url)
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture(name="session")
def session_fixture():
    """
    Provides an isolated database session per test.
    Creates all tables before yielding and drops them after.
    Supports SQLite (default) and PostgreSQL (via TEST_DATABASE_URL).
    """
    test_engine = _make_test_engine()
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Provides a FastAPI TestClient wired to the test database session.
    Uses raise_server_exceptions=False for endpoint error testing.
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app, raise_server_exceptions=False)
    yield client
    app.dependency_overrides.clear()

