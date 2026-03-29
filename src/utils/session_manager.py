from typing import Tuple, Optional

from passmanager.common.v0.secure_pb2 import (
    SecureRequest,
    SecureResponse
)

from enums import FailureReason


# TODO - Placeholder class. Requires completion.

class SessionManager():

    @staticmethod
    def open_session(request: SecureRequest) -> Tuple[bool, bytes, Optional[FailureReason]]:
        return True, b'', None

    @staticmethod
    def seal_session(response: bytes) -> SecureResponse:
        return SecureResponse()
