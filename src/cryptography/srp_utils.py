from typing import Tuple, Dict, Any


# TODO - Placeholder class. Requires completion.

class SRPUtils():

    @staticmethod
    def generate_ephemeral(
        srp_verifier_v: str
    ) -> Tuple[str, str]:
        """
        Generate the ephemeral values

        Returns:
            (str)   Public Ephemeral (B)
            (str)   Private Ephemeral (b)
        """
        return "", ""


    @staticmethod
    def compute_session_key(
        eph_val_A: str,
        eph_public_B: str,
        eph_private_b: str,
        srp_verifier_v: str
    ) -> str:
        """
        Compute the session key from its values

        Returns:
            (str)   The session key (K)
        """
        return ""

    @staticmethod
    def verify_proof(
        eph_val_A: str,
        eph_public_B: str,
        session_key_K: str,
        proof_val_M1: str
    ) -> str:
        """
        Verify the proof of a matching session key

        Returns:
            Server Proof (M2)
        """
        return ""
