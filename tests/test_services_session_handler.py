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

        self.start_new_session_called = []
        self.start_new_session_response = (
            True,
            None,
            "fake_public_id",
            b'fake_srp_salt',
            b'fake_eph_public_b',
            b'fake_master_key_salt'
        )
        def fake_start_new_session(username_hash):
            self.start_new_session_called.append(username_hash)
            return self.start_new_session_response
        monkeypatch.setattr(SessionManager, "start_new_session", fake_start_new_session)

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

        request = SessionStartRequest(
            username_hash=b'fake_username_hash'
        )

        response = SessionHandler.start(request)

        assert isinstance(response, SessionStartResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        fields = [error.field for error in response.failure_data.error_list]
        assert "username_hash" in fields

    def test_calls_start_new_session(self):
        """Should call the start new session function"""

        request = SessionStartRequest(
            username_hash=b'fake_username_hash'
        )

        response = SessionHandler.start(request)

        assert len(self.start_new_session_called) == 1

        start = self.start_new_session_called[0]
        assert start == b'fake_username_hash'

    @pytest.mark.parametrize(
        "failure_reason, field",
        [
            (FailureReason.UNSPECIFIED,         "unknown"),
            (FailureReason.UNKNOWN_EXCEPTION,   "server"),
            (FailureReason.USER_EXISTS,         "username"),
            (FailureReason.NOT_FOUND,           "new_username")
        ]
    )
    def test_returns_error_start_new_session_call_fails(self, failure_reason, field):
        """Should return correct error if start new session function fails"""

        self.start_new_session_response = False, failure_reason, "", b'', b'', b''

        request = SessionStartRequest(
            username_hash=b'fake_username_hash'
        )

        response = SessionHandler.start(request)

        assert isinstance(response, SessionStartResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == field
        assert error.code == failure_reason.error_code
        assert error.description == failure_reason.description

    def test_successful_completion(self):
        """Should return successful result"""

        self.start_new_session_response = (
            True,
            None,
            "fake_public_id",
            b'fake_srp_salt',
            b'fake_eph_public_b',
            b'fake_master_key_salt'
        )

        request = SessionStartRequest(
            username_hash=b'fake_username_hash'
        )

        response = SessionHandler.start(request)

        assert isinstance(response, SessionStartResponse)
        assert response.success

        response_data = response.success_data
        assert response_data.public_id == "fake_public_id"
        assert response_data.srp_salt == b'fake_srp_salt'
        assert response_data.eph_public_b == b'fake_eph_public_b'
        assert response_data.master_key_salt == b'fake_master_key_salt'


class TestAuth():
    """Test cases for session auth function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.sanitise_username_called = []
        self.sanitise_username_response = None
        def fake_sanitise_username(input):
            self.sanitise_username_called.append(input)
            return self.sanitise_username_response
        monkeypatch.setattr(ServiceUtils, "sanitise_username", fake_sanitise_username)

        self.sanitise_public_id_called = []
        self.sanitise_public_id_response = None
        def fake_sanitise_public_id(input):
            self.sanitise_public_id_called.append(input)
            return self.sanitise_public_id_response
        monkeypatch.setattr(ServiceUtils, "sanitise_public_id", fake_sanitise_public_id)

        self.sanitise_eph_val_a_called = []
        self.sanitise_eph_val_a_response = None
        def fake_sanitise_eph_val_a(input):
            self.sanitise_eph_val_a_called.append(input)
            return self.sanitise_eph_val_a_response
        monkeypatch.setattr(ServiceUtils, "sanitise_eph_val_a", fake_sanitise_eph_val_a)

        self.sanitise_proof_val_m1_called = []
        self.sanitise_proof_val_m1_response = None
        def fake_sanitise_proof_val_m1(input):
            self.sanitise_proof_val_m1_called.append(input)
            return self.sanitise_proof_val_m1_response
        monkeypatch.setattr(ServiceUtils, "sanitise_proof_val_m1", fake_sanitise_proof_val_m1)

        self.sanitise_maximum_requests_called = []
        self.sanitise_maximum_requests_response = None
        def fake_sanitise_maximum_requests(input):
            self.sanitise_maximum_requests_called.append(input)
            return self.sanitise_maximum_requests_response
        monkeypatch.setattr(ServiceUtils, "sanitise_maximum_requests", fake_sanitise_maximum_requests)

        self.sanitise_expiry_time_called = []
        self.sanitise_expiry_time_response = None
        def fake_sanitise_expiry_time(input):
            self.sanitise_expiry_time_called.append(input)
            return self.sanitise_expiry_time_response
        monkeypatch.setattr(ServiceUtils, "sanitise_expiry_time", fake_sanitise_expiry_time)

        self.auth_new_session_called = []
        self.auth_new_session_response = True, None, "fake_public_session_id", b'fake_server_proof'
        def fake_auth_new_session(
                username_hash: bytes,
                public_id: str,
                eph_val_a: bytes,
                proof_val_m1: bytes,
                maximum_requests: int,
                expiry_time: int
            ):
            self.auth_new_session_called.append((
                username_hash,
                public_id,
                eph_val_a,
                proof_val_m1,
                maximum_requests,
                expiry_time
            ))
            return self.auth_new_session_response
        monkeypatch.setattr(SessionManager, "auth_new_session", fake_auth_new_session)

        yield

    def test_calls_sanitise_username(self):
        """Should call sanitise username"""

        request = SessionAuthRequest(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_m1',
            maximum_requests=5,
            expiry_time=8
        )

        response = SessionHandler.auth(request)

        assert len(self.sanitise_username_called) == 1
        assert self.sanitise_username_called[0] == b'fake_username_hash'

    def test_calls_sanitise_public_id(self):
        """Should call sanitise public id"""

        request = SessionAuthRequest(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_m1',
            maximum_requests=5,
            expiry_time=8
        )

        response = SessionHandler.auth(request)

        assert len(self.sanitise_public_id_called) == 1
        assert self.sanitise_public_id_called[0] == "fake_public_id"

    def test_calls_sanitise_eph_val_a(self):
        """Should call sanitise eph val a"""

        request = SessionAuthRequest(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_m1',
            maximum_requests=5,
            expiry_time=8
        )

        response = SessionHandler.auth(request)

        assert len(self.sanitise_eph_val_a_called) == 1
        assert self.sanitise_eph_val_a_called[0] == b'fake_eph_val_a'

    def test_calls_sanitise_proof_val_m1(self):
        """Should call sanitise proof val m1"""

        request = SessionAuthRequest(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_m1',
            maximum_requests=5,
            expiry_time=8
        )

        response = SessionHandler.auth(request)

        assert len(self.sanitise_proof_val_m1_called) == 1
        assert self.sanitise_proof_val_m1_called[0] == b'fake_proof_val_m1'

    def test_calls_sanitise_maximum_requests(self):
        """Should call sanitise maximum requests"""

        request = SessionAuthRequest(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_m1',
            maximum_requests=5,
            expiry_time=8
        )

        response = SessionHandler.auth(request)

        assert len(self.sanitise_maximum_requests_called) == 1
        assert self.sanitise_maximum_requests_called[0] == 5

    def test_calls_sanitise_expiry_time(self):
        """Should call sanitise expiry time"""

        request = SessionAuthRequest(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_m1',
            maximum_requests=5,
            expiry_time=8
        )

        response = SessionHandler.auth(request)

        assert len(self.sanitise_expiry_time_called) == 1
        assert self.sanitise_expiry_time_called[0] == 8

    @pytest.mark.parametrize(
        "failing_sanitiser, field",
        [
            ("sanitise_username",           "username_hash"),
            ("sanitise_public_id",          "public_id"),
            ("sanitise_eph_val_a",          "eph_val_a"),
            ("sanitise_proof_val_m1",       "proof_val_m1"),
            ("sanitise_maximum_requests",   "maximum_requests"),
            ("sanitise_expiry_time",        "expiry_time")
        ]
    )
    def test_each_sanitising_invalid_failure(self, failing_sanitiser, field):
        """Should fetch invalid error for each sanitation fail"""

        setattr(self, f"{failing_sanitiser}_response", FailureReason.INVALID)

        request = SessionAuthRequest(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_m1',
            maximum_requests=5,
            expiry_time=8
        )

        response = SessionHandler.auth(request)

        assert isinstance(response, SessionAuthResponse)
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

        request = SessionAuthRequest(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_m1',
            maximum_requests=5,
            expiry_time=8
        )

        response = SessionHandler.auth(request)

        assert isinstance(response, SessionAuthResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        fields = [error.field for error in response.failure_data.error_list]
        assert "username_hash" in fields

    def test_calls_auth_new_session(self):
        """Should call the auth new session function"""

        request = SessionAuthRequest(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_m1',
            maximum_requests=5,
            expiry_time=8
        )

        response = SessionHandler.auth(request)

        assert len(self.auth_new_session_called) == 1

        auth = self.auth_new_session_called[0]
        assert auth[0] == b'fake_username_hash'
        assert auth[1] == "fake_public_id"
        assert auth[2] == b'fake_eph_val_a'
        assert auth[3] == b'fake_proof_val_m1'
        assert auth[4] == 5
        assert auth[5] == 8

    @pytest.mark.parametrize(
        "failure_reason, field",
        [
            (FailureReason.UNSPECIFIED,         "unknown"),
            (FailureReason.UNKNOWN_EXCEPTION,   "server"),
            (FailureReason.USER_EXISTS,         "username"),
            (FailureReason.NOT_FOUND,           "new_username")
        ]
    )
    def test_returns_error_auth_new_session_call_fails(self, failure_reason, field):
        """Should return correct error if auth new session function fails"""

        self.auth_new_session_response = False, failure_reason, "", b''

        request = SessionAuthRequest(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_m1',
            maximum_requests=5,
            expiry_time=8
        )

        response = SessionHandler.auth(request)

        assert isinstance(response, SessionAuthResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == field
        assert error.code == failure_reason.error_code
        assert error.description == failure_reason.description

    def test_successful_completion(self):
        """Should return successful result"""

        self.auth_new_session_response = True, None, "fake_public_session_id", b'fake_server_proof'

        request = SessionAuthRequest(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a=b'fake_eph_val_a',
            proof_val_m1=b'fake_proof_val_m1',
            maximum_requests=5,
            expiry_time=8
        )

        response = SessionHandler.auth(request)

        assert isinstance(response, SessionAuthResponse)
        assert response.success

        response_data = response.success_data
        assert response_data.session_id == "fake_public_session_id"
        assert response_data.server_proof == b'fake_server_proof'


class TestDelete():
    """Test cases for session delete function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.open_session_called = []
        self.open_session_response = True, None, b'fake_decrypted_bytes', 0
        def fake_open_session(request, password_session = False, first_request = False):
            self.open_session_called.append((request, password_session, first_request))
            return self.open_session_response
        monkeypatch.setattr(SessionManager, "open_session", fake_open_session)

        self.from_string_called = []
        self.from_string_response = SessionDeleteRequest(
            username_hash=b'fake_username_hash',
            session_id="fake_public_session_id"
        )
        self.from_string_exception = False
        def fake_from_string(data):
            self.from_string_called.append(data)
            if self.from_string_exception:
                raise DecodeError("invalid bytes")
            else:
                return self.from_string_response
        monkeypatch.setattr(SessionDeleteRequest, "FromString", fake_from_string)

        self.sanitise_username_called = []
        self.sanitise_username_response = None
        def fake_sanitise_username(input):
            self.sanitise_username_called.append(input)
            return self.sanitise_username_response
        monkeypatch.setattr(ServiceUtils, "sanitise_username", fake_sanitise_username)

        self.sanitise_public_id_called = []
        self.sanitise_public_id_response = None
        def fake_sanitise_public_id(input):
            self.sanitise_public_id_called.append(input)
            return self.sanitise_public_id_response
        monkeypatch.setattr(ServiceUtils, "sanitise_public_id", fake_sanitise_public_id)

        self.delete_called = []
        self.delete_response = True, None
        def fake_delete(user_id, public_id):
            self.delete_called.append((user_id, public_id))
            return self.delete_response
        monkeypatch.setattr(DBUtilsSession, "delete", fake_delete)

        self.serialize_to_string_called = []
        self.serialize_to_string_response = b'fake_serialized_bytes'
        def fake_serialize_to_string(input):
            self.serialize_to_string_called.append(input)
            return self.serialize_to_string_response
        monkeypatch.setattr(SessionDeleteResponse, "SerializeToString", fake_serialize_to_string)

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

        response = SessionHandler.delete(request)

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

        response = SessionHandler.delete(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "request"
        assert error.code == ErrorCode.RQS01
        assert error.description == FailureReason.DECRYPTION.description

    def test_calls_to_convert_to_proto(self):
        """Should attempt to convert returned bytes to protobuf"""

        self.from_string_response = SessionDeleteRequest()

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = SessionHandler.delete(request)

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

        response = SessionHandler.delete(request)

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

        response = SessionHandler.delete(request)

        assert len(self.sanitise_username_called) == 1
        assert self.sanitise_username_called[0] == b'fake_username_hash'

    def test_calls_sanitise_public_id(self):
        """Should call sanitise public id"""

        self.from_string_response.session_id = "fake_public_session_id"

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = SessionHandler.delete(request)

        assert len(self.sanitise_public_id_called) == 1
        assert self.sanitise_public_id_called[0] == "fake_public_session_id"

    @pytest.mark.parametrize(
        "failing_sanitiser, field",
        [
            ("sanitise_username",           "username_hash"),
            ("sanitise_public_id",          "session_id")
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

        response = SessionHandler.delete(request)

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
        self.sanitise_public_id_response = FailureReason.INVALID

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = SessionHandler.delete(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 2

        fields = [error.field for error in response.failure_data.error_list]
        assert "username_hash" in fields
        assert "session_id" in fields

    @pytest.mark.parametrize(
        "user_id, session_id",
        [
            (0,     "abc"),
            (15,    ""),
            (350,   "123")
        ]
    )
    def test_calls_delete(self, user_id, session_id):
        """Should call the session delete function"""

        self.open_session_response = True, None, b'fake_decrypted_bytes', user_id
        self.from_string_response.username_hash = b'fake_username_hash'
        self.from_string_response.session_id = session_id

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = SessionHandler.delete(request)

        assert len(self.delete_called) == 1
        delete = self.delete_called[0]
        assert delete[0] == user_id
        assert delete[1] == session_id

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
        """Should return correct error if session delete function fails"""

        self.delete_response = False, failure_reason

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = SessionHandler.delete(request)

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

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = SessionHandler.delete(request)

        assert len(self.serialize_to_string_called) == 1

        serialize_to_string = self.serialize_to_string_called[0]
        assert isinstance(serialize_to_string, SessionDeleteResponse)
        assert serialize_to_string.username_hash == b'fake_username_hash'

    def test_calls_seal_session(self):
        """Should call to seal session"""

        self.serialize_to_string_response = b'fake_serialized_bytes'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = SessionHandler.delete(request)

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

        response = SessionHandler.delete(request)

        assert response == secure_response


class TestClean():
    """Test cases for session clean function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.open_session_called = []
        self.open_session_response = True, None, b'fake_decrypted_bytes', 0
        def fake_open_session(request, password_session = False, first_request = False):
            self.open_session_called.append((request, password_session, first_request))
            return self.open_session_response
        monkeypatch.setattr(SessionManager, "open_session", fake_open_session)

        self.from_string_called = []
        self.from_string_response = SessionCleanRequest(
            username_hash=b'fake_username_hash'
        )
        self.from_string_exception = False
        def fake_from_string(data):
            self.from_string_called.append(data)
            if self.from_string_exception:
                raise DecodeError("invalid bytes")
            else:
                return self.from_string_response
        monkeypatch.setattr(SessionCleanRequest, "FromString", fake_from_string)

        self.sanitise_username_called = []
        self.sanitise_username_response = None
        def fake_sanitise_username(input):
            self.sanitise_username_called.append(input)
            return self.sanitise_username_response
        monkeypatch.setattr(ServiceUtils, "sanitise_username", fake_sanitise_username)

        self.clean_user_called = []
        self.clean_user_response = True, None
        def fake_clean_user(user_id):
            self.clean_user_called.append(user_id)
            return self.clean_user_response
        monkeypatch.setattr(DBUtilsSession, "clean_user", fake_clean_user)

        self.serialize_to_string_called = []
        self.serialize_to_string_response = b'fake_serialized_bytes'
        def fake_serialize_to_string(input):
            self.serialize_to_string_called.append(input)
            return self.serialize_to_string_response
        monkeypatch.setattr(SessionCleanResponse, "SerializeToString", fake_serialize_to_string)

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

        response = SessionHandler.clean(request)

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

        response = SessionHandler.clean(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "request"
        assert error.code == ErrorCode.RQS01
        assert error.description == FailureReason.DECRYPTION.description

    def test_calls_to_convert_to_proto(self):
        """Should attempt to convert returned bytes to protobuf"""

        self.from_string_response = SessionDeleteRequest()

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = SessionHandler.clean(request)

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

        response = SessionHandler.clean(request)

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

        response = SessionHandler.clean(request)

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

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = SessionHandler.clean(request)

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

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = SessionHandler.clean(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        fields = [error.field for error in response.failure_data.error_list]
        assert "username_hash" in fields

    @pytest.mark.parametrize(
        "user_id",
        [
            0,
            15,
            350
        ]
    )
    def test_calls_clean(self, user_id):
        """Should call the session clean_user function"""

        self.open_session_response = True, None, b'fake_decrypted_bytes', user_id
        self.from_string_response.username_hash = b'fake_username_hash'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = SessionHandler.clean(request)

        assert len(self.clean_user_called) == 1
        clean_user = self.clean_user_called
        assert clean_user[0] == user_id

    @pytest.mark.parametrize(
        "failure_reason, field",
        [
            (FailureReason.UNSPECIFIED,         "unknown"),
            (FailureReason.UNKNOWN_EXCEPTION,   "server"),
            (FailureReason.USER_EXISTS,         "username"),
            (FailureReason.NOT_FOUND,           "unknown")
        ]
    )
    def test_returns_error_clean_call_fails(self, failure_reason, field):
        """Should return correct error if session clean_user function fails"""

        self.clean_user_response = False, failure_reason

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = SessionHandler.clean(request)

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

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = SessionHandler.clean(request)

        assert len(self.serialize_to_string_called) == 1

        serialize_to_string = self.serialize_to_string_called[0]
        assert isinstance(serialize_to_string, SessionCleanResponse)
        assert serialize_to_string.username_hash == b'fake_username_hash'

    def test_calls_seal_session(self):
        """Should call to seal session"""

        self.serialize_to_string_response = b'fake_serialized_bytes'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = SessionHandler.clean(request)

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

        response = SessionHandler.clean(request)

        assert response == secure_response


if __name__ == '__main__':
    pytest.main(['-v', __file__])
