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

        # Start all mocks
        self.mock_begin_registration.start()
        self.mock_complete_registration.start()
        self.mock_get_user_key.start()
        self.mock_user_delete.start()

        yield

        # Stop all mocks
        self.mock_begin_registration.stop()
        self.mock_complete_registration.stop()
        self.mock_get_user_key.stop()
        self.mock_user_delete.stop()

    def _mock_service_response(self, mock_func, return_data, status_code):
        """Helper to set up mock service function responses."""
        mock_func.return_value = (return_data, status_code)

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
