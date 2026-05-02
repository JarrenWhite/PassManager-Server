import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from google.protobuf.message import DecodeError
from passmanager.session.v0.session_pb2 import (
    SessionStartRequest,
    SessionStartResponse,
    SessionAuthRequest,
    SessionAuthResponse
)
from passmanager.session.v0.session_payloads_pb2 import (
    SessionDeleteRequest,
    SessionDeleteResponse,
    SessionCleanRequest,
    SessionCleanResponse
)
from passmanager.common.v0.secure_pb2 import (
    SecureRequest,
    SecureResponse
)
from passmanager.common.v0.error_pb2 import (
    Failure,
    ErrorCode
)

from services.session_handler import SessionHandler
from utils.service_utils import ServiceUtils
from utils.db_utils_session import DBUtilsSession
from utils.session_manager import SessionManager
from enums.failure_reason import FailureReason


class TestStart():
    """Test cases for session start function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.sanitise_username_called = []
        self.sanitise_username_response = None
        def fake_sanitise_username(input):
            self.sanitise_username_called.append(input)
            return self.sanitise_username_response
        monkeypatch.setattr(ServiceUtils, "sanitise_username", fake_sanitise_username)

        yield

    def test_calls_sanitise_username(self):
        """Should call sanitise username"""

        request = SessionStartRequest(
            username_hash=b'fake_username_hash'
        )

        response = SessionHandler.start(request)

        assert len(self.sanitise_username_called) == 1
        assert self.sanitise_username_called[0] == b'fake_username_hash'

    @pytest.mark.parametrize(
        "failing_sanitiser, field",
        [
            ("sanitise_username",           "username_hash")
        ]
    )
    def test_each_sanitising_invalid_failure(self, failing_sanitiser, field):
        """Should fetch invalid error for each sanitation fail"""

        setattr(self, f"{failing_sanitiser}_response", FailureReason.INVALID)

        request = SessionStartRequest(
            username_hash=b'fake_username_hash'
        )

        response = SessionHandler.start(request)

        assert isinstance(response, SessionStartResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == field
        assert error.code == ErrorCode.GNR00
        assert error.description == FailureReason.INVALID.description

    def test_all_sanitising_functions_fail(self):
        """Should fetch all missing errors if all sanitising fails"""

        self.sanitise_username_response = FailureReason.INVALID
        self.sanitise_srp_salt_response = FailureReason.INVALID
        self.sanitise_srp_verifier_response = FailureReason.INVALID
        self.sanitise_master_key_salt_response = FailureReason.INVALID

        request = SessionStartRequest(
            username_hash=b'fake_username_hash'
        )

        response = SessionHandler.start(request)

        assert isinstance(response, SessionStartResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        fields = [error.field for error in response.failure_data.error_list]
        assert "username_hash" in fields


if __name__ == '__main__':
    pytest.main(['-v', __file__])
