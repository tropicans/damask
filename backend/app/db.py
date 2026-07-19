from sqlmodel import Session, create_engine, SQLModel
from app.core.config import settings

# SQLite connection args to allow multi-threaded access in FastAPI development
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, echo=True)

def init_db() -> None:
    # Import models here to register them with SQLModel metadata
    from app.models.user import User  # noqa
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
