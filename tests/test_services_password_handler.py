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

        self.start_password_session_called = []
        self.start_password_session_response = True, None, "fake_public_id", b'fake_srp_salt', b'fake_eph_public_b'
        def fake_start_password_session(user_id, srp_salt, srp_verifier, master_key_salt):
            self.start_password_session_called.append((user_id, srp_salt, srp_verifier, master_key_salt))
            return self.start_password_session_response
        monkeypatch.setattr(SessionManager, "start_password_session", fake_start_password_session)

        self.serialize_to_string_called = []
        self.serialize_to_string_response = b'fake_serialized_bytes'
        def fake_serialize_to_string(input):
            self.serialize_to_string_called.append(input)
            return self.serialize_to_string_response
        monkeypatch.setattr(PasswordStartResponse, "SerializeToString", fake_serialize_to_string)

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

    @pytest.mark.parametrize(
        "failing_sanitiser, field",
        [
            ("sanitise_username",           "username_hash"),
            ("sanitise_srp_salt",           "srp_salt"),
            ("sanitise_srp_verifier",       "srp_verifier"),
            ("sanitise_master_key_salt",    "master_key_salt")
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

        response = PasswordHandler.start(request)

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
        self.sanitise_srp_salt_response = FailureReason.INVALID
        self.sanitise_srp_verifier_response = FailureReason.INVALID
        self.sanitise_master_key_salt_response = FailureReason.INVALID

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.start(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 4

        fields = [error.field for error in response.failure_data.error_list]
        assert "username_hash" in fields
        assert "srp_salt" in fields
        assert "srp_verifier" in fields
        assert "master_key_salt" in fields

    @pytest.mark.parametrize(
        "user_id, srp_salt, srp_verifier, master_key_salt",
        [
            (0,     b'abc',     b'def',     b'ghi'),
            (15,    b'',        b'',        b''),
            (350,   b'123'*8,   b'qcd'*100, b'ghi'*300)
        ]
    )
    def test_calls_util(self, user_id, srp_salt, srp_verifier, master_key_salt):
        """Should call the util function"""

        self.open_session_response = True, None, b'fake_decrypted_bytes', user_id
        self.from_string_response.username_hash = b'fake_username_hash'
        self.from_string_response.srp_salt = srp_salt
        self.from_string_response.srp_verifier = srp_verifier
        self.from_string_response.master_key_salt = master_key_salt

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.start(request)

        assert len(self.start_password_session_called) == 1
        start_password_session = self.start_password_session_called[0]
        assert start_password_session[0] == user_id
        assert start_password_session[1] == srp_salt
        assert start_password_session[2] == srp_verifier
        assert start_password_session[3] == master_key_salt

    @pytest.mark.parametrize(
        "failure_reason, field",
        [
            (FailureReason.UNSPECIFIED,         "unknown"),
            (FailureReason.UNKNOWN_EXCEPTION,   "server"),
            (FailureReason.USER_EXISTS,         "username"),
            (FailureReason.NOT_FOUND,           "unknown")
        ]
    )
    def test_returns_error_util_call_fails(self, failure_reason, field):
        """Should return correct error if util function fails"""

        self.start_password_session_response = False, failure_reason, "", b'', b''

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
        assert error.field == field
        assert error.code == failure_reason.error_code
        assert error.description == failure_reason.description

    def test_calls_convert_to_proto(self):
        """Should convert protobuf to bytes"""

        self.from_string_response.username_hash = b'fake_username_hash'
        self.start_password_session_response = True, None, "fake_public_id", b'fake_srp_salt', b'fake_eph_public_b'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.start(request)

        assert len(self.serialize_to_string_called) == 1

        serialize_to_string = self.serialize_to_string_called[0]
        assert isinstance(serialize_to_string, PasswordStartResponse)
        assert serialize_to_string.username_hash == b'fake_username_hash'
        assert serialize_to_string.public_id == "fake_public_id"
        assert serialize_to_string.srp_salt == b'fake_srp_salt'
        assert serialize_to_string.eph_public_b == b'fake_eph_public_b'

    def test_calls_seal_session(self):
        """Should call to seal session"""

        self.serialize_to_string_response = b'fake_serialized_bytes'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.start(request)

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

        response = PasswordHandler.start(request)

        assert response == secure_response


class TestAuth():
    """Test cases for password auth function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.open_session_called = []
        self.open_session_response = True, None, b'fake_decrypted_bytes', 0
        def fake_open_session(request, password_session = False, first_request = False):
            self.open_session_called.append((request, password_session, first_request))
            return self.open_session_response
        monkeypatch.setattr(SessionManager, "open_session", fake_open_session)

        self.from_string_called = []
        self.from_string_response = PasswordAuthRequest(
            username_hash=b'fake_username_hash',
            public_id="fake_public_id",
            eph_val_a = b'fake_eph_val_a',
            proof_val_m1 = b'fake_val_m1'
        )
        self.from_string_exception = False
        def fake_from_string(data):
            self.from_string_called.append(data)
            if self.from_string_exception:
                raise DecodeError("invalid bytes")
            else:
                return self.from_string_response
        monkeypatch.setattr(PasswordAuthRequest, "FromString", fake_from_string)

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

        self.auth_password_session_called = []
        self.auth_password_session_response = True, None, "fake_public_id", b'fake_server_proof_m2', []
        def fake_auth_password_session(user_id, public_id, eph_val_a, proof_val_m1):
            self.auth_password_session_called.append((user_id, public_id, eph_val_a, proof_val_m1))
            return self.auth_password_session_response
        monkeypatch.setattr(SessionManager, "auth_password_session", fake_auth_password_session)

        self.serialize_to_string_called = []
        self.serialize_to_string_response = b'fake_serialized_bytes'
        def fake_serialize_to_string(input):
            self.serialize_to_string_called.append(input)
            return self.serialize_to_string_response
        monkeypatch.setattr(PasswordAuthResponse, "SerializeToString", fake_serialize_to_string)

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

        response = PasswordHandler.auth(request)

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

        response = PasswordHandler.auth(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "request"
        assert error.code == ErrorCode.RQS01
        assert error.description == FailureReason.DECRYPTION.description

    def test_calls_to_convert_to_proto(self):
        """Should attempt to convert returned bytes to protobuf"""

        self.from_string_response = PasswordAuthRequest()

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.auth(request)

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

        response = PasswordHandler.auth(request)

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

        response = PasswordHandler.auth(request)

        assert len(self.sanitise_username_called) == 1
        assert self.sanitise_username_called[0] == b'fake_username_hash'

    def test_calls_sanitise_public_id(self):
        """Should call sanitise public id"""

        self.from_string_response.public_id = "fake_public_id"

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.auth(request)

        assert len(self.sanitise_public_id_called) == 1
        assert self.sanitise_public_id_called[0] == "fake_public_id"

    def test_calls_sanitise_eph_val_a(self):
        """Should call sanitise eph val a"""

        self.from_string_response.eph_val_a = b'fake_eph_val_a'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.auth(request)

        assert len(self.sanitise_eph_val_a_called) == 1
        assert self.sanitise_eph_val_a_called[0] == b'fake_eph_val_a'

    def test_calls_sanitise_proof_val_m1(self):
        """Should call sanitise proof val m1"""

        self.from_string_response.proof_val_m1 = b'fake_proof_val_m1'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.auth(request)

        assert len(self.sanitise_proof_val_m1_called) == 1
        assert self.sanitise_proof_val_m1_called[0] == b'fake_proof_val_m1'

    @pytest.mark.parametrize(
        "failing_sanitiser, field",
        [
            ("sanitise_username",           "username_hash"),
            ("sanitise_public_id",          "public_id"),
            ("sanitise_eph_val_a",          "eph_val_a"),
            ("sanitise_proof_val_m1",       "proof_val_m1")
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

        response = PasswordHandler.auth(request)

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
        self.sanitise_eph_val_a_response = FailureReason.INVALID
        self.sanitise_proof_val_m1_response = FailureReason.INVALID

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.auth(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 4

        fields = [error.field for error in response.failure_data.error_list]
        assert "username_hash" in fields
        assert "public_id" in fields
        assert "eph_val_a" in fields
        assert "proof_val_m1" in fields

    @pytest.mark.parametrize(
        "user_id, public_id, eph_val_a, proof_val_m1",
        [
            (0,     "abc",      b'def',     b'ghi'),
            (15,    "",         b'',        b''),
            (350,   "123"*8,    b'qcd'*100, b'ghi'*300)
        ]
    )
    def test_calls_util(self, user_id, public_id, eph_val_a, proof_val_m1):
        """Should call the util function"""

        self.open_session_response = True, None, b'fake_decrypted_bytes', user_id
        self.from_string_response.username_hash = b'fake_username_hash'
        self.from_string_response.public_id = public_id
        self.from_string_response.eph_val_a = eph_val_a
        self.from_string_response.proof_val_m1 = proof_val_m1

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.auth(request)

        assert len(self.auth_password_session_called) == 1
        auth_password_session = self.auth_password_session_called[0]
        assert auth_password_session[0] == user_id
        assert auth_password_session[1] == public_id
        assert auth_password_session[2] == eph_val_a
        assert auth_password_session[3] == proof_val_m1

    @pytest.mark.parametrize(
        "failure_reason, field",
        [
            (FailureReason.UNSPECIFIED,         "unknown"),
            (FailureReason.UNKNOWN_EXCEPTION,   "server"),
            (FailureReason.USER_EXISTS,         "username"),
            (FailureReason.NOT_FOUND,           "unknown")
        ]
    )
    def test_returns_error_util_call_fails(self, failure_reason, field):
        """Should return correct error if util function fails"""

        self.auth_password_session_response = False, failure_reason, "", b'', []

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.auth(request)

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
        public_ids = ["", "123", "abc", "1a2b"*30]
        self.auth_password_session_response = True, None, "fake_public_id", b'fake_server_proof_m2', public_ids

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.auth(request)

        assert len(self.serialize_to_string_called) == 1

        serialize_to_string = self.serialize_to_string_called[0]
        assert isinstance(serialize_to_string, PasswordAuthResponse)
        assert serialize_to_string.username_hash == b'fake_username_hash'
        assert serialize_to_string.session_id == "fake_public_id"
        assert serialize_to_string.server_proof_m2 == b'fake_server_proof_m2'

        for id in public_ids:
            assert id in serialize_to_string.public_ids

    def test_calls_seal_session(self):
        """Should call to seal session"""

        self.serialize_to_string_response = b'fake_serialized_bytes'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.auth(request)

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

        response = PasswordHandler.auth(request)

        assert response == secure_response


class TestComplete():
    """Test cases for password complete function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.open_session_called = []
        self.open_session_response = True, None, b'fake_decrypted_bytes', 0
        def fake_open_session(request, password_session = False, first_request = False):
            self.open_session_called.append((request, password_session, first_request))
            return self.open_session_response
        monkeypatch.setattr(SessionManager, "open_session", fake_open_session)

        self.from_string_called = []
        self.from_string_response = PasswordCompleteRequest(
            username_hash=b'fake_username_hash'
        )
        self.from_string_exception = False
        def fake_from_string(data):
            self.from_string_called.append(data)
            if self.from_string_exception:
                raise DecodeError("invalid bytes")
            else:
                return self.from_string_response
        monkeypatch.setattr(PasswordCompleteRequest, "FromString", fake_from_string)

        self.sanitise_username_called = []
        self.sanitise_username_response = None
        def fake_sanitise_username(input):
            self.sanitise_username_called.append(input)
            return self.sanitise_username_response
        monkeypatch.setattr(ServiceUtils, "sanitise_username", fake_sanitise_username)

        self.commit_called = []
        self.commit_response = True, None, None
        def fake_commit(user_id):
            self.commit_called.append(user_id)
            return self.commit_response
        monkeypatch.setattr(DBUtilsPassword, "commit", fake_commit)

        self.serialize_to_string_called = []
        self.serialize_to_string_response = b'fake_serialized_bytes'
        def fake_serialize_to_string(input):
            self.serialize_to_string_called.append(input)
            return self.serialize_to_string_response
        monkeypatch.setattr(PasswordCompleteResponse, "SerializeToString", fake_serialize_to_string)

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

        response = PasswordHandler.complete(request)

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

        response = PasswordHandler.complete(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "request"
        assert error.code == ErrorCode.RQS01
        assert error.description == FailureReason.DECRYPTION.description

    def test_calls_to_convert_to_proto(self):
        """Should attempt to convert returned bytes to protobuf"""

        self.from_string_response = PasswordAuthRequest()

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.complete(request)

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

        response = PasswordHandler.complete(request)

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

        response = PasswordHandler.complete(request)

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

        response = PasswordHandler.complete(request)

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

        response = PasswordHandler.complete(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        fields = [error.field for error in response.failure_data.error_list]
        assert "username_hash" in fields

    @pytest.mark.parametrize(
        "user_id",
        [
            (0),
            (15),
            (350)
        ]
    )
    def test_calls_util(self, user_id):
        """Should call the util function"""

        self.open_session_response = True, None, b'fake_decrypted_bytes', user_id
        self.from_string_response.username_hash = b'fake_username_hash'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.complete(request)

        assert len(self.commit_called) == 1
        commit = self.commit_called[0]
        assert commit == user_id

    @pytest.mark.parametrize(
        "failure_reason, field",
        [
            (FailureReason.UNSPECIFIED,         "unknown"),
            (FailureReason.UNKNOWN_EXCEPTION,   "server"),
            (FailureReason.USER_EXISTS,         "username"),
            (FailureReason.NOT_FOUND,           "unknown")
        ]
    )
    def test_returns_error_util_call_fails(self, failure_reason, field):
        """Should return correct error if util function fails"""

        self.commit_response = False, failure_reason, None

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.complete(request)

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
        public_ids = ["", "123", "abc", "1a2b"*30]
        self.commit_response = True, None, public_ids

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.complete(request)

        assert len(self.serialize_to_string_called) == 1

        serialize_to_string = self.serialize_to_string_called[0]
        assert isinstance(serialize_to_string, PasswordCompleteResponse)
        assert serialize_to_string.username_hash == b'fake_username_hash'

    def test_calls_seal_session(self):
        """Should call to seal session"""

        self.serialize_to_string_response = b'fake_serialized_bytes'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.complete(request)

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

        response = PasswordHandler.complete(request)

        assert response == secure_response


class TestAbort():
    """Test cases for password abort function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.open_session_called = []
        self.open_session_response = True, None, b'fake_decrypted_bytes', 0
        def fake_open_session(request, password_session = False, first_request = False):
            self.open_session_called.append((request, password_session, first_request))
            return self.open_session_response
        monkeypatch.setattr(SessionManager, "open_session", fake_open_session)

        self.from_string_called = []
        self.from_string_response = PasswordAbortRequest(
            username_hash=b'fake_username_hash'
        )
        self.from_string_exception = False
        def fake_from_string(data):
            self.from_string_called.append(data)
            if self.from_string_exception:
                raise DecodeError("invalid bytes")
            else:
                return self.from_string_response
        monkeypatch.setattr(PasswordAbortRequest, "FromString", fake_from_string)

        self.sanitise_username_called = []
        self.sanitise_username_response = None
        def fake_sanitise_username(input):
            self.sanitise_username_called.append(input)
            return self.sanitise_username_response
        monkeypatch.setattr(ServiceUtils, "sanitise_username", fake_sanitise_username)

        yield

    def test_calls_open_session(self):
        """Should pass secure request to be opened"""

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.abort(request)

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

        response = PasswordHandler.abort(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "request"
        assert error.code == ErrorCode.RQS01
        assert error.description == FailureReason.DECRYPTION.description

    def test_calls_to_convert_to_proto(self):
        """Should attempt to convert returned bytes to protobuf"""

        self.from_string_response = PasswordAuthRequest()

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = PasswordHandler.abort(request)

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

        response = PasswordHandler.abort(request)

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

        response = PasswordHandler.abort(request)

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

        response = PasswordHandler.abort(request)

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

        response = PasswordHandler.abort(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        fields = [error.field for error in response.failure_data.error_list]
        assert "username_hash" in fields


if __name__ == '__main__':
    pytest.main(['-v', __file__])
