from typing import Tuple, Dict, Any


# TODO - Placeholder class. Requires completion.

class SRPUtils():

    @staticmethod
    def generate_ephemeral(
        srp_verifier_v: bytes
    ) -> Tuple[bytes, bytes]:
        """
        Generate the ephemeral values

        Returns:
            (bytes) Public Ephemeral (B)
            (bytes) Private Ephemeral (b)
        """
        return b'', b''


    @staticmethod
    def compute_session_key(
        eph_val_A: bytes,
        eph_public_B: bytes,
        eph_private_b: bytes,
        srp_verifier_v: bytes
    ) -> bytes:
        """
        Compute the session key from its values

        Returns:
            (bytes) The session key (K)
        """
        return b''


    @staticmethod
    def verify_proof(
        eph_val_A: bytes,
        eph_public_B: bytes,
        session_key_K: bytes,
        proof_val_M1: bytes
    ) -> bytes:
        """
        Verify the proof of a matching session key

        Returns:
            (bytes) Server Proof (M2)
        """
        return b''
