import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from google.protobuf.message import DecodeError
from passmanager.session.v0.session_pb2 import (
    SessionStartRequest,
    SessionStartResponse,
    SessionAuthRequest,
    SessionAuthResponse
)
from passmanager.session.v0.session_payloads_pb2 import (
    SessionDeleteRequest,
    SessionDeleteResponse,
    SessionCleanRequest,
    SessionCleanResponse
)
from passmanager.common.v0.secure_pb2 import (
    SecureRequest,
    SecureResponse
)
from passmanager.common.v0.error_pb2 import (
    Failure,
    ErrorCode
)

from services.session_handler import SessionHandler
from utils.service_utils import ServiceUtils
from utils.db_utils_session import DBUtilsSession
from utils.session_manager import SessionManager
from enums.failure_reason import FailureReason


class TestStart():
    """Test cases for session start function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):

        yield


if __name__ == '__main__':
    pytest.main(['-v', __file__])
