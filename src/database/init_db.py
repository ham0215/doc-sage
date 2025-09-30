"""Database initialization."""
import os
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base

logger = logging.getLogger(__name__)


def get_database_url(db_path: str = None) -> str:
    """
    Get database URL.

    Args:
        db_path: Path to SQLite database file (default from env: DB_PATH)

    Returns:
        SQLAlchemy database URL
    """
    if db_path is None:
        db_path = os.getenv("DB_PATH", "/app/data/doc-sage.db")

    # Ensure parent directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    return f"sqlite:///{db_path}"


def init_database(db_path: str = None) -> sessionmaker:
    """
    Initialize database and create all tables.

    Args:
        db_path: Path to SQLite database file (default from env: DB_PATH)

    Returns:
        SQLAlchemy sessionmaker instance
    """
    database_url = get_database_url(db_path)
    logger.info(f"Initializing database: {database_url}")

    engine = create_engine(
        database_url,
        echo=False,
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

    # Create sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return SessionLocal


def get_session(db_path: str = None) -> Session:
    """
    Get a database session.

    Args:
        db_path: Path to SQLite database file (default from env: DB_PATH)

    Returns:
        SQLAlchemy Session instance
    """
    SessionLocal = init_database(db_path)
    return SessionLocal()