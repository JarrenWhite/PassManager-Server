import os
import sys
import pytest
import tempfile
import shutil
import time
import gc

from sqlalchemy import text

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
        self._safe_remove_database()
        DatabaseUtils.database_initialised = False
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
        """Test that get_db_session opens a session (cannot verify close)"""
        with DatabaseUtils.get_db_session() as session:
            # Check that session exists
            result = session.execute(text("SELECT 1")).scalar()
            assert result == 1

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
        DatabaseUtils.database_initialised = False
        assert DatabaseUtils.database_initialised is False
        assert not os.path.exists(self.test_db_path)

        # Test that initialization returns True on first run
        result = DatabaseUtils.init_database()
        assert result is True
        assert DatabaseUtils.database_initialised is True

        # Verify that the database file & tables were created
        assert os.path.exists(self.test_db_path)
        with DatabaseUtils.get_db_session() as session:
            tables = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
            table_names = [table[0] for table in tables]
            assert 'user' in table_names
            assert 'session' in table_names
            assert 'encrypted' in table_names

    def test_failed_database_initialisation(self):
        """Test that databse initialisation fails if it's already been run"""
        # Ensure database is already initialized
        assert DatabaseUtils.database_initialised is True
        assert os.path.exists(self.test_db_path)

        # Create some test data to verify it's the same database after failed init
        test_username = "test_user_for_same_db_check"
        test_password_hash = "test_hash_123"

        # Insert test data into the existing database
        with DatabaseUtils.get_db_session() as session:
            from database.database_models import User
            test_user = User(username=test_username, password_hash=test_password_hash)
            session.add(test_user)
            session.commit()

            # Verify the test data was inserted
            user_count_before = session.execute(text("SELECT COUNT(*) FROM user")).scalar()
            assert user_count_before is not None
            assert user_count_before >= 1

        # Test that initialization returns False when already initialized
        result = DatabaseUtils.init_database()
        assert result is False
        assert DatabaseUtils.database_initialised is True

        # Verify database file still exists and is functional
        assert os.path.exists(self.test_db_path)
        with DatabaseUtils.get_db_session() as session:
            result = session.execute(text("SELECT 1")).scalar()
            assert result == 1

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
        test_password_hash = "hashed_password_123"
        result = DatabaseUtils.create_user(test_username, test_password_hash)

        # Confirm user was added correctly
        assert result is True
        assert DatabaseUtils.get_user_password_hash(test_username) == test_password_hash

    def test_create_user_duplicate_username(self):
        """Test creating a user with a username that already exists"""
        # Create user
        test_username = "test_user"
        test_password_hash = "hashed_password_123"
        result = DatabaseUtils.create_user(test_username, test_password_hash)

        # Confirm user was added correctly
        assert result is True
        assert DatabaseUtils.get_user_password_hash(test_username) == test_password_hash

        # Create another user with the same username
        second_test_password_hash = "new_hashed_password_456"
        result = DatabaseUtils.create_user(test_username, second_test_password_hash)

        # Confirm second user was not added
        assert result is False
        assert DatabaseUtils.get_user_password_hash(test_username) == test_password_hash

    def test_delete_user(self):
        """Test user deletion"""
        # Create user
        test_username = "test_user"
        test_password_hash = "hashed_password_123"
        result = DatabaseUtils.create_user(test_username, test_password_hash)

        # Confirm user was added correctly
        assert result is True
        assert DatabaseUtils.get_user_password_hash(test_username) == test_password_hash

        # Delete user
        result = DatabaseUtils.delete_user(test_username)

        # Confirm user was deleted correctly
        assert result is True
        assert DatabaseUtils.get_user_password_hash(test_username) is None

    def test_delete_user_cascades_to_sessions(self):
        """Test that deleting a user also removes their sessions"""
        pass

    def test_delete_user_cascades_to_secure_data(self):
        """Test that deleting a user also removes their secure data"""
        pass

    def test_get_user_password_hash_existing_user(self):
        """Test retrieving password hash for an existing user"""
        pass

    def test_get_user_password_hash_nonexistent_user(self):
        """Test retrieving password hash for a user that doesn't exist"""
        pass

    def test_create_session(self):
        """Test session creation"""
        pass

    def test_create_session_nonexistent_user(self):
        """Test creating a session for a user that doesn't exist"""
        pass

    def test_check_session_token_valid_token(self):
        """Test checking a valid, non-expired session token"""
        pass

    def test_check_session_token_expired_token(self):
        """Test checking an expired session token (should delete and return None)"""
        pass

    def test_check_session_token_nonexistent_token(self):
        """Test checking a token that doesn't exist"""
        pass

    def test__delete_session(self):
        """Test single session deletion"""
        pass

    def test_delete_session_nonexistent_token(self):
        """Test deleting a session token that doesn't exist"""
        pass

    def test_delete_all_sessions(self):
        """Test deleting all of a user's sessions"""
        pass

    def test_delete_all_sessions_nonexistent_user(self):
        """Test deleting all sessions for a user that doesn't exist"""
        pass

    def test_clean_sessions_with_expired_sessions(self):
        """Test cleaning sessions when there are expired sessions to remove"""
        pass

    def test_clean_sessions_with_no_expired_sessions(self):
        """Test cleaning sessions when there are no expired sessions"""
        pass

    def test_clean_sessions_with_mix_of_expiry(self):
        """Test cleaning sessions when there are a mix of expired sessions"""
        pass

    def test_create_secure_data(self):
        """Test secure data creation"""
        pass

    def test_create_secure_data_nonexistent_user(self):
        """Test creating secure data for a user that doesn't exist"""
        pass

    def test_edit_secure_data(self):
        """Test secure data editing"""
        pass

    def test_edit_secure_data_partial_update(self):
        """Test editing secure data with only some fields updated"""
        pass

    def test_edit_secure_data_nonexistent_entry(self):
        """Test editing a secure entry that doesn't exist"""
        pass

    def test_delete_secure_data(self):
        """Test secure data deletion"""
        pass

    def test_get_secure_entries_list_existing_user(self):
        """Test getting secure entries list for a user with data"""
        pass

    def test_get_secure_entries_list_user_without_data(self):
        """Test getting secure entries list for a user with no secure data"""
        pass

    def test_get_secure_entries_list_nonexistent_user(self):
        """Test getting secure entries list for a user that doesn't exist"""
        pass

    def test_get_secure_entry_data_existing_entry(self):
        """Test retrieving data for an existing secure entry"""
        pass

    def test_get_secure_entry_data_nonexistent_entry(self):
        """Test retrieving data for a secure entry that doesn't exist"""
        pass

    def test_shared_database_details(self):
        """Test that an update made in one instance of utils is seen in another"""
        pass

    def test_database_session_rollback_on_exception(self):
        """Test that database session properly rolls back on exception"""
        pass

    def test_database_session_commit_on_success(self):
        """Test that database session properly commits on successful operations"""
        pass


if __name__ == '__main__':
    pytest.main(['-v', __file__])
