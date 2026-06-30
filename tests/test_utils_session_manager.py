import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from utils.session_manager import SessionManager
from utils.db_utils_auth import DBUtilsAuth
from enums.failure_reason import FailureReason


class TestStartNewSession():
    """Test cases for the start new session function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.fetch_called = []
        self.fetch_response = True, None, 123, b'fake_srp_salt', b'fake_srp_verifier'
        def fake_fetch(username_hash):
            self.fetch_called.append(username_hash)
            return self.fetch_response
        monkeypatch.setattr(DBUtilsAuth, "fetch", fake_fetch)

        yield

    @pytest.mark.parametrize(
        "username_hash",
        [
            (b'abc'),
            (b''),
            (b'123'*8)
        ]
    )
    def test_calls_fetch(self, username_hash):
        """Should fetch srp salt and verifier for the user"""

        result = SessionManager.start_new_session(username_hash)

        assert len(self.fetch_called) == 1
        assert self.fetch_called[0] == username_hash

    @pytest.mark.parametrize(
        "failure_reason",
        [
            FailureReason.NOT_FOUND,
            FailureReason.DATABASE_UNINITIALISED,
            FailureReason.UNKNOWN_EXCEPTION
        ]
    )
    def test_fetch_fails(self, failure_reason):
        """Should return error if fetch fails"""

        self.fetch_response = False, failure_reason, 0, b'', b''

        result = SessionManager.start_new_session(b'fake_username_hash')

        assert not result[0]
        assert result[1] == failure_reason


if __name__ == '__main__':
    pytest.main(['-v', __file__])
