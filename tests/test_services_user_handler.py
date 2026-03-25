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

        self.sanitise_srp_salt_called = []
        self.sanitise_srp_salt_response = True, None
        def fake_sanitise_srp_salt(input):
            self.sanitise_srp_salt_called.append(input)
            return self.sanitise_srp_salt_response
        monkeypatch.setattr(ServiceUtils, "sanitise_srp_salt", fake_sanitise_srp_salt)

        self.sanitise_srp_verifier_called = []
        self.sanitise_srp_verifier_response = True, None
        def fake_sanitise_srp_verifier(input):
            self.sanitise_srp_verifier_called.append(input)
            return self.sanitise_srp_verifier_response
        monkeypatch.setattr(ServiceUtils, "sanitise_srp_verifier", fake_sanitise_srp_verifier)

        self.sanitise_master_key_salt_called = []
        self.sanitise_master_key_salt_response = True, None
        def fake_sanitise_master_key_salt(input):
            self.sanitise_master_key_salt_called.append(input)
            return self.sanitise_master_key_salt_response
        monkeypatch.setattr(ServiceUtils, "sanitise_master_key_salt", fake_sanitise_master_key_salt)

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

    def test_calls_sanitise_srp_salt(self):
        """Should call sanitise srp salt"""

        request = UserRegisterRequest(
            new_username=b'fake_username',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
        )

        response = UserHandler.register(request)

        assert len(self.sanitise_srp_salt_called) == 1
        assert self.sanitise_srp_salt_called[0] == b'fake_srp_salt'

    def test_calls_sanitise_srp_verifier(self):
        """Should call sanitise srp verifier"""

        request = UserRegisterRequest(
            new_username=b'fake_username',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
        )

        response = UserHandler.register(request)

        assert len(self.sanitise_srp_verifier_called) == 1
        assert self.sanitise_srp_verifier_called[0] == b'fake_srp_verifier'

    def test_calls_sanitise_master_key_salt(self):
        """Should call sanitise master_key_salt"""

        request = UserRegisterRequest(
            new_username=b'fake_username',
            srp_salt=b'fake_srp_salt',
            srp_verifier=b'fake_srp_verifier',
            master_key_salt=b'fake_master_key_salt',
        )

        response = UserHandler.register(request)

        assert len(self.sanitise_master_key_salt_called) == 1
        assert self.sanitise_master_key_salt_called[0] == b'fake_master_key_salt'


if __name__ == '__main__':
    pytest.main(['-v', __file__])
