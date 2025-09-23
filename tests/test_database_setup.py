import os
import sys
import pytest
import shutil
import tempfile
from pathlib import Path

from sqlalchemy.orm import declarative_base

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_setup import DatabaseSetup

class TestDatabaseSetup:
    """Test cases for database setup"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self.test_dir = tempfile.mkdtemp()

        yield

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init_db_function_takes_correct_parameters(self):
        """Should take directory and Database Base"""
        TestBase = declarative_base()
        directory = Path(self.test_dir)
        file_path = directory / "test_vault.db"
        DatabaseSetup.init_db(file_path, TestBase)
    
    def test_init_db_creates_directory(self):
        """Should create a directory if one does not exist"""
        TestBase = declarative_base()
        directory = Path(self.test_dir)
        file_path = directory / "test_vault.db"
        DatabaseSetup.init_db(file_path, TestBase)

        assert directory.exists()
    
    def test_init_db_creates_database_file(self):
        """Should create database file if none exists"""
        TestBase = declarative_base()
        directory = Path(self.test_dir)
        file_path = directory / "test_vault.db"
        DatabaseSetup.init_db(file_path, TestBase)

        assert file_path.exists()

    def test_init_db_does_not_overwrite_existing_db_file(self):
        """Should not overwrite an existing db file at target"""
        TestBase = declarative_base()
        directory = Path(self.test_dir)
        file_path = directory / "test_vault.db"

        DatabaseSetup.init_db(file_path, TestBase)
        initial_mtime = file_path.stat().st_mtime

        DatabaseSetup.init_db(file_path, TestBase)
        second_mtime = file_path.stat().st_mtime

        assert initial_mtime == second_mtime


if __name__ == '__main__':
    pytest.main(['-v', __file__])
