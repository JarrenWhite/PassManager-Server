from typing import Tuple, Optional, List
from datetime import datetime, timedelta

from passmanager.common.v0.secure_pb2 import (
    SecureRequest,
    SecureResponse
)

from enums import FailureReason
from .db_utils_auth import DBUtilsAuth
from cryptography import SRPUtils

EPHEMERAL_DELAY = 180

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
        # Fetch user auth details
        result = DBUtilsAuth.fetch(username_hash=username_hash)
        success, failure_reason, user_id, srp_salt, srp_verifier = result
        if not success:
            return False, failure_reason, "", b'', b'', b''

        # Generate ephemeral
        public_ephemeral, private_ephemeral = SRPUtils.generate_ephemeral(srp_verifier)

        # Add details to database
        result = DBUtilsAuth.start(
            user_id=user_id,
            eph_private_b=private_ephemeral,
            eph_public_b=public_ephemeral,
            expiry_time=(datetime.now() + timedelta(seconds=EPHEMERAL_DELAY))
        )
        success, failure_reason, public_id, master_key_salt = result
        if not success:
            return False, failure_reason, "", b'', b'', b''

        return True, None, public_id, srp_salt, srp_verifier, master_key_salt

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
        # Get details
        result = DBUtilsAuth.get_details(
            username_hash=username_hash,
            public_id=public_id
        )
        success, failure_reason, private_ephemeral, public_ephemeral, srp_verifier = result
        if not success:
            return False, failure_reason, "", b''

        # Calculate session key
        session_key = SRPUtils.compute_session_key(
            eph_val_a=eph_val_a,
            eph_public_b=public_ephemeral,
            eph_private_b=private_ephemeral,
            srp_verifier_v=srp_verifier
        )

        # Verify client proof
        success, proof_val_m2 = SRPUtils.verify_proof(
            eph_val_a=eph_val_a,
            eph_public_b=public_ephemeral,
            session_key_k=session_key,
            proof_val_m1=proof_val_m1
        )
        if not success:
            return False, FailureReason.NOT_FOUND, "", b''

        # Determine expiry details
        if maximum_requests < 0:
            max_reqs = None
        elif maximum_requests == 0:
            max_reqs = 100
        else:
            max_reqs = maximum_requests

        if expiry_time < 0:
            ex_time = None
        elif expiry_time == 0:
            ex_time = datetime.now() + timedelta(seconds=3600)
        else:
            ex_time = datetime.now() + timedelta(seconds=expiry_time)

        # Store session details
        result = DBUtilsAuth.complete(
            public_id=public_id,
            session_key=session_key,
            maximum_requests=max_reqs,
            expiry_time=ex_time
        )
        success, failure_reason, session_public_id = result
        if not success:
            return False, failure_reason, "", b''

        return True, None, session_public_id, proof_val_m2

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
