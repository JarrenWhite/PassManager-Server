import os
import sys
import pytest
from flask import Flask
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.api_data import data_bp
from services.service_data import ServiceData


class TestCreate():
    """Test cases for the Data Create API endpoint"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(data_bp)
        self.client = self.app.test_client()

    def test_call_frontend(self, monkeypatch):
        """Should pass data through to frontend, and return given code"""

        called = {"count": 0, "data": None}
        def fake_service_handler(data: Dict[str, Any]):
            called["count"] += 1
            called["data"] = data
            return {"false_key": "false_data"}, 546
        monkeypatch.setattr(ServiceData, "create", fake_service_handler)

        response = self.client.post(
            '/api/data/create',
            json={"false_json_key": "false_json_data"}
        )

        assert response.status_code == 546
        assert response.is_json
        assert response.get_json() == {"false_key": "false_data"}

        assert called["count"] == 1
        assert called["data"] == {"false_json_key": "false_json_data"}

    def test_no_json_content(self, monkeypatch):
        """Should pass empty dict if no JSON or form data"""

        called = {"count": 0, "data": None}

        def fake_service_handler(data: Dict[str, Any]):
            called["count"] += 1
            called["data"] = data
            return {"false_key": "false_data"}, 200
        monkeypatch.setattr(ServiceData, "create", fake_service_handler)

        response = self.client.post('/api/data/create')

        assert response.status_code == 200
        assert response.is_json
        assert response.get_json() == {"false_key": "false_data"}

        assert called["count"] == 1
        assert called["data"] == {}

    def test_get_request(self, monkeypatch):
        """Should fail if GET request used"""

        called = {"count": 0, "data": None}
        def fake_service_handler(data: Dict[str, Any]):
            called["count"] += 1
            called["data"] = data
            return {"false_key": "false_data"}, 546
        monkeypatch.setattr(ServiceData, "create", fake_service_handler)

        response = self.client.get(
            '/api/data/create',
            json={"false_json_key": "false_json_data"}
        )

        assert response.status_code == 405
        assert not response.is_json

        assert called["count"] == 0
        assert called["data"] == None

    def test_put_request(self, monkeypatch):
        """Should fail if PUT request used"""

        called = {"count": 0, "data": None}
        def fake_service_handler(data: Dict[str, Any]):
            called["count"] += 1
            called["data"] = data
            return {"false_key": "false_data"}, 546
        monkeypatch.setattr(ServiceData, "create", fake_service_handler)

        response = self.client.put(
            '/api/data/create',
            json={"false_json_key": "false_json_data"}
        )

        assert response.status_code == 405
        assert not response.is_json

        assert called["count"] == 0
        assert called["data"] == None

    def test_delete_request(self, monkeypatch):
        """Should fail if DELETE request used"""

        called = {"count": 0, "data": None}
        def fake_service_handler(data: Dict[str, Any]):
            called["count"] += 1
            called["data"] = data
            return {"false_key": "false_data"}, 546
        monkeypatch.setattr(ServiceData, "create", fake_service_handler)

        response = self.client.delete(
            '/api/data/create',
            json={"false_json_key": "false_json_data"}
        )

        assert response.status_code == 405
        assert not response.is_json

        assert called["count"] == 0
        assert called["data"] == None


if __name__ == '__main__':
    pytest.main(['-v', __file__])
