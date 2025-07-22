from typing import Dict, Any, Tuple, Optional


class Sanitise:

    @staticmethod
    def verify_keys(data: Dict[str, Any], required_keys: set[str]) -> Tuple[bool, Dict[str, Any]]:
        if set(data) != required_keys:
            allowed_list = "', '".join(sorted(required_keys))
            return False, {
                "error": f"Allowed and required parameters are: '{allowed_list}'"
            }
        else:
            return True, {}
