import os
import sys
import pytest
from datetime import datetime, timedelta

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

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
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )
        self.session.add(user)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == b'fake_hash'

    def test_all_required_fields_are_required(self):
        """Should require all fields in order to create object"""
        user = User(
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )
        self.session.add(user)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        users = self.session.query(User).all()
        assert len(users) == 0

        user = User(
            username_hash=b'fake_hash',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )
        self.session.add(user)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        users = self.session.query(User).all()
        assert len(users) == 0

        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )
        self.session.add(user)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        users = self.session.query(User).all()
        assert len(users) == 0

        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            password_change=False
        )
        self.session.add(user)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        users = self.session.query(User).all()
        assert len(users) == 0

        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt'
        )
        self.session.add(user)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        users = self.session.query(User).all()
        assert len(users) == 0

    def test_can_use_optional_fields(self):
        """Should be able to create new user with optional fields"""
        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False,
            new_srp_salt=b'new_srp_salt',
            new_srp_verifier=b'new_srp_verifier',
            new_master_key_salt=b'new_master_key_salt'
        )
        self.session.add(user)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == b'fake_hash'

    def test_username_uniqueness(self):
        """Should enforce unique usernames"""
        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )
        self.session.add(user)
        self.session.commit()

        user2 = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt_2',
            srp_verifier=b'fake_srp_verifier_2',
            master_key_salt=b'fake_master_key_salt_2',
            password_change=False
        )
        self.session.add(user2)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "unique constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        users = self.session.query(User).all()
        assert len(users) == 1
        assert users[0].id == user.id

    def test_all_fields_correct(self):
        """Should store all fields correctly"""
        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False,
            new_srp_salt=b'new_srp_salt',
            new_srp_verifier=b'new_srp_verifier',
            new_master_key_salt=b'new_master_key_salt'
        )
        self.session.add(user)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.id == user.id
        assert db_user.username_hash == b'fake_hash'
        assert db_user.srp_salt == b'fake_srp_salt'
        assert db_user.srp_verifier == b'fake_srp_verifier'
        assert db_user.master_key_salt == b'fake_master_key_salt'
        assert db_user.password_change == False
        assert db_user.new_srp_salt == b'new_srp_salt'
        assert db_user.new_srp_verifier == b'new_srp_verifier'
        assert db_user.new_master_key_salt == b'new_master_key_salt'

    def test_can_edit_data(self):
        """Should be possible to adjust all fields"""
        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )
        self.session.add(user)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.id == user.id
        assert db_user.username_hash == b'fake_hash'

        user.username_hash=b'new_fake_hash'
        user.srp_salt=b'new_fake_srp_salt'
        user.srp_verifier=b'new_fake_srp_verifier'
        user.master_key_salt=b'new_fake_master_key_salt'
        user.password_change=True
        self.session.commit()

        users = self.session.query(User).filter_by(username_hash=b'fake_hash').all()
        assert len(users) == 0

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.id == user.id
        assert db_user.username_hash == b'new_fake_hash'
        assert db_user.srp_salt == b'new_fake_srp_salt'
        assert db_user.srp_verifier == b'new_fake_srp_verifier'
        assert db_user.master_key_salt == b'new_fake_master_key_salt'
        assert db_user.password_change == True

    def test_can_add_optional_fields_late(self):
        """Should be able to add optional fields at a later point"""
        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )
        self.session.add(user)
        self.session.commit()

        user.new_srp_salt=b'new_srp_salt'
        user.new_srp_verifier=b'new_srp_verifier'
        user.new_master_key_salt=b'new_master_key_salt'
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.id == user.id
        assert db_user.new_srp_salt == b'new_srp_salt'
        assert db_user.new_srp_verifier == b'new_srp_verifier'
        assert db_user.new_master_key_salt == b'new_master_key_salt'

    def test_cannot_delete_required_fields(self):
        """Should not be possible to delete required fields"""
        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )
        self.session.add(user)
        self.session.commit()

        user.username_hash=None # type: ignore
        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        user.srp_salt=None # type: ignore
        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        user.srp_verifier=None # type: ignore
        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        user.master_key_salt=None # type: ignore
        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        user.password_change=None # type: ignore
        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == b'fake_hash'
        assert db_user.srp_salt == b'fake_srp_salt'
        assert db_user.srp_verifier == b'fake_srp_verifier'
        assert db_user.master_key_salt == b'fake_master_key_salt'

    def test_can_delete_completed_optional_fields(self):
        """Should be possible to delete optional fields"""
        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False,
            new_srp_salt=b'new_srp_salt',
            new_srp_verifier=b'new_srp_verifier',
            new_master_key_salt=b'new_master_key_salt'
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
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
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
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=False
        )
        self.session.add(ephemeral)
        self.session.commit()

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert db_ephemeral.eph_public_b == b'fake_eph_public_b'

    def test_all_required_fields_are_required(self):
        """Should require all fields in order to create object"""
        ephemerals = self.session.query(AuthEphemeral).all()
        assert len(ephemerals) == 0

        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=False
        )
        self.session.add(ephemeral)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        ephemerals = self.session.query(AuthEphemeral).all()
        assert len(ephemerals) == 0

        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=False
        )
        self.session.add(ephemeral)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        ephemerals = self.session.query(AuthEphemeral).all()
        assert len(ephemerals) == 0

        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            eph_private_b=b'fake_eph_private_b',
            expiry_time=expiry,
            password_change=False
        )
        self.session.add(ephemeral)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        ephemerals = self.session.query(AuthEphemeral).all()
        assert len(ephemerals) == 0

        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            password_change=False
        )
        self.session.add(ephemeral)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        ephemerals = self.session.query(AuthEphemeral).all()
        assert len(ephemerals) == 0

        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry
        )
        self.session.add(ephemeral)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        ephemerals = self.session.query(AuthEphemeral).all()
        assert len(ephemerals) == 0

    def test_public_id_created(self):
        """Should create a public ID of length 32"""
        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=False
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
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=True
        )
        self.session.add(ephemeral)
        self.session.commit()

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert db_ephemeral.eph_private_b == b'fake_eph_private_b'
        assert db_ephemeral.eph_public_b == b'fake_eph_public_b'
        assert db_ephemeral.user_id == 123456
        assert db_ephemeral.expiry_time == expiry
        assert db_ephemeral.public_id == ephemeral.public_id
        assert db_ephemeral.password_change == True

    def test_can_delete_entry(self):
        """Should be possible to delete entry"""
        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
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
            session_key=b'fake_session_key',
            request_count=0,
            last_used=last_used,
            password_change=False
        )
        self.session.add(login)
        self.session.commit()

        db_login = self.session.query(LoginSession).first()
        assert db_login is not None
        assert db_login.session_key == b'fake_session_key'

    def test_all_required_fields_are_required(self):
        """Should require all fields in order to create object"""
        last_used = datetime.now()
        login = LoginSession(
            session_key=b'fake_session_key',
            request_count=0,
            last_used=last_used,
            password_change=False
        )
        self.session.add(login)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        login = LoginSession(
            user_id=123456,
            request_count=0,
            last_used=last_used,
            password_change=False
        )
        self.session.add(login)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        login = LoginSession(
            user_id=123456,
            session_key=b'fake_session_key',
            last_used=last_used,
            password_change=False
        )
        self.session.add(login)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        login = LoginSession(
            user_id=123456,
            session_key=b'fake_session_key',
            request_count=0,
            password_change=False
        )
        self.session.add(login)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        ephemerals = self.session.query(LoginSession).all()
        assert len(ephemerals) == 0

        login = LoginSession(
            user_id=123456,
            session_key=b'fake_session_key',
            request_count=0,
            last_used=last_used
        )
        self.session.add(login)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        ephemerals = self.session.query(LoginSession).all()
        assert len(ephemerals) == 0

    def test_can_use_optional_fields(self):
        """Should be able to create new AuthEphemeral with optional fields"""
        last_used = datetime.now()
        expiry = datetime.now() + timedelta(hours=1)
        login = LoginSession(
            user_id=123456,
            session_key=b'fake_session_key',
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
        assert db_login.session_key == b'fake_session_key'

    def test_session_key_uniqueness(self):
        """Should enforce unique session key"""
        last_used = datetime.now()
        login = LoginSession(
            user_id=123456,
            session_key=b'fake_session_key',
            request_count=0,
            last_used=last_used,
            password_change=False
        )
        self.session.add(login)
        self.session.commit()

        last_used_2 = datetime.now() + timedelta(hours=-1)
        login2 = LoginSession(
            user_id=1234567,
            session_key=b'fake_session_key',
            request_count=0,
            last_used=last_used_2,
            password_change=False
        )
        self.session.add(login2)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "unique constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        logins = self.session.query(LoginSession).all()
        assert len(logins) == 1
        assert logins[0].id == login.id

    def test_public_id_created(self):
        """Should create a public ID of length 32"""
        last_used = datetime.now()
        login = LoginSession(
            user_id=123456,
            session_key=b'fake_session_key',
            request_count=0,
            last_used=last_used,
            password_change=False
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
            session_key=b'fake_session_key',
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
        assert db_login.session_key == b'fake_session_key'
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
            session_key=b'fake_session_key',
            request_count=0,
            last_used=last_used,
            password_change=False
        )
        self.session.add(login)
        self.session.commit()

        logins = self.session.query(LoginSession).all()
        assert len(logins) == 1

        self.session.delete(login)
        self.session.commit()

        logins = self.session.query(LoginSession).all()
        assert len(logins) == 0


class TestSecureDataModel():
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
            entry_name=b'fake_secure_data_name',
            entry_data=b'fake_secure_data_entry'
        )
        self.session.add(data)
        self.session.commit()

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.entry_name == b'fake_secure_data_name'

    def test_all_required_fields_are_required(self):
        """Should require all fields in order to create object"""
        data = SecureData(
            entry_name=b'fake_secure_data_name',
            entry_data=b'fake_secure_data_entry'
        )
        self.session.add(data)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        data = SecureData(
            user_id=123456,
            entry_data=b'fake_secure_data_entry'
        )
        self.session.add(data)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

        data = SecureData(
            user_id=123456,
            entry_name=b'fake_secure_data_name'
        )
        self.session.add(data)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "not null constraint failed" in error_message and "integrity" in error_message
        self.session.rollback()

    def test_can_use_optional_fields(self):
        """Should be able to create new AuthEphemeral with optional fields"""
        data = SecureData(
            user_id=123456,
            entry_name=b'fake_secure_data_name',
            entry_data=b'fake_secure_data_entry',
            new_entry_name=b'new_fake_secure_data_name',
            new_entry_data=b'new_fake_secure_data_entry'
        )
        self.session.add(data)
        self.session.commit()

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.entry_name == b'fake_secure_data_name'

    def test_public_id_created(self):
        """Should create a public ID of length 32"""
        data = SecureData(
            user_id=123456,
            entry_name=b'fake_secure_data_name',
            entry_data=b'fake_secure_data_entry'
        )
        self.session.add(data)
        self.session.commit()

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.public_id is not None
        assert len(db_data.public_id) == 32

    def test_all_fields_correct(self):
        """Should store all fields correctly"""
        data = SecureData(
            user_id=123456,
            entry_name=b'fake_secure_data_name',
            entry_data=b'fake_secure_data_entry',
            new_entry_name=b'new_fake_secure_data_name',
            new_entry_data=b'new_fake_secure_data_entry'
        )
        self.session.add(data)
        self.session.commit()

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.user_id == 123456
        assert db_data.entry_name == b'fake_secure_data_name'
        assert db_data.entry_data == b'fake_secure_data_entry'
        assert db_data.new_entry_name == b'new_fake_secure_data_name'
        assert db_data.new_entry_data == b'new_fake_secure_data_entry'
        assert db_data.public_id == data.public_id

    def test_can_delete_entry(self):
        """Should be possible to delete entry"""
        data = SecureData(
            user_id=123456,
            entry_name=b'fake_secure_data_name',
            entry_data=b'fake_secure_data_entry'
        )
        self.session.add(data)
        self.session.commit()

        data_entries = self.session.query(SecureData).all()
        assert len(data_entries) == 1

        self.session.delete(data)
        self.session.commit()

        data_entries = self.session.query(SecureData).all()
        assert len(data_entries) == 0


class TestDatabaseRelationships():
    """Test cases for the relationships between database models"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)

        with self.engine.connect() as conn:
            conn.execute(text("PRAGMA foreign_keys=ON"))

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        yield

        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_existing_user_id_required(self):
        """Should require existing user ID to create models"""
        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=False
        )
        self.session.add(ephemeral)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "foreign key" in error_message and "integrity" in error_message
        self.session.rollback()

        last_used = datetime.now()
        login = LoginSession(
            user_id=123456,
            session_key=b'fake_session_key',
            request_count=0,
            last_used=last_used,
            password_change=False
        )
        self.session.add(login)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "foreign key" in error_message and "integrity" in error_message
        self.session.rollback()

        data = SecureData(
            user_id=123456,
            entry_name=b'fake_secure_data_name',
            entry_data=b'fake_secure_data_entry'
        )
        self.session.add(data)

        with pytest.raises(IntegrityError) as exc_info:
            self.session.commit()
        error_message = str(exc_info.value).lower()
        assert "foreign key" in error_message and "integrity" in error_message
        self.session.rollback()

    def test_existing_user_id_functions(self):
        """Should be possible to add models with existing user id"""
        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )
        self.session.add(user)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == b'fake_hash'

        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=user.id,
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=False
        )
        self.session.add(ephemeral)
        self.session.commit()

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert db_ephemeral.eph_public_b == b'fake_eph_public_b'

        last_used = datetime.now()
        login = LoginSession(
            user_id=user.id,
            session_key=b'fake_session_key',
            request_count=0,
            last_used=last_used,
            password_change=False
        )
        self.session.add(login)
        self.session.commit()

        db_login = self.session.query(LoginSession).first()
        assert db_login is not None
        assert db_login.session_key == b'fake_session_key'

        data = SecureData(
            user_id=user.id,
            entry_name=b'fake_secure_data_name',
            entry_data=b'fake_secure_data_entry'
        )
        self.session.add(data)
        self.session.commit()

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.entry_name == b'fake_secure_data_name'

    def test_user_ephemeral_relationship(self):
        """Should be a relationship between user and all user's auth ephemerals"""
        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )
        self.session.add(user)
        self.session.commit()

        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user=user,
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=False
        )
        self.session.add(ephemeral)
        self.session.commit()

        expiry2 = datetime.now() + timedelta(hours=2)
        ephemeral2 = AuthEphemeral(
            user=user,
            eph_private_b=b'fake_eph_private_b_2',
            eph_public_b=b'fake_eph_public_b_2',
            expiry_time=expiry2,
            password_change=False
        )
        self.session.add(ephemeral2)
        self.session.commit()

        assert len(user.auth_ephemerals) == 2
        assert ephemeral in user.auth_ephemerals
        assert ephemeral2 in user.auth_ephemerals
        assert ephemeral.user_id == user.id
        assert ephemeral2.user_id == user.id

    def test_user_login_relationship(self):
        """Should be a relationship between user and all user's login sessions"""
        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )
        self.session.add(user)
        self.session.commit()

        last_used = datetime.now()
        login = LoginSession(
            user=user,
            session_key=b'fake_session_key',
            request_count=0,
            last_used=last_used,
            password_change=False
        )
        self.session.add(login)
        self.session.commit()

        last_used = datetime.now() + timedelta(hours=1)
        login2 = LoginSession(
            user=user,
            session_key=b'fake_session_key_2',
            request_count=0,
            last_used=last_used,
            password_change=False
        )
        self.session.add(login2)
        self.session.commit()

        assert len(user.login_sessions) == 2
        assert login in user.login_sessions
        assert login2 in user.login_sessions
        assert login.user_id == user.id
        assert login2.user_id == user.id

    def test_user_data_relationship(self):
        """Should be a relationship between user and all user's login sessions"""
        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )
        self.session.add(user)
        self.session.commit()

        data = SecureData(
            user=user,
            entry_name=b'fake_secure_data_name',
            entry_data=b'fake_secure_data_entry'
        )
        self.session.add(data)
        self.session.commit()

        data2 = SecureData(
            user=user,
            entry_name=b'fake_secure_data_name',
            entry_data=b'fake_secure_data_entry'
        )
        self.session.add(data2)
        self.session.commit()

        assert len(user.secure_data) == 2
        assert data in user.secure_data
        assert data2 in user.secure_data
        assert data.user_id == user.id
        assert data2.user_id == user.id

    def test_user_cascade_deletion(self):
        """Should delete all LoginSessions, AuthEphemerals and SecureData when User is deleted"""
        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )
        self.session.add(user)
        self.session.commit()

        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user=user,
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=False
        )
        self.session.add(ephemeral)
        self.session.commit()

        last_used = datetime.now()
        login = LoginSession(
            user=user,
            session_key=b'fake_session_key',
            request_count=0,
            last_used=last_used,
            password_change=False
        )
        self.session.add(login)
        self.session.commit()

        data = SecureData(
            user=user,
            entry_name=b'fake_secure_data_name',
            entry_data=b'fake_secure_data_entry'
        )
        self.session.add(data)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == b'fake_hash'

        db_login = self.session.query(LoginSession).first()
        assert db_login is not None
        assert db_login.session_key == b'fake_session_key'

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert db_ephemeral.eph_public_b == b'fake_eph_public_b'

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.entry_name == b'fake_secure_data_name'

        assert login in user.login_sessions
        assert ephemeral in user.auth_ephemerals
        assert data in user.secure_data
        assert login.user == user
        assert ephemeral.user == user
        assert data.user == user

        self.session.delete(user)
        self.session.commit()

        users = self.session.query(User).all()
        assert len(users) == 0
        ephemerals = self.session.query(AuthEphemeral).all()
        assert len(ephemerals) == 0
        login_sessions = self.session.query(LoginSession).all()
        assert len(login_sessions) == 0
        secure_data = self.session.query(SecureData).all()
        assert len(secure_data) == 0

    def test_auth_ephemeral_cascade_deletion(self):
        """Should delete AuthEphemeral from User when AuthEphemeral deleted"""
        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )
        self.session.add(user)
        self.session.commit()

        expiry = datetime.now() + timedelta(hours=1)
        eph = AuthEphemeral(
            user=user,
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=False
        )
        self.session.add(eph)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == b'fake_hash'

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert db_ephemeral.eph_public_b == b'fake_eph_public_b'

        assert eph in user.auth_ephemerals

        self.session.delete(eph)
        self.session.commit()

        ephemerals = self.session.query(AuthEphemeral).all()
        assert len(ephemerals) == 0
        assert eph not in user.auth_ephemerals
        assert user in self.session.query(User).all()

    def test_login_cascade_deletion(self):
        """Should delete LoginSession from User when LoginSession deleted"""
        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )
        self.session.add(user)
        self.session.commit()

        last_used = datetime.now()
        login = LoginSession(
            user=user,
            session_key=b'fake_session_key',
            request_count=0,
            last_used=last_used,
            password_change=False
        )
        self.session.add(login)
        self.session.commit()

        data = SecureData(
            user=user,
            entry_name=b'fake_secure_data_name',
            entry_data=b'fake_secure_data_entry'
        )
        self.session.add(data)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == b'fake_hash'

        db_login = self.session.query(LoginSession).first()
        assert db_login is not None
        assert db_login.session_key == b'fake_session_key'

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.entry_name == b'fake_secure_data_name'

        assert login in user.login_sessions
        assert data in user.secure_data
        assert login.user == user
        assert data.user == user

        self.session.delete(login)
        self.session.commit()

        login_sessions = self.session.query(LoginSession).all()
        assert len(login_sessions) == 0
        assert login not in user.login_sessions
        assert data in user.secure_data
        assert data.user == user

    def test_secure_data_cascade_deletion(self):
        """Should delete SecureData from User when SecureData deleted"""
        user = User(
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )
        self.session.add(user)
        self.session.commit()

        last_used = datetime.now()
        login = LoginSession(
            user=user,
            session_key=b'fake_session_key',
            request_count=0,
            last_used=last_used,
            password_change=False
        )
        self.session.add(login)
        self.session.commit()

        data = SecureData(
            user=user,
            entry_name=b'fake_secure_data_name',
            entry_data=b'fake_secure_data_entry'
        )
        self.session.add(data)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == b'fake_hash'

        db_login = self.session.query(LoginSession).first()
        assert db_login is not None
        assert db_login.session_key == b'fake_session_key'

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.entry_name == b'fake_secure_data_name'

        assert login in user.login_sessions
        assert data in user.secure_data
        assert login.user == user
        assert data.user == user

        self.session.delete(data)
        self.session.commit()

        secure_data_entries = self.session.query(SecureData).all()
        assert len(secure_data_entries) == 0
        assert login in user.login_sessions
        assert data not in user.secure_data
        assert login.user == user


class TestDatabaseModelsUnitTests():
    """Further unit tests for database models"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        yield

        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_empty_values(self):
        """Should be able to handle empty values in all models"""
        user = User(
            username_hash=b'',
            srp_salt=b'',
            srp_verifier=b'',
            master_key_salt=b'',
            password_change=False,
            new_srp_salt=b'',
            new_srp_verifier=b'',
            new_master_key_salt=b''
        )
        self.session.add(user)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == b''
        assert db_user.srp_salt == b''
        assert db_user.srp_verifier == b''
        assert db_user.master_key_salt == b''
        assert db_user.new_srp_salt == b''
        assert db_user.new_srp_verifier == b''
        assert db_user.new_master_key_salt == b''

        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            eph_private_b=b'',
            eph_public_b=b'',
            expiry_time=expiry,
            password_change=True
        )
        self.session.add(ephemeral)
        self.session.commit()

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert db_ephemeral.eph_private_b == b''
        assert db_ephemeral.eph_public_b == b''

        last_used = datetime.now()
        login = LoginSession(
            user_id=123456,
            session_key=b'',
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
        assert db_login.session_key == b''

        data = SecureData(
            user_id=123456,
            entry_name=b'',
            entry_data=b'',
            new_entry_name=b'',
            new_entry_data=b''
        )
        self.session.add(data)
        self.session.commit()

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.entry_name == b''
        assert db_data.entry_data == b''
        assert db_data.new_entry_name == b''
        assert db_data.new_entry_data == b''

    def test_long_strings(self):
        """Should be able to handle long strings in all models"""
        user = User(
            username_hash=b'x'*10000,
            srp_salt=b'x'*10000,
            srp_verifier=b'x'*10000,
            master_key_salt=b'x'*10000,
            password_change=False,
            new_srp_salt=b'x'*10000,
            new_srp_verifier=b'x'*10000,
            new_master_key_salt=b'x'*10000
        )
        self.session.add(user)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == b'x'*10000
        assert db_user.srp_salt == b'x'*10000
        assert db_user.srp_verifier == b'x'*10000
        assert db_user.master_key_salt == b'x'*10000
        assert db_user.new_srp_salt == b'x'*10000
        assert db_user.new_srp_verifier == b'x'*10000
        assert db_user.new_master_key_salt == b'x'*10000

        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            eph_private_b=b'x'*10000,
            eph_public_b=b'x'*10000,
            expiry_time=expiry,
            password_change=True
        )
        self.session.add(ephemeral)
        self.session.commit()

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert db_ephemeral.eph_private_b == b'x'*10000
        assert db_ephemeral.eph_public_b == b'x'*10000

        last_used = datetime.now()
        login = LoginSession(
            user_id=123456,
            session_key=b'x'*10000,
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
        assert db_login.session_key == b'x'*10000

        data = SecureData(
            user_id=123456,
            entry_name=b'x'*10000,
            entry_data=b'x'*10000,
            new_entry_name=b'x'*10000,
            new_entry_data=b'x'*10000
        )
        self.session.add(data)
        self.session.commit()

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.entry_name == b'x'*10000
        assert db_data.entry_data == b'x'*10000
        assert db_data.new_entry_name == b'x'*10000
        assert db_data.new_entry_data == b'x'*10000

    def test_special_characters(self):
        """Should be able to handle special character strings in all models"""
        user = User(
            username_hash=b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~',
            srp_salt=b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~',
            srp_verifier=b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~',
            master_key_salt=b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~',
            password_change=False,
            new_srp_salt=b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~',
            new_srp_verifier=b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~',
            new_master_key_salt=b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~',
        )
        self.session.add(user)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~'
        assert db_user.srp_salt == b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~'
        assert db_user.srp_verifier == b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~'
        assert db_user.master_key_salt == b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~'
        assert db_user.new_srp_salt == b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~'
        assert db_user.new_srp_verifier == b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~'
        assert db_user.new_master_key_salt == b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~'

        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            eph_private_b=b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~',
            eph_public_b=b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~',
            expiry_time=expiry,
            password_change=True
        )
        self.session.add(ephemeral)
        self.session.commit()

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert db_ephemeral.eph_public_b == b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~'
        assert db_ephemeral.eph_private_b == b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~'

        last_used = datetime.now()
        login = LoginSession(
            user_id=123456,
            session_key=b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~',
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
        assert db_login.session_key == b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~'

        data = SecureData(
            user_id=123456,
            entry_name=b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~',
            entry_data=b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~',
            new_entry_name=b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~',
            new_entry_data=b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~'
        )
        self.session.add(data)
        self.session.commit()

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.entry_name == b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~'
        assert db_data.entry_data == b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~'
        assert db_data.new_entry_name == b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~'
        assert db_data.new_entry_data == b'!@#$%^&*()_+-=[]{}|;\':\",./<>?`~'

    def test_other_byte_characters(self):
        """Should be able to handle other random bytes"""
        user = User(
            username_hash=b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd',
            srp_salt=b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd',
            srp_verifier=b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd',
            master_key_salt=b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd',
            password_change=False,
            new_srp_salt=b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd',
            new_srp_verifier=b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd',
            new_master_key_salt=b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd'
        )
        self.session.add(user)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd'
        assert db_user.srp_salt == b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd'
        assert db_user.srp_verifier == b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd'
        assert db_user.master_key_salt == b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd'
        assert db_user.new_srp_salt == b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd'
        assert db_user.new_srp_verifier == b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd'
        assert db_user.new_master_key_salt == b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd'

        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=123456,
            eph_private_b=b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd',
            eph_public_b=b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd',
            expiry_time=expiry,
            password_change=True
        )
        self.session.add(ephemeral)
        self.session.commit()

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert db_ephemeral.eph_private_b == b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd'
        assert db_ephemeral.eph_public_b == b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd'

        last_used = datetime.now()
        login = LoginSession(
            user_id=123456,
            session_key=b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd',
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
        assert db_login.session_key == b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd'

        data = SecureData(
            user_id=123456,
            entry_name=b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd',
            entry_data=b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd',
            new_entry_name=b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd',
            new_entry_data=b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd'
        )
        self.session.add(data)
        self.session.commit()

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.entry_name == b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd'
        assert db_data.entry_data == b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd'
        assert db_data.new_entry_name == b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd'
        assert db_data.new_entry_data == b'\x00\x01\x02\x06\x15\x1b\x1f\x7f\x80\x9a\xaf\xff\x10\x03\x04\x19\x7e\x42\x99\xcd'

    def test_small_ints(self):
        """Should be able to handle small ints in all models"""
        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=0,
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=True
        )
        self.session.add(ephemeral)
        self.session.commit()

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert ephemeral.user_id == 0

        last_used = datetime.now()
        login = LoginSession(
            user_id=0,
            session_key=b'fake_session_key',
            request_count=0,
            last_used=last_used,
            maximum_requests=0,
            expiry_time=expiry,
            password_change=True
        )
        self.session.add(login)
        self.session.commit()

        db_login = self.session.query(LoginSession).first()
        assert db_login is not None
        assert db_login.user_id == 0
        assert db_login.request_count == 0
        assert db_login.maximum_requests == 0

        data = SecureData(
            user_id=0,
            entry_name=b'fake_secure_data_name',
            entry_data=b'fake_secure_data_entry',
            new_entry_name=b'new_fake_secure_data_name',
            new_entry_data=b'new_fake_secure_data_entry'
        )
        self.session.add(data)
        self.session.commit()

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.user_id == 0

    def test_large_ints(self):
        """Should be able to handle large ints in all models"""
        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=9223372036854775807,
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=True
        )
        self.session.add(ephemeral)
        self.session.commit()

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert ephemeral.user_id == 9223372036854775807

        last_used = datetime.now()
        login = LoginSession(
            user_id=9223372036854775807,
            session_key=b'fake_session_key',
            request_count=9223372036854775807,
            last_used=last_used,
            maximum_requests=9223372036854775807,
            expiry_time=expiry,
            password_change=True
        )
        self.session.add(login)
        self.session.commit()

        db_login = self.session.query(LoginSession).first()
        assert db_login is not None
        assert db_login.user_id == 9223372036854775807
        assert db_login.request_count == 9223372036854775807
        assert db_login.maximum_requests == 9223372036854775807

        data = SecureData(
            user_id=9223372036854775807,
            entry_name=b'fake_secure_data_name',
            entry_data=b'fake_secure_data_entry',
            new_entry_name=b'new_fake_secure_data_name',
            new_entry_data=b'new_fake_secure_data_entry'
        )
        self.session.add(data)
        self.session.commit()

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.user_id == 9223372036854775807

    def test_negative_ints(self):
        """Should be able to handle negative ints in all models"""
        expiry = datetime.now() + timedelta(hours=1)
        ephemeral = AuthEphemeral(
            user_id=-9223372036854775806,
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=True
        )
        self.session.add(ephemeral)
        self.session.commit()

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert ephemeral.user_id == -9223372036854775806

        last_used = datetime.now()
        login = LoginSession(
            user_id=-9223372036854775806,
            session_key=b'fake_session_key',
            request_count=-9223372036854775806,
            last_used=last_used,
            maximum_requests=-9223372036854775806,
            expiry_time=expiry,
            password_change=True
        )
        self.session.add(login)
        self.session.commit()

        db_login = self.session.query(LoginSession).first()
        assert db_login is not None
        assert db_login.user_id == -9223372036854775806
        assert db_login.request_count == -9223372036854775806
        assert db_login.maximum_requests == -9223372036854775806

        data = SecureData(
            user_id=-9223372036854775806,
            entry_name=b'fake_secure_data_name',
            entry_data=b'fake_secure_data_entry',
            new_entry_name=b'new_fake_secure_data_name',
            new_entry_data=b'new_fake_secure_data_entry'
        )
        self.session.add(data)
        self.session.commit()

        db_data = self.session.query(SecureData).first()
        assert db_data is not None
        assert db_data.user_id == -9223372036854775806

    def test_past_datetimes(self):
        """Should be able to handle past datetime values"""
        expiry = datetime.min
        ephemeral = AuthEphemeral(
            user_id=123456,
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=True
        )
        self.session.add(ephemeral)
        self.session.commit()

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert db_ephemeral.expiry_time == datetime.min

        last_used = datetime.min
        login = LoginSession(
            user_id=123456,
            session_key=b'fake_session_key',
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
        assert db_login.last_used == datetime.min

    def test_future_datetimes(self):
        """Should be able to handle future datetime values"""
        expiry = datetime.max
        ephemeral = AuthEphemeral(
            user_id=123456,
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=True
        )
        self.session.add(ephemeral)
        self.session.commit()

        db_ephemeral = self.session.query(AuthEphemeral).first()
        assert db_ephemeral is not None
        assert db_ephemeral.expiry_time == datetime.max

        last_used = datetime.max
        login = LoginSession(
            user_id=123456,
            session_key=b'fake_session_key',
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
        assert db_login.last_used == datetime.max


if __name__ == '__main__':
    pytest.main(['-v', __file__])
