import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from services.service_session import ServiceSession
from enums.failure_reason import FailureReason
from utils.db_utils_session import DBUtilsSession
from utils.service_utils import ServiceUtils
from utils.session_manager import SessionManager


class TestStart():
    """Test cases for start session"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.sanitise_inputs_called = []
        self.sanitise_inputs_keys = []
        self.sanitise_inputs_return = True, {}, 0
        def fake_sanitise_inputs(data, required_keys):
            self.sanitise_inputs_called.append(data)
            self.sanitise_inputs_keys.append(required_keys)
            return self.sanitise_inputs_return
        monkeypatch.setattr(ServiceUtils, "sanitise_inputs", fake_sanitise_inputs)

        yield

    def test_value_sanitise_inputs(self):
        """Should pass final value inputs to be sanitised"""

        data = {
            "username": "fake_username"
        }
        response, code = ServiceSession.start(data)

        assert len(self.sanitise_inputs_called) == 1
        assert self.sanitise_inputs_called[0] == data

        assert len(self.sanitise_inputs_keys[0]) == 1
        assert "username" in self.sanitise_inputs_keys[0]

    def test_value_sanitise_inputs_fails(self):
        """Should return error if value sanitisation fails"""

        errors = [{"Error message": "Error string"}]
        self.sanitise_inputs_return = False, errors, 456

        data = {
            "username": "fake_username"
        }
        response, code = ServiceSession.start(data)

        assert len(response) == 2
        assert "success" in response
        assert "username_hash" not in response
        assert "errors" in response
        assert code == 456

        assert not response["success"]
        assert response["errors"] == errors


if __name__ == '__main__':
    pytest.main(['-v', __file__])
