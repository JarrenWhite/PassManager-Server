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

        self.sanitise_inputs_called = []
        self.sanitise_inputs_keys = []
        self.sanitise_inputs_return = True, {}, 0
        self.sanitise_inputs_return_2 = True, {}, 0
        def fake_sanitise_inputs(data, required_keys):
            self.sanitise_inputs_called.append(data)
            self.sanitise_inputs_keys.append(required_keys)
            if self.sanitise_inputs_return:
                return_value = self.sanitise_inputs_return
                self.sanitise_inputs_return = None
                return return_value
            return self.sanitise_inputs_return_2
        monkeypatch.setattr(ServiceUtils, "sanitise_inputs", fake_sanitise_inputs)

        self.create_called = []
        self.create_return = True, None
        def fake_create(
            username_hash,
            srp_salt,
            srp_verifier,
            master_key_salt
        ):
            self.create_called.append((username_hash, srp_salt, srp_verifier, master_key_salt))
            return self.create_return
        monkeypatch.setattr(DBUtilsUser, "create", fake_create)

        self.handle_failure_called = []
        self.handle_failure_return = {}, 0
        def fake_handle_failure(failure_reason):
            self.handle_failure_called.append(failure_reason)
            return self.handle_failure_return
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

        assert len(self.sanitise_inputs_called) == 1
        assert self.sanitise_inputs_called[0] == data

        assert len(self.sanitise_inputs_keys[0]) == 4
        assert "new_username" in self.sanitise_inputs_keys[0]
        assert "srp_salt" in self.sanitise_inputs_keys[0]
        assert "srp_verifier" in self.sanitise_inputs_keys[0]
        assert "master_key_salt" in self.sanitise_inputs_keys[0]

    def test_value_sanitise_inputs_fails(self):
        """Should return false if value sanitisation fails"""

        error = {"Error message": "Error string"}
        self.sanitise_inputs_return = False, error, 456

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

        assert len(self.create_called) == 1
        assert self.create_called[0] == ("fake_username", "fake_srp_salt", "fake_srp_verifier", "fake_master_key_salt")

    def test_handle_failure_reason(self):
        """Should handle failure reason if acting function fails"""

        self.create_return = False, FailureReason.UNKNOWN_EXCEPTION

        data = {
            "new_username": "fake_username",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_key_salt"
        }
        response, code = ServiceUser.register(data)

        assert len(self.handle_failure_called) == 1
        assert self.handle_failure_called[0] == FailureReason.UNKNOWN_EXCEPTION

    def test_returns_handle_failure_error(self):
        """Should return error message from handle failure"""

        error = {"error field": "error message"}
        self.create_return = False, FailureReason.UNKNOWN_EXCEPTION
        self.handle_failure_return = error, 987

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

        assert len(self.handle_failure_called) == 0

    def test_returns_successful_message(self):
        """Should return successful message and code"""

        data = {
            "new_username": "fake_username",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_key_salt"
        }
        response, code = ServiceUser.register(data)

        assert len(response) == 2
        assert "success" in response
        assert "username_hash" in response
        assert "errors" not in response
        assert code == 201

        assert response["success"]
        assert response["username_hash"] == "fake_username"


class TestUsername():
    """Test cases for change username"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.sanitise_inputs_called = []
        self.sanitise_inputs_keys = []
        self.sanitise_inputs_return = True, {}, 0
        self.sanitise_inputs_return_2 = True, {}, 0
        def fake_sanitise_inputs(data, required_keys):
            self.sanitise_inputs_called.append(data)
            self.sanitise_inputs_keys.append(required_keys)
            if self.sanitise_inputs_return:
                return_value = self.sanitise_inputs_return
                self.sanitise_inputs_return = None
                return return_value
            return self.sanitise_inputs_return_2
        monkeypatch.setattr(ServiceUtils, "sanitise_inputs", fake_sanitise_inputs)

        self.open_session_called = []
        false_session_values = {"username": "", "new_username": ""}
        self.open_session_return = True, false_session_values, 3, None
        def fake_open_session(session_id, request_number, encrypted_data):
            self.open_session_called.append((session_id, request_number, encrypted_data))
            return self.open_session_return
        monkeypatch.setattr(SessionManager, "open_session", fake_open_session)

        yield

    def test_session_sanitise_inputs(self):
        """Should pass session values to be sanitised"""

        data = {
            "session_id": "fake_session_id",
            "request_number": 3,
            "encrypted_data": "fake_encrypted_data"
        }
        response, code = ServiceUser.username(data)

        assert len(self.sanitise_inputs_called) == 1
        assert self.sanitise_inputs_called[0] == data

        assert len(self.sanitise_inputs_keys[0]) == 3
        assert "session_id" in self.sanitise_inputs_keys[0]
        assert "request_number" in self.sanitise_inputs_keys[0]
        assert "encrypted_data" in self.sanitise_inputs_keys[0]

    def test_session_sanitise_inputs_fails(self):
        """Should return false if session sanitisation fails"""

        error = {"Error message": "Error string"}
        self.sanitise_inputs_return = False, error, 456

        data = {
            "session_id": "fake_session_id",
            "request_number": 3,
            "encrypted_data": "fake_encrypted_data"
        }
        response, code = ServiceUser.username(data)

        assert len(response) == 2
        assert "success" in response
        assert "username_hash" not in response
        assert "errors" in response
        assert code == 456

        assert not response["success"]
        assert response["errors"] == [error]

    def test_open_session_called(self):
        """Should call to open session"""

        value = {"username": ""}
        self.open_session_return = True, value, 123456, None

        data = {
            "session_id": "fake_session_id",
            "request_number": 123,
            "encrypted_data": "fake_encrypted_data"
        }
        response, code = ServiceUser.username(data)

        assert len(self.open_session_called) == 1
        assert self.open_session_called[0] == ("fake_session_id", 123, "fake_encrypted_data")


if __name__ == '__main__':
    pytest.main(['-v', __file__])
