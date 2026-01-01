from typing import Tuple, Dict, Any

from utils import DBUtilsUser, ServiceUtils, SessionManager
from .session_keys import SESSION_KEYS


class ServiceUser():

    @staticmethod
    def register(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:

        keys = {"new_username", "srp_salt", "srp_verifier", "master_key_salt"}
        sanitised, error, http_code = ServiceUtils.sanitise_inputs(data, keys)
        if not sanitised:
            return {"success": False, "errors": [error]}, http_code

        success, failure = DBUtilsUser.create(
            username_hash= data["new_username"],
            srp_salt= data["srp_salt"],
            srp_verifier= data["srp_verifier"],
            master_key_salt= data["master_key_salt"]
        )

        if not success:
            assert failure
            return ServiceUtils.handle_failure(failure)

        return {}, 200


    @staticmethod
    def username(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:

        return {}, 200


    @staticmethod
    def delete(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:

        return {}, 200
