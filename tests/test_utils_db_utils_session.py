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
            password_changing=False
        )

        last_used = datetime.now() - timedelta(hours=1)
        fake_login_session = LoginSession(
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
        assert isinstance(response[2], str)
        assert isinstance(response[3], str)
        assert isinstance(response[4], int)
        assert response[0] == True
        assert response[1] == None
        assert response[2] == "fake_hash"
        assert response[3] == "fake_session_key"
        assert response[4] == 3

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


if __name__ == '__main__':
    pytest.main(['-v', __file__])
