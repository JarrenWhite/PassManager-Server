import os
import sys
import pytest
import shutil
import tempfile
from pathlib import Path

from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column
from sqlalchemy import Integer, inspect

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_setup import DatabaseSetup

class TestDatabaseSetup:
    """Test cases for database setup"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self.test_dir = tempfile.mkdtemp()

        yield

        shutil.rmtree(self.test_dir, ignore_errors=True)
        DatabaseSetup._reset_database()

    def _create_minimal_database(self):
        """Helper function to create and initialise a database"""
        TestBase = declarative_base()

        class TestTableOne(TestBase):
            __tablename__ = "test_table_one"
            id: Mapped[int] = mapped_column(Integer, primary_key=True)

        class TestTableTwo(TestBase):
            __tablename__ = "test_table_two"
            id: Mapped[int] = mapped_column(Integer, primary_key=True)

        file_path = Path(self.test_dir) / "test_vault.db"
        DatabaseSetup.init_db(file_path, TestBase)

    def test_init_db_function_takes_correct_parameters(self):
        """Should take directory and Database Base"""
        self._create_minimal_database()

    def test_init_db_creates_directory(self):
        """Should create a directory if one does not exist"""
        self._create_minimal_database()

        directory = Path(self.test_dir)
        assert directory.exists()

    def test_init_db_creates_database_file(self):
        """Should create database file if none exists"""
        self._create_minimal_database()

        file_path = Path(self.test_dir) / "test_vault.db"
        assert file_path.exists()

    def test_init_db_fails_if_already_called_once(self):
        """Should fail if init_db has already been called once"""
        self._create_minimal_database()

        new_test_dir = tempfile.mkdtemp()
        NewTestBase = declarative_base()
        new_directory = Path(new_test_dir)
        new_file_path = new_directory / "new_test_vault.db"

        try:
            DatabaseSetup.init_db(new_file_path, NewTestBase)
            raise AssertionError("Expected already initialised violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert "database already initialised" in error_message, f"Expected 'database already initialised' error, got: {error_message}"
        finally:
            shutil.rmtree(new_test_dir, ignore_errors=True)

    def test_get_session_before_init(self):
        """Should fail if init_db had not been called"""
        try:
            DatabaseSetup.get_session()
            raise AssertionError("Expected already initialised violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert "database not initialised" in error_message, f"Expected 'database not initialised' error, got: {error_message}"

    def test_get_session_after_init(self):
        """Should get session maker after doing init"""
        self._create_minimal_database()
        session = DatabaseSetup.get_session()
        assert isinstance(session, sessionmaker)

    def test_sessionmaker_has_expected_tables(self):
        """Should create tables from Base and bind them to the sessionmaker"""
        self._create_minimal_database()
        session_maker = DatabaseSetup.get_session()
        session = session_maker()
        inspector = inspect(session.bind)

        assert session is not None
        assert inspector is not None

        tables = inspector.get_table_names()
        assert "test_table_one" in tables
        assert "test_table_two" in tables


if __name__ == '__main__':
    pytest.main(['-v', __file__])
