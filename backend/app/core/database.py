"""
Database utilities.

This module sets up the SQLAlchemy engine and session factory based on the
configuration.  It also exposes a dependency for injecting a database session
into FastAPI endpoints.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import settings


# Create the SQLAlchemy engine
engine = create_engine(settings.database_url, echo=False, future=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()