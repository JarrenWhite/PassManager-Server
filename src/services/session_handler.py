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
        status, failure_reason, public_id, srp_salt, eph_public_b, master_key_salt = result

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
            public_id=public_id,
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
        error_list = []

        # Sanitise Inputs
        status = ServiceUtils.sanitise_username(request.username_hash)
        if status:
            error_list.append(status.error_proto("username_hash"))
        status = ServiceUtils.sanitise_public_id(request.public_id)
        if status:
            error_list.append(status.error_proto("public_id"))
        status = ServiceUtils.sanitise_eph_val_a(request.eph_val_a)
        if status:
            error_list.append(status.error_proto("eph_val_a"))
        status = ServiceUtils.sanitise_proof_val_m1(request.proof_val_m1)
        if status:
            error_list.append(status.error_proto("proof_val_m1"))
        status = ServiceUtils.sanitise_maximum_requests(request.maximum_requests)
        if status:
            error_list.append(status.error_proto("maximum_requests"))
        status = ServiceUtils.sanitise_expiry_time(request.expiry_time)
        if status:
            error_list.append(status.error_proto("expiry_time"))

        # Return errors
        if len(error_list) > 0:
            failure = Failure(
                error_list=error_list
            )
            return SessionAuthResponse(
                success=False,
                failure_data=failure
            )



        return SessionAuthResponse()


    @staticmethod
    def delete(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()


    @staticmethod
    def clean(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()
