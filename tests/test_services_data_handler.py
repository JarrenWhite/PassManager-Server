import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from google.protobuf.message import DecodeError
from passmanager.data.v0.data_payloads_pb2 import (
    DataCreateRequest,
    DataCreateResponse,
    DataEditRequest,
    DataEditResponse,
    DataDeleteRequest,
    DataDeleteResponse,
    DataGetRequest,
    DataGetResponse,
    DataListRequest,
    DataListResponse
)
from passmanager.common.v0.secure_pb2 import (
    SecureRequest,
    SecureResponse
)
from passmanager.common.v0.error_pb2 import (
    Failure,
    ErrorCode
)

from services.data_handler import DataHandler
from utils.service_utils import ServiceUtils
from utils.db_utils_user import DBUtilsUser
from utils.session_manager import SessionManager
from enums.failure_reason import FailureReason


class TestCreate:
    """Test cases for data create function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        self.open_session_called = []
        self.open_session_response = True, b'fake_decrypted_bytes', 0, None
        def fake_open_session(request, password_session = False, first_request = False):
            self.open_session_called.append((request, password_session, first_request))
            return self.open_session_response
        monkeypatch.setattr(SessionManager, "open_session", fake_open_session)

        yield

    def test_calls_open_session(self):
        """Should pass secure request to be opened"""

        request = SecureRequest(
            session_id="fake_session_id",
            request_number=0,
            encrypted_data=b'fake_encryption_data'
        )

        response = DataHandler.create(request)

        assert len(self.open_session_called) == 1
        assert self.open_session_called[0] == (request, True, True)


if __name__ == '__main__':
    pytest.main(['-v', __file__])
