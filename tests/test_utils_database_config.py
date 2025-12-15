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
        assert Path(called["filepath"]).resolve() == config_path

    def test_load_given_file(self, monkeypatch):
        """Should load the given config file if one given"""

        called = {"count": 0, "filepath": None}
        def fake_read(self, filepath):
            called["count"] += 1
            called["filepath"] = filepath
            return [str(filepath)]
        monkeypatch.setattr(ConfigParser, "read", fake_read)

        config_path = Path("test/file/path/config.ini")

        DatabaseConfig.load(config_path)

        assert called["count"] == 1
        assert Path(called["filepath"]).resolve() == config_path.resolve()

    def test_load_sets_parser_instance(self, monkeypatch):
        """Should set _config to parser instance"""

        created_parsers = []

        class FakeConfigParser(ConfigParser):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                created_parsers.append(self)

            def read(
                    self,
                    filenames,
                    encoding=None,
                ):
                    return [str(filenames)]

        monkeypatch.setattr(
            "utils.database_config.ConfigParser",
            FakeConfigParser
        )

        DatabaseConfig.load(Path("test/file/path/config.ini"))

        assert DatabaseConfig._config is not None
        assert isinstance(DatabaseConfig._config, ConfigParser)
        assert DatabaseConfig._config is created_parsers[0]

    def test_load_called_again(self, monkeypatch):
        """Should not read the file again on repeated load calls"""

        parser = ConfigParser()

        def fake_config_parser():
            return parser

        called = {"count": 0, "filepath": None}
        def fake_read(filepath, encoding=None):
            called["count"] += 1
            called["filepath"] = filepath
            return [str(filepath)]

        monkeypatch.setattr("utils.database_config.ConfigParser", fake_config_parser)
        monkeypatch.setattr(parser, "read", fake_read)

        DatabaseConfig.load(Path("test/file/path/config.ini"))
        DatabaseConfig.load(Path("other.ini"))

        assert called["count"] == 1
        assert called["filepath"].resolve() == Path("test/file/path/config.ini").resolve()
        assert DatabaseConfig._config is parser

    def test_config_ini_missing(self, monkeypatch):
        """Should raise exception if config file is missing"""
        def fake_read(filenames, encoding=None):
            return []

        monkeypatch.setattr(ConfigParser, "read", fake_read)

        with pytest.raises(FileNotFoundError):
            DatabaseConfig.load(Path("missing.ini"))


class TestGetPath():
    """Test the get_path function"""

    def test_returns_correct_path(self, monkeypatch):
        """Should return the correct path"""

        parser = ConfigParser()
        parser.add_section("paths")
        parser.set("paths", "data_dir", "data/files")

        monkeypatch.setattr(DatabaseConfig, "_config", parser)

        result = DatabaseConfig.get_path("data_dir")

        expected = DatabaseConfig.PROJECT_ROOT / Path("data/files")

        assert result == expected
        assert isinstance(result, Path)


if __name__ == '__main__':
    pytest.main(['-v', __file__])
