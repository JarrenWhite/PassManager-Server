from typing import Dict, Any, Tuple, Optional
import logging
logger = logging.getLogger("services")


class Sanitise:

    @staticmethod
    def keys(data: Dict[str, Any], required_keys: set[str], calling_function: str = "unknown") -> Tuple[bool, Dict[str, Any]]:
        """Verify that the keys received are correct"""
        if set(data) != required_keys:
            allowed_list = "', '".join(sorted(required_keys))
            logger.warning(f"Sanitise.keys ({calling_function}): Incorrect keys")
            return False, {
                "error": f"Allowed and required parameters are: '{allowed_list}'"
            }
        
        for key, value in data.items():
            ok, error = Sanitise.select_sanitising_function(key, value, calling_function)
            if not ok:
                return False, error

        return True, {}

    @staticmethod
    def select_sanitising_function(key_name, key_value, calling_function: str = "unknown") -> Tuple[bool, Dict[str, Any]]:
        switch = {
            "username": lambda x: Sanitise.username(x, calling_function),
            "password": lambda x: Sanitise.password(x, calling_function)
        }
        result = switch.get(key_name, lambda x: Sanitise.default(x, calling_function))(key_value)
        return result

    @staticmethod
    def username(username: str, calling_function: str = "unknown") -> Tuple[bool, Dict[str, Any]]:
        """Sanitise the received username"""
        return True, {}

    @staticmethod
    def password(password_hash: str, calling_function: str = "unknown") -> Tuple[bool, Dict[str, Any]]:
        """Sanitise the received password hash"""
        return True, {}
    
    @staticmethod
    def default(key_value: str, calling_function: str = "unknown") -> Tuple[bool, Dict[str, Any]]:
        """Default sanitising function. Should not be called"""
        logger.error(f"Sanitise.default called from {calling_function}: Unknown key encountered")
        return False, {"error": "Unknown key encountered."}
