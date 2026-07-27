import os
import sys
import pytest
import datetime

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import utils.session_manager
from utils.session_manager import SessionManager
from utils.db_utils_auth import DBUtilsAuth
from utils.db_utils_password import DBUtilsPassword
from enums.failure_reason import FailureReason
from cryptography.srp_utils import SRPUtils


class TestStartNewSession():
    """Test cases for the start new session function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.fetch_called = []
        self.fetch_response = True, None, 123, b'fake_srp_salt', b'fake_srp_verifier'
        def fake_fetch(username_hash = None, user_id = None):
            self.fetch_called.append((username_hash, user_id))
            return self.fetch_response
        monkeypatch.setattr(DBUtilsAuth, "fetch", fake_fetch)

        self.generate_ephemeral_called = []
        self.generate_ephemeral_response = b'fake_public_ephemeral', b'fake_private_ephemeral'
        def fake_generate_ephemeral(srp_verifier_v):
            self.generate_ephemeral_called.append(srp_verifier_v)
            return self.generate_ephemeral_response
        monkeypatch.setattr(SRPUtils, "generate_ephemeral", fake_generate_ephemeral)

        self.start_called = []
        self.start_response = True, None, "fake_public_id", b'fake_master_key_salt'
        def fake_start(user_id, eph_private_b, eph_public_b, expiry_time):
            self.start_called.append((user_id, eph_private_b, eph_public_b, expiry_time))
            return self.start_response
        monkeypatch.setattr(DBUtilsAuth, "start", fake_start)

        self.now_response = datetime.datetime(2024, 1, 15, 12, 0, 0)
        class FakeDatetime(datetime.datetime):
            @classmethod
            def now(cls, tz=None):
                return self.now_response
        monkeypatch.setattr(utils.session_manager, "datetime", FakeDatetime)

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

        fetch = self.fetch_called[0]
        assert fetch[0] == username_hash
        assert fetch[1] == None

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

        assert start[3] == now + datetime.timedelta(seconds=180)

    @pytest.mark.parametrize(
        "failure_reason",
        [
            FailureReason.NOT_FOUND,
            FailureReason.DATABASE_UNINITIALISED,
            FailureReason.UNKNOWN_EXCEPTION
        ]
    )
    def test_start_call_fails(self, failure_reason):
        """Should correctly handle failed start call"""

        self.start_response = False, failure_reason, "", b''

        result = SessionManager.start_new_session(b'fake_username_hash')

        assert not result[0]
        assert result[1] == failure_reason

    @pytest.mark.parametrize(
        "public_id, eph_public_b, srp_salt, master_key_salt",
        [
            ("abc",     b'abc',     b'def',     b'hij'),
            ("",        b'',        b'',        b''),
            ("def"*150, b'qcd'*100, b'ghi'*300, b'qew'*125)
        ]
    )
    def test_returns_correct_values(self, public_id, eph_public_b, srp_salt, master_key_salt):
        """Should return all correct values"""
        self.fetch_response = True, None, 1, srp_salt, b'fake_srp_verifier'
        self.start_response = True, None, public_id, master_key_salt
        self.generate_ephemeral_response = eph_public_b, b'fake_private_ephemeral'

        result = SessionManager.start_new_session(b'fake_username_hash')

        assert result[0]
        assert result[1] is None
        assert result[2] == public_id
        assert result[3] == eph_public_b
        assert result[4] == srp_salt
        assert result[5] == master_key_salt


class TestAuthNewSession():
    """Test cases for the auth new session function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.get_details_called = []
        self.get_details_response = True, None, b'fake_eph_private_b', b'fake_eph_public_b', b'fake_srp_verifier'
        def fake_get_details(public_id, user_id = None, username_hash = None):
            self.get_details_called.append((public_id, user_id, username_hash))
            return self.get_details_response
        monkeypatch.setattr(DBUtilsAuth, "get_details", fake_get_details)

        self.compute_session_key_called = []
        self.compute_session_key_response = b''
        def fake_compute_session_key(eph_val_a, eph_public_b, eph_private_b, srp_verifier_v):
            self.compute_session_key_called.append((eph_val_a, eph_public_b, eph_private_b, srp_verifier_v))
            return self.compute_session_key_response
        monkeypatch.setattr(SRPUtils, "compute_session_key", fake_compute_session_key)

        self.verify_proof_called = []
        self.verify_proof_response  = True, b'fake_server_proof'
        def fake_verify_proof(eph_val_a, eph_public_b, session_key_k, proof_val_m1):
            self.verify_proof_called.append((eph_val_a, eph_public_b, session_key_k, proof_val_m1))
            return self.verify_proof_response
        monkeypatch.setattr(SRPUtils, "verify_proof", fake_verify_proof)

        self.complete_called = []
        self.complete_response = True, None, "fake_session_public_id"
        def fake_complete(public_id, session_key, maximum_requests, expiry_time):
            self.complete_called.append((public_id, session_key, maximum_requests, expiry_time))
            return self.complete_response
        monkeypatch.setattr(DBUtilsAuth, "complete", fake_complete)

        self.now_response = datetime.datetime(2024, 1, 15, 12, 0, 0)
        class FakeDatetime(datetime.datetime):
            @classmethod
            def now(cls, tz=None):
                return self.now_response
        monkeypatch.setattr(utils.session_manager, "datetime", FakeDatetime)

        yield

    @pytest.mark.parametrize(
        "username_hash, public_id",
        [
            (b'abc',     "abc"),
            (b'',        ""),
            (b'qcd'*100, "def"*150)
        ]
    )
    def test_calls_get_details(self, username_hash, public_id):
        """Should fetch ephemeral details"""

        result = SessionManager.auth_new_session(
            username_hash=username_hash,
            public_id=public_id,
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_b1',
            maximum_requests=0,
            expiry_time=0
        )

        assert len(self.get_details_called) == 1

        get_details = self.get_details_called[0]
        assert get_details[0] == public_id
        assert get_details[1] == None
        assert get_details[2] == username_hash

    @pytest.mark.parametrize(
        "failure_reason",
        [
            FailureReason.NOT_FOUND,
            FailureReason.DATABASE_UNINITIALISED,
            FailureReason.UNKNOWN_EXCEPTION
        ]
    )
    def test_get_details_fails(self, failure_reason):
        """Should handle get_details failure"""

        self.get_details_response = False, failure_reason, b'', b'', b''

        result = SessionManager.auth_new_session(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_b1',
            maximum_requests=0,
            expiry_time=0
        )

        assert not result[0]
        assert result[1] == failure_reason
        assert len(self.complete_called) == 0

    @pytest.mark.parametrize(
        "eph_val_a, eph_public_b, eph_private_b, srp_verifier_v",
        [
            (b'xyz',    b'abc',     b'def',     b'hij'),
            (b'',       b'',        b'',        b''),
            (b'def'*150,b'qcd'*100, b'ghi'*300, b'qew'*125)
        ]
    )
    def test_calls_compute_session_key(self, eph_val_a, eph_public_b, eph_private_b, srp_verifier_v):
        """Should call to compute session key"""

        self.get_details_response = True, None, eph_private_b, eph_public_b, srp_verifier_v

        result = SessionManager.auth_new_session(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=eph_val_a,
            proof_val_m1=b'fake_proof_val_b1',
            maximum_requests=0,
            expiry_time=0
        )

        assert len(self.compute_session_key_called) == 1

        compute_session_key = self.compute_session_key_called[0]
        assert compute_session_key[0] == eph_val_a
        assert compute_session_key[1] == eph_public_b
        assert compute_session_key[2] == eph_private_b
        assert compute_session_key[3] == srp_verifier_v

    @pytest.mark.parametrize(
        "eph_val_a, eph_public_b, session_key_k, proof_val_m1",
        [
            (b'xyz',    b'abc',     b'def',     b'hij'),
            (b'',       b'',        b'',        b''),
            (b'def'*150,b'qcd'*100, b'ghi'*300, b'qew'*125)
        ]
    )
    def test_calls_verify_proof(self, eph_val_a, eph_public_b, session_key_k, proof_val_m1):
        """Should call to verify client proof"""

        self.get_details_response = True, None, b'fake_eph_private_b', eph_public_b, b'fake_srp_verifier'
        self.compute_session_key_response = session_key_k

        result = SessionManager.auth_new_session(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=eph_val_a,
            proof_val_m1=proof_val_m1,
            maximum_requests=0,
            expiry_time=0
        )

        assert len(self.verify_proof_called) == 1

        verify_proof = self.verify_proof_called[0]
        assert verify_proof[0] == eph_val_a
        assert verify_proof[1] == eph_public_b
        assert verify_proof[2] == session_key_k
        assert verify_proof[3] == proof_val_m1

    def test_verify_proof_fails(self):
        """Should handle verify proof failure"""

        self.verify_proof_response = False, b''

        result = SessionManager.auth_new_session(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_b1',
            maximum_requests=0,
            expiry_time=0
        )

        assert not result[0]
        assert result[1] == FailureReason.NOT_FOUND
        assert len(self.complete_called) == 0

    @pytest.mark.parametrize(
        "public_id, session_key",
        [
            ("abc",     b'abc'),
            ("",        b''),
            ("def"*150, b'qcd'*100)
        ]
    )
    def test_calls_complete(self, public_id, session_key):
        """Should call to complete auth"""

        self.compute_session_key_response = session_key

        result = SessionManager.auth_new_session(
            username_hash=b'fake_username_hash',
            public_id=public_id,
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_b1',
            maximum_requests=0,
            expiry_time=0
        )

        assert len(self.complete_called) == 1

        complete = self.complete_called[0]
        assert complete[0] == public_id
        assert complete[1] == session_key

    @pytest.mark.parametrize(
        "maximum_requests, passed_argument",
        [
            (-30,   None),
            (-1,    None),
            (0,     100),
            (15,    15),
            (100,   100)
        ]
    )
    def test_complete_max_requests(self, maximum_requests, passed_argument):
        """Should call complete with correct maximum requests"""

        result = SessionManager.auth_new_session(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_b1',
            maximum_requests=maximum_requests,
            expiry_time=0
        )

        complete = self.complete_called[0]

        assert complete[2] == passed_argument

    @pytest.mark.parametrize(
        "expiry_time, now",
        [
            (-1,    datetime.datetime(2024, 1, 15, 12, 0, 0)),
            (0,     datetime.datetime(2000, 6, 1, 0, 0, 0)),
            (86400, datetime.datetime(2005, 8, 6, 22, 8, 8)),
            (604800,datetime.datetime(1999, 12, 31, 23, 59, 59))
        ]
    )
    def test_sets_correct_expiry(self, expiry_time, now):
        """Should create entry in database with correct expiry"""

        self.now_response = now

        result = SessionManager.auth_new_session(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_b1',
            maximum_requests=0,
            expiry_time=expiry_time
        )

        complete = self.complete_called[0]

        if expiry_time < 0:
            expected_expiry = None
        elif expiry_time == 0:
            expected_expiry = now + datetime.timedelta(seconds=3600)
        else:
            expected_expiry = now + datetime.timedelta(seconds=expiry_time)

        assert complete[3] == expected_expiry

    @pytest.mark.parametrize(
        "failure_reason",
        [
            FailureReason.NOT_FOUND,
            FailureReason.DATABASE_UNINITIALISED,
            FailureReason.UNKNOWN_EXCEPTION
        ]
    )
    def test_complete_fails(self, failure_reason):
        """Should handle failure of complete call"""

        self.complete_response = False, failure_reason, ""

        result = SessionManager.auth_new_session(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_b1',
            maximum_requests=0,
            expiry_time=0
        )

        assert not result[0]
        assert result[1] == failure_reason

    @pytest.mark.parametrize(
        "session_public_id, server_proof_val_m2",
        [
            ("abc",     b'abc'),
            ("",        b''),
            ("def"*150, b'qcd'*100)
        ]
    )
    def test_returns_correct_values(self, session_public_id, server_proof_val_m2):
        """Should return the correct final values"""

        self.verify_proof_response = True, server_proof_val_m2
        self.complete_response = True, None, session_public_id

        result = SessionManager.auth_new_session(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_b1',
            maximum_requests=0,
            expiry_time=0
        )

        assert result[2] == session_public_id
        assert result[3] == server_proof_val_m2


class TestStartPasswordSession():
    """Test cases for the start password session function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.fetch_called = []
        self.fetch_response = True, None, 123, b'fake_srp_salt', b'fake_srp_verifier'
        def fake_fetch(username_hash = None, user_id = None):
            self.fetch_called.append((username_hash, user_id))
            return self.fetch_response
        monkeypatch.setattr(DBUtilsAuth, "fetch", fake_fetch)

        self.generate_ephemeral_called = []
        self.generate_ephemeral_response = b'fake_public_ephemeral', b'fake_private_ephemeral'
        def fake_generate_ephemeral(srp_verifier_v):
            self.generate_ephemeral_called.append(srp_verifier_v)
            return self.generate_ephemeral_response
        monkeypatch.setattr(SRPUtils, "generate_ephemeral", fake_generate_ephemeral)

        self.start_called = []
        self.start_response = True, None, "fake_public_id", b'fake_master_key_salt'
        def fake_start(user_id, eph_private_b, eph_public_b, expiry_time, srp_salt, srp_verifier, master_key_salt):
            self.start_called.append((user_id, eph_private_b, eph_public_b, expiry_time, srp_salt, srp_verifier, master_key_salt))
            return self.start_response
        monkeypatch.setattr(DBUtilsPassword, "start", fake_start)

        self.now_response = datetime.datetime(2024, 1, 15, 12, 0, 0)
        class FakeDatetime(datetime.datetime):
            @classmethod
            def now(cls, tz=None):
                return self.now_response
        monkeypatch.setattr(utils.session_manager, "datetime", FakeDatetime)

        yield

    @pytest.mark.parametrize(
        "user_id",
        [
            123,
            0,
            789456
        ]
    )
    def test_calls_fetch(self, user_id):
        """Should fetch srp salt and verifier for the user"""

        result = SessionManager.start_password_session(
            user_id,
            b'fake_srp_salt',
            b'fake_srp_verifier',
            b'fake_master_key_salt'
        )

        assert len(self.fetch_called) == 1

        fetch = self.fetch_called[0]
        assert fetch[0] == None
        assert fetch[1] == user_id

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

        result = SessionManager.start_password_session(
            123,
            b'fake_srp_salt',
            b'fake_srp_verifier',
            b'fake_master_key_salt'
        )

        assert not result[0]
        assert result[1] == failure_reason

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

        result = SessionManager.start_password_session(
            123,
            b'fake_srp_salt',
            b'fake_srp_verifier',
            b'fake_master_key_salt'
        )

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
    def test_create_db_entry_for_ephemerals(self, user_id, eph_private_b, eph_public_b):
        """Should create entry in database with correct ephemeral values"""

        self.fetch_response = True, None, user_id, b'fake_srp_salt', b'fake_srp_verifier'
        self.generate_ephemeral_response = eph_public_b, eph_private_b

        result = SessionManager.start_password_session(
            123,
            b'fake_srp_salt',
            b'fake_srp_verifier',
            b'fake_master_key_salt'
        )

        assert len(self.start_called) == 1

        start = self.start_called[0]
        assert start[0] == user_id
        assert start[1] == eph_private_b
        assert start[2] == eph_public_b

    @pytest.mark.parametrize(
        "srp_salt, srp_verifier, master_key_salt",
        [
            (b'abc',     b'def',    b'hij'),
            (b'',        b'',       b''),
            (b'qcd'*100, b'ghi'*300,b'red'*125)
        ]
    )
    def test_create_db_entry_for_master_password(self, srp_salt, srp_verifier, master_key_salt):
        """Should create entry in database with correct master password values"""

        self.fetch_response = True, None, 1, b'fake_srp_salt', b'fake_srp_verifier'

        result = SessionManager.start_password_session(
            123,
            srp_salt,
            srp_verifier,
            master_key_salt
        )

        assert len(self.start_called) == 1

        start = self.start_called[0]
        assert start[4] == srp_salt
        assert start[5] == srp_verifier
        assert start[6] == master_key_salt

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

        result = SessionManager.start_password_session(
            123,
            b'fake_srp_salt',
            b'fake_srp_verifier',
            b'fake_master_key_salt'
        )

        assert len(self.start_called) == 1
        start = self.start_called[0]

        assert start[3] == now + datetime.timedelta(seconds=180)

    @pytest.mark.parametrize(
        "failure_reason",
        [
            FailureReason.NOT_FOUND,
            FailureReason.DATABASE_UNINITIALISED,
            FailureReason.UNKNOWN_EXCEPTION
        ]
    )
    def test_start_call_fails(self, failure_reason):
        """Should correctly handle failed start call"""

        self.start_response = False, failure_reason, "", b''

        result = SessionManager.start_password_session(
            123,
            b'fake_srp_salt',
            b'fake_srp_verifier',
            b'fake_master_key_salt'
        )

        assert not result[0]
        assert result[1] == failure_reason

    @pytest.mark.parametrize(
        "public_id, eph_public_b, srp_salt, master_key_salt",
        [
            ("abc",     b'abc',     b'def',     b'hij'),
            ("",        b'',        b'',        b''),
            ("def"*150, b'qcd'*100, b'ghi'*300, b'qew'*125)
        ]
    )
    def test_returns_correct_values(self, public_id, eph_public_b, srp_salt, master_key_salt):
        """Should return all correct values"""
        self.fetch_response = True, None, 1, srp_salt, b'fake_srp_verifier'
        self.start_response = True, None, public_id, master_key_salt
        self.generate_ephemeral_response = eph_public_b, b'fake_private_ephemeral'

        result = SessionManager.start_password_session(
            123,
            b'fake_srp_salt',
            b'fake_srp_verifier',
            b'fake_master_key_salt'
        )

        assert result[0]
        assert result[1] is None
        assert result[2] == public_id
        assert result[3] == eph_public_b
        assert result[4] == srp_salt
        assert result[5] == master_key_salt


class TestAuthPasswordSession():
    """Test cases for the auth password session function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.get_details_called = []
        self.get_details_response = True, None, b'fake_eph_private_b', b'fake_eph_public_b', b'fake_srp_verifier'
        def fake_get_details(public_id, user_id = None, username_hash = None):
            self.get_details_called.append((public_id, user_id, username_hash))
            return self.get_details_response
        monkeypatch.setattr(DBUtilsAuth, "get_details", fake_get_details)

        self.compute_session_key_called = []
        self.compute_session_key_response = b''
        def fake_compute_session_key(eph_val_a, eph_public_b, eph_private_b, srp_verifier_v):
            self.compute_session_key_called.append((eph_val_a, eph_public_b, eph_private_b, srp_verifier_v))
            return self.compute_session_key_response
        monkeypatch.setattr(SRPUtils, "compute_session_key", fake_compute_session_key)

        yield

    @pytest.mark.parametrize(
        "user_id, public_id",
        [
            (1,     "abc"),
            (20,        ""),
            (357, "def"*150)
        ]
    )
    def test_calls_get_details(self, user_id, public_id):
        """Should fetch ephemeral details"""

        result = SessionManager.auth_password_session(
            user_id=user_id,
            public_id=public_id,
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_b1'
        )

        assert len(self.get_details_called) == 1

        get_details = self.get_details_called[0]
        assert get_details[0] == public_id
        assert get_details[1] == user_id
        assert get_details[2] == None

    @pytest.mark.parametrize(
        "failure_reason",
        [
            FailureReason.NOT_FOUND,
            FailureReason.DATABASE_UNINITIALISED,
            FailureReason.UNKNOWN_EXCEPTION
        ]
    )
    def test_get_details_fails(self, failure_reason):
        """Should handle get_details failure"""

        self.get_details_response = False, failure_reason, b'', b'', b''

        result = SessionManager.auth_password_session(
            user_id=123,
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_b1'
        )

        assert not result[0]
        assert result[1] == failure_reason

    @pytest.mark.parametrize(
        "eph_val_a, eph_public_b, eph_private_b, srp_verifier_v",
        [
            (b'xyz',    b'abc',     b'def',     b'hij'),
            (b'',       b'',        b'',        b''),
            (b'def'*150,b'qcd'*100, b'ghi'*300, b'qew'*125)
        ]
    )
    def test_calls_compute_session_key(self, eph_val_a, eph_public_b, eph_private_b, srp_verifier_v):
        """Should call to compute session key"""

        self.get_details_response = True, None, eph_private_b, eph_public_b, srp_verifier_v

        result = SessionManager.auth_password_session(
            user_id=123,
            public_id="fake_public_id",
            eph_val_a=eph_val_a,
            proof_val_m1=b'fake_proof_val_b1'
        )

        assert len(self.compute_session_key_called) == 1

        compute_session_key = self.compute_session_key_called[0]
        assert compute_session_key[0] == eph_val_a
        assert compute_session_key[1] == eph_public_b
        assert compute_session_key[2] == eph_private_b
        assert compute_session_key[3] == srp_verifier_v


if __name__ == '__main__':
    pytest.main(['-v', __file__])
