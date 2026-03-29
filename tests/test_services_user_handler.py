import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from passmanager.user.v0.user_pb2 import (
    UserRegisterRequest,
    UserRegisterResponse
)
from passmanager.common.v0.error_pb2 import (
    ErrorCode
)

from services.user_handler import UserHandler
from utils.service_utils import ServiceUtils
from enums.service_error import ServiceError


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
            ("sanitise_master_key_salt",    "master_key_salt"),
        ]
    )
    def test_each_sanitising_invalid_failure(self, failing_sanitiser, field):
        """Should fetch invalid error for each sanitation fail"""

        setattr(self, f"{failing_sanitiser}_response", ServiceError.FIELD_INVALID)

        request = UserRegisterRequest(
            new_username=b'fake_username',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
        )

        response = UserHandler.register(request)

        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == field
        assert error.code == ErrorCode.GNR00
        assert error.description == ServiceError.FIELD_INVALID.description

    @pytest.mark.parametrize(
        "failing_sanitiser, field",
        [
            ("sanitise_username",           "new_username"),
            ("sanitise_srp_salt",           "srp_salt"),
            ("sanitise_srp_verifier",       "srp_verifier"),
            ("sanitise_master_key_salt",    "master_key_salt"),
        ]
    )
    def test_each_sanitising_missing_failure(self, failing_sanitiser, field):
        """Should fetch missing error for each sanitation fail"""

        setattr(self, f"{failing_sanitiser}_response", ServiceError.FIELD_MISSING)

        request = UserRegisterRequest(
            new_username=b'fake_username',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
        )

        response = UserHandler.register(request)

        assert not response.success
        assert len(response.failure_data.error_list) == 1

        error = response.failure_data.error_list[0]
        assert error.field == field
        assert error.code == ErrorCode.GNR01
        assert error.description == ServiceError.FIELD_MISSING.description

    def test_all_sanitising_functions_fail(self):
        """Should fetch all missing errors if all sanitising fails"""

        self.sanitise_username_response = ServiceError.FIELD_MISSING
        self.sanitise_srp_salt_response = ServiceError.FIELD_MISSING
        self.sanitise_srp_verifier_response = ServiceError.FIELD_MISSING
        self.sanitise_master_key_salt_response = ServiceError.FIELD_MISSING

        request = UserRegisterRequest(
            new_username=b'fake_username',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
        )

        response = UserHandler.register(request)

        assert not response.success
        assert len(response.failure_data.error_list) == 4

        fields = [error.field for error in response.failure_data.error_list]
        assert "new_username" in fields
        assert "srp_salt" in fields
        assert "srp_verifier" in fields
        assert "master_key_salt" in fields


if __name__ == '__main__':
    pytest.main(['-v', __file__])
