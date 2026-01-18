import os
import sys
import pytest
from contextlib import contextmanager
from datetime import datetime, timedelta

from sqlalchemy.sql.elements import BinaryExpression

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from mock_classes import _MockSession, _MockQuery
from enums.failure_reason import FailureReason
from utils.db_utils_auth import DBUtilsAuth
from utils.db_utils_password import DBUtilsPassword
from database.database_setup import DatabaseSetup
from database.database_models import User, AuthEphemeral, LoginSession


class TestStart():
    """Test cases for database utils auth start function"""

    def test_nominal_case(self, monkeypatch):
        """Should create auth ephemeral & fetch srp_salt"""
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
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )

        mock_query = _MockQuery([fake_user])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        monkeypatch.setattr(AuthEphemeral, "public_id", "fake_public_id")

        expiry = datetime.now() + timedelta(hours=1)
        response = DBUtilsAuth.start(
            username_hash=b'fake_hash',
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[2], str)
        assert isinstance(response[3], bytes)
        assert response[0] == True
        assert response[1] == None
        assert response[2] == "fake_public_id"
        assert response[3] == b'fake_srp_salt'

        assert len(mock_session._added) == 1
        assert len(mock_session._deletes) == 0
        assert mock_session.commits == 1
        assert mock_session.flushes == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        db_ephemeral = mock_session._added[0]
        assert isinstance(db_ephemeral, AuthEphemeral)
        assert db_ephemeral.public_id == "fake_public_id"
        assert db_ephemeral.eph_private_b == b'fake_eph_private_b'
        assert db_ephemeral.eph_public_b == b'fake_eph_public_b'
        assert db_ephemeral.expiry_time == expiry
        assert db_ephemeral.password_change == False

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "username_hash"
        assert condition.right.value == b'fake_hash'

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        @contextmanager
        def mock_get_db_session():
            raise RuntimeError("Database not initialised.")
            yield
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        expiry = datetime.now() + timedelta(hours=1)
        response = DBUtilsAuth.start(
            username_hash=b'fake_hash',
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry
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
        response = DBUtilsAuth.start(
            username_hash=b'fake_hash',
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry
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
        response = DBUtilsAuth.start(
            username_hash=b'fake_hash',
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry
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
        assert str(condition.left.name) == "username_hash"
        assert condition.right.value == b'fake_hash'


class TestGetDetails():
    """Test cases for database utils auth get_details function"""

    def test_nominal_case(self, monkeypatch):
        """Should correctly fetch ephemeral details"""
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
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )

        expiry = datetime.now() + timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            id=123456,
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=False
        )

        mock_query = _MockQuery([fake_ephemeral])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsAuth.get_details(
            user_id=123456,
            public_id="fake_public_id"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[2], bytes)
        assert isinstance(response[3], int)
        assert isinstance(response[4], bytes)
        assert isinstance(response[5], bytes)
        assert response[0] == True
        assert response[1] == None
        assert response[2] == b'fake_hash'
        assert response[3] == 123456
        assert response[4] == b'fake_eph_private_b'
        assert response[5] == b'fake_eph_public_b'

        assert len(mock_session._added) == 0
        assert len(mock_session._deletes) == 0
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

        response = DBUtilsAuth.get_details(
            user_id=123456,
            public_id="fake_public_id"
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

        response = DBUtilsAuth.get_details(
            user_id=123456,
            public_id="fake_public_id"
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

        response = DBUtilsAuth.get_details(
            user_id=123456,
            public_id="fake_public_id"
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

    def test_handles_entry_expired(self, monkeypatch):
        """Should return correct failure reason if entry is expired, and delete entry"""
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
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )

        expiry = datetime.now() - timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=False
        )

        mock_query = _MockQuery([fake_ephemeral])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsAuth.get_details(
            user_id=123456,
            public_id="fake_public_id"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        db_ephemeral = mock_session._deletes[0]
        assert db_ephemeral.public_id == "ephemeral_fake_public_id"
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
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=True
        )

        expiry = datetime.now() - timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
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

        response = DBUtilsAuth.get_details(
            user_id=123456,
            public_id="fake_public_id"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert len(mock_session._deletes) == 0
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND
        assert called["cleaned"]
        assert called["user"] == fake_user

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
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )

        expiry = datetime.now() + timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            id=123456,
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=False
        )

        mock_query = _MockQuery([fake_ephemeral])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsAuth.get_details(
            user_id=654321,
            public_id="fake_public_id"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert len(mock_session._deletes) == 0
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND


class TestComplete():
    """Test cases for database utils auth complete function"""

    def test_nominal_case_minimal_inputs(self, monkeypatch):
        """Should create login session & fetch srp_salt with minimal inputs"""
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
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )

        expiry = datetime.now() + timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=False
        )

        mock_query = _MockQuery([fake_ephemeral])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        monkeypatch.setattr(LoginSession, "public_id", "session_fake_public_id")

        response = DBUtilsAuth.complete(
            public_id="ephemeral_fake_public_id",
            session_key=b'fake_session_key',
            maximum_requests=None,
            expiry_time=None
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
        assert db_session.session_key == b'fake_session_key'
        assert db_session.request_count == 0
        assert db_session.last_used < datetime.now()
        assert db_session.last_used > datetime.now() - timedelta(seconds=2)
        assert db_session.maximum_requests == None
        assert db_session.expiry_time == None
        assert db_session.password_change == False

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "public_id"
        assert condition.right.value == "ephemeral_fake_public_id"

    def test_nominal_case_maximal_inputs(self, monkeypatch):
        """Should create login session & fetch srp_salt with maximal inputs"""
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
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )

        expiry = datetime.now() + timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=False
        )

        mock_query = _MockQuery([fake_ephemeral])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        monkeypatch.setattr(LoginSession, "public_id", "session_fake_public_id")

        expiry = datetime.now() + timedelta(hours=1)
        response = DBUtilsAuth.complete(
            public_id="ephemeral_fake_public_id",
            session_key=b'fake_session_key',
            maximum_requests=99,
            expiry_time=expiry
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
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        db_ephemeral = mock_session._deletes[0]
        assert isinstance(db_ephemeral, AuthEphemeral)
        assert db_ephemeral.public_id == "ephemeral_fake_public_id"

        db_session = mock_session._added[0]
        assert isinstance(db_session, LoginSession)
        assert db_session.user == fake_user
        assert db_session.public_id == "session_fake_public_id"
        assert db_session.session_key == b'fake_session_key'
        assert db_session.request_count == 0
        assert db_session.last_used < datetime.now()
        assert db_session.last_used > datetime.now() - timedelta(seconds=2)
        assert db_session.maximum_requests == 99
        assert db_session.expiry_time == expiry
        assert db_session.password_change == False

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "public_id"
        assert condition.right.value == "ephemeral_fake_public_id"

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        @contextmanager
        def mock_get_db_session():
            raise RuntimeError("Database not initialised.")
            yield
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        expiry = datetime.now() + timedelta(hours=1)
        response = DBUtilsAuth.complete(
            public_id="ephemeral_fake_public_id",
            session_key=b'fake_session_key',
            maximum_requests=99,
            expiry_time=expiry
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
        response = DBUtilsAuth.complete(
            public_id="ephemeral_fake_public_id",
            session_key=b'fake_session_key',
            maximum_requests=99,
            expiry_time=expiry
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
        response = DBUtilsAuth.complete(
            public_id="ephemeral_fake_public_id",
            session_key=b'fake_session_key',
            maximum_requests=99,
            expiry_time=expiry
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

    def test_handles_entry_expired(self, monkeypatch):
        """Should return correct failure reason if entry is expired, and delete entry"""
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
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=False
        )

        expiry = datetime.now() - timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=False
        )

        mock_query = _MockQuery([fake_ephemeral])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        monkeypatch.setattr(LoginSession, "public_id", "session_fake_public_id")

        response = DBUtilsAuth.complete(
            public_id="ephemeral_fake_public_id",
            session_key=b'fake_session_key',
            maximum_requests=None,
            expiry_time=None
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

    def test_password_change_setting_fails(self, monkeypatch):
        """Should return failure from password change ephemeral"""
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
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=True
        )

        expiry = datetime.now() + timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=True
        )

        mock_query = _MockQuery([fake_ephemeral])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        monkeypatch.setattr(LoginSession, "public_id", "session_fake_public_id")

        called = {"cleaned": False, "user": None}
        def fake_clean_password(db_session, user):
            called["cleaned"] = True
            called["user"] = user
        monkeypatch.setattr(DBUtilsPassword, "clean_password_change", fake_clean_password)

        response = DBUtilsAuth.complete(
            public_id="ephemeral_fake_public_id",
            session_key=b'fake_session_key',
            maximum_requests=None,
            expiry_time=None
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.PASSWORD_CHANGE
        assert not called["cleaned"]
        assert called["user"] == None

    def test_password_change_setting_not_linked_to_user(self, monkeypatch):
        """Should not create password change session just because user password change is True"""
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
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=True
        )

        expiry = datetime.now() + timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=expiry,
            password_change=False
        )

        mock_query = _MockQuery([fake_ephemeral])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        monkeypatch.setattr(LoginSession, "public_id", "session_fake_public_id")

        called = {"cleaned": False, "user": None}
        def fake_clean_password(db_session, user):
            called["cleaned"] = True
            called["user"] = user
        monkeypatch.setattr(DBUtilsPassword, "clean_password_change", fake_clean_password)

        response = DBUtilsAuth.complete(
            public_id="ephemeral_fake_public_id",
            session_key=b'fake_session_key',
            maximum_requests=None,
            expiry_time=None
        )

        db_session = mock_session._added[0]
        assert isinstance(db_session, LoginSession)
        assert db_session.password_change == False
        assert len(mock_session._deletes) == 1
        assert not called["cleaned"]
        assert called["user"] == None

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
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=True
        )

        expiry = datetime.now() - timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
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

        response = DBUtilsAuth.complete(
            public_id="ephemeral_fake_public_id",
            session_key=b'fake_session_key',
            maximum_requests=None,
            expiry_time=None
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert len(mock_session._deletes) == 0
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND
        assert called["cleaned"]
        assert called["user"] == fake_user


class TestCleanAll():
    """Test cases for database utils auth clean all function"""

    def test_handles_empty_list(self, monkeypatch):
        """Should not attempt any deletions for an empty list"""
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

        response = DBUtilsAuth.clean_all()

        assert isinstance(response, tuple)
        assert response[0] is True
        assert response[1] is None
        assert len(mock_session._deletes) == 0

    def test_all_unexpired_entries(self, monkeypatch):
        """Should not delete any entries when all entries in date"""
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

        auth_ephemeral_one = AuthEphemeral(
            user_id=1,
            public_id="ephemeral_fake_public_id_one",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )
        auth_ephemeral_two = AuthEphemeral(
            user_id=2,
            public_id="ephemeral_fake_public_id_two",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )
        auth_ephemeral_three = AuthEphemeral(
            user_id=3,
            public_id="ephemeral_fake_public_id_three",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=False
        )

        mock_query = _MockQuery([auth_ephemeral_one, auth_ephemeral_two, auth_ephemeral_three])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsAuth.clean_all()

        assert isinstance(response, tuple)
        assert response[0] is True
        assert response[1] is None
        assert len(mock_session._deletes) == 0

    def test_all_expired_entries(self, monkeypatch):
        """Should delete standard expired entries"""
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

        auth_ephemeral_one = AuthEphemeral(
            user_id=1,
            public_id="ephemeral_fake_public_id_one",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=datetime.now() - timedelta(hours=1),
            password_change=False
        )
        auth_ephemeral_two = AuthEphemeral(
            user_id=2,
            public_id="ephemeral_fake_public_id_two",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=datetime.now() - timedelta(hours=1),
            password_change=False
        )
        auth_ephemeral_three = AuthEphemeral(
            user_id=3,
            public_id="ephemeral_fake_public_id_three",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=datetime.now() - timedelta(hours=1),
            password_change=False
        )

        mock_query = _MockQuery([auth_ephemeral_one, auth_ephemeral_two, auth_ephemeral_three])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsAuth.clean_all()

        assert isinstance(response, tuple)
        assert response[0] is True
        assert response[1] is None

        assert len(mock_session._deletes) == 3
        deleted_ids = [s.public_id for s in mock_session._deletes]
        assert "ephemeral_fake_public_id_one" in deleted_ids
        assert "ephemeral_fake_public_id_two" in deleted_ids
        assert "ephemeral_fake_public_id_three" in deleted_ids

    def test_expired_password_change_entry(self, monkeypatch):
        """Should call clean_password_change for expired password-change ephemeral entries"""
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
            username_hash=b'fake_hash',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
            password_change=True
        )

        expired_ephemeral = AuthEphemeral(
            user=fake_user,
            public_id="expired_password_ephemeral",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=datetime.now() - timedelta(hours=1),
            password_change=True
        )

        mock_query = _MockQuery([expired_ephemeral])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        called = {"cleaned": False, "user": None}
        def fake_clean_password(db_session, user):
            called["cleaned"] = True
            called["user"] = user
        monkeypatch.setattr(DBUtilsPassword, "clean_password_change", fake_clean_password)

        response = DBUtilsAuth.clean_all()

        assert isinstance(response, tuple)
        assert response[0] is True
        assert response[1] is None
        assert called["cleaned"]
        assert called["user"] == fake_user
        assert len(mock_session._deletes) == 0

    def test_not_expired_password_change_entry(self, monkeypatch):
        """Should not delete or clean password-change ephemeral entries that are not expired"""
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

        valid_ephemeral = AuthEphemeral(
            user_id=1,
            public_id="valid_password_ephemeral",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=True
        )

        mock_query = _MockQuery([valid_ephemeral])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        called = {"cleaned": False, "user": None}
        def fake_clean_password(db_session, user):
            called["cleaned"] = True
            called["user"] = user
        monkeypatch.setattr(DBUtilsPassword, "clean_password_change", fake_clean_password)

        response = DBUtilsAuth.clean_all()

        assert isinstance(response, tuple)
        assert response[0] is True
        assert response[1] is None
        assert len(mock_session._deletes) == 0
        assert not called["cleaned"]
        assert called["user"] == None

    def test_mixed_list(self, monkeypatch):
        """Should correctly handle a mix of ephemerals"""
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

        now = datetime.now()

        expired_ephemeral = AuthEphemeral(
            user_id=1,
            public_id="expired_ephemeral",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=now - timedelta(hours=1),
            password_change=False
        )
        valid_ephemeral_one = AuthEphemeral(
            user_id=2,
            public_id="valid_ephemeral_one",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=now + timedelta(hours=1),
            password_change=False
        )
        expired_password_ephemeral = AuthEphemeral(
            user_id=3,
            public_id="expired_password_ephemeral",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=now - timedelta(hours=1),
            password_change=True
        )
        valid_ephemeral_two = AuthEphemeral(
            user_id=4,
            public_id="valid_ephemeral_two",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=now + timedelta(hours=1),
            password_change=False
        )
        expired_ephemeral_two = AuthEphemeral(
            user_id=5,
            public_id="expired_ephemeral_two",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=now - timedelta(hours=2),
            password_change=False
        )
        expired_password_ephemeral_two = AuthEphemeral(
            user_id=6,
            public_id="expired_password_ephemeral_two",
            eph_private_b=b'fake_eph_private_b',
            eph_public_b=b'fake_eph_public_b',
            expiry_time=now - timedelta(hours=2),
            password_change=True
        )

        mock_query = _MockQuery([
            expired_ephemeral,
            valid_ephemeral_one,
            expired_password_ephemeral,
            valid_ephemeral_two,
            expired_ephemeral_two,
            expired_password_ephemeral_two,
        ])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        called = {"cleaned": 0}
        def fake_clean_password(db_session, user):
            called["cleaned"] += 1
        monkeypatch.setattr(DBUtilsPassword, "clean_password_change", fake_clean_password)

        response = DBUtilsAuth.clean_all()

        assert isinstance(response, tuple)
        assert response[0] is True
        assert response[1] is None

        deleted_ids = [s.public_id for s in mock_session._deletes]
        assert "expired_ephemeral" in deleted_ids
        assert "expired_ephemeral_two" in deleted_ids
        assert "valid_ephemeral_one" not in deleted_ids
        assert "valid_ephemeral_two" not in deleted_ids
        assert "expired_password_ephemeral" not in deleted_ids
        assert "expired_password_ephemeral_two" not in deleted_ids

        assert called["cleaned"] == 2

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        @contextmanager
        def mock_get_db_session():
            raise RuntimeError("Database not initialised.")
            yield
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        response = DBUtilsAuth.clean_all()

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

        response = DBUtilsAuth.clean_all()

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.UNKNOWN_EXCEPTION

        assert mock_session.commits == 0
        assert mock_session.rollbacks == 1
        assert mock_session.closed is True


if __name__ == '__main__':
    pytest.main(['-v', __file__])
