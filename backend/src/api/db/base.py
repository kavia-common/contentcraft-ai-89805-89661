from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from ..core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    """Create database tables."""
    from .models import user, blog  # noqa: F401
    Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    """Provide a DB session to request handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
