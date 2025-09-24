from pathlib import Path
from typing import Optional

from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy import create_engine

class DatabaseSetup:

    _sessionMaker: Optional[sessionmaker] = None

    @staticmethod
    def _reset_database():
        DatabaseSetup._sessionMaker = None

    @staticmethod
    def init_db(directory: Path, base: DeclarativeBase):
        if DatabaseSetup._sessionMaker is not None:
            raise RuntimeError("Database already initialised.")

        directory.parent.mkdir(parents=True, exist_ok=True)

        engine = create_engine(f"sqlite:///{directory}")
        base.metadata.create_all(engine)
        DatabaseSetup._sessionMaker = sessionmaker(bind=engine)

    @staticmethod
    def get_session() -> sessionmaker[Session]:
        if not DatabaseSetup._sessionMaker:
            raise RuntimeError("Database not initialised.")
        return DatabaseSetup._sessionMaker
