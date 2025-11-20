import tempfile
from pathlib import Path
from typing import Optional, Generator
from contextlib import contextmanager

from logging import getLogger
logger = getLogger("database")

from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy import create_engine, inspect


class DatabaseSetup:

    _session_maker: Optional[sessionmaker] = None

    @staticmethod
    def _reset_database():
        DatabaseSetup._session_maker = None

    @staticmethod
    def init_db(directory: Path, base: type[DeclarativeBase]):
        logger.debug("Initialising database...")

        if DatabaseSetup._session_maker is not None:
            raise RuntimeError("Database already initialised.")

        try:
            directory.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=directory.parent, delete=True):
                pass
        except (PermissionError, OSError) as e:
            raise PermissionError(f"Permission denied: Cannot write to directory {directory.parent}") from e

        engine = create_engine(f"sqlite:///{directory}")

        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        expected_tables = set(base.metadata.tables.keys())

        if existing_tables and existing_tables != expected_tables:
            raise RuntimeError(f"Schema mismatch: Existing database has incompatible schema. "
                             f"Expected tables: {sorted(expected_tables)}, "
                             f"Found tables: {sorted(existing_tables)}")

        base.metadata.create_all(engine)
        DatabaseSetup._session_maker = sessionmaker(bind=engine)
        logger.info(f"Database initialised to {str(directory)}")

    @staticmethod
    @contextmanager
    def get_db_session() -> Generator[Session, None, None]:
        if not DatabaseSetup._session_maker:
            raise RuntimeError("Database not initialised.")
        session = DatabaseSetup._session_maker()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
