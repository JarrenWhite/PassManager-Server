import os
import sys
import pytest
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_models import Base, User, LoginSession, SecureData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestDatabaseModels():
    """Test cases for database models."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up and tear down between each test method."""
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)

        # Create a session factory
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        yield

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
        assert test_user.id is not None
        assert isinstance(test_user.id, int)

        # Verify the user data is correct
        assert test_user.username == "testuser"
        assert test_user.password_hash == "hashed_password_123"

        # Query the user from database to ensure it was saved
        retrieved_user = self.session.query(User).filter_by(id=test_user.id).first()
        assert retrieved_user is not None
        assert retrieved_user.id == test_user.id
        assert retrieved_user.username == test_user.username
        assert retrieved_user.password_hash == test_user.password_hash

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
            assert ("unique constraint failed" in error_message or
                     "integrity" in error_message), f"Expected uniqueness constraint violation, got: {error_message}"
            self.session.rollback()

        # Verify only the first user exists in the database
        users = self.session.query(User).filter_by(username="testuser").all()
        assert len(users) == 1
        assert users[0].id == test_user_1.id

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
            assert ("not null" in error_message or
                     "null constraint" in error_message or
                     "integrity" in error_message), f"Expected NOT NULL constraint violation, got: {error_message}"
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
            assert ("not null" in error_message or
                     "null constraint" in error_message or
                       "integrity" in error_message), f"Expected NOT NULL constraint violation, got: {error_message}"
            self.session.rollback()

        # Verify no users were saved to the database
        all_users = self.session.query(User).all()
        assert len(all_users) == 0

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
        assert test_login_session.id is not None
        assert isinstance(test_login_session.id, int)

        # Verify the login session data is correct
        assert test_login_session.user_id == test_user.id
        assert test_login_session.token == "test_token_123"
        assert test_login_session.expiry == expiry

        # Query the login session from database to ensure it was saved
        retrieved_login_session = self.session.query(LoginSession).filter_by(id=test_login_session.id).first()
        assert retrieved_login_session is not None
        assert retrieved_login_session.id == test_login_session.id
        assert retrieved_login_session.user_id == test_login_session.user_id
        assert retrieved_login_session.token == test_login_session.token
        assert retrieved_login_session.expiry == test_login_session.expiry

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
            assert ("not null" in error_message or
                     "null constraint" in error_message or
                       "integrity" in error_message), f"Expected NOT NULL constraint violation, got: {error_message}"
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
            assert ("not null" in error_message or
                     "null constraint" in error_message or
                       "integrity" in error_message), f"Expected NOT NULL constraint violation, got: {error_message}"
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
            assert ("not null" in error_message or
                     "null constraint" in error_message or
                       "integrity" in error_message), f"Expected NOT NULL constraint violation, got: {error_message}"
            self.session.rollback()

        # Verify no login sessions were saved to the database
        all_login_sessions = self.session.query(LoginSession).all()
        assert len(all_login_sessions) == 0

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
        assert test_secure_data.id is not None
        assert isinstance(test_secure_data.id, int)

        # Verify the secure data data is correct
        assert test_secure_data.user_id == test_user.id
        assert test_secure_data.entry_name == "test_stored_password_title"
        assert test_secure_data.website == "test_encrypted_website"
        assert test_secure_data.username == "test_encrypted_username"
        assert test_secure_data.password == "test_encrypted_password"
        assert test_secure_data.notes == "test_encrypted_notes"

        # Query the secure data from database to ensure it was saved
        retrieved_secure_data = self.session.query(SecureData).filter_by(id=test_secure_data.id).first()
        assert retrieved_secure_data is not None
        assert retrieved_secure_data.user_id == test_user.id
        assert retrieved_secure_data.public_id == test_secure_data.public_id
        assert retrieved_secure_data.entry_name == test_secure_data.entry_name
        assert retrieved_secure_data.website == test_secure_data.website
        assert retrieved_secure_data.username == test_secure_data.username
        assert retrieved_secure_data.password == test_secure_data.password
        assert retrieved_secure_data.notes == test_secure_data.notes

    def test_secure_data_required_fields(self):
        """Test that required fields cannot be null."""
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
            assert ("not null" in error_message or
                     "null constraint" in error_message or
                       "integrity" in error_message), f"Expected NOT NULL constraint violation, got: {error_message}"
            self.session.rollback()

        # Verify no secure data was saved to the database
        all_secure_data = self.session.query(SecureData).all()
        assert len(all_secure_data) == 0

    def test_secure_data_optional_fields(self):
        """Test that optional fields can be null."""
        # Create a test user for the secure data
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
        assert test_secure_data_all_null.id
        assert isinstance(test_secure_data_all_null.id, int)

        # Verify the secure data has null values for optional fields
        assert test_secure_data_all_null.user_id == test_user.id
        assert test_secure_data_all_null.entry_name is None
        assert test_secure_data_all_null.website is None
        assert test_secure_data_all_null.username is None
        assert test_secure_data_all_null.password is None
        assert test_secure_data_all_null.notes is None

        # Query the secure data from database to ensure it was saved
        retrieved_secure_data = self.session.query(SecureData).filter_by(id=test_secure_data_all_null.id).first()
        assert retrieved_secure_data is not None
        assert retrieved_secure_data.user_id == test_secure_data_all_null.user_id
        assert retrieved_secure_data.entry_name is None
        assert retrieved_secure_data.website is None
        assert retrieved_secure_data.username is None
        assert retrieved_secure_data.password is None
        assert retrieved_secure_data.notes is None

        # Create secure data with some optional fields filled and some null
        test_secure_data_mixed = SecureData(
            user_id=test_user.id,
            entry_name="test_stored_password_title",
            website=None,
            username="test_encrypted_username",
            password=None,
            notes="test_encrypted_notes"
        )
        self.session.add(test_secure_data_mixed)
        self.session.commit()

        # Verify mixed null/non-null values are handled correctly
        assert test_secure_data_mixed.id is not None
        assert test_secure_data_mixed.entry_name == "test_stored_password_title"
        assert test_secure_data_mixed.website is None
        assert test_secure_data_mixed.username == "test_encrypted_username"
        assert test_secure_data_mixed.password is None
        assert test_secure_data_mixed.notes == "test_encrypted_notes"

    def test_user_login_session_relationship(self):
        """Test the relationship between User and LoginSession."""
        # Create a test user
        test_user = User(
            username="testuser",
            password_hash="hashed_password_123"
        )
        self.session.add(test_user)
        self.session.commit()

        # Create login sessions using model relationships
        expiry1 = datetime.now() + timedelta(hours=1)
        login_session_1 = LoginSession(
            user=test_user,
            token="token_1",
            expiry=expiry1
        )
        expiry2 = datetime.now() + timedelta(hours=2)
        login_session_2 = LoginSession(
            user=test_user,
            token="token_2",
            expiry=expiry2
        )

        self.session.add(login_session_1)
        self.session.add(login_session_2)
        self.session.commit()

        # Test bidirectional navigation - User -> LoginSessions
        assert len(test_user.login_sessions) == 2
        assert login_session_1 in test_user.login_sessions
        assert login_session_2 in test_user.login_sessions

        # Test bidirectional navigation - LoginSession -> User
        assert login_session_1.user == test_user
        assert login_session_2.user == test_user

        # Test that user_id is automatically set
        assert login_session_1.user_id == test_user.id
        assert login_session_2.user_id == test_user.id

        # Test querying through relationships
        user_sessions = self.session.query(LoginSession).filter(
            LoginSession.user == test_user
        ).all()
        assert len(user_sessions) == 2

        # Test that we can access session properties through the relationship
        session_tokens = [session.token for session in test_user.login_sessions]
        assert "token_1" in session_tokens
        assert "token_2" in session_tokens

        # Test that we can access user properties through the relationship
        assert login_session_1.user.username == "testuser"
        assert login_session_2.user.password_hash == "hashed_password_123"

    def test_user_secure_data_relationship(self):
        """Test the relationship between User and SecureData."""
        # Create a test user
        test_user = User(
            username="testuser",
            password_hash="hashed_password_123"
        )
        self.session.add(test_user)
        self.session.commit()

        # Create secure data entries using model relationships
        secure_data_1 = SecureData(
            user=test_user,
            entry_name="test_stored_password_title_1",
            website="test_encrypted_website_1",
            username="test_encrypted_username_1",
            password="test_encrypted_password_1",
            notes="test_encrypted_notes_1"
        )
        secure_data_2 = SecureData(
            user=test_user,
            entry_name="test_stored_password_title_2",
            website="test_encrypted_website_2",
            username="test_encrypted_username_2",
            password="test_encrypted_password_2",
            notes=None
        )

        self.session.add(secure_data_1)
        self.session.add(secure_data_2)
        self.session.commit()

        # Test bidirectional navigation - User -> SecureData
        assert len(test_user.secure_data) == 2
        assert secure_data_1 in test_user.secure_data
        assert secure_data_2 in test_user.secure_data

        # Test bidirectional navigation - SecureData -> User
        assert secure_data_1.user == test_user
        assert secure_data_2.user == test_user

        # Test that user_id is automatically set
        assert secure_data_1.user_id == test_user.id
        assert secure_data_2.user_id == test_user.id

        # Test querying through relationships
        user_secure_data = self.session.query(SecureData).filter(
            SecureData.user == test_user
        ).all()
        assert len(user_secure_data) == 2

        # Test that we can access secure data properties through the relationship
        entry_names = [entry.entry_name for entry in test_user.secure_data]
        assert "test_stored_password_title_1" in entry_names
        assert "test_stored_password_title_2" in entry_names

        # Test that we can access user properties through the relationship
        assert secure_data_1.user.username == "testuser"
        assert secure_data_2.user.password_hash == "hashed_password_123"

        # Test filtering secure data through relationships
        website_entries = [entry for entry in test_user.secure_data if "website_1" in entry.website]
        assert len(website_entries) == 1
        assert website_entries[0].entry_name == "test_stored_password_title_1"

        # Test that optional fields work correctly through relationships
        entries_with_notes = [entry for entry in test_user.secure_data if entry.notes is not None]
        assert len(entries_with_notes) == 1

        entries_without_notes = [entry for entry in test_user.secure_data if entry.notes is None]
        assert len(entries_without_notes) == 1

    def test_cascade_delete_behavior(self):
        """Test cascade delete behavior when a user is deleted."""
        # Create a test user
        test_user = User(
            username="testuser",
            password_hash="hashed_password_123"
        )
        self.session.add(test_user)
        self.session.commit()

        # Create login sessions for the user
        expiry1 = datetime.now() + timedelta(hours=1)
        expiry2 = datetime.now() + timedelta(hours=2)

        login_session_1 = LoginSession(
            user=test_user,
            token="token_1",
            expiry=expiry1
        )
        login_session_2 = LoginSession(
            user=test_user,
            token="token_2",
            expiry=expiry2
        )

        # Create secure data entries for the user
        secure_data_1 = SecureData(
            user=test_user,
            entry_name="test_stored_password_title_1",
            website="test_encrypted_website_1",
            username="test_encrypted_username_1",
            password="test_encrypted_password_1",
            notes="test_encrypted_notes_1"
        )
        secure_data_2 = SecureData(
            user=test_user,
            entry_name="test_stored_password_title_2",
            website="test_encrypted_website_2",
            username="test_encrypted_username_2",
            password="test_encrypted_password_2",
            notes="test_encrypted_notes_2"
        )

        self.session.add(login_session_1)
        self.session.add(login_session_2)
        self.session.add(secure_data_1)
        self.session.add(secure_data_2)
        self.session.commit()

        # Verify all records exist before deletion
        assert len(test_user.login_sessions) == 2
        assert len(test_user.secure_data) == 2

        all_login_sessions = self.session.query(LoginSession).all()
        all_secure_data = self.session.query(SecureData).all()
        assert len(all_login_sessions) == 2
        assert len(all_secure_data) == 2

        # Delete the user (this should trigger cascade delete)
        self.session.delete(test_user)
        self.session.commit()

        # Verify the user was deleted
        deleted_user = self.session.query(User).filter_by(username="testuser").first()
        assert deleted_user is None

        # Verify all related login sessions were automatically deleted
        remaining_login_sessions = self.session.query(LoginSession).all()
        assert len(remaining_login_sessions) == 0

        # Verify all related secure data was automatically deleted
        remaining_secure_data = self.session.query(SecureData).all()
        assert len(remaining_secure_data) == 0

        # Verify specific sessions and data are gone
        deleted_session_1 = self.session.query(LoginSession).filter_by(token="token_1").first()
        deleted_session_2 = self.session.query(LoginSession).filter_by(token="token_2").first()
        assert deleted_session_1 is None
        assert deleted_session_2 is None

        deleted_secure_data_1 = self.session.query(SecureData).filter_by(entry_name="test_stored_password_title_1").first()
        deleted_secure_data_2 = self.session.query(SecureData).filter_by(entry_name="test_stored_password_title_2").first()
        assert deleted_secure_data_1 is None
        assert deleted_secure_data_2 is None

    def test_token_uniqueness(self):
        """Test that login session tokens must be unique."""
        # Create a test user
        test_user = User(
            username="testuser",
            password_hash="hashed_password_123"
        )
        self.session.add(test_user)
        self.session.commit()

        # Create first login session
        expiry1 = datetime.now() + timedelta(hours=1)
        login_session_1 = LoginSession(
            user_id=test_user.id,
            token="unique_token_123",
            expiry=expiry1
        )
        self.session.add(login_session_1)
        self.session.commit()

        # Create second login session with same token
        expiry2 = datetime.now() + timedelta(hours=2)
        login_session_2 = LoginSession(
            user_id=test_user.id,
            token="unique_token_123",
            expiry=expiry2
        )
        self.session.add(login_session_2)

        # Attempt to commit
        try:
            self.session.commit()
            self.fail("Expected uniqueness constraint violation for token but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("unique constraint failed" in error_message or
                     "integrity" in error_message), f"Expected uniqueness constraint violation, got: {error_message}"
            self.session.rollback()

        # Verify only the first session exists
        sessions = self.session.query(LoginSession).filter_by(token="unique_token_123").all()
        assert len(sessions) == 1
        assert sessions[0].id == login_session_1.id

    def test_cascade_delete_user_without_related_data(self):
        """Test cascade delete behavior when user has no related records."""
        # Create a test user with no related data
        test_user = User(
            username="testuser",
            password_hash="hashed_password_123"
        )
        self.session.add(test_user)
        self.session.commit()

        # Verify user exists
        assert test_user.id is not None
        assert len(test_user.login_sessions) == 0
        assert len(test_user.secure_data) == 0

        # Delete the user
        self.session.delete(test_user)
        self.session.commit()

        # Verify the user was deleted
        deleted_user = self.session.query(User).filter_by(username="testuser").first()
        assert deleted_user is None

        # Verify no related data exists (should be empty anyway)
        all_login_sessions = self.session.query(LoginSession).all()
        all_secure_data = self.session.query(SecureData).all()
        assert len(all_login_sessions) == 0
        assert len(all_secure_data) == 0

    def test_user_username_string_handling(self):
        """Test that User username can handle various string lengths and content."""
        # Test with very long username
        long_username = "x" * 1000
        test_user_long = User(
            username=long_username,
            password_hash="hashed_password_123"
        )
        self.session.add(test_user_long)
        self.session.commit()

        # Test with special characters in username
        special_chars_username = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        test_user_special = User(
            username=special_chars_username,
            password_hash="hashed_password_123"
        )
        self.session.add(test_user_special)
        self.session.commit()

        # Test with unicode characters in username
        unicode_username = "测试用户 🚀 ñáéíóú"
        test_user_unicode = User(
            username=unicode_username,
            password_hash="hashed_password_123"
        )
        self.session.add(test_user_unicode)
        self.session.commit()

        # Test with spaces and mixed case
        mixed_username = "Test User 123 with Spaces"
        test_user_mixed = User(
            username=mixed_username,
            password_hash="hashed_password_123"
        )
        self.session.add(test_user_mixed)
        self.session.commit()

        # Verify all users were created successfully
        assert test_user_long.id is not None
        assert test_user_special.id is not None
        assert test_user_unicode.id is not None
        assert test_user_mixed.id is not None

        # Verify data integrity
        retrieved_long = self.session.query(User).filter_by(id=test_user_long.id).first()
        retrieved_special = self.session.query(User).filter_by(id=test_user_special.id).first()
        retrieved_unicode = self.session.query(User).filter_by(id=test_user_unicode.id).first()
        retrieved_mixed = self.session.query(User).filter_by(id=test_user_mixed.id).first()

        assert retrieved_long.username == long_username
        assert retrieved_special.username == special_chars_username
        assert retrieved_unicode.username == unicode_username
        assert retrieved_mixed.username == mixed_username

    def test_secure_data_string_handling(self):
        """Test that SecureData can handle various string lengths and content."""
        # Create a test user
        test_user = User(
            username="testuser",
            password_hash="hashed_password_123"
        )
        self.session.add(test_user)
        self.session.commit()

        # Test with very long strings
        long_string = "x" * 1000
        test_secure_data_long = SecureData(
            user_id=test_user.id,
            entry_name=long_string,
            website=long_string,
            username=long_string,
            password=long_string,
            notes=long_string
        )
        self.session.add(test_secure_data_long)
        self.session.commit()

        # Test with special characters
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        test_secure_data_special = SecureData(
            user_id=test_user.id,
            entry_name=special_chars,
            website=special_chars,
            username=special_chars,
            password=special_chars,
            notes=special_chars
        )
        self.session.add(test_secure_data_special)
        self.session.commit()

        # Test with unicode characters
        unicode_string = "测试数据 🚀 ñáéíóú"
        test_secure_data_unicode = SecureData(
            user_id=test_user.id,
            entry_name=unicode_string,
            website=unicode_string,
            username=unicode_string,
            password=unicode_string,
            notes=unicode_string
        )
        self.session.add(test_secure_data_unicode)
        self.session.commit()

        # Verify all were created successfully
        assert test_secure_data_long.id is not None
        assert test_secure_data_special.id is not None
        assert test_secure_data_unicode.id is not None

        # Verify data integrity
        retrieved_long = self.session.query(SecureData).filter_by(id=test_secure_data_long.id).first()
        retrieved_special = self.session.query(SecureData).filter_by(id=test_secure_data_special.id).first()
        retrieved_unicode = self.session.query(SecureData).filter_by(id=test_secure_data_unicode.id).first()

        assert retrieved_long.entry_name == long_string
        assert retrieved_special.entry_name == special_chars
        assert retrieved_unicode.entry_name == unicode_string

    def test_secure_data_fields_string_handling(self):
        """Test that SecureData individual fields can handle various string content."""
        # Create a test user
        test_user = User(
            username="testuser",
            password_hash="hashed_password_123"
        )
        self.session.add(test_user)
        self.session.commit()

        # Test entry_name field with various content
        entry_name_long = "x" * 1000
        entry_name_special = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        entry_name_unicode = "测试条目 🚀 ñáéíóú"
        entry_name_mixed = "Test Entry 123 with Spaces"

        # Test website field with various content
        website_long = "https://" + "x" * 1000
        website_special = "https://site!@#$%^&*()_+-=[]{}|;':\",./<>?`~.com"
        website_unicode = "https://测试网站🚀.com"
        website_mixed = "https://test-site-123.com/path with spaces"

        # Test username field with various content
        username_long = "x" * 1000
        username_special = "user!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        username_unicode = "测试用户名🚀"
        username_mixed = "test.user@domain.com"

        # Test password field with various content
        password_long = "x" * 1000
        password_special = "pass!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        password_unicode = "测试密码🚀"
        password_mixed = "My Password 123!"

        # Test notes field with various content
        notes_long = "x" * 1000
        notes_special = "notes!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        notes_unicode = "测试备注🚀"
        notes_mixed = "Test notes with spaces and 123 numbers"

        # Create SecureData entries with different field combinations
        test_secure_data_1 = SecureData(
            user_id=test_user.id,
            entry_name=entry_name_long,
            website=website_special,
            username=username_unicode,
            password=password_mixed,
            notes=notes_special
        )
        self.session.add(test_secure_data_1)

        test_secure_data_2 = SecureData(
            user_id=test_user.id,
            entry_name=entry_name_special,
            website=website_unicode,
            username=username_mixed,
            password=password_long,
            notes=notes_unicode
        )
        self.session.add(test_secure_data_2)

        test_secure_data_3 = SecureData(
            user_id=test_user.id,
            entry_name=entry_name_unicode,
            website=website_mixed,
            username=username_long,
            password=password_special,
            notes=notes_long
        )
        self.session.add(test_secure_data_3)

        test_secure_data_4 = SecureData(
            user_id=test_user.id,
            entry_name=entry_name_mixed,
            website=website_long,
            username=username_special,
            password=password_unicode,
            notes=notes_mixed
        )
        self.session.add(test_secure_data_4)

        self.session.commit()

        # Verify all entries were created successfully
        assert test_secure_data_1.id is not None
        assert test_secure_data_2.id is not None
        assert test_secure_data_3.id is not None
        assert test_secure_data_4.id is not None

        # Verify data integrity for each field type
        retrieved_1 = self.session.query(SecureData).filter_by(id=test_secure_data_1.id).first()
        retrieved_2 = self.session.query(SecureData).filter_by(id=test_secure_data_2.id).first()
        retrieved_3 = self.session.query(SecureData).filter_by(id=test_secure_data_3.id).first()
        retrieved_4 = self.session.query(SecureData).filter_by(id=test_secure_data_4.id).first()

        # Test entry_name field integrity
        assert retrieved_1.entry_name == entry_name_long
        assert retrieved_2.entry_name == entry_name_special
        assert retrieved_3.entry_name == entry_name_unicode
        assert retrieved_4.entry_name == entry_name_mixed

        # Test website field integrity
        assert retrieved_1.website == website_special
        assert retrieved_2.website == website_unicode
        assert retrieved_3.website == website_mixed
        assert retrieved_4.website == website_long

        # Test username field integrity
        assert retrieved_1.username == username_unicode
        assert retrieved_2.username == username_mixed
        assert retrieved_3.username == username_long
        assert retrieved_4.username == username_special

        # Test password field integrity
        assert retrieved_1.password == password_mixed
        assert retrieved_2.password == password_long
        assert retrieved_3.password == password_special
        assert retrieved_4.password == password_unicode

        # Test notes field integrity
        assert retrieved_1.notes == notes_special
        assert retrieved_2.notes == notes_unicode
        assert retrieved_3.notes == notes_long
        assert retrieved_4.notes == notes_mixed


if __name__ == '__main__':
    pytest.main(['-v', __file__])
