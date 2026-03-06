from passmanager.password.v0.password_pb2_grpc import PasswordServicer
from passmanager.common.v0.error_pb2 import (
    HealthResponse
)

from password_handler import PasswordHandler


class PasswordService(PasswordServicer):

    def Start(self, request, context):
        return PasswordHandler.start(request)

    def Auth(self, request, context):
        return PasswordHandler.auth(request)

    def Complete(self, request, context):
        return PasswordHandler.complete(request)

    def Abort(self, request, context):
        return PasswordHandler.abort(request)

    def Get(self, request, context):
        return PasswordHandler.get(request)

    def Update(self, request, context):
        return PasswordHandler.update(request)

    def Health(self, request, context):
        return HealthResponse(health=True)
