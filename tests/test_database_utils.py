import os
import sys
import pytest
import tempfile
import shutil
import time
import gc
from datetime import timedelta

from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database_utils import Database, FailureReason
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
        self._safe_remove_database()
        Database._database_initialised = False
        Database.init_database()

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
        """Test that get_db_session opens a session (cannot verify close)"""
        with Database._get_db_session() as session:
            # Check that session exists
            assert session.execute(text("SELECT 1")).scalar() == 1

            # Check that session is correct
            assert session is not None
            assert hasattr(session, 'commit')
            assert hasattr(session, 'rollback')
            assert hasattr(session, 'close')

    def test_database_initilaisation(self):
        """Test that the database initialises correctly the first time"""
        # Clean up existing database and reset everything
        reset_engine()
        self._safe_remove_database()
        Database._database_initialised = False
        assert Database._database_initialised is False
        assert not os.path.exists(self.test_db_path)

        # Test that initialization returns True on first run
        assert Database.init_database() is True
        assert Database._database_initialised is True

        # Verify that the database file & tables were created
        assert os.path.exists(self.test_db_path)
        with Database._get_db_session() as session:
            tables = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
            table_names = [table[0] for table in tables]
            assert 'user' in table_names
            assert 'session' in table_names
            assert 'encrypted' in table_names

    def test_failed_database_initialisation(self):
        """Test that databse initialisation fails if it's already been run"""
        # Ensure database is already initialized
        assert Database._database_initialised is True
        assert os.path.exists(self.test_db_path)

        # Create some test data to verify it's the same database after failed init
        test_username = "test_user_for_same_db_check"
        test_secret_key_hash = "test_hash_123"

        # Insert test data into the existing database
        with Database._get_db_session() as session:
            from database.database_models import User
            test_user = User(username=test_username, secret_key_hash=test_secret_key_hash, secret_key_enc=test_secret_key_hash)
            session.add(test_user)
            session.commit()

            # Verify the test data was inserted
            user_count_before = session.execute(text("SELECT COUNT(*) FROM user")).scalar()
            assert user_count_before is not None
            assert user_count_before >= 1

        # Test that initialization returns False when already initialized
        assert Database.init_database() is False
        assert Database._database_initialised is True

        # Verify database file still exists and is functional
        assert os.path.exists(self.test_db_path)
        with Database._get_db_session() as session:
            assert session.execute(text("SELECT 1")).scalar() == 1

            # Verify our test data is still there (proving it's the same database)
            user_count_after = session.execute(text("SELECT COUNT(*) FROM user")).scalar()
            assert user_count_after == user_count_before

            # Verify the specific test user still exists
            test_user_exists = session.execute(
                text("SELECT username FROM user WHERE username = :username"),
                {"username": test_username}
            ).scalar()
            assert test_user_exists == test_username

    def test_create_user(self):
        """Test user creation"""
        # Create user
        test_username = "test_user"
        test_secret_key_hash = "hashed_secret_key_123"
        test_secret_key_enc = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username, test_secret_key_hash, test_secret_key_enc)
        assert success is True
        assert failure_reason is None

        # Confirm user added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash

    def test_create_session(self):
        """Test session creation"""
        # Create user
        test_username = "test_user"
        test_secret_key_hash = "hashed_secret_key_123"
        test_secret_key_enc = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username, test_secret_key_hash, test_secret_key_enc)
        assert success is True
        assert failure_reason is None

        # Confirm user added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash

        # Create Session
        session_token = "session_01"
        session_expiry_time = timedelta(hours=1)
        success, failure_reason = Database.create_session(test_username, session_token, session_expiry_time)
        assert success is True
        assert failure_reason is None

        # Confirm session added
        success, failure_reason, username = Database.check_session_token(session_token)
        assert success is True
        assert failure_reason is None
        assert username == test_username

    def test_create_secure_data(self):
        """Test secure data creation"""
        # Create user
        test_username = "test_user"
        test_secret_key_hash = "hashed_secret_key_123"
        test_secret_key_enc = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username, test_secret_key_hash, test_secret_key_enc)
        assert success is True
        assert failure_reason is None

        # Confirm user added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash

        # Create Secure Data
        entry_name = "test_stored_password_title"
        website = "test_encrypted_website"
        username = "test_encrypted_username"
        password = "test_encrypted_password"
        notes = "test_encrypted_notes"
        success, failure_reason = Database.create_secure_data(test_username, entry_name, website, username, password, notes)
        assert success is True
        assert failure_reason is None

        # Confirm Secure Data added
        success, failure_reason, entries_list = Database.get_secure_entries_list(test_username)
        assert success is True
        assert failure_reason is None
        assert entries_list is not None
        assert len(entries_list) == 1

        # Check that entry data matches
        retrieved_entry_name, entry_public_id = entries_list[0]
        assert retrieved_entry_name == entry_name
        assert entry_public_id is not None
        assert len(entry_public_id) > 0

        # Verify secure data content
        success, failure_reason, entry_data = Database.get_secure_entry_data(entry_public_id)
        assert success is True
        assert failure_reason is None
        assert entry_data is not None
        assert entry_data["entry_name"] == entry_name
        assert entry_data["website"] == website
        assert entry_data["username"] == username
        assert entry_data["password"] == password
        assert entry_data["notes"] == notes
        assert entry_data["public_id"] == entry_public_id

    def test_create_user_duplicate_username(self):
        """Test creating a user with a username that already exists"""
        # Create user
        test_username = "test_user"
        test_secret_key_hash = "hashed_secret_key_123"
        test_secret_key_enc = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username, test_secret_key_hash, test_secret_key_enc)
        assert success is True
        assert failure_reason is None

        # Confirm user added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash

        # Create another user with the same username
        second_test_secret_key_hash = "new_hashed_secret_key_456"
        second_test_secret_key_enc = "new_encrypted_secret_key_456"
        success, failure_reason = Database.create_user(test_username, second_test_secret_key_hash, second_test_secret_key_enc)
        assert success is False
        assert failure_reason == FailureReason.ALREADY_EXISTS

        # Confirm second user was not added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash

    def test_delete_user(self):
        """Test user deletion"""
        # Create users
        test_username_1 = "test_user_1"
        test_secret_key_hash_1 = "hashed_secret_key_123"
        test_secret_key_enc_1 = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username_1, test_secret_key_hash_1, test_secret_key_enc_1)
        assert success is True
        assert failure_reason is None
        test_username_2 = "test_user_2"
        test_secret_key_hash_2 = "hashed_secret_key_123"
        test_secret_key_enc_2 = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username_2, test_secret_key_hash_2, test_secret_key_enc_2)
        assert success is True
        assert failure_reason is None

        # Confirm users added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username_1)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash_1
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username_2)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash_2

        # Delete user
        success, failure_reason = Database.delete_user(test_username_1)
        assert success is True
        assert failure_reason is None

        # Confirm user deleted and other user unaffected
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username_1)
        assert success is False
        assert failure_reason == FailureReason.USERNAME_NOT_FOUND
        assert secret_key_hash is None
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username_2)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash_2

    def test_delete_user_cascades_to_sessions(self):
        """Test that deleting a user also removes their sessions"""
        # Create user
        test_username = "test_user"
        test_secret_key_hash = "hashed_secret_key_123"
        test_secret_key_enc = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username, test_secret_key_hash, test_secret_key_enc)
        assert success is True
        assert failure_reason is None

        # Confirm user was added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash

        # Create Session
        session_token_1 = "session_01"
        session_expiry_time_1 = timedelta(hours=1)
        success, failure_reason = Database.create_session(test_username, session_token_1, session_expiry_time_1)
        assert success is True
        assert failure_reason is None

        # Create additional Session
        session_token_2 = "session_02"
        session_expiry_time_2 = timedelta(hours=1)
        success, failure_reason = Database.create_session(test_username, session_token_2, session_expiry_time_2)
        assert success is True
        assert failure_reason is None

        # Confirm additional sessions added
        success, failure_reason, username = Database.check_session_token(session_token_1)
        assert success is True
        assert failure_reason is None
        assert username == test_username
        success, failure_reason, username = Database.check_session_token(session_token_2)
        assert success is True
        assert failure_reason is None
        assert username == test_username

        # Delete user
        success, failure_reason = Database.delete_user(test_username)
        assert success is True
        assert failure_reason is None

        # Confirm user and sessions deleted
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is False
        assert failure_reason == FailureReason.USERNAME_NOT_FOUND
        assert secret_key_hash is None
        success, failure_reason, username = Database.check_session_token(session_token_1)
        assert success is False
        assert failure_reason == FailureReason.SESSION_NOT_FOUND
        assert username is None
        success, failure_reason, username = Database.check_session_token(session_token_2)
        assert success is False
        assert failure_reason == FailureReason.SESSION_NOT_FOUND
        assert username is None

    def test_delete_user_cascades_to_secure_data(self):
        """Test that deleting a user also removes their secure data"""
        # Create user
        test_username = "test_user"
        test_secret_key_hash = "hashed_secret_key_123"
        test_secret_key_enc = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username, test_secret_key_hash, test_secret_key_enc)
        assert success is True
        assert failure_reason is None

        # Confirm user was added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash

        # Create Secure Data
        entry_name = "test_stored_password_title"
        website = "test_encrypted_website"
        username = "test_encrypted_username"
        password = "test_encrypted_password"
        notes = "test_encrypted_notes"
        success, failure_reason = Database.create_secure_data(test_username, entry_name, website, username, password, notes)
        assert success is True
        assert failure_reason is None

        # Create additional Secure Data
        entry_name_2 = "test_stored_password_title_2"
        website_2 = "test_encrypted_website_2"
        username_2 = "test_encrypted_username_2"
        password_2 = "test_encrypted_password_2"
        notes_2 = "test_encrypted_notes_2"
        success, failure_reason = Database.create_secure_data(test_username, entry_name_2, website_2, username_2, password_2, notes_2)
        assert success is True
        assert failure_reason is None

        # Confirm Secure Data added
        success, failure_reason, entries_list = Database.get_secure_entries_list(test_username)
        assert success is True
        assert failure_reason is None
        assert entries_list is not None
        assert len(entries_list) == 2

        # Get public IDs for Secure Data
        secure_data_1_public_id = entries_list[0][1]
        secure_data_2_public_id = entries_list[1][1]
        assert secure_data_1_public_id is not None
        assert secure_data_2_public_id is not None

        # Delete user
        success, failure_reason = Database.delete_user(test_username)
        assert success is True
        assert failure_reason is None

        # Confirm user & Secure Data deleted
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is False
        assert failure_reason == FailureReason.USERNAME_NOT_FOUND
        assert secret_key_hash is None
        success, failure_reason, entries_list = Database.get_secure_entries_list(test_username)
        assert success is False
        assert failure_reason == FailureReason.USERNAME_NOT_FOUND
        assert entries_list is None
        success, failure_reason, entry_data = Database.get_secure_entry_data(secure_data_1_public_id)
        assert success is False
        assert failure_reason == FailureReason.ENTRY_NOT_FOUND
        assert entry_data is None
        success, failure_reason, entry_data = Database.get_secure_entry_data(secure_data_2_public_id)
        assert success is False
        assert failure_reason == FailureReason.ENTRY_NOT_FOUND
        assert entry_data is None

    def test_get_user_secret_key_enc_nonexistent_user(self):
        """Test retrieving encrypted secret key for a user that doesn't exist"""
        # Confirm user does not exist
        test_username = "test_user"
        success, failure_reason, secret_key_enc = Database.get_user_secret_key_enc(test_username)
        assert success is False
        assert failure_reason == FailureReason.USERNAME_NOT_FOUND
        assert secret_key_enc is None

    def test_get_user_secret_key_enc_existing_user(self):
        """Test retrieving encrypted secret key for an existing user"""
        # Create user
        test_username = "test_user"
        test_secret_key_hash = "hashed_secret_key_123"
        test_secret_key_enc = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username, test_secret_key_hash, test_secret_key_enc)
        assert success is True
        assert failure_reason is None

        # Retrieve encrypted secret key
        success, failure_reason, secret_key_enc = Database.get_user_secret_key_enc(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_enc == test_secret_key_enc

    def test_get_user_secret_key_hash_nonexistent_user(self):
        """Test retrieving password hash for a user that doesn't exist"""
        # Confirm user does not exist
        test_username = "test_user"
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is False
        assert failure_reason == FailureReason.USERNAME_NOT_FOUND
        assert secret_key_hash is None

    def test_create_session_nonexistent_user(self):
        """Test creating a session for a user that doesn't exist"""
        # Confirm user does not exist
        test_username = "test_user"
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is False
        assert failure_reason == FailureReason.USERNAME_NOT_FOUND
        assert secret_key_hash is None

        # Attempt to create session
        session_token = "session_01"
        session_expiry_time = timedelta(hours=1)
        success, failure_reason = Database.create_session(test_username, session_token, session_expiry_time)
        assert success is False
        assert failure_reason == FailureReason.USERNAME_NOT_FOUND

        # Ensure session was not created
        success, failure_reason, username = Database.check_session_token(session_token)
        assert success is False
        assert failure_reason == FailureReason.SESSION_NOT_FOUND
        assert username is None

    def test_check_session_token_expired_token(self):
        """Test checking an expired session token (should delete and return None)"""
        # Create user
        test_username = "test_user"
        test_secret_key_hash = "hashed_secret_key_123"
        test_secret_key_enc = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username, test_secret_key_hash, test_secret_key_enc)
        assert success is True
        assert failure_reason is None

        # Confirm user added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash

        # Create Session with expired time
        session_token = "session_01"
        session_expiry_time = timedelta(hours=-1)
        success, failure_reason = Database.create_session(test_username, session_token, session_expiry_time)
        assert success is True
        assert failure_reason is None

        # Confirm checking session returns None
        success, failure_reason, username = Database.check_session_token(session_token)
        assert success is False
        assert failure_reason == FailureReason.SESSION_NOT_FOUND
        assert username is None

    def test_check_session_token_nonexistent_token(self):
        """Test checking a token that doesn't exist"""
        session_token = "session_01"
        success, failure_reason, username = Database.check_session_token(session_token)
        assert success is False
        assert failure_reason == FailureReason.SESSION_NOT_FOUND
        assert username is None

    def test_create_session_token_existing_token(self):
        """Test creating a session with the same token as an existing session"""
        # Create users
        test_username_1 = "test_user_1"
        test_secret_key_hash_1 = "hashed_secret_key_123"
        test_secret_key_enc_1 = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username_1, test_secret_key_hash_1, test_secret_key_enc_1)
        assert success is True
        assert failure_reason is None
        test_username_2 = "test_user_2"
        test_secret_key_hash_2 = "hashed_secret_key_123"
        test_secret_key_enc_2 = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username_2, test_secret_key_hash_2, test_secret_key_enc_2)
        assert success is True
        assert failure_reason is None

        # Confirm users added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username_1)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash_1
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username_2)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash_2

        # Create Session
        session_token = "session_01"
        session_expiry_time = timedelta(hours=1)
        success, failure_reason = Database.create_session(test_username_1, session_token, session_expiry_time)
        assert success is True
        assert failure_reason is None

        # Confirm session added
        success, failure_reason, username = Database.check_session_token(session_token)
        assert success is True
        assert failure_reason is None
        assert username == test_username_1

        # Create another identical session, and verify original still exists
        success, failure_reason = Database.create_session(test_username_2, session_token, session_expiry_time)
        assert success is False  # This should fail due to unique constraint
        success, failure_reason, username = Database.check_session_token(session_token)
        assert success is True
        assert failure_reason is None
        assert username == test_username_1

    def test__delete_session(self):
        """Test single session deletion"""
        # Create user
        test_username = "test_user"
        test_secret_key_hash = "hashed_secret_key_123"
        test_secret_key_enc = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username, test_secret_key_hash, test_secret_key_enc)
        assert success is True
        assert failure_reason is None

        # Confirm user was added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash

        # Create Session
        session_token_1 = "session_01"
        session_expiry_time_1 = timedelta(hours=1)
        success, failure_reason = Database.create_session(test_username, session_token_1, session_expiry_time_1)
        assert success is True
        assert failure_reason is None

        # Create additional Session
        session_token_2 = "session_02"
        session_expiry_time_2 = timedelta(hours=1)
        success, failure_reason = Database.create_session(test_username, session_token_2, session_expiry_time_2)
        assert success is True
        assert failure_reason is None

        # Confirm additional sessions added
        success, failure_reason, username = Database.check_session_token(session_token_1)
        assert success is True
        assert failure_reason is None
        assert username == test_username
        success, failure_reason, username = Database.check_session_token(session_token_2)
        assert success is True
        assert failure_reason is None
        assert username == test_username

        # Delete Session, confirm deleted, and confirm other session(s) unaffected
        success, failure_reason = Database.delete_session(session_token_1)
        assert success is True
        assert failure_reason is None
        success, failure_reason, username = Database.check_session_token(session_token_1)
        assert success is False
        assert failure_reason == FailureReason.SESSION_NOT_FOUND
        assert username is None
        success, failure_reason, username = Database.check_session_token(session_token_2)
        assert success is True
        assert failure_reason is None
        assert username == test_username

    def test_delete_session_nonexistent_token(self):
        """Test deleting a session token that doesn't exist"""
        session_token = "session_01"
        success, failure_reason, username = Database.check_session_token(session_token)
        assert success is False
        assert failure_reason == FailureReason.SESSION_NOT_FOUND
        assert username is None
        success, failure_reason = Database.delete_session(session_token)
        assert success is False
        assert failure_reason == FailureReason.SESSION_NOT_FOUND

    def test_delete_all_sessions(self):
        """Test deleting all of a user's sessions"""
        # Create user
        test_username = "test_user"
        test_secret_key_hash = "hashed_secret_key_123"
        test_secret_key_enc = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username, test_secret_key_hash, test_secret_key_enc)
        assert success is True
        assert failure_reason is None

        # Confirm user was added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash

        # Create Session
        session_token_1 = "session_01"
        session_expiry_time_1 = timedelta(hours=1)
        success, failure_reason = Database.create_session(test_username, session_token_1, session_expiry_time_1)
        assert success is True
        assert failure_reason is None

        # Create additional Session
        session_token_2 = "session_02"
        session_expiry_time_2 = timedelta(hours=1)
        success, failure_reason = Database.create_session(test_username, session_token_2, session_expiry_time_2)
        assert success is True
        assert failure_reason is None

        # Confirm additional sessions added
        success, failure_reason, username = Database.check_session_token(session_token_1)
        assert success is True
        assert failure_reason is None
        assert username == test_username
        success, failure_reason, username = Database.check_session_token(session_token_2)
        assert success is True
        assert failure_reason is None
        assert username == test_username

        # Delete all sessions for user, and confirm deletion
        success, failure_reason = Database.delete_all_sessions(test_username)
        assert success is True
        assert failure_reason is None
        success, failure_reason, username = Database.check_session_token(session_token_1)
        assert success is False
        assert failure_reason == FailureReason.SESSION_NOT_FOUND
        assert username is None
        success, failure_reason, username = Database.check_session_token(session_token_2)
        assert success is False
        assert failure_reason == FailureReason.SESSION_NOT_FOUND
        assert username is None

    def test_delete_all_sessions_nonexistent_user(self):
        """Test deleting all sessions for a user that doesn't exist"""
        test_username = "test_user"
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is False
        assert failure_reason == FailureReason.USERNAME_NOT_FOUND
        assert secret_key_hash is None
        success, failure_reason = Database.delete_all_sessions(test_username)
        assert success is False
        assert failure_reason == FailureReason.USERNAME_NOT_FOUND

    def test_clean_sessions_with_expired_sessions(self):
        """Test cleaning sessions when there are expired sessions to remove"""
        # Create users
        test_username_1 = "test_user_1"
        test_secret_key_hash_1 = "hashed_secret_key_123"
        test_secret_key_enc_1 = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username_1, test_secret_key_hash_1, test_secret_key_enc_1)
        assert success is True
        assert failure_reason is None
        test_username_2 = "test_user_2"
        test_secret_key_hash_2 = "hashed_secret_key_123"
        test_secret_key_enc_2 = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username_2, test_secret_key_hash_2, test_secret_key_enc_2)
        assert success is True
        assert failure_reason is None

        # Confirm users added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username_1)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash_1
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username_2)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash_2

        # Create Sessions with expired time
        session_token_1 = "session_01"
        session_expiry_time_1 = timedelta(hours=-1)
        session_token_2 = "session_02"
        session_expiry_time_2 = timedelta(hours=-2)
        session_token_3 = "session_03"
        session_expiry_time_3 = timedelta(hours=-3)
        session_token_4 = "session_04"
        session_expiry_time_4 = timedelta(hours=-4)
        success, failure_reason = Database.create_session(test_username_1, session_token_1, session_expiry_time_1)
        assert success is True
        assert failure_reason is None
        success, failure_reason = Database.create_session(test_username_1, session_token_2, session_expiry_time_2)
        assert success is True
        assert failure_reason is None
        success, failure_reason = Database.create_session(test_username_2, session_token_3, session_expiry_time_3)
        assert success is True
        assert failure_reason is None
        success, failure_reason = Database.create_session(test_username_2, session_token_4, session_expiry_time_4)
        assert success is True
        assert failure_reason is None
        # (Cannot confirm sessions are added by inspection, due to automatic deletion of expired sessions)

        # Clean sessions, and confirm all deleted
        success, failure_reason = Database.clean_sessions()
        assert success is True
        assert failure_reason is None
        success, failure_reason, username = Database.check_session_token(session_token_1)
        assert success is False
        assert failure_reason == FailureReason.SESSION_NOT_FOUND
        assert username is None
        success, failure_reason, username = Database.check_session_token(session_token_2)
        assert success is False
        assert failure_reason == FailureReason.SESSION_NOT_FOUND
        assert username is None
        success, failure_reason, username = Database.check_session_token(session_token_3)
        assert success is False
        assert failure_reason == FailureReason.SESSION_NOT_FOUND
        assert username is None
        success, failure_reason, username = Database.check_session_token(session_token_4)
        assert success is False
        assert failure_reason == FailureReason.SESSION_NOT_FOUND
        assert username is None

    def test_clean_sessions_with_no_expired_sessions(self):
        """Test cleaning sessions when there are no expired sessions"""
        # Create users
        test_username_1 = "test_user_1"
        test_secret_key_hash_1 = "hashed_secret_key_123"
        test_secret_key_enc_1 = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username_1, test_secret_key_hash_1, test_secret_key_enc_1)
        assert success is True
        assert failure_reason is None
        test_username_2 = "test_user_2"
        test_secret_key_hash_2 = "hashed_secret_key_123"
        test_secret_key_enc_2 = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username_2, test_secret_key_hash_2, test_secret_key_enc_2)
        assert success is True
        assert failure_reason is None

        # Confirm users added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username_1)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash_1
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username_2)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash_2

        # Create Sessions with future expiry
        session_token_1 = "session_01"
        session_expiry_time_1 = timedelta(hours=1)
        session_token_2 = "session_02"
        session_expiry_time_2 = timedelta(hours=2)
        session_token_3 = "session_03"
        session_expiry_time_3 = timedelta(hours=3)
        session_token_4 = "session_04"
        session_expiry_time_4 = timedelta(hours=4)
        success, failure_reason = Database.create_session(test_username_1, session_token_1, session_expiry_time_1)
        assert success is True
        assert failure_reason is None
        success, failure_reason = Database.create_session(test_username_1, session_token_2, session_expiry_time_2)
        assert success is True
        assert failure_reason is None
        success, failure_reason = Database.create_session(test_username_2, session_token_3, session_expiry_time_3)
        assert success is True
        assert failure_reason is None
        success, failure_reason = Database.create_session(test_username_2, session_token_4, session_expiry_time_4)
        assert success is True
        assert failure_reason is None

        # Confirm sessions added
        success, failure_reason, username = Database.check_session_token(session_token_1)
        assert success is True
        assert failure_reason is None
        assert username == test_username_1
        success, failure_reason, username = Database.check_session_token(session_token_2)
        assert success is True
        assert failure_reason is None
        assert username == test_username_1
        success, failure_reason, username = Database.check_session_token(session_token_3)
        assert success is True
        assert failure_reason is None
        assert username == test_username_2
        success, failure_reason, username = Database.check_session_token(session_token_4)
        assert success is True
        assert failure_reason is None
        assert username == test_username_2

        # Clean sessions, and confirm all exist
        success, failure_reason = Database.clean_sessions()
        assert success is True
        assert failure_reason is None
        success, failure_reason, username = Database.check_session_token(session_token_1)
        assert success is True
        assert failure_reason is None
        assert username == test_username_1
        success, failure_reason, username = Database.check_session_token(session_token_2)
        assert success is True
        assert failure_reason is None
        assert username == test_username_1
        success, failure_reason, username = Database.check_session_token(session_token_3)
        assert success is True
        assert failure_reason is None
        assert username == test_username_2
        success, failure_reason, username = Database.check_session_token(session_token_4)
        assert success is True
        assert failure_reason is None
        assert username == test_username_2

    def test_clean_sessions_with_mix_of_expiry(self):
        """Test cleaning sessions when there are a mix of expired sessions"""
        # Create users
        test_username_1 = "test_user_1"
        test_secret_key_hash_1 = "hashed_secret_key_123"
        test_secret_key_enc_1 = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username_1, test_secret_key_hash_1, test_secret_key_enc_1)
        assert success is True
        assert failure_reason is None
        test_username_2 = "test_user_2"
        test_secret_key_hash_2 = "hashed_secret_key_123"
        test_secret_key_enc_2 = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username_2, test_secret_key_hash_2, test_secret_key_enc_2)
        assert success is True
        assert failure_reason is None

        # Confirm users added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username_1)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash_1
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username_2)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash_2

        # Create Sessions with past & future expiry
        session_token_1 = "session_01"
        session_expiry_time_1 = timedelta(hours=-1)
        session_token_2 = "session_02"
        session_expiry_time_2 = timedelta(hours=2)
        session_token_3 = "session_03"
        session_expiry_time_3 = timedelta(hours=-3)
        session_token_4 = "session_04"
        session_expiry_time_4 = timedelta(hours=4)
        success, failure_reason = Database.create_session(test_username_1, session_token_1, session_expiry_time_1)
        assert success is True
        assert failure_reason is None
        success, failure_reason = Database.create_session(test_username_1, session_token_2, session_expiry_time_2)
        assert success is True
        assert failure_reason is None
        success, failure_reason = Database.create_session(test_username_2, session_token_3, session_expiry_time_3)
        assert success is True
        assert failure_reason is None
        success, failure_reason = Database.create_session(test_username_2, session_token_4, session_expiry_time_4)
        assert success is True
        assert failure_reason is None

        # Confirm (non expired) sessions added
        success, failure_reason, username = Database.check_session_token(session_token_2)
        assert success is True
        assert failure_reason is None
        assert username == test_username_1
        success, failure_reason, username = Database.check_session_token(session_token_4)
        assert success is True
        assert failure_reason is None
        assert username == test_username_2

        # Clean sessions, and confirm correct sessions exist
        success, failure_reason = Database.clean_sessions()
        assert success is True
        assert failure_reason is None
        success, failure_reason, username = Database.check_session_token(session_token_1)
        assert success is False
        assert failure_reason == FailureReason.SESSION_NOT_FOUND
        assert username is None
        success, failure_reason, username = Database.check_session_token(session_token_2)
        assert success is True
        assert failure_reason is None
        assert username == test_username_1
        success, failure_reason, username = Database.check_session_token(session_token_3)
        assert success is False
        assert failure_reason == FailureReason.SESSION_NOT_FOUND
        assert username is None
        success, failure_reason, username = Database.check_session_token(session_token_4)
        assert success is True
        assert failure_reason is None
        assert username == test_username_2

    def test_create_secure_data_nonexistent_user(self):
        """Test creating secure data for a user that doesn't exist"""
        # Confirm user does not exist
        test_username = "test_user"
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is False
        assert failure_reason == FailureReason.USERNAME_NOT_FOUND
        assert secret_key_hash is None

        # Create Secure Data
        entry_name = "test_stored_password_title"
        website = "test_encrypted_website"
        username = "test_encrypted_username"
        password = "test_encrypted_password"
        notes = "test_encrypted_notes"
        success, failure_reason = Database.create_secure_data(test_username, entry_name, website, username, password, notes)
        assert success is False
        assert failure_reason == FailureReason.USERNAME_NOT_FOUND

    def test_edit_secure_data(self):
        """Test secure data editing"""
        # Create user
        test_username = "test_user"
        test_secret_key_hash = "hashed_secret_key_123"
        test_secret_key_enc = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username, test_secret_key_hash, test_secret_key_enc)
        assert success is True
        assert failure_reason is None

        # Confirm user added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash

        # Create Secure Data
        entry_name_1 = "test_stored_password_title_1"
        website_1 = "test_encrypted_website_1"
        username_1 = "test_encrypted_username_1"
        password_1 = "test_encrypted_password_1"
        notes_1 = "test_encrypted_notes_1"
        success, failure_reason = Database.create_secure_data(test_username, entry_name_1, website_1, username_1, password_1, notes_1)
        assert success is True
        assert failure_reason is None

        # Confirm secure data added and get public id
        success, failure_reason, entries_list = Database.get_secure_entries_list(test_username)
        assert success is True
        assert failure_reason is None
        assert entries_list is not None
        assert len(entries_list) == 1
        _, entry_public_id = entries_list[0]

        # Edit secure data
        entry_name_2 = "test_stored_password_title_2"
        website_2 = "test_encrypted_website_2"
        username_2 = "test_encrypted_username_2"
        password_2 = "test_encrypted_password_2"
        notes_2 = "test_encrypted_notes_2"
        success, failure_reason = Database.edit_secure_data(entry_public_id, entry_name_2, website_2, username_2, password_2, notes_2)
        assert success is True
        assert failure_reason is None

        # Verify edited secure data content
        success, failure_reason, entry_data = Database.get_secure_entry_data(entry_public_id)
        assert success is True
        assert failure_reason is None
        assert entry_data is not None
        assert entry_data["entry_name"] == entry_name_2
        assert entry_data["website"] == website_2
        assert entry_data["username"] == username_2
        assert entry_data["password"] == password_2
        assert entry_data["notes"] == notes_2

    def test_edit_secure_data_partial_update(self):
        """Test editing secure data with only some fields updated"""
        # Create user
        test_username = "test_user"
        test_secret_key_hash = "hashed_secret_key_123"
        test_secret_key_enc = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username, test_secret_key_hash, test_secret_key_enc)
        assert success is True
        assert failure_reason is None

        # Confirm user added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash

        # Create Secure Data
        entry_name_1 = "test_stored_password_title_1"
        website_1 = "test_encrypted_website_1"
        username_1 = "test_encrypted_username_1"
        password_1 = "test_encrypted_password_1"
        notes_1 = "test_encrypted_notes_1"
        success, failure_reason = Database.create_secure_data(test_username, entry_name_1, website_1, username_1, password_1, notes_1)
        assert success is True
        assert failure_reason is None

        # Confirm secure data added and get public id
        success, failure_reason, entries_list = Database.get_secure_entries_list(test_username)
        assert success is True
        assert failure_reason is None
        assert entries_list is not None
        assert len(entries_list) == 1
        _, entry_public_id = entries_list[0]

        # Edit secure data
        entry_name_2 = "test_stored_password_title_2"
        username_2 = "test_encrypted_username_2"
        notes_2 = "test_encrypted_notes_2"
        success, failure_reason = Database.edit_secure_data(entry_public_id, entry_name_2, None, username_2, None, notes_2)
        assert success is True
        assert failure_reason is None

        # Verify edited secure data content
        success, failure_reason, entry_data = Database.get_secure_entry_data(entry_public_id)
        assert success is True
        assert failure_reason is None
        assert entry_data is not None
        # Old details unchanged
        assert entry_data["website"] == website_1
        assert entry_data["password"] == password_1
        # New details changed
        assert entry_data["entry_name"] == entry_name_2
        assert entry_data["username"] == username_2
        assert entry_data["notes"] == notes_2

    def test_edit_secure_data_no_update(self):
        """Test editing secure data with no fields updated"""
        # Create user
        test_username = "test_user"
        test_secret_key_hash = "hashed_secret_key_123"
        test_secret_key_enc = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username, test_secret_key_hash, test_secret_key_enc)
        assert success is True
        assert failure_reason is None

        # Confirm user added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash

        # Create Secure Data
        entry_name = "test_stored_password_title_1"
        website = "test_encrypted_website_1"
        username = "test_encrypted_username_1"
        password = "test_encrypted_password_1"
        notes = "test_encrypted_notes_1"
        success, failure_reason = Database.create_secure_data(test_username, entry_name, website, username, password, notes)
        assert success is True
        assert failure_reason is None

        # Confirm secure data added and get public id
        success, failure_reason, entries_list = Database.get_secure_entries_list(test_username)
        assert success is True
        assert failure_reason is None
        assert entries_list is not None
        assert len(entries_list) == 1
        _, entry_public_id = entries_list[0]

        # Edit secure data
        success, failure_reason = Database.edit_secure_data(entry_public_id, None, None, None, None, None)
        assert success is True
        assert failure_reason is None

        # Verify edited secure data content
        success, failure_reason, entry_data = Database.get_secure_entry_data(entry_public_id)
        assert success is True
        assert failure_reason is None
        assert entry_data is not None
        # Old details unchanged
        assert entry_data["entry_name"] == entry_name
        assert entry_data["website"] == website
        assert entry_data["username"] == username
        assert entry_data["password"] == password
        assert entry_data["notes"] == notes

    def test_edit_secure_data_nonexistent_entry(self):
        """Test editing a secure entry that doesn't exist"""
        fake_public_entry_id = "public_entry_id"
        success, failure_reason = Database.edit_secure_data(fake_public_entry_id, None, None, None, None, None)
        assert success is False
        assert failure_reason == FailureReason.ENTRY_NOT_FOUND

    def test_delete_secure_data(self):
        """Test secure data deletion"""
        # Create user
        test_username = "test_user"
        test_secret_key_hash = "hashed_secret_key_123"
        test_secret_key_enc = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username, test_secret_key_hash, test_secret_key_enc)
        assert success is True
        assert failure_reason is None

        # Confirm user added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash

        # Create Secure Data
        entry_name_1 = "test_stored_password_title_1"
        website_1 = "test_encrypted_website_1"
        username_1 = "test_encrypted_username_1"
        password_1 = "test_encrypted_password_1"
        notes_1 = "test_encrypted_notes_1"
        success, failure_reason = Database.create_secure_data(test_username, entry_name_1, website_1, username_1, password_1, notes_1)
        assert success is True
        assert failure_reason is None
        entry_name_2 = "test_stored_password_title_2"
        website_2 = "test_encrypted_website_2"
        username_2 = "test_encrypted_username_2"
        password_2 = "test_encrypted_password_2"
        notes_2 = "test_encrypted_notes_2"
        success, failure_reason = Database.create_secure_data(test_username, entry_name_2, website_2, username_2, password_2, notes_2)
        assert success is True
        assert failure_reason is None

        # Confirm Secure Data entries added & get public ID
        success, failure_reason, entries_list = Database.get_secure_entries_list(test_username)
        assert success is True
        assert failure_reason is None
        assert entries_list is not None
        assert len(entries_list) == 2
        _, entry_public_id_1 = entries_list[0]
        _, entry_public_id_2 = entries_list[1]

        # Delete secure data & verify deletion
        success, failure_reason = Database.delete_secure_data(entry_public_id_1)
        assert success is True
        assert failure_reason is None
        success, failure_reason, entry_data = Database.get_secure_entry_data(entry_public_id_1)
        assert success is False
        assert failure_reason == FailureReason.ENTRY_NOT_FOUND
        assert entry_data is None
        success, failure_reason, entry_data = Database.get_secure_entry_data(entry_public_id_2)
        assert success is True
        assert failure_reason is None
        assert entry_data is not None

    def test_delete_secure_data_non_existing_data(self):
        """Test deleting secure entry which does not exist"""
        fake_public_entry_id = "public_entry_id"
        success, failure_reason = Database.delete_secure_data(fake_public_entry_id)
        assert success is False
        assert failure_reason == FailureReason.ENTRY_NOT_FOUND

    def test_get_secure_entries_list_existing_user(self):
        """Test getting secure entries list for a user with data"""
        # Create user
        test_username = "test_user"
        test_secret_key_hash = "hashed_secret_key_123"
        test_secret_key_enc = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username, test_secret_key_hash, test_secret_key_enc)
        assert success is True
        assert failure_reason is None

        # Confirm user added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash

        # Create Secure Data
        entry_name_1 = "test_stored_password_title_1"
        website_1 = "test_encrypted_website_1"
        username_1 = "test_encrypted_username_1"
        password_1 = "test_encrypted_password_1"
        notes_1 = "test_encrypted_notes_1"
        success, failure_reason = Database.create_secure_data(test_username, entry_name_1, website_1, username_1, password_1, notes_1)
        assert success is True
        assert failure_reason is None
        entry_name_2 = "test_stored_password_title_2"
        website_2 = "test_encrypted_website_2"
        username_2 = "test_encrypted_username_2"
        password_2 = "test_encrypted_password_2"
        notes_2 = "test_encrypted_notes_2"
        success, failure_reason = Database.create_secure_data(test_username, entry_name_2, website_2, username_2, password_2, notes_2)
        assert success is True
        assert failure_reason is None

        # Confirm Secure Data entries added
        success, failure_reason, entries_list = Database.get_secure_entries_list(test_username)
        assert success is True
        assert failure_reason is None
        assert entries_list is not None
        assert len(entries_list) == 2
        entry_names = [name for name, _ in entries_list]
        assert entry_name_1 in entry_names
        assert entry_name_2 in entry_names

    def test_get_secure_entries_list_user_without_data(self):
        """Test getting secure entries list for a user with no secure data"""
        # Create user
        test_username = "test_user"
        test_secret_key_hash = "hashed_secret_key_123"
        test_secret_key_enc = "encrypted_secret_key_123"
        success, failure_reason = Database.create_user(test_username, test_secret_key_hash, test_secret_key_enc)
        assert success is True
        assert failure_reason is None

        # Confirm user added
        success, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(test_username)
        assert success is True
        assert failure_reason is None
        assert secret_key_hash == test_secret_key_hash
        success, failure_reason, entries_list = Database.get_secure_entries_list(test_username)
        assert success is True
        assert failure_reason is None
        assert entries_list == []

    def test_get_secure_entries_list_nonexistent_user(self):
        """Test getting secure entries list for a user that doesn't exist"""
        test_username = "test_user"
        success, failure_reason, entries_list = Database.get_secure_entries_list(test_username)
        assert success is False
        assert failure_reason == FailureReason.USERNAME_NOT_FOUND
        assert entries_list is None

    def test_get_secure_entry_data_nonexistent_entry(self):
        """Test retrieving data for a secure entry that doesn't exist"""
        fake_public_id = "secure_data_01"
        success, failure_reason, entry_data = Database.get_secure_entry_data(fake_public_id)
        assert success is False
        assert failure_reason == FailureReason.ENTRY_NOT_FOUND
        assert entry_data is None

    def test_create_registeration(self):
        """Test creating a registration successfully"""
        secret_key = "test_secret_key_hash"
        duration = timedelta(hours=1)

        success, failure_reason, public_id = Database.create_registeration(secret_key, duration)

        assert success is True
        assert failure_reason is None
        assert public_id is not None
        assert isinstance(public_id, str)
        assert len(public_id) > 0

    def test_fetch_registeration(self):
        """Test fetching a registration successfully"""
        secret_key = "test_secret_key_hash"
        duration = timedelta(hours=1)

        # Create registration
        success, failure_reason, public_id = Database.create_registeration(secret_key, duration)
        assert success is True
        assert failure_reason is None
        assert public_id is not None

        # Fetch registration
        success, failure_reason, fetched_secret_key = Database.fetch_registeration(public_id)

        assert success is True
        assert failure_reason is None
        assert fetched_secret_key == secret_key

    def test_fetch_registeration_nonexistent(self):
        """Test fetching a registration that doesn't exist"""
        fake_public_id = "nonexistent_registration_id"

        success, failure_reason, secret_key = Database.fetch_registeration(fake_public_id)

        assert success is False
        assert failure_reason == FailureReason.REGISTRATION_NOT_FOUND
        assert secret_key is None

    def test_fetch_registeration_expired(self):
        """Test fetching an expired registration"""
        secret_key = "test_secret_key_hash"
        duration = timedelta(hours=-1)

        # Create registration
        success, failure_reason, public_id = Database.create_registeration(secret_key, duration)
        assert success is True
        assert failure_reason is None
        assert public_id is not None

        # Try to fetch expired registration
        success, failure_reason, fetched_secret_key = Database.fetch_registeration(public_id)

        assert success is False
        assert failure_reason == FailureReason.REGISTRATION_NOT_FOUND
        assert fetched_secret_key is None

    def test_delete_registeration(self):
        """Test deleting a registration successfully"""
        secret_key = "test_secret_key_hash"
        duration = timedelta(hours=1)

        # Create registration
        success, failure_reason, public_id = Database.create_registeration(secret_key, duration)
        assert success is True
        assert failure_reason is None
        assert public_id is not None

        # Verify registration exists
        success, failure_reason, fetched_secret_key = Database.fetch_registeration(public_id)
        assert success is True
        assert failure_reason is None
        assert fetched_secret_key == secret_key

        # Delete registration
        success, failure_reason = Database.delete_registeration(public_id)

        assert success is True
        assert failure_reason is None

        # Verify registration is deleted
        success, failure_reason, fetched_secret_key = Database.fetch_registeration(public_id)
        assert success is False
        assert failure_reason == FailureReason.REGISTRATION_NOT_FOUND
        assert fetched_secret_key is None

    def test_delete_registeration_nonexistent(self):
        """Test deleting a registration that doesn't exist"""
        fake_public_id = "nonexistent_registration_id"

        success, failure_reason = Database.delete_registeration(fake_public_id)

        assert success is False
        assert failure_reason == FailureReason.REGISTRATION_NOT_FOUND

    def test_clean_registrations_with_expired_registrations(self):
        """Test cleaning registrations with expired ones present"""
        # Create multiple registrations with different expiry times
        secret_key_1 = "test_secret_key_1"
        secret_key_2 = "test_secret_key_2"
        secret_key_3 = "test_secret_key_3"

        # Create one that expires immediately
        success, failure_reason, public_id_1 = Database.create_registeration(secret_key_1, timedelta(hours=-1))
        assert success is True
        assert failure_reason is None
        assert public_id_1 is not None

        # Create one that expires in 1 hour
        success, failure_reason, public_id_2 = Database.create_registeration(secret_key_2, timedelta(hours=1))
        assert success is True
        assert failure_reason is None
        assert public_id_2 is not None

        # Create one that expires in 2 hours
        success, failure_reason, public_id_3 = Database.create_registeration(secret_key_3, timedelta(hours=2))
        assert success is True
        assert failure_reason is None
        assert public_id_3 is not None

        # Verify all registrations exist initially
        success, failure_reason, _ = Database.fetch_registeration(public_id_1)
        assert success is False
        assert failure_reason == FailureReason.REGISTRATION_NOT_FOUND

        success, failure_reason, _ = Database.fetch_registeration(public_id_2)
        assert success is True
        assert failure_reason is None

        success, failure_reason, _ = Database.fetch_registeration(public_id_3)
        assert success is True
        assert failure_reason is None

        # Clean registrations
        success, failure_reason = Database.clean_registrations()

        assert success is True
        assert failure_reason is None

        # Verify expired registration is cleaned and others remain
        success, failure_reason, _ = Database.fetch_registeration(public_id_2)
        assert success is True
        assert failure_reason is None

        success, failure_reason, _ = Database.fetch_registeration(public_id_3)
        assert success is True
        assert failure_reason is None

    def test_clean_registrations_with_no_expired_registrations(self):
        """Test cleaning registrations when none are expired"""
        # Create registrations that won't expire soon
        secret_key_1 = "test_secret_key_1"
        secret_key_2 = "test_secret_key_2"

        success, failure_reason, public_id_1 = Database.create_registeration(secret_key_1, timedelta(hours=1))
        assert success is True
        assert failure_reason is None
        assert public_id_1 is not None

        success, failure_reason, public_id_2 = Database.create_registeration(secret_key_2, timedelta(hours=2))
        assert success is True
        assert failure_reason is None
        assert public_id_2 is not None

        # Verify registrations exist
        success, failure_reason, _ = Database.fetch_registeration(public_id_1)
        assert success is True
        assert failure_reason is None

        success, failure_reason, _ = Database.fetch_registeration(public_id_2)
        assert success is True
        assert failure_reason is None

        # Clean registrations
        success, failure_reason = Database.clean_registrations()

        assert success is True
        assert failure_reason is None

        # Verify all registrations still exist
        success, failure_reason, _ = Database.fetch_registeration(public_id_1)
        assert success is True
        assert failure_reason is None

        success, failure_reason, _ = Database.fetch_registeration(public_id_2)
        assert success is True
        assert failure_reason is None

    def test_clean_registrations_with_mix_of_expiry(self):
        """Test cleaning registrations with a mix of expired and non-expired ones"""
        # Create registrations with different expiry times
        secret_key_expired_1 = "test_secret_key_expired_1"
        secret_key_expired_2 = "test_secret_key_expired_2"
        secret_key_valid_1 = "test_secret_key_valid_1"
        secret_key_valid_2 = "test_secret_key_valid_2"

        # Create expired registrations
        success, failure_reason, public_id_expired_1 = Database.create_registeration(secret_key_expired_1, timedelta(hours=-1))
        assert success is True
        assert failure_reason is None
        assert public_id_expired_1 is not None

        success, failure_reason, public_id_expired_2 = Database.create_registeration(secret_key_expired_2, timedelta(hours=-1))
        assert success is True
        assert failure_reason is None
        assert public_id_expired_2 is not None

        # Create valid registrations
        success, failure_reason, public_id_valid_1 = Database.create_registeration(secret_key_valid_1, timedelta(hours=1))
        assert success is True
        assert failure_reason is None
        assert public_id_valid_1 is not None

        success, failure_reason, public_id_valid_2 = Database.create_registeration(secret_key_valid_2, timedelta(hours=2))
        assert success is True
        assert failure_reason is None
        assert public_id_valid_2 is not None

        # Clean registrations
        success, failure_reason = Database.clean_registrations()

        assert success is True
        assert failure_reason is None

        # Verify expired registrations are cleaned
        success, failure_reason, _ = Database.fetch_registeration(public_id_expired_1)
        assert success is False
        assert failure_reason == FailureReason.REGISTRATION_NOT_FOUND

        success, failure_reason, _ = Database.fetch_registeration(public_id_expired_2)
        assert success is False
        assert failure_reason == FailureReason.REGISTRATION_NOT_FOUND

        # Verify valid registrations remain
        success, failure_reason, _ = Database.fetch_registeration(public_id_valid_1)
        assert success is True
        assert failure_reason is None

        success, failure_reason, _ = Database.fetch_registeration(public_id_valid_2)
        assert success is True
        assert failure_reason is None


if __name__ == '__main__':
    pytest.main(['-v', __file__])
