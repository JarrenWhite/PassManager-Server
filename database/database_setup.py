from pathlib import Path
from sqlalchemy.orm import DeclarativeBase

class DatabaseSetup:

    @staticmethod
    def set_config(directory: Path, base: DeclarativeBase):
        pass
