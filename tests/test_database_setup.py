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

    def test_get_db_filename_with_env_var(self):
        """Test get_db_filename when VAULT_PATH is set"""
        
        result = get_db_filename()
        self.assertEqual(result, self.test_db_path)

    def test_get_db_filename_without_env_var(self):
        """Test get_db_filename when VAULT_PATH is not set"""

        if "VAULT_PATH" in os.environ:
            del os.environ["VAULT_PATH"]

        result = get_db_filename()
        self.assertEqual(result, "data/vault.db")

    def test_get_db_url(self):
        """Test get_db_url returns correct SQLite URL"""

        result = get_db_url()
        expected_url = f"sqlite:///{self.test_db_path}"
        self.assertEqual(result, expected_url)

    def test_get_engine(self):
        """Test get_engine creates a valid engine"""
        from sqlalchemy import Engine
        
        result = get_engine()
        self.assertIsInstance(result, Engine)
        self.assertEqual(result.url.database, self.test_db_path)

    def test_get_session_local(self):
        """Test get_session_local creates a valid session factory"""
        from sqlalchemy.orm import sessionmaker
        
        result = get_session_local()
        self.assertIsInstance(result, sessionmaker)

    def test_init_db_creates_new_database(self):
        """Test init_db creates a new database when none exists"""
        # Ensure database doesn't exist
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        # Test that database doesn't exist initially
        self.assertFalse(os.path.exists(self.test_db_path))
        
        # Call init_db
        init_db()
        
        # Verify database file was created
        self.assertTrue(os.path.exists(self.test_db_path))

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
        self.assertEqual(stat_before.st_mtime, stat_after.st_mtime)

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
        self.assertFalse(os.path.exists(parent_dir))
        
        # Call init_db
        init_db()
        
        # Verify parent directory and database file were created
        self.assertTrue(os.path.exists(parent_dir))
        self.assertTrue(os.path.exists(deep_test_path))


if __name__ == '__main__':
    unittest.main() 
