from pathlib import Path
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine

class DatabaseSetup:

    @staticmethod
    def init_db(directory: Path, base: DeclarativeBase):
        directory.parent.mkdir(parents=True, exist_ok=True)

        engine = create_engine(f"sqlite:///{directory}")
        base.metadata.create_all(engine)
