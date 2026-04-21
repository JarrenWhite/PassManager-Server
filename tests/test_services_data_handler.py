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
        def fake_seal_session(session_id, response):
            self.seal_session_called.append((session_id, response))
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
        assert self.open_session_called[0] == (request, False, False)

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

        sealed = self.seal_session_called[0]
        assert sealed[0] == "fake_session_id"
        assert sealed[1] == b'fake_serialized_bytes'

    @pytest.mark.parametrize(
        "secure_response",
        [
            SecureResponse(
                success=True,
                success_data=SecureResponse.Success(
                    session_id="",
                    encrypted_data=b''
                )
            ),
            SecureResponse(
                success=True,
                success_data=SecureResponse.Success(
                    session_id="fake_session_id",
                    encrypted_data=b'fake_encrypted_data'
                )
            ),
            SecureResponse(
                success=True,
                success_data=SecureResponse.Success(
                    session_id="abc123",
                    encrypted_data=b'987zyx'
                )
            ),
            SecureResponse(
                success=False,
                failure_data=Failure(
                    error_list=[FailureReason.PASSWORD_CHANGE.error_proto()]
                )
            ),
            SecureResponse(
                success=False,
                failure_data=Failure(
                    error_list=[FailureReason.INCOMPLETE.error_proto()]
                )
            ),
            SecureResponse(
                success=False,
                failure_data=Failure(
                    error_list=[FailureReason.NOT_FOUND.error_proto()]
                )
            )
        ]
    )
    def test_sealed_session_returned(self, secure_response):
        """Should return result of sealed session"""

        self.seal_session_response = secure_response

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.create(request)

        assert response == secure_response


class TestEdit:
    """Test cases for data edit function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.open_session_called = []
        self.open_session_response = True, b'fake_decrypted_bytes', 0, None
        def fake_open_session(request, password_session = False, first_request = False):
            self.open_session_called.append((request, password_session, first_request))
            return self.open_session_response
        monkeypatch.setattr(SessionManager, "open_session", fake_open_session)

        self.from_string_called = []
        self.from_string_response = DataEditRequest(
            username_hash=b'fake_username_hash',
            entry_public_id="fake_entry_public_id",
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
        monkeypatch.setattr(DataEditRequest, "FromString", fake_from_string)

        self.sanitise_username_called = []
        self.sanitise_username_response = None
        def fake_sanitise_username(input):
            self.sanitise_username_called.append(input)
            return self.sanitise_username_response
        monkeypatch.setattr(ServiceUtils, "sanitise_username", fake_sanitise_username)

        self.sanitise_entry_public_id_called = []
        self.sanitise_entry_public_id_response = None
        def fake_sanitise_entry_public_id(input):
            self.sanitise_entry_public_id_called.append(input)
            return self.sanitise_entry_public_id_response
        monkeypatch.setattr(ServiceUtils, "sanitise_entry_public_id", fake_sanitise_entry_public_id)

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

        self.edit_called = []
        self.edit_response = True, None
        def fake_edit(user_id, public_id, entry_name, entry_data):
            self.edit_called.append((user_id, public_id, entry_name, entry_data))
            return self.edit_response
        monkeypatch.setattr(DBUtilsData, "edit", fake_edit)

        self.serialize_to_string_called = []
        self.serialize_to_string_response = b'fake_serialized_bytes'
        def fake_serialize_to_string(input):
            self.serialize_to_string_called.append(input)
            return self.serialize_to_string_response
        monkeypatch.setattr(DataEditResponse, "SerializeToString", fake_serialize_to_string)

        self.seal_session_called = []
        self.seal_session_response = SecureResponse(
            success=True,
            success_data=SecureResponse.Success(
                session_id="fake_session_id",
                encrypted_data=b'fake_encrypted_data'
            )
        )
        def fake_seal_session(session_id, response):
            self.seal_session_called.append((session_id, response))
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

        response = DataHandler.edit(request)

        assert len(self.open_session_called) == 1
        assert self.open_session_called[0] == (request, False, False)

    def test_open_session_fails(self):
        """Should return error if open session fails"""

        self.open_session_response = False, b'', 0, FailureReason.DECRYPTION

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.edit(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "request"
        assert error.code == ErrorCode.RQS01
        assert error.description == FailureReason.DECRYPTION.description

    def test_calls_to_convert_to_proto(self):
        """Should attempt to convert returned bytes to protobuf"""

        self.from_string_response = DataEditRequest()

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.edit(request)

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

        response = DataHandler.edit(request)

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

        response = DataHandler.edit(request)

        assert len(self.sanitise_username_called) == 1
        assert self.sanitise_username_called[0] == b'fake_username_hash'

    def test_calls_sanitise_entry_public_id(self):
        """Should call sanitise entry public id"""

        self.from_string_response.entry_public_id = "fake_entry_public_id"

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.edit(request)

        assert len(self.sanitise_entry_public_id_called) == 1
        assert self.sanitise_entry_public_id_called[0] == "fake_entry_public_id"

    def test_calls_sanitise_entry_name(self):
        """Should call sanitise entry name"""

        self.from_string_response.entry_name = b'fake_entry_name'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.edit(request)

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

        response = DataHandler.edit(request)

        assert len(self.sanitise_entry_data_called) == 1
        assert self.sanitise_entry_data_called[0] == b'fake_entry_data'

    @pytest.mark.parametrize(
        "failing_sanitiser, field",
        [
            ("sanitise_username",           "username_hash"),
            ("sanitise_entry_public_id",    "entry_public_id"),
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

        response = DataHandler.edit(request)

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
        self.sanitise_entry_public_id_response = FailureReason.INVALID
        self.sanitise_entry_name_response = FailureReason.INVALID
        self.sanitise_entry_data_response = FailureReason.INVALID

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.edit(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 4

        fields = [error.field for error in response.failure_data.error_list]
        assert "username_hash" in fields
        assert "entry_public_id" in fields
        assert "entry_name" in fields
        assert "entry_data" in fields

    @pytest.mark.parametrize(
        "user_id, entry_public_id, entry_name, entry_data",
        [
            (0,     "abc",  b'abc',     b'def'),
            (15,    "",     b'',        b''),
            (350,   "123"*8,b'qcd'*100, b'ghi'*300)
        ]
    )
    def test_calls_edit(self, user_id, entry_public_id, entry_name, entry_data):
        """Should call the data edit function"""

        self.open_session_response = True, b'fake_decrypted_bytes', user_id, None
        self.from_string_response.username_hash = b'fake_username_hash'
        self.from_string_response.entry_public_id = entry_public_id
        self.from_string_response.entry_name = entry_name
        self.from_string_response.entry_data = entry_data

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.edit(request)

        assert len(self.edit_called) == 1

        create = self.edit_called[0]
        assert create[0] == user_id
        assert create[1] == entry_public_id
        assert create[2] == entry_name
        assert create[3] == entry_data

    @pytest.mark.parametrize(
        "failure_reason, field",
        [
            (FailureReason.UNSPECIFIED,         "unknown"),
            (FailureReason.UNKNOWN_EXCEPTION,   "server"),
            (FailureReason.USER_EXISTS,         "username"),
            (FailureReason.NOT_FOUND,           "unknown")
        ]
    )
    def test_returns_error_edit_call_fails(self, failure_reason, field):
        """Should return correct error if data edit function fails"""

        self.edit_response = False, failure_reason

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.edit(request)

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
        self.from_string_response.entry_public_id = "fake_entry_public_id"

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.edit(request)

        assert len(self.serialize_to_string_called) == 1

        serialize_to_string = self.serialize_to_string_called[0]
        assert isinstance(serialize_to_string, DataEditResponse)
        assert serialize_to_string.username_hash == b'fake_username_hash'
        assert serialize_to_string.entry_public_id == "fake_entry_public_id"

    def test_calls_seal_session(self):
        """Should call to seal session"""

        self.serialize_to_string_response = b'fake_serialized_bytes'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.edit(request)

        assert len(self.seal_session_called) == 1

        sealed = self.seal_session_called[0]
        assert sealed[0] == "fake_session_id"
        assert sealed[1] == b'fake_serialized_bytes'

    @pytest.mark.parametrize(
        "secure_response",
        [
            SecureResponse(
                success=True,
                success_data=SecureResponse.Success(
                    session_id="",
                    encrypted_data=b''
                )
            ),
            SecureResponse(
                success=True,
                success_data=SecureResponse.Success(
                    session_id="fake_session_id",
                    encrypted_data=b'fake_encrypted_data'
                )
            ),
            SecureResponse(
                success=True,
                success_data=SecureResponse.Success(
                    session_id="abc123",
                    encrypted_data=b'987zyx'
                )
            ),
            SecureResponse(
                success=False,
                failure_data=Failure(
                    error_list=[FailureReason.PASSWORD_CHANGE.error_proto()]
                )
            ),
            SecureResponse(
                success=False,
                failure_data=Failure(
                    error_list=[FailureReason.INCOMPLETE.error_proto()]
                )
            ),
            SecureResponse(
                success=False,
                failure_data=Failure(
                    error_list=[FailureReason.NOT_FOUND.error_proto()]
                )
            )
        ]
    )
    def test_sealed_session_returned(self, secure_response):
        """Should return result of sealed session"""

        self.seal_session_response = secure_response

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.edit(request)

        assert response == secure_response

    def test_entry_name_none_sanitised(self):
        """Should pass sanitisation gracefully if entry name is empty"""

        self.from_string_response.ClearField("entry_name")

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.edit(request)

        assert len(self.sanitise_entry_name_called) == 0

    def test_entry_data_none_sanitised(self):
        """Should pass sanitisation gracefully if entry data is empty"""

        self.from_string_response.ClearField("entry_data")

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.edit(request)

        assert len(self.sanitise_entry_data_called) == 0

    def test_entry_name_none_handled(self):
        """Should pass the none entry name to edit function"""

        self.from_string_response.ClearField("entry_name")
        self.from_string_response.entry_data = b'fake_entry_data'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.edit(request)

        assert self.edit_called[0][2] == None
        assert self.edit_called[0][3] == b'fake_entry_data'

    def test_entry_data_none_handled(self):
        """Should pass the none entry data to edit function"""

        self.from_string_response.entry_name = b'fake_entry_name'
        self.from_string_response.ClearField("entry_data")

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.edit(request)

        assert self.edit_called[0][2] == b'fake_entry_name'
        assert self.edit_called[0][3] == None

    def test_all_entries_none(self):
        """Should correctly handle both entry fields being none"""

        self.from_string_response.ClearField("entry_name")
        self.from_string_response.ClearField("entry_data")

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.edit(request)

        assert len(self.edit_called) == 1

        edit = self.edit_called[0]
        assert edit[2] == None
        assert edit[3] == None


class TestDelete:
    """Test cases for data delete function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.open_session_called = []
        self.open_session_response = True, b'fake_decrypted_bytes', 0, None
        def fake_open_session(request, password_session = False, first_request = False):
            self.open_session_called.append((request, password_session, first_request))
            return self.open_session_response
        monkeypatch.setattr(SessionManager, "open_session", fake_open_session)

        self.from_string_called = []
        self.from_string_response = DataDeleteRequest(
            username_hash=b'fake_username_hash',
            entry_public_id="fake_entry_public_id"
        )
        self.from_string_exception = False
        def fake_from_string(data):
            self.from_string_called.append(data)
            if self.from_string_exception:
                raise DecodeError("invalid bytes")
            else:
                return self.from_string_response
        monkeypatch.setattr(DataDeleteRequest, "FromString", fake_from_string)

        self.sanitise_username_called = []
        self.sanitise_username_response = None
        def fake_sanitise_username(input):
            self.sanitise_username_called.append(input)
            return self.sanitise_username_response
        monkeypatch.setattr(ServiceUtils, "sanitise_username", fake_sanitise_username)

        self.sanitise_entry_public_id_called = []
        self.sanitise_entry_public_id_response = None
        def fake_sanitise_entry_public_id(input):
            self.sanitise_entry_public_id_called.append(input)
            return self.sanitise_entry_public_id_response
        monkeypatch.setattr(ServiceUtils, "sanitise_entry_public_id", fake_sanitise_entry_public_id)

        self.delete_called = []
        self.delete_response = True, None
        def fake_delete(user_id, public_id):
            self.delete_called.append((user_id, public_id))
            return self.delete_response
        monkeypatch.setattr(DBUtilsData, "delete", fake_delete)

        self.serialize_to_string_called = []
        self.serialize_to_string_response = b'fake_serialized_bytes'
        def fake_serialize_to_string(input):
            self.serialize_to_string_called.append(input)
            return self.serialize_to_string_response
        monkeypatch.setattr(DataDeleteResponse, "SerializeToString", fake_serialize_to_string)

        self.seal_session_called = []
        self.seal_session_response = SecureResponse(
            success=True,
            success_data=SecureResponse.Success(
                session_id="fake_session_id",
                encrypted_data=b'fake_encrypted_data'
            )
        )
        def fake_seal_session(session_id, response):
            self.seal_session_called.append((session_id, response))
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

        response = DataHandler.delete(request)

        assert len(self.open_session_called) == 1
        assert self.open_session_called[0] == (request, False, False)

    def test_open_session_fails(self):
        """Should return error if open session fails"""

        self.open_session_response = False, b'', 0, FailureReason.DECRYPTION

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.delete(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "request"
        assert error.code == ErrorCode.RQS01
        assert error.description == FailureReason.DECRYPTION.description

    def test_calls_to_convert_to_proto(self):
        """Should attempt to convert returned bytes to protobuf"""

        self.from_string_response = DataDeleteRequest()

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.delete(request)

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

        response = DataHandler.delete(request)

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

        response = DataHandler.delete(request)

        assert len(self.sanitise_username_called) == 1
        assert self.sanitise_username_called[0] == b'fake_username_hash'

    def test_calls_sanitise_entry_public_id(self):
        """Should call sanitise entry public id"""

        self.from_string_response.entry_public_id = "fake_entry_public_id"

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.delete(request)

        assert len(self.sanitise_entry_public_id_called) == 1
        assert self.sanitise_entry_public_id_called[0] == "fake_entry_public_id"

    @pytest.mark.parametrize(
        "failing_sanitiser, field",
        [
            ("sanitise_username",           "username_hash"),
            ("sanitise_entry_public_id",    "entry_public_id")
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

        response = DataHandler.delete(request)

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
        self.sanitise_entry_public_id_response = FailureReason.INVALID

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.delete(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 2

        fields = [error.field for error in response.failure_data.error_list]
        assert "username_hash" in fields
        assert "entry_public_id" in fields

    @pytest.mark.parametrize(
        "user_id, entry_public_id",
        [
            (0,     "abc"),
            (15,    ""),
            (350,   "123"*8)
        ]
    )
    def test_calls_delete(self, user_id, entry_public_id):
        """Should call the data delete function"""

        self.open_session_response = True, b'fake_decrypted_bytes', user_id, None
        self.from_string_response.username_hash = b'fake_username_hash'
        self.from_string_response.entry_public_id = entry_public_id

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.delete(request)

        assert len(self.delete_called) == 1

        create = self.delete_called[0]
        assert create[0] == user_id
        assert create[1] == entry_public_id

    @pytest.mark.parametrize(
        "failure_reason, field",
        [
            (FailureReason.UNSPECIFIED,         "unknown"),
            (FailureReason.UNKNOWN_EXCEPTION,   "server"),
            (FailureReason.USER_EXISTS,         "username"),
            (FailureReason.NOT_FOUND,           "unknown")
        ]
    )
    def test_returns_error_delete_call_fails(self, failure_reason, field):
        """Should return correct error if data delete function fails"""

        self.delete_response = False, failure_reason

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.delete(request)

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
        self.from_string_response.entry_public_id = "fake_entry_public_id"

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.delete(request)

        assert len(self.serialize_to_string_called) == 1

        serialize_to_string = self.serialize_to_string_called[0]
        assert isinstance(serialize_to_string, DataDeleteResponse)
        assert serialize_to_string.username_hash == b'fake_username_hash'
        assert serialize_to_string.entry_public_id == "fake_entry_public_id"

    def test_calls_seal_session(self):
        """Should call to seal session"""

        self.serialize_to_string_response = b'fake_serialized_bytes'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.delete(request)

        assert len(self.seal_session_called) == 1

        sealed = self.seal_session_called[0]
        assert sealed[0] == "fake_session_id"
        assert sealed[1] == b'fake_serialized_bytes'

    @pytest.mark.parametrize(
        "secure_response",
        [
            SecureResponse(
                success=True,
                success_data=SecureResponse.Success(
                    session_id="",
                    encrypted_data=b''
                )
            ),
            SecureResponse(
                success=True,
                success_data=SecureResponse.Success(
                    session_id="fake_session_id",
                    encrypted_data=b'fake_encrypted_data'
                )
            ),
            SecureResponse(
                success=True,
                success_data=SecureResponse.Success(
                    session_id="abc123",
                    encrypted_data=b'987zyx'
                )
            ),
            SecureResponse(
                success=False,
                failure_data=Failure(
                    error_list=[FailureReason.PASSWORD_CHANGE.error_proto()]
                )
            ),
            SecureResponse(
                success=False,
                failure_data=Failure(
                    error_list=[FailureReason.INCOMPLETE.error_proto()]
                )
            ),
            SecureResponse(
                success=False,
                failure_data=Failure(
                    error_list=[FailureReason.NOT_FOUND.error_proto()]
                )
            )
        ]
    )
    def test_sealed_session_returned(self, secure_response):
        """Should return result of sealed session"""

        self.seal_session_response = secure_response

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.delete(request)

        assert response == secure_response


class TestGet:
    """Test cases for data get function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.open_session_called = []
        self.open_session_response = True, b'fake_decrypted_bytes', 0, None
        def fake_open_session(request, password_session = False, first_request = False):
            self.open_session_called.append((request, password_session, first_request))
            return self.open_session_response
        monkeypatch.setattr(SessionManager, "open_session", fake_open_session)

        self.from_string_called = []
        self.from_string_response = DataGetRequest(
            username_hash=b'fake_username_hash',
            entry_public_id="fake_entry_public_id"
        )
        self.from_string_exception = False
        def fake_from_string(data):
            self.from_string_called.append(data)
            if self.from_string_exception:
                raise DecodeError("invalid bytes")
            else:
                return self.from_string_response
        monkeypatch.setattr(DataGetRequest, "FromString", fake_from_string)

        self.sanitise_username_called = []
        self.sanitise_username_response = None
        def fake_sanitise_username(input):
            self.sanitise_username_called.append(input)
            return self.sanitise_username_response
        monkeypatch.setattr(ServiceUtils, "sanitise_username", fake_sanitise_username)

        self.sanitise_entry_public_id_called = []
        self.sanitise_entry_public_id_response = None
        def fake_sanitise_entry_public_id(input):
            self.sanitise_entry_public_id_called.append(input)
            return self.sanitise_entry_public_id_response
        monkeypatch.setattr(ServiceUtils, "sanitise_entry_public_id", fake_sanitise_entry_public_id)

        self.get_entry_called = []
        self.get_entry_response = True, None, b'fake_entry_name', b'fake_entry_data'
        def fake_get_entry(user_id, public_id):
            self.get_entry_called.append((user_id, public_id))
            return self.get_entry_response
        monkeypatch.setattr(DBUtilsData, "get_entry", fake_get_entry)

        self.serialize_to_string_called = []
        self.serialize_to_string_response = b'fake_serialized_bytes'
        def fake_serialize_to_string(input):
            self.serialize_to_string_called.append(input)
            return self.serialize_to_string_response
        monkeypatch.setattr(DataGetResponse, "SerializeToString", fake_serialize_to_string)

        self.seal_session_called = []
        self.seal_session_response = SecureResponse(
            success=True,
            success_data=SecureResponse.Success(
                session_id="fake_session_id",
                encrypted_data=b'fake_encrypted_data'
            )
        )
        def fake_seal_session(session_id, response):
            self.seal_session_called.append((session_id, response))
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

        response = DataHandler.get(request)

        assert len(self.open_session_called) == 1
        assert self.open_session_called[0] == (request, False, False)

    def test_open_session_fails(self):
        """Should return error if open session fails"""

        self.open_session_response = False, b'', 0, FailureReason.DECRYPTION

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.get(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "request"
        assert error.code == ErrorCode.RQS01
        assert error.description == FailureReason.DECRYPTION.description

    def test_calls_to_convert_to_proto(self):
        """Should attempt to convert returned bytes to protobuf"""

        self.from_string_response = DataGetRequest()

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.get(request)

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

        response = DataHandler.get(request)

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

        response = DataHandler.get(request)

        assert len(self.sanitise_username_called) == 1
        assert self.sanitise_username_called[0] == b'fake_username_hash'

    def test_calls_sanitise_entry_public_id(self):
        """Should call sanitise entry public id"""

        self.from_string_response.entry_public_id = "fake_entry_public_id"

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.get(request)

        assert len(self.sanitise_entry_public_id_called) == 1
        assert self.sanitise_entry_public_id_called[0] == "fake_entry_public_id"

    @pytest.mark.parametrize(
        "failing_sanitiser, field",
        [
            ("sanitise_username",           "username_hash"),
            ("sanitise_entry_public_id",    "entry_public_id")
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

        response = DataHandler.get(request)

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
        self.sanitise_entry_public_id_response = FailureReason.INVALID

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.get(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 2

        fields = [error.field for error in response.failure_data.error_list]
        assert "username_hash" in fields
        assert "entry_public_id" in fields

    @pytest.mark.parametrize(
        "user_id, entry_public_id",
        [
            (0,     "abc"),
            (15,    ""),
            (350,   "123"*8)
        ]
    )
    def test_calls_get_entry(self, user_id, entry_public_id):
        """Should call the data get entry function"""

        self.open_session_response = True, b'fake_decrypted_bytes', user_id, None
        self.from_string_response.username_hash = b'fake_username_hash'
        self.from_string_response.entry_public_id = entry_public_id

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.get(request)

        assert len(self.get_entry_called) == 1

        create = self.get_entry_called[0]
        assert create[0] == user_id
        assert create[1] == entry_public_id

    @pytest.mark.parametrize(
        "failure_reason, field",
        [
            (FailureReason.UNSPECIFIED,         "unknown"),
            (FailureReason.UNKNOWN_EXCEPTION,   "server"),
            (FailureReason.USER_EXISTS,         "username"),
            (FailureReason.NOT_FOUND,           "unknown")
        ]
    )
    def test_returns_error_get_call_fails(self, failure_reason, field):
        """Should return correct error if data get function fails"""

        self.get_entry_response = False, failure_reason, b'', b''

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.get(request)

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
        self.from_string_response.entry_public_id = "fake_entry_public_id"

        self.get_entry_response = True, None, b'fake_entry_name', b'fake_entry_data'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.get(request)

        assert len(self.serialize_to_string_called) == 1

        serialize_to_string = self.serialize_to_string_called[0]
        assert isinstance(serialize_to_string, DataGetResponse)
        assert serialize_to_string.username_hash == b'fake_username_hash'
        assert serialize_to_string.entry_public_id == "fake_entry_public_id"
        assert serialize_to_string.entry_name == b'fake_entry_name'
        assert serialize_to_string.entry_data == b'fake_entry_data'

    def test_calls_seal_session(self):
        """Should call to seal session"""

        self.serialize_to_string_response = b'fake_serialized_bytes'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.get(request)

        assert len(self.seal_session_called) == 1

        sealed = self.seal_session_called[0]
        assert sealed[0] == "fake_session_id"
        assert sealed[1] == b'fake_serialized_bytes'

    @pytest.mark.parametrize(
        "secure_response",
        [
            SecureResponse(
                success=True,
                success_data=SecureResponse.Success(
                    session_id="",
                    encrypted_data=b''
                )
            ),
            SecureResponse(
                success=True,
                success_data=SecureResponse.Success(
                    session_id="fake_session_id",
                    encrypted_data=b'fake_encrypted_data'
                )
            ),
            SecureResponse(
                success=True,
                success_data=SecureResponse.Success(
                    session_id="abc123",
                    encrypted_data=b'987zyx'
                )
            ),
            SecureResponse(
                success=False,
                failure_data=Failure(
                    error_list=[FailureReason.PASSWORD_CHANGE.error_proto()]
                )
            ),
            SecureResponse(
                success=False,
                failure_data=Failure(
                    error_list=[FailureReason.INCOMPLETE.error_proto()]
                )
            ),
            SecureResponse(
                success=False,
                failure_data=Failure(
                    error_list=[FailureReason.NOT_FOUND.error_proto()]
                )
            )
        ]
    )
    def test_sealed_session_returned(self, secure_response):
        """Should return result of sealed session"""

        self.seal_session_response = secure_response

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.get(request)

        assert response == secure_response


class TestList:
    """Test cases for data list function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.open_session_called = []
        self.open_session_response = True, b'fake_decrypted_bytes', 0, None
        def fake_open_session(request, password_session = False, first_request = False):
            self.open_session_called.append((request, password_session, first_request))
            return self.open_session_response
        monkeypatch.setattr(SessionManager, "open_session", fake_open_session)

        self.from_string_called = []
        self.from_string_response = DataListRequest(
            username_hash=b'fake_username_hash'
        )
        self.from_string_exception = False
        def fake_from_string(data):
            self.from_string_called.append(data)
            if self.from_string_exception:
                raise DecodeError("invalid bytes")
            else:
                return self.from_string_response
        monkeypatch.setattr(DataListRequest, "FromString", fake_from_string)

        yield

    def test_calls_open_session(self):
        """Should pass secure request to be opened"""

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.list(request)

        assert len(self.open_session_called) == 1
        assert self.open_session_called[0] == (request, False, False)

    def test_open_session_fails(self):
        """Should return error if open session fails"""

        self.open_session_response = False, b'', 0, FailureReason.DECRYPTION

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.list(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "request"
        assert error.code == ErrorCode.RQS01
        assert error.description == FailureReason.DECRYPTION.description

    def test_calls_to_convert_to_proto(self):
        """Should attempt to convert returned bytes to protobuf"""

        self.from_string_response = DataListRequest()

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.list(request)

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

        response = DataHandler.list(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "request"
        assert error.code == ErrorCode.RQS01
        assert error.description == FailureReason.DECRYPTION.description


if __name__ == '__main__':
    pytest.main(['-v', __file__])
