import os
import sys
import pytest
from contextlib import contextmanager
from datetime import datetime, timedelta

from sqlalchemy.sql.elements import BinaryExpression

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.mock_classes import _MockSession, _MockQuery
from utils.utils_enums import FailureReason
from utils.db_utils_session import DBUtilsSession
from utils.db_utils_password import DBUtilsPassword
from database.database_setup import DatabaseSetup
from database.database_models import User, LoginSession


class TestGetDetails():
    """Test cases for database utils session get_details function"""

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
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=False
        )

        last_used = datetime.now() - timedelta(hours=1)
        fake_login_session = LoginSession(
            id=789123,
            user=fake_user,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=last_used,
            maximum_requests=None,
            expiry_time=None,
            password_change=False
        )

        mock_query = _MockQuery([fake_login_session])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsSession.get_details(
            public_id="session_fake_public_id"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[2], int)
        assert isinstance(response[3], int)
        assert isinstance(response[4], str)
        assert isinstance(response[5], int)
        assert isinstance(response[6], bool)
        assert response[0] == True
        assert response[1] == None
        assert response[2] == 123456
        assert response[3] == 789123
        assert response[4] == "fake_session_key"
        assert response[5] == 3
        assert response[6] == False

        assert len(mock_session._added) == 0
        assert len(mock_session._deletes) == 0
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "public_id"
        assert condition.right.value == "session_fake_public_id"

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        @contextmanager
        def mock_get_db_session():
            raise RuntimeError("Database not initialised.")
            yield
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        response = DBUtilsSession.get_details(
            public_id="session_fake_public_id"
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

        response = DBUtilsSession.get_details(
            public_id="session_fake_public_id"
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

        mock_query = _MockQuery([None])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsSession.get_details(
            public_id="session_fake_public_id"
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
        assert condition.right.value == "session_fake_public_id"

    def test_handles_entry_expired_request_count(self, monkeypatch):
        """Should return correct failure reason if entry is expired due to request count, and delete entry"""
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

        last_used = datetime.now() - timedelta(hours=1)
        fake_login_session = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=last_used,
            maximum_requests=3,
            expiry_time=None,
            password_change=False
        )

        mock_query = _MockQuery([fake_login_session])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsSession.get_details(
            public_id="session_fake_public_id"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        db_ephemeral = mock_session._deletes[0]
        assert db_ephemeral.public_id == "session_fake_public_id"
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "public_id"
        assert condition.right.value == "session_fake_public_id"

    def test_handles_entry_expired_expiry_time(self, monkeypatch):
        """Should return correct failure reason if entry is expired due to expiry time, and delete entry"""
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

        last_used = datetime.now() - timedelta(hours=1)
        expiry_time = datetime.now() - timedelta(seconds=1)
        fake_login_session = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=last_used,
            maximum_requests=None,
            expiry_time=expiry_time,
            password_change=False
        )

        mock_query = _MockQuery([fake_login_session])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsSession.get_details(
            public_id="session_fake_public_id"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        db_ephemeral = mock_session._deletes[0]
        assert db_ephemeral.public_id == "session_fake_public_id"
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "public_id"
        assert condition.right.value == "session_fake_public_id"


class TestLogUse():
    """Test cases for database utils session get_details function"""

    def test_nominal_case(self, monkeypatch):
        """Should increment the request count by 1, and return the session key"""
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

        last_used = datetime.now() - timedelta(hours=1)
        expiry_time = datetime.now() + timedelta(seconds=1)
        fake_login_session = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=last_used,
            maximum_requests=None,
            expiry_time=expiry_time,
            password_change=False
        )

        mock_query = _MockQuery([fake_login_session])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsSession.log_use(
            session_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[2], str)
        assert response[0] == True
        assert response[1] == None
        assert response[2] == "fake_session_key"
        assert fake_login_session.request_count == 4

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

        response = DBUtilsSession.log_use(
            session_id=123456
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

        response = DBUtilsSession.log_use(
            session_id=123456
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

        mock_query = _MockQuery([None])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsSession.log_use(
            session_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True


class TestDelete():
    """Test cases for database utils session delete function"""

    def test_nominal_case(self, monkeypatch):
        """Should delete given session"""
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

        last_used = datetime.now() - timedelta(hours=1)
        expiry_time = datetime.now() + timedelta(seconds=1)
        fake_login_session = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=last_used,
            maximum_requests=None,
            expiry_time=expiry_time,
            password_change=False
        )

        mock_query = _MockQuery([fake_login_session])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsSession.delete(
            public_id="session_fake_public_id"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert response[0] == True
        assert response[1] == None

        assert len(mock_session._deletes) == 1
        db_session = mock_session._deletes[0]
        assert db_session.public_id == "session_fake_public_id"
        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "public_id"
        assert condition.right.value == "session_fake_public_id"

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        @contextmanager
        def mock_get_db_session():
            raise RuntimeError("Database not initialised.")
            yield
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        response = DBUtilsSession.delete(
            public_id="session_fake_public_id"
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

        response = DBUtilsSession.delete(
            public_id="session_fake_public_id"
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

        mock_query = _MockQuery([None])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsSession.delete(
            public_id="session_fake_public_id"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

    def test_handles_password_change_session(self, monkeypatch):
        """Should return correct failure reason if entry is password change session"""
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

        last_used = datetime.now() - timedelta(hours=1)
        expiry_time = datetime.now() + timedelta(seconds=1)
        fake_login_session = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=last_used,
            maximum_requests=None,
            expiry_time=expiry_time,
            password_change=True
        )

        mock_query = _MockQuery([fake_login_session])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsSession.delete(
            public_id="fake_session_key"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.PASSWORD_CHANGE

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

    def test_handles_entry_expired_request_count(self, monkeypatch):
        """Should return correct failure reason if entry is expired due to request count, and delete entry"""
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

        last_used = datetime.now() - timedelta(hours=1)
        fake_login_session = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=last_used,
            maximum_requests=3,
            expiry_time=None,
            password_change=False
        )

        mock_query = _MockQuery([fake_login_session])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsSession.delete(
            public_id="session_fake_public_id"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        db_ephemeral = mock_session._deletes[0]
        assert db_ephemeral.public_id == "session_fake_public_id"
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND

    def test_handles_entry_expired_expiry_time(self, monkeypatch):
        """Should return correct failure reason if entry is expired due to expiry time, and delete entry"""
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

        last_used = datetime.now() - timedelta(hours=1)
        expiry_time = datetime.now() - timedelta(seconds=1)
        fake_login_session = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=last_used,
            maximum_requests=None,
            expiry_time=expiry_time,
            password_change=False
        )

        mock_query = _MockQuery([fake_login_session])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsSession.delete(
            public_id="session_fake_public_id"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        db_ephemeral = mock_session._deletes[0]
        assert db_ephemeral.public_id == "session_fake_public_id"
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND

    def test_handles_entry_expired_with_password_change(self, monkeypatch):
        """Should return correct failure reason if entry is expired due to expiry time, and delete entry"""
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

        last_used = datetime.now() - timedelta(hours=1)
        expiry_time = datetime.now() - timedelta(seconds=1)
        fake_login_session = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id",
            session_key="fake_session_key",
            request_count=3,
            last_used=last_used,
            maximum_requests=None,
            expiry_time=expiry_time,
            password_change=True
        )

        mock_query = _MockQuery([fake_login_session])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        called = {"cleaned": False}
        def fake_clean_password(db_session, user):
            called["cleaned"] = True
        monkeypatch.setattr(DBUtilsPassword, "clean_password_change", fake_clean_password)

        response = DBUtilsSession.delete(
            public_id="session_fake_public_id"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND
        assert called["cleaned"]


class TestCleanUser():
    """Test cases for database utils session clean_user function"""

    def test_nominal_case(self, monkeypatch):
        """Should delete all login sessions for given user"""
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

        last_used = datetime.now() - timedelta(hours=1)
        expiry_time = datetime.now() + timedelta(seconds=1)
        fake_login_session_one = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id_one",
            session_key="fake_session_key",
            request_count=3,
            last_used=last_used,
            maximum_requests=None,
            expiry_time=expiry_time,
            password_change=False
        )
        fake_login_session_two = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id_two",
            session_key="fake_session_key",
            request_count=3,
            last_used=last_used,
            maximum_requests=None,
            expiry_time=expiry_time,
            password_change=False
        )
        fake_login_session_three = LoginSession(
            user_id=123456,
            public_id="session_fake_public_id_three",
            session_key="fake_session_key",
            request_count=3,
            last_used=last_used,
            maximum_requests=None,
            expiry_time=expiry_time,
            password_change=False
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=False,
            login_sessions=[fake_login_session_one, fake_login_session_two, fake_login_session_three]
        )

        mock_query = _MockQuery([fake_user])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsSession.clean_user(
            user_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert response[0] == True
        assert response[1] == None

        assert len(mock_session._deletes) == 3
        deleted_ids = [
            mock_session._deletes[0].public_id,
            mock_session._deletes[1].public_id,
            mock_session._deletes[2].public_id
        ]
        assert "session_fake_public_id_one" in deleted_ids
        assert "session_fake_public_id_two" in deleted_ids
        assert "session_fake_public_id_three" in deleted_ids
        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "id"
        assert condition.right.value == 123456


if __name__ == '__main__':
    pytest.main(['-v', __file__])
