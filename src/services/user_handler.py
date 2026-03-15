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


# TODO - Placeholder class. Requires completion.

class UserHandler():

    @staticmethod
    def register(request: UserRegisterRequest) -> UserRegisterResponse:
        return UserRegisterResponse()

    @staticmethod
    def username(request: UserUsernameRequest) -> UserUsernameResponse:
        return UserUsernameResponse()

    @staticmethod
    def delete(request: UserDeleteRequest) -> UserDeleteResponse:
        return UserDeleteResponse()
