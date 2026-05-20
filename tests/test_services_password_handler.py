import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from google.protobuf.message import DecodeError
from passmanager.common.v0.secure_pb2 import (
    SecureRequest,
    SecureResponse
)
from passmanager.common.v0.error_pb2 import (
    Failure,
    ErrorCode
)

from services.password_handler import PasswordHandler
from utils.service_utils import ServiceUtils
from utils.db_utils_password import DBUtilsPassword
from utils.session_manager import SessionManager
from enums.failure_reason import FailureReason


class TestStart():
    """Test cases for password start function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.open_session_called = []
        self.open_session_response = True, None, b'fake_decrypted_bytes', 0
        def fake_open_session(request, password_session = False, first_request = False):
            self.open_session_called.append((request, password_session, first_request))
            return self.open_session_response
        monkeypatch.setattr(SessionManager, "open_session", fake_open_session)

        yield

    def test_calls_open_session(self):
        """Should pass secure request to be opened"""

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.start(request)

        assert len(self.open_session_called) == 1
        assert self.open_session_called[0] == (request, False, False)

    def test_open_session_fails(self):
        """Should return error if open session fails"""

        self.open_session_response = False, FailureReason.DECRYPTION, b'', 0

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.start(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "request"
        assert error.code == ErrorCode.RQS01
        assert error.description == FailureReason.DECRYPTION.description



if __name__ == '__main__':
    pytest.main(['-v', __file__])
