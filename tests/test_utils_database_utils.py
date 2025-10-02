import os
import sys
import pytest
from typing import Optional, Callable

from sqlalchemy.exc import IntegrityError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database_utils import DatabaseUtils
from utils.utils_enums import FailureReason
from database.database_setup import DatabaseSetup
from database.database_models import User


class _FakeQuery:
    def __init__(self, results):
        self._results = results

    def filter(self, condition):
        return self

    def first(self):
        return self._results[0] if self._results else None


class _FakeSession:
    def __init__(self, on_commit: Optional[Callable[[], None]] = None):
        self._added = []
        self.commits = 0
        self.rollbacks = 0
        self.closed = False
        self._on_commit = on_commit

    def add(self, obj):
        self._added.append(obj)

    def commit(self):
        self.commits += 1
        if self._on_commit:
            self._on_commit()

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True

    def query(self):
        pass


def _prepare_fake_session(test_class, monkeypatch, exception_message : Optional[str] = None):
    """Prepare a Fake Session with the given exception on commit"""
    if exception_message:
        def raise_exception():
            raise IntegrityError(exception_message, params=None, orig=Exception("Fake exception"))
        test_class._fake_session = _FakeSession(on_commit=raise_exception)
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: test_class._fake_session))
    else:
        test_class._fake_session = _FakeSession()
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: test_class._fake_session))

def _prepare_db_not_initialised_error(monkeypatch):
    def _raise_runtime_error():
        raise RuntimeError("Database not initialised.")
    monkeypatch.setattr(DatabaseSetup, "get_session", lambda: _raise_runtime_error)


def _fake_query_response(monkeypatch, response_list):
    def fake_query(self, model):
        return _FakeQuery(response_list)
    monkeypatch.setattr(_FakeSession, "query", fake_query)


class TestCreateUser():
    """Test cases for the database utilities create_user function"""

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


class TestChangeUsername():
    """Test cases for the database utilities change_username function"""

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
        db_user = self._fake_session._added[0]
        assert db_user.username_hash == "new_fake_hash"
        assert self._fake_session.commits == 1
        assert self._fake_session.rollbacks == 0
        assert self._fake_session.closed is True


if __name__ == '__main__':
    pytest.main(['-v', __file__])
