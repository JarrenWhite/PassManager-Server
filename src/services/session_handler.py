from google.protobuf.message import DecodeError
from passmanager.common.v0.secure_pb2 import (
    SecureRequest,
    SecureResponse
)
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
from passmanager.common.v0.error_pb2 import (
    Failure
)

from utils import ServiceUtils, SessionManager, DBUtilsSession
from enums import FailureReason


# TODO - Placeholder class. Requires completion.

class SessionHandler:

    @staticmethod
    def start(request: SessionStartRequest) -> SessionStartResponse:
        return SessionStartResponse()

    @staticmethod
    def auth(request: SessionAuthRequest) -> SessionAuthResponse:
        return SessionAuthResponse()

    @staticmethod
    def delete(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()

    @staticmethod
    def clean(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()
