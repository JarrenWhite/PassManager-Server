import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from google.protobuf.message import DecodeError
from passmanager.data.v0.data_payloads_pb2 import (
    DataCreateRequest,
    DataCreateResponse,
    DataEditRequest,
    DataEditResponse,
    DataDeleteRequest,
    DataDeleteResponse,
    DataGetRequest,
    DataGetResponse,
    DataListRequest,
    DataListResponse
)
from passmanager.common.v0.secure_pb2 import (
    SecureRequest,
    SecureResponse
)
from passmanager.common.v0.error_pb2 import (
    Failure,
    ErrorCode
)

from services.data_handler import DataHandler
from utils.service_utils import ServiceUtils
from utils.db_utils_user import DBUtilsUser
from utils.session_manager import SessionManager
from enums.failure_reason import FailureReason


class TestCreate:
    """Test cases for data create function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.open_session_called = []
        self.open_session_response = True, b'fake_decrypted_bytes', 0, None
        def fake_open_session(request, password_session = False, first_request = False):
            self.open_session_called.append((request, password_session, first_request))
            return self.open_session_response
        monkeypatch.setattr(SessionManager, "open_session", fake_open_session)

        self.from_string_called = []
        self.from_string_response = DataCreateRequest(
            username_hash=b'fake_username_hash'
        )
        self.from_string_exception = False
        def fake_from_string(data):
            self.from_string_called.append(data)
            if self.from_string_exception:
                raise DecodeError("invalid bytes")
            else:
                return self.from_string_response
        monkeypatch.setattr(DataCreateRequest, "FromString", fake_from_string)

        yield

    def test_calls_open_session(self):
        """Should pass secure request to be opened"""

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.create(request)

        assert len(self.open_session_called) == 1
        assert self.open_session_called[0] == (request, True, True)

    def test_open_session_fails(self):
        """Should return error if open session fails"""

        self.open_session_response = False, b'', 0, FailureReason.DECRYPTION

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.create(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "request"
        assert error.code == ErrorCode.RQS01
        assert error.description == FailureReason.DECRYPTION.description

    def test_calls_to_convert_to_proto(self):
        """Should attempt to convert returned bytes to protobuf"""

        self.from_string_response = DataCreateRequest()

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.create(request)

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

        response = DataHandler.create(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "request"
        assert error.code == ErrorCode.RQS01
        assert error.description == FailureReason.DECRYPTION.description


if __name__ == '__main__':
    pytest.main(['-v', __file__])
