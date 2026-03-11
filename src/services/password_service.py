from logging import getLogger
logger = getLogger("api")

from passmanager.password.v0.password_pb2_grpc import PasswordServicer
from passmanager.common.v0.error_pb2 import (
    HealthResponse
)

from password_handler import PasswordHandler


class PasswordService(PasswordServicer):

    def Start(self, request, context):
        logger.info("Start called by: %s", context.peer())
        return PasswordHandler.start(request)

    def Auth(self, request, context):
        logger.info("Auth called by: %s", context.peer())
        return PasswordHandler.auth(request)

    def Complete(self, request, context):
        logger.info("Complete called by: %s", context.peer())
        return PasswordHandler.complete(request)

    def Abort(self, request, context):
        logger.info("Abort called by: %s", context.peer())
        return PasswordHandler.abort(request)

    def Get(self, request, context):
        logger.info("Get called by: %s", context.peer())
        return PasswordHandler.get(request)

    def Update(self, request, context):
        logger.info("Update called by: %s", context.peer())
        return PasswordHandler.update(request)

    def Health(self, request, context):
        logger.info("Health called by: %s", context.peer())
        return HealthResponse(health=True)
