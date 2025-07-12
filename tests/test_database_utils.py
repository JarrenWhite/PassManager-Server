import os
import sys
import pytest
import tempfile
import shutil
import time
import gc

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database_utils import DatabaseUtils
from database.database_setup import reset_engine
from sqlalchemy import text


class TestDatabaseUtils:
    """Test cases for database utils."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up test fixtures before each test method."""
        # Store original environment variable if it exists
        self.original_vault_path = os.environ.get("VAULT_PATH")

        # Create a temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, "test_vault.db")
        os.environ["VAULT_PATH"] = self.test_db_path

        # Reset engine and initialize database
        reset_engine()
        DatabaseUtils.init_database()

        yield

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
                    raise AssertionError(f"Could not remove test database file: {e}")
                    return
                time.sleep(0.1 * (attempt + 1))

    def test_db_session_creation(self):
        """Test that get_db_session opens and closes a session"""
        pass

    def test_database_initilaisation(self):
        """Test that the database initialises correctly the first time"""
        pass

    def test_failed_database_initialisation(self):
        """Test that databse initialisation fails if it's already been run"""
        pass

    def test_shared_database_initialiastion(self):
        """Test that multiple instances of Database share database_initialised"""
        pass

    def test_create_user(self):
        """Test user creation"""
        pass

    def test_delete_user(self):
        """Test user deletion"""
        pass

    def test_create_session(self):
        """Test session creation"""
        pass

    def test__delete_session(self):
        """Test single session deletion"""
        pass

    def test_delete_all_sessions(self):
        """Test deleting all of a user's sessions"""
        pass

    def test_session_cleaning(self):
        """Test that expired sessions are removed during cleaning"""
        pass

    def test_create_secure_data(self):
        """Test secure data creation"""
        pass

    def test_edit_secure_data(self):
        """Test secure data editing"""
        pass

    def test_delete_secure_data(self):
        """Test secure data deletion"""
        pass

    def test_all_secure_data_is_revealed(self):
        """Test that secure data appears for a user"""
        pass

    def test_shared_database_details(self):
        """Test that an update made in one instance of utils is seen in another"""
        pass
