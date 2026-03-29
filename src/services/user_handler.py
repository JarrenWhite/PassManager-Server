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

from utils import ServiceUtils, DBUtilsUser


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

        # Fake temporary return
        success_data = UserRegisterResponse.Success(
            username_hash=b''
        )
        return UserRegisterResponse(
            success=True,
            success_data=success_data
        )


    @staticmethod
    def username(request: UserUsernameRequest) -> UserUsernameResponse:
        return UserUsernameResponse()


    @staticmethod
    def delete(request: UserDeleteRequest) -> UserDeleteResponse:
        return UserDeleteResponse()
