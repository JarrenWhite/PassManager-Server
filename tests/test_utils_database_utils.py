import os
import sys
import pytest
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.mock_classes import _MockSession, _MockQuery

from utils.database_utils import DatabaseUtils
from utils.utils_enums import FailureReason
from database.database_setup import DatabaseSetup
from database.database_models import User, AuthEphemeral, LoginSession


class TestUserCreate():
    """Test cases for the database utils user_create function"""

    def test_nominal_case(self, monkeypatch):
        """Should create user and add to Database"""
        mock_session = _MockSession()
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        response = DatabaseUtils.user_create(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert response[0] == True
        assert response[1] == None

        assert len(mock_session._added) == 1
        assert len(mock_session._deletes) == 0
        db_user = mock_session._added[0]
        assert isinstance(db_user, User)
        assert db_user.username_hash == "fake_hash"
        assert db_user.srp_salt == "fake_srp_salt"
        assert db_user.srp_verifier == "fake_srp_verifier"
        assert db_user.master_key_salt == "fake_master_key_salt"
        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        def _raise_runtime_error():
            raise RuntimeError("Database not initialised.")
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: _raise_runtime_error)

        response = DatabaseUtils.user_create(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
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
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        response = DatabaseUtils.user_create(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.UNKNOWN_EXCEPTION

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 1
        assert mock_session.closed is True

    def test_handles_unique_constraint_failure(self, monkeypatch):
        """Should return correct failure reason if username hash exists"""
        def raise_exception():
            raise IntegrityError("unique constraint failed", params=None, orig=Exception("Fake exception"))
        mock_session = _MockSession(on_commit=raise_exception)
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        mock_session.add(
            User(
                username_hash="fake_hash",
                srp_salt="fake_srp_salt",
                srp_verifier="fake_srp_verifier",
                master_key_salt="fake_master_key_salt"
            )
        )

        response = DatabaseUtils.user_create(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.DUPLICATE

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 1
        assert mock_session.closed is True


class TestUserChangeUsername():
    """Test cases for the database utils user_change_username function"""

    def test_nominal_case(self, monkeypatch):
        """Should change username of given user"""
        mock_session = _MockSession()
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        fake_user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )

        def fake_query(self, model):
            return _MockQuery([fake_user])
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DatabaseUtils.user_change_username(
            username_hash="fake_hash",
            new_username_hash="new_fake_hash"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert response[0] == True
        assert response[1] == None

        assert len(mock_session._added) == 0
        assert len(mock_session._deletes) == 0
        assert fake_user.username_hash == "new_fake_hash"
        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        def _raise_runtime_error():
            raise RuntimeError("Database not initialised.")
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: _raise_runtime_error)

        response = DatabaseUtils.user_change_username(
            username_hash="fake_hash",
            new_username_hash="new_fake_hash"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.DATABASE_UNINITIALISED

    def test_handles_unique_constraint_failure(self, monkeypatch):
        """Should return correct failure reason if new username hash already exists"""
        def raise_exception():
            raise IntegrityError("unique constraint failed", params=None, orig=Exception("Fake exception"))
        mock_session = _MockSession(on_commit=raise_exception)
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        fake_user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )

        def fake_query(self, model):
            return _MockQuery([fake_user])
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DatabaseUtils.user_change_username(
            username_hash="fake_hash",
            new_username_hash="new_fake_hash"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.DUPLICATE

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 1
        assert mock_session.closed is True

    def test_handles_server_exception(self, monkeypatch):
        """Should return correct failure reason if other exception seen"""
        def raise_unknown_exception():
            raise ValueError("Something went wrong")
        mock_session = _MockSession(on_commit=raise_unknown_exception)
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        response = DatabaseUtils.user_change_username(
            username_hash="fake_hash",
            new_username_hash="new_fake_hash"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.UNKNOWN_EXCEPTION

        assert mock_session.commits == 0
        assert mock_session.rollbacks == 1
        assert mock_session.closed is True

    def test_entry_not_found(self, monkeypatch):
        """Should return correct failure reason if entry is not found"""
        mock_session = _MockSession()
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        def fake_query(self, model):
            return _MockQuery([None])
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DatabaseUtils.user_change_username(
            username_hash="fake_hash",
            new_username_hash="new_fake_hash"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True


class TestUserDelete():
    """Test cases for database utils user_delete function"""

    def test_nominal_case(self, monkeypatch):
        """Should delete given user"""
        mock_session = _MockSession()
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        fake_user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        mock_session.add(fake_user)

        def fake_query(self, model):
            return _MockQuery([fake_user])
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DatabaseUtils.user_delete(
            username_hash="fake_hash"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert response[0] == True
        assert response[1] == None

        assert len(mock_session._added) == 1
        assert len(mock_session._deletes) == 1
        db_user = mock_session._deletes[0]
        assert db_user.username_hash == "fake_hash"
        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        def _raise_runtime_error():
            raise RuntimeError("Database not initialised.")
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: _raise_runtime_error)

        response = DatabaseUtils.user_delete(
            username_hash="fake_hash"
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
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        response = DatabaseUtils.user_delete(
            username_hash="fake_hash"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.UNKNOWN_EXCEPTION

        assert mock_session.commits == 0
        assert mock_session.rollbacks == 1
        assert mock_session.closed is True

    def test_entry_not_found(self, monkeypatch):
        """Should return correct failure reason if entry is not found"""
        mock_session = _MockSession()
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        def fake_query(self, model):
            return _MockQuery([None])
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DatabaseUtils.user_delete(
            username_hash="fake_hash"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True


class TestSessionStartAuth():
    """Test cases for database utils session_start_auth function"""

    def test_nominal_case(self, monkeypatch):
        """Should create auth ephemeral & fetch srp_salt"""
        mock_session = _MockSession()
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )

        def fake_query(self, model):
            return _MockQuery([fake_user])
        monkeypatch.setattr(_MockSession, "query", fake_query)

        monkeypatch.setattr(AuthEphemeral, "public_id", "fake_public_id")

        expiry = datetime.now() + timedelta(hours=1)
        response = DatabaseUtils.session_start_auth(
            username_hash="fake_hash",
            ephemeral_b="fake_ephemeral_b",
            expires_at=expiry
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[2], str)
        assert isinstance(response[3], str)
        assert response[0] == True
        assert response[1] == None
        assert response[2] == "fake_public_id"
        assert response[3] == "fake_srp_salt"

        assert len(mock_session._added) == 1
        assert len(mock_session._deletes) == 0
        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        db_ephemeral = mock_session._added[0]
        assert isinstance(db_ephemeral, AuthEphemeral)
        assert db_ephemeral.public_id == "fake_public_id"
        assert db_ephemeral.ephemeral_b == "fake_ephemeral_b"
        assert db_ephemeral.expires_at == expiry
        assert db_ephemeral.password_change == None

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        def _raise_runtime_error():
            raise RuntimeError("Database not initialised.")
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: _raise_runtime_error)

        expiry = datetime.now() + timedelta(hours=1)
        response = DatabaseUtils.session_start_auth(
            username_hash="fake_hash",
            ephemeral_b="fake_ephemeral_b",
            expires_at=expiry
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
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        expiry = datetime.now() + timedelta(hours=1)
        response = DatabaseUtils.session_start_auth(
            username_hash="fake_hash",
            ephemeral_b="fake_ephemeral_b",
            expires_at=expiry
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.UNKNOWN_EXCEPTION

        assert mock_session.commits == 0
        assert mock_session.rollbacks == 1
        assert mock_session.closed is True

    def test_entry_not_found(self, monkeypatch):
        """Should return correct failure reason if entry is not found"""
        mock_session = _MockSession()
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        def fake_query(self, model):
            return _MockQuery([None])
        monkeypatch.setattr(_MockSession, "query", fake_query)

        expiry = datetime.now() + timedelta(hours=1)
        response = DatabaseUtils.session_start_auth(
            username_hash="fake_hash",
            ephemeral_b="fake_ephemeral_b",
            expires_at=expiry
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True


class TestSessionCompleteAuth():
    """Test cases for database utils session_complete_auth function"""

    def test_nominal_case_minimal_inputs(self, monkeypatch):
        """Should create login session & fetch srp_salt with minimal inputs"""
        mock_session = _MockSession()
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )

        expiry = datetime.now() + timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            ephemeral_b="fake_ephemeral_b",
            expires_at=expiry
        )

        def fake_query(self, model):
            return _MockQuery([fake_ephemeral])
        monkeypatch.setattr(_MockSession, "query", fake_query)

        monkeypatch.setattr(LoginSession, "public_id", "session_fake_public_id")

        response = DatabaseUtils.session_complete_auth(
            public_id="session_fake_public_id",
            session_key="fake_session_key",
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
        assert db_session.maximum_requests == None
        assert db_session.expiry_time == None
        assert db_session.password_change == None

    def test_nominal_case_maximal_inputs(self, monkeypatch):
        """Should create login session & fetch srp_salt with maximal inputs"""
        mock_session = _MockSession()
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )

        expiry = datetime.now() + timedelta(hours=1)
        fake_ephemeral = AuthEphemeral(
            user=fake_user,
            public_id="ephemeral_fake_public_id",
            ephemeral_b="fake_ephemeral_b",
            expires_at=expiry
        )

        def fake_query(self, model):
            return _MockQuery([fake_ephemeral])
        monkeypatch.setattr(_MockSession, "query", fake_query)

        monkeypatch.setattr(LoginSession, "public_id", "session_fake_public_id")

        expiry = datetime.now() + timedelta(hours=1)
        response = DatabaseUtils.session_complete_auth(
            public_id="session_fake_public_id",
            session_key="fake_session_key",
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
        assert db_session.session_key == "fake_session_key"
        assert db_session.request_count == 0
        assert db_session.last_used < datetime.now()
        assert db_session.last_used > datetime.now() - timedelta(seconds=2)
        assert db_session.maximum_requests == 99
        assert db_session.expiry_time == expiry
        assert db_session.password_change == None

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        def _raise_runtime_error():
            raise RuntimeError("Database not initialised.")
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: _raise_runtime_error)

        expiry = datetime.now() + timedelta(hours=1)
        response = DatabaseUtils.session_complete_auth(
            public_id="session_fake_public_id",
            session_key="fake_session_key",
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
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        expiry = datetime.now() + timedelta(hours=1)
        response = DatabaseUtils.session_complete_auth(
            public_id="session_fake_public_id",
            session_key="fake_session_key",
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

    def test_entry_not_found(self, monkeypatch):
        """Should return correct failure reason if entry is not found"""
        mock_session = _MockSession()
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: mock_session))

        def fake_query(self, model):
            return _MockQuery([None])
        monkeypatch.setattr(_MockSession, "query", fake_query)

        expiry = datetime.now() + timedelta(hours=1)
        response = DatabaseUtils.session_complete_auth(
            public_id="session_fake_public_id",
            session_key="fake_session_key",
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


if __name__ == '__main__':
    pytest.main(['-v', __file__])
