from typing import Dict, Any, Tuple, List

from enums import FailureReason

from .session_manager import SessionManager


# TODO - Placeholder class. Requires completion.

SESSION_KEYS = {"session_id", "request_number", "encrypted_data"}

class ServiceUtils():
    """Utility functions for managing service calls"""

    @staticmethod
    def sanitise_inputs(
        data: Dict[str, Any],
        required_keys: set[str]
    ) -> Tuple[bool, List[Dict[str, Any]], int]:
        """
        Verify that the received keys are correct

        Returns:
            (bool)  Returns true if sanitised, false otherwise
            (List)  List of Error message if sanitisation fails
            (int)   HTTP status code if sanitisation fails
        """
        return True, [{}], 0


    @staticmethod
    def open_session(
        data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any], int, List[Dict[str, Any]], int]:
        """
        Open a given session

        Returns:
            (bool)  Returns true if opened, false otherwise
            (Dict)  Decrypted values if successful
            (int)   Internal User ID if successful
            (Dict)  List of Error message if opening fails
            (int)   HTTP status code if opening fails
        """

        sanitised, errors, http_code = ServiceUtils.sanitise_inputs(data, SESSION_KEYS)
        if not sanitised:
            return False, {}, 0, errors, http_code

        decrypted, values, user_id, http_code = SessionManager.open_session(
            data["session_id"],
            data["request_number"],
            data["encrypted_data"]
        )
        if not decrypted:
            return False, {}, 0, [values], http_code

        return True, values, user_id, [], 0


    @staticmethod
    def handle_failure(
        failure_reason: FailureReason
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Verify that the

        Returns:
            (List)  List of Error message for failure reason
            (int)   HTTP status code for failure reason
        """
        return [{}], 200
