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
        error_list = []

        # Sanitise Inputs
        status = ServiceUtils.sanitise_username(request.username_hash)
        if status:
            error_list.append(status.error_proto("username_hash"))

        # Return errors
        if len(error_list) > 0:
            failure = Failure(
                error_list=error_list
            )
            return SessionStartResponse(
                success=False,
                failure_data=failure
            )

        # Call Util function
        status, failure_reason = SessionManager.start_new_session(
            username_hash=request.username_hash
        )


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
