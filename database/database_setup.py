from pathlib import Path
from sqlalchemy.orm import DeclarativeBase

class DatabaseSetup:

    @staticmethod
    def set_config(directory: Path, base: DeclarativeBase):
        pass

    @staticmethod
    def init_db():
        raise RuntimeError("No config exists")
