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
        result = SessionManager.start_new_session(
            username_hash=request.username_hash
        )
        status, failure_reason, auth_id, srp_salt, eph_public_b, master_key_salt = result

        # Return error
        if not status:
            assert failure_reason
            error_list.append(failure_reason.error_proto("new_username"))

            failure = Failure(
                error_list=error_list
            )
            return SessionStartResponse(
                success=False,
                failure_data=failure
            )

        # Successful Return
        success_data = SessionStartResponse.Success(
            auth_id=auth_id,
            srp_salt=srp_salt,
            eph_public_b=eph_public_b,
            master_key_salt=master_key_salt
        )
        return SessionStartResponse(
            success=True,
            success_data=success_data
        )


    @staticmethod
    def auth(request: SessionAuthRequest) -> SessionAuthResponse:
        return SessionAuthResponse()


    @staticmethod
    def delete(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()


    @staticmethod
    def clean(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()
