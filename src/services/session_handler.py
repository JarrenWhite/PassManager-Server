from passmanager.session.v0.session_pb2 import (
    SessionStartRequest,
    SessionStartResponse,
    SessionAuthRequest,
    SessionAuthResponse
)
from passmanager.session.v0.session_payloads_pb2 import (
    SessionDeleteRequest,
    SessionDeleteResponse,
    SessionCleanRequest,
    SessionCleanResponse
)


# TODO - Placeholder class. Requires completion.

class SessionHandler:

    @staticmethod
    def start(request: SessionStartRequest) -> SessionStartResponse:
        return SessionStartResponse()

    @staticmethod
    def auth(request: SessionAuthRequest) -> SessionAuthResponse:
        return SessionAuthResponse()

    @staticmethod
    def delete(request: SessionDeleteRequest) -> SessionDeleteResponse:
        return SessionDeleteResponse()

    @staticmethod
    def clean(request: SessionCleanRequest) -> SessionCleanResponse:
        return SessionCleanResponse()
