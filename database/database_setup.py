import os
import logging
logger = logging.getLogger("database")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .database_models import Base

def get_db_filename():
    return os.getenv("VAULT_PATH", "data/vault.db")

def get_db_url():
    return f"sqlite:///{get_db_filename()}"

def get_engine():
    return create_engine(get_db_url(), pool_pre_ping=True)

def get_session_local():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

def init_db():
    db_filename = get_db_filename()
    if not os.path.exists(db_filename):
        logger.info("Database not found. Creating new database...")
        os.makedirs(os.path.dirname(db_filename), exist_ok=True)
        engine = get_engine()
        Base.metadata.create_all(engine)
        logger.info("Database created.")
    else:
        logger.info("Existing database discovered.")
