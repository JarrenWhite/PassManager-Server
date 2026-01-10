from typing import Tuple, Dict, Any

from utils import DBUtilsUser, ServiceUtils, SessionManager
from .session_keys import SESSION_KEYS


class ServiceUser():

    @staticmethod
    def register(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:

        keys = {"new_username", "srp_salt", "srp_verifier", "master_key_salt"}
        sanitised, errors, http_code = ServiceUtils.sanitise_inputs(data, keys)
        if not sanitised:
            return {"success": False, "errors": errors}, http_code

        success, failure = DBUtilsUser.create(
            username_hash= data["new_username"],
            srp_salt= data["srp_salt"],
            srp_verifier= data["srp_verifier"],
            master_key_salt= data["master_key_salt"]
        )

        if not success:
            assert failure
            errors, http_code = ServiceUtils.handle_failure(failure)
            return {"success": False, "errors": errors}, http_code

        return {"success": True, "username_hash": data["new_username"]}, 201


    @staticmethod
    def username(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:

        sanitised, errors, http_code = ServiceUtils.sanitise_inputs(data, SESSION_KEYS)
        if not sanitised:
            return {"success": False, "errors": errors}, http_code

        decrypted, values, user_id, http_code = SessionManager.open_session(
            data["session_id"],
            data["request_number"],
            data["encrypted_data"]
        )
        if not decrypted:
            return {"success": False, "errors": [values]}, http_code

        keys = {"username", "new_username"}
        sanitised, errors, http_code = ServiceUtils.sanitise_inputs(values, keys)
        if not sanitised:
            return {"success": False, "errors": errors}, http_code

        success, failure = DBUtilsUser.change_username(
            user_id= user_id,
            new_username_hash= values["new_username"]
        )

        if not success:
            assert failure
            errors, http_code = ServiceUtils.handle_failure(failure)
            return {"success": False, "errors": errors}, http_code

        success, sealed_data, error, http_code = SessionManager.seal_session(
            data["session_id"], {"new_username": values["new_username"]}
        )
        if not success:
            return {"success": False, "errors": [error]}, http_code

        return {"success": True, "session_id": data["session_id"], "encrypted_data": sealed_data}, 200


    @staticmethod
    def delete(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:

        sanitised, errors, http_code = ServiceUtils.sanitise_inputs(data, SESSION_KEYS)

        return {}, 200
