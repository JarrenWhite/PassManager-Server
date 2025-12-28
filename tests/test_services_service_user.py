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
        def fake_sanitise_inputs(data, required_keys):
            self.fake_sanitise_inputs_called.append(data)
            self.fake_sanitise_inputs_keys.append(required_keys)
            return self.fake_sanitise_inputs_return
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
            "new_username": "",
            "srp_salt": "",
            "srp_verifier": "",
            "master_key_salt": ""
        }
        ServiceUser.register(data)

        assert len(self.fake_sanitise_inputs_called) == 1
        assert self.fake_sanitise_inputs_called[0] == data

        assert len(self.fake_sanitise_inputs_keys[0])
        assert "new_username" in self.fake_sanitise_inputs_keys[0]
        assert "srp_salt" in self.fake_sanitise_inputs_keys[0]
        assert "srp_verifier" in self.fake_sanitise_inputs_keys[0]
        assert "master_key_salt" in self.fake_sanitise_inputs_keys[0]


if __name__ == '__main__':
    pytest.main(['-v', __file__])
