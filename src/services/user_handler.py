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

from utils import ServiceUtils


# TODO - Placeholder class. Requires completion.

class UserHandler():

    @staticmethod
    def register(request: UserRegisterRequest) -> UserRegisterResponse:
        ServiceUtils.sanitise_username(request.new_username)
        ServiceUtils.sanitise_srp_salt(request.srp_salt)
        ServiceUtils.sanitise_srp_verifier(request.srp_verifier)
        ServiceUtils.sanitise_master_key_salt(request.master_key_salt)

        return UserRegisterResponse()


    @staticmethod
    def username(request: UserUsernameRequest) -> UserUsernameResponse:
        return UserUsernameResponse()


    @staticmethod
    def delete(request: UserDeleteRequest) -> UserDeleteResponse:
        return UserDeleteResponse()
