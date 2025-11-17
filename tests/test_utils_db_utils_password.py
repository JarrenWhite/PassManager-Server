import os
import sys
import pytest
from contextlib import contextmanager
from datetime import datetime, timedelta

from sqlalchemy.sql.elements import BinaryExpression

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.mock_classes import _MockSession, _MockQuery
from utils.utils_enums import FailureReason
from utils.db_utils_password import DBUtilsPassword
from database.database_setup import DatabaseSetup
from database.database_models import User, AuthEphemeral, LoginSession, SecureData


class TestCleanPasswordChange():
    """Test cases for database utils password clean password change function"""

    def test_user_password_change_set_to_false(self):
        """Should change user password change status to false"""
        mock_session = _MockSession()

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[],
            login_sessions=[],
            secure_data=[]
        )

        DBUtilsPassword.clean_password_change(
            db_session=mock_session, # type: ignore
            user=fake_user
        )

        assert fake_user.password_change == False
        assert fake_user.new_srp_salt == None
        assert fake_user.new_srp_verifier == None
        assert fake_user.new_master_key_salt == None

    def test_delete_auth_ephemeral(self):
        """Should delete any password change auth ephemerals"""
        mock_session = _MockSession()

        ephemeral = AuthEphemeral(
            user_id=1,
            public_id="valid_password_ephemeral",
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=True
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[
                ephemeral
            ],
            login_sessions=[],
            secure_data=[]
        )

        DBUtilsPassword.clean_password_change(
            db_session=mock_session, # type: ignore
            user=fake_user
        )

        assert len(mock_session._deletes) == 1
        assert mock_session._deletes[0] == ephemeral

    def test_non_password_ephemerals(self):
        """Should not delete auth ephemerals that are not password related"""
        mock_session = _MockSession()

        ephemeral_1 = AuthEphemeral(
            user_id=1,
            public_id="valid_password_ephemeral",
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )
        ephemeral_2 = AuthEphemeral(
            user_id=1,
            public_id="valid_password_ephemeral",
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )
        ephemeral_3 = AuthEphemeral(
            user_id=1,
            public_id="valid_password_ephemeral",
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[
                ephemeral_1,
                ephemeral_2,
                ephemeral_3
            ],
            login_sessions=[],
            secure_data=[]
        )

        DBUtilsPassword.clean_password_change(
            db_session=mock_session, # type: ignore
            user=fake_user
        )

        assert len(mock_session._deletes) == 0

    def test_non_password_ephemeral_among_others(self):
        """Should delete correct ephemeral in list of others"""
        mock_session = _MockSession()

        ephemeral_1 = AuthEphemeral(
            user_id=1,
            public_id="valid_password_ephemeral",
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )
        ephemeral_2 = AuthEphemeral(
            user_id=1,
            public_id="valid_password_ephemeral",
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=True
        )
        ephemeral_3 = AuthEphemeral(
            user_id=1,
            public_id="valid_password_ephemeral",
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[
                ephemeral_1,
                ephemeral_2,
                ephemeral_3
            ],
            login_sessions=[],
            secure_data=[]
        )

        DBUtilsPassword.clean_password_change(
            db_session=mock_session, # type: ignore
            user=fake_user
        )

        assert len(mock_session._deletes) == 1
        assert mock_session._deletes[0] == ephemeral_2

    def test_delete_password_session(self):
        """Should delete any password change login session"""
        mock_session = _MockSession()

        login_session = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=True
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[],
            login_sessions=[
                login_session
            ],
            secure_data=[]
        )

        DBUtilsPassword.clean_password_change(
            db_session=mock_session, # type: ignore
            user=fake_user
        )

        assert len(mock_session._deletes) == 1
        assert mock_session._deletes[0] == login_session

    def test_non_password_sessions(self):
        """Should not delete login sessions that are not password related"""
        mock_session = _MockSession()

        login_session_1 = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )
        login_session_2 = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )
        login_session_3 = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[],
            login_sessions=[
                login_session_1,
                login_session_2,
                login_session_3
            ],
            secure_data=[]
        )

        DBUtilsPassword.clean_password_change(
            db_session=mock_session, # type: ignore
            user=fake_user
        )

        assert len(mock_session._deletes) == 0

    def test_non_password_session_among_others(self):
        """Should delete correct session in list of others"""
        mock_session = _MockSession()

        login_session_1 = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )
        login_session_2 = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=True
        )
        login_session_3 = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[],
            login_sessions=[
                login_session_1,
                login_session_2,
                login_session_3
            ],
            secure_data=[]
        )

        DBUtilsPassword.clean_password_change(
            db_session=mock_session, # type: ignore
            user=fake_user
        )

        assert len(mock_session._deletes) == 1
        assert mock_session._deletes[0] == login_session_2

    def test_remove_details_from_completed_data(self):
        """Should remove new password details from all sessions"""
        mock_session = _MockSession()

        secure_data = SecureData(
            user_id=123456,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name",
            new_entry_data="new_fake_entry_data"
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[],
            login_sessions=[],
            secure_data=[
                secure_data
            ]
        )

        DBUtilsPassword.clean_password_change(
            db_session=mock_session, # type: ignore
            user=fake_user
        )

        assert len(mock_session._deletes) == 0
        assert secure_data.new_entry_name == None
        assert secure_data.new_entry_data == None
        assert secure_data.user_id == 123456
        assert secure_data.public_id == "fake_public_id"
        assert secure_data.entry_name == "fake_entry_name"
        assert secure_data.entry_data == "fake_entry_data"

    def test_multiple_secure_data_entries(self):
        """Should remove data from all secure data in a list"""
        mock_session = _MockSession()

        secure_data_1 = SecureData(
            user_id=123456,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name",
            new_entry_data="new_fake_entry_data"
        )
        secure_data_2 = SecureData(
            user_id=123456,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name",
            new_entry_data="new_fake_entry_data"
        )
        secure_data_3 = SecureData(
            user_id=123456,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name",
            new_entry_data="new_fake_entry_data"
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[],
            login_sessions=[],
            secure_data=[
                secure_data_1,
                secure_data_2,
                secure_data_3
            ]
        )

        DBUtilsPassword.clean_password_change(
            db_session=mock_session, # type: ignore
            user=fake_user
        )

        assert len(mock_session._deletes) == 0
        assert secure_data_1.new_entry_name == None
        assert secure_data_1.new_entry_data == None
        assert secure_data_2.new_entry_name == None
        assert secure_data_2.new_entry_data == None
        assert secure_data_3.new_entry_name == None
        assert secure_data_3.new_entry_data == None

    def test_multiple_incomplete_secure_data_entries(self):
        """Should not adjust data content of non password secure data"""
        mock_session = _MockSession()

        secure_data = SecureData(
            user_id=123456,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name=None,
            new_entry_data=None
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[],
            login_sessions=[],
            secure_data=[
                secure_data
            ]
        )

        DBUtilsPassword.clean_password_change(
            db_session=mock_session, # type: ignore
            user=fake_user
        )

        assert len(mock_session._deletes) == 0
        assert secure_data.new_entry_name == None
        assert secure_data.new_entry_data == None
        assert secure_data.user_id == 123456
        assert secure_data.public_id == "fake_public_id"
        assert secure_data.entry_name == "fake_entry_name"
        assert secure_data.entry_data == "fake_entry_data"

    def test_mix_of_details(self):
        """Should delete the correct entries, ignoring the rest"""
        mock_session = _MockSession()

        ephemeral_1 = AuthEphemeral(
            user_id=1,
            public_id="valid_password_ephemeral",
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )
        ephemeral_2 = AuthEphemeral(
            user_id=1,
            public_id="valid_password_ephemeral",
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=True
        )
        ephemeral_3 = AuthEphemeral(
            user_id=1,
            public_id="valid_password_ephemeral",
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )

        login_session_1 = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )
        login_session_2 = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=True
        )
        login_session_3 = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )

        secure_data_1 = SecureData(
            user_id=123456,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name=None,
            new_entry_data=None
        )
        secure_data_2 = SecureData(
            user_id=123456,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name",
            new_entry_data="new_fake_entry_data"
        )
        secure_data_3 = SecureData(
            user_id=123456,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name",
            new_entry_data="new_fake_entry_data"
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[
                ephemeral_1,
                ephemeral_2,
                ephemeral_3
            ],
            login_sessions=[
                login_session_1,
                login_session_2,
                login_session_3
            ],
            secure_data=[
                secure_data_1,
                secure_data_2,
                secure_data_3
            ]
        )

        DBUtilsPassword.clean_password_change(
            db_session=mock_session, # type: ignore
            user=fake_user
        )

        assert fake_user.password_change == False
        assert fake_user.new_srp_salt == None
        assert fake_user.new_srp_verifier == None
        assert fake_user.new_master_key_salt == None

        assert len(mock_session._deletes) == 2
        assert ephemeral_2 in mock_session._deletes
        assert login_session_2 in mock_session._deletes
        assert secure_data_1.new_entry_name == None
        assert secure_data_1.new_entry_data == None
        assert secure_data_2.new_entry_name == None
        assert secure_data_2.new_entry_data == None
        assert secure_data_3.new_entry_name == None
        assert secure_data_3.new_entry_data == None


class TestStart():
    """Test cases for database utils password start function"""

    def test_set_new_password_details(self, monkeypatch):
        """Should add new password details to a user"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=False
        )

        mock_query = _MockQuery([fake_user])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        monkeypatch.setattr(AuthEphemeral, "public_id", "fake_public_id")

        expiry = datetime.now() + timedelta(hours=1)
        response = DBUtilsPassword.start(
            user_id=123456,
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=expiry,
            srp_salt="new_fake_srp_salt",
            srp_verifier="new_fake_srp_verifier",
            master_key_salt="new_fake_master_key_salt"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[2], str)
        assert response[0] == True
        assert response[1] == None

        assert fake_user.password_change
        assert fake_user.srp_salt == "fake_srp_salt"
        assert fake_user.srp_verifier == "fake_srp_verifier"
        assert fake_user.master_key_salt == "fake_master_key_salt"
        assert fake_user.new_srp_salt == "new_fake_srp_salt"
        assert fake_user.new_srp_verifier == "new_fake_srp_verifier"
        assert fake_user.new_master_key_salt == "new_fake_master_key_salt"

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "id"
        assert condition.right.value == 123456

    def test_create_change_password_auth_ephemeral(self, monkeypatch):
        """Should create a password change auth ephemeral"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=False
        )

        mock_query = _MockQuery([fake_user])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        monkeypatch.setattr(AuthEphemeral, "public_id", "fake_public_id")

        expiry = datetime.now() + timedelta(hours=1)
        response = DBUtilsPassword.start(
            user_id=123456,
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=expiry,
            srp_salt="new_fake_srp_salt",
            srp_verifier="new_fake_srp_verifier",
            master_key_salt="new_fake_master_key_salt"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[2], str)
        assert response[0] == True
        assert response[1] == None
        assert response[2] == "fake_public_id"

        assert len(mock_session._added) == 1
        assert len(mock_session._deletes) == 0
        assert mock_session.commits == 1
        assert mock_session.flushes == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        db_ephemeral = mock_session._added[0]
        assert isinstance(db_ephemeral, AuthEphemeral)
        assert db_ephemeral.public_id == "fake_public_id"
        assert db_ephemeral.eph_private_b == "fake_eph_private_b"
        assert db_ephemeral.eph_public_b == "fake_eph_public_b"
        assert db_ephemeral.expiry_time == expiry
        assert db_ephemeral.password_change == True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "id"
        assert condition.right.value == 123456

    def test_handles_entry_not_found(self, monkeypatch):
        """Should return correct failure reason if entry is not found"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        mock_query = _MockQuery([])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        expiry = datetime.now() + timedelta(hours=1)
        response = DBUtilsPassword.start(
            user_id=123456,
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=expiry,
            srp_salt="new_fake_srp_salt",
            srp_verifier="new_fake_srp_verifier",
            master_key_salt="new_fake_master_key_salt"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "id"
        assert condition.right.value == 123456

    def test_handles_password_change_in_progress(self, monkeypatch):
        """Should return correct failure reason if password change is in progress"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True
        )

        mock_query = _MockQuery([fake_user])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        expiry = datetime.now() + timedelta(hours=1)
        response = DBUtilsPassword.start(
            user_id=123456,
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=expiry,
            srp_salt="new_fake_srp_salt",
            srp_verifier="new_fake_srp_verifier",
            master_key_salt="new_fake_master_key_salt"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.PASSWORD_CHANGE

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "id"
        assert condition.right.value == 123456

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        @contextmanager
        def mock_get_db_session():
            raise RuntimeError("Database not initialised.")
            yield
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        expiry = datetime.now() + timedelta(hours=1)
        response = DBUtilsPassword.start(
            user_id=123456,
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=expiry,
            srp_salt="new_fake_srp_salt",
            srp_verifier="new_fake_srp_verifier",
            master_key_salt="new_fake_master_key_salt"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.DATABASE_UNINITIALISED

    def test_handles_server_exception(self, monkeypatch):
        """Should return correct failure reason if other exception seen"""
        def raise_unknown_exception():
            raise ValueError("Something went wrong")
        mock_session = _MockSession(on_commit=raise_unknown_exception)

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        expiry = datetime.now() + timedelta(hours=1)
        response = DBUtilsPassword.start(
            user_id=123456,
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=expiry,
            srp_salt="new_fake_srp_salt",
            srp_verifier="new_fake_srp_verifier",
            master_key_salt="new_fake_master_key_salt"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.UNKNOWN_EXCEPTION

        assert mock_session.commits == 0
        assert mock_session.rollbacks == 1
        assert mock_session.closed is True


class TestComplete():
    """Test cases for database utils password commit function"""

    def test_nominal_case(self, monkeypatch):
        """Should create password change login session from ephemeral"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            secure_data=[]
        )

        expiry = datetime.now() + timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=expiry,
            password_change=True
        )

        mock_query = _MockQuery([fake_ephemeral])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        monkeypatch.setattr(LoginSession, "public_id", "session_fake_public_id")

        response = DBUtilsPassword.complete(
            user_id=123456,
            public_id="ephemeral_fake_public_id",
            session_key="fake_session_key",
            expiry=expiry
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[2], str)
        assert response[0] == True
        assert response[1] == None
        assert response[2] == "session_fake_public_id"

        assert len(mock_session._added) == 1
        assert len(mock_session._deletes) == 1
        assert mock_session.commits == 1
        assert mock_session.flushes == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        db_ephemeral = mock_session._deletes[0]
        assert isinstance(db_ephemeral, AuthEphemeral)
        assert db_ephemeral.public_id == "ephemeral_fake_public_id"

        db_session = mock_session._added[0]
        assert isinstance(db_session, LoginSession)
        assert db_session.user == fake_user
        assert db_session.public_id == "session_fake_public_id"
        assert db_session.session_key == "fake_session_key"
        assert db_session.request_count == 0
        assert db_session.last_used < datetime.now()
        assert db_session.last_used > datetime.now() - timedelta(seconds=2)
        assert db_session.maximum_requests == 1
        assert db_session.expiry_time == expiry
        assert db_session.password_change == True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "public_id"
        assert condition.right.value == "ephemeral_fake_public_id"

    def test_correct_maximum_request_count(self, monkeypatch):
        """Should create maximum request count matching 2 x secure data count, +1"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        secure_data_1 = SecureData(
            user_id=123456,
            public_id="fake_public_id_1",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name_1",
            new_entry_data="new_fake_entry_data_1"
        )
        secure_data_2 = SecureData(
            user_id=123456,
            public_id="fake_public_id_2",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name_2",
            new_entry_data="new_fake_entry_data_2"
        )
        secure_data_3 = SecureData(
            user_id=123456,
            public_id="fake_public_id_3",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name_3",
            new_entry_data="new_fake_entry_data_3"
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            secure_data=[
                secure_data_1,
                secure_data_2,
                secure_data_3
            ]
        )

        expiry = datetime.now() + timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=expiry,
            password_change=True
        )

        mock_query = _MockQuery([fake_ephemeral])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        monkeypatch.setattr(LoginSession, "public_id", "session_fake_public_id")

        response = DBUtilsPassword.complete(
            user_id=123456,
            public_id="ephemeral_fake_public_id",
            session_key="fake_session_key",
            expiry=expiry
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[2], str)
        assert response[0] == True
        assert response[1] == None
        assert response[2] == "session_fake_public_id"

        db_session = mock_session._added[0]
        assert isinstance(db_session, LoginSession)
        assert db_session.maximum_requests == 7

    def test_ephemeral_is_not_password_change(self, monkeypatch):
        """Should fail if the auth ephemeral is not a password change type"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            secure_data=[]
        )

        expiry = datetime.now() + timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=expiry,
            password_change=False
        )

        mock_query = _MockQuery([fake_ephemeral])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        monkeypatch.setattr(LoginSession, "public_id", "session_fake_public_id")

        response = DBUtilsPassword.complete(
            user_id=123456,
            public_id="ephemeral_fake_public_id",
            session_key="fake_session_key",
            expiry=expiry
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.INCOMPLETE

    def test_expired_password_change(self, monkeypatch):
        """Should call clean_password_change if expired password change ephemeral"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            secure_data=[]
        )

        expiry = datetime.now() - timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=expiry,
            password_change=True
        )

        mock_query = _MockQuery([fake_ephemeral])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        called = {"cleaned": False, "user": None}
        def fake_clean_password(db_session, user):
            called["cleaned"] = True
            called["user"] = user
        monkeypatch.setattr(DBUtilsPassword, "clean_password_change", fake_clean_password)

        expiry = datetime.now() + timedelta(hours=1)
        response = DBUtilsPassword.complete(
            user_id=123456,
            public_id="ephemeral_fake_public_id",
            session_key="fake_session_key",
            expiry=expiry
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert len(mock_session._deletes) == 0
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND
        assert called["cleaned"]
        assert called["user"] == fake_user

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        @contextmanager
        def mock_get_db_session():
            raise RuntimeError("Database not initialised.")
            yield
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        expiry = datetime.now() + timedelta(hours=1)
        response = DBUtilsPassword.complete(
            user_id=123456,
            public_id="ephemeral_fake_public_id",
            session_key="fake_session_key",
            expiry=expiry
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.DATABASE_UNINITIALISED

    def test_handles_server_exception(self, monkeypatch):
        """Should return correct failure reason if other exception seen"""
        def raise_unknown_exception():
            raise ValueError("Something went wrong")
        mock_session = _MockSession(on_commit=raise_unknown_exception)

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        expiry = datetime.now() + timedelta(hours=1)
        response = DBUtilsPassword.complete(
            user_id=123456,
            public_id="ephemeral_fake_public_id",
            session_key="fake_session_key",
            expiry=expiry
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.UNKNOWN_EXCEPTION

        assert mock_session.commits == 0
        assert mock_session.rollbacks == 1
        assert mock_session.closed is True

    def test_handles_entry_not_found(self, monkeypatch):
        """Should return correct failure reason if entry is not found"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        mock_query = _MockQuery([])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        expiry = datetime.now() + timedelta(hours=1)
        response = DBUtilsPassword.complete(
            user_id=123456,
            public_id="ephemeral_fake_public_id",
            session_key="fake_session_key",
            expiry=expiry
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "public_id"
        assert condition.right.value == "ephemeral_fake_public_id"

    def test_user_id_match_fails(self, monkeypatch):
        """Should fail if user id does not match"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            secure_data=[]
        )

        expiry = datetime.now() + timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=expiry,
            password_change=True
        )

        mock_query = _MockQuery([fake_ephemeral])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        monkeypatch.setattr(LoginSession, "public_id", "session_fake_public_id")

        response = DBUtilsPassword.complete(
            user_id=654321,
            public_id="ephemeral_fake_public_id",
            session_key="fake_session_key",
            expiry=expiry
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert len(mock_session._deletes) == 0
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND


class TestCommit():
    """Test cases for database utils password commit function"""

    def test_completes_user_details(self, monkeypatch):
        """Should move new srp details, and remove password change status"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        login_session = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=True
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[],
            login_sessions=[
                login_session
            ],
            secure_data=[]
        )

        mock_query = _MockQuery([fake_user])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsPassword.commit(
            user_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert response[0] == True
        assert response[1] == None

        assert not fake_user.password_change
        assert fake_user.srp_salt == "new_fake_srp_salt"
        assert fake_user.srp_verifier == "new_fake_srp_verifier"
        assert fake_user.master_key_salt == "new_fake_master_key_salt"
        assert fake_user.new_srp_salt == None
        assert fake_user.new_srp_verifier == None
        assert fake_user.new_master_key_salt == None

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "id"
        assert condition.right.value == 123456

    def test_deletes_password_session(self, monkeypatch):
        """Should delete the change_password login session"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        login_session_1 = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )
        login_session_2 = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )
        login_session_3 = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[],
            login_sessions=[
                login_session_1,
                login_session_2,
                login_session_3
            ],
            secure_data=[]
        )

        mock_query = _MockQuery([fake_user])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsPassword.commit(
            user_id=123456
        )

        assert len(mock_session._deletes) == 3
        assert login_session_1 in mock_session._deletes
        assert login_session_2 in mock_session._deletes
        assert login_session_3 in mock_session._deletes

    def test_updates_secure_data_entries(self, monkeypatch):
        """Should move new encrypted data into current slots"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        login_session = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=True
        )

        secure_data_1 = SecureData(
            user_id=123456,
            public_id="fake_public_id_1",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name_1",
            new_entry_data="new_fake_entry_data_1"
        )
        secure_data_2 = SecureData(
            user_id=123456,
            public_id="fake_public_id_2",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name_2",
            new_entry_data="new_fake_entry_data_2"
        )
        secure_data_3 = SecureData(
            user_id=123456,
            public_id="fake_public_id_3",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name_3",
            new_entry_data="new_fake_entry_data_3"
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[],
            login_sessions=[
                login_session
            ],
            secure_data=[
                secure_data_1,
                secure_data_2,
                secure_data_3
            ]
        )

        mock_query = _MockQuery([fake_user])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsPassword.commit(
            user_id=123456
        )

        assert secure_data_1.public_id == "fake_public_id_1"
        assert secure_data_1.entry_name == "new_fake_entry_name_1"
        assert secure_data_1.entry_data == "new_fake_entry_data_1"
        assert secure_data_1.new_entry_name == None
        assert secure_data_1.new_entry_data == None

        assert secure_data_2.public_id == "fake_public_id_2"
        assert secure_data_2.entry_name == "new_fake_entry_name_2"
        assert secure_data_2.entry_data == "new_fake_entry_data_2"
        assert secure_data_2.new_entry_name == None
        assert secure_data_2.new_entry_data == None

        assert secure_data_3.public_id == "fake_public_id_3"
        assert secure_data_3.entry_name == "new_fake_entry_name_3"
        assert secure_data_3.entry_data == "new_fake_entry_data_3"
        assert secure_data_3.new_entry_name == None
        assert secure_data_3.new_entry_data == None

    def test_public_id_returns(self, monkeypatch):
        """Should return list of public IDs"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        login_session = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=True
        )

        secure_data_1 = SecureData(
            user_id=123456,
            public_id="fake_public_id_1",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name_1",
            new_entry_data="new_fake_entry_data_1"
        )
        secure_data_2 = SecureData(
            user_id=123456,
            public_id="fake_public_id_2",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name_2",
            new_entry_data="new_fake_entry_data_2"
        )
        secure_data_3 = SecureData(
            user_id=123456,
            public_id="fake_public_id_3",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name_3",
            new_entry_data="new_fake_entry_data_3"
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[],
            login_sessions=[
                login_session
            ],
            secure_data=[
                secure_data_1,
                secure_data_2,
                secure_data_3
            ]
        )

        mock_query = _MockQuery([fake_user])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsPassword.commit(
            user_id=123456
        )

        assert isinstance(response[2], list)

        assert "fake_public_id_1" in response[2]
        assert "fake_public_id_2" in response[2]
        assert "fake_public_id_3" in response[2]

    def test_password_change_incomplete_srp(self, monkeypatch):
        """Should fail if any srp details yet incomplete, and call clean_password_change"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        login_session = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=True
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier=None,
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[],
            login_sessions=[
                login_session
            ],
            secure_data=[]
        )

        mock_query = _MockQuery([fake_user])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        called = {"cleaned": False, "user": None}
        def fake_clean_password(db_session, user):
            called["cleaned"] = True
            called["user"] = user
        monkeypatch.setattr(DBUtilsPassword, "clean_password_change", fake_clean_password)

        response = DBUtilsPassword.commit(
            user_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.INCOMPLETE

        assert called["cleaned"] == True
        assert called["user"] == fake_user

    def test_password_change_incomplete_data(self, monkeypatch):
        """Should fail if any secure data yet incomplete, and call clean_password_change"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        login_session = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=True
        )

        secure_data_1 = SecureData(
            user_id=123456,
            public_id="fake_public_id_1",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name_1",
            new_entry_data="new_fake_entry_data_1"
        )
        secure_data_2 = SecureData(
            user_id=123456,
            public_id="fake_public_id_2",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name=None,
            new_entry_data=None
        )
        secure_data_3 = SecureData(
            user_id=123456,
            public_id="fake_public_id_3",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name_3",
            new_entry_data="new_fake_entry_data_3"
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[],
            login_sessions=[
                login_session
            ],
            secure_data=[
                secure_data_1,
                secure_data_2,
                secure_data_3
            ]
        )

        mock_query = _MockQuery([fake_user])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        called = {"cleaned": False, "user": None}
        def fake_clean_password(db_session, user):
            called["cleaned"] = True
            called["user"] = user
        monkeypatch.setattr(DBUtilsPassword, "clean_password_change", fake_clean_password)

        response = DBUtilsPassword.commit(
            user_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.INCOMPLETE

        assert called["cleaned"] == True
        assert called["user"] == fake_user

    def test_handles_entry_not_found(self, monkeypatch):
        """Should return correct failure reason if entry is not found"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        mock_query = _MockQuery([])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsPassword.commit(
            user_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "id"
        assert condition.right.value == 123456

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        @contextmanager
        def mock_get_db_session():
            raise RuntimeError("Database not initialised.")
            yield
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        response = DBUtilsPassword.commit(
            user_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.DATABASE_UNINITIALISED

    def test_handles_server_exception(self, monkeypatch):
        """Should return correct failure reason if other exception seen"""
        def raise_unknown_exception():
            raise ValueError("Something went wrong")
        mock_session = _MockSession(on_commit=raise_unknown_exception)

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        response = DBUtilsPassword.commit(
            user_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.UNKNOWN_EXCEPTION

        assert mock_session.commits == 0
        assert mock_session.rollbacks == 1
        assert mock_session.closed is True


class TestAbort():
    """Test cases for database utils password abort function"""

    def test_nominal_case(self, monkeypatch):
        """Should fetch the user and call clean_password_change"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        login_session = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=datetime.now() - timedelta(hours=1),
            maximum_requests=None,
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=True
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt",
            auth_ephemerals=[],
            login_sessions=[
                login_session
            ],
            secure_data=[]
        )

        mock_query = _MockQuery([fake_user])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        called = {"cleaned": False, "user": None}
        def fake_clean_password(db_session, user):
            called["cleaned"] = True
            called["user"] = user
        monkeypatch.setattr(DBUtilsPassword, "clean_password_change", fake_clean_password)

        response = DBUtilsPassword.abort(
            user_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert response[0] == True
        assert response[1] == None

        assert called["cleaned"] == True
        assert called["user"] == fake_user

    def test_handles_entry_not_found(self, monkeypatch):
        """Should return correct failure reason if entry is not found"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        mock_query = _MockQuery([])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsPassword.abort(
            user_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "id"
        assert condition.right.value == 123456

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        @contextmanager
        def mock_get_db_session():
            raise RuntimeError("Database not initialised.")
            yield
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        response = DBUtilsPassword.abort(
            user_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.DATABASE_UNINITIALISED

    def test_handles_server_exception(self, monkeypatch):
        """Should return correct failure reason if other exception seen"""
        def raise_unknown_exception():
            raise ValueError("Something went wrong")
        mock_session = _MockSession(on_commit=raise_unknown_exception)

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        response = DBUtilsPassword.abort(
            user_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.UNKNOWN_EXCEPTION

        assert mock_session.commits == 0
        assert mock_session.rollbacks == 1
        assert mock_session.closed is True

class TestUpdate():
    """Test cases for database utils password clean password change function"""

    def test_nominal_case(self, monkeypatch):
        """Should add new data to given secure data entry"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt"
        )

        secure_data = SecureData(
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name=None,
            new_entry_data=None,
            user=fake_user
        )

        mock_query = _MockQuery([secure_data])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsPassword.update(
            user_id=123456,
            public_id="fake_public_id",
            entry_name="new_fake_entry_name",
            entry_data="new_fake_entry_data"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert response[0] == True
        assert response[1] == None

        assert secure_data.entry_name == "fake_entry_name"
        assert secure_data.entry_data == "fake_entry_data"
        assert secure_data.new_entry_name == "new_fake_entry_name"
        assert secure_data.new_entry_data == "new_fake_entry_data"

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "public_id"
        assert condition.right.value == "fake_public_id"

    def test_handles_already_completed_secure_data(self, monkeypatch):
        """Should correctly handle case when secure data is already completed"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt"
        )

        secure_data = SecureData(
            user_id=123456,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name="new_fake_entry_name",
            new_entry_data="new_fake_entry_name",
            user=fake_user
        )

        mock_query = _MockQuery([secure_data])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        called = {"cleaned": False, "user": None}
        def fake_clean_password(db_session, user):
            called["cleaned"] = True
            called["user"] = user
        monkeypatch.setattr(DBUtilsPassword, "clean_password_change", fake_clean_password)

        response = DBUtilsPassword.update(
            user_id=123456,
            public_id="fake_public_id",
            entry_name="new_fake_entry_name",
            entry_data="new_fake_entry_data"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.DUPLICATE

        assert called["cleaned"] == True
        assert called["user"] == fake_user

    def test_handles_entry_not_found(self, monkeypatch):
        """Should return correct failure reason if entry is not found"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        mock_query = _MockQuery([])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsPassword.update(
            user_id=123456,
            public_id="fake_public_id",
            entry_name="new_fake_entry_name",
            entry_data="new_fake_entry_data"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "public_id"
        assert condition.right.value == "fake_public_id"

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        @contextmanager
        def mock_get_db_session():
            raise RuntimeError("Database not initialised.")
            yield
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        response = DBUtilsPassword.update(
            user_id=123456,
            public_id="fake_public_id",
            entry_name="new_fake_entry_name",
            entry_data="new_fake_entry_data"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.DATABASE_UNINITIALISED

    def test_handles_server_exception(self, monkeypatch):
        """Should return correct failure reason if other exception seen"""
        def raise_unknown_exception():
            raise ValueError("Something went wrong")
        mock_session = _MockSession(on_commit=raise_unknown_exception)

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        response = DBUtilsPassword.update(
            user_id=123456,
            public_id="fake_public_id",
            entry_name="new_fake_entry_name",
            entry_data="new_fake_entry_data"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.UNKNOWN_EXCEPTION

        assert mock_session.commits == 0
        assert mock_session.rollbacks == 1
        assert mock_session.closed is True

    def test_user_id_match_fails(self, monkeypatch):
        """Should fail if user id does not match"""
        mock_session = _MockSession()

        @contextmanager
        def mock_get_db_session():
            try:
                yield mock_session
                mock_session.commit()
            except Exception:
                mock_session.rollback()
                raise
            finally:
                mock_session.close()
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            new_srp_salt="new_fake_srp_salt",
            new_srp_verifier="new_fake_srp_verifier",
            new_master_key_salt="new_fake_master_key_salt"
        )

        secure_data = SecureData(
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data",
            new_entry_name=None,
            new_entry_data=None,
            user=fake_user
        )

        mock_query = _MockQuery([secure_data])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsPassword.update(
            user_id=654321,
            public_id="fake_public_id",
            entry_name="new_fake_entry_name",
            entry_data="new_fake_entry_data"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert len(mock_session._deletes) == 0
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND


if __name__ == '__main__':
    pytest.main(['-v', __file__])
