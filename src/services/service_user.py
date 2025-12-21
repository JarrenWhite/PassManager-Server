from typing import Tuple, Dict, Any

from utils import DBUtilsUser, ServiceUtils, SessionManager
from .session_keys import SESSION_KEYS


class ServiceUser():

    @staticmethod
    def register(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:

        keys = {"username_hash", "srp_salt", "srp_verifier", "master_key_salt"}
        sanitised, error, http_code = ServiceUtils.sanitise_inputs(data, keys)
        if not sanitised:
            return {"success": False, "errors": [error]}, http_code

        status, failure_reason = DBUtilsUser.create(
            data["username_hash"],
            data["srp_salt"],
            data["srp_verifier"],
            data["master_key_salt"]
        )

        if not status and failure_reason:
            error, http_code = ServiceUtils.handle_failure(failure_reason)
            return {"success": False, "errors": [error]}, http_code

        return {"success": True, "username_hash": data["username_hash"], "errors": []}, 201


    @staticmethod
    def username(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:

        sanitised, error, http_code = ServiceUtils.sanitise_inputs(data, SESSION_KEYS)
        if not sanitised:
            return {"success": False, "errors": [error]}, http_code

        decrypted, values, user_id, http_code = SessionManager.open_session(
            data["session_id"],
            data["request_number"],
            data["encrypted_data"]
        )
        if not decrypted:
            return {"success": False, "session_id": data["session_id"], "errors": [values]}, http_code

        keys = {"username", "new_username"}
        sanitised, error, http_code = ServiceUtils.sanitise_inputs(values, keys)
        if not sanitised:
            return {"success": False, "errors": [error]}, http_code

        DBUtilsUser.change_username(user_id, values["new_username"])

        return {}, 200


    @staticmethod
    def delete(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200
