import os
import sys
import pytest
from typing import Dict, Any
from pathlib import Path
from configparser import ConfigParser

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from utils.database_config import DatabaseConfig


class TestLoad():
    """Test cases for the load function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        DatabaseConfig._config = None
        yield

    def test_load_default_file(self, monkeypatch):
        """Should load the default config file if no filepath given"""

        called = {"count": 0, "filepath": None}
        def fake_read(self, filepath):
            called["count"] += 1
            called["filepath"] = filepath
            return [str(filepath)]
        monkeypatch.setattr(ConfigParser, "read", fake_read)

        DatabaseConfig.load()

        config_path = (Path(__file__).resolve().parent / ".." / "config" / "config.ini").resolve()

        assert called["count"] == 1
        assert called["filepath"].resolve() == config_path



if __name__ == '__main__':
    pytest.main(['-v', __file__])
