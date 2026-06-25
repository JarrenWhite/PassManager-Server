from typing import Tuple, Optional, List

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
    ) -> Tuple[bool, Optional[FailureReason], str, bytes, bytes, bytes]:
        """
        Start the process to create a new auth session

        Returns:
            (str)   Public ID
            (bytes) SRP Salt
            (bytes) Ephemeral Public ID
            (bytes) Master Key Salt
        """
        return True, None, "", b'', b'', b''

    @staticmethod
    def auth_new_session(
        username_hash: bytes,
        public_id: str,
        eph_val_a: bytes,
        proof_val_m1: bytes,
        maximum_requests: int,
        expiry_time: int
    ) -> Tuple[bool, Optional[FailureReason], str, bytes]:
        """
        Authenticate and create a session

        Returns:
            (str)   Session Public ID
            (bytes) Server Proof (M2)
        """
        return True, None, "", b''

    @staticmethod
    def start_password_session(
        user_id: int,
        srp_salt: bytes,
        srp_verifier: bytes,
        master_key_salt: bytes
    ) -> Tuple[bool, Optional[FailureReason], str, bytes]:
        """
        Start the process to create a new password session

        Returns:
            (str)   Public ID
            (bytes) Public Ephemeral (b)
        """
        return True, None, "", b''

    @staticmethod
    def auth_password_session(
        user_id: int,
        public_id: str,
        eph_val_a: bytes,
        proof_val_m1: bytes
    ) -> Tuple[bool, Optional[FailureReason], str, bytes, List[str]]:
        """
        Authenticate and create a password session

        Returns:
            (str)   Session Public ID
            (bytes) Server Proof (M2)
            ([str]) Entry Public IDs
        """
        return True, None, "", b'', []

    @staticmethod
    def open_session(
        request: SecureRequest,
        password_session: bool = False,
        first_request: bool = False
    ) -> Tuple[bool, Optional[FailureReason], bytes, int]:
        """
        Decrypt a message sent in a secure request

        Returns:
            (bytes) Decrypted Bytes
            (int)   User ID
        """
        return True, None, b'', 0

    @staticmethod
    def seal_session(
        session_id: str,
        response: bytes
    ) -> SecureResponse:
        """
        Encrypt a message into a secure response

        Returns:
            (SecureResponse)    Secured response
        """
        return SecureResponse()
