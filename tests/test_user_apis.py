import os
import sys
import pytest
from unittest.mock import patch
from flask import Flask
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.user_apis import user_bp


class TestUserAPIs:
    """Test cases for user API endpoints."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up and tear down between each test method."""
        # Create a test Flask app
        self.app = Flask(__name__)
        self.app.register_blueprint(user_bp)

        # Create test client
        self.client = self.app.test_client()

        # Set up mock patches for service functions
        self.mock_begin_registration = patch('api.user_apis.begin_user_registration')
        self.mock_complete_registration = patch('api.user_apis.complete_user_registration')
        self.mock_get_user_key = patch('api.user_apis.get_user_key')
        self.mock_user_delete = patch('api.user_apis.user_delete')

        # Start & store all mocks
        self.begin_registration_mock = self.mock_begin_registration.start()
        self.complete_registration_mock = self.mock_complete_registration.start()
        self.get_user_key_mock = self.mock_get_user_key.start()
        self.user_delete_mock = self.mock_user_delete.start()

        yield

        # Stop all mocks
        self.mock_begin_registration.stop()
        self.mock_complete_registration.stop()
        self.mock_get_user_key.stop()
        self.mock_user_delete.stop()

    def _make_json_request(self, endpoint, data=None):
        """Helper to make JSON POST requests."""
        if data is None:
            data = {}
        return self.client.post(endpoint,
                              data=json.dumps(data),
                              content_type='application/json')

    def _make_form_request(self, endpoint, data=None):
        """Helper to make form POST requests."""
        if data is None:
            data = {}
        return self.client.post(endpoint, data=data)

    def test_begin_user_registration_success(self):
        """Test successful user registration key generation"""
        # Mock service response
        mock_response = {
            "registration_id": "test_registration_id_123",
            "secret_key": "test_secret_key_string"
        }
        # Set return value
        self.begin_registration_mock.return_value = (mock_response, 201)

        # Make request
        response = self.client.post('/api/user/newkey')

        # Verify response
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data == mock_response
        self.begin_registration_mock.assert_called_once()

    def test_begin_user_registration_service_failure(self):
        """Test user registration key generation when service fails"""
        # Mock service response
        mock_response = {
            "error": "Service error"
        }
        # Set return value
        self.begin_registration_mock.return_value = (mock_response, 500)

        # Make request
        response = self.client.post('/api/user/newkey')

        # Verify response
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data == mock_response
        self.begin_registration_mock.assert_called_once()

    def test_begin_user_registration_invalid_method(self):
        """Test that the endpoint only accepts POST requests"""
        # Test GET, PUT and DELETE requests
        response = self.client.get('/api/user/newkey')
        assert response.status_code == 405
        response = self.client.put('/api/user/newkey')
        assert response.status_code == 405
        response = self.client.delete('/api/user/newkey')
        assert response.status_code == 405

        # Verify response
        self.begin_registration_mock.assert_not_called()

    def test_complete_user_registration_with_json(self):
        """Test successful user registration completion with JSON data"""
        # Mock service response
        mock_response = {}
        # Set return value
        self.complete_registration_mock.return_value = (mock_response, 201)

        # Test data - all required fields for user registration
        test_data = {
            "registration_id": "test_registration_id_123",
            "secret_key_plain": "test_secret_key_bytes",
            "secret_key_enc": "encrypted_secret_key_string",
            "username": "test_user"
        }

        # Make request using JSON helper
        response = self._make_json_request('/api/user/create', test_data)

        # Verify response
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data == mock_response
        self.complete_registration_mock.assert_called_once_with(test_data)

    def test_complete_user_registration_with_form_data(self):
        """Test successful user registration completion with form data"""
        # Mock service response
        mock_response = {}
        # Set return value
        self.complete_registration_mock.return_value = (mock_response, 201)

        # Test data - all required fields for user registration
        test_data = {
            "registration_id": "test_registration_id_123",
            "secret_key_plain": "test_secret_key_bytes",
            "secret_key_enc": "encrypted_secret_key_string",
            "username": "test_user"
        }

        # Make request using form helper
        response = self._make_form_request('/api/user/create', test_data)

        # Verify response
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data == mock_response
        self.complete_registration_mock.assert_called_once_with(test_data)

    def test_complete_user_registration_invalid_method(self):
        """Test that the endpoint only accepts POST requests"""
        # Test GET, PUT and DELETE requests
        response = self.client.get('/api/user/create')
        assert response.status_code == 405
        response = self.client.put('/api/user/create')
        assert response.status_code == 405
        response = self.client.delete('/api/user/create')
        assert response.status_code == 405

        # Verify response
        self.complete_registration_mock.assert_not_called()

    def test_user_auth_with_json(self):
        """Test successful user authentication with JSON data"""
        # Mock service response
        mock_response = {"secret_key": "test_secret_key_string"}
        # Set return value
        self.get_user_key_mock.return_value = (mock_response, 201)

        # Test data - all required fields for user registration
        test_data = {
            "username": "test_user"
        }

        # Make request using JSON helper
        response = self._make_json_request('/api/user/fetchkey', test_data)

        # Verify response
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data == mock_response
        self.get_user_key_mock.assert_called_once_with(test_data)

    def test_user_auth_with_form_data(self):
        """Test successful user authentication with form data"""
        # Mock service response
        mock_response = {"secret_key": "test_secret_key_string"}
        # Set return value
        self.get_user_key_mock.return_value = (mock_response, 201)

        # Test data - all required fields for user registration
        test_data = {
            "username": "test_user"
        }

        # Make request using JSON helper
        response = self._make_form_request('/api/user/fetchkey', test_data)

        # Verify response
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data == mock_response
        self.get_user_key_mock.assert_called_once_with(test_data)

    def test_user_auth_service_failure(self):
        """Test user authentication when service fails"""
        # Mock service response
        mock_response = {
            "error": "Service error"
        }
        # Set return value
        self.get_user_key_mock.return_value = (mock_response, 500)

        # Make request
        response = self.client.post('/api/user/fetchkey')

        # Verify response
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data == mock_response
        self.get_user_key_mock.assert_called_once()

    def test_user_auth_invalid_method(self):
        """Test that the endpoint only accepts POST requests"""
        # Test GET, PUT and DELETE requests
        response = self.client.get('/api/user/fetchkey')
        assert response.status_code == 405
        response = self.client.put('/api/user/fetchkey')
        assert response.status_code == 405
        response = self.client.delete('/api/user/fetchkey')
        assert response.status_code == 405

        # Verify response
        self.get_user_key_mock.assert_not_called()

    def test_user_delete_with_json(self):
        """Test successful user deletion with JSON data"""
        # Mock service response
        mock_response = {}
        # Set return value
        self.user_delete_mock.return_value = (mock_response, 200)

        # Test data - all required fields for user deletion
        test_data = {
            "username": "test_user",
            "secret_key_plain": "test_secret_key_bytes"
        }

        # Make request using JSON helper
        response = self._make_json_request('/api/user/delete', test_data)

        # Verify response
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data == mock_response
        self.user_delete_mock.assert_called_once_with(test_data)

    def test_user_delete_with_form_data(self):
        """Test successful user deletion with form data"""
        # Mock service response
        mock_response = {}
        # Set return value
        self.user_delete_mock.return_value = (mock_response, 200)

        # Test data - all required fields for user deletion
        test_data = {
            "username": "test_user",
            "secret_key_plain": "test_secret_key_bytes"
        }

        # Make request using form helper
        response = self._make_form_request('/api/user/delete', test_data)

        # Verify response
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data == mock_response
        self.user_delete_mock.assert_called_once_with(test_data)

    def test_user_delete_service_failure(self):
        """Test user deletion when service fails"""
        # Mock service response
        mock_response = {
            "error": "Service error"
        }
        # Set return value
        self.user_delete_mock.return_value = (mock_response, 500)

        # Make request
        response = self.client.post('/api/user/delete')

        # Verify response
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data == mock_response
        self.user_delete_mock.assert_called_once()

    def test_user_delete_invalid_method(self):
        """Test that the endpoint only accepts POST requests"""
        # Test GET, PUT and DELETE requests
        response = self.client.get('/api/user/delete')
        assert response.status_code == 405
        response = self.client.put('/api/user/delete')
        assert response.status_code == 405
        response = self.client.delete('/api/user/delete')
        assert response.status_code == 405

        # Verify response
        self.user_delete_mock.assert_not_called()

    def test_health_check_success(self):
        """Test health check endpoint returns healthy status"""
        # Make GET request to health endpoint
        response = self.client.get('/api/user/health')

        # Verify response
        assert response.status_code == 200
        response_data = json.loads(response.data)
        expected_response = {
            'status': 'healthy',
            'service': 'user-api'
        }
        assert response_data == expected_response

    def test_health_check_invalid_method(self):
        """Test that the endpoint only accepts GET requests"""
        # Test POST, PUT and DELETE requests
        response = self.client.post('/api/user/health')
        assert response.status_code == 405
        response = self.client.put('/api/user/health')
        assert response.status_code == 405
        response = self.client.delete('/api/user/health')
        assert response.status_code == 405


if __name__ == '__main__':
    pytest.main(['-v', __file__])
