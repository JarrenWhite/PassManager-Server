import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from services.service_user import ServiceUser
from enums.failure_reason import FailureReason
from utils.db_utils_user import DBUtilsUser
from utils.service_utils import ServiceUtils
from utils.session_manager import SessionManager


class TestRegister():
    """Test cases for register user"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.fake_sanitise_inputs_called = []
        self.fake_sanitise_inputs_keys = []
        self.fake_sanitise_inputs_return = True, {}, 0
        self.fake_sanitise_inputs_return_2 = True, {}, 0
        def fake_sanitise_inputs(data, required_keys):
            self.fake_sanitise_inputs_called.append(data)
            self.fake_sanitise_inputs_keys.append(required_keys)
            if self.fake_sanitise_inputs_return:
                return_value = self.fake_sanitise_inputs_return
                self.fake_sanitise_inputs_return = None
                return return_value
            return self.fake_sanitise_inputs_return_2
        monkeypatch.setattr(ServiceUtils, "sanitise_inputs", fake_sanitise_inputs)

        self.fake_create_calls = []
        self.fake_create_return = True, None
        def fake_create(
            username_hash,
            srp_salt,
            srp_verifier,
            master_key_salt
        ):
            self.fake_create_calls.append((username_hash, srp_salt, srp_verifier, master_key_salt))
            return self.fake_create_return
        monkeypatch.setattr(DBUtilsUser, "create", fake_create)

        self.fake_handle_failure_calls = []
        self.fake_handle_failure_return = {}, 0
        def fake_handle_failure(failure_reason):
            self.fake_handle_failure_calls.append(failure_reason)
            return self.fake_handle_failure_return
        monkeypatch.setattr(ServiceUtils, "handle_failure", fake_handle_failure)

        yield

    def test_value_sanitise_inputs(self):
        """Should pass final value inputs to be sanitised"""

        data = {
            "new_username": "fake_username",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_key_salt"
        }
        response, code = ServiceUser.register(data)

        assert len(self.fake_sanitise_inputs_called) == 1
        assert self.fake_sanitise_inputs_called[0] == data

        assert len(self.fake_sanitise_inputs_keys[0])
        assert "new_username" in self.fake_sanitise_inputs_keys[0]
        assert "srp_salt" in self.fake_sanitise_inputs_keys[0]
        assert "srp_verifier" in self.fake_sanitise_inputs_keys[0]
        assert "master_key_salt" in self.fake_sanitise_inputs_keys[0]

    def test_value_sanitise_inputs_fails(self):
        """Should return false if value sanitisation fails"""

        error = {"Error message": "Error string"}
        self.fake_sanitise_inputs_return = False, error, 456

        data = {
            "new_username": "fake_username",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_key_salt"
        }
        response, code = ServiceUser.register(data)

        assert len(response) == 2
        assert "success" in response
        assert "username_hash" not in response
        assert "errors" in response
        assert code == 456

        assert not response["success"]
        assert response["errors"] == [error]

    def test_calls_acting_function(self):
        """Should call main acting function"""

        data = {
            "new_username": "fake_username",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_key_salt"
        }
        response, code = ServiceUser.register(data)

        assert len(self.fake_create_calls) == 1
        assert self.fake_create_calls[0] == ("fake_username", "fake_srp_salt", "fake_srp_verifier", "fake_master_key_salt")

    def test_handle_failure_reason(self):
        """Should handle failure reason if acting function fails"""

        self.fake_create_return = False, FailureReason.UNKNOWN_EXCEPTION

        data = {
            "new_username": "fake_username",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_key_salt"
        }
        response, code = ServiceUser.register(data)

        assert len(self.fake_handle_failure_calls) == 1
        assert self.fake_handle_failure_calls[0] == FailureReason.UNKNOWN_EXCEPTION

    def test_returns_handle_failure_error(self):
        """Should return error message from handle failure"""

        error = {"error field": "error message"}
        self.fake_create_return = False, FailureReason.UNKNOWN_EXCEPTION
        self.fake_handle_failure_return = error, 987

        data = {
            "new_username": "fake_username",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_key_salt"
        }
        response, code = ServiceUser.register(data)

        assert len(response) == 2
        assert "success" in response
        assert "username_hash" not in response
        assert "errors" in response
        assert code == 987

        assert not response["success"]
        assert response["errors"] == [error]

    def test_acting_function_succeeds(self):
        """Should not handle failure reason if acting function call succeeds"""

        data = {
            "new_username": "fake_username",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_key_salt"
        }
        response, code = ServiceUser.register(data)

        assert len(self.fake_handle_failure_calls) == 0


# returns success json


if __name__ == '__main__':
    pytest.main(['-v', __file__])
