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
        directory = Path(self.test_dir)
        DatabaseSetup.set_config(directory, TestBase)


if __name__ == '__main__':
    pytest.main(['-v', __file__])
