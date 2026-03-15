from logging import getLogger
logger = getLogger("api")

from passmanager.session.v0.session_pb2_grpc import SessionServicer
from passmanager.common.v0.error_pb2 import (
    HealthResponse
)

from session_handler import SessionHandler


class SessionService(SessionServicer):

    def Start(self, request, context):
        logger.info("Start called by: %s", context.peer())
        return SessionHandler.start(request)

    def Auth(self, request, context):
        logger.info("Auth called by: %s", context.peer())
        return SessionHandler.auth(request)

    def Delete(self, request, context):
        logger.info("Delete called by: %s", context.peer())
        return SessionHandler.delete(request)

    def Clean(self, request, context):
        logger.info("Clean called by: %s", context.peer())
        return SessionHandler.clean(request)

    def Health(self, request, context):
        logger.info("Health called by: %s", context.peer())
        return HealthResponse(health=True)
