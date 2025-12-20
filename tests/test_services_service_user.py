import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from services.service_user import ServiceUser
from enums.failure_reason import FailureReason
from utils.db_utils_user import DBUtilsUser
from utils.service_utils import ServiceUtils


class TestRegister():
    """Test cases for register user"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        yield

    def test_creates_user(self, monkeypatch):
        """Should call DBUtilsUser to create a user"""

        fake_create_calls = []
        def fake_create(
            username_hash,
            srp_salt,
            srp_verifier,
            master_key_salt
        ):
            fake_create_calls.append((username_hash, srp_salt, srp_verifier, master_key_salt))
            return True, None
        monkeypatch.setattr(DBUtilsUser, "create", fake_create)

        data = {
            "username_hash": "fake_hash",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_salt"
        }
        response, code = ServiceUser.register(data)

        assert len(fake_create_calls) == 1
        assert fake_create_calls[0] == ("fake_hash", "fake_srp_salt", "fake_srp_verifier", "fake_master_salt")

    def test_success_response(self, monkeypatch):
        """Should return correct response and http code"""

        fake_create_calls = []
        def fake_create(
            username_hash,
            srp_salt,
            srp_verifier,
            master_key_salt
        ):
            fake_create_calls.append((username_hash, srp_salt, srp_verifier, master_key_salt))
            return True, None
        monkeypatch.setattr(DBUtilsUser, "create", fake_create)

        data = {
            "username_hash": "fake_hash",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_salt"
        }
        response, code = ServiceUser.register(data)

        assert code == 201

        assert "success" in response
        assert "username_hash" in response
        assert "errors" in response
        assert response["success"] is True
        assert response["username_hash"] == "fake_hash"
        assert response["errors"] == []

    def test_calls_sanitise_inputs(self, monkeypatch):
        """Should call sanitise inputs with correct keys"""

        fake_create_calls = []
        def fake_create(
            username_hash,
            srp_salt,
            srp_verifier,
            master_key_salt
        ):
            fake_create_calls.append((username_hash, srp_salt, srp_verifier, master_key_salt))
            return True, None
        monkeypatch.setattr(DBUtilsUser, "create", fake_create)

        fake_sanitise_inputs_called = []
        error = {"Sanitising Error": "Sanitising Error Message"}
        def fake_sanitise_inputs(data, required_keys):
            for key in required_keys:
                fake_sanitise_inputs_called.append(key)
            return False, error, 400
        monkeypatch.setattr(ServiceUtils, "sanitise_inputs", fake_sanitise_inputs)

        data = {
            "username_hash": "fake_hash",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_salt"
        }
        response, code = ServiceUser.register(data)

        assert len(fake_sanitise_inputs_called) == 4
        assert "username_hash" in fake_sanitise_inputs_called
        assert "srp_salt" in fake_sanitise_inputs_called
        assert "srp_verifier" in fake_sanitise_inputs_called
        assert "master_key_salt" in fake_sanitise_inputs_called

    def test_sanitise_inputs_fails(self, monkeypatch):
        """Should fail with error if sanitise input fails"""

        fake_create_calls = []
        def fake_create(
            username_hash,
            srp_salt,
            srp_verifier,
            master_key_salt
        ):
            fake_create_calls.append((username_hash, srp_salt, srp_verifier, master_key_salt))
            return False, FailureReason.DUPLICATE
        monkeypatch.setattr(DBUtilsUser, "create", fake_create)

        error = {"Sanitising Error": "Sanitising Error Message"}
        def fake_sanitise_inputs(data, required_keys):
            return False, error, 400
        monkeypatch.setattr(ServiceUtils, "sanitise_inputs", fake_sanitise_inputs)

        data = {
            "username_hash": "fake_hash"
        }
        response, code = ServiceUser.register(data)

        assert len(fake_create_calls) == 0

        assert code == 400

        assert "success" in response
        assert "username_hash" not in response
        assert "errors" in response
        assert response["success"] is False
        assert response["errors"] == [error]

    def test_handle_failure_not_called(self, monkeypatch):
        """Should not call handle_failure if call is a success"""

        fake_create_calls = []
        def fake_create(
            username_hash,
            srp_salt,
            srp_verifier,
            master_key_salt
        ):
            fake_create_calls.append((username_hash, srp_salt, srp_verifier, master_key_salt))
            return True, None
        monkeypatch.setattr(DBUtilsUser, "create", fake_create)

        fake_handle_failure_calls = []
        def fake_handle_failure(failure_reason):
            fake_handle_failure_calls.append(failure_reason)
            return {}, 200
        monkeypatch.setattr(ServiceUtils, "handle_failure", fake_handle_failure)

        data = {
            "username_hash": "fake_hash",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_salt"
        }
        response, code = ServiceUser.register(data)

        assert len(fake_handle_failure_calls) == 0

    def test_failure_reason_handled(self, monkeypatch):
        """Should call handle_failure and return its response as an error"""

        fake_create_calls = []
        def fake_create(
            username_hash,
            srp_salt,
            srp_verifier,
            master_key_salt
        ):
            fake_create_calls.append((username_hash, srp_salt, srp_verifier, master_key_salt))
            return False, FailureReason.DUPLICATE
        monkeypatch.setattr(DBUtilsUser, "create", fake_create)

        fake_handle_failure_calls = []
        error = {"Failure handle": "Failure handle message"}
        def fake_handle_failure(failure_reason):
            fake_handle_failure_calls.append(failure_reason)
            return error, 409
        monkeypatch.setattr(ServiceUtils, "handle_failure", fake_handle_failure)

        data = {
            "username_hash": "fake_hash",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_salt"
        }
        response, code = ServiceUser.register(data)

        assert len(fake_create_calls) == 1
        assert fake_create_calls[0] == ("fake_hash", "fake_srp_salt", "fake_srp_verifier", "fake_master_salt")

        assert code == 409

        assert "success" in response
        assert "username_hash" not in response
        assert "errors" in response
        assert response["success"] is False
        assert response["errors"] == [error]


if __name__ == '__main__':
    pytest.main(['-v', __file__])
