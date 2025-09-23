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

    def test_setup_config_function_takes_correct_parameters(self):
        """Should take directory and Database Base"""
        TestBase = declarative_base()
        directory = Path(self.test_dir) / "test_vault.db"
        DatabaseSetup.set_config(directory, TestBase)

    def test_init_db_returns_exception_if_no_config(self):
        """Should return exception if no config is complete"""
        try:
            DatabaseSetup.init_db()
            raise AssertionError("Expected no config violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("no config exists" in error_message), f"Expected config violation, got: {error_message}"


if __name__ == '__main__':
    pytest.main(['-v', __file__])
