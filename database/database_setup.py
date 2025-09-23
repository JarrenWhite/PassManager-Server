from pathlib import Path
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine

class DatabaseSetup:

    _initialised: bool = False

    @staticmethod
    def init_db(directory: Path, base: DeclarativeBase):
        if DatabaseSetup._initialised:
            raise RuntimeError("Database already initialised.")

        directory.parent.mkdir(parents=True, exist_ok=True)

        engine = create_engine(f"sqlite:///{directory}")
        base.metadata.create_all(engine)
        DatabaseSetup._initialised = True
