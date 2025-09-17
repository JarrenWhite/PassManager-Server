import os
import sys
import pytest
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_models import Base, User, AuthEphemeral, LoginSession, SecureData

class TestDatabaseUserModel():
    """Test cases for the User database model"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        yield

        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_can_create_user(self):
        """Should be able to create new user with minimal fields"""
        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        self.session.add(user)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == "fake_hash"

    def test_all_required_fields_are_required(self):
        """Should require all fields in order to create object"""
        user = User(
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        self.session.add(user)

        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        users = self.session.query(User).all()
        assert len(users) == 0

        user = User(
            username_hash="fake_hash",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        self.session.add(user)

        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        users = self.session.query(User).all()
        assert len(users) == 0

        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            master_key_salt="fake_master_key_salt"
        )
        self.session.add(user)

        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        users = self.session.query(User).all()
        assert len(users) == 0

        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
        )
        self.session.add(user)

        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        users = self.session.query(User).all()
        assert len(users) == 0

    def test_can_use_optional_fields(self):
        """Should be able to create new user with optional fields"""
        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            new_srp_salt="new_srp_salt",
            new_srp_verifier="new_srp_verifier",
            new_master_key_salt="new_master_key_salt"
        )
        self.session.add(user)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == "fake_hash"

    def test_username_uniqueness(self):
        """Should enforce unique usernames"""
        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        self.session.add(user)
        self.session.commit()

        user2 = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt_2",
            srp_verifier="fake_srp_verifier_2",
            master_key_salt="fake_master_key_salt_2"
        )
        self.session.add(user2)

        try:
            self.session.commit()
            raise AssertionError("Expected uniqueness constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("unique constraint failed" in error_message or "integrity" in error_message), f"Expected uniqueness constraint violation, got: {error_message}"
            self.session.rollback()

        users = self.session.query(User).all()
        assert len(users) == 1
        assert users[0].id == user.id

    def test_all_fields_correct(self):
        """Should store all fields correctly"""
        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            new_srp_salt="new_srp_salt",
            new_srp_verifier="new_srp_verifier",
            new_master_key_salt="new_master_key_salt"
        )
        self.session.add(user)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.id == user.id
        assert db_user.username_hash == "fake_hash"
        assert db_user.srp_salt == "fake_srp_salt"
        assert db_user.srp_verifier == "fake_srp_verifier"
        assert db_user.master_key_salt == "fake_master_key_salt"
        assert db_user.new_srp_salt == "new_srp_salt"
        assert db_user.new_srp_verifier == "new_srp_verifier"
        assert db_user.new_master_key_salt == "new_master_key_salt"

    def test_can_edit_data(self):
        """Should be possible to adjust all fields"""
        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        self.session.add(user)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.id == user.id
        assert db_user.username_hash == "fake_hash"

        user.username_hash="new_fake_hash"
        user.srp_salt="new_fake_srp_salt"
        user.srp_verifier="new_fake_srp_verifier"
        user.master_key_salt="new_fake_master_key_salt"
        self.session.commit()

        users = self.session.query(User).filter_by(username_hash="fake_hash").all()
        assert len(users) == 0

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.id == user.id
        assert db_user.username_hash == "new_fake_hash"
        assert db_user.srp_salt == "new_fake_srp_salt"
        assert db_user.srp_verifier == "new_fake_srp_verifier"
        assert db_user.master_key_salt == "new_fake_master_key_salt"

    def test_can_add_optional_fields_late(self):
        """Should be able to add optional fields at a later point"""
        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        self.session.add(user)
        self.session.commit()

        user.new_srp_salt="new_srp_salt"
        user.new_srp_verifier="new_srp_verifier"
        user.new_master_key_salt="new_master_key_salt"
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.id == user.id
        assert db_user.new_srp_salt == "new_srp_salt"
        assert db_user.new_srp_verifier == "new_srp_verifier"
        assert db_user.new_master_key_salt == "new_master_key_salt"

    def test_cannot_delete_required_fields(self):
        """Should not be possible to delete required fields"""
        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        self.session.add(user)
        self.session.commit()

        user.username_hash=None # type: ignore
        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        user.srp_salt=None # type: ignore
        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        user.srp_verifier=None # type: ignore
        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        user.master_key_salt=None # type: ignore
        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == "fake_hash"
        assert db_user.srp_salt == "fake_srp_salt"
        assert db_user.srp_verifier == "fake_srp_verifier"
        assert db_user.master_key_salt == "fake_master_key_salt"

    def test_can_delete_completed_optional_fields(self):
        """Should be possible to delete optional fields"""
        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            new_srp_salt="new_srp_salt",
            new_srp_verifier="new_srp_verifier",
            new_master_key_salt="new_master_key_salt"
        )
        self.session.add(user)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None

        user.new_srp_salt = None
        user.new_srp_verifier = None
        user.new_master_key_salt = None

        assert db_user.new_srp_salt == None
        assert db_user.new_srp_verifier == None
        assert db_user.new_master_key_salt == None

    def test_can_delete_entry(self):
        """Should be possible to delete entry"""
        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        self.session.add(user)
        self.session.commit()

        users = self.session.query(User).all()
        assert len(users) == 1

        self.session.delete(user)
        self.session.commit()

        users = self.session.query(User).all()
        assert len(users) == 0


class TestDatabaseAuthEphemeralModel():
    """Test cases for the Auth Ephemeral database model"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        yield

        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_can_create_ephemeral(self):
        """Should be able to create AuthEphemeral with minimal fields"""
        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            ephemeral_b="fake_ephemeral_bytes",
            expires_at=expiry
        )
        self.session.add(ephemeral)
        self.session.commit()

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert db_ephemeral.ephemeral_b == "fake_ephemeral_bytes"

    def test_all_required_fields_are_required(self):
        """Should require all fields in order to create object"""
        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            expires_at=expiry
        )
        self.session.add(ephemeral)

        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        ephemerals = self.session.query(AuthEphemeral).all()
        assert len(ephemerals) == 0

        ephemeral = AuthEphemeral(
            ephemeral_b="fake_ephemeral_bytes",
            expires_at=expiry
        )
        self.session.add(ephemeral)

        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        ephemerals = self.session.query(AuthEphemeral).all()
        assert len(ephemerals) == 0

        ephemeral = AuthEphemeral(
            ephemeral_b="fake_ephemeral_bytes",
            user_id=123456,
        )
        self.session.add(ephemeral)

        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        ephemerals = self.session.query(AuthEphemeral).all()
        assert len(ephemerals) == 0

    def test_can_use_optional_fields(self):
        """Should be able to create new AuthEphemeral with optional fields"""
        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            ephemeral_b="fake_ephemeral_bytes",
            expires_at=expiry,
            password_change=True
        )
        self.session.add(ephemeral)
        self.session.commit()

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert db_ephemeral.ephemeral_b == "fake_ephemeral_bytes"

    def test_public_id_created(self):
        """Should create a public ID of length 32"""
        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            ephemeral_b="fake_ephemeral_bytes",
            expires_at=expiry
        )
        self.session.add(ephemeral)
        self.session.commit()

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert db_ephemeral.public_id is not None
        assert len(db_ephemeral.public_id) == 32

    def test_all_fields_correct(self):
        """Should store all fields correctly"""
        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            ephemeral_b="fake_ephemeral_bytes",
            expires_at=expiry,
            password_change=True
        )
        self.session.add(ephemeral)
        self.session.commit()

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert db_ephemeral.ephemeral_b == "fake_ephemeral_bytes"
        assert db_ephemeral.user_id == 123456
        assert db_ephemeral.expires_at == expiry
        assert db_ephemeral.public_id == ephemeral.public_id
        assert db_ephemeral.password_change == True

    def test_can_delete_entry(self):
        """Should be possible to delete entry"""
        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            ephemeral_b="fake_ephemeral_bytes",
            expires_at=expiry,
            password_change=True
        )
        self.session.add(ephemeral)
        self.session.commit()

        users = self.session.query(AuthEphemeral).all()
        assert len(users) == 1

        self.session.delete(ephemeral)
        self.session.commit()

        users = self.session.query(AuthEphemeral).all()
        assert len(users) == 0


class TestLoginSessionModel():
    """Test cases for the Login Session database model"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        yield

        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_can_create_session(self):
        """Should be able to create LoginSession with minimal fields"""
        last_used = datetime.now()
        login = LoginSession(
            user_id=123456,
            session_key="fake_session_key",
            request_count=0,
            last_used=last_used
        )
        self.session.add(login)
        self.session.commit()

        db_login = self.session.query(LoginSession).first()
        assert db_login is not None
        assert db_login.session_key == "fake_session_key"

    def test_all_required_fields_are_required(self):
        """Should require all fields in order to create object"""
        last_used = datetime.now()
        login = LoginSession(
            session_key="fake_session_key",
            request_count=0,
            last_used=last_used
        )
        self.session.add(login)

        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        login = LoginSession(
            user_id=123456,
            request_count=0,
            last_used=last_used
        )
        self.session.add(login)

        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        login = LoginSession(
            user_id=123456,
            session_key="fake_session_key",
            last_used=last_used
        )
        self.session.add(login)

        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        login = LoginSession(
            user_id=123456,
            session_key="fake_session_key",
            request_count=0
        )
        self.session.add(login)

        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        ephemerals = self.session.query(LoginSession).all()
        assert len(ephemerals) == 0

    def test_can_use_optional_fields(self):
        """Should be able to create new AuthEphemeral with optional fields"""
        last_used = datetime.now()
        expiry = datetime.now() + timedelta(hours=1)
        login = LoginSession(
            user_id=123456,
            session_key="fake_session_key",
            request_count=0,
            last_used=last_used,
            maximum_requests=5,
            expiry_time=expiry,
            password_change=True
        )
        self.session.add(login)
        self.session.commit()

        db_login = self.session.query(LoginSession).first()
        assert db_login is not None
        assert db_login.session_key == "fake_session_key"

    def test_public_id_created(self):
        """Should create a public ID of length 32"""
        last_used = datetime.now()
        login = LoginSession(
            user_id=123456,
            session_key="fake_session_key",
            request_count=0,
            last_used=last_used
        )
        self.session.add(login)
        self.session.commit()

        db_login = self.session.query(LoginSession).first()
        assert db_login is not None
        assert db_login.public_id is not None
        assert len(db_login.public_id) == 32

    def test_all_fields_correct(self):
        """Should store all fields correctly"""
        last_used = datetime.now()
        expiry = datetime.now() + timedelta(hours=1)
        login = LoginSession(
            user_id=123456,
            session_key="fake_session_key",
            request_count=0,
            last_used=last_used,
            maximum_requests=5,
            expiry_time=expiry,
            password_change=True
        )
        self.session.add(login)
        self.session.commit()

        db_login = self.session.query(LoginSession).first()
        assert db_login is not None
        assert db_login.user_id == 123456
        assert db_login.session_key == "fake_session_key"
        assert db_login.request_count == 0
        assert db_login.last_used == last_used
        assert db_login.maximum_requests == 5
        assert db_login.expiry_time == expiry
        assert db_login.password_change == True
        assert db_login.public_id == login.public_id

    def test_can_delete_entry(self):
        """Should be possible to delete entry"""
        last_used = datetime.now()
        login = LoginSession(
            user_id=123456,
            session_key="fake_session_key",
            request_count=0,
            last_used=last_used
        )
        self.session.add(login)
        self.session.commit()

        logins = self.session.query(LoginSession).all()
        assert len(logins) == 1

        self.session.delete(login)
        self.session.commit()

        logins = self.session.query(LoginSession).all()
        assert len(logins) == 0


class TestSecureDataModels():
    """Test cases for the Secure Data database model"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        yield

        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_can_create_data(self):
        """Should be able to create SecureData with minimal fields"""
        data = SecureData(
            user_id=123456,
            entry_name="fake_secure_data_name",
            entry_data="fake_secure_data_entry"
        )
        self.session.add(data)
        self.session.commit()

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.entry_name == "fake_secure_data_name"

    def test_all_required_fields_are_required(self):
        """Should require all fields in order to create object"""
        data = SecureData(
            entry_name="fake_secure_data_name",
            entry_data="fake_secure_data_entry"
        )
        self.session.add(data)

        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        data = SecureData(
            user_id=123456,
            entry_data="fake_secure_data_entry"
        )
        self.session.add(data)

        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        data = SecureData(
            user_id=123456,
            entry_name="fake_secure_data_name"
        )
        self.session.add(data)

        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

    def test_can_use_optional_fields(self):
        """Should be able to create new AuthEphemeral with optional fields"""
        data = SecureData(
            user_id=123456,
            entry_name="fake_secure_data_name",
            entry_data="fake_secure_data_entry",
            new_entry_name="new_fake_secure_data_name",
            new_entry_data="new_fake_secure_data_entry"
        )
        self.session.add(data)
        self.session.commit()

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.entry_name == "fake_secure_data_name"

    def test_public_id_created(self):
        """Should create a public ID of length 32"""
        data = SecureData(
            user_id=123456,
            entry_name="fake_secure_data_name",
            entry_data="fake_secure_data_entry"
        )
        self.session.add(data)
        self.session.commit()

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.public_id is not None
        assert len(db_data.public_id) == 32


if __name__ == '__main__':
    pytest.main(['-v', __file__])
