from typing import Tuple, Optional

from passmanager.common.v0.secure_pb2 import (
    SecureRequest,
    SecureResponse
)

from enums import FailureReason


# TODO - Placeholder class. Requires completion.

class SessionManager():

    @staticmethod
    def open_session(
        request: SecureRequest,
        password_session: bool = False,
        first_request: bool = False
    ) -> Tuple[bool, bytes, int, Optional[FailureReason]]:
        return True, b'', 0, None

    @staticmethod
    def seal_session(
        session_id: str,
        response: bytes
    ) -> SecureResponse:
        return SecureResponse()
