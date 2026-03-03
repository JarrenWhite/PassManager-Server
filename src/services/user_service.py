from passmanager.user.v0.user_pb2_grpc import UserServicer
from passmanager.common.v0.error_pb2 import (
    HealthResponse
)

from user_handler import UserHandler


class UserService(UserServicer):

    def Register(self, request, context):
        return UserHandler.register(request)

    def Username(self, request, context):
        return UserHandler.username(request)

    def Delete(self, request, context):
        return UserHandler.delete(request)

    def Health(self, request, context):
        return HealthResponse(health=True)
