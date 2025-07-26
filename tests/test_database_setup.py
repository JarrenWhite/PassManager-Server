import os
import sys
import shutil
import tempfile
import pytest
import time
import gc

from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_setup import init_db, _get_db_filename, _get_db_url, _get_engine, get_session_local, reset_engine


class TestDatabaseSetup:
    """Test cases for database setup"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up test fixtures before each test method."""
        # Store original environment variable if it exists
        self.original_vault_path = os.environ.get("VAULT_PATH")

        # Create a temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, "test_vault.db")
        os.environ["VAULT_PATH"] = self.test_db_path

        # Track resources for cleanup
        self.engines_to_dispose = []
        self.sessions_to_close = []

        yield

        for session in self.sessions_to_close:
            try:
                session.close()
            except Exception as e:
                raise AssertionError(f"Failed to close session during cleanup: {e}")

        for engine in self.engines_to_dispose:
            try:
                engine.dispose()
            except Exception as e:
                raise AssertionError(f"Failed to dispose engine during cleanup: {e}")

        try:
            reset_engine()
        except Exception:
            pass

        # Force garbage collection
        gc.collect()
        self._safe_remove_database()

        # Clean up the test directory
        try:
            shutil.rmtree(self.test_dir, ignore_errors=True)
        except Exception as e:
            raise AssertionError(f"Failed to remove test database file during cleanup: {e}")

        # Restore original environment variable
        if self.original_vault_path is not None:
            os.environ["VAULT_PATH"] = self.original_vault_path
        elif "VAULT_PATH" in os.environ:
            del os.environ["VAULT_PATH"]

    def _safe_remove_database(self):
        """Safely remove database file with retry logic for Windows"""
        if not os.path.exists(self.test_db_path):
            return

        # Try up to 5 times with increasing delays
        for attempt in range(5):
            try:
                os.remove(self.test_db_path)
                return
            except (OSError, PermissionError) as e:
                if attempt == 4:
                    raise AssertionError(f"Warning: Could not remove test database file: {e}")
                time.sleep(0.1 * (attempt + 1))

    def test_get_db_filename_with_env_var(self):
        """Test get_db_filename when VAULT_PATH is set"""

        result = _get_db_filename()
        assert result == self.test_db_path

    def test_get_db_filename_without_env_var(self):
        """Test get_db_filename when VAULT_PATH is not set"""

        if "VAULT_PATH" in os.environ:
            del os.environ["VAULT_PATH"]

        result = _get_db_filename()
        assert result == "data/vault.db"

    def test_get_db_url(self):
        """Test get_db_url returns correct SQLite URL"""

        result = _get_db_url()
        expected_url = f"sqlite:///{self.test_db_path}"
        assert result == expected_url

    def test_get_engine(self):
        """Test get_engine creates a valid engine"""
        from sqlalchemy import Engine

        engine = _get_engine()

        assert isinstance(engine, Engine)
        assert engine.url.database == self.test_db_path

    def test_get_session_local(self):
        """Test get_session_local creates a valid session factory"""
        from sqlalchemy.orm import sessionmaker

        session_factory = get_session_local()
        assert isinstance(session_factory, sessionmaker)

    def test_init_db_creates_new_database(self):
        """Test init_db creates a new database when none exists"""
        # Ensure database doesn't exist
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

        # Test that database doesn't exist initially
        assert not os.path.exists(self.test_db_path)

        # Call init_db
        init_db()

        # Verify database file was created
        assert os.path.exists(self.test_db_path)

    def test_init_db_with_existing_database(self):
        """Test init_db does nothing when database already exists"""
        # Create database first
        init_db()

        # Get file modification time
        stat_before = os.stat(self.test_db_path)

        # Call init_db again
        init_db()

        # Get file modification time after
        stat_after = os.stat(self.test_db_path)

        # File modification time should be the same (no changes)
        assert stat_before.st_mtime == stat_after.st_mtime

    def test_init_db_creates_parent_directory(self):
        """Test init_db creates parent directory when it doesn't exist"""
        # Set up a path with a non-existent parent directory
        deep_test_path = os.path.join(self.test_dir, "nonexistent", "subdir", "test_vault.db")
        os.environ["VAULT_PATH"] = deep_test_path

        # Ensure the directory doesn't exist
        parent_dir = os.path.dirname(deep_test_path)
        if os.path.exists(parent_dir):
            shutil.rmtree(parent_dir)

        # Test that parent directory doesn't exist initially
        assert not os.path.exists(parent_dir)

        # Call init_db
        init_db()

        # Verify parent directory and database file were created
        assert os.path.exists(parent_dir)
        assert os.path.exists(deep_test_path)

    def test_database_schema_creation(self):
        """Test that init_db creates all expected tables"""
        init_db()

        engine = _get_engine()
        self.engines_to_dispose.append(engine)

        # Check that all tables exist
        expected_tables = ['user', 'session', 'encrypted']
        with engine.connect() as connection:
            actual_tables = engine.dialect.get_table_names(connection)

            for table in expected_tables:
                assert table in actual_tables

    def test_reset_engine_resets_session_factory(self):
        """Test that reset_engine also resets the session factory"""
        # Get initial session factory
        session_factory1 = get_session_local()
        assert isinstance(session_factory1, sessionmaker)

        # Reset engines
        reset_engine()

        # Get new session factory
        session_factory2 = get_session_local()

        # Should be different objects
        assert session_factory1 is not session_factory2
        assert isinstance(session_factory2, sessionmaker)


if __name__ == '__main__':
    pytest.main(['-v', __file__])
