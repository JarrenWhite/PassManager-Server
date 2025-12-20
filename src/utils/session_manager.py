from typing import Dict, Any, Tuple, Optional


# TODO - Placeholder class. Requires completion.

class SessionManager():
    """Utility functions for managing sessions"""

    @staticmethod
    def open_session(
        session_id: str,
        request_number: int,
        encrypted_data: str
    ) -> Tuple[bool, Dict[str, Any], Optional[int]]:
        """
        Verify that the received keys are correct

        Returns:
            (bool)  Returns true if decrypted, false otherwise
            (Dict)  Decrypted values if successful, error message if failed
            (int)   HTTP status code if sanitisation fails
        """
        return True, {}, None
