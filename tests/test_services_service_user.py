import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from services.service_user import ServiceUser
from utils.db_utils_user import DBUtilsUser
from utils.utils_enums import FailureReason
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
            username_hash: str,
            srp_salt: str,
            srp_verifier: str,
            master_key_salt: str
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
            username_hash: str,
            srp_salt: str,
            srp_verifier: str,
            master_key_salt: str
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

    def test_sanitise_inputs_fails(self, monkeypatch):
        """Should fail with error if sanitise input fails"""

        fake_create_calls = []
        def fake_create(
            username_hash: str,
            srp_salt: str,
            srp_verifier: str,
            master_key_salt: str
        ):
            fake_create_calls.append((username_hash, srp_salt, srp_verifier, master_key_salt))
            return False, FailureReason.DUPLICATE
        monkeypatch.setattr(DBUtilsUser, "create", fake_create)

        error = {"Sanitising Error", "Sanitising Error Message"}
        def fake_sanitise_inputs(data, required_keys):
            return False, error
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

    def test_duplicate_username(self, monkeypatch):
        """Should fail with error if duplicate username"""

        fake_create_calls = []
        def fake_create(
            username_hash: str,
            srp_salt: str,
            srp_verifier: str,
            master_key_salt: str
        ):
            fake_create_calls.append((username_hash, srp_salt, srp_verifier, master_key_salt))
            return False, FailureReason.DUPLICATE
        monkeypatch.setattr(DBUtilsUser, "create", fake_create)

        data = {
            "username_hash": "fake_hash",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_salt"
        }
        response, code = ServiceUser.register(data)

        errors = [{"field": "username_hash", "error_code": "ltd00", "error": "Username hash already exists"}]

        assert len(fake_create_calls) == 1
        assert fake_create_calls[0] == ("fake_hash", "fake_srp_salt", "fake_srp_verifier", "fake_master_salt")

        assert code == 409

        assert "success" in response
        assert "username_hash" not in response
        assert "errors" in response
        assert response["success"] is False
        assert response["errors"] == errors

    def test_database_uninitialised(self, monkeypatch):
        """Should fail with error if database uninitialised"""

        fake_create_calls = []
        def fake_create(
            username_hash: str,
            srp_salt: str,
            srp_verifier: str,
            master_key_salt: str
        ):
            fake_create_calls.append((username_hash, srp_salt, srp_verifier, master_key_salt))
            return False, FailureReason.DATABASE_UNINITIALISED
        monkeypatch.setattr(DBUtilsUser, "create", fake_create)

        data = {
            "username_hash": "fake_hash",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_salt"
        }
        response, code = ServiceUser.register(data)

        errors = [{"field": "server", "error_code": "svr00", "error": "Unknown server error"}]

        assert len(fake_create_calls) == 1
        assert fake_create_calls[0] == ("fake_hash", "fake_srp_salt", "fake_srp_verifier", "fake_master_salt")

        assert code == 500

        assert "success" in response
        assert "username_hash" not in response
        assert "errors" in response
        assert response["success"] is False
        assert response["errors"] == errors

    def test_database_exception(self, monkeypatch):
        """Should fail with error if database exception"""

        fake_create_calls = []
        def fake_create(
            username_hash: str,
            srp_salt: str,
            srp_verifier: str,
            master_key_salt: str
        ):
            fake_create_calls.append((username_hash, srp_salt, srp_verifier, master_key_salt))
            return False, FailureReason.UNKNOWN_EXCEPTION
        monkeypatch.setattr(DBUtilsUser, "create", fake_create)

        data = {
            "username_hash": "fake_hash",
            "srp_salt": "fake_srp_salt",
            "srp_verifier": "fake_srp_verifier",
            "master_key_salt": "fake_master_salt"
        }
        response, code = ServiceUser.register(data)

        errors = [{"field": "server", "error_code": "svr00", "error": "Unknown server error"}]

        assert len(fake_create_calls) == 1
        assert fake_create_calls[0] == ("fake_hash", "fake_srp_salt", "fake_srp_verifier", "fake_master_salt")

        assert code == 500

        assert "success" in response
        assert "username_hash" not in response
        assert "errors" in response
        assert response["success"] is False
        assert response["errors"] == errors


if __name__ == '__main__':
    pytest.main(['-v', __file__])
