import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from google.protobuf.message import DecodeError
from passmanager.common.v0.secure_pb2 import (
    SecureRequest,
    SecureResponse
)
from passmanager.common.v0.error_pb2 import (
    Failure,
    ErrorCode
)

from services.password_handler import PasswordHandler
from utils.service_utils import ServiceUtils
from utils.db_utils_password import DBUtilsPassword
from utils.session_manager import SessionManager
from enums.failure_reason import FailureReason