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
from utils.db_utils_data import DBUtilsData
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
            username_hash=b'fake_username_hash',
            entry_name=b'fake_entry_name',
            entry_data=b'fake_entry_data'
        )
        self.from_string_exception = False
        def fake_from_string(data):
            self.from_string_called.append(data)
            if self.from_string_exception:
                raise DecodeError("invalid bytes")
            else:
                return self.from_string_response
        monkeypatch.setattr(DataCreateRequest, "FromString", fake_from_string)

        self.sanitise_username_called = []
        self.sanitise_username_response = None
        def fake_sanitise_username(input):
            self.sanitise_username_called.append(input)
            return self.sanitise_username_response
        monkeypatch.setattr(ServiceUtils, "sanitise_username", fake_sanitise_username)

        self.sanitise_entry_name_called = []
        self.sanitise_entry_name_response = None
        def fake_sanitise_entry_name(input):
            self.sanitise_entry_name_called.append(input)
            return self.sanitise_entry_name_response
        monkeypatch.setattr(ServiceUtils, "sanitise_entry_name", fake_sanitise_entry_name)

        self.sanitise_entry_data_called = []
        self.sanitise_entry_data_response = None
        def fake_sanitise_entry_data(input):
            self.sanitise_entry_data_called.append(input)
            return self.sanitise_entry_data_response
        monkeypatch.setattr(ServiceUtils, "sanitise_entry_data", fake_sanitise_entry_data)

        self.create_called = []
        self.create_response = True, None, "fake_public_id"
        def fake_create(user_id, entry_name, entry_data):
            self.create_called.append((user_id, entry_name, entry_data))
            return self.create_response
        monkeypatch.setattr(DBUtilsData, "create", fake_create)

        self.serialize_to_string_called = []
        self.serialize_to_string_response = b'fake_serialized_bytes'
        def fake_serialize_to_string(input):
            self.serialize_to_string_called.append(input)
            return self.serialize_to_string_response
        monkeypatch.setattr(DataCreateResponse, "SerializeToString", fake_serialize_to_string)

        self.seal_session_called = []
        self.seal_session_response = SecureResponse(
            success=True,
            success_data=SecureResponse.Success(
                session_id="fake_session_id",
                encrypted_data=b'fake_encrypted_data'
            )
        )
        def fake_seal_session(response):
            self.seal_session_called.append(response)
            return self.seal_session_response
        monkeypatch.setattr(SessionManager, "seal_session", fake_seal_session)

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

    def test_calls_sanitise_username(self):
        """Should call sanitise username"""

        self.from_string_response.username_hash = b'fake_username_hash'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.create(request)

        assert len(self.sanitise_username_called) == 1
        assert self.sanitise_username_called[0] == b'fake_username_hash'

    def test_calls_sanitise_entry_name(self):
        """Should call sanitise entry name"""

        self.from_string_response.entry_name = b'fake_entry_name'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.create(request)

        assert len(self.sanitise_entry_name_called) == 1
        assert self.sanitise_entry_name_called[0] == b'fake_entry_name'

    def test_calls_sanitise_entry_data(self):
        """Should call sanitise entry data"""

        self.from_string_response.entry_data = b'fake_entry_data'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.create(request)

        assert len(self.sanitise_entry_data_called) == 1
        assert self.sanitise_entry_data_called[0] == b'fake_entry_data'

    @pytest.mark.parametrize(
        "failing_sanitiser, field",
        [
            ("sanitise_username",           "username_hash"),
            ("sanitise_entry_name",         "entry_name"),
            ("sanitise_entry_data",         "entry_data")
        ]
    )
    def test_each_sanitising_invalid_failure(self, failing_sanitiser, field):
        """Should fetch invalid error for each sanitation fail"""

        setattr(self, f"{failing_sanitiser}_response", FailureReason.INVALID)

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
        assert error.field == field
        assert error.code == ErrorCode.GNR00
        assert error.description == FailureReason.INVALID.description

    def test_all_sanitising_functions_fail(self):
        """Should fetch all missing errors if all sanitising fails"""

        self.sanitise_username_response = FailureReason.INVALID
        self.sanitise_entry_name_response = FailureReason.INVALID
        self.sanitise_entry_data_response = FailureReason.INVALID

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.create(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 3

        fields = [error.field for error in response.failure_data.error_list]
        assert "username_hash" in fields
        assert "entry_name" in fields
        assert "entry_data" in fields

    @pytest.mark.parametrize(
        "user_id, entry_name, entry_data",
        [
            (0,     b'abc',     b'def'),
            (15,    b'',        b''),
            (350,   b'qcd'*100, b'ghi'*300)
        ]
    )
    def test_calls_create(self, user_id, entry_name, entry_data):
        """Should call the data create function"""

        self.open_session_response = True, b'fake_decrypted_bytes', user_id, None
        self.from_string_response.username_hash = b'fake_username_hash'
        self.from_string_response.entry_name = entry_name
        self.from_string_response.entry_data = entry_data

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.create(request)

        assert len(self.create_called) == 1

        create = self.create_called[0]
        assert create[0] == user_id
        assert create[1] == entry_name
        assert create[2] == entry_data

    @pytest.mark.parametrize(
        "failure_reason, field",
        [
            (FailureReason.UNSPECIFIED,         "unknown"),
            (FailureReason.UNKNOWN_EXCEPTION,   "server"),
            (FailureReason.USER_EXISTS,         "username"),
            (FailureReason.NOT_FOUND,           "unknown")
        ]
    )
    def test_returns_error_create_call_fails(self, failure_reason, field):
        """Should return correct error if data create function fails"""

        self.create_response = False, failure_reason, ""

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
        assert error.field == field
        assert error.code == failure_reason.error_code
        assert error.description == failure_reason.description

    def test_calls_convert_to_proto(self):
        """Should convert protobuf to bytes"""

        self.from_string_response.username_hash = b'fake_username_hash'
        self.create_response = True, None, "fake_public_id"

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.create(request)

        assert len(self.serialize_to_string_called) == 1

        serialize_to_string = self.serialize_to_string_called[0]
        assert isinstance(serialize_to_string, DataCreateResponse)
        assert serialize_to_string.username_hash == b'fake_username_hash'
        assert serialize_to_string.entry_public_id == "fake_public_id"

    def test_calls_seal_session(self):
        """Should call to seal session"""

        self.serialize_to_string_response = b'fake_serialized_bytes'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.create(request)

        assert len(self.seal_session_called) == 1
        assert self.seal_session_called[0] == b'fake_serialized_bytes'


if __name__ == '__main__':
    pytest.main(['-v', __file__])
