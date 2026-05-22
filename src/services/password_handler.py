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
        error_list = []

        # Open secure session
        open_session = SessionManager.open_session(
            request=secure_request
        )
        status, failure_reason, decrypted_bytes, user_id = open_session
        if not status:
            assert failure_reason
            error_list.append(failure_reason.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Convert to Protobuf Message
        try:
            request = PasswordStartRequest.FromString(decrypted_bytes)
        except DecodeError:
            error_list.append(FailureReason.DECRYPTION.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Sanitise Inputs
        status = ServiceUtils.sanitise_username(request.username_hash)
        if status:
            error_list.append(status.error_proto("username_hash"))
        status = ServiceUtils.sanitise_srp_salt(request.srp_salt)
        if status:
            error_list.append(status.error_proto("srp_salt"))
        status = ServiceUtils.sanitise_srp_verifier(request.srp_verifier)
        if status:
            error_list.append(status.error_proto("srp_verifier"))
        status = ServiceUtils.sanitise_master_key_salt(request.master_key_salt)
        if status:
            error_list.append(status.error_proto("master_key_salt"))

        # Return errors
        if len(error_list) > 0:
            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Call Util function
        result = SessionManager.start_password_session(
            user_id=user_id,
            srp_salt=request.srp_salt,
            srp_verifier=request.srp_verifier,
            master_key_salt=request.master_key_salt
        )
        status, failure_reason, public_id, srp_salt, public_ephemeral, master_key_salt = result



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
