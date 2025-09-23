from pathlib import Path
from sqlalchemy.orm import DeclarativeBase

class DatabaseSetup:

    @staticmethod
    def init_db(directory: Path, base: DeclarativeBase):
        directory.parent.mkdir(parents=True, exist_ok=True)
