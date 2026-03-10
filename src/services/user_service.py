from logging import getLogger
logger = getLogger("api")

from passmanager.user.v0.user_pb2_grpc import UserServicer
from passmanager.common.v0.error_pb2 import (
    HealthResponse
)

from user_handler import UserHandler


class UserService(UserServicer):

    def Register(self, request, context):
        logger.info("Register called by: %s", context.peer())
        return UserHandler.register(request)

    def Username(self, request, context):
        logger.info("Username called by: %s", context.peer())
        return UserHandler.username(request)

    def Delete(self, request, context):
        logger.info("Delete called by: %s", context.peer())
        return UserHandler.delete(request)

    def Health(self, request, context):
        logger.info("Health called by: %s", context.peer())
        return HealthResponse(health=True)
