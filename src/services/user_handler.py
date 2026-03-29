from google.protobuf.message import DecodeError
from passmanager.common.v0.secure_pb2 import (
    SecureRequest,
    SecureResponse
)
from passmanager.user.v0.user_pb2 import (
    UserRegisterRequest,
    UserRegisterResponse
)
from passmanager.user.v0.user_payloads_pb2 import (
    UserUsernameRequest,
    UserUsernameResponse,
    UserDeleteRequest,
    UserDeleteResponse
)
from passmanager.common.v0.error_pb2 import (
    Failure
)

from utils import ServiceUtils, SessionManager, DBUtilsUser
from enums import FailureReason


# TODO - Placeholder class. Requires completion.

class UserHandler():

    @staticmethod
    def register(request: UserRegisterRequest) -> UserRegisterResponse:
        error_list = []

        # Sanitise Inputs
        status = ServiceUtils.sanitise_username(request.new_username)
        if status:
            error_list.append(status.error_proto("new_username"))
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
            return UserRegisterResponse(
                success=False,
                failure_data=failure
            )

        # Call Util function
        status, failure_reason = DBUtilsUser.create(
            username_hash=request.new_username,
            srp_salt=request.srp_salt,
            srp_verifier=request.srp_verifier,
            master_key_salt=request.master_key_salt
        )

        # Return error
        if not status:
            assert failure_reason
            error_list.append(failure_reason.error_proto("new_username"))

            failure = Failure(
                error_list=error_list
            )
            return UserRegisterResponse(
                success=False,
                failure_data=failure
            )

        # Successful Return
        success_data = UserRegisterResponse.Success(
            username_hash=request.new_username
        )
        return UserRegisterResponse(
            success=True,
            success_data=success_data
        )


    @staticmethod
    def username(secure_request: SecureRequest) -> SecureResponse:
        error_list = []

        # Open secure session
        status, decrypted_bytes, user_id, failure_reason = SessionManager.open_session(secure_request)
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
            request = UserUsernameRequest.FromString(decrypted_bytes)
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
        status = ServiceUtils.sanitise_username(request.new_username)
        if status:
            error_list.append(status.error_proto("new_username"))

        # Return Errors
        if len(error_list) > 0:
            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Call Util function
        status, failure_reason = DBUtilsUser.change_username(
            user_id=user_id,
            new_username_hash=request.new_username
        )

        # Return error
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

        # Successful Return
        response = UserUsernameResponse(
            new_username=request.new_username
        )
        response.SerializeToString()


    @staticmethod
    def delete(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()
