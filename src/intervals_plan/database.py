"""
Unified SQLite Database Engine and Session Management for Personal AI Training Analyst.
Enforces SQLite foreign keys, WAL mode, transaction isolation, and backup/restore capabilities.
"""

from __future__ import annotations

import contextlib
import logging
import os
import pathlib
import shutil
import sqlite3
from typing import Generator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()

DEFAULT_DB_DIR = pathlib.Path.cwd() / "data" / "database"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "training_analyst.db"


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
    """Enforce SQLite foreign key constraints and fast WAL mode."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.close()


def get_db_path(custom_path: Optional[str | pathlib.Path] = None) -> pathlib.Path:
    """Resolve database path from argument, environment variable, or default."""
    if custom_path:
        return pathlib.Path(custom_path)
    env_path = os.environ.get("TRAINING_ANALYST_DB_PATH")
    if env_path:
        return pathlib.Path(env_path)
    return DEFAULT_DB_PATH


def create_db_engine(db_path: Optional[str | pathlib.Path] = None) -> Engine:
    """Create SQLAlchemy engine for the SQLite database."""
    resolved_path = get_db_path(db_path)
    if resolved_path != pathlib.Path(":memory:"):
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        sqlite_url = f"sqlite:///{resolved_path.as_posix()}"
    else:
        sqlite_url = "sqlite:///:memory:"

    engine = create_engine(
        sqlite_url,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
    )
    return engine


def init_db(engine: Optional[Engine] = None, db_path: Optional[str | pathlib.Path] = None) -> Engine:
    """Initialize all database tables defined on Base."""
    # Import db_models to register all declarative models onto Base.metadata
    from intervals_plan import db_models  # noqa: F401

    eng = engine or create_db_engine(db_path)
    Base.metadata.create_all(bind=eng)
    return eng


def get_session_factory(engine: Optional[Engine] = None, db_path: Optional[str | pathlib.Path] = None) -> sessionmaker[Session]:
    """Create a configured sessionmaker instance."""
    eng = engine or create_db_engine(db_path)
    return sessionmaker(autocommit=False, autoflush=False, bind=eng)


@contextlib.contextmanager
def get_db_session(engine: Optional[Engine] = None, db_path: Optional[str | pathlib.Path] = None) -> Generator[Session, None, None]:
    """Context manager providing a transactional database session."""
    factory = get_session_factory(engine, db_path)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def backup_database(src_path: Optional[str | pathlib.Path] = None, dest_path: Optional[str | pathlib.Path] = None) -> pathlib.Path:
    """Safely back up the SQLite database to destination using SQLite online backup API."""
    source_p = get_db_path(src_path)
    if not source_p.exists():
        raise FileNotFoundError(f"Database file not found at {source_p}")

    if dest_path:
        destination_p = pathlib.Path(dest_path)
    else:
        import datetime
        ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_dir = source_p.parent.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        destination_p = backup_dir / f"training_analyst_backup_{ts}.db"

    destination_p.parent.mkdir(parents=True, exist_ok=True)

    # Use native SQLite backup API for 100% consistent live backup
    src_conn = sqlite3.connect(source_p)
    dst_conn = sqlite3.connect(destination_p)
    with dst_conn:
        src_conn.backup(dst_conn)
    dst_conn.close()
    src_conn.close()
    logger.info("Database backup created at %s", destination_p)
    return destination_p


def restore_database(backup_path: str | pathlib.Path, target_path: Optional[str | pathlib.Path] = None) -> pathlib.Path:
    """Restore database from backup using SQLite backup API."""
    bk_p = pathlib.Path(backup_path)
    if not bk_p.exists():
        raise FileNotFoundError(f"Backup file not found at {bk_p}")

    tgt_p = get_db_path(target_path)
    tgt_p.parent.mkdir(parents=True, exist_ok=True)

    src_conn = sqlite3.connect(bk_p)
    dst_conn = sqlite3.connect(tgt_p)
    with dst_conn:
        src_conn.backup(dst_conn)
    dst_conn.close()
    src_conn.close()
    logger.info("Database restored from %s to %s", bk_p, tgt_p)
    return tgt_p
