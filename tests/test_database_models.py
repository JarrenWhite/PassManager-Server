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
        retrieved_user = self.session.query(User).filter_by(id=test_user.id).first()
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
        # Create a test user for the login session
        test_user = User(
            username="testuser",
            password_hash="hashed_password_123"
        )
        self.session.add(test_user)
        self.session.commit()

        # Create login session
        expiry = datetime.now() + timedelta(hours=1)
        test_login_session = LoginSession(
            user_id=test_user.id,
            token="test_token_123",
            expiry=expiry
        )
        self.session.add(test_login_session)
        self.session.commit()

        # Verify login session was created with an ID
        self.assertIsNotNone(test_login_session.id)
        self.assertIsInstance(test_login_session.id, int)

        # Verify the login session data is correct
        self.assertEqual(test_login_session.user_id, test_user.id)
        self.assertEqual(test_login_session.token, "test_token_123")
        self.assertEqual(test_login_session.expiry, expiry)

        # Query the login session from database to ensure it was saved
        retrieved_login_session = self.session.query(LoginSession).filter_by(id=test_login_session.id).first()
        self.assertIsNotNone(retrieved_login_session)
        self.assertEqual(retrieved_login_session.id, test_login_session.id)
        self.assertEqual(retrieved_login_session.user_id, test_login_session.user_id)
        self.assertEqual(retrieved_login_session.token, test_login_session.token)
        self.assertEqual(retrieved_login_session.expiry, test_login_session.expiry)
    
    def test_login_session_required_fields(self):
        """Test that required fields cannot be null."""
        # Create a test user for the login session
        test_user = User(
            username="testuser",
            password_hash="hashed_password_123"
        )
        self.session.add(test_user)
        self.session.commit()

        # Create login session without user_id
        expiry = datetime.now() + timedelta(hours=1)
        test_session_no_user_id = LoginSession(
            user_id=None,
            token="test_token_123",
            expiry=expiry
        )
        self.session.add(test_session_no_user_id)

        # Attempt to commit
        try:
            self.session.commit()
            self.fail("Expected NOT NULL constraint violation for user_id but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            self.assertTrue(
                "not null" in error_message or "null constraint" in error_message or "integrity" in error_message,
                f"Expected NOT NULL constraint violation, got: {error_message}"
            )
            self.session.rollback()

        # Create login session without token
        test_session_no_token = LoginSession(
            user_id=test_user.id,
            token=None,
            expiry=expiry
        )
        self.session.add(test_session_no_token)

        # Attempt to commit
        try:
            self.session.commit()
            self.fail("Expected NOT NULL constraint violation for token but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            self.assertTrue(
                "not null" in error_message or "null constraint" in error_message or "integrity" in error_message,
                f"Expected NOT NULL constraint violation, got: {error_message}"
            )
            self.session.rollback()

        # Create login session without expiry
        test_session_no_expiry = LoginSession(
            user_id=test_user.id,
            token="test_token_123",
            expiry=None
        )
        self.session.add(test_session_no_expiry)

        # Attempt to commit
        try:
            self.session.commit()
            self.fail("Expected NOT NULL constraint violation for expiry but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            self.assertTrue(
                "not null" in error_message or "null constraint" in error_message or "integrity" in error_message,
                f"Expected NOT NULL constraint violation, got: {error_message}"
            )
            self.session.rollback()
        
        # Verify no login sessions were saved to the database
        all_login_sessions = self.session.query(LoginSession).all()
        self.assertEqual(len(all_login_sessions), 0)
    
    def test_secure_data_creation(self):
        """Test creating a SecureData instance."""
        # Create a test user for the secure data
        test_user = User(
            username="testuser",
            password_hash="hashed_password_123"
        )
        self.session.add(test_user)
        self.session.commit()

        # Create secure data
        test_secure_data = SecureData(
            user_id=test_user.id,
            entry_name="test_stored_password_title",
            website="test_encrypted_website",
            username="test_encrypted_username",
            password="test_encrypted_password",
            notes="test_encrypted_notes"
        )
        self.session.add(test_secure_data)
        self.session.commit()

        # Verify secure data was created with an ID
        self.assertIsNotNone(test_secure_data.id)
        self.assertIsInstance(test_secure_data.id, int)

        # Verify the secure data data is correct
        self.assertEqual(test_secure_data.user_id, test_user.id)
        self.assertEqual(test_secure_data.entry_name, "test_stored_password_title")
        self.assertEqual(test_secure_data.website, "test_encrypted_website")
        self.assertEqual(test_secure_data.username, "test_encrypted_username")
        self.assertEqual(test_secure_data.password, "test_encrypted_password")
        self.assertEqual(test_secure_data.notes, "test_encrypted_notes")

        # Query the secure data from database to ensure it was saved
        retrieved_secure_data = self.session.query(SecureData).filter_by(id=test_secure_data.id).first()
        self.assertIsNotNone(retrieved_secure_data)
        self.assertEqual(retrieved_secure_data.user_id, test_secure_data.id)
        self.assertEqual(retrieved_secure_data.entry_name, test_secure_data.entry_name)
        self.assertEqual(retrieved_secure_data.website, test_secure_data.website)
        self.assertEqual(retrieved_secure_data.username, test_secure_data.username)
        self.assertEqual(retrieved_secure_data.password, test_secure_data.password)
        self.assertEqual(retrieved_secure_data.notes, test_secure_data.notes)
    
    def test_secure_data_required_fields(self):
        """Test that required fields cannot be null."""
        # Create a test user for foreign key reference
        test_user = User(
            username="testuser",
            password_hash="hashed_password_123"
        )
        self.session.add(test_user)
        self.session.commit()

        # Create secure data without user_id
        test_secure_data_no_user_id = SecureData(
            user_id=None,
            entry_name="test_stored_password_title",
            website="test_encrypted_website",
            username="test_encrypted_username",
            password="test_encrypted_password",
            notes="test_encrypted_notes"
        )
        self.session.add(test_secure_data_no_user_id)

        # Attempt to commit
        try:
            self.session.commit()
            self.fail("Expected NOT NULL constraint violation for user_id but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            self.assertTrue(
                "not null" in error_message or "null constraint" in error_message or "integrity" in error_message,
                f"Expected NOT NULL constraint violation, got: {error_message}"
            )
            self.session.rollback()
        
        # Verify no secure data was saved to the database
        all_secure_data = self.session.query(SecureData).all()
        self.assertEqual(len(all_secure_data), 0)
    
    def test_secure_data_optional_fields(self):
        """Test that optional fields can be null."""
        # Create a test user for foreign key reference
        test_user = User(
            username="testuser",
            password_hash="hashed_password_123"
        )
        self.session.add(test_user)
        self.session.commit()

        # Create secure data with all optional fields as null
        test_secure_data_all_null = SecureData(
            user_id=test_user.id,
            entry_name=None,
            website=None,
            username=None,
            password=None,
            notes=None
        )
        self.session.add(test_secure_data_all_null)
        self.session.commit()

        # Verify secure data was created with an ID
        self.assertIsNotNone(test_secure_data_all_null.id)
        self.assertIsInstance(test_secure_data_all_null.id, int)

        # Verify the secure data has null values for optional fields
        self.assertEqual(test_secure_data_all_null.user_id, test_user.id)
        self.assertIsNone(test_secure_data_all_null.entry_name)
        self.assertIsNone(test_secure_data_all_null.website)
        self.assertIsNone(test_secure_data_all_null.username)
        self.assertIsNone(test_secure_data_all_null.password)
        self.assertIsNone(test_secure_data_all_null.notes)

        # Query the secure data from database to ensure it was saved
        retrieved_secure_data = self.session.query(SecureData).filter_by(id=test_secure_data_all_null.id).first()
        self.assertIsNotNone(retrieved_secure_data)
        self.assertEqual(retrieved_secure_data.user_id, test_secure_data_all_null.user_id)
        self.assertIsNone(retrieved_secure_data.entry_name)
        self.assertIsNone(retrieved_secure_data.website)
        self.assertIsNone(retrieved_secure_data.username)
        self.assertIsNone(retrieved_secure_data.password)
        self.assertIsNone(retrieved_secure_data.notes)

        # Create secure data with some optional fields filled and some null
        test_secure_data_mixed = SecureData(
            user_id=test_user.id,
            entry_name="test_entry",
            website=None,
            username="test_user",
            password=None,
            notes="test_notes"
        )
        self.session.add(test_secure_data_mixed)
        self.session.commit()

        # Verify mixed null/non-null values are handled correctly
        self.assertIsNotNone(test_secure_data_mixed.id)
        self.assertEqual(test_secure_data_mixed.entry_name, "test_entry")
        self.assertIsNone(test_secure_data_mixed.website)
        self.assertEqual(test_secure_data_mixed.username, "test_user")
        self.assertIsNone(test_secure_data_mixed.password)
        self.assertEqual(test_secure_data_mixed.notes, "test_notes")
    
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
