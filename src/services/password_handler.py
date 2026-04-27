from google.protobuf.message import DecodeError
from passmanager.common.v0.secure_pb2 import (
    SecureRequest,
    SecureResponse
)
from passmanager.password.v0.password_payloads_pb2 import (
    PasswordStartRequest,
    PasswordStartResponse,
    PasswordAuthRequest,
    PasswordAuthResponse,
    PasswordCompleteRequest,
    PasswordCompleteResponse,
    PasswordAbortRequest,
    PasswordAbortResponse,
    PasswordGetRequest,
    PasswordGetResponse,
    PasswordUpdateRequest,
    PasswordUpdateResponse
)
from passmanager.common.v0.error_pb2 import (
    Failure
)

from utils import ServiceUtils, SessionManager, DBUtilsPassword
from enums import FailureReason


# TODO - Placeholder class. Requires completion.

class PasswordHandler():

    @staticmethod
    def start(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()

    @staticmethod
    def auth(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()

    @staticmethod
    def complete(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()

    @staticmethod
    def abort(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()

    @staticmethod
    def get(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()

    @staticmethod
    def update(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()
