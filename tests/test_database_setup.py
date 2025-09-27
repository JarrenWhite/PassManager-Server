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

        self.TestBase = TestBase
        self.TestTableOne = TestTableOne
        self.TestTableTwo = TestTableTwo

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

        with pytest.raises(RuntimeError) as exc_info:
            DatabaseSetup.init_db(new_file_path, NewTestBase)
        error_message = str(exc_info.value).lower()
        assert "database already initialised" in error_message

        shutil.rmtree(new_test_dir, ignore_errors=True)

    def test_get_session_before_init(self):
        """Should fail if init_db had not been called"""
        with pytest.raises(RuntimeError) as exc_info:
            DatabaseSetup.get_session()
        error_message = str(exc_info.value).lower()
        assert "database not initialised" in error_message

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

    def test_session_make_links_to_same_sessions(self):
        """Should be able to see consistent data in sessions between sessions"""
        self._create_minimal_database()
        session_maker = DatabaseSetup.get_session()

        session1 = session_maker()
        row1 = session1.query(self.TestTableOne).all()
        assert row1 == []

        # Make record & add to session
        record = self.TestTableOne()
        session1.add(record)
        session1.commit()
        record_id = record.id
        session1.close()

        # Check exists on new session from same session maker
        session2 = session_maker()
        same_record = session2.query(self.TestTableOne).filter_by(id=record_id).one()
        assert same_record.id == record_id
        session2.close()

        # Check exists on new session from new session maker
        session_maker2 = DatabaseSetup.get_session()
        session3 = session_maker2()
        same_record = session3.query(self.TestTableOne).filter_by(id=record_id).one()
        assert same_record.id == record_id
        session3.close()

    def test_persistence_across_restarts(self):
        """Should have persistent data even when a new engine is created"""
        self._create_minimal_database()
        session_maker = DatabaseSetup.get_session()

        # Make record & add to session
        session1 = session_maker()
        record = self.TestTableOne()
        session1.add(record)
        session1.commit()
        record_id = record.id
        session1.close()

        # Simulate restart
        DatabaseSetup._reset_database()
        file_path = Path(self.test_dir) / "test_vault.db"
        DatabaseSetup.init_db(file_path, self.TestBase)
        new_session_maker = DatabaseSetup.get_session()

        # Check exists on new session from new session maker from new engine
        session2 = new_session_maker()
        same_record = session2.query(self.TestTableOne).filter_by(id=record_id).one()
        assert same_record.id == record_id
        session2.close()


class TestDatabaseSetupUnitTests:
    """Further unit tests for database setup"""

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

        self.TestBase = TestBase
        self.TestTableOne = TestTableOne
        self.TestTableTwo = TestTableTwo

        file_path = Path(self.test_dir) / "test_vault.db"
        DatabaseSetup.init_db(file_path, TestBase)


if __name__ == '__main__':
    pytest.main(['-v', __file__])
