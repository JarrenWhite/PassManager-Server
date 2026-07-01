import os
import sys
import pytest
import datetime

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import utils.session_manager
from utils.session_manager import SessionManager
from utils.db_utils_auth import DBUtilsAuth
from enums.failure_reason import FailureReason
from cryptography.srp_utils import SRPUtils


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

        self.generate_ephemeral_called = []
        self.generate_ephemeral_response = b'fake_public_ephemeral', b'fake_private_ephemeral'
        def fake_generate_ephemeral(srp_verifier_v):
            self.generate_ephemeral_called.append(srp_verifier_v)
            return self.generate_ephemeral_response
        monkeypatch.setattr(SRPUtils, "generate_ephemeral", fake_generate_ephemeral)

        self.now_response = datetime.datetime(2024, 1, 15, 12, 0, 0)
        class FakeDatetime(datetime.datetime):
            @classmethod
            def now(cls, tz=None):
                return self.now_response
        monkeypatch.setattr(utils.session_manager, "datetime", FakeDatetime)

        self.start_called = []
        self.start_response = True, None, "fake_public_id"
        def fake_start(user_id, eph_private_b, eph_public_b, expiry_time):
            self.start_called.append((user_id, eph_private_b, eph_public_b, expiry_time))
            return self.start_response
        monkeypatch.setattr(DBUtilsAuth, "start", fake_start)

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
        assert len(self.start_called) == 0

    @pytest.mark.parametrize(
        "srp_verifier",
        [
            (b'abc'),
            (b''),
            (b'123'*8)
        ]
    )
    def test_calls_generate_ephemeral(self, srp_verifier):
        """Should pass srp_verifier to generate_ephemeral"""

        self.fetch_response = True, None, 0, b'fake_srp_salt', srp_verifier

        result = SessionManager.start_new_session(b'fake_username_hash')

        assert len(self.generate_ephemeral_called) == 1
        assert self.generate_ephemeral_called[0] == srp_verifier

    @pytest.mark.parametrize(
        "user_id, eph_private_b, eph_public_b",
        [
            (0,     b'abc',     b'def'),
            (15,    b'',        b''),
            (350,   b'qcd'*100, b'ghi'*300)
        ]
    )
    def test_create_db_entry(self, user_id, eph_private_b, eph_public_b):
        """Should create entry in database with correct values"""

        self.fetch_response = True, None, user_id, b'fake_srp_salt', b'fake_srp_verifier'
        self.generate_ephemeral_response = eph_public_b, eph_private_b

        result = SessionManager.start_new_session(b'fake_username_hash')

        assert len(self.start_called) == 1

        start = self.start_called[0]
        assert start[0] == user_id
        assert start[1] == eph_private_b
        assert start[2] == eph_public_b

    @pytest.mark.parametrize(
        "now",
        [
            datetime.datetime(2024, 1, 15, 12, 0, 0),
            datetime.datetime(2000, 6, 1, 0, 0, 0),
            datetime.datetime(1999, 12, 31, 23, 59, 59)
        ]
    )
    def test_sets_correct_expiry(self, now):
        """Should create entry in database with correct expiry"""

        self.now_response = now

        result = SessionManager.start_new_session(b'fake_username_hash')

        assert len(self.start_called) == 1
        start = self.start_called[0]

        assert start[3] == self.now_response + datetime.timedelta(seconds=180)


if __name__ == '__main__':
    pytest.main(['-v', __file__])
