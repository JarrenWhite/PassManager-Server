from typing import Dict, Any, Tuple, Optional
import logging
logger = logging.getLogger("services")


class Sanitise:

    @staticmethod
    def keys(data: Dict[str, Any], required_keys: set[str]) -> Tuple[bool, Dict[str, Any]]:
        """Verify that the keys received are correct"""
        if set(data) != required_keys:
            allowed_list = "', '".join(sorted(required_keys))
            return False, {
                "error": f"Allowed and required parameters are: '{allowed_list}'"
            }
        
        for key, value in data.items():
            ok, error = Sanitise.select_sanitising_function(key, value)
            if not ok:
                return False, error

        return True, {}

    @staticmethod
    def select_sanitising_function(key_name, key_value) -> Tuple[bool, Dict[str, Any]]:
        switch = {
            "password": Sanitise.password,
            "username": Sanitise.username
        }
        result = switch.get(key_name, Sanitise.default)(key_value)
        return result

    @staticmethod
    def username(username: str) -> Tuple[bool, Dict[str, Any]]:
        """Sanitise the received username"""
        return True, {}

    @staticmethod
    def password(password_hash: str) -> Tuple[bool, Dict[str, Any]]:
        """Sanitise the received password hash"""
        return True, {}
    
    @staticmethod
    def default(key_value: str) -> Tuple[bool, Dict[str, Any]]:
        """Default sanitising function. Should not be called"""
        return False, {"error": "Unknown key encountered."}
