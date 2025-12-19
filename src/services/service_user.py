from typing import Tuple, Dict, Any

from utils import DBUtilsUser, ServiceUtils, FailureReason


class ServiceUser():

    @staticmethod
    def register(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        keys = {"username_hash", "srp_salt", "srp_verifier", "master_key_salt"}
        status, error = ServiceUtils.sanitise_inputs(data, keys)

        if not status:
            return {"success": False, "errors": [error]}, 400

        status, failure_reason = DBUtilsUser.create(
            data["username_hash"],
            data["srp_salt"],
            data["srp_verifier"],
            data["master_key_salt"]
        )

        if not status and failure_reason == FailureReason.DUPLICATE:
            errors = [{"field": "username_hash", "error_code": "ltd00", "error": "Username hash already exists"}]
            return {"success": False, "errors": errors}, 409
        elif not status:
            errors = [{"field": "server", "error_code": "svr00", "error": "Unknown server error"}]
            return {"success": False, "errors": errors}, 500
        return {"success": True, "username_hash": data["username_hash"], "errors": []}, 201


    @staticmethod
    def username(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200


    @staticmethod
    def delete(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200
