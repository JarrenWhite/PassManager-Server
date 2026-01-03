from typing import Dict, Any, Tuple, List

from enums import FailureReason


# TODO - Placeholder class. Requires completion.

class ServiceUtils():
    """Utility functions for managing service calls"""

    @staticmethod
    def sanitise_inputs(data: Dict[str, Any], required_keys: set[str]) -> Tuple[bool, List[Dict[str, Any]], int]:
        """
        Verify that the received keys are correct

        Returns:
            (bool)  Returns true if sanitised, false otherwise
            (List)  List of Error message if sanitisation fails
            (int)   HTTP status code if sanitisation fails
        """
        return True, [{}], 0


    @staticmethod
    def handle_failure(failure_reason: FailureReason) -> Tuple[List[Dict[str, Any]], int]:
        """
        Verify that the

        Returns:
            (List)  List of Error message for failure reason
            (int)   HTTP status code for failure reason
        """
        return [{}], 200
