from typing import Tuple, Dict, Any

from utils import DBUtilsUser

class ServiceUser():

    @staticmethod
    def register(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        status, result = DBUtilsUser.create(
            data["username_hash"],
            data["srp_salt"],
            data["srp_verifier"],
            data["master_key_salt"]
        )

        if not status:
            errors = [{"field": "username_hash", "error_code": "gnr02", "error": "Username hash already exists"}]
            return {"success": False, "username_hash": data["username_hash"], "errors": errors}, 409
        return {"success": True, "username_hash": data["username_hash"], "errors": []}, 201

    @staticmethod
    def username(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200

    @staticmethod
    def delete(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200
