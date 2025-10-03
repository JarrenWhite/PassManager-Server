import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_utils import _FakeSession, _prepare_fake_session, _prepare_db_not_initialised_error, _fake_query_response

from utils.database_utils import DatabaseUtils
from utils.utils_enums import FailureReason
from database.database_setup import DatabaseSetup
from database.database_models import User


class TestCreateUser():
    """Test cases for the database utils create_user function"""

    _fake_session: _FakeSession

    def test_nominal_case(self, monkeypatch):
        """Should create user and add to Database"""
        _prepare_fake_session(self, monkeypatch)

        response = DatabaseUtils.create_user(
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

        response = DatabaseUtils.create_user(
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

        response = DatabaseUtils.create_user(
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

        response = DatabaseUtils.create_user(
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


class TestChangeUsername():
    """Test cases for the database utils change_username function"""

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

        response = DatabaseUtils.change_username(
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
        assert db_user.username_hash == "new_fake_hash"
        assert self._fake_session.commits == 1
        assert self._fake_session.rollbacks == 0
        assert self._fake_session.closed is True

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        _prepare_db_not_initialised_error(monkeypatch)

        response = DatabaseUtils.change_username(
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

        response = DatabaseUtils.change_username(
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

        response = DatabaseUtils.change_username(
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


class TestDeleteUser():
    """Test cases for database utils delete_user function"""

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

        response = DatabaseUtils.delete_user(
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

        response = DatabaseUtils.delete_user(
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

        response = DatabaseUtils.delete_user(
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

        response = DatabaseUtils.delete_user(
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


if __name__ == '__main__':
    pytest.main(['-v', __file__])
