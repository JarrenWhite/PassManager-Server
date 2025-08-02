import os
import sys
import pytest
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.service_utils import Service
from utils.utils_enums import FailureReason


class TestServiceUtils:
    """Test cases for service utility functions."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up and tear down between each test method."""
        # Set up mock patches for all sanitizing functions
        self.mock_username = patch('utils.service_utils.Service._username')
        self.mock_registration_id = patch('utils.service_utils.Service._registration_id')
        self.mock_secret_key_enc = patch('utils.service_utils.Service._secret_key_enc')
        self.mock_secret_key_plain = patch('utils.service_utils.Service._secret_key_plain')
        self.mock_default = patch('utils.service_utils.Service._default')

        # Start all mocks
        self.mock_username.start()
        self.mock_registration_id.start()
        self.mock_secret_key_enc.start()
        self.mock_secret_key_plain.start()
        self.mock_default.start()

        yield

        # Stop all mocks
        self.mock_username.stop()
        self.mock_registration_id.stop()
        self.mock_secret_key_enc.stop()
        self.mock_secret_key_plain.stop()
        self.mock_default.stop()

    def _mock_sanitize_success(self, mock_func, return_value=None):
        """Helper to mock successful sanitizing operations."""
        if return_value is not None:
            mock_func.return_value = (True, return_value)
        else:
            mock_func.return_value = (True, {})

    def _mock_sanitize_failure(self, mock_func, error_message):
        """Helper to mock failed sanitizing operations."""
        mock_func.return_value = (False, {"error": error_message})


if __name__ == '__main__':
    pytest.main(['-v', __file__])
