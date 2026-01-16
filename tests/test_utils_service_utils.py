import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from utils.service_utils import ServiceUtils
from utils.session_manager import SessionManager


class TestOpenSession():
    """Test cases for open_session function"""

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

        self.open_session_called = []
        false_session_values = {"data_field": "", "data_field_two": ""}
        self.open_session_return = True, false_session_values, 3, 0
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
        success, values, user_id, errors, code = ServiceUtils.open_session(data)

        assert len(self.sanitise_inputs_called) >= 1
        assert self.sanitise_inputs_called[0] == data

        assert len(self.sanitise_inputs_keys[0]) == 3
        assert "session_id" in self.sanitise_inputs_keys[0]
        assert "request_number" in self.sanitise_inputs_keys[0]
        assert "encrypted_data" in self.sanitise_inputs_keys[0]

    def test_session_sanitise_inputs_fails(self):
        """Should return error if session sanitisation fails"""

        expected_errors = [{"Error message": "Error string"}]
        self.sanitise_inputs_return = False, expected_errors, 456

        data = {
            "session_id": "fake_session_id",
            "request_number": 3,
            "encrypted_data": "fake_encrypted_data"
        }
        success, values, user_id, errors, code = ServiceUtils.open_session(data)

        assert not success
        assert values == {}
        assert user_id == 0
        assert errors == expected_errors
        assert code == 456

    def test_open_session_called(self):
        """Should call to open session"""

        data = {
            "session_id": "fake_session_id",
            "request_number": 123,
            "encrypted_data": "fake_encrypted_data"
        }
        success, values, user_id, errors, code = ServiceUtils.open_session(data)

        assert len(self.open_session_called) == 1
        assert self.open_session_called[0] == ("fake_session_id", 123, "fake_encrypted_data")

    def test_open_session_fails(self):
        """Should return error if open session fails"""

        expected_errors = {"Error message": "Error string"}
        self.open_session_return = False, expected_errors, 0, 875

        data = {
            "session_id": "fake_session_id",
            "request_number": 3,
            "encrypted_data": "fake_encrypted_data"
        }
        success, values, user_id, errors, code = ServiceUtils.open_session(data)

        assert not success
        assert values == {}
        assert user_id == 0
        assert errors == [expected_errors]
        assert code == 875

    def test_call_is_successful(self):
        """Should return correct values if all successful"""

        false_session_values = {"data_field": "", "data_field_two": ""}
        self.open_session_return = True, false_session_values, 123456, 0

        data = {
            "session_id": "fake_session_id",
            "request_number": 3,
            "encrypted_data": "fake_encrypted_data"
        }
        success, values, user_id, errors, code = ServiceUtils.open_session(data)

        assert success
        assert values == false_session_values
        assert user_id == 123456
        assert errors == []
        assert code == 0


if __name__ == '__main__':
    pytest.main(['-v', __file__])
