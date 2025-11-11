"""
Database session management with connection pooling
Enterprise-grade connection handling for SQLAlchemy
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, event, Engine, pool
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool, StaticPool

from backend.db.models import Base

# Global engine and session factory
_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None
_scoped_session_factory: Optional[scoped_session] = None


def get_database_url() -> str:
    """
    Get database URL from environment or use default
    Supports both SQLite and PostgreSQL for enterprise deployments
    """
    # Check for explicit database URL
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        # Handle Heroku/Vercel postgres:// URLs
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        return db_url

    # Check for Vercel deployment
    if os.environ.get('VERCEL'):
        # Use in-memory SQLite for Vercel (read-only filesystem)
        return 'sqlite:///:memory:'

    # Default to local SQLite
    db_path = os.environ.get('LOKI_DB_PATH', 'data/loki.db')
    return f'sqlite:///{db_path}'


def get_engine(echo: bool = False, pool_size: int = 5, max_overflow: int = 10) -> Engine:
    """
    Get or create database engine with connection pooling

    Args:
        echo: Enable SQL query logging
        pool_size: Number of persistent connections
        max_overflow: Max connections above pool_size

    Returns:
        SQLAlchemy Engine instance
    """
    global _engine

    if _engine is not None:
        return _engine

    db_url = get_database_url()
    is_sqlite = db_url.startswith('sqlite')

    # Configure engine based on database type
    if is_sqlite:
        # SQLite specific configuration
        if db_url == 'sqlite:///:memory:':
            # In-memory database for testing/Vercel
            _engine = create_engine(
                db_url,
                echo=echo,
                connect_args={
                    'check_same_thread': False,  # Allow multi-threading
                    'timeout': 30  # Connection timeout
                },
                poolclass=StaticPool,  # Use static pool for in-memory
            )
        else:
            # File-based SQLite
            # Ensure directory exists
            if '/' in db_url:
                db_file = db_url.replace('sqlite:///', '')
                db_dir = os.path.dirname(db_file)
                if db_dir:
                    os.makedirs(db_dir, exist_ok=True)

            _engine = create_engine(
                db_url,
                echo=echo,
                connect_args={
                    'check_same_thread': False,
                    'timeout': 30
                },
                poolclass=StaticPool,  # SQLite works best with static pool
            )

        # Enable foreign key support for SQLite
        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
            cursor.execute("PRAGMA synchronous=NORMAL")  # Balance safety and speed
            cursor.close()

    else:
        # PostgreSQL or other database
        _engine = create_engine(
            db_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,  # Recycle connections after 1 hour
            poolclass=QueuePool,
        )

    return _engine


def get_session_factory() -> sessionmaker:
    """
    Get or create session factory

    Returns:
        SQLAlchemy sessionmaker instance
    """
    global _session_factory

    if _session_factory is None:
        engine = get_engine()
        _session_factory = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False  # Allow access to objects after commit
        )

    return _session_factory


def get_scoped_session() -> scoped_session:
    """
    Get thread-local scoped session
    Useful for web applications to ensure one session per request

    Returns:
        Scoped session instance
    """
    global _scoped_session_factory

    if _scoped_session_factory is None:
        session_factory = get_session_factory()
        _scoped_session_factory = scoped_session(session_factory)

    return _scoped_session_factory


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions
    Automatically handles commits and rollbacks

    Usage:
        with get_session() as session:
            document = Document(content="test")
            session.add(document)
            # Auto-commits on exit

    Yields:
        SQLAlchemy Session instance
    """
    session_factory = get_session_factory()
    session = session_factory()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(drop_all: bool = False) -> None:
    """
    Initialize database schema
    Creates all tables defined in models

    Args:
        drop_all: If True, drops all tables before creating
    """
    engine = get_engine()

    if drop_all:
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)


def dispose_engine() -> None:
    """
    Dispose of engine and reset session factories
    Call this when shutting down application
    """
    global _engine, _session_factory, _scoped_session_factory

    if _scoped_session_factory is not None:
        _scoped_session_factory.remove()
        _scoped_session_factory = None

    if _engine is not None:
        _engine.dispose()
        _engine = None

    _session_factory = None


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection helper for FastAPI/Flask

    Usage with FastAPI:
        @app.get("/items")
        def list_items(db: Session = Depends(get_db)):
            return db.query(Item).all()

    Yields:
        Database session
    """
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


class DatabaseHealth:
    """Health check utilities for database"""

    @staticmethod
    def check_connection() -> bool:
        """
        Check if database connection is healthy

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            return False

    @staticmethod
    def get_stats() -> dict:
        """
        Get database connection pool statistics

        Returns:
            Dictionary with pool stats
        """
        try:
            engine = get_engine()
            pool = engine.pool

            return {
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'pool_timeout': pool.timeout(),
            }
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def get_table_counts() -> dict:
        """
        Get row counts for all tables

        Returns:
            Dictionary mapping table names to row counts
        """
        from backend.db.models import (
            Document, Validation, ValidationResult,
            Correction, AuditTrail, Tag
        )

        counts = {}
        try:
            with get_session() as session:
                counts['documents'] = session.query(Document).count()
                counts['validations'] = session.query(Validation).count()
                counts['validation_results'] = session.query(ValidationResult).count()
                counts['corrections'] = session.query(Correction).count()
                counts['audit_trails'] = session.query(AuditTrail).count()
                counts['tags'] = session.query(Tag).count()
        except Exception as e:
            counts['error'] = str(e)

        return counts
