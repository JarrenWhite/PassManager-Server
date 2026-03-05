from passmanager.session.v0.session_pb2_grpc import SessionServicer
from passmanager.common.v0.error_pb2 import (
    HealthResponse
)

from session_handler import SessionHandler


class SessionService(SessionServicer):

    def Start(self, request, context):
        return SessionHandler.start(request)

    def Auth(self, request, context):
        return SessionHandler.auth(request)

    def Delete(self, request, context):
        return SessionHandler.delete(request)

    def Clean(self, request, context):
        return SessionHandler.clean(request)

    def Health(self, request, context):
        return HealthResponse(health=True)
