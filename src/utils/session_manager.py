from typing import Dict, Any, Tuple


# TODO - Placeholder class. Requires completion.

class SessionManager():
    """Utility functions for managing sessions"""

    @staticmethod
    def open_session(
        session_id: str,
        request_number: int,
        encrypted_data: str
    ) -> Tuple[bool, Dict[str, Any], int, int]:
        """
        Verify that the received keys are correct

        Returns:
            (bool)  Returns true if decrypted, false otherwise
            (Dict)  Decrypted values if successful, error message if failed
            (int)   Internal User ID if successful
            (int)   HTTP status code if session decrypting fails
        """
        return True, {}, 0, 0

    @staticmethod
    def seal_session(
        session_id: str,
        unencrypted_data: Dict[str, Any]
    ) -> Tuple[bool, str, int]:
        """
        Docstring for seal_session

        Returns:
            (bool)  Returns true if encrypted, false otherwise
            (Dict)  Encrypted data if successful
            (int)   HTTP status code if session encrypting fails
        """
        return True, "", 0
