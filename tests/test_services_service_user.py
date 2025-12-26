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

        self.fake_sanitise_inputs_called = []
        self.fake_sanitise_inputs_keys = []
        self.fake_sanitise_inputs_return = True, {}, 0
        def fake_sanitise_inputs(data, required_keys):
            self.fake_sanitise_inputs_called.append(data)
            self.fake_sanitise_inputs_keys.append(required_keys)
            return self.fake_sanitise_inputs_return
        monkeypatch.setattr(ServiceUtils, "sanitise_inputs", fake_sanitise_inputs)

        self.fake_handle_failure_calls = []
        self.fake_handle_failure_return = {}, 0
        def fake_handle_failure(failure_reason):
            self.fake_handle_failure_calls.append(failure_reason)
            return self.fake_handle_failure_return
        monkeypatch.setattr(ServiceUtils, "handle_failure", fake_handle_failure)

        yield

    def test_creates_user(self):
        """Should call DBUtilsUser to create a user"""

        data = {
            "username_hash": "fake_hash",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_salt"
        }
        response, code = ServiceUser.register(data)

        assert len(self.fake_create_calls) == 1
        assert self.fake_create_calls[0] == ("fake_hash", "fake_srp_salt", "fake_srp_verifier", "fake_master_salt")

    def test_success_response(self):
        """Should return correct response and http code"""

        data = {
            "username_hash": "fake_hash",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_salt"
        }
        response, code = ServiceUser.register(data)

        assert code == 201

        assert len(response) == 3
        assert "success" in response
        assert "username_hash" in response
        assert "errors" in response
        assert response["success"] is True
        assert response["username_hash"] == "fake_hash"
        assert response["errors"] == []

    def test_calls_sanitise_inputs(self):
        """Should call sanitise inputs with correct keys"""

        data = {
            "username_hash": "fake_hash",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_salt"
        }
        response, code = ServiceUser.register(data)

        assert len(self.fake_sanitise_inputs_called) == 1
        assert self.fake_sanitise_inputs_called[0] == data

        assert len(self.fake_sanitise_inputs_keys[0]) == 4
        assert "username_hash" in self.fake_sanitise_inputs_keys[0]
        assert "srp_salt" in self.fake_sanitise_inputs_keys[0]
        assert "srp_verifier" in self.fake_sanitise_inputs_keys[0]
        assert "master_key_salt" in self.fake_sanitise_inputs_keys[0]

    def test_sanitise_inputs_fails(self):
        """Should fail with error if sanitise input fails"""

        error = {"Sanitising Error": "Sanitising Error Message"}
        self.fake_sanitise_inputs_return = False, error, 400

        data = {
            "username_hash": "fake_hash"
        }
        response, code = ServiceUser.register(data)

        assert len(self.fake_create_calls) == 0

        assert code == 400

        assert len(response) == 2
        assert "success" in response
        assert "username_hash" not in response
        assert "errors" in response
        assert response["success"] is False
        assert response["errors"] == [error]

    def test_handle_failure_not_called(self):
        """Should not call handle_failure if call is a success"""

        data = {
            "username_hash": "fake_hash",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_salt"
        }
        response, code = ServiceUser.register(data)

        assert len(self.fake_handle_failure_calls) == 0

    def test_failure_reason_handled(self):
        """Should call handle_failure and return its response as an error"""

        self.fake_create_return = False, FailureReason.DUPLICATE

        error = {"Failure handle": "Failure handle message"}
        self.fake_handle_failure_return = error, 409

        data = {
            "username_hash": "fake_hash",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_salt"
        }
        response, code = ServiceUser.register(data)

        assert len(self.fake_create_calls) == 1
        assert self.fake_create_calls[0] == ("fake_hash", "fake_srp_salt", "fake_srp_verifier", "fake_master_salt")

        assert code == 409

        assert len(response) == 2
        assert "success" in response
        assert "username_hash" not in response
        assert "errors" in response
        assert response["success"] is False
        assert response["errors"] == [error]


class TestUsername():
    """Test cases for change username"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.fake_change_username_calls = []
        self.fake_change_username_return = True, None
        def fake_change_username(
            user_id,
            new_username
        ):
            self.fake_change_username_calls.append((user_id, new_username))
            return self.fake_change_username_return
        monkeypatch.setattr(DBUtilsUser, "change_username", fake_change_username)

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

        self.fake_handle_failure_calls = []
        self.fake_handle_failure_return = {}, 0
        def fake_handle_failure(failure_reason):
            self.fake_handle_failure_calls.append(failure_reason)
            return self.fake_handle_failure_return
        monkeypatch.setattr(ServiceUtils, "handle_failure", fake_handle_failure)

        self.fake_open_session_called = []
        self.fake_open_session_return = True, {"username": "", "new_username": ""}, 0, 0
        def fake_open_session(session_id, request_number, encrypted_data):
            self.fake_open_session_called.append((session_id, request_number, encrypted_data))
            return self.fake_open_session_return
        monkeypatch.setattr(SessionManager, "open_session", fake_open_session)

        yield

    def test_sanitise_initial_inputs(self):
        """Should call sanitise_inputs for session values"""

        data = {
            "session_id": "fake_session_id",
            "request_number": 123456,
            "encrypted_data": "fake_encrypted_data"
        }
        response, code = ServiceUser.username(data)

        assert len(self.fake_sanitise_inputs_called) >= 1
        assert self.fake_sanitise_inputs_called[0] == data

        assert len(self.fake_sanitise_inputs_keys[0]) == 3
        assert "session_id" in self.fake_sanitise_inputs_keys[0]
        assert "request_number" in self.fake_sanitise_inputs_keys[0]
        assert "encrypted_data" in self.fake_sanitise_inputs_keys[0]

    def test_initial_sanitise_inputs_fails(self):
        """Should return error message if initial sanitise input fails"""

        error = {"Error Key": "Error Message"}
        self.fake_sanitise_inputs_return = False, error, 456

        data = {
            "session_id": "fake_session_id",
            "encrypted_data": "fake_encrypted_data"
        }
        response, code = ServiceUser.username(data)

        assert code == 456

        assert len(response) == 2
        assert "success" in response
        assert "session_id" not in response
        assert "encrypted_data" not in response
        assert "errors" in response
        assert response["success"] is False
        assert response["errors"] == [error]

    def test_calls_open_session(self):
        """Should call open_session if initial sanitise is successful"""

        value = {"username": "", "new_username": ""}
        self.fake_open_session_return = True, value, 123456, None

        data = {
            "session_id": "fake_session_id",
            "request_number": 123456,
            "encrypted_data": "fake_encrypted_data"
        }
        response, code = ServiceUser.username(data)

        assert len(self.fake_open_session_called) == 1
        assert self.fake_open_session_called[0] == ("fake_session_id", 123456, "fake_encrypted_data")

    def test_open_session_fails(self):
        """Should return errors if open_session fails"""

        error = {"Error key": "Error message"}
        self.fake_open_session_return = False, error, None, 925

        data = {
            "session_id": "fake_session_id",
            "request_number": 123456,
            "encrypted_data": "fake_encrypted_data"
        }
        response, code = ServiceUser.username(data)

        assert code == 925

        assert len(response) == 3
        assert "success" in response
        assert "session_id" in response
        assert "encrypted_data" not in response
        assert "errors" in response
        assert response["success"] is False
        assert response["session_id"] == "fake_session_id"
        assert response["errors"] == [error]

    def test_secondary_sanitise_input(self):
        """Should call sanitise_inputs again with decrypted values"""

        session_data = {"username": "fake_old_username", "new_username": "fake_new_username"}
        self.fake_open_session_return = True, session_data, 123456, None

        data = {
            "session_id": "fake_session_id",
            "request_number": 123456,
            "encrypted_data": "fake_encrypted_data"
        }
        response, code = ServiceUser.username(data)

        assert len(self.fake_sanitise_inputs_called) == 2
        assert self.fake_sanitise_inputs_called[1] == session_data

        assert len(self.fake_sanitise_inputs_keys[1]) == 2
        assert "username" in self.fake_sanitise_inputs_keys[1]
        assert "new_username" in self.fake_sanitise_inputs_keys[1]

    def test_secondary_sanitise_fails(self):
        """Should return error message if secondary sanitise inputs fails"""

        error = {"Error key": "Error message"}
        self.fake_sanitise_inputs_return_2 = False, error, 654

        data = {
            "session_id": "fake_session_id",
            "request_number": 123456,
            "encrypted_data": "fake_encrypted_data"
        }
        response, code = ServiceUser.username(data)

        assert len(self.fake_sanitise_inputs_called) == 2

        assert code == 654

        assert len(response) == 2
        assert "success" in response
        assert "session_id" not in response
        assert "encrypted_data" not in response
        assert "errors" in response
        assert response["success"] is False
        assert response["errors"] == [error]

    def test_calls_change_username(self):
        """Should call change_username if all previous details correct"""

        session_data = {"username": "fake_old_username", "new_username": "fake_new_username"}
        self.fake_open_session_return = True, session_data, 123456, None

        data = {
            "session_id": "fake_session_id",
            "request_number": 123456,
            "encrypted_data": "fake_encrypted_data"
        }
        response, code = ServiceUser.username(data)

        assert len(self.fake_change_username_calls) == 1
        assert self.fake_change_username_calls[0] == (123456, "fake_new_username")

    def test_handle_failure_not_called(self):
        """Should not call handle_failure if call is a success"""

        data = {
            "session_id": "fake_session_id",
            "request_number": 123456,
            "encrypted_data": "fake_encrypted_data"
        }
        response, code = ServiceUser.username(data)

        assert len(self.fake_handle_failure_calls) == 0

    def test_failure_reason_handled(self):
        """Should call handle_failure and return its response as an error"""

        self.fake_change_username_return = False, FailureReason.NOT_FOUND

        session_data = {"username": "fake_old_username", "new_username": "fake_new_username"}
        self.fake_open_session_return = True, session_data, 123456, None

        error = {"Failure handle": "Failure handle message"}
        self.fake_handle_failure_return = error, 409

        data = {
            "session_id": "fake_session_id",
            "request_number": 123456,
            "encrypted_data": "fake_encrypted_data"
        }
        response, code = ServiceUser.username(data)

        assert len(self.fake_change_username_calls) == 1
        assert self.fake_change_username_calls[0] == (123456, "fake_new_username")
        assert len(self.fake_handle_failure_calls) == 1

        assert code == 409

        assert len(response) == 2
        assert "success" in response
        assert "username_hash" not in response
        assert "errors" in response
        assert response["success"] is False
        assert response["errors"] == [error]


class TestDelete():
    """Test cases for delete user"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.fake_delete_calls = []
        self.fake_delete_return = True, None
        def fake_delete(user_id):
            self.fake_delete_calls.append(user_id)
            return self.fake_delete_return
        monkeypatch.setattr(DBUtilsUser, "delete", fake_delete)

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

        self.fake_handle_failure_calls = []
        self.fake_handle_failure_return = {}, 0
        def fake_handle_failure(failure_reason):
            self.fake_handle_failure_calls.append(failure_reason)
            return self.fake_handle_failure_return
        monkeypatch.setattr(ServiceUtils, "handle_failure", fake_handle_failure)

        self.fake_open_session_called = []
        self.fake_open_session_return = True, {"username": "", "new_username": ""}, 0, 0
        def fake_open_session(session_id, request_number, encrypted_data):
            self.fake_open_session_called.append((session_id, request_number, encrypted_data))
            return self.fake_open_session_return
        monkeypatch.setattr(SessionManager, "open_session", fake_open_session)

        yield

    def test_sanitise_initial_inputs(self):
        """Should call sanitise_inputs for session values"""

        data = {
            "session_id": "fake_session_id",
            "request_number": 123456,
            "encrypted_data": "fake_encrypted_data"
        }
        response, code = ServiceUser.delete(data)

        assert len(self.fake_sanitise_inputs_called) >= 1
        assert self.fake_sanitise_inputs_called[0] == data

        assert len(self.fake_sanitise_inputs_keys[0]) == 3
        assert "session_id" in self.fake_sanitise_inputs_keys[0]
        assert "request_number" in self.fake_sanitise_inputs_keys[0]
        assert "encrypted_data" in self.fake_sanitise_inputs_keys[0]

    def test_initial_sanitise_inputs_fails(self):
        """Should return error message if initial sanitise input fails"""

        error = {"Error Key": "Error Message"}
        self.fake_sanitise_inputs_return = False, error, 456

        data = {
            "session_id": "fake_session_id",
            "encrypted_data": "fake_encrypted_data"
        }
        response, code = ServiceUser.delete(data)

        assert code == 456

        assert len(response) == 2
        assert "success" in response
        assert "session_id" not in response
        assert "encrypted_data" not in response
        assert "errors" in response
        assert response["success"] is False
        assert response["errors"] == [error]

    def test_calls_open_session(self):
        """Should call open_session if initial sanitise is successful"""

        value = {"username": ""}
        self.fake_open_session_return = True, value, 123456, None

        data = {
            "session_id": "fake_session_id",
            "request_number": 123456,
            "encrypted_data": "fake_encrypted_data"
        }
        response, code = ServiceUser.delete(data)

        assert len(self.fake_open_session_called) == 1
        assert self.fake_open_session_called[0] == ("fake_session_id", 123456, "fake_encrypted_data")

    def test_open_session_fails(self):
        """Should return errors if open_session fails"""

        error = {"Error key": "Error message"}
        self.fake_open_session_return = False, error, None, 925

        data = {
            "session_id": "fake_session_id",
            "request_number": 123456,
            "encrypted_data": "fake_encrypted_data"
        }
        response, code = ServiceUser.delete(data)

        assert code == 925

        assert len(response) == 3
        assert "success" in response
        assert "session_id" in response
        assert "encrypted_data" not in response
        assert "errors" in response
        assert response["success"] is False
        assert response["session_id"] == "fake_session_id"
        assert response["errors"] == [error]


if __name__ == '__main__':
    pytest.main(['-v', __file__])
