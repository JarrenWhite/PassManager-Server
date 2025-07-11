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
