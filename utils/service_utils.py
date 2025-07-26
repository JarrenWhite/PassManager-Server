from typing import Dict, Any, Tuple
import logging
logger = logging.getLogger("services")

from .utils_enums import FailureReason


class Service:

    @staticmethod
    def sanitise_inputs(data: Dict[str, Any], required_keys: set[str], calling_function: str = "unknown") -> Tuple[bool, Dict[str, Any]]:
        """Verify that the keys received are correct"""
        if set(data) != required_keys:
            allowed_list = "', '".join(sorted(required_keys))
            logger.warning(f"Sanitise.keys ({calling_function}): Incorrect keys")
            return False, {
                "error": f"Allowed and required parameters are: '{allowed_list}'"
            }

        for key, value in data.items():
            ok, error = Service.select_sanitising_function(key, value, calling_function)
            if not ok:
                return False, error

        return True, {}

    @staticmethod
    def select_sanitising_function(key_name, key_value, calling_function: str = "unknown") -> Tuple[bool, Dict[str, Any]]:
        switch = {
            "username": lambda x: Service._username(x, calling_function),
            "password": lambda x: Service._password(x, calling_function)
        }
        result = switch.get(key_name, lambda x: Service._default(x, calling_function))(key_value)
        return result

    @staticmethod
    def handle_failure(failure_reason: FailureReason, calling_function: str = "unknown") -> Tuple[Dict[str, Any], int]:
        """Handle common failure scenarios and return appropriate HTTP responses"""

        if failure_reason == FailureReason.SERVER_EXCEPTION:
            logger.error(f"{calling_function}: Rejected - Server exception")
            return {"error": "Unknown error"}, 500

        elif failure_reason == FailureReason.ALREADY_EXISTS:
            logger.info(f"{calling_function}: Rejected - Username exists")
            return {"error": "Username already exists"}, 409

        elif failure_reason == FailureReason.USERNAME_NOT_FOUND:
            logger.warning(f"{calling_function}: Rejected - Username not found")
            return {"error": "Incorrect username or password"}, 401

        elif failure_reason == FailureReason.SESSION_NOT_FOUND:
            logger.warning(f"{calling_function}: Rejected - Session not found")
            return {"error": "Session not found or expired"}, 401

        elif failure_reason == FailureReason.ENTRY_NOT_FOUND:
            logger.warning(f"{calling_function}: Rejected - Entry not found")
            return {"error": "Entry not found"}, 404

        # Default case
        logger.error(f"{calling_function}: Rejected - Failure reason unknown")
        return {"error": "Unknown error"}, 500

    @staticmethod
    def _username(username: str, calling_function: str = "unknown") -> Tuple[bool, Dict[str, Any]]:
        """Sanitise the received username"""
        return True, {}

    @staticmethod
    def _password(password_hash: str, calling_function: str = "unknown") -> Tuple[bool, Dict[str, Any]]:
        """Sanitise the received password hash"""
        return True, {}

    @staticmethod
    def _default(key_value: str, calling_function: str = "unknown") -> Tuple[bool, Dict[str, Any]]:
        """Default sanitising function. Should not be called"""
        logger.error(f"Sanitise.default called from {calling_function}: Unknown key encountered")
        return False, {"error": "Unknown key encountered."}
