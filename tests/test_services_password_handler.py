import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from google.protobuf.message import DecodeError
from passmanager.password.v0.password_payloads_pb2 import (
    PasswordStartRequest,
    PasswordStartResponse,
    PasswordAuthRequest,
    PasswordAuthResponse,
    PasswordCompleteRequest,
    PasswordCompleteResponse,
    PasswordAbortRequest,
    PasswordAbortResponse,
    PasswordGetRequest,
    PasswordGetResponse,
    PasswordUpdateRequest,
    PasswordUpdateResponse
)
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

        self.from_string_called = []
        self.from_string_response = PasswordStartRequest(
            username_hash=b'fake_username_hash',
            srp_salt = b'fake_srp_salt',
            srp_verifier = b'fake_srp_verifier',
            master_key_salt = b'fake_master_key_salt'
        )
        self.from_string_exception = False
        def fake_from_string(data):
            self.from_string_called.append(data)
            if self.from_string_exception:
                raise DecodeError("invalid bytes")
            else:
                return self.from_string_response
        monkeypatch.setattr(PasswordStartRequest, "FromString", fake_from_string)

        self.sanitise_username_called = []
        self.sanitise_username_response = None
        def fake_sanitise_username(input):
            self.sanitise_username_called.append(input)
            return self.sanitise_username_response
        monkeypatch.setattr(ServiceUtils, "sanitise_username", fake_sanitise_username)

        self.sanitise_srp_salt_called = []
        self.sanitise_srp_salt_response = None
        def fake_sanitise_srp_salt(input):
            self.sanitise_srp_salt_called.append(input)
            return self.sanitise_srp_salt_response
        monkeypatch.setattr(ServiceUtils, "sanitise_srp_salt", fake_sanitise_srp_salt)

        self.sanitise_srp_verifier_called = []
        self.sanitise_srp_verifier_response = None
        def fake_sanitise_srp_verifier(input):
            self.sanitise_srp_verifier_called.append(input)
            return self.sanitise_srp_verifier_response
        monkeypatch.setattr(ServiceUtils, "sanitise_srp_verifier", fake_sanitise_srp_verifier)

        self.sanitise_master_key_salt_called = []
        self.sanitise_master_key_salt_response = None
        def fake_sanitise_master_key_salt(input):
            self.sanitise_master_key_salt_called.append(input)
            return self.sanitise_master_key_salt_response
        monkeypatch.setattr(ServiceUtils, "sanitise_master_key_salt", fake_sanitise_master_key_salt)

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

    def test_calls_to_convert_to_proto(self):
        """Should attempt to convert returned bytes to protobuf"""

        self.from_string_response = PasswordStartRequest()

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.start(request)

        assert len(self.from_string_called) == 1
        assert self.from_string_called[0] == b'fake_decrypted_bytes'

    def test_convert_to_proto_fails(self):
        """Should fail if conversion to proto raises exception"""

        self.from_string_exception = True

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

    def test_calls_sanitise_username(self):
        """Should call sanitise username"""

        self.from_string_response.username_hash = b'fake_username_hash'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.start(request)

        assert len(self.sanitise_username_called) == 1
        assert self.sanitise_username_called[0] == b'fake_username_hash'

    def test_calls_sanitise_srp_salt(self):
        """Should call sanitise srp salt"""

        self.from_string_response.srp_salt = b'fake_srp_salt'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.start(request)

        assert len(self.sanitise_srp_salt_called) == 1
        assert self.sanitise_srp_salt_called[0] == b'fake_srp_salt'

    def test_calls_sanitise_srp_verifier(self):
        """Should call sanitise srp verifier"""

        self.from_string_response.srp_verifier = b'fake_srp_verifier'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.start(request)

        assert len(self.sanitise_srp_verifier_called) == 1
        assert self.sanitise_srp_verifier_called[0] == b'fake_srp_verifier'

    def test_calls_sanitise_master_key_salt(self):
        """Should call sanitise master key salt"""

        self.from_string_response.master_key_salt = b'fake_master_key_salt'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.start(request)

        assert len(self.sanitise_master_key_salt_called) == 1
        assert self.sanitise_master_key_salt_called[0] == b'fake_master_key_salt'





if __name__ == '__main__':
    pytest.main(['-v', __file__])
