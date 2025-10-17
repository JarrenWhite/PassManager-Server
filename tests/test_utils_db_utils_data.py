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
    """Test cases for database utils auth create function"""

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


if __name__ == '__main__':
    pytest.main(['-v', __file__])
