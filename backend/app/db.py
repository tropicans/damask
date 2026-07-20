"""
Database module for SecureData Web.
Configures the SQLModel/SQLAlchemy engine, manages SQLite pragmas,
and provides database session dependencies.
"""

import logging
import time

from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from app.core.config import settings

logger = logging.getLogger("app.db")

# SQLite connection args to allow multi-threaded access in FastAPI development
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, echo=True)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Enables SQLite foreign key support on the connection event.
    Ensure that SQLite cascade deletes function properly.
    """
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def _wait_for_db(max_retries: int = 5, delay_seconds: int = 2) -> None:
    """
    Waits for the database to become ready.
    Retries up to max_retries times with delay_seconds between each attempt.
    Raises RuntimeError if the database is unreachable after all retries.
    """
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established.")
            return
        except Exception as exc:
            logger.warning(
                "Database not ready (attempt %d/%d): %s. Retrying in %ds...",
                attempt, max_retries, exc, delay_seconds,
            )
            if attempt < max_retries:
                time.sleep(delay_seconds)
    raise RuntimeError(
        f"Database not reachable after {max_retries} attempts. "
        "Check DATABASE_URL and service health."
    )


def init_db() -> None:
    """
    Initializes database tables. Imports all SQLModel tables to register them
    with metadata before creating tables. Waits for the DB to be ready first.
    """
    _wait_for_db()
    # Import models here to register them with SQLModel metadata
    from app.models.user import User, Invite, LoginAudit  # noqa
    from app.models.job import MaskingJob, JobDetail, RevertJob  # noqa
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    FastAPI Dependency generator for database sessions.
    Yields:
        Session: SQLModel database session.
    """
    with Session(engine) as session:
        yield session

