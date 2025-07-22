from typing import Dict, Any, Tuple, Optional


class Sanitise:

    @staticmethod
    def keys(data: Dict[str, Any], required_keys: set[str]) -> Tuple[bool, Dict[str, Any]]:
        """Verify that the keys received are correct"""
        if set(data) != required_keys:
            allowed_list = "', '".join(sorted(required_keys))
            return False, {
                "error": f"Allowed and required parameters are: '{allowed_list}'"
            }
        return True, {}

    @staticmethod
    def username(username: str) -> Tuple[bool, Dict[str, Any]]:
        """Sanitise the received username"""
        return True, {}

    @staticmethod
    def password(password_hash: str) -> Tuple[bool, Dict[str, Any]]:
        """Sanitise the received password hash"""
        return True, {}
