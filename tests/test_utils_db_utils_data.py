import os
import sys
import pytest
from contextlib import contextmanager

from sqlalchemy.sql.elements import BinaryExpression

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.mock_classes import _MockSession, _MockQuery
from database.database_setup import DatabaseSetup
from utils.utils_enums import FailureReason
from utils.db_utils_data import DBUtilsData
from database.database_models import User, SecureData


class TestCreate():
    """Test cases for database utils data create function"""

    def test_nominal_case(self, monkeypatch):
        """Should create a data entry, with the given data"""
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

        monkeypatch.setattr(SecureData, "public_id", "fake_public_id")

        response = DBUtilsData.create(
            user_id=123456,
            entry_name="fake_encrypted_entry_name",
            entry_data="fake_encrypted_entry_data"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[2], str)
        assert response[0] == True
        assert response[1] == None
        assert response[2] == "fake_public_id"

        assert len(mock_session._added) == 1
        assert len(mock_session._deletes) == 0
        db_secure_data = mock_session._added[0]
        assert isinstance(db_secure_data, SecureData)
        assert db_secure_data.user.id == 123456
        assert db_secure_data.user.username_hash == "fake_hash"
        assert db_secure_data.entry_name == "fake_encrypted_entry_name"
        assert db_secure_data.entry_data == "fake_encrypted_entry_data"

        assert mock_session.commits == 1
        assert mock_session.flushes == 1
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

        response = DBUtilsData.create(
            user_id=123456,
            entry_name="fake_encrypted_entry_name",
            entry_data="fake_encrypted_entry_data"
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

        response = DBUtilsData.create(
            user_id=123456,
            entry_name="fake_encrypted_entry_name",
            entry_data="fake_encrypted_entry_data"
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

        response = DBUtilsData.create(
            user_id=123456,
            entry_name="fake_encrypted_entry_name",
            entry_data="fake_encrypted_entry_data"
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

    def test_handles_password_change(self, monkeypatch):
        """Should return correct error if user is in process of password change"""
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

        monkeypatch.setattr(SecureData, "public_id", "fake_public_id")

        response = DBUtilsData.create(
            user_id=123456,
            entry_name="fake_encrypted_entry_name",
            entry_data="fake_encrypted_entry_data"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.PASSWORD_CHANGE


class TestEdit():
    """Test cases for database utils data edit function"""

    def test_change_name(self, monkeypatch):
        """Should correctly change the entry name, without changing the entry data"""
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

        secure_data = SecureData(
            user=fake_user,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data"
        )

        mock_query = _MockQuery([secure_data])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsData.edit(
            public_id="fake_public_id",
            entry_name="new_fake_entry_name",
            entry_data=None
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert response[0] == True
        assert response[1] == None

        assert len(mock_session._added) == 0
        assert len(mock_session._deletes) == 0
        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "public_id"
        assert condition.right.value == "fake_public_id"

        assert secure_data.entry_name == "new_fake_entry_name"
        assert secure_data.entry_data == "fake_entry_data"

    def test_change_data(self, monkeypatch):
        """Should correctly change the entry data, without changing the entry name"""
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

        secure_data = SecureData(
            user=fake_user,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data"
        )

        mock_query = _MockQuery([secure_data])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsData.edit(
            public_id="fake_public_id",
            entry_name=None,
            entry_data="new_fake_entry_data"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert response[0] == True
        assert response[1] == None

        assert len(mock_session._added) == 0
        assert len(mock_session._deletes) == 0
        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "public_id"
        assert condition.right.value == "fake_public_id"

        assert secure_data.entry_name == "fake_entry_name"
        assert secure_data.entry_data == "new_fake_entry_data"

    def test_change_both_fields(self, monkeypatch):
        """Should correctly change both entry name and entry data"""
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

        secure_data = SecureData(
            user=fake_user,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data"
        )

        mock_query = _MockQuery([secure_data])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsData.edit(
            public_id="fake_public_id",
            entry_name="new_fake_entry_name",
            entry_data="new_fake_entry_data"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert response[0] == True
        assert response[1] == None

        assert len(mock_session._added) == 0
        assert len(mock_session._deletes) == 0
        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "public_id"
        assert condition.right.value == "fake_public_id"

        assert secure_data.entry_name == "new_fake_entry_name"
        assert secure_data.entry_data == "new_fake_entry_data"

    def test_change_neither_field(self, monkeypatch):
        """Should not change either field if neither option populated"""
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

        secure_data = SecureData(
            user=fake_user,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data"
        )

        mock_query = _MockQuery([secure_data])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsData.edit(
            public_id="fake_public_id",
            entry_name=None,
            entry_data=None
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert response[0] == True
        assert response[1] == None

        assert len(mock_session._added) == 0
        assert len(mock_session._deletes) == 0
        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "public_id"
        assert condition.right.value == "fake_public_id"

        assert secure_data.entry_name == "fake_entry_name"
        assert secure_data.entry_data == "fake_entry_data"

    def test_handles_database_unprepared_failure(self, monkeypatch):
        """Should return correct failure reason if database is not setup"""
        @contextmanager
        def mock_get_db_session():
            raise RuntimeError("Database not initialised.")
            yield
        monkeypatch.setattr(DatabaseSetup, "get_db_session", mock_get_db_session)

        response = DBUtilsData.edit(
            public_id="fake_public_id",
            entry_name=None,
            entry_data=None
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

        response = DBUtilsData.edit(
            public_id="fake_public_id",
            entry_name=None,
            entry_data=None
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

        response = DBUtilsData.edit(
            public_id="fake_public_id",
            entry_name=None,
            entry_data=None
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

    def test_handles_password_change(self, monkeypatch):
        """Should return correct error if user is in process of password change"""
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

        secure_data = SecureData(
            user=fake_user,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data"
        )

        mock_query = _MockQuery([secure_data])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsData.edit(
            public_id="fake_public_id",
            entry_name=None,
            entry_data=None
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.PASSWORD_CHANGE


class TestDelete():
    """Test cases for database utils data delete function"""

    def test_nominal_case(self, monkeypatch):
        """Should correctly delete the provided data entry"""
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

        secure_data = SecureData(
            user=fake_user,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data"
        )

        mock_query = _MockQuery([secure_data])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsData.delete(
            public_id="fake_public_id"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert response[0] == True
        assert response[1] == None

        assert len(mock_session._deletes) == 1
        db_session = mock_session._deletes[0]
        assert db_session.public_id == "fake_public_id"
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

        response = DBUtilsData.delete(
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

        response = DBUtilsData.delete(
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

        response = DBUtilsData.delete(
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

    def test_handles_password_change(self, monkeypatch):
        """Should return correct error if user is in process of password change"""
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

        secure_data = SecureData(
            user=fake_user,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data"
        )

        mock_query = _MockQuery([secure_data])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsData.delete(
            public_id="fake_public_id"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.PASSWORD_CHANGE


class TestGetEntry():
    """Test cases for database utils data get entry function"""

    def test_nominal_case(self, monkeypatch):
        """Should return correct details for the data item"""
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

        secure_data = SecureData(
            user=fake_user,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data"
        )

        mock_query = _MockQuery([secure_data])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsData.get_entry(
            public_id="fake_public_id"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[2], str)
        assert isinstance(response[3], str)
        assert response[0] == True
        assert response[1] == None
        assert response[2] == "fake_entry_name"
        assert response[3] == "fake_entry_data"

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

        response = DBUtilsData.get_entry(
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

        response = DBUtilsData.get_entry(
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

        response = DBUtilsData.get_entry(
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

    def test_handles_password_change(self, monkeypatch):
        """Should return correct error if user is in process of password change"""
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

        secure_data = SecureData(
            user=fake_user,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data"
        )

        mock_query = _MockQuery([secure_data])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsData.get_entry(
            public_id="fake_public_id"
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.PASSWORD_CHANGE

    def test_password_change_fetch(self, monkeypatch):
        """Should correctly fetch details for password change user if flag is true"""
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

        secure_data = SecureData(
            user=fake_user,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data"
        )

        mock_query = _MockQuery([secure_data])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsData.get_entry(
            public_id="fake_public_id",
            password_change=True
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[2], str)
        assert isinstance(response[3], str)
        assert response[0] == True
        assert response[1] == None
        assert response[2] == "fake_entry_name"
        assert response[3] == "fake_entry_data"

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "public_id"
        assert condition.right.value == "fake_public_id"


class TestGetList():
    """Test cases for database utils data get list function"""

    def test_no_data_entries(self, monkeypatch):
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
            password_change=False,
            secure_data=[]
        )

        mock_query = _MockQuery([fake_user])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsData.get_list(
            user_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[2], dict)
        assert response[0] == True
        assert response[1] == None
        assert response[2] == {}

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "id"
        assert condition.right.value == 123456

    def test_one_data_entry(self, monkeypatch):
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

        secure_data = SecureData(
            user_id=123456,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data"
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=False,
            secure_data=[secure_data]
        )

        mock_query = _MockQuery([fake_user])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsData.get_list(
            user_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[2], dict)
        assert response[0] == True
        assert response[1] == None
        assert len(response[2]) == 1
        assert "fake_public_id" in response[2]
        assert isinstance(response[2]["fake_public_id"], str)
        assert response[2]["fake_public_id"] == "fake_entry_name"

        assert mock_session.commits == 1
        assert mock_session.rollbacks == 0
        assert mock_session.closed is True

        assert len(mock_query._filters) == 1
        condition = mock_query._filters[0]
        assert isinstance(condition, BinaryExpression)
        assert str(condition.left.name) == "id"
        assert condition.right.value == 123456

    def test_multiple_data_entries(self, monkeypatch):
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

        secure_data_one = SecureData(
            user_id=123456,
            public_id="fake_public_id_one",
            entry_name="fake_entry_name_one",
            entry_data="fake_entry_data_one"
        )
        secure_data_two = SecureData(
            user_id=123457,
            public_id="fake_public_id_two",
            entry_name="fake_entry_name_two",
            entry_data="fake_entry_data_two"
        )
        secure_data_three = SecureData(
            user_id=123458,
            public_id="fake_public_id_three",
            entry_name="fake_entry_name_three",
            entry_data="fake_entry_data_three"
        )
        secure_data_four = SecureData(
            user_id=123459,
            public_id="fake_public_id_four",
            entry_name="fake_entry_name_four",
            entry_data="fake_entry_data_four"
        )
        secure_data_five = SecureData(
            user_id=123460,
            public_id="fake_public_id_five",
            entry_name="fake_entry_name_five",
            entry_data="fake_entry_data_five"
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=False,
            secure_data=[
                secure_data_one,
                secure_data_two,
                secure_data_three,
                secure_data_four,
                secure_data_five
            ]
        )

        mock_query = _MockQuery([fake_user])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsData.get_list(
            user_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[2], dict)
        assert response[0] == True
        assert response[1] == None
        assert len(response[2]) == 5

        assert "fake_public_id_one" in response[2]
        assert "fake_public_id_two" in response[2]
        assert "fake_public_id_three" in response[2]
        assert "fake_public_id_four" in response[2]
        assert "fake_public_id_five" in response[2]

        assert isinstance(response[2]["fake_public_id_one"], str)
        assert isinstance(response[2]["fake_public_id_two"], str)
        assert isinstance(response[2]["fake_public_id_three"], str)
        assert isinstance(response[2]["fake_public_id_four"], str)
        assert isinstance(response[2]["fake_public_id_five"], str)

        assert response[2]["fake_public_id_one"] == "fake_entry_name_one"
        assert response[2]["fake_public_id_two"] == "fake_entry_name_two"
        assert response[2]["fake_public_id_three"] == "fake_entry_name_three"
        assert response[2]["fake_public_id_four"] == "fake_entry_name_four"
        assert response[2]["fake_public_id_five"] == "fake_entry_name_five"

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

        response = DBUtilsData.get_list(
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

        response = DBUtilsData.get_list(
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

        response = DBUtilsData.get_list(
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

    def test_handles_password_change(self, monkeypatch):
        """Should return correct error if user is in process of password change"""
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

        secure_data = SecureData(
            user_id=123456,
            public_id="fake_public_id",
            entry_name="fake_entry_name",
            entry_data="fake_entry_data"
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            secure_data=[secure_data]
        )

        mock_query = _MockQuery([fake_user])
        def fake_query(self, model):
            return mock_query
        monkeypatch.setattr(_MockSession, "query", fake_query)

        response = DBUtilsData.get_list(
            user_id=123456
        )

        assert isinstance(response, tuple)
        assert isinstance(response[0], bool)
        assert isinstance(response[1], FailureReason)
        assert response[0] == False
        assert response[1] == FailureReason.PASSWORD_CHANGE


if __name__ == '__main__':
    pytest.main(['-v', __file__])
