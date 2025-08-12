from typing import Dict, Any, Tuple
import re
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

        elif failure_reason == FailureReason.REGISTRATION_NOT_FOUND:
            logger.warning(f"{calling_function}: Rejected - Entry not found")
            return {"error": "Entry not found"}, 404

        # Default case
        logger.error(f"{calling_function}: Rejected - Failure reason unknown")
        return {"error": "Unknown error"}, 500

    @staticmethod
    def select_sanitising_function(key_name, key_value, calling_function: str = "unknown") -> Tuple[bool, Dict[str, Any]]:
        switch = {
            "username": lambda x: Service._username(x, calling_function),
            "registration_id": lambda x: Service._registration_id(x, calling_function),
            "secret_key_enc": lambda x: Service._secret_key_enc(x, calling_function),
            "secret_key_plain": lambda x: Service._secret_key_plain(x, calling_function)
        }
        result = switch.get(key_name, lambda x: Service._default(x, calling_function))(key_value)
        return result

    @staticmethod
    def _username(username: str, calling_function: str = "unknown") -> Tuple[bool, Dict[str, Any]]:
        """Sanitise the received username (SHA-256 hash from the frontend)"""
        if not isinstance(username, str):
            logger.warning(f"Sanitise.username ({calling_function}): Username is not a string.")
            return False, {"error": "Username must be a string"}

        if not username.strip():
            logger.warning(f"Sanitise.username ({calling_function}): Username is empty.")
            return False, {"error": "Username cannot be empty"}

        if len(username) != 64:
            logger.warning(f"Sanitise.username ({calling_function}): Username length is {len(username)}, expected 64.")
            return False, {"error": "Username must be exactly 64 characters (SHA-256 hash)"}

        if not all(c in '0123456789abcdefABCDEF' for c in username):
            logger.warning(f"Sanitise.username ({calling_function}): Username contains invalid characters.")
            return False, {"error": "Username contains invalid characters (SHA-256 hash)"}

        return True, {}

    @staticmethod
    def _registration_id(registration_id: str, calling_function: str = "unknown") -> Tuple[bool, Dict[str, Any]]:
        """Sanitise the received registration id (UUID v4 hex string)"""
        if not isinstance(registration_id, str):
            logger.warning(f"Sanitise.registration_id ({calling_function}): Registration ID is not a string")
            return False, {"error": "Registration ID must be a string"}

        if not registration_id.strip():
            logger.warning(f"Sanitise.registration_id ({calling_function}): Registration ID is empty")
            return False, {"error": "Registration ID cannot be empty"}

        if len(registration_id) != 32:
            logger.warning(f"Sanitise.registration_id ({calling_function}): Registration ID length is {len(registration_id)}, expected 32.")
            return False, {"error": "Registration ID must be exactly 32 characters (UUID v4 hex)"}

        if not all(c in '0123456789abcdefABCDEF' for c in registration_id):
            logger.warning(f"Sanitise.registration_id ({calling_function}): Registration ID contains invalid characters")
            return False, {"error": "Registration ID contains invalid characters"}

        return True, {}

    @staticmethod
    def _secret_key_plain(secret_key_plain: str, calling_function: str = "unknown") -> Tuple[bool, Dict[str, Any]]:
        """Sanitise the received plain text secret key (string representation of 32 bytes from secrets.token_bytes)"""
        if not isinstance(secret_key_plain, str):
            logger.warning(f"Sanitise.secret_key_plain ({calling_function}): Secret key is not a string.")
            return False, {"error": "The received key does not match the stored one for this ID"}

        if not secret_key_plain.strip():
            logger.warning(f"Sanitise.secret_key_plain ({calling_function}): Secret key is empty.")
            return False, {"error": "The received key does not match the stored one for this ID"}

        if not secret_key_plain.startswith("b'") or not secret_key_plain.endswith("'"):
            logger.warning(f"Sanitise.secret_key_plain ({calling_function}): Secret key is not in valid bytes format.")
            return False, {"error": "The received key does not match the stored one for this ID"}

        # Extract the actual bytes content (remove b'' wrapper)
        bytes_content = secret_key_plain[2:-1]

        if len(bytes_content) != 128:
            logger.warning(f"Sanitise.secret_key_plain ({calling_function}): Secret key length is {len(bytes_content)}, expected 128.")
            return False, {"error": "The received key does not match the stored one for this ID"}

        # Check if the content contains valid hex escape sequences
        # Valid format: \x00 through \xff
        if not re.match(r'^(\\x[0-9a-fA-F]{2})*$', bytes_content):
            logger.warning(f"Sanitise.secret_key_plain ({calling_function}): Secret key contains invalid hex sequences.")
            return False, {"error": "The received key does not match the stored one for this ID"}

        return True, {}

    @staticmethod
    def _secret_key_enc(secret_key_enc: str, calling_function: str = "unknown") -> Tuple[bool, Dict[str, Any]]:
        """Sanitise the received encrypted secret key"""
        return True, {}

    @staticmethod
    def _default(key_value: str, calling_function: str = "unknown") -> Tuple[bool, Dict[str, Any]]:
        """Default sanitising function. Should not be called"""
        logger.error(f"Sanitise.default called from {calling_function}: Unknown key encountered")
        return False, {"error": "Unknown key encountered."}
