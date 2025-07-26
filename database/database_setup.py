import os
import logging
from typing import Optional
logger = logging.getLogger("database")

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from .database_models import Base

# Global engine instance to avoid creating multiple engines
_engine: Optional[Engine] = None
_session_local: Optional[sessionmaker[Session]] = None

def _get_db_filename() -> str:
    return os.getenv("VAULT_PATH", "data/vault.db")

def _get_db_url() -> str:
    return f"sqlite:///{_get_db_filename()}"

def _get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(_get_db_url(), pool_pre_ping=True)
    return _engine

def get_session_local() -> sessionmaker[Session]:
    global _session_local
    if _session_local is None:
        _session_local = sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())
    return _session_local

def reset_engine() -> None:
    """Reset the global engine and session factory. Used for testing."""
    global _engine, _session_local
    if _engine:
        _engine.dispose()
    _engine = None
    _session_local = None

def init_db() -> None:
    db_filename = _get_db_filename()
    if not os.path.exists(db_filename):
        logger.info("init_db: Database not found. Creating new database.")
        os.makedirs(os.path.dirname(db_filename), exist_ok=True)
        engine = _get_engine()
        Base.metadata.create_all(engine)
        logger.info("init_db: Database created.")
    else:
        logger.debug("init_db: Existing database discovered.")
