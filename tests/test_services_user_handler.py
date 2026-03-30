import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from google.protobuf.message import DecodeError
from passmanager.user.v0.user_pb2 import (
    UserRegisterRequest,
    UserRegisterResponse
)
from passmanager.user.v0.user_payloads_pb2 import (
    UserUsernameRequest,
    UserUsernameResponse
)
from passmanager.common.v0.secure_pb2 import (
    SecureRequest,
    SecureResponse
)
from passmanager.common.v0.error_pb2 import (
    Failure,
    ErrorCode
)

from services.user_handler import UserHandler
from utils.service_utils import ServiceUtils
from utils.db_utils_user import DBUtilsUser
from utils.session_manager import SessionManager
from enums.failure_reason import FailureReason


class TestRegister:
    """Test cases for user register function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

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

        self.create_called = []
        self.create_response = True, None
        def fake_create(username_hash, srp_salt, srp_verifier, master_key_salt):
            self.create_called.append((username_hash, srp_salt, srp_verifier, master_key_salt))
            return self.create_response
        monkeypatch.setattr(DBUtilsUser, "create", fake_create)

        yield

    def test_calls_sanitise_username(self):
        """Should call sanitise username"""

        request = UserRegisterRequest(
            new_username=b'fake_username',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
        )

        response = UserHandler.register(request)

        assert len(self.sanitise_username_called) == 1
        assert self.sanitise_username_called[0] == b'fake_username'

    def test_calls_sanitise_srp_salt(self):
        """Should call sanitise srp salt"""

        request = UserRegisterRequest(
            new_username=b'fake_username',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
        )

        response = UserHandler.register(request)

        assert len(self.sanitise_srp_salt_called) == 1
        assert self.sanitise_srp_salt_called[0] == b'fake_srp_salt'

    def test_calls_sanitise_srp_verifier(self):
        """Should call sanitise srp verifier"""

        request = UserRegisterRequest(
            new_username=b'fake_username',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
        )

        response = UserHandler.register(request)

        assert len(self.sanitise_srp_verifier_called) == 1
        assert self.sanitise_srp_verifier_called[0] == b'fake_srp_verifier'

    def test_calls_sanitise_master_key_salt(self):
        """Should call sanitise master key salt"""

        request = UserRegisterRequest(
            new_username=b'fake_username',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
        )

        response = UserHandler.register(request)

        assert len(self.sanitise_master_key_salt_called) == 1
        assert self.sanitise_master_key_salt_called[0] == b'fake_master_key_salt'

    @pytest.mark.parametrize(
        "failing_sanitiser, field",
        [
            ("sanitise_username",           "new_username"),
            ("sanitise_srp_salt",           "srp_salt"),
            ("sanitise_srp_verifier",       "srp_verifier"),
            ("sanitise_master_key_salt",    "master_key_salt")
        ]
    )
    def test_each_sanitising_invalid_failure(self, failing_sanitiser, field):
        """Should fetch invalid error for each sanitation fail"""

        setattr(self, f"{failing_sanitiser}_response", FailureReason.INVALID)

        request = UserRegisterRequest(
            new_username=b'fake_username',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
        )

        response = UserHandler.register(request)

        assert isinstance(response, UserRegisterResponse)
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

        request = UserRegisterRequest(
            new_username=b'fake_username',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
        )

        response = UserHandler.register(request)

        assert isinstance(response, UserRegisterResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 4

        fields = [error.field for error in response.failure_data.error_list]
        assert "new_username" in fields
        assert "srp_salt" in fields
        assert "srp_verifier" in fields
        assert "master_key_salt" in fields

    def test_calls_create(self):
        """Should call the user create function"""

        request = UserRegisterRequest(
            new_username=b'fake_username',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
        )

        response = UserHandler.register(request)

        assert len(self.create_called) == 1

        create = self.create_called[0]
        assert create[0] == b'fake_username'
        assert create[1] == b'fake_srp_salt'
        assert create[2] == b'fake_srp_verifier'
        assert create[3] == b'fake_master_key_salt'

    @pytest.mark.parametrize(
        "failure_reason, field",
        [
            (FailureReason.UNSPECIFIED,         "unknown"),
            (FailureReason.UNKNOWN_EXCEPTION,   "server"),
            (FailureReason.USER_EXISTS,         "username"),
            (FailureReason.NOT_FOUND,           "new_username")
        ]
    )
    def test_returns_error_create_call_fails(self, failure_reason, field):
        """Should return correct error if user create function fails"""

        self.create_response = False, failure_reason

        request = UserRegisterRequest(
            new_username=b'fake_username',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
        )

        response = UserHandler.register(request)

        assert isinstance(response, UserRegisterResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == field
        assert error.code == failure_reason.error_code
        assert error.description == failure_reason.description

    def test_successful_completion(self):
        """Should return successful result"""

        request = UserRegisterRequest(
            new_username=b'fake_username',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
        )

        response = UserHandler.register(request)

        assert isinstance(response, UserRegisterResponse)
        assert response.success
        assert response.success_data.username_hash == b'fake_username'


class TestUsername:
    """Test cases for user username function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.open_session_called = []
        self.open_session_response = True, b'fake_decrypted_bytes', 0, None
        def fake_open_session(request):
            self.open_session_called.append(request)
            return self.open_session_response
        monkeypatch.setattr(SessionManager, "open_session", fake_open_session)

        self.from_string_called = []
        self.from_string_response = UserUsernameRequest(
            username_hash=b'fake_username_hash',
            new_username=b'fake_new_username'
        )
        self.from_string_exception = False
        def fake_from_string(data):
            self.from_string_called.append(data)
            if self.from_string_exception:
                raise DecodeError("invalid bytes")
            else:
                return self.from_string_response
        monkeypatch.setattr(UserUsernameRequest, "FromString", fake_from_string)

        self.sanitise_username_called = []
        self.sanitise_username_responses = []
        def fake_sanitise_username(input):
            idx = len(self.sanitise_username_called)
            self.sanitise_username_called.append(input)
            if idx < len(self.sanitise_username_responses):
                return self.sanitise_username_responses[idx]
            return None
        monkeypatch.setattr(ServiceUtils, "sanitise_username", fake_sanitise_username)

        self.change_username_called = []
        self.change_username_response = True, None
        def fake_change_username(user_id, new_username_hash):
            self.change_username_called.append((user_id, new_username_hash))
            return self.change_username_response
        monkeypatch.setattr(DBUtilsUser, "change_username", fake_change_username)

        self.serialize_to_string_called = []
        self.serialize_to_string_response = b'fake_serialized_bytes'
        def fake_serialize_to_string(input):
            self.serialize_to_string_called.append(input)
            return self.serialize_to_string_response
        monkeypatch.setattr(UserUsernameResponse, "SerializeToString", fake_serialize_to_string)

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

        response = UserHandler.username(request)

        assert len(self.open_session_called) == 1
        assert self.open_session_called[0] == request

    def test_open_session_fails(self):
        """Should return error if open session fails"""

        self.open_session_response = False, b'', 0, FailureReason.DECRYPTION

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = UserHandler.username(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "request"
        assert error.code == ErrorCode.RQS01
        assert error.description == FailureReason.DECRYPTION.description

    def test_calls_to_convert_to_proto(self):
        """Should attempt to convert returned bytes to protobuf"""

        self.from_string_response = UserUsernameRequest()

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = UserHandler.username(request)

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

        response = UserHandler.username(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "request"
        assert error.code == ErrorCode.RQS01
        assert error.description == FailureReason.DECRYPTION.description

    def test_calls_sanitise_username_for_existing(self):
        """Should call sanitise username for existing username"""

        self.from_string_response.username_hash = b'fake_username_hash'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = UserHandler.username(request)

        assert len(self.sanitise_username_called) >= 1
        assert self.sanitise_username_called[0] == b'fake_username_hash'

    def test_calls_sanitise_username_for_new(self):
        """Should call sanitise username for new username"""

        self.from_string_response.new_username = b'fake_new_username'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = UserHandler.username(request)

        assert len(self.sanitise_username_called) == 2
        assert self.sanitise_username_called[1] == b'fake_new_username'

    def test_sanitise_existing_username_fails(self):
        """Should fail if existing username is not sanitary"""

        self.sanitise_username_responses = [FailureReason.INVALID]

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = UserHandler.username(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "username_hash"
        assert error.code == ErrorCode.GNR00
        assert error.description == FailureReason.INVALID.description

    def test_sanitise_new_username_fails(self):
        """Should fail if new username is not sanitary"""

        self.sanitise_username_responses = [None, FailureReason.INVALID]

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = UserHandler.username(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "new_username"
        assert error.code == ErrorCode.GNR00
        assert error.description == FailureReason.INVALID.description

    def test_all_sanitising_functions_fail(self):
        """Should fetch all missing errors if all sanitising fails"""

        self.sanitise_username_responses = [FailureReason.INVALID, FailureReason.INVALID]

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = UserHandler.username(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 2

        fields = [error.field for error in response.failure_data.error_list]
        assert "username_hash" in fields
        assert "new_username" in fields

    @pytest.mark.parametrize(
        "user_id",
        [
            0,
            15,
            350
        ]
    )
    def test_calls_change_username(self, user_id):
        """Should call the user change username function"""

        self.open_session_response = True, b'fake_decrypted_bytes', user_id, None
        self.from_string_response.new_username = b'fake_new_username'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = UserHandler.username(request)

        assert len(self.change_username_called) == 1

        change_username = self.change_username_called[0]
        assert change_username[0] == user_id
        assert change_username[1] == b'fake_new_username'

    @pytest.mark.parametrize(
        "failure_reason, field",
        [
            (FailureReason.UNSPECIFIED,         "unknown"),
            (FailureReason.UNKNOWN_EXCEPTION,   "server"),
            (FailureReason.USER_EXISTS,         "username"),
            (FailureReason.NOT_FOUND,           "unknown")
        ]
    )
    def test_returns_error_change_username_call_fails(self, failure_reason, field):
        """Should return correct error if user change username function fails"""

        self.change_username_response = False, failure_reason

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = UserHandler.username(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == field
        assert error.code == failure_reason.error_code
        assert error.description == failure_reason.description

    def test_calls_convert_to_proto(self):
        """Should convert protobuf to bytes"""

        self.from_string_response.new_username = b'fake_new_username'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = UserHandler.username(request)

        assert len(self.serialize_to_string_called) == 1

        serialize_to_string = self.serialize_to_string_called[0]
        assert isinstance(serialize_to_string, UserUsernameResponse)
        assert serialize_to_string.new_username == b'fake_new_username'

    def test_calls_seal_session(self):
        """Should call to seal session"""

        self.serialize_to_string_response = b'fake_serialized_bytes'

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = UserHandler.username(request)

        assert len(self.seal_session_called) == 1
        assert self.seal_session_called[0] == b'fake_serialized_bytes'

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

        response = UserHandler.username(request)

        assert response == secure_response


class TestDelete():
    """Test cases for user delete function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.open_session_called = []
        self.open_session_response = True, b'fake_decrypted_bytes', 0, None
        def fake_open_session(request):
            self.open_session_called.append(request)
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

        response = UserHandler.delete(request)

        assert len(self.open_session_called) == 1
        assert self.open_session_called[0] == request

    def test_open_session_fails(self):
        """Should return error if open session fails"""

        self.open_session_response = False, b'', 0, FailureReason.DECRYPTION

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = UserHandler.delete(request)

        assert isinstance(response, SecureResponse)
        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == "request"
        assert error.code == ErrorCode.RQS01
        assert error.description == FailureReason.DECRYPTION.description


if __name__ == '__main__':
    pytest.main(['-v', __file__])
