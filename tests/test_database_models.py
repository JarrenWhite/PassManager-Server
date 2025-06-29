import os
import sys
import unittest
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_models import Base, User, LoginSession, SecureData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestDatabaseModels(unittest.TestCase):
    """Test cases for database models."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        
        # Create a session factory
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def tearDown(self):
        """Clean up after each test method."""
        self.session.close()
        Base.metadata.drop_all(self.engine)
    
    def test_user_creation(self):
        """Test creating a User instance."""
        # Create a test user
        test_user = User(
            username="testuser",
            password_hash="hashed_password_123"
        )
        
        # Add to session and commit
        self.session.add(test_user)
        self.session.commit()
        
        # Verify the user was created with an ID
        self.assertIsNotNone(test_user.id)
        self.assertIsInstance(test_user.id, int)
        
        # Verify the user data is correct
        self.assertEqual(test_user.username, "testuser")
        self.assertEqual(test_user.password_hash, "hashed_password_123")
        
        # Query the user from database to ensure it was saved
        retrieved_user = self.session.query(User).filter_by(username="testuser").first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.id, test_user.id)
        self.assertEqual(retrieved_user.username, test_user.username)
        self.assertEqual(retrieved_user.password_hash, test_user.password_hash)
    
    def test_user_username_uniqueness(self):
        """Test that usernames must be unique."""
        # Create & commit test user
        test_user_1 = User(
            username="testuser",
            password_hash="hashed_password_123"
        )
        self.session.add(test_user_1)
        self.session.commit()

        # Create second test user with same username
        test_user_2 = User(
            username="testuser",
            password_hash="different_password_123"
        )
        self.session.add(test_user_2)
        
        # Attempt to commit
        try:
            self.session.commit()
            self.fail("Expected uniqueness constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            self.assertTrue(
                "unique constraint failed" in error_message or "integrity" in error_message,
                f"Expected uniqueness constraint violation, got: {error_message}"
            )
            self.session.rollback()
        
        # Verify only the first user exists in the database
        users = self.session.query(User).filter_by(username="testuser").all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].id, test_user_1.id)
    
    def test_user_required_fields(self):
        """Test that required fields cannot be null."""
        # Create user without username
        test_user_no_username = User(
            username=None,
            password_hash="hashed_password_123"
        )
        self.session.add(test_user_no_username)

        # Attempt to commit
        try:
            self.session.commit()
            self.fail("Expected NOT NULL constraint violation for username but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            self.assertTrue(
                "not null" in error_message or "null constraint" in error_message or "integrity" in error_message,
                f"Expected NOT NULL constraint violation, got: {error_message}"
            )
            self.session.rollback()

        # Create user without password
        test_user_no_password = User(
            username="testuser",
            password_hash=None
        )
        self.session.add(test_user_no_password)

        # Attempt to commit
        try:
            self.session.commit()
            self.fail("Expected NOT NULL constraint violation for password_hash but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            self.assertTrue(
                "not null" in error_message or "null constraint" in error_message or "integrity" in error_message,
                f"Expected NOT NULL constraint violation, got: {error_message}"
            )
            self.session.rollback()
        
        # Verify no users were saved to the database
        all_users = self.session.query(User).all()
        self.assertEqual(len(all_users), 0)
    
    def test_login_session_creation(self):
        """Test creating a LoginSession instance."""
        # TODO: Implement test for LoginSession creation
        pass
    
    def test_login_session_foreign_key_constraint(self):
        """Test that LoginSession requires a valid user_id."""
        # TODO: Implement test for foreign key constraint
        pass
    
    def test_login_session_expiry_field(self):
        """Test that expiry field accepts datetime values."""
        # TODO: Implement test for expiry datetime field
        pass
    
    def test_secure_data_creation(self):
        """Test creating a SecureData instance."""
        # TODO: Implement test for SecureData creation
        pass
    
    def test_secure_data_foreign_key_constraint(self):
        """Test that SecureData requires a valid user_id."""
        # TODO: Implement test for foreign key constraint
        pass
    
    def test_secure_data_optional_fields(self):
        """Test that SecureData optional fields can be null."""
        # TODO: Implement test for optional fields
        pass
    
    def test_user_login_session_relationship(self):
        """Test the relationship between User and LoginSession."""
        # TODO: Implement test for User-LoginSession relationship
        pass
    
    def test_user_secure_data_relationship(self):
        """Test the relationship between User and SecureData."""
        # TODO: Implement test for User-SecureData relationship
        pass
    
    def test_cascade_delete_behavior(self):
        """Test cascade delete behavior when a user is deleted."""
        # TODO: Implement test for cascade delete behavior
        pass


if __name__ == '__main__':
    unittest.main() 
