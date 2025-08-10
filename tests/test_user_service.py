import os
import sys
import pytest
import hashlib
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from services.user_service import (
    begin_user_registration,
    complete_user_registration,
    get_user_key,
    user_delete
)
from utils.utils_enums import FailureReason


class TestUserService:
    """Test cases for user service functions."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up and tear down between each test method."""
        # Set up mock patches for Database functions
        self.mock_create_registration = patch('services.user_service.Database.create_registration')
        self.mock_fetch_registration = patch('services.user_service.Database.fetch_registration')
        self.mock_delete_registration = patch('services.user_service.Database.delete_registration')
        self.mock_create_user = patch('services.user_service.Database.create_user')
        self.mock_get_user_secret_key_enc = patch('services.user_service.Database.get_user_secret_key_enc')
        self.mock_get_user_secret_key_hash = patch('services.user_service.Database.get_user_secret_key_hash')
        self.mock_delete_user = patch('services.user_service.Database.delete_user')

        # Set up mock patches for Service functions
        self.mock_sanitise_inputs = patch('services.user_service.Service.sanitise_inputs')
        self.mock_handle_failure = patch('services.user_service.Service.handle_failure')

        # Set up mock patches for external modules
        self.mock_secrets = patch('services.user_service.secrets')
        self.mock_timedelta = patch('services.user_service.timedelta')

        # Start & store all mocks
        self.create_registration_mock = self.mock_create_registration.start()
        self.fetch_registration_mock = self.mock_fetch_registration.start()
        self.delete_registration_mock = self.mock_delete_registration.start()
        self.create_user_mock = self.mock_create_user.start()
        self.get_user_secret_key_enc_mock = self.mock_get_user_secret_key_enc.start()
        self.get_user_secret_key_hash_mock = self.mock_get_user_secret_key_hash.start()
        self.delete_user_mock = self.mock_delete_user.start()
        self.sanitise_inputs_mock = self.mock_sanitise_inputs.start()
        self.handle_failure_mock = self.mock_handle_failure.start()
        self.secrets_mock = self.mock_secrets.start()
        self.timedelta_mock = self.mock_timedelta.start()

        yield

        # Stop all mocks
        self.mock_create_registration.stop()
        self.mock_fetch_registration.stop()
        self.mock_delete_registration.stop()
        self.mock_create_user.stop()
        self.mock_get_user_secret_key_enc.stop()
        self.mock_get_user_secret_key_hash.stop()
        self.mock_delete_user.stop()
        self.mock_sanitise_inputs.stop()
        self.mock_handle_failure.stop()
        self.mock_secrets.stop()
        self.mock_timedelta.stop()

    def _mock_database_success(self, mock_func, return_value=None):
        """Helper to mock successful database utils operations."""
        if return_value is not None:
            mock_func.return_value = (True, None, return_value)
        else:
            mock_func.return_value = (True, None)

    def _mock_database_failure(self, mock_func, failure_reason):
        """Helper to mock failed database utils operations."""
        mock_func.return_value = (False, failure_reason, None)

    def _mock_database_failure_2(self, mock_func, failure_reason):
        """Helper to mock failed database utils operations that return 2 values."""
        mock_func.return_value = (False, failure_reason)

    def test_begin_user_registration_success(self):
        """Test successful user registration initialization."""
        # Mock key
        mock_key = b"test_secret_key_bytes"
        self.secrets_mock.token_bytes.return_value = mock_key

        # Mock database function
        mock_public_id = "test_public_id"
        self._mock_database_success(self.create_registration_mock, mock_public_id)

        # Mock response & attempt function
        mock_response = {"registration_id": mock_public_id, "secret_key": mock_key}
        response, response_code = begin_user_registration()

        # Verify response
        assert response == mock_response
        assert response_code == 201
        self.secrets_mock.token_bytes.assert_called_once_with(32)
        self.handle_failure_mock.assert_not_called()
        expected_hash = hashlib.sha256(mock_key).hexdigest()
        self.create_registration_mock.assert_called_once_with(expected_hash, self.timedelta_mock.return_value)

    def test_begin_user_registration_database_failure(self):
        """Test begin_user_registration when database create_registration fails."""
        # Mock key
        mock_key = b"test_secret_key_bytes"
        self.secrets_mock.token_bytes.return_value = mock_key

        # Mock database function
        failure_reason = FailureReason.SERVER_EXCEPTION
        self._mock_database_failure(self.create_registration_mock, failure_reason)

        # Mock failure handling
        mock_error_response = "Unknown error"
        self.handle_failure_mock.return_value = (mock_error_response, 500)

        # Call function
        response, response_code = begin_user_registration()

        # Verify response
        assert response == mock_error_response
        assert response_code == 500
        self.secrets_mock.token_bytes.assert_called_once_with(32)
        self.handle_failure_mock.assert_called_once_with(failure_reason, "begin_user_registration")
        expected_hash = hashlib.sha256(mock_key).hexdigest()
        self.create_registration_mock.assert_called_once_with(expected_hash, self.timedelta_mock.return_value)

    def test_complete_user_registration_success(self):
        """Test successful user registration completion."""
        # Mock sanitise
        self.sanitise_inputs_mock.return_value = True, {}

        # Mock fetch registration
        mock_key = b"test_secret_key_bytes"
        mock_key_hash = hashlib.sha256(mock_key).hexdigest()
        self._mock_database_success(self.fetch_registration_mock, mock_key_hash)

        # Mock create user
        self._mock_database_success(self.create_user_mock)

        # Mock delete registration
        self._mock_database_success(self.delete_registration_mock)

        # Test data
        test_data = {
            "registration_id": "test_registration_id",
            "secret_key_plain": mock_key,
            "secret_key_enc": "test_key_enc",
            "username": "test_username"
        }

        # Call function
        response, response_code = complete_user_registration(test_data)

        # Verify response
        assert response == {}
        assert response_code == 201
        self.sanitise_inputs_mock.assert_called_once_with(
            test_data,
            {"registration_id", "secret_key_plain", "secret_key_enc", "username"},
            "complete_user_registration"
        )
        self.fetch_registration_mock.assert_called_once_with("test_registration_id")
        self.create_user_mock.assert_called_once_with("test_username", mock_key_hash, "test_key_enc")
        self.delete_registration_mock.assert_called_once_with("test_registration_id")
        self.handle_failure_mock.assert_not_called()

    def test_complete_user_registration_sanitise_failure(self):
        """Test complete_user_registration when input sanitization fails."""
        # Mock sanitise failure
        mock_error_response = {"error": "Invalid input"}
        self.sanitise_inputs_mock.return_value = False, mock_error_response

        # Test data
        test_data = {
            "registration_id": "test_registration_id",
            "secret_key_plain": b"test_secret_key_bytes",
            "secret_key_enc": "test_key_enc",
            "username": "test_username"
        }

        # Call function
        response, response_code = complete_user_registration(test_data)

        # Verify response
        assert response == mock_error_response
        assert response_code == 400
        self.sanitise_inputs_mock.assert_called_once_with(
            test_data,
            {"registration_id", "secret_key_plain", "secret_key_enc", "username"},
            "complete_user_registration"
        )
        self.fetch_registration_mock.assert_not_called()
        self.create_user_mock.assert_not_called()
        self.delete_registration_mock.assert_not_called()
        self.handle_failure_mock.assert_not_called()

    def test_complete_user_registration_fetch_registration_failure(self):
        """Test complete_user_registration when fetching registration fails."""
        # Mock sanitise success
        self.sanitise_inputs_mock.return_value = True, {}

        # Mock fetch registration failure
        failure_reason = FailureReason.USERNAME_NOT_FOUND
        self._mock_database_failure(self.fetch_registration_mock, failure_reason)

        # Mock failure handling
        mock_error_response = "Registration not found"
        self.handle_failure_mock.return_value = (mock_error_response, 404)

        # Test data
        test_data = {
            "registration_id": "test_registration_id",
            "secret_key_plain": b"test_secret_key_bytes",
            "secret_key_enc": "test_key_enc",
            "username": "test_username"
        }

        # Call function
        response, response_code = complete_user_registration(test_data)

        # Verify response
        assert response == mock_error_response
        assert response_code == 404
        self.sanitise_inputs_mock.assert_called_once_with(
            test_data,
            {"registration_id", "secret_key_plain", "secret_key_enc", "username"},
            "complete_user_registration"
        )
        self.fetch_registration_mock.assert_called_once_with("test_registration_id")
        self.handle_failure_mock.assert_called_once_with(failure_reason, "complete_user_registration")
        self.create_user_mock.assert_not_called()
        self.delete_registration_mock.assert_not_called()

    def test_complete_user_registration_secret_key_mismatch(self):
        """Test complete_user_registration when secret key hash doesn't match."""
        # Mock sanitise
        self.sanitise_inputs_mock.return_value = True, {}

        # Mock fetch registration success with different key hash
        mock_key = b"test_secret_key_bytes"
        mock_key_hash = hashlib.sha256(mock_key).hexdigest()
        self._mock_database_success(self.fetch_registration_mock, mock_key_hash)

        # Test data with different secret key
        different_key = b"different_secret_key_bytes"
        test_data = {
            "registration_id": "test_registration_id",
            "secret_key_plain": different_key,
            "secret_key_enc": "test_key_enc",
            "username": "test_username"
        }

        # Call function
        response, response_code = complete_user_registration(test_data)

        # Verify response
        expected_error = {"error": "The received key does not match the stored one for this ID"}
        assert response == expected_error
        assert response_code == 400
        self.sanitise_inputs_mock.assert_called_once_with(
            test_data,
            {"registration_id", "secret_key_plain", "secret_key_enc", "username"},
            "complete_user_registration"
        )
        self.fetch_registration_mock.assert_called_once_with("test_registration_id")
        self.create_user_mock.assert_not_called()
        self.delete_registration_mock.assert_not_called()
        self.handle_failure_mock.assert_not_called()

    def test_complete_user_registration_create_user_failure(self):
        """Test complete_user_registration when user creation fails."""
        # Mock sanitise
        self.sanitise_inputs_mock.return_value = True, {}

        # Mock fetch registration
        mock_key = b"test_secret_key_bytes"
        mock_key_hash = hashlib.sha256(mock_key).hexdigest()
        self._mock_database_success(self.fetch_registration_mock, mock_key_hash)

        # Mock create user failure
        failure_reason = FailureReason.ALREADY_EXISTS
        self._mock_database_failure_2(self.create_user_mock, failure_reason)

        # Mock failure handling
        mock_error_response = "User already exists"
        self.handle_failure_mock.return_value = (mock_error_response, 409)

        # Test data
        test_data = {
            "registration_id": "test_registration_id",
            "secret_key_plain": mock_key,
            "secret_key_enc": "test_key_enc",
            "username": "test_username"
        }

        # Call function
        response, response_code = complete_user_registration(test_data)

        # Verify response
        assert response == mock_error_response
        assert response_code == 409
        self.sanitise_inputs_mock.assert_called_once_with(
            test_data,
            {"registration_id", "secret_key_plain", "secret_key_enc", "username"},
            "complete_user_registration"
        )
        self.fetch_registration_mock.assert_called_once_with("test_registration_id")
        self.create_user_mock.assert_called_once_with("test_username", mock_key_hash, "test_key_enc")
        self.handle_failure_mock.assert_called_once_with(failure_reason, "complete_user_registration")
        self.delete_registration_mock.assert_not_called()

    def test_complete_user_registration_delete_registration_failure(self):
        """Test complete_user_registration when registration deletion fails but user is created."""
        # Mock sanitise
        self.sanitise_inputs_mock.return_value = True, {}

        # Mock fetch registration
        mock_key = b"test_secret_key_bytes"
        mock_key_hash = hashlib.sha256(mock_key).hexdigest()
        self._mock_database_success(self.fetch_registration_mock, mock_key_hash)

        # Mock create user
        self._mock_database_success(self.create_user_mock)

        # Mock delete registration failure
        failure_reason = FailureReason.SERVER_EXCEPTION
        self._mock_database_failure_2(self.delete_registration_mock, failure_reason)

        # Test data
        test_data = {
            "registration_id": "test_registration_id",
            "secret_key_plain": mock_key,
            "secret_key_enc": "test_key_enc",
            "username": "test_username"
        }

        # Call function
        response, response_code = complete_user_registration(test_data)

        # Verify response
        assert response == {}
        assert response_code == 201
        self.sanitise_inputs_mock.assert_called_once_with(
            test_data,
            {"registration_id", "secret_key_plain", "secret_key_enc", "username"},
            "complete_user_registration"
        )
        self.fetch_registration_mock.assert_called_once_with("test_registration_id")
        self.create_user_mock.assert_called_once_with("test_username", mock_key_hash, "test_key_enc")
        self.delete_registration_mock.assert_called_once_with("test_registration_id")
        self.handle_failure_mock.assert_not_called()

    def test_get_user_key_success(self):
        """Test successful retrieval of user's encrypted secret key."""
        # Mock sanitise success
        self.sanitise_inputs_mock.return_value = True, {}

        # Mock database function success
        mock_secret_key_enc = "test_encrypted_secret_key"
        self._mock_database_success(self.get_user_secret_key_enc_mock, mock_secret_key_enc)

        # Test data
        test_data = {"username": "test_username"}

        # Call function
        response, response_code = get_user_key(test_data)

        # Verify response
        expected_response = {"secret_key": mock_secret_key_enc}
        assert response == expected_response
        assert response_code == 200
        self.sanitise_inputs_mock.assert_called_once_with(
            test_data,
            {"username"},
            "get_user_key"
        )
        self.get_user_secret_key_enc_mock.assert_called_once_with("test_username")
        self.handle_failure_mock.assert_not_called()

    def test_get_user_key_sanitise_failure(self):
        """Test get_user_key when input sanitization fails."""
        # Mock sanitise failure
        mock_error_response = {"error": "Invalid input"}
        self.sanitise_inputs_mock.return_value = False, mock_error_response

        # Test data
        test_data = {"username": "test_username"}

        # Call function
        response, response_code = get_user_key(test_data)

        # Verify response
        assert response == mock_error_response
        assert response_code == 400
        self.sanitise_inputs_mock.assert_called_once_with(
            test_data,
            {"username"},
            "get_user_key"
        )
        self.get_user_secret_key_enc_mock.assert_not_called()
        self.handle_failure_mock.assert_not_called()

    def test_get_user_key_database_failure(self):
        """Test get_user_key when database get_user_secret_key_enc fails."""
        # Mock sanitise success
        self.sanitise_inputs_mock.return_value = True, {}

        # Mock database function failure
        failure_reason = FailureReason.USERNAME_NOT_FOUND
        self._mock_database_failure(self.get_user_secret_key_enc_mock, failure_reason)

        # Mock failure handling
        mock_error_response = "User not found"
        self.handle_failure_mock.return_value = (mock_error_response, 404)

        # Test data
        test_data = {"username": "test_username"}

        # Call function
        response, response_code = get_user_key(test_data)

        # Verify response
        assert response == mock_error_response
        assert response_code == 404
        self.sanitise_inputs_mock.assert_called_once_with(
            test_data,
            {"username"},
            "get_user_key"
        )
        self.get_user_secret_key_enc_mock.assert_called_once_with("test_username")
        self.handle_failure_mock.assert_called_once_with(failure_reason, "get_user_key")

    def test_user_delete_success(self):
        """Test successful user deletion."""
        pass

    def test_user_delete_sanitise_failure(self):
        """Test user_delete when input sanitization fails."""
        pass

    def test_user_delete_get_hash_failure(self):
        """Test user_delete when fetching user's secret key hash fails."""
        pass

    def test_user_delete_secret_key_mismatch(self):
        """Test user_delete when secret key hash doesn't match (authentication fails)."""
        pass

    def test_user_delete_database_delete_failure(self):
        """Test user_delete when database delete_user operation fails."""
        pass


if __name__ == '__main__':
    pytest.main(['-v', __file__])
