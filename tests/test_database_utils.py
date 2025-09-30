import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database_utils import DatabaseUtils
from database.database_setup import DatabaseSetup


class _FakeSession:
    def __init__(self):
        self._added = []
        self.commits = 0
        self.refreshes = 0
        self.closed = False

    def add(self, obj):
        self._added.append(obj)

    def commit(self):
        self.commits += 1

    def refresh(self, obj):
        self.refreshes += 1

    def close(self):
        self.closed = True


class TestDatabaseUtils():
    """Test cases for the database utilities"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):
        self._fake_session = _FakeSession()
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: self._fake_session))

    def test_create_user(self):
        """Should create user and add to Database"""
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
        created_user = self._fake_session._added[0]
        assert created_user.username_hash == "fake_hash"
        assert created_user.srp_salt == "fake_srp_salt"
        assert created_user.srp_verifier == "fake_srp_verifier"
        assert created_user.master_key_salt == "fake_master_key_salt"
        assert self._fake_session.commits == 1
        assert self._fake_session.refreshes == 0
        assert self._fake_session.closed is True


if __name__ == '__main__':
    pytest.main(['-v', __file__])
