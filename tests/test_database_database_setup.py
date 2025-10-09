import os
import sys
import pytest
import shutil
import tempfile
import platform
from pathlib import Path

from sqlalchemy.orm import declarative_base, Session, Mapped, mapped_column
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

    def test_get_db_session_before_init(self):
        """Should fail if init_db had not been called"""
        with pytest.raises(RuntimeError) as exc_info:
            with DatabaseSetup.get_db_session():
                pass
        error_message = str(exc_info.value).lower()
        assert "database not initialised" in error_message

    def test_get_db_session_after_init(self):
        """Should get a usable Session after doing init"""
        self._create_minimal_database()
        with DatabaseSetup.get_db_session() as session:
            assert isinstance(session, Session)

    def test_session_has_expected_tables(self):
        """Should create tables from Base and bind them to the engine"""
        self._create_minimal_database()
        with DatabaseSetup.get_db_session() as session:
            inspector = inspect(session.bind)

        assert session is not None
        assert inspector is not None

        tables = inspector.get_table_names()
        assert "test_table_one" in tables
        assert "test_table_two" in tables

    def test_consistent_data_between_sessions(self):
        """Should be able to see consistent data across sessions"""
        self._create_minimal_database()

        with DatabaseSetup.get_db_session() as session1:
            row1 = session1.query(self.TestTableOne).all()
            assert row1 == []

            # Make record & add to session
            record = self.TestTableOne()
            session1.add(record)
            session1.commit()
            record_id = record.id

        # Check exists on new session
        with DatabaseSetup.get_db_session() as session2:
            same_record = session2.query(self.TestTableOne).filter_by(id=record_id).one()
            assert same_record.id == record_id

        # Check exists on another new session
        with DatabaseSetup.get_db_session() as session3:
            same_record = session3.query(self.TestTableOne).filter_by(id=record_id).one()
            assert same_record.id == record_id

    def test_persistence_across_restarts(self):
        """Should have persistent data even when a new engine is created"""
        self._create_minimal_database()

        # Make record & add to session
        with DatabaseSetup.get_db_session() as session1:
            record = self.TestTableOne()
            session1.add(record)
            session1.commit()
            record_id = record.id

        # Simulate restart
        DatabaseSetup._reset_database()
        file_path = Path(self.test_dir) / "test_vault.db"
        DatabaseSetup.init_db(file_path, self.TestBase)

        # Check exists on new session from new engine
        with DatabaseSetup.get_db_session() as session2:
            same_record = session2.query(self.TestTableOne).filter_by(id=record_id).one()
            assert same_record.id == record_id


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

    def test_init_db_fails_if_target_file_exists_but_not_valid_sqlite(self):
        """Should raise exception if target file already exists but is not a valid sqlite file"""
        TestBase = declarative_base()

        class TestTable(TestBase):
            __tablename__ = "test_table"
            id: Mapped[int] = mapped_column(Integer, primary_key=True)

        file_path = Path(self.test_dir) / "invalid_db.db"
        with open(file_path, 'w') as f:
            f.write("This is not a valid SQLite database file content")

        with pytest.raises(Exception) as exc_info:
            DatabaseSetup.init_db(file_path, TestBase)

        error_message = str(exc_info.value).lower()
        assert "file is not a database" in error_message

    def test_init_db_fails_if_target_directory_not_writable(self):
        """Should raise exception if the target directory is not writable"""
        TestBase = declarative_base()

        class TestTable(TestBase):
            __tablename__ = "test_table"
            id: Mapped[int] = mapped_column(Integer, primary_key=True)

        # Windows
        if platform.system() == "Windows":
            file_path = Path("Z:\\non_existent\\path\\test_vault.db")

            with pytest.raises(Exception) as exc_info:
                DatabaseSetup.init_db(file_path, TestBase)

            error_message = str(exc_info.value).lower()
            assert "permission denied" in error_message

        # Linux / Mac
        else:
            readonly_dir = Path(self.test_dir) / "readonly_dir"
            readonly_dir.mkdir(parents=True, exist_ok=True)
            readonly_dir.chmod(0o444)

            try:
                file_path = readonly_dir / "test_vault.db"

                with pytest.raises(Exception) as exc_info:
                    DatabaseSetup.init_db(file_path, TestBase)

                error_message = str(exc_info.value).lower()
                assert "permission denied" in error_message

            finally:
                readonly_dir.chmod(0o755)

    def test_re_init_with_different_base(self):
        """Should raise exception when re-initialising with a different Base"""
        self._create_minimal_database()

        DatabaseSetup._reset_database()

        DifferentBase = declarative_base()

        class DifferentTable(DifferentBase):
            __tablename__ = "different_table"
            id: Mapped[int] = mapped_column(Integer, primary_key=True)

        file_path = Path(self.test_dir) / "test_vault.db"

        with pytest.raises(Exception) as exc_info:
            DatabaseSetup.init_db(file_path, DifferentBase)

        error_message = str(exc_info.value).lower()
        assert "schema mismatch" in error_message


if __name__ == '__main__':
    pytest.main(['-v', __file__])