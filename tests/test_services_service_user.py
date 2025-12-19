import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from services.service_user import ServiceUser
from utils.db_utils_user import DBUtilsUser


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

    def test_generates_correct_response(self, monkeypatch):
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

        assert response == {"success": True, "username_hash": "fake_hash", "errors": []}
        assert code == 201


if __name__ == '__main__':
    pytest.main(['-v', __file__])
