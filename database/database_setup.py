import os
import logging
logger = logging.getLogger("database")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .database_models import Base

# Global engine instance to avoid creating multiple engines
_engine = None
_session_local = None

def get_db_filename():
    return os.getenv("VAULT_PATH", "data/vault.db")

def get_db_url():
    return f"sqlite:///{get_db_filename()}"

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(get_db_url(), pool_pre_ping=True)
    return _engine

def get_session_local():
    global _session_local
    if _session_local is None:
        _session_local = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _session_local

def reset_engine():
    """Reset the global engine and session factory. Used for testing."""
    global _engine, _session_local
    if _engine:
        _engine.dispose()
    _engine = None
    _session_local = None

def init_db():
    db_filename = get_db_filename()
    if not os.path.exists(db_filename):
        logger.info("init_db: Database not found. Creating new database.")
        os.makedirs(os.path.dirname(db_filename), exist_ok=True)
        engine = get_engine()
        Base.metadata.create_all(engine)
        logger.info("init_db: Database created.")
    else:
        logger.debug("init_db: Existing database discovered.")
