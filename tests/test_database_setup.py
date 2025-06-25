import os
import tempfile
import shutil
import unittest
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker

# Import the modules to test
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_setup import (
    Base, User, Session, PasswordItem, Encrypted, 
    init_db, get_db_filename, get_db_url, get_engine
)


class TestDatabaseSetup(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        
        # Set up test database path
        self.test_db_path = os.path.join(self.test_dir, "test_vault.db")
        os.environ["VAULT_PATH"] = self.test_db_path
        
        # Get the db filename and url
        self.original_db_filename = get_db_filename()
        self.original_db_url = get_db_url()
        
        # Create test engine and session
        self.test_engine = get_engine()
        self.TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.test_engine)
        
        # Create tables
        Base.metadata.create_all(self.test_engine)
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove test database and directory
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
        # Restore original environment
        if "VAULT_PATH" in os.environ:
            del os.environ["VAULT_PATH"]
    
    def test_user_model(self):
        """Test User model creation and attributes."""
        session = self.TestSessionLocal()
        
        # Create a test user
        user = User(username="testuser", password_hash="hashed_password_123")
        session.add(user)
        session.commit()
        
        # Verify user was created
        retrieved_user = session.query(User).filter_by(username="testuser").first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.username, "testuser")
        self.assertEqual(retrieved_user.password_hash, "hashed_password_123")
        self.assertIsInstance(retrieved_user.id, int)
        
        session.close()
    
    def test_user_unique_constraint(self):
        """Test that username must be unique."""
        session = self.TestSessionLocal()
        
        # Create first user
        user1 = User(username="testuser", password_hash="hash1")
        session.add(user1)
        session.commit()
        
        # Try to create second user with same username
        user2 = User(username="testuser", password_hash="hash2")
        session.add(user2)
        
        with self.assertRaises(Exception):  # SQLAlchemy will raise an integrity error
            session.commit()
        
        session.rollback()
        session.close()
    
    def test_session_model(self):
        """Test Session model creation and attributes."""
        session = self.TestSessionLocal()
        
        # Create a test user first
        user = User(username="testuser", password_hash="hash")
        session.add(user)
        session.commit()
        
        # Create a session
        expiry = datetime.now() + timedelta(hours=1)
        user_session = Session(
            user_id=user.id,
            token="test_token_123",
            expiry=expiry
        )
        session.add(user_session)
        session.commit()
        
        # Verify session was created
        retrieved_session = session.query(Session).filter_by(token="test_token_123").first()
        self.assertIsNotNone(retrieved_session)
        self.assertEqual(retrieved_session.user_id, user.id)
        self.assertEqual(retrieved_session.token, "test_token_123")
        self.assertEqual(retrieved_session.expiry, expiry)
        
        session.close()
    
    def test_password_item_model(self):
        """Test PasswordItem model creation and attributes."""
        session = self.TestSessionLocal()
        
        # Create a test user first
        user = User(username="testuser", password_hash="hash")
        session.add(user)
        session.commit()
        
        # Create a password item
        password_item = PasswordItem(
            user_id=user.id,
            encrypted_id=1,
            entry_name="Test Entry",
            website="https://example.com"
        )
        session.add(password_item)
        session.commit()
        
        # Verify password item was created
        retrieved_item = session.query(PasswordItem).filter_by(entry_name="Test Entry").first()
        self.assertIsNotNone(retrieved_item)
        self.assertEqual(retrieved_item.user_id, user.id)
        self.assertEqual(retrieved_item.encrypted_id, 1)
        self.assertEqual(retrieved_item.entry_name, "Test Entry")
        self.assertEqual(retrieved_item.website, "https://example.com")
        
        session.close()
    
    def test_encrypted_model(self):
        """Test Encrypted model creation and attributes."""
        session = self.TestSessionLocal()
        
        # Create an encrypted entry
        encrypted = Encrypted(
            username="test_username",
            password="encrypted_password_data",
            notes="Test notes"
        )
        session.add(encrypted)
        session.commit()
        
        # Verify encrypted entry was created
        retrieved_encrypted = session.query(Encrypted).filter_by(username="test_username").first()
        self.assertIsNotNone(retrieved_encrypted)
        self.assertEqual(retrieved_encrypted.username, "test_username")
        self.assertEqual(retrieved_encrypted.password, "encrypted_password_data")
        self.assertEqual(retrieved_encrypted.notes, "Test notes")
        
        session.close()
    
    def test_foreign_key_relationships(self):
        """Test foreign key relationships between tables."""
        session = self.TestSessionLocal()
        
        # Create a user
        user = User(username="testuser", password_hash="hash")
        session.add(user)
        session.commit()
        
        # Create a session for the user
        expiry = datetime.now() + timedelta(hours=1)
        user_session = Session(user_id=user.id, token="token", expiry=expiry)
        session.add(user_session)
        
        # Create a password item for the user
        password_item = PasswordItem(
            user_id=user.id,
            encrypted_id=1,
            entry_name="Test",
            website="https://example.com"
        )
        session.add(password_item)
        session.commit()
        
        # Verify relationships work
        user_sessions = session.query(Session).filter_by(user_id=user.id).all()
        self.assertEqual(len(user_sessions), 1)
        
        user_password_items = session.query(PasswordItem).filter_by(user_id=user.id).all()
        self.assertEqual(len(user_password_items), 1)
        
        session.close()
    
    def test_init_db_creates_database(self):
        """Test that init_db creates database when it doesn't exist."""
        # Create a temporary directory for this test
        temp_dir = tempfile.mkdtemp()
        temp_data_dir = os.path.join(temp_dir, "data")
        temp_db_path = os.path.join(temp_data_dir, "vault.db")
        
        try:
            # Set up environment for this test
            original_vault_path = os.environ.get("VAULT_PATH")
            os.environ["VAULT_PATH"] = temp_db_path
            
            # Remove test database if it exists
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
            
            # Call init_db
            init_db()
            
            # Verify database was created
            self.assertTrue(os.path.exists(temp_db_path))
            
            # Verify tables were created by trying to query them
            test_engine = get_engine()
            test_session = sessionmaker(bind=test_engine)()
            
            # Try to query each table to ensure they exist
            users = test_session.query(User).all()
            sessions = test_session.query(Session).all()
            password_items = test_session.query(PasswordItem).all()
            encrypted_items = test_session.query(Encrypted).all()
            
            # If no exception was raised, tables exist
            self.assertIsInstance(users, list)
            self.assertIsInstance(sessions, list)
            self.assertIsInstance(password_items, list)
            self.assertIsInstance(encrypted_items, list)
            
            test_session.close()
            
        finally:
            # Clean up
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Restore original environment
            if original_vault_path:
                os.environ["VAULT_PATH"] = original_vault_path
            elif "VAULT_PATH" in os.environ:
                del os.environ["VAULT_PATH"]
    
    def test_init_db_does_not_recreate_existing_database(self):
        """Test that init_db doesn't recreate existing database."""
        # Create a temporary directory for this test
        temp_dir = tempfile.mkdtemp()
        temp_data_dir = os.path.join(temp_dir, "data")
        temp_db_path = os.path.join(temp_data_dir, "vault.db")
        
        try:
            # Set up environment for this test
            original_vault_path = os.environ.get("VAULT_PATH")
            os.environ["VAULT_PATH"] = temp_db_path
            
            # Ensure database exists
            init_db()
            original_size = os.path.getsize(temp_db_path)
            
            # Call init_db again
            init_db()
            new_size = os.path.getsize(temp_db_path)
            
            # Size should be the same (no recreation)
            self.assertEqual(original_size, new_size)
            
        finally:
            # Clean up
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Restore original environment
            if original_vault_path:
                os.environ["VAULT_PATH"] = original_vault_path
            elif "VAULT_PATH" in os.environ:
                del os.environ["VAULT_PATH"]
    
    def test_environment_variable_db_path(self):
        """Test that VAULT_PATH environment variable is respected."""
        custom_path = os.path.join(self.test_dir, "custom_vault.db")
        os.environ["VAULT_PATH"] = custom_path
        
        self.assertEqual(get_db_filename(), custom_path)
    
    def test_default_db_path(self):
        """Test default database path when VAULT_PATH is not set."""
        if "VAULT_PATH" in os.environ:
            del os.environ["VAULT_PATH"]
        
        self.assertEqual(get_db_filename(), "data/vault.db")


class TestDatabaseModelsConstraints(unittest.TestCase):
    """Test cases for database model constraints and edge cases."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, "test_vault.db")
        os.environ["VAULT_PATH"] = self.test_db_path
        
        self.test_engine = get_engine()
        self.TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.test_engine)
        Base.metadata.create_all(self.test_engine)
    
    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        shutil.rmtree(self.test_dir, ignore_errors=True)
        if "VAULT_PATH" in os.environ:
            del os.environ["VAULT_PATH"]
    
    def test_user_nullable_constraints(self):
        """Test that User model nullable constraints are enforced."""
        session = self.TestSessionLocal()
        
        # Test User model - username should not be nullable
        with self.assertRaises(Exception):
            user = User(username=None, password_hash="hash")
            session.add(user)
            session.commit()
        session.rollback()
        
        # Test User model - password_hash should not be nullable
        with self.assertRaises(Exception):
            user = User(username="test", password_hash=None)
            session.add(user)
            session.commit()
        session.rollback()
        session.close()
    
    def test_session_nullable_constraints(self):
        """Test that Session model nullable constraints are enforced."""
        session = self.TestSessionLocal()
        
        # Create a user
        user = User(username="testuser", password_hash="hash")
        session.add(user)
        session.commit()
        
        # Test Session model - user_id should not be nullable
        with self.assertRaises(Exception):
            session_obj = Session(user_id=None, token="token", expiry=datetime.now())
            session.add(session_obj)
            session.commit()
        session.rollback()
        
        # Test Session model - token should not be nullable
        with self.assertRaises(Exception):
            session_obj = Session(user_id=user.id, token=None, expiry=datetime.now())
            session.add(session_obj)
            session.commit()
        session.rollback()
        
        # Test Session model - expiry should not be nullable
        with self.assertRaises(Exception):
            session_obj = Session(user_id=user.id, token="token", expiry=None)
            session.add(session_obj)
            session.commit()
        session.rollback()
        session.close()
    
    def test_password_item_nullable_constraints(self):
        """Test that PasswordItem model nullable constraints are enforced."""
        session = self.TestSessionLocal()
        
        # Create a user
        user = User(username="testuser", password_hash="hash")
        session.add(user)
        session.commit()
        
        # Test PasswordItem model - user_id should not be nullable
        with self.assertRaises(Exception):
            password_item = PasswordItem(user_id=None, encrypted_id=1, entry_name="Test", website="https://example.com")
            session.add(password_item)
            session.commit()
        
        session.rollback()
        
        # Test PasswordItem model - encrypted_id should not be nullable
        with self.assertRaises(Exception):
            password_item = PasswordItem(user_id=user.id, encrypted_id=None, entry_name="Test", website="https://example.com")
            session.add(password_item)
            session.commit()
        
        session.rollback()
        session.close()


if __name__ == "__main__":
    unittest.main(verbosity=2) 