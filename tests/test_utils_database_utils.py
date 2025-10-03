import os
import sys
import pytest
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_utils import _FakeSession, _prepare_fake_session, _prepare_db_not_initialised_error, _fake_query_response

from utils.database_utils import DatabaseUtils
from utils.utils_enums import FailureReason
from database.database_setup import DatabaseSetup
from database.database_models import User, AuthEphemeral


class TestUserCreate():
    """Test cases for the database utils user_create function"""

    _fake_session: _FakeSession

    def test_nominal_case(self, monkeypatch):
        """Should create user and add to Database"""
        _prepare_fake_session(self, monkeypatch)

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

        assert len(self._fake_session._added) == 1
        assert len(self._fake_session._deletes) == 0
        db_user = self._fake_session._added[0]
        assert isinstance(db_user, User)
        assert db_user.username_hash == "fake_hash"
        assert db_user.srp_salt == "fake_srp_salt"
        assert db_user.srp_verifier == "fake_srp_verifier"
        assert db_user.master_key_salt == "fake_master_key_salt"
        assert self._fake_session.commits == 1
        assert self._fake_session.rollbacks == 0
        assert self._fake_session.closed is True

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        _prepare_db_not_initialised_error(monkeypatch)

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
        self._fake_session = _FakeSession(on_commit=raise_unknown_exception)
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: self._fake_session))

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

        assert self._fake_session.commits == 1
        assert self._fake_session.rollbacks == 1
        assert self._fake_session.closed is True

    def test_handles_unique_constraint_failure(self, monkeypatch):
        """Should return correct failure reason if username hash exists"""
        _prepare_fake_session(self, monkeypatch, "unique constraint failed")

        self._fake_session.add(
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

        assert self._fake_session.commits == 1
        assert self._fake_session.rollbacks == 1
        assert self._fake_session.closed is True


class TestUserChangeUsername():
    """Test cases for the database utils user_change_username function"""

    _fake_session: _FakeSession

    def test_nominal_case(self, monkeypatch):
        """Should change username of given user"""
        _prepare_fake_session(self, monkeypatch)

        fake_user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        self._fake_session.add(fake_user)

        _fake_query_response(monkeypatch, [fake_user])

        response = DatabaseUtils.user_change_username(
            username_hash="fake_hash",
            new_username_hash="new_fake_hash"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert response[0] == True
        assert response[1] == None

        assert len(self._fake_session._added) == 1
        assert len(self._fake_session._deletes) == 0
        db_user = self._fake_session._added[0]
        assert isinstance(db_user, User)
        assert db_user.username_hash == "new_fake_hash"
        assert self._fake_session.commits == 1
        assert self._fake_session.rollbacks == 0
        assert self._fake_session.closed is True

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        _prepare_db_not_initialised_error(monkeypatch)

        response = DatabaseUtils.user_change_username(
            username_hash="fake_hash",
            new_username_hash="new_fake_hash"
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
        self._fake_session = _FakeSession(on_commit=raise_unknown_exception)
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: self._fake_session))

        response = DatabaseUtils.user_change_username(
            username_hash="fake_hash",
            new_username_hash="new_fake_hash"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.UNKNOWN_EXCEPTION

        assert self._fake_session.commits == 0
        assert self._fake_session.rollbacks == 1
        assert self._fake_session.closed is True

    def test_entry_not_found(self, monkeypatch):
        """Should return correct failure reason if entry is not found"""
        _prepare_fake_session(self, monkeypatch, "")

        _fake_query_response(monkeypatch, [None])

        response = DatabaseUtils.user_change_username(
            username_hash="fake_hash",
            new_username_hash="new_fake_hash"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND

        assert self._fake_session.commits == 1
        assert self._fake_session.rollbacks == 0
        assert self._fake_session.closed is True


class TestUserDelete():
    """Test cases for database utils user_delete function"""

    _fake_session: _FakeSession

    def test_nominal_case(self, monkeypatch):
        """Should delete given user"""
        _prepare_fake_session(self, monkeypatch)

        fake_user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        self._fake_session.add(fake_user)

        _fake_query_response(monkeypatch, [fake_user])

        response = DatabaseUtils.user_delete(
            username_hash="fake_hash"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert response[0] == True
        assert response[1] == None

        assert len(self._fake_session._added) == 1
        assert len(self._fake_session._deletes) == 1
        db_user = self._fake_session._deletes[0]
        assert db_user.username_hash == "fake_hash"
        assert self._fake_session.commits == 1
        assert self._fake_session.rollbacks == 0
        assert self._fake_session.closed is True

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        _prepare_db_not_initialised_error(monkeypatch)

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
        self._fake_session = _FakeSession(on_commit=raise_unknown_exception)
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: self._fake_session))

        response = DatabaseUtils.user_delete(
            username_hash="fake_hash"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.UNKNOWN_EXCEPTION

        assert self._fake_session.commits == 0
        assert self._fake_session.rollbacks == 1
        assert self._fake_session.closed is True

    def test_entry_not_found(self, monkeypatch):
        """Should return correct failure reason if entry is not found"""
        _prepare_fake_session(self, monkeypatch, "")

        _fake_query_response(monkeypatch, [None])

        response = DatabaseUtils.user_delete(
            username_hash="fake_hash"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.NOT_FOUND

        assert self._fake_session.commits == 1
        assert self._fake_session.rollbacks == 0
        assert self._fake_session.closed is True


class TestSessionStartAuth():
    """Test cases for database utils session_start_auth function"""

    _fake_session: _FakeSession

    def test_nominal_case(self, monkeypatch):
        """Should create password change session """
        _prepare_fake_session(self, monkeypatch)

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        self._fake_session.add(fake_user)
        _fake_query_response(monkeypatch, [fake_user])

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

        assert len(self._fake_session._added) == 2
        assert len(self._fake_session._deletes) == 0
        db_user = self._fake_session._added[0]
        assert isinstance(db_user, User)
        assert db_user.username_hash == "fake_hash"
        assert self._fake_session.commits == 1
        assert self._fake_session.rollbacks == 0
        assert self._fake_session.closed is True

        db_ephemeral = self._fake_session._added[1]
        assert isinstance(db_ephemeral, AuthEphemeral)
        assert db_ephemeral.public_id == "fake_public_id"
        assert db_ephemeral.ephemeral_b == "fake_ephemeral_b"
        assert db_ephemeral.expires_at == expiry
        assert db_ephemeral.password_change == None

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        _prepare_db_not_initialised_error(monkeypatch)

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
        self._fake_session = _FakeSession(on_commit=raise_unknown_exception)
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: self._fake_session))

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

        assert self._fake_session.commits == 0
        assert self._fake_session.rollbacks == 1
        assert self._fake_session.closed is True

    def test_entry_not_found(self, monkeypatch):
        """Should return correct failure reason if entry is not found"""
        _prepare_fake_session(self, monkeypatch, "")

        _fake_query_response(monkeypatch, [None])

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

        assert self._fake_session.commits == 1
        assert self._fake_session.rollbacks == 0
        assert self._fake_session.closed is True


if __name__ == '__main__':
    pytest.main(['-v', __file__])
