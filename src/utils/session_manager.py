from typing import Tuple, Optional

from passmanager.common.v0.secure_pb2 import (
    SecureRequest,
    SecureResponse
)

from enums import FailureReason


# TODO - Placeholder class. Requires completion.

class SessionManager():

    @staticmethod
    def start_new_session(
        username_hash: bytes
    ) -> Tuple[bool, Optional[FailureReason]]:
        return True, None

    @staticmethod
    def auth_new_session(
        username_hash: bytes,
        auth_id: str,
        eph_val_a: bytes,
        proof_val_m1: bytes,
        maximum_requests: int,
        expiry_time: int
    ) -> Tuple[bool, Optional[FailureReason], bytes]:
        return True, None, b''

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
