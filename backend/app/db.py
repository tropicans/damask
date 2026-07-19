from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy import event
from sqlalchemy.engine import Engine
from app.core.config import settings

# SQLite connection args to allow multi-threaded access in FastAPI development
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, echo=True)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

def init_db() -> None:
    # Import models here to register them with SQLModel metadata
    from app.models.user import User  # noqa
    from app.models.job import MaskingJob, JobDetail  # noqa
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
