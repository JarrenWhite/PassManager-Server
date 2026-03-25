import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from passmanager.user.v0.user_pb2 import (
    UserRegisterRequest,
    UserRegisterResponse
)

from services.user_handler import UserHandler
from utils.service_utils import ServiceUtils


class TestRegister:
    """Test cases for user register function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.sanitise_username_called = []
        self.sanitise_username_response = True, None
        def fake_sanitise_username(input):
            self.sanitise_username_called.append(input)
            return self.sanitise_username_response
        monkeypatch.setattr(ServiceUtils, "sanitise_username", fake_sanitise_username)

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


if __name__ == '__main__':
    pytest.main(['-v', __file__])
