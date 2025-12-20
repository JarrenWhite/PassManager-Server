from typing import Tuple, Dict, Any

from enums import FailureReason
from utils import DBUtilsUser, ServiceUtils


class ServiceUser():

    @staticmethod
    def register(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:

        keys = {"username_hash", "srp_salt", "srp_verifier", "master_key_salt"}
        sanitised, error, http_code = ServiceUtils.sanitise_inputs(data, keys)
        if not sanitised and http_code:
            return {"success": False, "errors": [error]}, http_code

        status, failure_reason = DBUtilsUser.create(
            data["username_hash"],
            data["srp_salt"],
            data["srp_verifier"],
            data["master_key_salt"]
        )

        if not status and failure_reason:
            error, http_code = ServiceUtils.handle_failure_reason(failure_reason)
            return {"success": False, "errors": [error]}, http_code

        return {"success": True, "username_hash": data["username_hash"], "errors": []}, 201


    @staticmethod
    def username(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200


    @staticmethod
    def delete(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200
