from passmanager.password.v0.password_payloads_pb2 import (
    PasswordStartRequest,
    PasswordStartResponse,
    PasswordAuthRequest,
    PasswordAuthResponse,
    PasswordCompleteRequest,
    PasswordCompleteResponse,
    PasswordAbortRequest,
    PasswordAbortResponse,
    PasswordGetRequest,
    PasswordGetResponse,
    PasswordUpdateRequest,
    PasswordUpdateResponse
)


# TODO - Placeholder class. Requires completion.

class PasswordHandler():

    @staticmethod
    def start(request: PasswordStartRequest) -> PasswordStartResponse:
        return PasswordStartResponse()

    @staticmethod
    def auth(request: PasswordAuthRequest) -> PasswordAuthResponse:
        return PasswordAuthResponse()

    @staticmethod
    def complete(request: PasswordCompleteRequest) -> PasswordCompleteResponse:
        return PasswordCompleteResponse()

    @staticmethod
    def abort(request: PasswordAbortRequest) -> PasswordAbortResponse:
        return PasswordAbortResponse()

    @staticmethod
    def get(request: PasswordGetRequest) -> PasswordGetResponse:
        return PasswordGetResponse()

    @staticmethod
    def update(request: PasswordUpdateRequest) -> PasswordUpdateResponse:
        return PasswordUpdateResponse()
