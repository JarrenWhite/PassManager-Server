from configparser import ConfigParser
from typing import Optional
from pathlib import Path


class DatabaseConfig:
    _config = None


    PROJECT_ROOT = Path(__file__).resolve().parents[2]


    @classmethod
    def load(cls, file_path: Optional[Path] = None):
        if cls._config is not None:
            return

        if not file_path:
            file_path = Path(__file__).resolve().parents[2] / "config" / "db_config.ini"

        parser = ConfigParser()
        read_files = parser.read(file_path)

        if not read_files:
            raise FileNotFoundError(f"Config file not found: {file_path}")

        cls._config = parser


    @classmethod
    def get_path(cls, key: str) -> Optional[Path]:
        if cls._config is None:
            cls.load()

        section = cls._config.get("paths") # type: ignore

        if section is None:
            return None
        value = section.get(key).strip()
        if not value:
            return None

        try:
            return cls.PROJECT_ROOT / Path(value)
        except Exception:
            return None
