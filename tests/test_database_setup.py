import os
import sys
import shutil
import tempfile
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_setup import init_db, get_db_filename, get_db_url, get_engine, get_session_local


class TestDatabaseSetup(unittest.TestCase):
    """Test cases for database setup"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Store original environment variable if it exists
        self.original_vault_path = os.environ.get("VAULT_PATH")
        
        # Create a temporary directory for test database
        self.test_dir = tempfile.mkdtemp()

        # Set up test database path
        self.test_db_path = os.path.join(self.test_dir, "test_vault.db")
        os.environ["VAULT_PATH"] = self.test_db_path

    def tearDown(self):
        """Clean up after each test method."""
        # Close the engine if it exists
        if hasattr(self, 'test_engine'):
            self.test_engine.dispose()
        
        # Remove test database and directory
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
        # Restore original environment variable
        if self.original_vault_path is not None:
            os.environ["VAULT_PATH"] = self.original_vault_path
        elif "VAULT_PATH" in os.environ:
            del os.environ["VAULT_PATH"]


if __name__ == '__main__':
    unittest.main() 
